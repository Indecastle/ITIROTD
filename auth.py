


class User:
    counter = 1

    def __init__(self):
        self.id = User.counter
        self.nickname = "name" + str(User.counter)
        User.counter += 1


class Session:
    counter = 1001

    def __init__(self, user):
        self.id = str(Session.counter)
        self.user = user
        Session.counter += 1


USERS = []
SESSIONS = []


def create_session(request):
    user = User()
    session = Session(user)
    USERS.append(user)
    SESSIONS.append(session)
    request.response.send_cookie('SessionId', session.id)
    request.response.send_cookie('nickname', user.nickname)


def get_auth(request):
    cookie = request.cookies
    sid = cookie.get('SessionId')
    if cookie is None or 'SessionId' not in cookie or all(sid != s.id for s in SESSIONS):
        create_session(request)

    return 200

