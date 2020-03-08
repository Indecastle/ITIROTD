from typing import Dict, List, Tuple
from helper import find_first
import db
from models import *





USERS: List[User] = []
SESSIONS: List[Session] = []
AUTHORIZE: List[Authorize] = []


def create_session(request, nickname, user_id):
    session_id = db.create_session(user_id)
    if session_id is not None:
        request.response.send_cookie('SessionId', session_id)
        request.response.send_cookie('nickname', nickname)


def delete_session(request):
    request.response.remove_cookie('SessionId')
    request.response.remove_cookie('nickname')


def get_session(request):
    cookie = request.cookies
    sid = cookie.get('SessionId')
    if 'SessionId' in cookie:
        session = db.find_session(sid)
        if session:
            return session
    return None


def isvalid_cookie(request, session) -> bool:
    if 'SessionId' in request.cookies:
        if session is None:
            delete_session(request)
            return False
        else:
            request.auth_is = True
            request.auth_session = session
    return True


def check_authpage(request):
    return any(request.path == a.url for a in AUTHORIZE)


def check_authrole(request, session):
    user = db.find_user(id=session.user_id)
    authorize: Authorize = find_first(lambda a: request.path == a.url, AUTHORIZE)
    if session is not None and authorize is not None:
        if authorize.roles & user.roles or not authorize.roles:
            return True
    return False


def get_auth(request):
    session = get_session(request)
    if not isvalid_cookie(request, session):
        return 302
    if check_authpage(request):
        if session and check_authrole(request, session):
            return 200
        else:
            # create_session(request)
            return 401

    return 200
