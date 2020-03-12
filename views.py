import time, json
import PythonInsideHtml36 as pih
from routes import *
from render import *
from auth import SESSIONS


@route('/')
def index(request):
    request.response.headers['kek'] = 'lol'
    kwargs = {'time': time, 'debug_start_time': time.time()}
    return render_template(request, 'templates/index.html', **kwargs).encode()


@route('/blog')
def blog(request):
    kwargs = {'filepath': 'sun.ico'}
    return render_template(request, 'templates/blog.html', **kwargs).encode()


@route('/blog', Method.POST)
def blog_POST(request):
    return json.dumps(request.POST_query).encode()


@route('/chat', authorize=Authorize())
def chat(request):
    kwargs = {}
    return render_template(request, 'templates/chat.html', **kwargs).encode()


@route('/mytest')
def test_page(request):
    SESSIONS.clear()
    return redirect_to(request, request, '/')

@route('/index_POST', Method.POST)
def blog_POST(request):
    photo = request.POST_query['photo'][0]
    import uuid
    u = uuid.uuid1()
    filename = 'static/other/' + str(u.hex) + '.jpg'
    file = open(filename, 'wb')
    file.write(photo)
    file.close()

    kwargs = {'filepath': filename}

    return render_template(request, 'templates/blog.html', **kwargs).encode()
