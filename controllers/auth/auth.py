import json

from routes import route, Method, redirect_to
from render import render_template
from auth import *
from helper import find_first
from error import *


@route('/auth/login')
def myauth(request, **kwargs):
    kwargs.setdefault('message', '')
    return render_template('templates/auth/login.html', **kwargs).encode()


@route('/auth/login', Method.POST)
def myauth_POST(request):
    data = request.POST_query
    nickname, password = data["username"][0], data["password"][0]

    user = find_first(lambda u: nickname == u.nickname, USERS)
    if user is not None:
        if user.password == password:
            create_session(request, user)
            return redirect_to(request, '/')
    else:
        # user = User(nickname, password, roles=[UserRole.USER])
        # USERS.append(user)
        # create_session(request, USERS)
        pass

    kwargs = {'message': "Not valid user"}
    return render_template('templates/auth/login.html', **kwargs).encode()
