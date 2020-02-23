import socket, re, os, json
from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs, urlsplit
from views import *

URLS = {
    '/favicon.ico': ico,
    '/': index,
    '/blog': blog,
    '/chat': chat
}


def get_static_file(url):
    with open(url[1:]) as file:
        return file.read().encode()


def generate_headers(request, method, url):
    code = 200
    content_type = "text/html"
    if method not in ('GET', 'POST'):
        code = 405
    elif re.match(r'^/static', url):
        if os.path.isfile(url[1:]):
            r = re.match(r'^/static/(\w+)/', url)
            if r is not None:
                content_type_folder = r.group(1)
                content_type = 'text/' + content_type_folder
            else:
                content_type = 'text/plain'
        else:
            code = 404
    else:
        if url not in URLS:
            code = 404

    request.response.code = code
    request.response.content_type = content_type

    return code


def generate_content(request, code, url):
    if code in (404, 405):
        return my_error(code)  # b'<h1>404</h1><p>Not found</p>'
    if re.match(r'^/static', url):
        return get_static_file(url)
    return URLS[url](request)


def send_headers(request):
    request.send_response(request.response.code)
    for k, v in request.response.headers.items():
        request.send_header(k, v)
    request.end_headers()


def generate_response(request):
    method, url = request.command, request.path

    code = generate_headers(request, method, url)
    body = generate_content(request, code, url)

    send_headers(request)
    request.wfile.write(body)


class Response:
    def __init__(self, request):
        self.request = request
        self.wfile = request.wfile
        self.send_header = request.send_header

        self.code = 200
        self.headers = {
            'content_type': "text/html"
        }


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
        self._set_headers()
        postvars = self.parse_POST()
        json_vars = json.dumps(postvars).encode('utf-8')
        self.wfile.write(json_vars)

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
    server = ThreadingSimpleServer(('localhost', 8000), CustomServer)
    server.serve_forever()

print("Run Server...")
run()
# url = '/static/js/MyJS.js'
# print(re.match(r'^/static', url) )
