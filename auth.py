from typing import Dict, List, Tuple
from enum import Enum, auto
from helper import find_first


class UserRole(Enum):
    USER = auto()
    ADMIN = auto()


class Authorize:
    def __init__(self, roles=None):
        self.roles = set(roles) if roles is not None else set()
        self.url = None


class User:
    counter = 1

    def __init__(self, nickname, password, roles=None):
        if roles is None:
            roles = {UserRole.USER}
        self.id = User.counter
        self.nickname = nickname
        self.password = password
        self.roles = set(roles)
        User.counter += 1


class Session:
    counter = 1001

    def __init__(self, user):
        self.id = str(Session.counter)
        self.user = user
        Session.counter += 1


USERS: List[User] = [User("admin", "123", roles=[UserRole.ADMIN, UserRole.USER]), User("user", "abc")]
SESSIONS: List[Session] = []
AUTHORIZE: List[Authorize] = []


def create_session(request, user):
    # user = User(roles=[UserRole.USER])
    session = Session(user)
    USERS.append(user)
    SESSIONS.append(session)
    request.response.send_cookie('SessionId', session.id)
    request.response.send_cookie('nickname', user.nickname)


def delete_session(request):
    request.response.remove_cookie('SessionId')
    request.response.remove_cookie('nickname')


def isvalid_cookie(request) -> bool:
    cookie = request.cookies
    sid = cookie.get('SessionId')
    if cookie is not None and 'SessionId' in cookie and all(sid != s.id for s in SESSIONS):
        delete_session(request)
        return False
    return True


def check_authpage(request):
    return any(request.path == a.url for a in AUTHORIZE)


def check_authrole(request):
    cookie = request.cookies
    sid = cookie.get('SessionId')
    session: Session = find_first(lambda s: sid == s.id, SESSIONS)
    authorize: Authorize = find_first(lambda a: request.path == a.url, AUTHORIZE)
    if session is not None and authorize is not None:
        if authorize.roles & session.user.roles or not authorize.roles:
            return True
    return False


def get_auth(request):
    if not isvalid_cookie(request):
        return 302
    if check_authpage(request):
        if check_authrole(request):
            return 200
        else:
            # create_session(request)
            return 401

    return 200
