from contextlib import closing
import pymysql.cursors
from tabulate import tabulate
from models import *
from pprint import pprint

# Connect to the database
connection = pymysql.connect(host='192.168.100.5',
                             port=3409,
                             user='test',
                             password='test',
                             db='ITIROTD',
                             charset='utf8mb4',
                             autocommit=True)


def convert_args_to_querystr(joinstr, **vargs):
    return joinstr.join([f'{key}="{value}"' for key, value in vargs.items()])


def execute(request, args=None, limit=None):
    with connection.cursor() as cursor:
        cursor.execute(request, args)
        rows = cursor.fetchmany(limit) if limit else cursor.fetchall()
        desc = list(map(lambda d: d[0], cursor.description)) if cursor.description else ()
        return desc, rows


def select_rows(name_table, columns='*',  where='', limit=None):
    return execute(f'SELECT {columns} FROM {name_table} {where};', limit=limit)


def convert_to_user(row, roles):
    roles = list(map(lambda r: UserRole(r[1]), roles)) if roles else ()
    print(roles)
    user = User(*row, roles=roles)
    return user


def get_users(limit=None, where=''):
    users = select_rows('users', columns='id, login, password, name, email, photopath', where=where, limit=limit)
    if users and users[1]:
        users_obj = []
        for row in users[1]:
            roles_ref = select_rows('users_has_roles', where="WHERE users_id=%s" % row[0])
            user = convert_to_user(row, roles_ref[1])
            users_obj.append(user)
        return users_obj
    return None


def find_user(**vargs):
    str_args = convert_args_to_querystr(' AND ', **vargs)
    users = get_users(where='WHERE %s' % str_args)
    return users[0] if users else None


def convert_to_session(row):
    return Session(*row)


def find_session(id):
    sessions = select_rows('sessions', where='WHERE id="%s"' % id)
    if sessions and sessions[1]:
        session = convert_to_session(sessions[1][0])
        return session
    return None


def get_roles(limit=None):
    return select_rows('roles', limit)


def get_sessions(limit=None, where=''):
    return execute(f"""
        SELECT sessions.id, sessions.id_user, users.name AS username, users.password AS password
        FROM sessions
        inner join users on sessions.id_user = users.id
        {where};
        """)


def get_next_AUTO_INCREMENT(table):
    rows = execute(f""" 
        SELECT AUTO_INCREMENT
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = "ITIROTD"
        AND TABLE_NAME = "{table}";
    """)
    if rows and rows[1]:
        return rows[1][0][0]
    return None


def get_LAST_INSERT_ID():
    rows = execute("SELECT LAST_INSERT_ID();")
    if rows and rows[1]:
        return rows[1][0][0]
    return None


def create_user(login, password, name, photopath):
    with connection.cursor() as cursor:
        user = find_user(login=login)

        if user is None:
            cursor.execute("INSERT INTO users (login, password, name, photopath) VALUES (%s, %s, %s, %s);", (login, password, name, photopath))
            connection.commit()
            return cursor.lastrowid
        return None


def create_session(id_user):
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO sessions (id_user) VALUES (%s);", (id_user))
        connection.commit()
        return cursor.lastrowid


def update_user(id_user, **vargs):
    str_args = convert_args_to_querystr(', ', **vargs)
    return execute(f"UPDATE users SET {str_args} WHERE id=%s", id_user)


if __name__ == "__main__":
    # create_user('kek18', 'lol')
    # u = find_user("ADMIN")
    # print(u.id, u.nickname, u.roles)
    # print(*get_users(), sep='\n')
    # print(*get_sessions(), sep='\n')

    # print(*get_sessions()[1], sep='\n')
    # res = get_sessions()
    # print(tabulate(res[1], headers=res[0]))

    # res2 = select_rows('sessions', 100)
    # print(*res2[1], sep='\n')

    # res3 = find_session(1)
    # print(res3.id, res3.user_id)

    # res4 = get_users()
    # for u in res4:
    #     print(u.id, u.nickname, list(map(lambda r: r.name, u.roles)))

    # result = convert_args_to_querystr(id=2, name='ADMIN')
    # print(result)

    # create_session(13)

    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO sessions (id_user) VALUES (%s);", 25)
        connection.commit()
        print(cursor.lastrowid)
