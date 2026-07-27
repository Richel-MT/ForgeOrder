-- command: create
CREATE TABLE IF NOT EXISTS tables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    is_available INTEGER NOT NULL DEFAULT 1,
    is_deleted INTEGER NOT NULL DEFAULT 0
);

-- command: new
INSERT INTO tables (name, is_available)
VALUES (?, ?);

-- command: get_from_name
SELECT * FROM tables WHERE name = ?

-- command: get_all
SELECT * FROM tables WHERE is_deleted = 0
ORDER BY id ASC

-- command: update
UPDATE tables SET name = ?, is_available = ? WHERE id = ?

-- command: soft_delete
UPDATE tables SET is_deleted = 1, is_available = 0, name = name || '_disabled' || datetime('now') WHERE id = ?


