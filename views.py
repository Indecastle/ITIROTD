import time, json
import PythonInsideHtml36 as pih
from routes import *
from render import *
from auth import SESSIONS
from helper import save_photo


@route('/', '/index')
def index(request):
    request.response.headers['kek'] = 'lol'
    kwargs = {'time': time, 'debug_start_time': time.time()}
    return render_template(request, 'templates/index.html', **kwargs)


@route('/blog')
def blog(request):
    kwargs = {'filepath': 'static/sun.ico'}
    return render_template(request, 'templates/blog.html', **kwargs)


@route('/blog', method=Method.POST)
def blog_POST(request):
    return json.dumps(request.POST_query)


@route('/mytest')
def test_page(request):
    SESSIONS.clear()
    return redirect_to(request, request, '/')


@route('/index_POST', method=Method.POST)
def blog_POST(request):
    photo = request.POST_query['photo'][0]
    photopath = save_photo(photo)

    kwargs = {'filepath': photopath}

    return render_template(request, 'templates/blog.html', **kwargs)
