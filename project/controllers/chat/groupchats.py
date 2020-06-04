import json
from routes import route, Method, redirect_to
from render import render_template
from auth import *
import db
import models
from helper import try_to_int, convert_args_to_querystr


@route('chat/groupchats/', authorize=Authorize(), ajax=True)
def chat_groupchats(request, **kwargs):
    query = request.query
    count_str = query.get('count', [0])[0]
    count = try_to_int(count_str, null=0)

    kwargs.update(count=count)

    user = request.auth_get_user()
    chats = db.get_chats_by_user(user.id, limit=count)
    kwargs.update(chats=chats)

    return render_template(request, 'templates/chat/groupchats.html', kwargs=kwargs)


@route('chat/createchat/', authorize=Authorize(), ajax=True)
def chat_createchat(request, **kwargs):
    query = request.query
    return render_template(request, 'templates/chat/createchat.html', kwargs=kwargs)


@route('chat/createchat/', method=Method.POST, authorize=Authorize())
def chat_createchat_POST(request):
    query = request.POST_query
    name, type_chat, password = query.get2('name'), query.get2('type'), query.get2('password')
    ajax_json = {}
    if not name or \
            not type_chat or \
            type_chat == 'SECURE' and not password:
        ajax_json.update(message='Bad request')
        return json.dumps(ajax_json)
        # return render_template(request, 'templates/chat/createchat.html', message='Bad request')
    # return redirect_to(request)

    user = request.auth_get_user()
    secure = models.Chat.Type[type_chat].value
    chat_id = db.create_chat(name, secure, password, user.id)
    # db.add_user_to_chat(chat_id, user.id)

    newquery = {'chat_id': chat_id}
    if password:
        newquery.update(password=password)
    newquery = db.convert_args_to_querystr('&', query=newquery, is_str=False)
    # ajax_json.update(redirect='/chat/chat?' + newquery)
    return redirect_to(request, f'/chat/chat?' + newquery)
