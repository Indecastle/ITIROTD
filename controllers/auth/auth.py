import json

from routes import route, Method, redirect_to
from render import render_template
from auth import *
from helper import find_first
from error import *
from db import create_user, find_user


@route('auth')
def myauth(request, **kwargs):
    kwargs.setdefault('message', '')
    return render_template(request, 'templates/auth/login.html', **kwargs).encode()


@route('/auth/login', Method.POST)
def myauth_login_POST(request):
    data = request.POST_query
    nickname, password = data["username"][0], data["password"][0]

    user = find_user(name=nickname)
    if user is not None:
        if user.password == password:
            create_session(request, user.nickname, user.id)
            return redirect_to(request, '/')
    else:
        pass

    kwargs = {'message': "Not valid user"}
    return render_template(request, 'templates/auth/login.html', **kwargs).encode()


@route('/auth/register', Method.POST)
def myauth_register_POST(request):
    data = request.POST_query
    nickname, password, email = data["username"][0], data["password"][0], data['email'][0]

    user = find_user(name=nickname)
    if user is None:
        user_id = create_user(nickname, password)
        create_session(request, nickname, user_id)
        return redirect_to(request, '/')
    else:
        pass

    kwargs = {'message': "Not valid user"}
    return render_template(request, 'templates/auth/login.html', **kwargs).encode()


@route('/auth/logout')
def myauth_logout_POST(request):
    delete_session(request)
    return redirect_to(request, '/')
