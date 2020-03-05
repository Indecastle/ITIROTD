from render import render_template

error_messages = {404: "Page Not Found",
                  405: "Method not allowed",
                  401: "no access"}


def my_error(code):
    kwargs = {'code': code, 'message': error_messages.get(code, "Another ERROR")}
    return render_template('shared/Error.html', **kwargs).encode()
