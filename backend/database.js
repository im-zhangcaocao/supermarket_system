const sqlite3 = require('sqlite3').verbose();
const path = require('path');

// 数据库文件路径（存放在项目根目录）
const dbPath = path.join(__dirname, '..', 'supermarket.db');
const db = new sqlite3.Database(dbPath);

// 初始化表：产品表（示例）
db.serialize(() => {
    db.run(`
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    `);
    // 可选：插入一些测试数据
    db.get("SELECT COUNT(*) as count FROM products", (err, row) => {
        if (row.count === 0) {
            db.run("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", ["冰箱", 2999, 10]);
            db.run("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", ["洗衣机", 1999, 5]);
        }
    });
});

module.exports = db;