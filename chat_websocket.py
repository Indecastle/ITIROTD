import threading, itertools, time

import asyncio
import json
import logging
import websockets
from helper import find_first, try_to_int
import db
from models import Chat, Message

logging.basicConfig()

lock = asyncio.Lock()


# datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')

class SessionChat:
    def __init__(self, chat):
        self.lock = asyncio.Lock()
        self.lock_messages = asyncio.Lock()
        self.chat = chat
        self.USERS = []
        self.USERS_INFO = []

        self.actions = {
            'send_message': self.action_send_message
        }

    async def connect_chat(self, websocket, user):
        userinfo = (websocket, user)
        async with self.lock:
            if all(user.id != u.id for u in self.USERS):
                self.USERS.append(user)
            self.USERS_INFO.append(userinfo)
        await websocket.send(self.event_messages())
        await self.notify_users()

    async def disconnect_chat(self, websocket, user2):
        async with self.lock:
            user_info = self.get_userinfo(websocket)
            if user_info is None:
                return
            self.USERS_INFO.remove(user_info)
            if all(x[1].id != user_info[1].id for x in self.USERS_INFO):
                user = find_first(lambda u: u.id == user_info[1].id, self.USERS)
                self.USERS.remove(user)
        await self.notify_users()

    def get_userinfo(self, websocket):
        return find_first(lambda x: x[0] == websocket, self.USERS_INFO)

    def event_messages(self):
        messages = list(map(lambda m: (m.text, m.user.nickname), self.chat.messages))
        return json.dumps({"type": "get_messages", "messages": messages})

    def users_event(self):
        list_users = [u.nickname for u in self.USERS]
        return json.dumps({"type": "users", "users": list_users})

    # def event_init(self):
    #     messages = list(map(lambda m: (m.text, m.user.nickname), self.chat.messages))
    #     return json.dumps({"type": "init", "users": self.USERS, "messages": messages})

    def event_send_message(self, message_info):
        return json.dumps({"type": "get_one_message", "text": message_info[0], 'who': message_info[1]})

    async def notify_messages(self):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            message = self.event_messages()
            await asyncio.wait([user[0].send(message) for user in self.USERS_INFO])

    async def notify_users(self):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            message = self.users_event()
            await asyncio.wait([user[0].send(message) for user in self.USERS_INFO])

    async def send_message(self, message_info):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            message = self.event_send_message(message_info)
            await asyncio.wait([user[0].send(message) for user in self.USERS_INFO])

    async def action_send_message(self, data, user):
        text = data['text']
        when = int(time.time())
        message_id = db.create_message(self.chat.id, user.id, when, text)
        new_message = Message(message_id, self.chat.id, user.id, when, text)
        new_message.user = user
        async with self.lock_messages:
            self.chat.messages.append(new_message)
        message_info = (text, user.login)
        await self.send_message(message_info)


SESSION_CHATS = []


async def register(websocket):
    message = await websocket.recv()
    sessionid = try_to_int(json.loads(message)["session"])
    chat_id = try_to_int(json.loads(message)["chat_id"])
    password = json.loads(message)["password"]
    if sessionid is None or chat_id is None:
        return None, None
    user_temp = db.find_user_by_sessionid(sessionid)
    if not user_temp:
        return None, None
    chat = db.get_chats_by_user(user_id=user_temp.id, chat_id=chat_id)
    if chat is None or chat.secure == Chat.Type.SECURE and chat.password != password:
        return None, None
    else:
        session_chat = find_first(lambda sc: sc.chat.id == chat.id, SESSION_CHATS)
        if session_chat is None:
            chat_extended = db.get_chats_by_user(user_id=user_temp.id, chat_id=chat_id, is_messages=True, is_users=True)
            session_chat = SessionChat(chat_extended)
            async with lock:
                SESSION_CHATS.append(session_chat)
        user = find_first(lambda u: u.id == user_temp.id, session_chat.chat.users)
        if user is None:
            user = user_temp
            session_chat.chat.users.append(user)

        await session_chat.connect_chat(websocket, user)
        return session_chat, user


async def unregister(websocket, session_chat, user):
    if session_chat is not None:
        await session_chat.disconnect_chat(websocket, user)
        if not session_chat.USERS:
            async with lock:
                SESSION_CHATS.remove(session_chat)
    print('current_sessions(after unregister):', len(SESSION_CHATS))


async def action_loop(websocket, path):
    # register(websocket) sends user_event() to websocket
    session_chat, user = None, None
    try:
        session_chat, user = await register(websocket)
        if user is None:
            await websocket.send(json.dumps({"type": "redirect"}))
            return

        async for message in websocket:
            data = json.loads(message)
            if data["action"] in session_chat.actions:
                await session_chat.actions[data['action']](data, user)
            else:
                logging.error("unsupported event: {}", data)
    finally:
        await unregister(websocket, session_chat, user)


def start_asyncio():
    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(action_loop, "localhost", 6789)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    chat_service = threading.Thread(target=run_in_thread)
    chat_service.start()


if __name__ == "__main__":
    start_server = websockets.serve(action_loop, "localhost", 6789)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
