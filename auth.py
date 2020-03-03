


class User:
    counter = 1

    def __init__(self):
        self.id = User.counter
        self.nickname = "name" + str(User.counter)
        User.counter += 1


class Session:
    counter = 1001

    def __init__(self, user):
        self.id = Session.counter
        self.user = user
        Session.counter += 1


USERS = []
SESSIONS = []


def get_auth(request):
    Cookie = request.cookies
    if Cookie is None:
        user = User()
        session = Session(user)
        USERS.append(user)
        SESSIONS.append(Session(user))
        request.response.send_cookie('SessionId', str(session.id))
        request.response.send_cookie('nickname', user.nickname)
    else:
        if False:
            pass

    return 200
