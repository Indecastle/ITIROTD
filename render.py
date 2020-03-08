import PythonInsideHtml36 as pih

args = {
    'link_for': lambda s: "../static/" + s
}


def render_template(request, file, **kwargs):
    template = pih.PIH(file)
    code = template.pythonCode()

    e = {**args, 'request': request}
    e.update(**kwargs)

    exec(code, e)
    print(e.keys())
    if 'base' in e:
        return render_template(request, e["base"], body=e["py_code"].getvalue())
    else:
        return e["py_code"].getvalue()


args['render_template'] = render_template
