from enum import Enum, auto


class UserRole(Enum):
    USER = auto()
    ADMIN = auto()


class Authorize:
    def __init__(self, roles=None):
        self.roles = set(roles) if roles is not None else set()
        self.url = None


class User:
    counter = 1

    def __init__(self, id, nickname, password, roles=None):
        if roles is None or roles == []:
            roles = {UserRole.USER}
        self.id = id
        self.nickname = nickname
        self.password = password
        self.roles = set(roles)
        User.counter += 1


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
