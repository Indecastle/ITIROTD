import threading, itertools

import asyncio
import json
import logging
import websockets
from helper import find_first
import db

logging.basicConfig()

STATE = {"value": 0}

USERS = []
USERS_INFO = []
MESSAGES = []
lock = asyncio.Lock()


def find_first(pred, iterable):
    return next(filter(pred, iterable), None)


def get_userinfo(websocket):
    return find_first(lambda x: x[0] == websocket, USERS_INFO)


def event_messages():
    return json.dumps({"type": "get_messages", "messages": MESSAGES})


def users_event():
    list_users = [u.nickname for u in USERS]
    return json.dumps({"type": "users", "users": list_users})


def event_init():
    return json.dumps({"type": "init", "users": USERS, "messages": MESSAGES})


def event_send_message(message_info):
    return json.dumps({"type": "get_one_message", "text": message_info[0], 'who': message_info[1]})


async def notify_messages():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = event_messages()
        await asyncio.wait([user[0].send(message) for user in USERS_INFO])


async def notify_users():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([user[0].send(message) for user in USERS_INFO])


async def send_message(message_info):
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = event_send_message(message_info)
        await asyncio.wait([user[0].send(message) for user in USERS_INFO])


async def register(websocket):
    message = await websocket.recv()
    sessionid = json.loads(message)["session"]
    user = db.find_user_by_sessionid(sessionid)
    if not user:
        websocket.close()
        return None
    userinfo = (websocket, user)
    async with lock:
        if all(user.id != u.id for u in USERS):
            USERS.append(user)
        USERS_INFO.append(userinfo)
    await notify_users()
    return user.login


async def unregister(websocket):
    async with lock:
        user_info = get_userinfo(websocket)
        USERS_INFO.remove(user_info)
        if all(x[1].id != user_info[1].id for x in USERS_INFO):
            USERS.remove(user_info[1])
    await notify_users()


async def counter(websocket, path):
    # register(websocket) sends user_event() to websocket
    try:
        login = await register(websocket)
        await websocket.send(event_messages())
        async for message in websocket:
            data = json.loads(message)
            if data["action"] == "send_message":
                message_info = (data['text'], login)
                MESSAGES.append(message_info)
                await send_message(message_info)
            else:
                logging.error("unsupported event: {}", data)
    finally:
        await unregister(websocket)


def start_asyncio():
    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(counter, "localhost", 6789)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    chat_service = threading.Thread(target=run_in_thread)
    chat_service.start()


if __name__ == "__main__":
    start_server = websockets.serve(counter, "localhost", 6789)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
