const express = require('express');
const path = require('path');
const db = require('./models/db');

const app = express();
const PORT = 3000;

// 提供前端静态文件（frontend 目录）
app.use(express.static(path.join(__dirname, '../frontend')));

// 测试 API：返回数据库中的测试消息
app.get('/api/test', (req, res) => {
    db.get("SELECT message FROM test WHERE id = 1", (err, row) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json({ message: row ? row.message : 'No data' });
    });
});

// 启动服务器
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
    console.log(`Test API: http://localhost:${PORT}/api/test`);
});