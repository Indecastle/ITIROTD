import socket, re, os, json
from collections import defaultdict
from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs, urlsplit
from views import *
from routes import *
from helper import get_content_type
from chat_websocket import start_asyncio
from auth import get_auth


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

    request.response.code = code
    request.response.content_type = content_type
    return code


def generate_content(request, method, code, url):
    if code in (404, 405):
        return my_error(code)  # b'<h1>404</h1><p>Not found</p>'
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

    get_auth(request)
    code = generate_headers(request, method, url)
    body = generate_content(request, method, code, url)

    send_headers(request)
    request.wfile.write(body)


class Response:
    def __init__(self, request):
        self.request = request
        self.wfile = request.wfile
        self.send_header = request.send_header

        self.code = 200
        self.headers = defaultdict(list)
        self.headers['content_type'].append("text/html")
        self.POST_query = None


class CustomServer(BaseHTTPRequestHandler):
    def _init(self):
        self.response = Response(self)

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
        self.response.POST_query = self.parse_POST()
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
