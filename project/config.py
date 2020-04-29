import pathlib, os

SOCKET_HTTP = ('', 80)
SOCKET_HTTPS = ('', 443)
WEBSOCKET_CHAT_PATH = ('', 6789)

DB = {
    'host': os.getenv('server_database_host'),
    'port': int(os.getenv('server_database_port')),
    'user': os.getenv('server_database_username'),
    'password': os.getenv('server_database_password'),
    'db': 'ITIROTD',
    'charset': 'utf8mb4',
    'autocommit': True
}


SSL_PEM_PATH = pathlib.Path(__file__).with_name("server.pem")
# print(SSL_PEM_PATH)