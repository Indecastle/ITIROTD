import time, json
import PythonInsideHtml36 as pih
from routes import *
from render import *
from auth import SESSIONS
from helper import save_photo
from error import my_error



@route('/blog')
def blog(request):
    kwargs = {'filepath': 'static/sun.ico'}
    return render_template(request, 'templates/blog.html', kwargs=kwargs)


@route('/test_frames/chat')
def test_chat(request):
    return render_template(request, 'templates/html_frames/chat.html')

@route('/test_frames/list_chats')
def test_chat(request):
    return render_template(request, 'templates/html_frames/list_chat.html')

@route('/test_frames/create_chat')
def test_chat(request):
    return render_template(request, 'templates/html_frames/create_chat.html')

@route('/test_frames/login')
def test_chat(request):
    return render_template(request, 'templates/html_frames/login.html')