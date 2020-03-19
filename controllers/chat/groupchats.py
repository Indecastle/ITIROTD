from routes import route, Method, redirect_to
from render import render_template
from auth import *
import db
import models


@route('chat/groupchats/', authorize=Authorize())
def chat_groupchats(request, **kwargs):
    query = request.query
    count_str = query.get('count', [0])[0]
    count = 0
    try:
        count = int(count_str)
    except ValueError:
        pass
    kwargs.update(count=count)

    user = request.auth_get_user()
    chats = db.get_chats_by_user(user.id, limit=count)
    kwargs.update(chats=chats)

    return render_template(request, 'templates/chat/groupchats.html', **kwargs)


@route('chat/createchat/', authorize=Authorize())
def chat_createchat(request, **kwargs):
    query = request.query
    return render_template(request, 'templates/chat/createchat.html', **kwargs)


@route('chat/createchat/', method=Method.POST, authorize=Authorize())
def chat_createchat(request):
    query = request.POST_query
    print('query_post: ', query)
    name, type_chat, password = query['name'][0], query['type'][0], query['password'][0]

    if not name and \
            name and not type_chat and \
            name and type_chat == 'secure' and not password:
        return render_template(request, 'templates/chat/createchat.html', message='Bad request')

    user = request.auth_get_user()
    secure = models.Chat.Type[type_chat].value
    row = db.create_chat(name, secure, user.id, password)


    return redirect_to(request, '/chat/groupchats/')
