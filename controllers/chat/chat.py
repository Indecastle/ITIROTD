from routes import route, Method, redirect_to
from render import render_template
from auth import *
from helper import find_first, save_photo
from error import *
import db


@route('/chat/chat', authorize=Authorize())
def chat(request):
    kwargs = {}
    return render_template(request, 'templates/chat/chat.html', **kwargs)