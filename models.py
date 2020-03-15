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
    counter = 1

    def __init__(self, id, login, password, nickname, email, photopath, roles=None):
        if not roles:
            roles = {UserRole.USER}
        self.id = id
        self.login = login
        self.password = password
        self.nickname = nickname
        self.email = email
        self.photopath = photopath
        self.roles = set(roles)
        User.counter += 1

    def get_email(self):
        return self.email if self.email else ''


class Session:
    counter = 1001

    def __init__(self, id, user_id):
        self.id = id
        self.user_id = user_id
        self.user = None


if __name__ == "__main__":
    a = UserRole.USER
    b = str(a)

    print(UserRole["USER"])
    print(UserRole(1))
