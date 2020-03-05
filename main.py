import socket, re, os, json
from collections import defaultdict
from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs, urlsplit
from http import cookies

from auth import get_auth
from error import *
from routes import *
from helper import get_content_type
from chat_websocket import start_asyncio
import views

import controllers

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
        if method == 'GET' and url not in URLS:
            code = 404
        elif method == 'POST' and url not in URLS_POST:
            code = 404
        if code == 200:
            code = get_auth(request)

    request.response.code = code
    request.response.content_type = content_type
    return code


def generate_content(request, method, code, url):
    if code in (401, 404, 405):
        return my_error(code)  # b'<h1>404</h1><p>Not found</p>'
    if code == 301:
        return redirect_to(request)
    if re.match(r'^/static', url):
        return get_static_file(url)
    else:
        if method == 'GET':
            return URLS[url](request)
        if method == 'POST':
            return URLS_POST[url](request)


def send_headers(request):
    request.send_response(request.response.code)
    for k, v_list in request.response.headers.items():
        for v in v_list:
            request.send_header(k, v)
    request.end_headers()


def generate_response(request):
    method, url = request.command, request.path

    code = generate_headers(request, method, url)
    body = generate_content(request, method, code, url)

    send_headers(request)
    request.wfile.write(body)


class Response:
    def __init__(self, request):
        self.request = request
        self.wfile = request.wfile

        self.code = 200
        self.headers = defaultdict(list)
        self.send_header('content_type', 'text/html')

    def send_header(self, key, value):
        self.headers[key].append(value)

    def send_cookie(self, key, value, path='/'):
        self.send_header('Set-Cookie', f"{key}={value}; path={path}")

    def remove_cookie(self, key):  # Set-Cookie: token=deleted; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT
        self.send_header('Set-Cookie', f"{key}=deleted; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT")


class CustomServer(BaseHTTPRequestHandler):
    def _init(self):
        self.response = Response(self)
        self.parse_cookies()
        self.POST_query = None

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
        ctype, pdict = parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            postvars = parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            str = self.rfile.read(length).decode('utf-8')
            postvars = parse_qs(
                str,
                keep_blank_values=1)
        else:
            postvars = {}
        return postvars

    def parse_query_GET(self):
        self.query = parse_qs(urlsplit(self.path).query)
        self.path = urlsplit(self.path).path

    def parse_cookies(self):
        self.cookies = self.headers['Cookie']
        if self.cookies is not None:
            c = cookies.SimpleCookie(self.cookies)
            self.cookies = dict(map(lambda x: (x.key, x.value), dict(c).values()))
        else:
            self.cookies = {}


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass


def run():
    start_asyncio()

    server = ThreadingSimpleServer(('localhost', 8000), CustomServer)
    server.serve_forever()

print("Run Server...")
run()
# url = '/static/js/MyJS.js'
# print(re.match(r'^/static', url) )
