 -- command: create
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    
    type INTEGER NOT NULL, -- 0: 堂食 --1：打包
    table_id INTEGER, -- 桌号id，打包时为NULL

    note TEXT,
    
    FOREIGN KEY (table_id) REFERENCES tables (id),
    FOREIGN KEY (creator) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS sub_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    parent_id INTEGER NOT NULL,

    created_at TIMESTAMP NOT NULL, -- 子订单的创建时间

    FOREIGN KEY (parent_id) REFERENCES orders (id),
)

CREATE TABLE IF NOT EXISTS order_status (
    id INTEGER PRIMARY KEY,

    status INTEGER NOT NULL DEFAULT 0, --0: 已下单 --1: 制作中 --2: 待结账 --3: 已结账
    created_at TIMESTAMP NOT NULL, -- 下单时间

    updated_at TIMESTAMP NOT NULL, -- 最后更新时间

    finish_at TIMESTAMP, -- 完成时间（菜品全部完成）
    pay_at TIMESTAMP, -- 支付时间
    
    cashier INTEGER NOT NULL, -- 收银员id
    
    pay_method INTEGER, --0: 现金 --1: 支付宝 --2: 微信
    

    total_amount INTEGER NOT NULL, -- 订单总金额

    discount INTEGER, --优惠金额
    discount_type INTEGER, --0: 抹零 --1: 优惠固定金额 --2: 按比例优惠
    discount_msg TEXT, -- 优惠信息

    finally_amount INTEGER, --最终金额


    FOREIGN KEY (id) REFERENCES orders (id),
    FOREIGN KEY (cashier) REFERENCES users (id)
);



CREATE TABLE IF NOT EXISTS order_items (

    id INTEGER PRIMARY KEY AUTOINCREMENT, 

    parent_id INTEGER NOT NULL,
    sub_id INTEGER NOT NULL,

    dish_id INTEGER NOT NULL,

    price INTEGER NOT NULL,
    count INTEGER NOT NULL,

    total_mount INTEGER NOT NULL,

    choices JSON,
    
    note TEXT,

    finished INTEGER NOT NULL DEFAULT 0, --0: 未完成 --1: 已完成
    finished_at TIMESTAMP, -- 完成时间
    
    FOREIGN KEY (parent_id) REFERENCES orders (id),
    FOREIGN KEY (sub_id) REFERENCES sub_orders (id),
    FOREIGN KEY (dish_id) REFERENCES dishes (id),
);





-- command: get_latest
SELECT * FROM orders WHERE id LIKE ? ORDER BY id DESC LIMIT 1

-- command: items.new
INSERT INTO order_items (order_id, dish_id, price, count, total_mount, choices)
VALUES (?, ?, ?, ?, ?, ?);

-- command: update
UPDATE orders SET creator = ?, display_no = ?, table_no = ?, total_mount = ?, note = ? WHERE id = ?

-- command: stats.update
UPDATE order_stats SET status = ?, updated_at = ?, pay_at = ?, finish_at = ?, pay_method = ?, discount = ?, finally_mount = ? WHERE id = ?

