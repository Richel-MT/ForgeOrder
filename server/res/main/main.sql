-- command: init
PRAGMA foreign_keys = ON;

PRAGMA journal_mode = WAL;

-- $users.create

-- $tables.create

-- $orders.create

-- $dishes.create


CREATE TABLE IF NOT EXISTS settings(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL
);

CREATE TABLE If NOT EXISTS print_task (
    id TEXT PRIMARY KEY, -- uuid v7
    status INTEGER DEFAULT 0,  -- 0：等待中 -- 1：打印中 -- 2：成功 --3：错误
    
    content TEXT NOT NULL, -- Receipt JSON
    context TEXT, -- 上下文

    error_message TEXT,

    
    created_at TIMESTAMP NOT NULL, -- 任务创建时间
    started_at TIMESTAMP, -- 开始打印的时间
    finished_at TIMESTAMP -- 打印完成时间（错误也用这个）


)




- settings 表操作

-- command: settings.init_settings
INSERT or IGNORE settings (key, value)
VALUES (?, ?)

-- command: settings.get
SELECT * FROM settings WHERE key = ?

-- command: settings.insert
INSERT INTO settings (key, value)
VALUES (?, ?)

-- command: settings.update
INSERT INTO settings (key, value)
VALUES (?, ?)
ON CONFLICT(key) DO UPDATE SET value = excluded.value


-- printtask

-- command: print_task.new
INSERT INTO print_task (id, content, context, created_at)
VALUES (?, ?, ?, ?)

-- command: print_task.get
SELECT * FROM print_task WHERE id = ?

-- command: print_task.update
UPDATE print_task SET status = ?, error_message = ?, started_at = ?, finished_at = ? WHERE id = ?



