import time;
import PythonInsideHtml36 as pih

def render_base_template(**kwargs):
    pass

args = {
    'link_for': lambda s: "static/" + s
}

def render_template(file, **kwargs):
    template = pih.PIH(file)
    code = template.pythonCode()

    e = {**args}
    e.update(**kwargs)

    exec(code, e)
    print(e.keys())
    if 'base' in e:
        return render_template(e["base"], body= e["py_code"].getvalue())
    else:
        return e["py_code"].getvalue()


args['render_template'] = render_template


def my_error(code):
    kwargs = {'code': code, 'message': 'Error'}
    if code == 404:
        kwargs['message'] = "Not Found"
    elif code == 405:
        kwargs['message'] = "Method not allowed"
    return render_template('shared/Error.html', **kwargs).encode()


def index(request):
    request.response.headers['kek'] = 'lol'
    kwargs = {'time': time, 'debug_start_time': time.time()}
    return render_template('templates/index.html', **kwargs).encode()


def blog(request):
    return render_template('templates/blog.html').encode()


def ico(request):
    with open('sun.ico', 'rb') as template:
        return template.read()

def chat(request):
    kwargs = {}
    return render_template('templates/chat.html', **kwargs).encode()