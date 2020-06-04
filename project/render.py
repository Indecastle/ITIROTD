import PythonInsideHtml36 as pih
import models

args = {
    'link_for': lambda s: "/static/" + s,
    'message': '',
    'models': models
}


def render_template(request, file, kwargs={}):
    template = pih.PIH(file)
    code = template.pythonCode()

    e = {**args, 'request': request, 'base_vars': dict()}
    e.update(**kwargs)

    exec(code, e)
    # print(e.keys())
    if 'base' in e:
        return render_template(request, e["base"], kwargs={'body': e["py_code"].getvalue(),
                                                           'base_vars': e["base_vars"]})
    else:
        return e["py_code"].getvalue()


args['render_template'] = render_template


def render_base_main(request):
    return render_template(request, 'shared/base.html', kwargs={'body': '',
                                                                'base_vars': {}})