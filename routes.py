from enum import Enum

class Method(Enum):
    GET = 1
    POST = 2


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


def route(url, method= Method.GET):
    global URLS, URLS_POST
    def actual_decorator(func):
        if method == Method.GET:
            URLS[url] = func
        elif method == Method.POST:
            URLS_POST[url] = func

        return func

    return actual_decorator
