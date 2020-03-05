import time, json
import PythonInsideHtml36 as pih
from routes import *
from render import *
from auth import SESSIONS


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
    return json.dumps(request.POST_query).encode()


@route('/chat', authorize=Authorize())
def chat(request):
    kwargs = {}
    return render_template('templates/chat.html', **kwargs).encode()


@route('/mytest')
def test_page(request):
    SESSIONS.clear()
    return redirect_to(request, '/')
