from contextlib import closing
import pymysql.cursors
from tabulate import tabulate
from models import *
from pprint import pprint
import threading
from helper import find_first
from config import DB

lock = threading.RLock()
connection = None


# Connect to the database
def Connect():
    global connection
    connection = pymysql.connect(**DB)


def convert_args_to_querystr(joinstr, **vargs):
    return joinstr.join([f'{key}="{value}"' for key, value in vargs.items()])


def execute(request, args=None, limit=None):
    with connection.cursor() as cursor:
        with lock:
            try:
                cursor.execute(request, args)
                rows = cursor.fetchmany(limit) if limit else cursor.fetchall()
                desc = list(map(lambda d: d[0], cursor.description)) if cursor.description else ()
                return desc, rows
            except pymysql.err.InterfaceError as e:
                Connect()
                raise Exception('InterfaceError')


def select_rows(name_table, columns='*', where='', limit=None):
    return execute(f'SELECT {columns} FROM {name_table} {where};', limit=limit)


def convert_to_user(row, roles):
    roles = list(map(lambda r: UserRole(r[1]), roles)) if roles else ()
    # print(roles)
    user = User(*row, roles=roles)
    return user


def get_users(limit=None, where=''):
    users = select_rows('users', columns='id, login, password, name, photopath, email', where=where, limit=limit)
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


def find_user_by_sessionid(id):
    session = find_session(id)
    if session:
        user = find_user(id=session.user_id)
        return user
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


# def get_next_AUTO_INCREMENT(table):
#     rows = execute(f"""
#         SELECT AUTO_INCREMENT
#         FROM information_schema.TABLES
#         WHERE TABLE_SCHEMA = "ITIROTD"
#         AND TABLE_NAME = "{table}";
#     """)
#     if rows and rows[1]:
#         return rows[1][0][0]
#     return None
#
#
# def get_LAST_INSERT_ID():
#     rows = execute("SELECT LAST_INSERT_ID();")
#     if rows and rows[1]:
#         return rows[1][0][0]
#     return None


def create_user(login, password, name, photopath):
    with connection.cursor() as cursor:
        with lock:
            user = find_user(login=login)

            if user is None:
                cursor.execute("INSERT INTO users (login, password, name, photopath) VALUES (%s, %s, %s, %s);",
                               (login, password, name, photopath))
                connection.commit()
                return cursor.lastrowid
            return None


def create_session(id_user):
    with connection.cursor() as cursor:
        with lock:
            cursor.execute("INSERT INTO sessions (id_user) VALUES (%s);", (id_user))
            connection.commit()
            return cursor.lastrowid


# ======================================================

def create_message(chat_id, user_id, when, text):
    with connection.cursor() as cursor:
        with lock:
            cursor.execute("INSERT INTO messages (chat_id, users_id, `when`, text) VALUES (%s, %s, %s, %s);",
                           (chat_id, user_id, when, text))
            connection.commit()
            return cursor.lastrowid


def get_messages(chat_id, limit=None):
    messages_ref = select_rows('messages', columns='id, chat_id, users_id, `when`, text',
                               where='WHERE chat_id=%s' % chat_id, limit=limit)
    if messages_ref and messages_ref[1]:
        return list(map(lambda m: Message(*m), messages_ref[1]))
    return None


# ======================================================


def convert_to_chat(row, users_ref, messages):
    users = list(map(lambda u: User(*u), users_ref)) if users_ref else None
    log_users = []
    if messages:
        for m in messages:
            m.user = find_first(lambda u: u.id == m.user_id, users)
            if m.user is None:
                m.user = find_first(lambda u: u.id == m.user_id, log_users)
                if m.user is None:
                    m.user = find_user(id=m.user_id)
                    log_users.append(log_users)

    # print(users)
    chat = Chat(*row, users=users, messages=messages)
    return chat


def create_chat(name, secure, user_id, password=None):
    with connection.cursor() as cursor:
        with lock:
            cursor.execute("INSERT INTO chat (name, secure, password) VALUES (%s, %s, %s);", (name, secure, password))
            connection.commit()
            chat_id = cursor.lastrowid
            cursor.execute("INSERT INTO chat_has_users (chat_id, users_id) VALUES (%s, %s);", (chat_id, user_id))
            connection.commit()
            return chat_id


def _get_chats_sql(chats_sql, is_messages=False, is_users=False, limit=None):
    if chats_sql and chats_sql[1]:
        chats_obj = []
        for row in chats_sql[1]:
            if is_users:
                users_ref = execute("SELECT users.* FROM chat_has_users "
                                    "inner join users on chat_has_users.users_id=users.id "
                                    "WHERE chat_id=%s;", row[0], limit=limit)[1]
            else:
                users_ref = None
            messages = get_messages(row[0]) if is_messages else None
            chat = convert_to_chat(row, users_ref, messages)
            chats_obj.append(chat)
        return chats_obj
    return None


def get_chats(limit=None, where='', is_messages=False, is_users=False):
    chats = select_rows('chat', columns='id, name, secure, password', where=where, limit=limit)
    return _get_chats_sql(chats, is_messages=is_messages, is_users=is_users)


def get_chats_by_user(user_id, chat_id=None, is_messages=False, is_users=False, limit=None):
    where_args = {'users_id': user_id}
    if chat_id is not None:
        where_args.update(chat_id=chat_id)
    where_sql = convert_args_to_querystr(' AND ', **where_args)

    chats = execute("SELECT chat.* FROM chat_has_users "
                    "INNER JOIN chat on chat_has_users.chat_id=chat.id "
                    f"WHERE {where_sql};", limit=limit)
    chats_obj = _get_chats_sql(chats, is_messages=is_messages, is_users=is_users)
    if chats_obj is None or chat_id is None:
        return chats_obj
    return chats_obj[0]


def find_chat(where={}, is_messages=False, is_users=False):
    str_args = convert_args_to_querystr(' AND ', **where)
    chats = get_chats(where='WHERE %s' % str_args, is_messages=is_messages, is_users=is_users)
    return chats[0] if chats else None


# ======================================================


def update_user(id_user, **vargs):
    str_args = convert_args_to_querystr(', ', **vargs)
    return execute(f"UPDATE users SET {str_args} WHERE id=%s", id_user)


if __name__ == "__main__":
    pass
    Connect()
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

    # with connection.cursor() as cursor:
    #     cursor.execute("INSERT INTO sessions (id_user) VALUES (%s);", 25)
    #     connection.commit()
    #     print(cursor.lastrowid)

    # chats = get_chats()
    # print(chats)

    chats = get_chats_by_user(37, is_messages=True)
    print(chats)
