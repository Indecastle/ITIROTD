from enum import Enum, auto


class UserRole(Enum):
    USER = auto()
    ADMIN = auto()


class Authorize:
    def __init__(self, roles=None):
        self.roles = set(roles) if roles is not None else set()
        self.url = None

    def get_copy(self):
        return Authorize(self.roles)


class User:
    def __init__(self, id, login, password, nickname, photopath, email, roles=None):
        if not roles:
            roles = {UserRole.USER}
        self.id = id
        self.login = login
        self.password = password
        self.nickname = nickname
        self.email = email
        self.photopath = photopath
        self.roles = set(roles)

        self.is_reading = False

    def get_email(self):
        return self.email if self.email else ''

    def to_dict(self):
        return {'id': self.id, 'login': self.login, 'nickname': self.nickname, 'email': self.email,
                'is_reading': self.is_reading}


class Session:
    def __init__(self, id, user_id, hash, when):
        self.id = id
        self.user_id = user_id
        self.when = when
        self.hash = hash
        self.user = None


class Chat:
    class Type(Enum):
        PUBLIC = auto()
        SECURE = auto()

    def __init__(self, id, name, secure, password='123', users=None, messages=None, log_users=None):
        if users is None: users = []
        if messages is None: messages = []
        if log_users is None: log_users = []
        self.id = id
        self.name = name
        self.secure = Chat.Type(secure)
        self.password = password
        self.users = users
        self.log_users = log_users
        self.messages = messages


class Message:
    def __init__(self, id, chat_id, user_id, when, text, isreaded=True):
        self.id = id
        self.chat_id = chat_id
        self.user_id = user_id
        self.when = when
        self.text = text

        self.user = None
        self.isreaded = isreaded

    def to_dict(self):
        return {'id': self.id, 'user_id': self.user_id, 'when': self.when, 'text': self.text,
                'isreaded': self.isreaded}


if __name__ == "__main__":
    a = UserRole.USER
    b = str(a)

    print(UserRole["USER"])
    print(UserRole(1))

    print(Chat.Type(1))
    print(Chat.Type(2))
