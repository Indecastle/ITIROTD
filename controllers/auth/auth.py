import json

from routes import route, Method, redirect_to
from render import render_template
from auth import *
from helper import find_first, save_photo, equal_passhash, convert_pass_to_passhash
from error import *
from db import create_user, find_user


@route('auth/login')
def myauth(request, **kwargs):
    kwargs.setdefault('message', '')
    return render_template(request, 'templates/auth/login.html', **kwargs)


@route('/auth/login', method=Method.POST)
def myauth_login_POST(request):
    data = request.POST_query
    login, password = data["login"][0], data["password"][0]

    user = find_user(login=login)
    if user is not None:
        if equal_passhash(user.password, password):
            create_session(request, user.login, user.id)
            return redirect_to(request, '/')
    else:
        pass

    kwargs = {'message': "Not valid user"}
    return render_template(request, 'templates/auth/login.html', **kwargs)


@route('auth/register')
def myauth(request, **kwargs):
    kwargs.setdefault('message', '')
    return render_template(request, 'templates/auth/register.html', **kwargs)


@route('/auth/register', method=Method.POST)
def myauth_register_POST(request):
    data = request.POST_query
    login, password, nickname, photodata = data.get2('login'), data.get2('password'), data.get2('nickname'), \
                                           data.get2('photodata', '')

    user = find_user(login=login)
    if user is None:
        photopath = save_photo(photodata)
        pass_hex = convert_pass_to_passhash(password)
        user_id = create_user(login, pass_hex, nickname, photopath)
        create_session(request, login, user_id)
        return redirect_to(request, '/')
    else:
        pass

    kwargs = {'message': "Not valid user"}
    return render_template(request, 'templates/auth/register.html', **kwargs)


@route('/auth/logout')
def myauth_logout_POST(request):
    delete_session(request)
    return redirect_to(request, '/')
