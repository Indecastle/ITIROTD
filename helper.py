import os
from uuid import uuid1
from enum import Enum, auto

content_types = {
    '.ico': 'image/vnd.microsoft.icon',
    '.html': 'text/html',
    '.js': 'text/javascript',
    '.css': 'text/css'
}


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
