import socket, re, os, json
from collections import defaultdict
from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs, urlsplit, urlparse
from http import cookies
import ssl, threading

from auth import get_auth
from error import *
from routes import *
from helper import get_content_type, G, N
from chat_websocket import start_asyncio
import db
import models
import config
from render import render_base_main

import controllers



def log_request(request):
    if request.auth_session is not None:
        user = request.auth_get_user()
        print(G + 'Session_id: ', request.auth_session.user_id, ' |  user_id: ', user.id, ' |  login: ', user.login,
              ' |  path: ', request.path + N)
    else:
        print(G + 'null' + N)


def get_static_file(url):
    with open(url[1:], 'rb') as file:
        return file.read()


def generate_headers(request, method, url):
    code = 200
    content_type = "text/html"
    if method not in ('GET', 'POST'):
        code = 405
    elif re.match(r'^/static', url):
        if os.path.isfile(url[1:]):
            subp = url[8:]
            content_type = get_content_type(subp)

        else:
            code = 404
    else:
        if re.match(r'^/json', url):
            content_type = 'application/json'
        if method == 'GET' and url not in URLS_GET and url not in URLS_GET_ajax:
            code = 404
        elif method == 'POST' and url not in URLS_POST:
            code = 404
        code2 = get_auth(request)
        code = code2 if code == 200 else code

    request.response.code = code
    request.response.content_type = content_type
    return code


def generate_content(request, method, code, url, is_ajax):
    if str(code)[0] == '4':
        return my_error(request, is_ajax=True).encode('utf-8')  # b'<h1>404</h1><p>Not found</p>'
    if code == 302:
        return redirect_to(request)
    if re.match(r'^/static', url):
        return get_static_file(url)
    else:
        log_request(request)
        if method == 'GET':
            # if is_ajax:
            #     func = URLS_GET_ajax.get(url)
            #     if func is None:
            #         return b''
            #     return URLS_GET_ajax[url](request).encode('utf-8')
            return URLS_GET[url](request).encode('utf-8')
        if method == 'POST':
            return URLS_POST[url](request).encode('utf-8')


def send_headers(request):
    request.send_response(request.response.code)
    request.response.send_header('Content-Type', request.response.content_type)
    for k, v_list in request.response.headers.items():
        for v in v_list:
            request.send_header(k, v)
    request.end_headers()


def generate_response(request):
    method, url = request.command, request.path


    code = generate_headers(request, method, url)
    if url in URLS_GET_redirect or method == 'POST' or re.match(r'^/json', url) or re.match(r'^/static', url) or 'ajax' in request.headers:
        body = generate_content(request, method, code, url, 'ajax' in request.headers)
    else:
        body = render_base_main(request).encode('utf-8')

    request.response.send_header('Content-Length', len(body))
    send_headers(request)
    request.wfile.write(body)


class Response:
    def __init__(self, request):
        self.request = request
        self.wfile = request.wfile

        self.code = 200
        self.content_type = 'text/html'
        self.headers = defaultdict(list)

    def send_header(self, key, value):
        self.headers[key].append(value)

    def send_cookie(self, key, value, path='/'):
        self.send_header('Set-Cookie', f"{key}={value}; path={path}; expires=Thu, 01 Jan 2050 00:00:00 GMT")

    def remove_cookie(self, key):  # Set-Cookie: token=deleted; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT
        self.send_header('Set-Cookie', f"{key}=deleted; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT")


class QueryDict(dict):
    def __init__(self, query_dict):
        super().__init__()
        self.update(**query_dict)

    def get2(self, key, null=None):
        return self.get(key, [null])[0]

    def getmany(self, key, null=None):
        return self.get(key, null)


class RedirectCustomServer(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def redirect(self):
        newpath = f'https://{config.HOST}{self.path}'
        self.send_response(302)
        self.send_header('Content-Length', '0')
        self.send_header('Location', newpath)
        self.end_headers()
        self.wfile.write(b'')

    def do_GET(self):
        self.redirect()

    def do_POST(self):
        self.redirect()


class CustomServer(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def _init(self):
        # self.protocol_version = 'HTTP/1.1'
        self.response = Response(self)
        self.parse_cookies()
        self.query = None
        self.POST_query = None
        self.auth_is = False
        self.auth_session = None
        self._auth_user = False

    def auth_get_user(self, none=None) -> models.User:
        if self.auth_session and self._auth_user is False:
            user = db.find_user(id=self.auth_session.user_id)
            self._auth_user = user if user else none
        return self._auth_user

    def _set_headers(self):
        self.send_response(200)
        # self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._init()
        self.parse_query_GET()
        generate_response(self)

    def do_POST(self):
        self._init()
        self.POST_query = self.parse_POST()
        print("POST:", self.POST_query)
        generate_response(self)

    def parse_POST(self):
        kek = self.headers['content-type']
        ctype, pdict = parse_header(kek)
        if ctype == 'multipart/form-data':
            pdict['boundary'] = pdict['boundary'].encode('ascii')
            pdict['CONTENT-LENGTH'] = self.headers['content-length']
            postvars = parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            str = self.rfile.read(length).decode('utf-8')
            postvars = parse_qs(
                str,
                keep_blank_values=1)
        else:
            postvars = {}
        return QueryDict(postvars)

    def parse_query_GET(self):
        self.query = parse_qs(urlsplit(self.path).query)
        self.query = QueryDict(self.query)
        self.path = urlsplit(self.path).path
        if self.path != '/':
            self.path = self.path.rstrip('/')

    def parse_cookies(self):
        self.cookies = self.headers['Cookie']
        if self.cookies is not None:
            c = cookies.SimpleCookie(self.cookies)
            self.cookies = dict(map(lambda x: (x.key, x.value), dict(c).values()))
        else:
            self.cookies = dict()


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass


def run():
    db.Connect()
    start_asyncio()

    def start_http_server():
        server = ThreadingSimpleServer(config.SOCKET_HTTP, RedirectCustomServer)
        server.serve_forever()

    chat_service = threading.Thread(target=start_http_server)
    chat_service.start()

    server2 = ThreadingSimpleServer(config.SOCKET_HTTPS, CustomServer)
    server2.socket = ssl.wrap_socket(server2.socket, 
                                     certfile=config.SSL_CERT_PEM_PATH,
                                     keyfile=config.SSL_KEY_PEM_PATH,
                                     server_side=True)
    server2.serve_forever()


print("Run Server...")
run()
# url = '/static/js/MyJS.js'
# print(re.match(r'^/static', url) )
