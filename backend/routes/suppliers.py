"""
供应商管理 API 路由
"""
from flask import Blueprint, request, jsonify
from models import db, Supplier, PurchaseOrder, PurchaseReceipt, PurchaseReceiptItem, PurchaseOrderItem
from datetime import datetime

suppliers_bp = Blueprint('suppliers', __name__, url_prefix='/api/suppliers')


def calculate_supplier_kpi(supplier):
    """计算供应商KPI指标"""
    orders = PurchaseOrder.query.filter_by(supplier_id=supplier.supplier_id).all()
    
    if not orders:
        return {
            'on_time_delivery_rate': 0,
            'average_delivery_days': 0,
            'last_order_date': None,
            'quality_rate': 0.0,
            'quality_count': 0,
            'total_inspected': 0
        }
    
    # 计算准时交付率
    on_time_count = 0
    total_completed = 0
    total_delivery_days = 0
    
    for order in orders:
        if order.status in ['completed', 'partial'] and order.received_time:
            total_completed += 1
            
            # 计算交付天数
            order_time = order.order_time
            received_time = order.received_time
            delivery_days = (received_time - order_time).days
            total_delivery_days += delivery_days
            
            # 判断是否准时交付
            if order.expected_date:
                expected_dt = datetime.combine(order.expected_date, datetime.min.time())
                if received_time <= expected_dt:
                    on_time_count += 1
    
    # 计算准时交付率
    on_time_delivery_rate = round((on_time_count / total_completed) * 100, 1) if total_completed > 0 else 0
    
    # 计算平均交付天数
    average_delivery_days = round(total_delivery_days / total_completed, 1) if total_completed > 0 else 0
    
    # 计算最近采购日期
    order_times = [order.order_time for order in orders if order.order_time]
    last_order_date = max(order_times).date().isoformat() if order_times else None
    
    # 计算合格率
    quality_count = 0
    total_inspected = 0
    
    for order in orders:
        receipt_items = PurchaseReceiptItem.query.join(
            PurchaseReceipt, PurchaseReceipt.receipt_id == PurchaseReceiptItem.receipt_id
        ).filter(PurchaseReceipt.purchase_order_id == order.purchase_order_id).all()
        
        for item in receipt_items:
            total_inspected += item.quantity
            if item.quality_status == '合格':
                quality_count += item.quantity
    
    quality_rate = round((quality_count / total_inspected) * 100, 1) if total_inspected > 0 else 0.0
    
    return {
        'on_time_rate': on_time_delivery_rate,
        'average_delivery_days': average_delivery_days,
        'last_order_date': last_order_date,
        'quality_rate': quality_rate,
        'quality_count': quality_count,
        'total_inspected': total_inspected
    }


@suppliers_bp.route('', methods=['GET'])
def get_suppliers():
    """获取所有供应商（包含KPI指标）"""
    try:
        status = request.args.get('status', type=int)
        sort_by = request.args.get('sort_by', 'supplier_id')
        sort_order = request.args.get('sort_order', 'desc')
        
        query = Supplier.query
        
        if status is not None:
            query = query.filter(Supplier.status == status)
        
        # 数据库层排序
        sort_columns = {
            'supplier_id': Supplier.supplier_id,
            'supplier_name': Supplier.supplier_name
        }
        
        if sort_by in sort_columns:
            if sort_order == 'asc':
                query = query.order_by(sort_columns[sort_by].asc())
            else:
                query = query.order_by(sort_columns[sort_by].desc())
        else:
            query = query.order_by(Supplier.supplier_id.desc())
        
        suppliers = query.all()
        
        supplier_data = []
        for supplier in suppliers:
            supplier_dict = supplier.to_dict()
            kpi = calculate_supplier_kpi(supplier)
            supplier_dict.update(kpi)
            supplier_data.append(supplier_dict)
        
        # 如果按KPI字段排序，需要在内存中排序
        if sort_by in ['on_time_rate', 'average_delivery_days', 'quality_rate']:
            if sort_order == 'asc':
                supplier_data.sort(key=lambda x: x.get(sort_by, 0))
            else:
                supplier_data.sort(key=lambda x: x.get(sort_by, 0), reverse=True)
        
        return jsonify({
            'success': True,
            'data': supplier_data,
            'total': len(supplier_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@suppliers_bp.route('/<int:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    """获取单个供应商"""
    try:
        supplier = Supplier.query.get(supplier_id)
        
        if not supplier:
            return jsonify({
                'success': False,
                'error': '供应商不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': supplier.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@suppliers_bp.route('', methods=['POST'])
def create_supplier():
    """添加供应商"""
    try:
        data = request.get_json()
        
        # 基本验证
        if 'supplier_name' not in data:
            return jsonify({
                'success': False,
                'error': '缺少供应商名称'
            }), 400
        
        # 检查是否已存在同名供应商
        existing = Supplier.query.filter_by(supplier_name=data['supplier_name']).first()
        if existing:
            return jsonify({
                'success': False,
                'error': '供应商名称已存在'
            }), 400
        
        # 创建供应商
        supplier = Supplier(
            supplier_name=data['supplier_name'],
            contact_person=data.get('contact_person'),
            contact_phone=data.get('contact_phone'),
            address=data.get('address'),
            status=int(data.get('status', 1))
        )
        
        db.session.add(supplier)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': supplier.to_dict(),
            'message': '供应商添加成功'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@suppliers_bp.route('/<int:supplier_id>', methods=['PUT'])
def update_supplier(supplier_id):
    """更新供应商"""
    try:
        supplier = Supplier.query.get(supplier_id)
        
        if not supplier:
            return jsonify({
                'success': False,
                'error': '供应商不存在'
            }), 404
        
        data = request.get_json()
        
        # 更新字段
        for field in ['supplier_name', 'contact_person', 'contact_phone', 'address', 'status']:
            if field in data:
                setattr(supplier, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': supplier.to_dict(),
            'message': '供应商更新成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@suppliers_bp.route('/<int:supplier_id>', methods=['DELETE'])
def delete_supplier(supplier_id):
    """删除供应商"""
    try:
        supplier = Supplier.query.get(supplier_id)
        
        if not supplier:
            return jsonify({
                'success': False,
                'error': '供应商不存在'
            }), 404
        
        # 检查关联的采购订单
        related_orders = PurchaseOrder.query.filter_by(supplier_id=supplier_id).count()
        
        if related_orders > 0:
            return jsonify({
                'success': False,
                'error': f'该供应商存在 {related_orders} 个关联采购订单，无法删除'
            }), 400
        
        # 删除供应商
        db.session.delete(supplier)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '供应商删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@suppliers_bp.route('/<int:supplier_id>/orders', methods=['GET'])
def get_supplier_orders(supplier_id):
    """获取供应商的采购订单"""
    try:
        supplier = Supplier.query.get(supplier_id)
        
        if not supplier:
            return jsonify({
                'success': False,
                'error': '供应商不存在'
            }), 404
        
        # 获取该供应商的所有采购订单
        orders = PurchaseOrder.query.filter_by(supplier_id=supplier_id)\
            .order_by(PurchaseOrder.order_time.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [order.to_dict() for order in orders],
            'total': len(orders)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@suppliers_bp.route('/<int:supplier_id>/statistics', methods=['GET'])
def get_supplier_statistics(supplier_id):
    """获取供应商统计信息"""
    try:
        supplier = Supplier.query.get(supplier_id)
        
        if not supplier:
            return jsonify({
                'success': False,
                'error': '供应商不存在'
            }), 404
        
        # 统计采购订单
        orders = PurchaseOrder.query.filter_by(supplier_id=supplier_id).all()
        
        total_orders = len(orders)
        total_amount = sum(order.total_amount or 0 for order in orders)
        pending_orders = len([o for o in orders if o.status == 'pending'])
        completed_orders = len([o for o in orders if o.status == 'completed'])
        
        return jsonify({
            'success': True,
            'data': {
                'supplier_id': supplier_id,
                'supplier_name': supplier.supplier_name,
                'total_orders': total_orders,
                'total_amount': total_amount,
                'pending_orders': pending_orders,
                'completed_orders': completed_orders
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
