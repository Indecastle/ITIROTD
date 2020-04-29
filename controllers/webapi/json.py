import json

from routes import route, Method, redirect_to
from render import render_template
from auth import *
from helper import find_first, save_photo, try_to_int, try_jsbool_to_bool
from error import *
from db import create_user, find_user


@route('json/get_users', authorize=Authorize())
def json_get_users(request, **kwargs):
    query = request.query
    substr, count = query.get2('search', ''), query.get2('count', 100)
    count = try_to_int(count)
    if count is None:
        json_list_users = '[]'
    else:
        list_users = db.get_users(where=f'WHERE login LIKE "%{substr}%"', limit=f'LIMIT {count}')
        json_list_users = [u.to_dict() for u in list_users]
    return json.dumps({'user': json_list_users})


@route('json/get_chats', authorize=Authorize())
def json_get_chats(request, **kwargs):
    user = request.auth_get_user()
    query = request.query
    substr, isnotmy, count = query.get2('search', ''), query.get2('isnotmy', False), query.get2('count', 100)
    count = try_to_int(count)
    isnotmy = try_jsbool_to_bool(isnotmy)
    if count is None or user is None:
        json_list_chats = '[]'
    else:
        list_chats = db.get_chats_by_user(user.id, where=f'chat.name LIKE "%{substr}%"',
                                          limit=f'LIMIT {count}', is_other=isnotmy)
        if list_chats is None:
            list_chats = []
        json_list_chats = [c.to_dict() for c in list_chats]
    return json.dumps({'chats': json_list_chats})
