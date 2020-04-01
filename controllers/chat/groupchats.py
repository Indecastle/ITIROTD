from routes import route, Method, redirect_to
from render import render_template
from auth import *
import db
import models
from helper import try_to_int, convert_args_to_querystr


@route('chat/groupchats/', authorize=Authorize())
def chat_groupchats(request, **kwargs):
    query = request.query
    count_str = query.get('count', [0])[0]
    count = try_to_int(count_str, null=0)

    kwargs.update(count=count)

    user = request.auth_get_user()
    chats = db.get_chats_by_user(user.id, limit=count)
    kwargs.update(chats=chats)

    return render_template(request, 'templates/chat/groupchats.html', **kwargs)


@route('chat/createchat/', authorize=Authorize())
def chat_createchat(request, **kwargs):
    query = request.query
    users = db.get_users()
    user = request.auth_get_user()
    users = list(filter(lambda u: u.id != user.id, users))
    kwargs.update(users=users)
    return render_template(request, 'templates/chat/createchat.html', **kwargs)


@route('chat/createchat/', method=Method.POST, authorize=Authorize())
def chat_createchat_POST(request):
    query = request.POST_query
    print('query_post: ', query)
    name, type_chat, password, users = query['name'][0], query['type'][0], query['password'][0], query.get('users', [])

    if not name or \
            not type_chat or \
            type_chat == 'SECURE' and not password:
        return chat_createchat(request, message='Bad request')
        # return render_template(request, 'templates/chat/createchat.html', message='Bad request')
    # return redirect_to(request)

    user = request.auth_get_user()
    secure = models.Chat.Type[type_chat].value
    chat_id = db.create_chat(name, secure, password, user.id)
    for user_id in users:
        db.add_user_to_chat(chat_id, user_id)
    # db.add_user_to_chat(chat_id, user.id)

    newquery = {'chat_id': chat_id}
    if password:
        newquery.update(password=password)
    newquery = db.convert_args_to_querystr('&', query=newquery, is_str=False)
    print(newquery)
    return redirect_to(request, f'/chat/chat?' + newquery)
