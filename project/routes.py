import json
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
URLS_GET = {}
URLS_GET_ajax = {}
URLS_GET_redirect = {}
URLS_POST = {}


def route(*urls, method=Method.GET, authorize=None, ajax=False, title='', redirect=False):
    # global URLS, URLS_POST
    def actual_decorator(func):
        def ajax_func(request):
            ajax_dict = {
                'html': func(request),
                'title': title
            }
            return json.dumps(ajax_dict)

        # nonlocal urls
        for url in urls:
            if url != '/':
                url = '/' + url.strip('/')
            if method == Method.GET:
                if redirect:
                    URLS_GET_redirect[url] = func
                if ajax is True:
                    URLS_GET[url] = ajax_func
                else:
                    URLS_GET[url] = func
            elif method == Method.POST:
                URLS_POST[url] = func

            if authorize is not None:
                copy_auth = authorize.get_copy()
                copy_auth.url = url
                AUTHORIZE.append(copy_auth)

        return func

    return actual_decorator


def redirect_to(request, url=None, method=Method.GET, is_manual=False):
    if url is None:
        url = request.path

#     if 'Set-Cookie' in request.response.headers:
#         return f'''
#         <head>
#   <meta http-equiv="refresh" content="0; URL={url}" />
# </head>
# '''.encode()
    if not is_manual:
        request.response.code = 302
        request.response.send_header('Location', url)
        request.response.send_header('KEK', '1234567890')
    return ''
