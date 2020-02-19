import time;
import PythonInsideHtml36 as pih


def render_template(file, **kwargs):
	template  = pih.PIH(file)
	code = template.pythonCode()
	
	e = {}
	e.update(**kwargs)

	exec(code, e)
	return e["py_code"].getvalue()


def index():
    kwargs = {'time': time, 'debug_start_time': time.time()}
    return render_template('templates/index.html', **kwargs).encode()


def blog():
    with open('templates/blog.html') as template:
        return template.read().encode()


def ico():
    with open('sun.ico', 'rb') as template:
        return template.read()
