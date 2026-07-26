-- command: create
CREATE TABLE IF NOT EXISTS tables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    is_available INTEGER NOT NULL DEFAULT 1
);

-- command: new
INSERT INTO tables (name, is_available)
VALUES (?, ?);

-- command: get_from_name
SELECT * FROM tables WHERE name = ?

-- command: get_all_available
SELECT * FROM tables WHERE is_available = 1
