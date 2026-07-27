-- command: create
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


-- command: new
INSERT INTO print_task (id, content, context, created_at)
VALUES (?, ?, ?, ?)

-- command: get
SELECT * FROM print_task WHERE id = ?

-- command: update
UPDATE print_task SET status = ?, error_message = ?, started_at = ?, finished_at = ? WHERE id = ?