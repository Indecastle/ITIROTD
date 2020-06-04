from routes import route, Method, redirect_to
from render import render_template
from auth import *
import db
import models
from helper import try_to_int, convert_args_to_querystr
from error import *


@route('chat/enjoy_chat/', authorize=Authorize(), ajax=True)
def chat_enjoy(request, **kwargs):
    query = request.query
    chat_id = query.get2('chat_id')
    if chat_id is None or try_to_int(chat_id) is None:
        request.response.code = 444
        return my_error(request, message=("chat", "chat not found"))
    user = request.auth_get_user()
    # chat = db.get_chats_by_user(user_id=user.id, chat_id=chat_id, is_users=True)
    chat = db.find_chat({'id': chat_id}, is_users=True)

    if chat is None:
        request.response.code = 444
        return my_error(request, message=("chat", "chat not found"))
    elif any(u.id == user.id for u in chat.users):
        request.response.code = 444
        return my_error(request, message=("chat", "chat has user"))
    return render_template(request, 'templates/chat/enjoychat.html', kwargs={'chat':chat})


@route('chat/enjoy_chat', method=Method.POST, authorize=Authorize())
def chat_enjoy_POST(request, **kwargs):
    query = request.POST_query
    chat_id, chat_password = query.get2('chat_id'), query.get2('pass')
    if chat_id is None or try_to_int(chat_id) is None:
        return redirect_to(request, '/')

    user = request.auth_get_user()
    chat = db.find_chat({'id': chat_id}, is_users=True)
    ajax_json = {}
    if chat is None:
        ajax_json.update(message='Chat not found or bad passwor')
        return json.dumps(ajax_json)
    elif chat.secure == Chat.Type.SECURE and chat.password != chat_password:
        ajax_json.update(message='Bad password')
        return json.dumps(ajax_json)
    elif any(u.id == user.id for u in chat.users):
        ajax_json.update(message='Chat has user')
        return json.dumps(ajax_json)
    db.add_user_to_chat(chat_id, user.id)

    ajax_json.update(redirect=True,
                     newurl='/chat/chat?chat_id=%s' % chat_id)
    redirect_to(request, is_manual=True)
    return json.dumps(ajax_json)
