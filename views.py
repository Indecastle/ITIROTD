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


def index():
    kwargs = {'time': time, 'debug_start_time': time.time()}
    return render_template('templates/index.html', **kwargs).encode()


def blog():
    return render_template('templates/blog.html').encode()


def ico():
    with open('sun.ico', 'rb') as template:
        return template.read()

def chat():
    kwargs = {}
    return render_template('templates/chat.html', **kwargs).encode()