import os
from uuid import uuid1

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


def save_photo(photodata):
    if not photodata:
        return None
    u = uuid1()
    filename = 'static/other/' + str(u.hex) + '.jpg'
    file = open(filename, 'wb')
    file.write(photodata)
    file.close()
    return filename
