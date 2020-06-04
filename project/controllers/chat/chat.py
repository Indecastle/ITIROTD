from routes import route, Method, redirect_to
from render import render_template
from auth import *
from helper import find_first, save_photo, try_to_int
from error import *
import db


@route('/chat/chat', authorize=Authorize(), ajax=True)
def chat(request):
    query = request.query
    # chat_id, chat_password = request.query_get('chat_id'), request.query_get('chat_id')
    chat_id = query.get2('chat_id')
    if chat_id is None or try_to_int(chat_id) is None:
        request.response.code = 404
        return my_error(request, message=("chat", "bad chat_id"))
        # return redirect_to(request, '/')
    chat = db.find_chat({'id': chat_id})
    if chat is None:
        request.response.code = 404
        return my_error(request, message=("chat", "chat not found"))
    user = request.auth_get_user()
    chat = db.get_chats_by_user(user_id=user.id, chat_id=chat_id)
    if chat is None:
        return redirect_to(request, f'/chat/enjoy_chat?chat_id={chat_id}')

    kwargs = {}
    return render_template(request, 'templates/chat/chat.html', kwargs=kwargs)