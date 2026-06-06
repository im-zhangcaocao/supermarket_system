# 子任务 B3 完成总结 - 采购订单管理 API

## 已实现功能

### 1. 采购订单 API （8个端点）

| 方法 | 端点 | 功能 |
|------|------|------|
| GET | `/api/purchase/orders` | 获取采购订单列表（支持筛选和分页） |
| GET | `/api/purchase/orders/<order_id>` | 获取采购订单详情 |
| POST | `/api/purchase/orders` | 创建采购订单 |
| POST | `/api/purchase/orders/<order_id>/receipt` | 确认收货 |
| GET | `/api/purchase/overdue` | 获取超期未完成订单 |
| PUT | `/api/purchase/orders/<order_id>` | 更新采购订单 |
| DELETE | `/api/purchase/orders/<order_id>` | 删除采购订单 |
| GET | `/api/purchase/suppliers/<supplier_id>/orders` | 获取供应商采购订单 |

### 2. 订单号生成规则
- **格式**：PO + yyyymmdd + 4位流水号
- **示例**：PO202406050001
- **规则**：每天从 0001 开始重新编号

### 3. 核心特性

#### 3.1 创建采购订单
- ✅ 验证供应商是否存在
- ✅ 验证商品信息完整性
- ✅ 自动计算订单金额
- ✅ 设置状态为待交付(pending)

#### 3.2 确认收货
- ✅ 验证订单状态（未完成）
- ✅ 验证收货数量不超过剩余数量
- ✅ **使用数据库事务**确保原子性
- ✅ 更新库存（增加）
- ✅ 记录库存日志
- ✅ 记录财务支出（type=2）
- ✅ 自动创建新产品（如果商品不存在）
- ✅ 更新订单状态：
  - 全部完成：status = completed (2)
  - 部分完成：status = partial (1)

#### 3.3 超期订单提醒
- ✅ 查询条件：expected_date < 当前日期且未完成
- ✅ 返回逾期天数
- ✅ 按预期日期排序

#### 3.4 订单更新/删除
- ✅ 验证订单状态（已完成订单不能修改/删除）
- ✅ 检查是否有已收货记录（有收货不能删除）

### 4. 状态说明

| 状态值 | 状态文本 | 说明 |
|--------|----------|------|
| pending / 0 | 待交付 | 订单已创建，等待供应商发货 |
| partial / 1 | 部分交付 | 部分商品已收货 |
| completed / 2 | 已完成 | 所有商品已收货 |

## 新增文件

```
backend/
├── routes/
│   └── purchase.py         # 采购订单 API 实现
├── test_purchase.py        # 采购订单 API 测试脚本
└── [更新的文件]
    ├── routes/__init__.py
    └── app.py
```

## 测试脚本

### 运行测试
```bash
# 启动后端服务
cd backend
python app.py

# 在另一个终端运行测试
python test_purchase.py
```

### 测试内容
1. 获取采购订单列表
2. 创建新采购订单
3. 获取订单详情
4. 确认收货（部分收货）
5. 获取超期订单
6. 获取供应商采购订单

## 使用示例（curl）

### 1. 创建采购订单
```bash
curl -X POST http://127.0.0.1:5000/api/purchase/orders \
  -H "Content-Type: application/json" \
  -d '{
    "supplier_id": 1,
    "expected_date": "2024-06-15",
    "remark": "测试采购",
    "items": [
      {"product_id": 1, "quantity": 5, "unit_price": 1500.00}
    ]
  }'
```

### 2. 确认收货
```bash
curl -X POST http://127.0.0.1:5000/api/purchase/orders/{order_id}/receipt \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"product_id": 1, "received_quantity": 3}
    ],
    "operator": "buyer",
    "remark": "部分收货"
  }'
```

### 3. 查询超期订单
```bash
curl http://127.0.0.1:5000/api/purchase/overdue
```

### 4. 获取订单列表（带筛选）
```bash
curl "http://127.0.0.1:5000/api/purchase/orders?supplier_id=1&status=0"
```

## 事务处理

### 确认收货事务
```python
with db.session.begin_nested():
    # 更新库存（增加）
    # 记录库存日志
    # 创建新产品（如需要）
    # 记录财务支出
    # 更新订单项收货数量
    # 更新订单状态
```

## 边界情况处理

1. **重复确认收货**：检查订单状态，已完成订单不能重复收货
2. **实收数量超过订购数量**：验证并拒绝超过剩余数量的收货
3. **新产品处理**：自动创建产品记录（status=1, current_stock=实收数量）
4. **已完成订单保护**：已完成的订单不能修改或删除
5. **有收货记录保护**：有收货记录的订单不能删除

## 完成时间

2024年6月5日

---

**状态**：✅ 子任务 B3 完成并测试通过
