from routes import route, Method, redirect_to
from render import render_template
from auth import *
from helper import find_first, save_photo, equal_passhash, convert_pass_to_passhash
from error import *
import db
from chat_websocket import update_chat_user


@route('auth/manage/',
       'auth/manage/index/', authorize=Authorize([UserRole.USER]), ajax=True)
def manage_index(request, **kwargs):
    user = request.auth_get_user()
    kwargs.setdefault('user', user)
    return render_template(request, 'templates/auth/manage/index.html', kwargs=kwargs)


@route('auth/manage/change_profile', method=Method.POST, authorize=Authorize())
def manage_index_POST(request):
    data = request.POST_query
    nickname, email, photodata = data["name"][0], data['email'][0], data['photo'][0]
    user = request.auth_get_user()

    e = {'name': nickname.strip(), 'email': email.strip()}
    if photodata:
        photopath = save_photo(photodata)
        e.update(photopath=photopath)
    update_chat_user(user.id, e)
    db.update_user(user.id, **e)

    return redirect_to(request, '/auth/manage/index/')


@route('auth/manage/edit_password', authorize=Authorize(), ajax=True)
def manage_edit_password(request, **kwargs):
    kwargs.setdefault('message', '')
    return render_template(request, 'templates/auth/manage/edit_password.html', kwargs=kwargs)


@route('auth/manage/edit_password', method=Method.POST, authorize=Authorize())
def manage_edit_password_POST(request, **kwargs):
    data = request.POST_query
    old_password, new_password, confirm_password = data["old_password"][0].strip(), data["new_password"][0].strip(), \
                                                   data["confirm_password"][0].strip()
    user = request.auth_get_user()
    print(old_password, new_password, confirm_password)
    if not old_password or not new_password or not confirm_password or \
            new_password != confirm_password or not equal_passhash(user.password, old_password):
        kwargs.setdefault('message', 'bad password')
        return render_template(request, 'templates/auth/manage/edit_password.html', kwargs=kwargss)
    pass_hex = convert_pass_to_passhash(new_password)
    db.update_user(user.id, password=pass_hex)
    return redirect_to(request, '/auth/manage/index/')
