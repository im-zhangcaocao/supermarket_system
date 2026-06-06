# 家电超市管理系统

基于 Flask + Vue.js 3 构建的现代化家电超市管理系统，提供完整的库存管理、销售管理、采购管理、财务管理等功能模块。

## 技术栈

### 后端
- **框架**: Flask 2.0+
- **数据库**: SQLite 3
- **ORM**: SQLAlchemy 2.0+
- **认证**: JWT (PyJWT)
- **密码加密**: bcrypt

### 前端
- **框架**: Vue.js 3 (Composition API)
- **构建工具**: Vite 5.0+
- **UI 组件**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **图表**: ECharts
- **HTTP 客户端**: Axios

## 功能模块

### 1. 库存管理
- 商品信息管理（添加、编辑、删除、禁用）
- 库存查询与预警
- 库存流水记录
- 库存调整与盘点

### 2. 销售管理
- 订单创建与支付
- 积分抵扣功能
- 退货管理
- 销售统计报表

### 3. 采购管理
- 采购订单管理
- 收货确认与质检
- 供应商管理
- 采购建议生成

### 4. 客户管理
- 客户信息管理
- 积分系统
- 购买历史记录
- 品类/品牌偏好分析

### 5. 员工管理
- 员工信息管理
- 角色权限控制（管理员、收银员、采购员）
- 密码重置
- 删除员工功能

### 6. 财务管理
- 财务流水记录
- 收入/支出分析
- 利润计算
- 其他支出录入

### 7. 数据管理
- 数据库备份与恢复
- 数据导入导出
- 数据库初始化

### 8. 统计报表
- 销售趋势分析
- 供应商采购排名
- 库存变化趋势

## 项目结构

```
supermarket/
├── backend/                    # 后端代码
│   ├── app.py                  # Flask 应用入口
│   ├── models.py               # 数据库模型定义
│   ├── routes/                 # API 路由
│   │   ├── auth.py             # 认证相关
│   │   ├── employees.py        # 员工管理
│   │   ├── products.py         # 产品管理
│   │   ├── stock.py            # 库存管理
│   │   ├── sales.py            # 销售管理
│   │   ├── purchase.py         # 采购管理
│   │   ├── suppliers.py        # 供应商管理
│   │   ├── customers.py        # 客户管理
│   │   ├── finance.py          # 财务管理
│   │   ├── reports.py          # 报表统计
│   │   ├── dashboard.py        # 仪表盘
│   │   └── db_manage.py        # 数据库管理
│   ├── middleware/             # 中间件
│   │   └── auth.py             # 认证中间件
│   ├── init_db.py              # 数据库初始化脚本
│   └── database.db             # SQLite 数据库文件
├── src/                        # 前端代码
│   ├── views/                  # 页面组件
│   ├── components/             # 通用组件
│   ├── api/                    # API 客户端
│   ├── router/                 # 路由配置
│   ├── stores/                 # 状态管理
│   ├── utils/                  # 工具函数
│   ├── App.vue                 # 根组件
│   └── main.js                 # 入口文件
├── index.html                  # HTML 模板
├── package.json                # 前端依赖
├── vite.config.js              # Vite 配置
└── README.md                   # 项目说明
```

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 18+
- npm 或 yarn

### 安装依赖

#### 后端依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 前端依赖
```bash
npm install
```

### 初始化数据库

```bash
cd backend
python init_db.py
```

### 启动服务

#### 启动后端服务
```bash
cd backend
python app.py
```
后端服务将运行在 http://localhost:5001

#### 启动前端开发服务器
```bash
npm run dev
```
前端服务将运行在 http://localhost:5173

### 构建生产版本

```bash
npm run build
```

## 默认账号

系统初始化后创建以下默认账号：

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | 123 |
| 收银员 | cashier | 123 |
| 采购员 | buyer | 123 |

## API 接口

### 认证接口
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户退出
- `POST /api/auth/verify` - 验证 Token

### 员工管理（管理员权限）
- `GET /api/employees` - 获取员工列表
- `POST /api/employees` - 添加员工
- `GET /api/employees/<id>` - 获取员工详情
- `PUT /api/employees/<id>` - 更新员工信息
- `DELETE /api/employees/<id>` - 删除员工

### 产品管理
- `GET /api/products` - 获取产品列表
- `POST /api/products` - 添加产品
- `GET /api/products/<id>` - 获取产品详情
- `PUT /api/products/<id>` - 更新产品
- `DELETE /api/products/<id>` - 删除产品

### 库存管理
- `GET /api/stock/<product_id>` - 查询库存
- `POST /api/stock/add` - 增加库存
- `POST /api/stock/deduct` - 扣减库存
- `GET /api/stock/logs` - 获取库存流水

### 销售管理
- `GET /api/sales/orders` - 获取销售订单
- `POST /api/sales/orders` - 创建订单
- `POST /api/sales/orders/<id>/pay` - 支付订单
- `POST /api/sales/orders/<id>/return` - 退货

### 采购管理
- `GET /api/purchase/orders` - 获取采购订单
- `POST /api/purchase/orders` - 创建采购订单
- `POST /api/purchase/orders/<id>/receipt` - 确认收货

### 财务管理
- `GET /api/finance/records` - 获取财务流水
- `POST /api/finance/other-expense` - 录入其他支出
- `GET /api/finance/summary` - 获取财务汇总

## 权限说明

### 管理员权限
- 访问所有功能模块
- 管理员工账号
- 数据管理（备份、恢复、导入导出）

### 收银员权限
- 销售管理（创建订单、处理退货）
- 库存管理（查看库存）

### 采购员权限
- 采购管理（创建采购订单、确认收货）
- 供应商管理

## 开发说明

### 开发模式
后端使用 Flask 调试模式运行，支持热重载。
前端使用 Vite 开发服务器，支持 HMR 热更新。

### 代码规范
- Python 代码遵循 PEP 8 规范
- JavaScript/TypeScript 代码遵循 ESLint 规范
- Vue 组件使用 Composition API

## 安全注意事项

1. 密码使用 bcrypt 加密存储
2. JWT Token 有效期为 24 小时
3. 敏感接口需要管理员权限验证
4. 使用 HTTPS 进行生产部署
5. 定期备份数据库

## License

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！