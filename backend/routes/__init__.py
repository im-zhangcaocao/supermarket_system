"""
API 路由包
"""
from .products import products_bp
from .stock import stock_bp
from .suppliers import suppliers_bp
from .sales import sales_bp
from .purchase import purchase_bp
from .customers import customers_bp
from .employees import employees_bp
from .auth import auth_bp
from .finance import finance_bp
from .reports import reports_bp, dashboard_bp
from .db_manage import db_manage_bp

__all__ = ['products_bp', 'stock_bp', 'suppliers_bp', 'sales_bp', 'purchase_bp', 
           'customers_bp', 'employees_bp', 'auth_bp', 'finance_bp', 
           'reports_bp', 'dashboard_bp', 'db_manage_bp']
