use ITIROTD;

INSERT INTO users (login, password, name, email) VALUES ('ADMIN', '123', 'ADMIN', 'admin@sobaka.by');
INSERT INTO users (login, password, name) VALUES ('USER', 'abc', 'USER');
SELECT LAST_INSERT_ID();


SELECT * FROM users;
SELECT * FROM users WHERE name='ADMIN';

SELECT sessions.id, users.name AS username, users.password AS password
FROM sessions
inner join users on sessions.id_user = users.id;

INSERT INTO roles (id, name) VALUES (1, "USER"), (2, "ADMIN");

INSERT INTO users_has_roles (users_id, roles_id) VALUES (1, 1), (1, 2);

set global sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION';
set session sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION';

SELECT users.id as id_user, users.name as name_user, roles.id as id_role, roles.name as name_role FROM users_has_roles
inner join users on users_has_roles.users_id = users.id
inner join roles on users_has_roles.roles_id = roles.id;
/*group by users.name;*/

SELECT * FROM users_has_roles WHERE users_id=13;

SELECT users.* FROM chat_has_users
INNER JOIN users on chat_has_users.users_id = users.id
WHERE chat_has_users.chat_id=5;


INSERT INTO chat (name, secure, password) VALUES ("first_chat", 2, "123456");

INSERT INTO chat_has_users (chat_id, users_id) VALUES (7, 37);

SELECT users.* FROM chat_has_users
INNER JOIN users on chat_has_users.users_id!=users.id
WHERE chat_id=1;

SELECT chat.* FROM chat_has_users
INNER JOIN users on chat_has_users.users_id = users.id
INNER JOIN chat on chat_has_users.chat_id = chat.id
WHERE users.id=1;

SELECT chat.* FROM chat
WHERE chat.id not in (
	SELECT chat.id FROM chat_has_users
	INNER JOIN chat on chat_has_users.chat_id = chat.id
	WHERE users_id=1)
    AND chat.name LIKE "%%" LIMIT 1000;
    

DELETE FROM messages
WHERE chat_id = 2 AND (id = '1' OR id = '2' OR id = '3');

UPDATE messages 
SET `text` = 'kek123'
WHERE id = 3;