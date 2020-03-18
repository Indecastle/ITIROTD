from routes import route, Method, redirect_to
from render import render_template
from auth import *


@route('chat/groupchats/', authorize=Authorize())
def manage_index(request, **kwargs):
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