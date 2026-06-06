"""
数据库管理路由 - 用于清空和初始化数据库
"""
from flask import Blueprint, jsonify, request, send_file
from models import db, User, Customer, Supplier, Product, SalesOrder, SalesOrderItem, \
    PurchaseOrder, PurchaseOrderItem, InventoryLog, FinancialRecord, ProductEditLog
from sqlalchemy import text
from datetime import datetime
import json
import os

db_manage_bp = Blueprint('db_manage', __name__)

@db_manage_bp.route('/api/db/clear', methods=['POST'])
def clear_database():
    """清空数据库所有数据（保留表结构）"""
    try:
        # 获取所有表名（SQLAlchemy 2.0+ 兼容方式）
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        # 按外键依赖顺序删除数据
        table_order = [
            'customer_points_logs',
            'sales_order_items', 
            'purchase_order_items',
            'sales_orders',
            'purchase_orders',
            'inventory_logs',
            'financial_records',
            'customers',
            'suppliers',
            'products',
            'warehouse_locations',
            'warehouse_areas',
            'product_edit_logs',
            'users'
        ]
        
        with db.engine.connect() as conn:
            for table in table_order:
                if table in tables:
                    conn.execute(text(f'DELETE FROM {table}'))
            
            # 重置自增计数器
            for table in tables:
                conn.execute(text(f'DELETE FROM sqlite_sequence WHERE name = "{table}"'))
            conn.commit()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '数据库清空成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'清空数据库失败: {str(e)}'
        }), 500

@db_manage_bp.route('/api/db/reinit', methods=['POST'])
def reinit_database():
    """重新初始化数据库（清空并创建示例数据）"""
    try:
        # 获取所有表名
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        # 清空所有表
        with db.engine.connect() as conn:
            for table in tables:
                conn.execute(text(f'DELETE FROM {table}'))
                conn.execute(text(f'DELETE FROM sqlite_sequence WHERE name = "{table}"'))
            conn.commit()
        
        db.session.commit()
        
        # 重新导入并执行初始化
        import importlib
        import init_db
        importlib.reload(init_db)
        
        return jsonify({
            'success': True,
            'message': '数据库重新初始化成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'初始化数据库失败: {str(e)}'
        }), 500

@db_manage_bp.route('/api/db/status', methods=['GET'])
def get_db_status():
    """获取数据库状态"""
    try:
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        # 统计各表数据量
        stats = {}
        with db.engine.connect() as conn:
            for table in tables:
                result = conn.execute(text(f'SELECT COUNT(*) FROM {table}'))
                stats[table] = result.scalar()
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取数据库状态失败: {str(e)}'
        }), 500


@db_manage_bp.route('/api/db/export', methods=['GET'])
def export_database():
    """导出数据库所有数据"""
    try:
        # 导出所有表数据
        data = {
            'export_time': datetime.now().isoformat(),
            'version': '1.0',
            'tables': {}
        }
        
        # 导出用户表
        data['tables']['users'] = [user.to_dict() for user in User.query.all()]
        
        # 导出客户表
        data['tables']['customers'] = [customer.to_dict() for customer in Customer.query.all()]
        
        # 导出供应商表
        data['tables']['suppliers'] = [supplier.to_dict() for supplier in Supplier.query.all()]
        
        # 导出商品表
        data['tables']['products'] = [product.to_dict() for product in Product.query.all()]
        
        # 导出销售订单表
        data['tables']['sales_orders'] = [order.to_dict() for order in SalesOrder.query.all()]
        
        # 导出销售订单项表
        data['tables']['sales_order_items'] = [item.to_dict() for item in SalesOrderItem.query.all()]
        
        # 导出采购订单表
        data['tables']['purchase_orders'] = [order.to_dict() for order in PurchaseOrder.query.all()]
        
        # 导出采购订单项表
        data['tables']['purchase_order_items'] = [item.to_dict() for item in PurchaseOrderItem.query.all()]
        
        # 导出库存日志表
        data['tables']['inventory_logs'] = [log.to_dict() for log in InventoryLog.query.all()]
        
        # 导出财务记录表
        data['tables']['financial_records'] = [record.to_dict() for record in FinancialRecord.query.all()]
        
        # 导出商品编辑日志表
        data['tables']['product_edit_logs'] = [log.to_dict() for log in ProductEditLog.query.all()]
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'导出数据库失败: {str(e)}'
        }), 500


@db_manage_bp.route('/api/db/import', methods=['POST'])
def import_database():
    """导入数据库数据"""
    try:
        data = request.get_json()
        
        if not data or 'tables' not in data:
            return jsonify({
                'success': False,
                'message': '无效的导入数据格式'
            }), 400
        
        tables = data['tables']
        
        # 使用事务确保导入的原子性
        with db.session.begin_nested():
            # 清空现有数据（按外键顺序）
            table_order = [
                'sales_order_items', 'purchase_order_items',
                'sales_orders', 'purchase_orders',
                'inventory_logs', 'financial_records',
                'product_edit_logs',
                'customers', 'suppliers', 'products', 'users'
            ]
            
            for table_name in table_order:
                if table_name in ['users', 'customers', 'suppliers', 'products', 
                                'sales_orders', 'sales_order_items', 'purchase_orders', 
                                'purchase_order_items', 'inventory_logs', 'financial_records',
                                'product_edit_logs']:
                    model_class = {
                        'users': User,
                        'customers': Customer,
                        'suppliers': Supplier,
                        'products': Product,
                        'sales_orders': SalesOrder,
                        'sales_order_items': SalesOrderItem,
                        'purchase_orders': PurchaseOrder,
                        'purchase_order_items': PurchaseOrderItem,
                        'inventory_logs': InventoryLog,
                        'financial_records': FinancialRecord,
                        'product_edit_logs': ProductEditLog
                    }.get(table_name)
                    if model_class:
                        model_class.query.delete()
        
        # 重置自增计数器
        inspector = db.inspect(db.engine)
        all_tables = inspector.get_table_names()
        with db.engine.connect() as conn:
            for table in all_tables:
                conn.execute(text(f'DELETE FROM sqlite_sequence WHERE name = "{table}"'))
            conn.commit()
        
        db.session.commit()
        
        # 导入数据
        with db.session.begin_nested():
            # 导入用户
            if 'users' in tables:
                for user_data in tables['users']:
                    user = User(**user_data)
                    db.session.add(user)
            
            # 导入客户
            if 'customers' in tables:
                for customer_data in tables['customers']:
                    customer = Customer(**customer_data)
                    db.session.add(customer)
            
            # 导入供应商
            if 'suppliers' in tables:
                for supplier_data in tables['suppliers']:
                    supplier = Supplier(**supplier_data)
                    db.session.add(supplier)
            
            # 导入商品
            if 'products' in tables:
                for product_data in tables['products']:
                    product = Product(**product_data)
                    db.session.add(product)
            
            # 导入销售订单
            if 'sales_orders' in tables:
                for order_data in tables['sales_orders']:
                    order = SalesOrder(**order_data)
                    db.session.add(order)
            
            # 导入销售订单项
            if 'sales_order_items' in tables:
                for item_data in tables['sales_order_items']:
                    item = SalesOrderItem(**item_data)
                    db.session.add(item)
            
            # 导入采购订单
            if 'purchase_orders' in tables:
                for order_data in tables['purchase_orders']:
                    order = PurchaseOrder(**order_data)
                    db.session.add(order)
            
            # 导入采购订单项
            if 'purchase_order_items' in tables:
                for item_data in tables['purchase_order_items']:
                    item = PurchaseOrderItem(**item_data)
                    db.session.add(item)
            
            # 导入库存日志
            if 'inventory_logs' in tables:
                for log_data in tables['inventory_logs']:
                    log = InventoryLog(**log_data)
                    db.session.add(log)
            
            # 导入财务记录
            if 'financial_records' in tables:
                for record_data in tables['financial_records']:
                    record = FinancialRecord(**record_data)
                    db.session.add(record)
            
            # 导入商品编辑日志
            if 'product_edit_logs' in tables:
                for log_data in tables['product_edit_logs']:
                    log = ProductEditLog(**log_data)
                    db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '数据库导入成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'导入数据库失败: {str(e)}'
        }), 500


@db_manage_bp.route('/api/db/backup', methods=['POST'])
def backup_database():
    """创建数据库备份"""
    try:
        # 导出数据作为备份
        data = {
            'backup_time': datetime.now().isoformat(),
            'version': '1.0',
            'tables': {}
        }
        
        data['tables']['users'] = [user.to_dict() for user in User.query.all()]
        data['tables']['customers'] = [customer.to_dict() for customer in Customer.query.all()]
        data['tables']['suppliers'] = [supplier.to_dict() for supplier in Supplier.query.all()]
        data['tables']['products'] = [product.to_dict() for product in Product.query.all()]
        data['tables']['sales_orders'] = [order.to_dict() for order in SalesOrder.query.all()]
        data['tables']['sales_order_items'] = [item.to_dict() for item in SalesOrderItem.query.all()]
        data['tables']['purchase_orders'] = [order.to_dict() for order in PurchaseOrder.query.all()]
        data['tables']['purchase_order_items'] = [item.to_dict() for item in PurchaseOrderItem.query.all()]
        data['tables']['inventory_logs'] = [log.to_dict() for log in InventoryLog.query.all()]
        data['tables']['financial_records'] = [record.to_dict() for record in FinancialRecord.query.all()]
        data['tables']['product_edit_logs'] = [log.to_dict() for log in ProductEditLog.query.all()]
        
        # 保存备份文件
        backup_dir = os.path.join(os.path.dirname(__file__), '..', 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        backup_filename = f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        backup_path = os.path.join(backup_dir, backup_filename)
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'message': '备份创建成功',
            'backup_file': backup_filename
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建备份失败: {str(e)}'
        }), 500


@db_manage_bp.route('/api/db/restore', methods=['POST'])
def restore_database():
    """从备份恢复数据库"""
    try:
        data = request.get_json()
        backup_data = data.get('backup_data')
        
        if not backup_data or 'tables' not in backup_data:
            return jsonify({
                'success': False,
                'message': '无效的备份数据格式'
            }), 400
        
        tables = backup_data['tables']
        
        # 使用事务确保恢复的原子性
        with db.session.begin_nested():
            # 清空现有数据
            table_order = [
                'sales_order_items', 'purchase_order_items',
                'sales_orders', 'purchase_orders',
                'inventory_logs', 'financial_records',
                'product_edit_logs',
                'customers', 'suppliers', 'products', 'users'
            ]
            
            for table_name in table_order:
                model_class = {
                    'users': User,
                    'customers': Customer,
                    'suppliers': Supplier,
                    'products': Product,
                    'sales_orders': SalesOrder,
                    'sales_order_items': SalesOrderItem,
                    'purchase_orders': PurchaseOrder,
                    'purchase_order_items': PurchaseOrderItem,
                    'inventory_logs': InventoryLog,
                    'financial_records': FinancialRecord,
                    'product_edit_logs': ProductEditLog
                }.get(table_name)
                if model_class:
                    model_class.query.delete()
        
        # 重置自增计数器
        inspector = db.inspect(db.engine)
        all_tables = inspector.get_table_names()
        with db.engine.connect() as conn:
            for table in all_tables:
                conn.execute(text(f'DELETE FROM sqlite_sequence WHERE name = "{table}"'))
            conn.commit()
        
        db.session.commit()
        
        # 恢复数据
        with db.session.begin_nested():
            if 'users' in tables:
                for user_data in tables['users']:
                    user = User(**user_data)
                    db.session.add(user)
            
            if 'customers' in tables:
                for customer_data in tables['customers']:
                    customer = Customer(**customer_data)
                    db.session.add(customer)
            
            if 'suppliers' in tables:
                for supplier_data in tables['suppliers']:
                    supplier = Supplier(**supplier_data)
                    db.session.add(supplier)
            
            if 'products' in tables:
                for product_data in tables['products']:
                    product = Product(**product_data)
                    db.session.add(product)
            
            if 'sales_orders' in tables:
                for order_data in tables['sales_orders']:
                    order = SalesOrder(**order_data)
                    db.session.add(order)
            
            if 'sales_order_items' in tables:
                for item_data in tables['sales_order_items']:
                    item = SalesOrderItem(**item_data)
                    db.session.add(item)
            
            if 'purchase_orders' in tables:
                for order_data in tables['purchase_orders']:
                    order = PurchaseOrder(**order_data)
                    db.session.add(order)
            
            if 'purchase_order_items' in tables:
                for item_data in tables['purchase_order_items']:
                    item = PurchaseOrderItem(**item_data)
                    db.session.add(item)
            
            if 'inventory_logs' in tables:
                for log_data in tables['inventory_logs']:
                    log = InventoryLog(**log_data)
                    db.session.add(log)
            
            if 'financial_records' in tables:
                for record_data in tables['financial_records']:
                    record = FinancialRecord(**record_data)
                    db.session.add(record)
            
            if 'product_edit_logs' in tables:
                for log_data in tables['product_edit_logs']:
                    log = ProductEditLog(**log_data)
                    db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '数据库恢复成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'恢复数据库失败: {str(e)}'
        }), 500