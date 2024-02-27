import os, time, hashlib
import pprint
from typing import List

import db
from helper import find_first
from models import *

USERS: List[User] = []
SESSIONS: List[Session] = []
AUTHORIZE: List[Authorize] = []


def create_session(request, login, user_id):
    salt = os.urandom(32)
    hash_object = hashlib.sha512(salt + str(user_id).encode('utf-8'))
    hash = hash_object.hexdigest()
    when = int(time.time())
    session_id = db.create_session(user_id, hash, when)
    if session_id is not None:
        request.response.send_cookie('SessionHash', hash)
        request.response.send_cookie('user_id', user_id)
        request.response.send_cookie('login', login)
    return hash, user_id


def delete_session(request):
    request.response.remove_cookie('SessionHash')
    request.response.remove_cookie('user_id')
    request.response.remove_cookie('login')


def get_session(request):
    cookie = request.cookies
    sh = cookie.get('SessionHash')
    uid = cookie.get('user_id')
    if 'SessionHash' in cookie:
        session = db.find_session(uid, sh)
        if session:
            return session
    return None


def isvalid_cookie(request, session) -> bool:
    if 'SessionHash' in request.cookies:
        if session is None:
            return False
        else:
            request.auth_is = True
            request.auth_session = session
    return True


def check_authpage(request):
    return any(request.path == a.url for a in AUTHORIZE)


def check_authrole(request, session):
    user = request.auth_get_user()
    authorize: Authorize = find_first(lambda a: request.path == a.url, AUTHORIZE)
    if session is not None and authorize is not None:
        if authorize.roles & user.roles or not authorize.roles:
            return True
    return False


def get_auth(request):
    try:
        session = get_session(request)
    except Exception as e:
        return 405
    if not isvalid_cookie(request, session):
        delete_session(request)
        return 302
    if check_authpage(request):
        if not (session and check_authrole(request, session)):
            return 401

    return 200
