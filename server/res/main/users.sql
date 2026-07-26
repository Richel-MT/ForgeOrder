
-- command: create
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0,
    is_available INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL,
    last_login_at TIMESTAMP
);

-- command: new
INSERT INTO users (username, password, is_admin, is_available, created_at)
VALUES (?, ?, ?, ?, ?);

-- command: get_from_username
SELECT * FROM users WHERE username = ?

-- command: get_from_id
SELECT * FROM users WHERE id = ?


-- command: change_password
UPDATE users SET password = ? WHERE id = ?