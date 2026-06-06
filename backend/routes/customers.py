"""
客户管理 API 路由
"""
from flask import Blueprint, request, jsonify
from models import db, Customer, SalesOrder, SalesOrderItem
import re

customers_bp = Blueprint('customers', __name__, url_prefix='/api/customers')


def validate_phone(phone):
    """验证手机号格式"""
    # 简单的手机号验证：11位数字，以1开头
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None


@customers_bp.route('', methods=['GET'])
def get_customers():
    """获取客户列表（支持分页、排序和筛选）"""
    try:
        # 获取查询参数
        name = request.args.get('name')
        phone = request.args.get('phone')
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        sort_by = request.args.get('sort_by', 'customer_id')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 构建查询
        query = Customer.query
        
        # 筛选条件
        if name:
            query = query.filter(Customer.name.like(f'%{name}%'))
        
        if phone:
            query = query.filter(Customer.phone.like(f'%{phone}%'))
        
        # 排序
        if sort_by in ['customer_id', 'name', 'register_time']:
            if sort_order == 'asc':
                query = query.order_by(getattr(Customer, sort_by).asc())
            else:
                query = query.order_by(getattr(Customer, sort_by).desc())
        
        # 分页
        total = query.count()
        customers = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return jsonify({
            'success': True,
            'data': [customer.to_dict() for customer in customers],
            'total': total,
            'page': page,
            'page_size': page_size
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@customers_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """获取单个客户信息"""
    try:
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({
                'success': False,
                'error': '客户不存在',
                'code': 404
            }), 404
        
        return jsonify({
            'success': True,
            'data': customer.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@customers_bp.route('', methods=['POST'])
def create_customer():
    """添加客户"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        phone = data.get('phone')
        if not phone:
            return jsonify({
                'success': False,
                'error': '手机号为必填项',
                'code': 400
            }), 400
        
        # 验证手机号格式
        if not validate_phone(phone):
            return jsonify({
                'success': False,
                'error': '手机号格式不正确',
                'code': 400
            }), 400
        
        # 检查手机号是否已存在
        existing = Customer.query.filter_by(phone=phone).first()
        if existing:
            return jsonify({
                'success': False,
                'error': '该手机号已被注册',
                'code': 400
            }), 400
        
        # 获取会员等级并设置折扣率
        membership_level = data.get('membership_level', '普通会员')
        discount_rate = 1.0
        if membership_level == '白银会员':
            discount_rate = 0.95
        elif membership_level == '黄金会员':
            discount_rate = 0.9
        
        # 创建客户
        customer = Customer(
            name=data.get('name', ''),
            phone=phone,
            email=data.get('email'),
            address=data.get('address'),
            register_time=data.get('register_time'),
            membership_level=membership_level,
            discount_rate=discount_rate,
            points=data.get('points', 0)
        )
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': customer.to_dict(),
            'message': '客户添加成功',
            'code': 201
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@customers_bp.route('/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """更新客户信息"""
    try:
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({
                'success': False,
                'error': '客户不存在',
                'code': 404
            }), 404
        
        data = request.get_json()
        
        # 更新字段（仅允许更新指定字段）
        allowed_fields = ['name', 'phone', 'email', 'address', 'membership_level', 'points']
        
        for field in allowed_fields:
            if field in data:
                setattr(customer, field, data[field])
        
        # 如果更新了会员等级，同步更新折扣率
        if 'membership_level' in data:
            membership_level = data['membership_level']
            if membership_level == '普通会员':
                customer.discount_rate = 1.0
            elif membership_level == '白银会员':
                customer.discount_rate = 0.95
            elif membership_level == '黄金会员':
                customer.discount_rate = 0.9
        
        # 如果更新了手机号，验证格式
        if 'phone' in data:
            if not validate_phone(data['phone']):
                return jsonify({
                    'success': False,
                    'error': '手机号格式不正确',
                    'code': 400
                }), 400
            
            # 检查新手机号是否已被其他客户使用
            existing = Customer.query.filter(
                Customer.phone == data['phone'],
                Customer.customer_id != customer_id
            ).first()
            if existing:
                return jsonify({
                    'success': False,
                    'error': '该手机号已被其他客户使用',
                    'code': 400
                }), 400
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': customer.to_dict(),
            'message': '客户信息更新成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """删除客户"""
    try:
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({
                'success': False,
                'error': '客户不存在',
                'code': 404
            }), 404
        
        # 检查是否存在关联的销售订单
        order_count = SalesOrder.query.filter_by(customer_id=customer_id).count()
        if order_count > 0:
            return jsonify({
                'success': False,
                'error': f'该客户存在 {order_count} 个销售订单，无法删除',
                'code': 400
            }), 400
        
        # 删除客户
        db.session.delete(customer)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '客户删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@customers_bp.route('/<int:customer_id>/orders', methods=['GET'])
def get_customer_orders(customer_id):
    """获取客户购买历史"""
    try:
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({
                'success': False,
                'error': '客户不存在',
                'code': 404
            }), 404
        
        # 获取客户的所有订单
        orders = SalesOrder.query.filter_by(customer_id=customer_id)\
                                .order_by(SalesOrder.order_time.desc())\
                                .all()
        
        result = []
        for order in orders:
            order_data = order.to_dict()
            order_data['items'] = []
            
            # 获取订单明细
            total_paid = 0
            for item in order.items:
                item_data = item.to_dict()
                item_data['subtotal'] = item.quantity * item.unit_price
                total_paid += item_data['subtotal']
                order_data['items'].append(item_data)
            
            order_data['total_paid'] = total_paid
            result.append(order_data)
        
        return jsonify({
            'success': True,
            'data': result,
            'customer': customer.to_dict(),
            'total_orders': len(result)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500
