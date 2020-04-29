from enum import Enum, auto
from auth import AUTHORIZE, Authorize, UserRole


class Method(Enum):
    GET = auto()
    POST = auto()


# URLS = {
#    '/favicon.ico': ico,
#    '/': index,
#    '/blog': blog,
#    '/chat': chat
# }
# URLS_POST = {
#    '/blog': blog_POST,
# }
URLS = {}
URLS_POST = {}


def route(*urls, method=Method.GET, authorize=None):
    # global URLS, URLS_POST
    def actual_decorator(func):
        # nonlocal urls
        for url in urls:
            if url != '/':
                url = '/' + url.strip('/')
            if method == Method.GET:
                URLS[url] = func
            elif method == Method.POST:
                URLS_POST[url] = func

            if authorize is not None:
                copy_auth = authorize.get_copy()
                copy_auth.url = url
                AUTHORIZE.append(copy_auth)

        return func

    return actual_decorator


def redirect_to(request, url=None, method=Method.GET):
    if url is None:
        url = request.path

#     if 'Set-Cookie' in request.response.headers:
#         return f'''
#         <head>
#   <meta http-equiv="refresh" content="0; URL={url}" />
# </head>
# '''.encode()

    request.response.code = 302
    request.response.send_header('Location', url)
    request.response.send_header('KEK', '1234567890')
    return ''
