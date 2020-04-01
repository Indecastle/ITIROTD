from routes import route, Method, redirect_to
from render import render_template
from auth import *
from helper import find_first, save_photo, try_to_int
from error import *
import db


@route('/chat/chat', authorize=Authorize())
def chat(request):
    query = request.query
    # chat_id, chat_password = request.query_get('chat_id'), request.query_get('chat_id')
    chat_id, chat_password = query.get2('chat_id'), query.get2('pass')
    if 'chat_id' is None or try_to_int(chat_id) is None:
        return redirect_to(request, '/')
    user = request.auth_get_user()
    chat = db.get_chats_by_user(user_id=user.id, chat_id=chat_id)
    if chat is None or chat.secure == Chat.Type.SECURE and chat.password != chat_password:
        request.response.code = 444
        return my_error(request, message=("chat secure", "bad password of chat or access denied"))
        # return redirect_to(request, '/')

    kwargs = {}
    return render_template(request, 'templates/chat/chat.html', **kwargs)