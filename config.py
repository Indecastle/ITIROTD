import pathlib

SOCKET_HTTP = ('', 80)
SOCKET_HTTPS = ('', 443)
WEBSOCKET_CHAT_PATH = ('', 6789)

DB = {
    'host': '13.48.235.180',
    'port': 3409,
    'user': 'user',
    'password': 'user',
    'db': 'ITIROTD',
    'charset': 'utf8mb4',
    'autocommit': True
}


SSL_PEM_PATH = pathlib.Path(__file__).with_name("server.pem")
# print(SSL_PEM_PATH)