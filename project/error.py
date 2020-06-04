import json
from render import render_template

error_messages = {404: ("Page Not Found", "we are sorry, but the page you requested was not found"),
                  405: ("Method not allowed", "we are sorry, but the Method not allowed"),
                  401: ("no access", "we are sorry, but the page no access")}

error_codes = {'other': "<span>4</span><span>0</span><span>0</span>",
               401: "<span>4</span><span>0</span><span>1</span>",
               404: "<span>4</span><span>0</span><span>4</span>",
               405: "<span>4</span><span>0</span><span>5</span>"}


def gen_code(code):
    return ''.join(f"<span>{c}</span>" for c in str(code))


def my_error(request, message=None, is_ajax=False):
    code = request.response.code
    if message is None:
        message = request.responses.get(code, ("other", "Another ERROR"))
    kwargs = {'code': code,
              'message': message,
              'code_span': gen_code(code),
              'base_vars': {'title': 'ERROR'}}

    if is_ajax:
        ajax_dict = {
            'html': render_template(request, 'shared/Error.html', kwargs=kwargs),
            'title': 'Error'
        }
        return json.dumps(ajax_dict)
    else:
        return render_template(request, 'shared/Error.html', kwargs=kwargs)
