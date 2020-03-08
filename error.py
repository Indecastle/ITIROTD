from render import render_template

error_messages = {404: "Page Not Found",
                  405: "Method not allowed",
                  401: "no access"}


def my_error(request, code):
    kwargs = {'code': code, 'message': error_messages.get(code, "Another ERROR")}
    return render_template(request, 'shared/Error.html', **kwargs).encode()
