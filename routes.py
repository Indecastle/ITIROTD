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


def route(url, method=Method.GET, authorize=None):
    # global URLS, URLS_POST
    def actual_decorator(func):
        if url == '/test':
            print(url)
        if method == Method.GET:
            URLS[url] = func
        elif method == Method.POST:
            URLS_POST[url] = func

        if authorize is not None:
            authorize.url = url
            AUTHORIZE.append(authorize)

        return func

    return actual_decorator


def redirect_to(request, url=None, method=Method.GET):
    if url is None:
        url = request.path
    request.response.code = 301
    request.response.headers['Location'] = url
    return b''
