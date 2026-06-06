"""
数据库初始化脚本
创建所有表并插入示例数据（每种数据仅保留3条）
"""
from datetime import datetime, timedelta
from models import db, User, Customer, Product, Supplier, SalesOrder, SalesOrderItem
from models import PurchaseOrder, PurchaseOrderItem, InventoryLog, FinancialRecord
from app import app


def init_database():
    """初始化数据库并插入示例数据"""
    print("正在创建数据库表...")
    
    with app.app_context():
        # 删除所有表并重新创建
        db.drop_all()
        db.create_all()
        
        print("[OK] 数据库表创建成功")
        print("正在插入示例数据...")
        
        # 1. 创建用户（3条）
        users = [
            User(username='cashier', password='123', role='cashier', status=1),
            User(username='buyer', password='123', role='purchaser', status=1),
            User(username='admin', password='123', role='admin', status=1)
        ]
        db.session.add_all(users)
        db.session.flush()
        print("[OK] 用户数据插入成功 (3条)")
        
        # 2. 创建客户（3条）
        customers = [
            Customer(
                name='张三',
                phone='13800138000',
                email='zhangsan@example.com',
                address='成都高新区',
                register_time=datetime(2026, 1, 1).date(),
                points=5000
            ),
            Customer(
                name='李四',
                phone='13900139000',
                email='lisi@example.com',
                address='成都武侯区',
                register_time=datetime(2026, 2, 15).date(),
                points=2000
            ),
            Customer(
                name='王五',
                phone='13700137000',
                email='wangwu@example.com',
                address='成都锦江区',
                register_time=datetime(2026, 3, 20).date(),
                points=800
            )
        ]
        db.session.add_all(customers)
        db.session.flush()
        print("[OK] 客户数据插入成功 (3条)")
        
        # 3. 创建供应商（3条）
        suppliers = [
            Supplier(
                supplier_name='海尔电器有限公司',
                contact_person='王经理',
                contact_phone='0532-1234567',
                address='青岛',
                status=1
            ),
            Supplier(
                supplier_name='美的集团',
                contact_person='李经理',
                contact_phone='0757-1234567',
                address='佛山',
                status=1
            ),
            Supplier(
                supplier_name='小米科技有限公司',
                contact_person='张经理',
                contact_phone='010-1234567',
                address='北京',
                status=1
            )
        ]
        db.session.add_all(suppliers)
        db.session.flush()
        print("[OK] 供应商数据插入成功 (3条)")
        
        # 4. 创建商品（3条）
        products = [
            Product(
                product_name='海尔冰箱 BCD-216',
                brand='海尔',
                model='BCD-216',
                category='冰箱',
                retail_price=1899.00,
                purchase_ref_price=1500.00,
                current_stock=10,
                threshold=5,
                status=1,
                unit='台',
                warehouse='A',
                shelf_no='1'
            ),
            Product(
                product_name='美的空调 KFR-35',
                brand='美的',
                model='KFR-35',
                category='空调',
                retail_price=2599.00,
                purchase_ref_price=2000.00,
                current_stock=3,
                threshold=5,
                status=1,
                unit='台',
                warehouse='B',
                shelf_no='5'
            ),
            Product(
                product_name='小米电视 4A 55寸',
                brand='小米',
                model='4A55',
                category='电视',
                retail_price=1899.00,
                purchase_ref_price=1600.00,
                current_stock=8,
                threshold=5,
                status=1,
                unit='台',
                warehouse='C',
                shelf_no='10'
            )
        ]
        db.session.add_all(products)
        db.session.flush()
        print("[OK] 商品数据插入成功 (3条)")
        
        # 5. 创建销售订单（3条）
        order1 = SalesOrder(
            order_id='SO202606010001',
            customer_id=1,
            order_time=datetime(2026, 6, 1, 10, 30, 0),
            total_amount=3798.00,
            discount_amount=0.00,
            final_amount=3798.00,
            payment_method='微信支付',
            payment_status=1,
            shipping_address='成都高新区天府大道100号',
            is_cancelled=0,
            is_returned=0
        )
        
        order2 = SalesOrder(
            order_id='SO202606020001',
            customer_id=2,
            order_time=datetime(2026, 6, 2, 14, 20, 0),
            total_amount=2599.00,
            discount_amount=0.00,
            final_amount=2599.00,
            payment_method='支付宝',
            payment_status=1,
            shipping_address='成都武侯区科华北路66号',
            is_cancelled=0,
            is_returned=0
        )
        
        order3 = SalesOrder(
            order_id='SO202606030001',
            customer_id=3,
            order_time=datetime(2026, 6, 3, 9, 45, 0),
            total_amount=1899.00,
            discount_amount=0.00,
            final_amount=1899.00,
            payment_method='微信支付',
            payment_status=1,
            shipping_address='成都锦江区春熙路100号',
            is_cancelled=0,
            is_returned=0
        )
        
        db.session.add_all([order1, order2, order3])
        db.session.flush()
        print("[OK] 销售订单数据插入成功 (3条)")
        
        # 6. 创建销售订单项（3条）
        sales_items = [
            SalesOrderItem(
                order_id='SO202606010001',
                product_id=1,
                quantity=2,
                unit_price=1899.00,
                cost_price=1500.00
            ),
            SalesOrderItem(
                order_id='SO202606020001',
                product_id=2,
                quantity=1,
                unit_price=2599.00,
                cost_price=2000.00
            ),
            SalesOrderItem(
                order_id='SO202606030001',
                product_id=3,
                quantity=1,
                unit_price=1899.00,
                cost_price=1600.00
            )
        ]
        db.session.add_all(sales_items)
        print("[OK] 销售订单项数据插入成功 (3条)")
        
        # 7. 创建采购订单（3条）
        purchase_order1 = PurchaseOrder(
            purchase_order_id='PO202606010001',
            supplier_id=2,
            order_time=datetime(2026, 6, 1, 14, 0, 0),
            expected_date=datetime(2026, 6, 5).date(),
            status='completed',
            total_amount=10000.00,
            remark='采购美的空调',
            received_time=datetime(2026, 6, 5, 10, 0, 0)
        )
        
        purchase_order2 = PurchaseOrder(
            purchase_order_id='PO202606020001',
            supplier_id=1,
            order_time=datetime(2026, 6, 2, 10, 0, 0),
            expected_date=datetime(2026, 6, 6).date(),
            status='partial',
            total_amount=7500.00,
            remark='采购海尔冰箱',
            received_time=datetime(2026, 6, 5, 11, 0, 0)
        )
        
        purchase_order3 = PurchaseOrder(
            purchase_order_id='PO202606030001',
            supplier_id=3,
            order_time=datetime(2026, 6, 3, 15, 0, 0),
            expected_date=datetime(2026, 6, 8).date(),
            status='pending',
            total_amount=8000.00,
            remark='采购小米电视'
        )
        
        db.session.add_all([purchase_order1, purchase_order2, purchase_order3])
        db.session.flush()
        print("[OK] 采购订单数据插入成功 (3条)")
        
        # 8. 创建采购订单项（3条）
        purchase_items = [
            PurchaseOrderItem(
                purchase_order_id='PO202606010001',
                product_id=2,
                quantity=5,
                received_quantity=5,
                unit_price=2000.00
            ),
            PurchaseOrderItem(
                purchase_order_id='PO202606020001',
                product_id=1,
                quantity=5,
                received_quantity=3,
                unit_price=1500.00
            ),
            PurchaseOrderItem(
                purchase_order_id='PO202606030001',
                product_id=3,
                quantity=5,
                received_quantity=0,
                unit_price=1600.00
            )
        ]
        db.session.add_all(purchase_items)
        print("[OK] 采购订单项数据插入成功 (3条)")
        
        # 9. 创建库存日志（3条）
        inventory_logs = [
            InventoryLog(
                product_id=1,
                relate_order_id='SO202606010001',
                change_type='销售出库',
                change_qty=-2,
                before_quantity=12,
                after_quantity=10,
                operator='cashier',
                operate_time=datetime(2026, 6, 1, 10, 35, 0),
                remark='销售订单出库'
            ),
            InventoryLog(
                product_id=2,
                relate_order_id='PO202606010001',
                change_type='采购入库',
                change_qty=5,
                before_quantity=3,
                after_quantity=8,
                operator='buyer',
                operate_time=datetime(2026, 6, 5, 10, 5, 0),
                remark='采购入库'
            ),
            InventoryLog(
                product_id=1,
                relate_order_id='PO202606020001',
                change_type='采购入库',
                change_qty=3,
                before_quantity=10,
                after_quantity=13,
                operator='buyer',
                operate_time=datetime(2026, 6, 5, 11, 5, 0),
                remark='采购入库'
            )
        ]
        db.session.add_all(inventory_logs)
        print("[OK] 库存日志数据插入成功 (3条)")
        
        # 10. 创建财务记录（3条）
        financial_records = [
            FinancialRecord(
                type=1,  # 收入
                amount=3798.00,
                relate_order_id='SO202606010001',
                occur_time=datetime(2026, 6, 1, 10, 35, 0),
                remark='销售收款'
            ),
            FinancialRecord(
                type=2,  # 采购支出
                amount=10000.00,
                relate_order_id='PO202606010001',
                occur_time=datetime(2026, 6, 5, 10, 5, 0),
                remark='采购支出'
            ),
            FinancialRecord(
                type=1,  # 收入
                amount=2599.00,
                relate_order_id='SO202606020001',
                occur_time=datetime(2026, 6, 2, 14, 25, 0),
                remark='销售收款'
            )
        ]
        db.session.add_all(financial_records)
        print("[OK] 财务记录数据插入成功 (3条)")
        
        # 提交所有更改
        db.session.commit()
        
        print("\n" + "="*50)
        print("数据库初始化完成！")
        print("="*50)
        print("\n默认账号:")
        print("  - 收银员: cashier / 123")
        print("  - 采购员: buyer / 123")
        print("  - 管理员: admin / 123")


if __name__ == '__main__':
    init_database()
