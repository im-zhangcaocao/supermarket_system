from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # cashier, purchaser, admin
    status = db.Column(db.Integer, default=1)  # 1: 正常, 0: 禁用
    last_login = db.Column(db.DateTime, nullable=True)
    phone = db.Column(db.String(20))  # 手机号码
    email = db.Column(db.String(100))  # 邮箱地址
    address = db.Column(db.String(255))  # 居住地址
    real_name = db.Column(db.String(50))  # 真实姓名
    salary_type = db.Column(db.String(20), default='monthly')  # 薪资类型：hourly, monthly
    salary_rate = db.Column(db.Float, default=0)  # 薪资标准
    hire_date = db.Column(db.Date)  # 入职日期
    reset_password_required = db.Column(db.Integer, default=0)  # 是否需要重置密码

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'role': self.role,
            'status': self.status,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'real_name': self.real_name,
            'salary_type': self.salary_type,
            'salary_rate': self.salary_rate,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'reset_password_required': self.reset_password_required
        }


class Customer(db.Model):
    """客户模型"""
    __tablename__ = 'customers'

    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.String(255))
    register_time = db.Column(db.Date, default=datetime.now().date)
    points = db.Column(db.Integer, default=0)  # 客户积分
    membership_level = db.Column(db.String(20), default='普通会员')  # 会员等级：普通会员、白银会员、黄金会员
    discount_rate = db.Column(db.Float, default=1.0)  # 折扣率
    points_expiry_date = db.Column(db.Date)  # 积分过期日期

    def to_dict(self):
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'register_time': self.register_time.isoformat() if self.register_time else None,
            'points': self.points,
            'membership_level': self.membership_level,
            'discount_rate': self.discount_rate,
            'points_expiry_date': self.points_expiry_date.isoformat() if self.points_expiry_date else None
        }


class Product(db.Model):
    """商品模型"""
    __tablename__ = 'products'

    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    category = db.Column(db.String(50))
    retail_price = db.Column(db.Float, nullable=False, default=0.0)
    purchase_ref_price = db.Column(db.Float)
    current_stock = db.Column(db.Integer, nullable=False, default=0)
    threshold = db.Column(db.Integer, nullable=False, default=10)
    status = db.Column(db.Integer, default=1)  # 1: 在售, 0: 下架
    unit = db.Column(db.String(20), default='台')
    warehouse = db.Column(db.String(10))  # 仓库 A-F
    shelf_no = db.Column(db.String(20))   # 货位 1-20

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'brand': self.brand,
            'model': self.model,
            'category': self.category,
            'retail_price': self.retail_price,
            'purchase_ref_price': self.purchase_ref_price,
            'current_stock': self.current_stock,
            'threshold': self.threshold,
            'status': self.status,
            'unit': self.unit,
            'warehouse': self.warehouse,
            'shelf_no': self.shelf_no
        }


class Supplier(db.Model):
    """供应商模型"""
    __tablename__ = 'suppliers'

    supplier_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    supplier_name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(50))
    contact_phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    status = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier_name,
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'address': self.address,
            'status': self.status
        }


class SalesOrder(db.Model):
    """销售订单模型"""
    __tablename__ = 'sales_orders'

    order_id = db.Column(db.String(50), primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'))
    order_time = db.Column(db.DateTime, default=datetime.now)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    final_amount = db.Column(db.Float, nullable=False, default=0.0)
    payment_method = db.Column(db.String(20))  # 微信支付, 支付宝, 现金, 银行卡
    payment_status = db.Column(db.Integer, default=0)  # 0: 未付款, 1: 已付款
    shipping_address = db.Column(db.String(255))
    is_cancelled = db.Column(db.Integer, default=0)  # 0: 正常, 1: 已取消
    is_returned = db.Column(db.Integer, default=0)  # 0: 正常, 1: 已退货
    delivery_status = db.Column(db.Integer, default=0)  # 0: 待交付, 1: 已交付
    points_earned = db.Column(db.Integer, default=0)  # 获得的积分（等于实付金额）
    points_used = db.Column(db.Integer, default=0)  # 使用的积分数量
    points_discount = db.Column(db.Float, default=0.0)  # 积分抵扣金额

    # 关联关系
    customer = db.relationship('Customer', backref='sales_orders')
    items = db.relationship('SalesOrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'order_id': self.order_id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'order_time': self.order_time.isoformat() if self.order_time else None,
            'total_amount': self.total_amount,
            'discount_amount': self.discount_amount,
            'final_amount': self.final_amount,
            'payment_method': self.payment_method,
            'points_earned': self.points_earned,
            'points_used': self.points_used,
            'points_discount': self.points_discount,
            'payment_status': self.payment_status,
            'shipping_address': self.shipping_address,
            'is_cancelled': self.is_cancelled,
            'is_returned': self.is_returned,
            'delivery_status': self.delivery_status
        }


class SalesOrderItem(db.Model):
    """销售订单项模型"""
    __tablename__ = 'sales_order_items'

    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.String(50), db.ForeignKey('sales_orders.order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    cost_price = db.Column(db.Float)  # 成本价

    # 关联关系
    product = db.relationship('Product', backref='sales_items')

    def to_dict(self):
        return {
            'item_id': self.item_id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product.product_name if self.product else None,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'cost_price': self.cost_price,
            'category': self.product.category if self.product else None,
            'brand': self.product.brand if self.product else None
        }


class PurchaseOrder(db.Model):
    """采购订单模型"""
    __tablename__ = 'purchase_orders'

    purchase_order_id = db.Column(db.String(50), primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.supplier_id'), nullable=False)
    order_time = db.Column(db.DateTime, default=datetime.now)
    expected_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')  # pending: 待收货, partial: 部分收货, completed: 已完成
    total_amount = db.Column(db.Float, default=0.0)
    remark = db.Column(db.String(255))
    received_time = db.Column(db.DateTime)

    # 关联关系
    supplier = db.relationship('Supplier', backref='purchase_orders')
    items = db.relationship('PurchaseOrderItem', backref='purchase_order', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'purchase_order_id': self.purchase_order_id,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.supplier_name if self.supplier else None,
            'order_time': self.order_time.isoformat() if self.order_time else None,
            'expected_date': self.expected_date.isoformat() if self.expected_date else None,
            'status': self.status,
            'total_amount': self.total_amount,
            'remark': self.remark,
            'received_time': self.received_time.isoformat() if self.received_time else None
        }


class PurchaseOrderItem(db.Model):
    """采购订单项模型"""
    __tablename__ = 'purchase_order_items'

    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    purchase_order_id = db.Column(db.String(50), db.ForeignKey('purchase_orders.purchase_order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    received_quantity = db.Column(db.Integer, default=0)  # 已收货数量
    unit_price = db.Column(db.Float, nullable=False)

    # 关联关系
    product = db.relationship('Product', backref='purchase_items')

    def to_dict(self):
        return {
            'item_id': self.item_id,
            'purchase_order_id': self.purchase_order_id,
            'product_id': self.product_id,
            'product_name': self.product.product_name if self.product else None,
            'quantity': self.quantity,
            'received_quantity': self.received_quantity,
            'unit_price': self.unit_price
        }


class PurchaseReceipt(db.Model):
    """采购收货记录模型"""
    __tablename__ = 'purchase_receipts'

    receipt_id = db.Column(db.String(50), primary_key=True)
    purchase_order_id = db.Column(db.String(50), db.ForeignKey('purchase_orders.purchase_order_id'), nullable=False)
    receipt_time = db.Column(db.DateTime, default=datetime.now)
    operator = db.Column(db.String(50), default='system')
    remark = db.Column(db.String(255))
    status = db.Column(db.String(20), default='completed')  # completed: 已完成

    # 关联关系
    purchase_order = db.relationship('PurchaseOrder', backref='receipts')
    items = db.relationship('PurchaseReceiptItem', backref='receipt', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'receipt_id': self.receipt_id,
            'purchase_order_id': self.purchase_order_id,
            'receipt_time': self.receipt_time.isoformat() if self.receipt_time else None,
            'operator': self.operator,
            'remark': self.remark,
            'status': self.status
        }


class PurchaseReceiptItem(db.Model):
    """采购收货明细模型"""
    __tablename__ = 'purchase_receipt_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    receipt_id = db.Column(db.String(50), db.ForeignKey('purchase_receipts.receipt_id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(100))
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    quality_status = db.Column(db.String(20), default='合格')

    def to_dict(self):
        return {
            'id': self.id,
            'receipt_id': self.receipt_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'quality_status': self.quality_status
        }


class ReplenishmentAdvice(db.Model):
    """补货建议模型"""
    __tablename__ = 'replenishment_advice'

    advice_id = db.Column(db.String(50), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    product_name = db.Column(db.String(100))
    brand = db.Column(db.String(50))
    category = db.Column(db.String(50))
    current_stock = db.Column(db.Integer, default=0)
    threshold = db.Column(db.Integer, default=0)
    suggested_qty = db.Column(db.Integer, default=0)
    daily_sales = db.Column(db.Integer, default=0)
    reason = db.Column(db.String(200))
    estimated_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.Integer, default=0)  # 0: 待处理, 1: 已生成订单, 2: 已取消
    generated_date = db.Column(db.DateTime, default=datetime.now)
    order_id = db.Column(db.String(50))

    # 关联关系
    product = db.relationship('Product', backref='replenishment_advices')

    def to_dict(self):
        return {
            'advice_id': self.advice_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'brand': self.brand,
            'category': self.category,
            'current_stock': self.current_stock,
            'threshold': self.threshold,
            'suggested_qty': self.suggested_qty,
            'daily_sales': self.daily_sales,
            'reason': self.reason,
            'estimated_amount': self.estimated_amount,
            'status': self.status,
            'generated_date': self.generated_date.isoformat() if self.generated_date else None,
            'order_id': self.order_id
        }


class InventoryLog(db.Model):
    """库存日志模型"""
    __tablename__ = 'inventory_logs'

    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    relate_order_id = db.Column(db.String(50))
    change_type = db.Column(db.String(50), nullable=False)  # 销售出库, 采购入库, 退货入库, 盘点调整
    change_qty = db.Column(db.Integer, nullable=False)  # 正数表示增加，负数表示减少
    before_quantity = db.Column(db.Integer, nullable=False)
    after_quantity = db.Column(db.Integer, nullable=False)
    operator = db.Column(db.String(50))
    operate_time = db.Column(db.DateTime, default=datetime.now)
    remark = db.Column(db.String(255))

    # 关联关系
    product = db.relationship('Product', backref='inventory_logs')

    def to_dict(self):
        return {
            'log_id': self.log_id,
            'product_id': self.product_id,
            'product_name': self.product.product_name if self.product else None,
            'relate_order_id': self.relate_order_id,
            'change_type': self.change_type,
            'change_qty': self.change_qty,
            'before_quantity': self.before_quantity,
            'after_quantity': self.after_quantity,
            'operator': self.operator,
            'operate_time': self.operate_time.isoformat() if self.operate_time else None,
            'remark': self.remark
        }


class FinancialRecord(db.Model):
    """财务记录模型"""
    __tablename__ = 'financial_records'

    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Integer, nullable=False)  # 1: 收入, 2: 支出, 3: 成本, 4: 退款, 5: 其他支出
    amount = db.Column(db.Float, nullable=False)
    relate_order_id = db.Column(db.String(50))
    occur_time = db.Column(db.DateTime, default=datetime.now)
    remark = db.Column(db.String(255))
    category = db.Column(db.String(50))  # 支出类别（用于其他支出）

    def to_dict(self):
        return {
            'record_id': self.record_id,
            'type': self.type,
            'type_text': '收入' if self.type == 1 else ('支出' if self.type == 2 else ('成本' if self.type == 3 else ('退款' if self.type == 4 else '其他支出'))),
            'amount': self.amount,
            'relate_order_id': self.relate_order_id,
            'occur_time': self.occur_time.isoformat() if self.occur_time else None,
            'remark': self.remark,
            'category': self.category
        }


class ProductEditLog(db.Model):
    """商品编辑日志模型"""
    __tablename__ = 'product_edit_logs'

    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    edit_type = db.Column(db.String(50), nullable=False)  # create, update, delete
    edit_field = db.Column(db.String(50))
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    operator = db.Column(db.String(50))
    operate_time = db.Column(db.DateTime, default=datetime.now)
    remark = db.Column(db.String(255))

    def to_dict(self):
        return {
            'log_id': self.log_id,
            'product_id': self.product_id,
            'edit_type': self.edit_type,
            'edit_field': self.edit_field,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'operator': self.operator,
            'operate_time': self.operate_time.isoformat() if self.operate_time else None,
            'remark': self.remark
        }
