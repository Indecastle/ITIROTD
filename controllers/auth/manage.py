from routes import route, Method, redirect_to
from render import render_template
from auth import *
from helper import find_first, save_photo
from error import *
from db import create_user, find_user


@route('auth/manage/',
       'auth/manage/index/', authorize=Authorize([UserRole.USER]))
def myauth(request, **kwargs):
    user = request.auth_get_user()
    kwargs.setdefault('user', user)
    return render_template(request, 'templates/auth/manage/index.html', **kwargs)
