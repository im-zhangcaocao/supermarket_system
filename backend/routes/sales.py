"""
销售订单管理 API 路由
"""
from flask import Blueprint, request, jsonify
from models import db, SalesOrder, SalesOrderItem, Customer, Product, InventoryLog, FinancialRecord
from datetime import datetime, date

sales_bp = Blueprint('sales', __name__, url_prefix='/api/sales')


def generate_order_id():
    """生成订单号：SO + yyyymmdd + 4位流水号（每天从0001开始）"""
    today_str = date.today().strftime('%Y%m%d')
    today_prefix = f'SO{today_str}'
    
    # 查询今天最大的订单号
    today_orders = SalesOrder.query.filter(SalesOrder.order_id.like(f'{today_prefix}%')).all()
    
    if not today_orders:
        sequence = 1
    else:
        # 提取流水号并找出最大值
        max_seq = 0
        for order in today_orders:
            seq_str = order.order_id[-4:]
            if seq_str.isdigit():
                seq = int(seq_str)
                if seq > max_seq:
                    max_seq = seq
        sequence = max_seq + 1
    
    # 格式化为4位数字
    order_id = f'{today_prefix}{sequence:04d}'
    return order_id


def calculate_order_amount(items):
    """计算订单金额"""
    total_amount = 0.0
    for item in items:
        total_amount += item['unit_price'] * item['quantity']
    return total_amount


@sales_bp.route('/orders', methods=['GET'])
def get_sales_orders():
    """获取所有销售订单"""
    try:
        # 获取查询参数
        customer_id = request.args.get('customer_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        is_cancelled = request.args.get('is_cancelled', type=int)
        
        # 构建查询
        query = SalesOrder.query
        
        if customer_id:
            query = query.filter(SalesOrder.customer_id == customer_id)
        
        if start_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(SalesOrder.order_time >= start_datetime)
        
        if end_date:
            end_datetime = datetime.strptime(f'{end_date} 23:59:59', '%Y-%m-%d %H:%M:%S')
            query = query.filter(SalesOrder.order_time <= end_datetime)
        
        if is_cancelled is not None:
            query = query.filter(SalesOrder.is_cancelled == is_cancelled)
        
        # 按订单时间倒序排列
        orders = query.order_by(SalesOrder.order_time.desc()).all()
        
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


@sales_bp.route('/orders/<order_id>', methods=['GET'])
def get_sales_order(order_id):
    """获取单个订单及明细"""
    try:
        order = SalesOrder.query.filter_by(order_id=order_id).first()
        
        if not order:
            return jsonify({
                'success': False,
                'error': '订单不存在'
            }), 404
        
        # 包含订单明细
        order_data = order.to_dict()
        order_data['items'] = [item.to_dict() for item in order.items]
        
        return jsonify({
            'success': True,
            'data': order_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sales_bp.route('/orders', methods=['POST'])
def create_sales_order():
    """创建销售订单（支持积分抵扣）"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['customer_id', 'items', 'payment_method']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必需字段: {field}'
                }), 400
        
        customer_id = data['customer_id']
        items_data = data['items']
        payment_method = data['payment_method']
        shipping_address = data.get('shipping_address', '')
        discount_amount = data.get('discount_amount', 0.0)
        points_used = data.get('points_used', 0)  # 使用的积分数量
        
        # 验证客户是否存在
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({
                'success': False,
                'error': '客户不存在'
            }), 400
        
        # 验证订单明细
        if not items_data or len(items_data) == 0:
            return jsonify({
                'success': False,
                'error': '订单至少需要一个商品'
            }), 400
        
        # 验证每个商品
        for item_data in items_data:
            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity', 0)
            
            if not product_id or quantity <= 0:
                return jsonify({
                    'success': False,
                    'error': '商品信息不完整'
                }), 400
            
            # 检查商品是否存在
            product = Product.query.get(product_id)
            if not product:
                return jsonify({
                    'success': False,
                    'error': f'商品不存在: {product_id}'
                }), 400
            
            # 检查库存是否充足
            if product.current_stock < quantity:
                return jsonify({
                    'success': False,
                    'error': f'商品库存不足: {product.product_name} (当前库存: {product.current_stock}, 需要: {quantity})'
                }), 400
            
            # 如果没有提供单价，使用商品的零售价格
            if 'unit_price' not in item_data:
                item_data['unit_price'] = product.retail_price
            
            # 记录成本价
            item_data['cost_price'] = product.purchase_ref_price or 0.0
        
        # 计算订单金额
        total_amount = calculate_order_amount(items_data)
        
        # 处理积分抵扣（100积分=1元）
        points_discount = 0.0
        if points_used > 0:
            # 验证积分是否足够
            if customer.points < points_used:
                return jsonify({
                    'success': False,
                    'error': f'积分不足: 当前积分 {customer.points}, 需要 {points_used}'
                }), 400
            
            # 计算抵扣金额（最多抵扣订单金额的90%）
            points_discount = min(points_used / 100.0, total_amount * 0.9)
        
        # 计算最终金额
        final_amount = max(0.0, total_amount - discount_amount - points_discount)
        
        # 生成订单号
        order_id = generate_order_id()
        
        # 创建订单
        order = SalesOrder(
            order_id=order_id,
            customer_id=customer_id,
            order_time=datetime.now(),
            total_amount=total_amount,
            discount_amount=discount_amount,
            final_amount=final_amount,
            payment_method=payment_method,
            payment_status=0,  # 未付款
            shipping_address=shipping_address,
            is_cancelled=0,
            is_returned=0,
            delivery_status=0,
            points_used=points_used,
            points_discount=points_discount,
            points_earned=0  # 支付完成后计算
        )
        
        db.session.add(order)
        
        # 创建订单明细
        for item_data in items_data:
            order_item = SalesOrderItem(
                order_id=order_id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                cost_price=item_data.get('cost_price', 0.0)
            )
            db.session.add(order_item)
        
        # 如果使用了积分，先扣除积分（支付失败时回滚）
        if points_used > 0:
            customer.points -= points_used
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'order_id': order_id,
                'order': order.to_dict(),
                'customer_points': customer.points
            },
            'message': '订单创建成功'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sales_bp.route('/orders/<order_id>/pay', methods=['POST'])
def pay_order(order_id):
    """支付订单：扣减库存，记录财务收入，计算积分"""
    try:
        data = request.get_json() or {}
        operator = data.get('operator', 'system')
        
        # 查询订单
        order = SalesOrder.query.filter_by(order_id=order_id).first()
        
        if not order:
            return jsonify({
                'success': False,
                'error': '订单不存在'
            }), 404
        
        if order.payment_status == 1:
            return jsonify({
                'success': False,
                'error': '订单已支付'
            }), 400
        
        if order.is_cancelled == 1:
            return jsonify({
                'success': False,
                'error': '订单已取消'
            }), 400
        
        # 查询客户
        customer = Customer.query.get(order.customer_id)
        
        # 使用事务确保原子性
        with db.session.begin_nested():
            # 更新订单支付状态
            order.payment_status = 1
            
            # 扣减库存并记录库存日志
            for item in order.items:
                product = Product.query.get(item.product_id)
                
                if not product:
                    raise ValueError(f'商品不存在: {item.product_id}')
                
                if product.current_stock < item.quantity:
                    raise ValueError(f'商品库存不足: {product.product_name}')
                
                # 记录库存变动前数量
                before_quantity = product.current_stock
                
                # 扣减库存
                product.current_stock -= item.quantity
                
                # 记录库存日志
                inventory_log = InventoryLog(
                    product_id=item.product_id,
                    relate_order_id=order_id,
                    change_type='销售出库',
                    change_qty=-item.quantity,
                    before_quantity=before_quantity,
                    after_quantity=product.current_stock,
                    operator=operator,
                    remark=f'订单{order_id}销售出库'
                )
                db.session.add(inventory_log)
            
            # 记录财务收入
            financial_record = FinancialRecord(
                type=1,  # 收入
                amount=order.final_amount,
                relate_order_id=order_id,
                occur_time=datetime.now(),
                remark=f'订单{order_id}销售收入'
            )
            db.session.add(financial_record)
            
            # 计算积分（积分 = 实付金额，1元 = 1积分）
            points_earned = int(order.final_amount)
            order.points_earned = points_earned
            
            # 更新客户积分
            if customer:
                customer.points += points_earned
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'order': order.to_dict(),
                'customer_points': customer.points if customer else 0,
                'points_earned': points_earned
            },
            'message': f'支付成功，库存已扣减，获得 {points_earned} 积分'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sales_bp.route('/orders/<order_id>/return', methods=['POST'])
def return_order(order_id):
    """退货（整单或部分退货）"""
    try:
        data = request.get_json()
        return_items = data.get('items', [])
        operator = data.get('operator', 'system')
        remark = data.get('remark', '')
        
        # 查询订单
        order = SalesOrder.query.filter_by(order_id=order_id).first()
        
        if not order:
            return jsonify({
                'success': False,
                'error': '订单不存在'
            }), 404
        
        if order.payment_status == 0:
            return jsonify({
                'success': False,
                'error': '订单未支付，不能退货'
            }), 400
        
        if order.is_returned == 1:
            return jsonify({
                'success': False,
                'error': '订单已退货'
            }), 400
        
        # 验证退货商品
        if not return_items or len(return_items) == 0:
            # 如果没有指定退货项目，默认整单退货
            return_items = [{'product_id': item.product_id, 'quantity': item.quantity} for item in order.items]
        
        # 验证退货数量
        total_return_amount = 0.0
        return_map = {}
        
        for return_item in return_items:
            product_id = return_item['product_id']
            return_qty = return_item['quantity']
            
            # 查找订单项
            order_item = next((item for item in order.items if item.product_id == product_id), None)
            if not order_item:
                return jsonify({
                    'success': False,
                    'error': f'商品不在订单中: {product_id}'
                }), 400
            
            if return_qty > order_item.quantity:
                return jsonify({
                    'success': False,
                    'error': f'退货数量超过订单数量: {order_item.product.product_name}'
                }), 400
            
            # 计算退货金额
            return_amount = order_item.unit_price * return_qty
            total_return_amount += return_amount
            
            return_map[product_id] = {
                'item': order_item,
                'quantity': return_qty
            }
        
        # 使用事务确保原子性
        with db.session.begin_nested():
            # 更新订单状态
            order.is_returned = 1
            
            # 增加库存并记录库存日志
            for product_id, return_data in return_map.items():
                order_item = return_data['item']
                return_qty = return_data['quantity']
                
                product = Product.query.get(product_id)
                if not product:
                    raise ValueError(f'商品不存在: {product_id}')
                
                # 记录库存变动前数量
                before_quantity = product.current_stock
                
                # 增加库存
                product.current_stock += return_qty
                
                # 记录库存日志
                inventory_log = InventoryLog(
                    product_id=product_id,
                    relate_order_id=order_id,
                    change_type='退货入库',
                    change_qty=return_qty,
                    before_quantity=before_quantity,
                    after_quantity=product.current_stock,
                    operator=operator,
                    remark=f'订单{order_id}退货入库{remark}'
                )
                db.session.add(inventory_log)
            
            # 记录财务退货（type=4 退款）
            financial_record = FinancialRecord(
                type=4,  # 退款
                amount=total_return_amount,
                relate_order_id=order_id,
                occur_time=datetime.now(),
                remark=f'订单{order_id}退款{remark}'
            )
            db.session.add(financial_record)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'order_id': order_id,
                'return_amount': total_return_amount,
                'return_items': [{'product_id': p, 'quantity': d['quantity']} for p, d in return_map.items()]
            },
            'message': '退货成功，库存已增加'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sales_bp.route('/orders/<order_id>/deliver', methods=['POST'])
def deliver_order(order_id):
    """标记订单已交付"""
    try:
        data = request.get_json() or {}
        operator = data.get('operator', 'system')
        remark = data.get('remark', '')
        
        # 查询订单
        order = SalesOrder.query.filter_by(order_id=order_id).first()
        
        if not order:
            return jsonify({
                'success': False,
                'error': '订单不存在'
            }), 404
        
        if order.delivery_status == 1:
            return jsonify({
                'success': False,
                'error': '订单已交付'
            }), 400
        
        # 更新交付状态
        order.delivery_status = 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': order.to_dict(),
            'message': '订单已标记为交付'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
