# 后端服务运行说明

## 快速开始

### 1. 进入后端目录

```bash
cd backend
```

### 2. 创建虚拟环境（推荐）

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 初始化数据库

```bash
python init_db.py
```

应该看到以下输出：
```
正在创建数据库表...
✓ 数据库表创建成功
正在插入示例数据...
✓ 用户数据插入成功
✓ 客户数据插入成功
✓ 供应商数据插入成功
✓ 商品数据插入成功
✓ 销售订单数据插入成功
✓ 销售订单项数据插入成功
✓ 采购订单数据插入成功
✓ 采购订单项数据插入成功
✓ 库存日志数据插入成功
✓ 财务记录数据插入成功

==================================================
数据库初始化完成！
==================================================

默认账号:
  - 收银员: cashier / 123
  - 采购员: buyer / 123
  - 管理员: admin / 123
```

### 5. 启动后端服务

```bash
python app.py
```

应该看到以下输出：
```
==================================================
家电超市管理系统后端服务
==================================================
启动服务: http://127.0.0.1:5000

可用端点:
  - GET  /                        # API 信息
  - GET  /health                  # 健康检查
  ...
==================================================
```

### 6. 运行 API 测试

在另一个终端窗口中运行测试：

```bash
# 测试产品、库存、供应商 API
python test_api.py

# 测试销售订单 API
python test_sales.py
```

## 项目结构

```
backend/
├── app.py              # Flask 主应用
├── models.py           # SQLAlchemy 模型定义
├── init_db.py          # 数据库初始化脚本
├── check_setup.py      # 环境验证脚本
├── test_api.py         # 产品、库存、供应商 API 测试脚本
├── test_sales.py       # 销售订单 API 测试脚本
├── requirements.txt    # Python 依赖列表
├── README.md           # 本文档
├── database.db         # SQLite 数据库文件（自动生成）
└── routes/             # API 路由目录
    ├── __init__.py
    ├── products.py     # 产品管理 API
    ├── stock.py        # 库存管理 API
    ├── suppliers.py    # 供应商管理 API
    └── sales.py        # 销售订单管理 API
```

## API 文档

### 基础信息

- **基础 URL**: `http://127.0.0.1:5000`
- **数据格式**: JSON
- **字符编码**: UTF-8

### 通用响应格式

成功响应：
```json
{
  "success": true,
  "data": {...},
  "message": "操作成功"
}
```

错误响应：
```json
{
  "success": false,
  "error": "错误信息"
}
```

### 1. 产品管理 API

#### 1.1 获取所有产品
```http
GET /api/products?category=空调&status=1
```

查询参数：
- `category`: 按分类筛选（可选）
- `status`: 按状态筛选（可选，1=在售，0=下架）

响应示例：
```json
{
  "success": true,
  "data": [
    {
      "product_id": 1,
      "product_name": "海尔冰箱 BCD-216",
      "brand": "海尔",
      "category": "冰箱",
      "retail_price": 1899.00,
      "current_stock": 10,
      "threshold": 5,
      "status": 1
    }
  ],
  "total": 5
}
```

#### 1.2 获取单个产品
```http
GET /api/products/{id}
```

#### 1.3 添加产品
```http
POST /api/products
Content-Type: application/json

{
  "product_name": "新商品",
  "brand": "品牌",
  "model": "型号",
  "category": "类别",
  "retail_price": 1999.00,
  "purchase_ref_price": 1500.00,
  "current_stock": 10,
  "threshold": 5,
  "operator": "admin"
}
```

#### 1.4 更新产品
```http
PUT /api/products/{id}
Content-Type: application/json

{
  "retail_price": 2099.00,
  "threshold": 8,
  "operator": "admin"
}
```

#### 1.5 删除产品
```http
DELETE /api/products/{id}
```

注意：有关联订单的产品无法删除

#### 1.6 禁用产品
```http
PATCH /api/products/{id}/disable
```

#### 1.7 设置预警阈值
```http
PATCH /api/products/{id}/threshold
Content-Type: application/json

{
  "threshold": 10,
  "operator": "admin"
}
```

### 2. 库存管理 API

#### 2.1 查询库存
```http
GET /api/stock/{product_id}
```

响应示例：
```json
{
  "success": true,
  "data": {
    "product_id": 1,
    "product_name": "海尔冰箱 BCD-216",
    "current_stock": 10,
    "threshold": 5,
    "is_low_stock": false
  }
}
```

#### 2.2 扣减库存
```http
POST /api/stock/deduct
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 2,
  "relate_order_id": "SO202606010001",
  "operator": "cashier",
  "remark": "销售订单出库"
}
```

#### 2.3 增加库存
```http
POST /api/stock/add
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 10,
  "reason": "采购入库",
  "operator_id": "buyer",
  "relate_order_id": "PO202606010001",
  "remark": "采购入库"
}
```

#### 2.4 低库存预警
```http
GET /api/stock/alerts
```

响应示例：
```json
{
  "success": true,
  "data": [
    {
      "product_id": 2,
      "product_name": "美的空调 KFR-35",
      "current_stock": 3,
      "threshold": 5,
      "shortage": 2
    }
  ],
  "total": 1
}
```

#### 2.5 库存流水
```http
GET /api/stock/logs?product_id=1&start_date=2026-06-01&end_date=2026-06-30
```

查询参数：
- `product_id`: 按产品筛选（可选）
- `start_date`: 开始日期（可选，格式：YYYY-MM-DD）
- `end_date`: 结束日期（可选，格式：YYYY-MM-DD）

#### 2.6 手动调整库存
```http
POST /api/stock/adjust
Content-Type: application/json

{
  "product_id": 1,
  "delta": -2,
  "reason": "盘点调整",
  "operator_id": "admin",
  "remark": "月度盘点调整"
}
```

注意：`delta` 为正数表示增加，负数表示减少

### 3. 供应商管理 API

#### 3.1 获取所有供应商
```http
GET /api/suppliers?status=1
```

查询参数：
- `status`: 按状态筛选（可选，1=正常，0=禁用）

#### 3.2 获取单个供应商
```http
GET /api/suppliers/{id}
```

#### 3.3 添加供应商
```http
POST /api/suppliers
Content-Type: application/json

{
  "supplier_name": "新供应商有限公司",
  "contact_person": "张经理",
  "contact_phone": "400-123-4567",
  "address": "北京市朝阳区"
}
```

#### 3.4 更新供应商
```http
PUT /api/suppliers/{id}
Content-Type: application/json

{
  "contact_person": "李经理",
  "contact_phone": "400-654-3210"
}
```

#### 3.5 删除供应商
```http
DELETE /api/suppliers/{id}
```

注意：有关联采购订单的供应商无法删除

#### 3.6 供应商采购订单
```http
GET /api/suppliers/{id}/orders
```

#### 3.7 供应商统计
```http
GET /api/suppliers/{id}/statistics
```

响应示例：
```json
{
  "success": true,
  "data": {
    "supplier_id": 2,
    "supplier_name": "美的集团",
    "total_orders": 1,
    "total_amount": 20000.00,
    "pending_orders": 0,
    "completed_orders": 1
  }
}
```

### 4. 销售订单 API

#### 4.1 获取所有订单
```http
GET /api/sales/orders?customer_id=1&start_date=2024-01-01&end_date=2024-12-31
```

查询参数：
- `customer_id`: 按客户筛选（可选）
- `start_date`: 开始日期（可选，格式：YYYY-MM-DD）
- `end_date`: 结束日期（可选，格式：YYYY-MM-DD）
- `is_cancelled`: 按取消状态筛选（可选，0: 未取消，1: 已取消）

响应示例：
```json
{
  "success": true,
  "data": [
    {
      "order_id": "SO202406050001",
      "customer_id": 1,
      "order_time": "2024-06-05T10:30:00",
      "final_amount": 3798.00,
      "payment_status": 1,
      "is_returned": 0,
      "delivery_status": 0
    }
  ],
  "total": 1
}
```

#### 4.2 获取单个订单详情
```http
GET /api/sales/orders/{order_id}
```

#### 4.3 创建销售订单
```http
POST /api/sales/orders
Content-Type: application/json

{
  "customer_id": 1,
  "payment_method": "微信支付",
  "shipping_address": "配送地址",
  "discount_amount": 0.0,
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "unit_price": 1899.00
    }
  ]
}
```

**订单号生成规则**：SO + yyyymmdd + 4位流水号（每天从0001开始）

响应示例：
```json
{
  "success": true,
  "data": {
    "order_id": "SO202406050001",
    "order": { ... }
  },
  "message": "订单创建成功"
}
```

#### 4.4 支付订单
```http
POST /api/sales/orders/{order_id}/pay
Content-Type: application/json

{
  "operator": "cashier"
}
```

**功能**：
- 更新订单支付状态为已支付
- 扣减库存
- 记录财务收入（type=1）
- 使用数据库事务确保原子性

#### 4.5 退货
```http
POST /api/sales/orders/{order_id}/return
Content-Type: application/json

{
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ],
  "operator": "cashier",
  "remark": "客户退货"
}
```

**功能**：
- 如果不指定 items，默认整单退货
- 检查订单已支付且未退货
- 增加库存
- 记录财务退款（type=4）
- 使用数据库事务确保原子性

#### 4.6 标记订单交付
```http
POST /api/sales/orders/{order_id}/deliver
Content-Type: application/json

{
  "operator": "cashier",
  "remark": "已送达"
}
```

## 使用示例（curl）

### 获取所有产品
```bash
curl http://127.0.0.1:5000/api/products
```

### 添加产品
```bash
curl -X POST http://127.0.0.1:5000/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "测试商品",
    "brand": "测试品牌",
    "retail_price": 999.00,
    "current_stock": 10,
    "operator": "admin"
  }'
```

### 扣减库存
```bash
curl -X POST http://127.0.0.1:5000/api/stock/deduct \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2,
    "relate_order_id": "SO-TEST-001",
    "operator": "cashier"
  }'
```

### 查询低库存预警
```bash
curl http://127.0.0.1:5000/api/stock/alerts
```

## 技术栈

- **Web 框架**: Flask
- **数据库 ORM**: Flask-SQLAlchemy
- **数据库**: SQLite
- **跨域支持**: Flask-CORS
- **WSGI**: Werkzeug

## 默认测试数据

### 用户
- 收银员: `cashier` / `123`
- 采购员: `buyer` / `123`
- 管理员: `admin` / `123`

### 示例数据
- 3 个客户
- 3 个供应商
- 5 个商品（冰箱、空调、电视等）
- 2 个销售订单
- 1 个采购订单
- 库存日志和财务记录

## 常见问题

### 1. 端口被占用
修改 `app.py` 中的端口号：
```python
app.run(debug=True, host='127.0.0.1', port=5001)  # 改为 5001
```

### 2. 数据库重置
删除 `database.db` 并重新初始化：
```bash
del database.db
python init_db.py
```

### 3. 虚拟环境问题
确保已激活虚拟环境：
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 4. 跨域问题
API 已配置 CORS，如仍有问题，检查浏览器控制台或前端配置。

## 下一步

子任务 A1-A2 已完成。接下来可以继续：

- **子任务 A3**: 实现用户认证和登录 API
- **子任务 A4**: 实现销售订单 API
- **子任务 A5**: 实现采购管理 API
- **子任务 A6**: 实现财务管理 API

## 许可证

MIT License
