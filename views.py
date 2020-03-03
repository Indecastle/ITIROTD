import time, json
import PythonInsideHtml36 as pih
from routes import *
from render import *


def my_error(code):
    kwargs = {'code': code, 'message': 'Error'}
    if code == 404:
        kwargs['message'] = "Not Found"
    elif code == 405:
        kwargs['message'] = "Method not allowed"
    return render_template('shared/Error.html', **kwargs).encode()


@route('/')
def index(request):
    request.response.headers['kek'] = 'lol'
    kwargs = {'time': time, 'debug_start_time': time.time()}
    return render_template('templates/index.html', **kwargs).encode()


@route('/blog')
def blog(request):
    return render_template('templates/blog.html').encode()


@route('/blog', Method.POST)
def blog_POST(request):
    return json.dumps(request.response.POST_query).encode()

@route('/chat')
def chat(request):
    kwargs = {}
    return render_template('templates/chat.html', **kwargs).encode()
