import os

content_types = {
    '.ico': 'image/vnd.microsoft.icon',
    '.html': 'text/html',
    '.js': 'text/javascript',
    '.css': 'text/css'
}


def get_content_type(path):
    extension = os.path.splitext(path)[1]
    return content_types[extension]


def find_first(pred, iterable):
    return next(filter(pred, iterable), None)
