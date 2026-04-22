const sqlite3 = require('sqlite3').verbose();
const path = require('path');

// 数据库文件路径（存放在项目根目录的 database 文件夹下）
const dbPath = path.join(__dirname, '../../database/supermarket.db');
const db = new sqlite3.Database(dbPath);

// 初始化：创建一个简单的测试表
db.serialize(() => {
    db.run(`
        CREATE TABLE IF NOT EXISTS test (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT
        )
    `);
    // 插入一条测试数据（如果表为空）
    db.get("SELECT COUNT(*) as count FROM test", (err, row) => {
        if (row.count === 0) {
            db.run("INSERT INTO test (message) VALUES (?)", ["Hello from database"]);
        }
    });
});

module.exports = db;