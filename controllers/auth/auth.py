import json

from routes import route, Method, redirect_to
from render import render_template
from auth import *
from helper import find_first, save_photo
from error import *
from db import create_user, find_user


@route('auth')
def myauth(request, **kwargs):
    kwargs.setdefault('message', '')
    return render_template(request, 'templates/auth/login.html', **kwargs)


@route('/auth/login', method=Method.POST)
def myauth_login_POST(request):
    data = request.POST_query
    login, password = data["login"][0], data["password"][0]

    user = find_user(login=login)
    if user is not None:
        valid_pass = bytes.fromhex(user.password)
        salt, valid_key = valid_pass[:32], valid_pass[32:]
        key = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
        if valid_key == key:
            create_session(request, user.login, user.id)
            return redirect_to(request, '/')
    else:
        pass

    kwargs = {'message': "Not valid user"}
    return render_template(request, 'templates/auth/login.html', **kwargs)


@route('/auth/register', method=Method.POST)
def myauth_register_POST(request):
    data = request.POST_query
    login, password, nickname, photodata = data["login"][0], data["password"][0], data['nickname'][0], data['photodata'][0]

    user = find_user(login=login)
    if user is None:
        photopath = save_photo(photodata)

        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
        password2 = (salt + key).hex()

        user_id = create_user(login, password2, nickname, photopath)
        create_session(request, login, user_id)
        return redirect_to(request, '/')
    else:
        pass

    kwargs = {'message': "Not valid user"}
    return render_template(request, 'templates/auth/login.html', **kwargs)


@route('/auth/logout')
def myauth_logout_POST(request):
    delete_session(request)
    return redirect_to(request, '/')
