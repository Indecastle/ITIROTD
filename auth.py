


class User:
    counter = 1

    def __init__(self):
        self.id = User.counter
        self.nickname = "name" + str(User.counter)
        User.counter += 1


class Session:
    counter = 1

    def __init__(self):
        self.id = Session.counter
        Session.counter += 1


USERS = []


def get_auth(request):
    Cookie = request.headers.get("Cookie")
    if Cookie is None:
        user = User()
        USERS.append(user)
        request.response.headers['Set-Cookie'].append("SessionId=" + str(user.id))
        request.response.headers['Set-Cookie'].append("SessionId=" + user.nickname)
