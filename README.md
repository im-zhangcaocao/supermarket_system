supermarket-system/                 # 项目根目录
│
├── backend/                        # 后端代码（Node.js + Express）
│   ├── api/                        # API 路由模块（按业务拆分）
│   │   ├── products.js             # 产品相关接口
│   │   ├── orders.js               # 销售订单接口
│   │   ├── purchase.js             # 采购订单接口
│   │   ├── users.js                # 用户注册/登录接口
│   │   ├── finance.js              # 财务统计接口
│   │   └── reports.js              # 报表接口
│   ├── models/                     # 数据模型（可选，直接操作 SQLite）
│   │   └── db.js                   # 数据库连接与初始化
│   ├── middleware/                 # 中间件（如身份验证、日志）
│   │   └── auth.js                 # JWT 或 session 验证
│   ├── utils/                      # 工具函数
│   │   └── helpers.js
│   ├── server.js                   # 应用入口，注册路由、启动服务
│   ├── package.json                # 后端依赖
│   └── .env                        # 环境变量（端口、数据库路径等）
│
├── frontend/                       # 前端静态文件（独立于后端）
│   ├── index.html                  # 客户主页面
│   ├── admin.html                  # 后台管理页面
│   ├── css/
│   │   ├── common.css              # 公共样式
│   │   ├── front.css               # 前台样式
│   │   └── admin.css               # 后台样式
│   ├── js/
│   │   ├── common.js               # 公共函数（API 调用封装、工具）
│   │   ├── front.js                # 前台业务逻辑
│   │   └── admin/                  # 后台模块脚本（按功能拆分）
│   │       ├── admin.js            # 后台入口（路由、权限）
│   │       ├── inventory.js        # 库存管理模块
│   │       ├── sales.js            # 销售管理模块
│   │       ├── purchase.js         # 采购管理模块
│   │       ├── users.js            # 用户管理模块
│   │       ├── finance.js          # 财务管理模块
│   │       └── reports.js          # 统计报表模块
│   └── assets/                     # 图片、图标等
│
├── database/                       # SQLite 数据库文件存放目录
│   └── supermarket.db              # 实际数据库文件（被 .gitignore 忽略）
│
├── logs/                           # 日志文件（可选）
│
├── .gitignore                      # 忽略 node_modules, database/*.db, .env 等
├── README.md                       # 项目说明文档
└── package.json                    # 根目录 package.json（如果前后端统一管理）