const express = require('express');
const cors = require('cors');
const path = require('path');
const db = require('./database');

const app = express();
const PORT = 3000;

// 中间件
app.use(cors());
app.use(express.json());
// 提供前端静态文件（public 目录）
app.use(express.static(path.join(__dirname, '..', 'public')));

// ---------- API 路由 ----------

// 获取所有产品
app.get('/api/products', (req, res) => {
    db.all('SELECT * FROM products ORDER BY id DESC', [], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json(rows);
    });
});

// 添加新产品
app.post('/api/products', (req, res) => {
    const { name, price, stock } = req.body;
    if (!name || price === undefined || stock === undefined) {
        return res.status(400).json({ error: '缺少必要字段' });
    }
    db.run(
        'INSERT INTO products (name, price, stock) VALUES (?, ?, ?)',
        [name, price, stock],
        function(err) {
            if (err) {
                return res.status(500).json({ error: err.message });
            }
            res.json({ id: this.lastID, name, price, stock });
        }
    );
});

// 启动服务器
app.listen(PORT, () => {
    console.log(`服务器已启动：http://localhost:${PORT}`);
    console.log(`前端页面：http://localhost:${PORT}`);
});