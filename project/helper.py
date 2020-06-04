import os
from uuid import uuid1
from enum import Enum, auto
import hashlib

content_types = {
    '.ico': 'image/vnd.microsoft.icon',
    '.html': 'text/html',
    '.js': 'text/javascript',
    '.css': 'text/css'
}

R = "\033[0;31;40m"  # RED
G = "\033[0;32;32m"  # GREEN
Y = "\033[0;33;40m"  # Yellow
B = "\033[0;35;36m"  # Blue
N = "\033[0m"  # Reset
BOLD = '\033[1m'


def get_content_type(path):
    extension = os.path.splitext(path)[1]
    if extension in content_types:
        return content_types[extension]
    else:
        return 'multipart/form-data'


def find_first(pred, iterable):
    return next(filter(pred, iterable), None)


def try_to_int(text, null=None):
    try:
        return int(text)
    except ValueError:
        return null
    except TypeError:
        return null


def try_jsbool_to_bool(text, null=None):
    if text == 'true':
        return True
    elif text == 'false':
        return False
    return null


def convert_pass_to_passhash(password):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    password_hex = (salt + key).hex()
    return password_hex


def equal_passhash(valid_byte_pass, password):
    valid_pass = bytes.fromhex(valid_byte_pass)
    salt, valid_key = valid_pass[:32], valid_pass[32:]
    key = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    return valid_key == key


def convert_args_to_querystr(joinstr, query, is_str=True, key=None):
    convert_value = lambda value: f'"{value}"' if is_str else value
    if key is None:
        return joinstr.join([f'{key}={convert_value(value)}' for key, value in query.items()])
    else:
        return joinstr.join([f'{key}={convert_value(value)}' for value in query])


def save_photo(photodata):
    if not photodata:
        return None
    u = uuid1()
    filename = 'static/other/' + str(u.hex) + '.jpg'
    file = open(filename, 'wb')
    file.write(photodata)
    file.close()
    return filename


class ManageNavPages:
    class Pages(Enum):
        INDEX = auto()
        EDIT_PASSWORD = auto()

    @staticmethod
    def page_nav_class(vars, target_active):
        if vars['active_page'] == target_active:
            return 'active'
        return ''

    @staticmethod
    def index_nav(vars):
        return ManageNavPages.page_nav_class(vars, ManageNavPages.Pages.INDEX)

    @staticmethod
    def edit_nav(vars):
        return ManageNavPages.page_nav_class(vars, ManageNavPages.Pages.EDIT_PASSWORD)
