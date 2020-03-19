from routes import route, Method, redirect_to
from render import render_template
from auth import *


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

    chats = db.get_chats(limit=count)
    kwargs.update(chats=chats)

    return render_template(request, 'templates/chat/groupchats.html', **kwargs)


@route('chat/createchat/', authorize=Authorize())
def chat_createchat(request, **kwargs):
    query = request.query
    return render_template(request, 'templates/chat/createchat.html', **kwargs)


@route('chat/createchat/', method=Method.POST, authorize=Authorize())
def chat_createchat(request, **kwargs):
    query = request.POST_query
    print('query_post: ', query)
    return redirect_to(request, '/chat/groupchats/')