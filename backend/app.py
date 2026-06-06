"""
Flask 主应用
家电超市管理系统后端 API
"""
from flask import Flask
from flask_cors import CORS
from models import db
from routes import products_bp, stock_bp, suppliers_bp, sales_bp, purchase_bp, \
                   customers_bp, employees_bp, auth_bp, finance_bp, \
                   reports_bp, dashboard_bp, db_manage_bp


def create_app():
    """创建 Flask 应用实例"""
    app = Flask(__name__)
    
    # 数据库配置 - 使用绝对路径确保数据持久化
    import os
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "database.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'supermarket-secret-key-2026'
    
    # 初始化扩展
    db.init_app(app)
    
    # 启用 CORS（允许前端跨域访问）
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 注册蓝图
    app.register_blueprint(products_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(purchase_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(db_manage_bp)
    
    return app


# 创建应用实例
app = create_app()


@app.route('/')
def index():
    """首页"""
    return {
        'message': '家电超市管理系统 API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'products': '/api/products',
            'stock': '/api/stock',
            'suppliers': '/api/suppliers',
            'sales': '/api/sales/orders',
            'purchase': '/api/purchase/orders',
            'customers': '/api/customers',
            'employees': '/api/employees',
            'auth': '/api/auth',
            'finance': '/api/finance',
            'reports': '/api/reports',
            'dashboard': '/api/dashboard'
        }
    }


@app.route('/health')
def health():
    """健康检查"""
    return {
        'status': 'healthy',
        'database': 'connected'
    }


if __name__ == '__main__':
    print("="*50)
    print("家电超市管理系统后端服务")
    print("="*50)
    print("启动服务: http://127.0.0.1:5001")
    print("\n可用端点:")
    print("  - GET  /                        # API 信息")
    print("  - GET  /health                  # 健康检查")
    print("\n产品管理 API:")
    print("  - GET    /api/products                    # 获取所有产品")
    print("  - GET    /api/products/<id>               # 获取单个产品")
    print("  - POST   /api/products                    # 添加产品")
    print("  - PUT    /api/products/<id>               # 更新产品")
    print("  - DELETE /api/products/<id>               # 删除产品")
    print("  - PATCH  /api/products/<id>/disable       # 禁用产品")
    print("  - PATCH  /api/products/<id>/threshold     # 设置预警阈值")
    print("\n库存管理 API:")
    print("  - GET    /api/stock/<product_id>          # 查询库存")
    print("  - POST   /api/stock/deduct                # 扣减库存")
    print("  - POST   /api/stock/add                   # 增加库存")
    print("  - GET    /api/stock/alerts                # 低库存预警")
    print("  - GET    /api/stock/logs                  # 库存流水")
    print("  - POST   /api/stock/adjust                # 手动调整库存")
    print("\n供应商管理 API:")
    print("  - GET    /api/suppliers                   # 获取所有供应商")
    print("  - GET    /api/suppliers/<id>              # 获取单个供应商")
    print("  - POST   /api/suppliers                   # 添加供应商")
    print("  - PUT    /api/suppliers/<id>             # 更新供应商")
    print("  - DELETE /api/suppliers/<id>             # 删除供应商")
    print("  - GET    /api/suppliers/<id>/orders       # 供应商订单")
    print("  - GET    /api/suppliers/<id>/statistics   # 供应商统计")
    print("\n销售订单 API:")
    print("  - GET    /api/sales/orders               # 获取所有订单")
    print("  - GET    /api/sales/orders/<id>          # 获取单个订单")
    print("  - POST   /api/sales/orders               # 创建订单")
    print("  - POST   /api/sales/orders/<id>/pay      # 支付订单")
    print("  - POST   /api/sales/orders/<id>/return   # 退货")
    print("  - POST   /api/sales/orders/<id>/deliver  # 标记交付")
    print("\n采购订单 API:")
    print("  - GET    /api/purchase/orders            # 获取采购订单列表")
    print("  - GET    /api/purchase/orders/<id>       # 获取采购订单详情")
    print("  - POST   /api/purchase/orders            # 创建采购订单")
    print("  - POST   /api/purchase/orders/<id>/receipt # 确认收货")
    print("  - GET    /api/purchase/overdue           # 超期订单提醒")
    print("  - PUT    /api/purchase/orders/<id>       # 更新采购订单")
    print("  - DELETE /api/purchase/orders/<id>       # 删除采购订单")
    print("\n客户管理 API:")
    print("  - GET    /api/customers                  # 获取客户列表")
    print("  - GET    /api/customers/<id>             # 获取客户详情")
    print("  - POST   /api/customers                  # 添加客户")
    print("  - PUT    /api/customers/<id>             # 更新客户")
    print("  - DELETE /api/customers/<id>             # 删除客户")
    print("  - GET    /api/customers/<id>/orders      # 客户购买历史")
    print("\n员工管理 API (管理员):")
    print("  - GET    /api/employees                  # 获取员工列表")
    print("  - GET    /api/employees/<id>             # 获取员工详情")
    print("  - POST   /api/employees                  # 添加员工")
    print("  - PUT    /api/employees/<id>             # 更新员工")
    print("  - POST   /api/employees/<id>/reset-password # 重置密码")
    print("  - DELETE /api/employees/<id>             # 删除员工")
    print("\n认证 API:")
    print("  - POST   /api/auth/login                 # 用户登录")
    print("  - POST   /api/auth/logout                # 用户退出")
    print("  - POST   /api/auth/verify                # 验证 token")
    print("\n财务管理 API:")
    print("  - GET    /api/finance/records            # 财务流水")
    print("  - POST   /api/finance/other-expense      # 录入其他支出")
    print("  - GET    /api/finance/summary            # 财务汇总")
    print("  - GET    /api/finance/profit             # 利润数值")
    print("  - GET    /api/finance/daily-summary      # 每日汇总")
    print("  - GET    /api/finance/category-summary   # 类别统计")
    print("\n报表 API:")
    print("  - GET    /api/reports/sales-trend        # 销售趋势")
    print("  - GET    /api/reports/category-sales     # 类别销售占比")
    print("  - GET    /api/reports/supplier-ranking   # 供应商采购排名")
    print("  - GET    /api/reports/inventory-trend    # 库存变化趋势")
    print("\n仪表盘 API:")
    print("  - GET    /api/dashboard/stats            # 统计数据")
    print("  - GET    /api/dashboard/quick-stats      # 快速统计")
    print("="*50)
    
    app.run(debug=True, host='127.0.0.1', port=5001)
