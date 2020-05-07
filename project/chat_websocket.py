import threading, itertools, time, ssl, asyncio, json, logging, websockets
from helper import find_first, try_to_int
import db
from models import Chat, Message
from config import WEBSOCKET_CHAT_PATH, SSL_PEM_PATH
from itertools import takewhile

logging.basicConfig()

lock = asyncio.Lock()
SESSION_CHATS = []

def update_chat_user(user_id, user_dict):
    for sc in SESSION_CHATS:
        user = find_first(lambda u: u.id == user_id, sc.chat.users)
        if user is not None:
            user.update(user_dict)

# datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')

class SessionChatUser:
    def __init__(self, websocket, user):
        self.websocket = websocket
        self.user = user
        self.is_reading = False


class SessionChat:
    def __init__(self, chat):
        self.lock = asyncio.Lock()
        self.lock_messages = asyncio.Lock()
        self.chat = chat
        self.USERS = []
        self.USERS_INFO = []
        self.is_focus_last_user = None

        self.actions = {
            'send_message': self.action_send_message,
            'window_onfocus': self.action_window_onfocus,
            'reading_message': self.action_reading_message
        }

    async def websocket_send(self, message, users_info=None, except_user_info=None):
        if users_info is None:
            users_info = self.USERS_INFO
        elif type(users_info) != list:
            users_info = [users_info]
        users_info = [ui for ui in users_info if ui is not except_user_info]
        if users_info:
            await asyncio.wait([ui.websocket.send(message) for ui in users_info])

    async def connect_chat(self, websocket, user, is_new_user):
        async with self.lock:
            if all(user.id != u.id for u in self.USERS):
                self.USERS.append(user)
            user_info = SessionChatUser(websocket, user)
            self.USERS_INFO.append(user_info)
        # await websocket.send(self.gen_init(user))
        self.message_readed(user_info)
        await self.websocket_send(self.gen_init(user), user_info)
        await self.notify_all_users()
        await self.notify_users()
        await self.notify_messages(user_info)
        await self.action_reading_message({'is_reading': False}, user_info)
        return user_info

    async def disconnect_chat(self, websocket, user_info):
        async with self.lock:
            # user_info = self.get_userinfo(websocket)
            # if user_info is None:
            #     return
            self.USERS_INFO.remove(user_info)
            if all(x.user.id != user_info.user.id for x in self.USERS_INFO):
                user = find_first(lambda u: u.id == user_info.user.id, self.USERS)
                self.USERS.remove(user)
        await self.notify_users()
        await self.action_reading_message({'is_reading': False}, user_info)

    def get_userinfo(self, websocket):
        return find_first(lambda x: x.websocket == websocket, self.USERS_INFO)

    def gen_init(self, user):
        users_dict = [u.to_dict() for u in self.chat.users]
        return json.dumps({"type": "init", "user": user.to_dict()})

    async def notify_all_users(self):
        list_users = [u.to_dict() for u in self.chat.users]
        message = json.dumps({"type": "all_users",  'users': list_users})
        await self.websocket_send(message)

    async def notify_messages(self, user_info):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            messages = list(map(lambda m: (m.to_dict(), m.user.to_dict()), self.chat.messages))
            json_encoded = json.dumps({"type": "get_messages", "messages": messages})
            await self.websocket_send(json_encoded, user_info)

    async def notify_users(self):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            list_users = [u.to_dict() for u in self.USERS]
            message = json.dumps({"type": "users", "users": list_users})
            await self.websocket_send(message)

    async def send_message(self, message, uuid):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            json_encoded = json.dumps(
                {"type": "get_one_message", "message": message.to_dict(), 'user': message.user.to_dict(), 'uuid': uuid})
            await self.websocket_send(json_encoded)

    async def action_send_message(self, data, user_info):
        await asyncio.sleep(1.0)
        await self.action_window_onfocus(None, user_info)
        user = user_info.user
        text = data['text']
        uuid = data['uuid']
        when = int(time.time())
        message_id = db.create_message(self.chat.id, user.id, when, text)
        new_message = Message(message_id, self.chat.id, user.id, when, text, isreaded=False)
        new_message.user = user
        async with self.lock_messages:
            self.chat.messages.append(new_message)
        await self.send_message(new_message, uuid)
        # self.is_focus = False

    async def action_window_onfocus(self, data, user_info):
        self.message_readed(user_info)
        # self.is_focus = True
        json_encoded = json.dumps({"type": "window_onfocus", 'user_id': user_info.user.id})
        await self.websocket_send(json_encoded, except_user_info=user_info)

    def message_readed(self, user_info):
        if self.is_focus_last_user and (self.is_focus_last_user.id != user_info.user.id):
            for message in takewhile(lambda m: m.isreaded is False, reversed(self.chat.messages)):
                message.isreaded = True
        self.is_focus_last_user = user_info.user

    async def send_isreading(self, user_info):
        users_isreading = list(user.to_dict() for user in self.USERS if user.is_reading)
        # print('users_isreading', users_isreading)
        json_str = json.dumps(
            {"type": "is_reading", "user": None, 'users_is_reading': users_isreading})
        await self.websocket_send(json_str, except_user_info=user_info)

    async def action_reading_message(self, data, user_info):
        user_info.is_reading = data['is_reading']
        is_reading = any(ui.is_reading for ui in self.USERS_INFO if ui.user is user_info.user)
        if user_info.user.is_reading != is_reading:
            user_info.user.is_reading = is_reading
            await self.send_isreading(user_info)


async def register(websocket):
    message = await websocket.recv()
    message = json.loads(message)
    sessionHash = message["sessionHash"]
    user_id = try_to_int(message["user_id"])
    chat_id = try_to_int(message["chat_id"])
    if sessionHash is None or chat_id is None:
        return None, None
    user_temp = db.find_user_by_sessionid(user_id, sessionHash)
    if not user_temp:
        return None, None

    chat = db.get_chats_by_user(user_id=user_temp.id, chat_id=chat_id)
    session_chat = find_first(lambda sc: sc.chat.id == chat.id, SESSION_CHATS)
    if session_chat is None:
        chat_extended = db.get_chats_by_user(user_id=user_temp.id, chat_id=chat_id, is_messages=True, is_users=True)
        session_chat = SessionChat(chat_extended)
        async with lock:
            SESSION_CHATS.append(session_chat)
    user = find_first(lambda u: u.id == user_temp.id, session_chat.chat.users)
    is_new_user = False
    if user is None:
        is_new_user = True
        user = user_temp
        session_chat.chat.users.append(user)

    user_info = await session_chat.connect_chat(websocket, user, is_new_user)
    return session_chat, user_info


async def unregister(websocket, session_chat, user_info):
    if session_chat is not None:
        await session_chat.disconnect_chat(websocket, user_info)
        # if not session_chat.USERS:
        #     async with lock:
        #         SESSION_CHATS.remove(session_chat)
    # print('current_sessions(after unregister):', len(SESSION_CHATS))


async def action_loop(websocket, path):
    # register(websocket) sends user_event() to websocket
    session_chat, user_info = None, None
    try:
        session_chat, user_info = await register(websocket)
        if user_info is None:
            await websocket.send(json.dumps({"type": "redirect"}))
            return

        async for message in websocket:
            data = json.loads(message)
            if data["action"] in session_chat.actions:
                await session_chat.actions[data['action']](data, user_info)
            else:
                logging.error("unsupported event: {}", data)
    finally:
        await unregister(websocket, session_chat, user_info)


def start_asyncio():
    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(SSL_PEM_PATH)
        # start_server = websockets.serve(action_loop, *WEBSOCKET_CHAT_PATH, ssl=ssl_context)
        start_server = websockets.serve(action_loop, *WEBSOCKET_CHAT_PATH)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    chat_service = threading.Thread(target=run_in_thread)
    chat_service.start()


if __name__ == "__main__":
    start_server = websockets.serve(action_loop, *WEBSOCKET_CHAT_PATH)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
