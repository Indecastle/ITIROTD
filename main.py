import socket, re, os
from views import *

URLS = {
    '/': index,
    '/blog': blog
}


def get_static_file(url):
    with open(url[1:]) as file:
        return file.read()


def parse_request(request):
    parsed = request.split(' ')
    method = parsed[0]
    url = parsed[1]
    return method, url


def generate_headers(method, url):
    if not method == 'GET':
        return ('HTTP/1.1 405 Method not allowed\n\n', 405)

    if not url in URLS and re.match(r'^/static', url) and not os.path.isfile(url[1:]):
        return ('HTTP/1.1 404 Not found\n\n', 404)

    return ('HTTP/1.1 200 OK\n\n', 200)


def generate_content(code, url):
    if code == 404:
        return '<h1>404</h1><p>Not found</p>'
    if code == 405:
        return '<h1>405</h1><p>Method not allowed</p>'
    if re.match(r'^/static', url):
        return get_static_file(url)
    return URLS[url]()


def generate_response(request):
    method, url = parse_request(request)
    headers, code = generate_headers(method, url)
    body = generate_content(code, url)
    
    return (headers + body).encode()


def run():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', 5000))
    server_socket.listen()

    while True:
        client_socket, addr = server_socket.accept()
        request = client_socket.recv(1024)
        print('=====request======')
        print(request)
        #print()
        print(addr)
        print('=====request end======')

        if request != b'':
            response = generate_response(request.decode('utf-8'))
            print('=====response======')
            print(response)
            print('=====response end======\n')

            client_socket.sendall(response)
        client_socket.close()
        

run()
#url = '/static/js/MyJS.js'
#print(re.match(r'^/static', url) )
