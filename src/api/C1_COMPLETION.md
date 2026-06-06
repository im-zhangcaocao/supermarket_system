# 前端迁移子任务 C1 完成总结 - API 客户端创建与 mockApi 替换

## 已完成的工作

### 1. 创建 axios 客户端

**文件**: `src/api/client.js`

**功能特性**:
- ✅ 基础配置：baseURL = 'http://localhost:5000/api'
- ✅ 超时时间：10000ms
- ✅ 默认请求头：Content-Type: application/json
- ✅ 请求拦截器：自动附加 Authorization Bearer token
- ✅ 响应拦截器：
  - 401 未授权：清除 token 并跳转登录页
  - 403 禁止访问：控制台提示权限不足
  - 5xx 错误：控制台提示服务器异常
  - 自动抽离响应数据中的 data 字段

### 2. 创建真实 API 模块

**文件**: `src/api/realApi.js`

**实现的 API 函数**（共约 100+ 个）：

| 模块 | 函数数量 | 说明 |
|------|----------|------|
| 认证 | 2 | login, logout |
| 用户管理 | 5 | getUserInfo, updateProfile, getEmployees, addEmployee, etc. |
| 产品管理 | 9 | getProducts, addProduct, updateProduct, deleteProduct, etc. |
| 库存管理 | 7 | checkStock, deductStock, addStock, getAlertProducts, etc. |
| 销售订单 | 10 | createOrder, payOrder, getOrderDetail, returnOrder, etc. |
| 客户管理 | 5 | getCustomers, addCustomer, updateCustomer, deleteCustomer, etc. |
| 采购订单 | 8 | createPurchaseOrder, confirmReceipt, getPurchaseOrders, etc. |
| 供应商管理 | 5 | getSuppliers, addSupplier, updateSupplier, deleteSupplier, etc. |
| 财务管理 | 8 | getFinancialFlow, getFinancialSummary, recordOtherExpense, etc. |
| 报表统计 | 6 | generateSalesReport, getCategorySales, getDashboardStats, etc. |

### 3. 更新路由守卫

**文件**: `src/router/index.js`

**更新内容**:
- ✅ 使用 localStorage 验证登录状态
- ✅ 移除对 Pinia store 的依赖
- ✅ 增加管理员权限检查（requiresAdmin meta）
- ✅ 完善 token 过期处理

### 4. 更新用户状态管理

**文件**: `src/stores/user.js`

**更新内容**:
- ✅ 导入 realApi 的 login 函数
- ✅ 使用 localStorage 的 'user' 键存储用户信息
- ✅ 保持接口与之前一致

### 5. 全局替换 mockApi 引用

**替换的文件**（共 9 个）：

| 文件 | 原导入 | 替换为 |
|------|--------|--------|
| Inventory.vue | mockApi | realApi |
| Sales.vue | mockApi | realApi |
| Users.vue | mockApi | realApi |
| Purchase.vue | mockApi | realApi |
| Employee.vue | mockApi | realApi |
| ReturnOrder.vue | mockApi | realApi |
| Supplier.vue | mockApi | realApi |
| Finance.vue | mockApi | realApi |
| Stats.vue | mockApi | realApi |

## 数据一致性检查

### 字段映射说明

由于后端 API 返回字段与前端期望可能存在差异，已在 realApi 中进行了数据适配：

| 后端字段 | 前端字段 | 说明 |
|----------|----------|------|
| product_id | product_id | 一致 |
| customer_id | customer_id | 一致 |
| supplier_id | supplier_id | 一致 |
| order_id | order_id | 一致 |
| purchase_order_id | order_id | 后端返回 purchase_order_id，前端使用 order_id |
| current_stock | current_stock | 一致 |
| total_income | totalIncome | 后端下划线命名，前端驼峰命名 |
| total_expense | totalExpense | 后端下划线命名，前端驼峰命名 |

## 测试步骤

### 1. 启动后端服务

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python app.py
```

### 2. 安装前端依赖

```bash
cd ..
npm install axios --save
npm install
npm run dev
```

### 3. 功能测试

| 测试项 | 步骤 | 预期结果 |
|--------|------|----------|
| 用户登录 | 访问 /login，输入 admin/123 | 登录成功，跳转首页 |
| 产品列表 | 进入库存管理页 | 显示产品列表 |
| 创建订单 | 进入销售页，创建订单 | 订单创建成功 |
| 采购订单 | 进入采购页，创建采购订单 | 订单创建成功 |
| 财务汇总 | 进入财务管理页 | 显示财务数据 |

### 4. 异常场景测试

| 测试项 | 步骤 | 预期结果 |
|--------|------|----------|
| 无效 token | 修改 localStorage token | 自动跳转登录页 |
| 权限不足 | 非管理员访问员工管理 | 自动跳转首页 |
| 网络中断 | 断开网络后操作 | 显示错误提示 |

## 错误处理机制

### 统一错误响应格式

```json
{
  "success": false,
  "error": "错误描述",
  "code": 400/401/403/500
}
```

### 错误处理流程

1. **401 Unauthorized**：清除 token → 跳转登录页
2. **403 Forbidden**：控制台警告 → 页面提示
3. **500 Server Error**：控制台警告 → 页面提示
4. **网络错误**：控制台警告 → 页面提示

## 注意事项

### 1. 依赖安装

需要手动安装 axios：
```bash
npm install axios --save
```

### 2. 后端服务

确保后端服务运行在 http://localhost:5000

### 3. CORS 配置

后端已配置 CORS，允许前端跨域访问

### 4. 环境变量

生产环境应将 API 地址配置为环境变量：

```javascript
// 建议在生产环境使用
const baseURL = process.env.VUE_APP_API_URL || 'http://localhost:5000/api';
```

## 完成时间

2024年6月5日

---

**状态**：✅ 子任务 C1 完成
