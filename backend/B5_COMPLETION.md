# 子任务 B5 完成总结 - 财务相关 API

## 已实现功能

### 1. 财务流水 API（2个端点）

| 方法 | 端点 | 功能 |
|------|------|------|
| GET | `/api/finance/records` | 获取财务流水（支持类型和日期筛选） |
| POST | `/api/finance/other-expense` | 录入其他支出 |

### 2. 财务统计 API（4个端点）

| 方法 | 端点 | 功能 |
|------|------|------|
| GET | `/api/finance/summary` | 获取财务汇总（收入、支出、利润） |
| GET | `/api/finance/profit` | 获取利润数值 |
| GET | `/api/finance/daily-summary` | 获取每日财务汇总 |
| GET | `/api/finance/category-summary` | 按类别统计支出 |

### 3. 财务类型说明

| 类型码 | 类型名称 | 说明 |
|--------|----------|------|
| 1 | 销售收入 | 销售订单支付产生的收入 |
| 2 | 采购支出 | 采购订单收货产生的支出 |
| 3 | 其他支出 | 录入的其他费用支出 |
| 4 | 退货退款 | 销售退货产生的退款 |

### 4. 利润计算公式

```
总收入 = 销售收入 - 退货退款
总支出 = 采购支出 + 其他支出
净利润 = 总收入 - 总支出
       = (销售收入 - 退货退款) - (采购支出 + 其他支出)
       = 销售收入 - 采购支出 - 其他支出 - 退货退款
```

### 5. 核心特性

#### 5.1 财务流水
- ✅ 支持按类型筛选（type 参数）
- ✅ 支持按日期范围筛选（start_date, end_date）
- ✅ 支持分页（page, page_size）
- ✅ 按时间倒序排列

#### 5.2 财务汇总
- ✅ 计算销售收入、采购支出、其他支出、退货退款
- ✅ 计算实际收入（扣除退货后的收入）
- ✅ 计算净利润
- ✅ 计算毛利率
- ✅ 返回清晰的计算公式说明

#### 5.3 其他支出录入
- ✅ 验证必填字段（category, amount, note）
- ✅ 验证金额大于0
- ✅ 支持自定义日期
- ✅ 创建财务记录（type=3）

#### 5.4 每日汇总
- ✅ 按日期分组统计
- ✅ 计算每日利润
- ✅ 支持日期范围筛选

#### 5.5 类别统计
- ✅ 按类别分组统计其他支出
- ✅ 计算每个类别的总金额和记录数
- ✅ 按金额降序排序

## 新增文件

```
backend/
├── routes/
│   └── finance.py        # 财务管理 API 实现
└── test_finance.py       # 财务管理 API 测试脚本
```

## 测试脚本

### 运行测试
```bash
# 启动后端服务
cd backend
python app.py

# 在另一个终端运行测试
python test_finance.py
```

### 测试内容
1. 获取财务流水
2. 获取财务汇总（收入、支出、利润）
3. 获取利润数值
4. 录入其他支出
5. 获取每日财务汇总
6. 获取类别统计
7. 按类型筛选财务流水

## 使用示例（curl）

### 1. 获取财务汇总
```bash
curl http://127.0.0.1:5000/api/finance/summary
```

响应示例：
```json
{
  "success": true,
  "data": {
    "sales_income": 5000.00,
    "purchase_expense": 3000.00,
    "other_expense": 500.00,
    "return_refund": 200.00,
    "total_income": 4800.00,
    "total_expense": 3500.00,
    "profit": 1300.00,
    "gross_profit_margin": 40.00,
    "record_count": 10
  },
  "formula": {
    "total_income": "销售收入 - 退货退款",
    "total_expense": "采购支出 + 其他支出",
    "profit": "(销售收入 - 退货退款) - (采购支出 + 其他支出)"
  }
}
```

### 2. 获取利润
```bash
curl http://127.0.0.1:5000/api/finance/profit?start_date=2024-01-01&end_date=2024-12-31
```

### 3. 录入其他支出
```bash
curl -X POST http://127.0.0.1:5000/api/finance/other-expense \
  -H "Content-Type: application/json" \
  -d '{
    "category": "水电费",
    "amount": 500.00,
    "note": "2024年6月水电费",
    "date": "2024-06-05"
  }'
```

### 4. 获取财务流水（按类型筛选）
```bash
curl "http://127.0.0.1:5000/api/finance/records?type=1"
```

### 5. 获取每日汇总
```bash
curl "http://127.0.0.1:5000/api/finance/daily-summary?start_date=2024-06-01&end_date=2024-06-30"
```

## API 参数说明

### 1. 财务流水查询参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | int | 否 | 类型筛选（1:销售, 2:采购, 3:其他, 4:退货） |
| start_date | string | 否 | 开始日期（YYYY-MM-DD） |
| end_date | string | 否 | 结束日期（YYYY-MM-DD） |
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认20 |

### 2. 财务汇总查询参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| start_date | string | 否 | 开始日期（YYYY-MM-DD） |
| end_date | string | 否 | 结束日期（YYYY-MM-DD） |

### 3. 其他支出录入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | string | 是 | 支出类别 |
| amount | float | 是 | 金额（必须大于0） |
| note | string | 是 | 备注说明 |
| date | string | 否 | 日期（YYYY-MM-DD，默认今天） |

## 完成时间

2024年6月5日

---

**状态**：✅ 子任务 B5 完成并测试通过
