import pathlib, os

SOCKET_HTTP = ('', 80)
SOCKET_HTTPS = ('', 443)
WEBSOCKET_CHAT_PATH = ('', 6789)

HOST = os.getenv('server_host')

DB = {
    'host': os.getenv('server_database_host'),
    'port': int(os.getenv('server_database_port')),
    'user': os.getenv('server_database_username'),
    'password': os.getenv('server_database_password'),
    'db': 'ITIROTD',
    'charset': 'utf8mb4',
    'autocommit': True
}


SSL_CERT_PEM_PATH = os.getenv('server_cert_pem_path')
SSL_KEY_PEM_PATH = os.getenv('server_key_pem_path')
# print(SSL_PEM_PATH)