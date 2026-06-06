# 快速入门指南

## 一键启动（推荐）

### Windows
```bash
cd backend
python start.py
```

### Linux/Mac
```bash
cd backend
python3 start.py
```

`start.py` 会自动检查环境、初始化数据库并启动服务。

## 手动启动

如果一键启动失败，请按以下步骤手动操作：

### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. 初始化数据库
```bash
python init_db.py
```

### 3. 启动服务
```bash
python app.py
```

## 验证服务

服务启动后，打开浏览器访问：

- API 信息：http://127.0.0.1:5000/
- 健康检查：http://127.0.0.1:5000/health
- 产品列表：http://127.0.0.1:5000/api/products

## 测试 API

### 使用浏览器或 Postman

#### 获取所有产品
```
GET http://127.0.0.1:5000/api/products
```

#### 添加产品
```
POST http://127.0.0.1:5000/api/products
Content-Type: application/json

{
  "product_name": "测试商品",
  "brand": "测试品牌",
  "retail_price": 999.00,
  "current_stock": 10,
  "operator": "admin"
}
```

#### 扣减库存
```
POST http://127.0.0.1:5000/api/stock/deduct
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 2,
  "relate_order_id": "SO-TEST-001",
  "operator": "cashier"
}
```

### 使用测试脚本

```bash
python test_api.py
```

这将自动测试所有 API 端点。

## 常见问题

### 端口被占用
修改 `app.py` 中的端口号，将 `port=5000` 改为其他端口。

### 数据库错误
删除 `database.db` 文件，重新运行 `python init_db.py`。

### 依赖缺失
确保虚拟环境已激活，然后运行 `pip install -r requirements.txt`。

## 下一步

- 查看完整 API 文档：[README.md](README.md)
- 运行完整测试：`python test_api.py`
- 开始开发：使用 Postman 或前端应用连接 API
