
-- command: create
CREATE TABLE IF NOT EXISTS settings(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL
);




-- command: init_settings
INSERT or IGNORE settings (key, value)
VALUES (?, ?)

-- command: get
SELECT * FROM settings WHERE key = ?

-- command: insert
INSERT INTO settings (key, value)
VALUES (?, ?)

-- command: update
INSERT INTO settings (key, value)
VALUES (?, ?)
ON CONFLICT(key) DO UPDATE SET value = excluded.value
-- 有相同key的记录时，更新value