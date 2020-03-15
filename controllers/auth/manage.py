from routes import route, Method, redirect_to
from render import render_template
from auth import *
from helper import find_first, save_photo
from error import *
import db


@route('auth/manage/',
       'auth/manage/index/', authorize=Authorize([UserRole.USER]))
def manage_index(request, **kwargs):
    user = request.auth_get_user()
    kwargs.setdefault('user', user)
    return render_template(request, 'templates/auth/manage/index.html', **kwargs)


@route('auth/manage/change_profile', method=Method.POST, authorize=Authorize())
def manage_index_POST(request):
    data = request.POST_query
    nickname, email, photodata = data["name"][0], data['email'][0], data['photo'][0]
    user = request.auth_get_user()

    e = {'name': nickname.strip(), 'email': email.strip()}
    if photodata:
        photopath = save_photo(photodata)
        e.update(photopath=photopath)

    db.update_user(user.id, **e)

    return redirect_to(request, '/auth/manage/index/')


@route('auth/manage/edit_password', authorize=Authorize())
def manage_edit_password(request, **kwargs):
    kwargs.setdefault('message', '')
    return render_template(request, 'templates/auth/manage/edit_password.html', **kwargs)


@route('auth/manage/edit_password', method=Method.POST, authorize=Authorize())
def manage_edit_password_POST(request, **kwargs):
    data = request.POST_query
    new_password = data["new_password"][0].strip()
    user = request.auth_get_user()

    if not new_password:
        kwargs.setdefault('message', 'bad password')
        return render_template(request, 'templates/auth/manage/edit_password.html', **kwargs)

    db.update_user(user.id, password=new_password)
    return redirect_to(request, '/auth/manage/index/')
