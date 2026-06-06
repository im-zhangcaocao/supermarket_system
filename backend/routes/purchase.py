"""
采购订单管理 API 路由
"""
from flask import Blueprint, request, jsonify
from models import db, PurchaseOrder, PurchaseOrderItem, PurchaseReceipt, PurchaseReceiptItem, Supplier, Product, InventoryLog, FinancialRecord, ReplenishmentAdvice
from datetime import datetime, date
from sqlalchemy import func

purchase_bp = Blueprint('purchase', __name__, url_prefix='/api/purchase')


def generate_purchase_order_id():
    """生成采购订单号：PO + yyyymmdd + 4位流水号（每天从0001开始）"""
    today_str = date.today().strftime('%Y%m%d')
    today_prefix = f'PO{today_str}'
    
    # 查询今天最大的订单号
    today_orders = PurchaseOrder.query.filter(PurchaseOrder.purchase_order_id.like(f'{today_prefix}%')).all()
    
    if not today_orders:
        sequence = 1
    else:
        # 提取流水号并找出最大值
        max_seq = 0
        for order in today_orders:
            seq_str = order.purchase_order_id[-4:]
            if seq_str.isdigit():
                seq = int(seq_str)
                if seq > max_seq:
                    max_seq = seq
        sequence = max_seq + 1
    
    # 格式化为4位数字
    order_id = f'{today_prefix}{sequence:04d}'
    return order_id


def calculate_order_amount(items):
    """计算采购订单总金额"""
    total_amount = 0.0
    for item in items:
        total_amount += item['unit_price'] * item['quantity']
    return total_amount


def convert_status(status):
    """将字符串状态转换为数字状态（兼容旧数据）"""
    status_map = {
        'pending': 0,
        'partial': 1,
        'completed': 2,
        0: 0,
        1: 1,
        2: 2
    }
    return status_map.get(status, 0)


def get_status_text(status):
    """获取状态文本"""
    text_map = {
        0: '待交付',
        1: '部分交付',
        2: '已完成',
        'pending': '待交付',
        'partial': '部分交付',
        'completed': '已完成'
    }
    return text_map.get(status, '未知')


@purchase_bp.route('/orders', methods=['GET'])
def get_purchase_orders():
    """获取采购订单列表"""
    try:
        # 获取查询参数
        supplier_id = request.args.get('supplier_id', type=int)
        status = request.args.get('status', type=int)
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        
        # 构建查询
        query = PurchaseOrder.query
        
        if supplier_id:
            query = query.filter(PurchaseOrder.supplier_id == supplier_id)
        
        if status is not None:
            # 兼容数字和字符串状态
            query = query.filter(PurchaseOrder.status.in_([status, str(status)]))
        
        # 按订单时间倒序排列
        total = query.count()
        orders = query.order_by(PurchaseOrder.order_time.desc())\
                      .offset((page - 1) * page_size)\
                      .limit(page_size)\
                      .all()
        
        # 转换状态格式并计算汇总数据
        result = []
        for order in orders:
            order_data = order.to_dict()
            
            # 计算采购数量和已收数量
            total_expected_qty = 0
            total_received_qty = 0
            for item in order.items:
                total_expected_qty += item.quantity
                total_received_qty += item.received_quantity
            
            # 获取状态文本
            order_status = convert_status(order.status)
            order_data['status'] = order_status
            order_data['status_text'] = get_status_text(order_status)
            
            # 添加汇总字段
            order_data['create_time'] = order_data['order_time']  # 兼容前端字段名
            order_data['actual_delivery_date'] = order_data['received_time']  # 实际交付日期
            order_data['total_expected_qty'] = total_expected_qty
            order_data['total_received_qty'] = total_received_qty
            
            # 添加订单明细（用于确认收货弹窗）
            order_data['items'] = []
            for item in order.items:
                item_data = item.to_dict()
                item_data['subtotal'] = item.quantity * item.unit_price
                order_data['items'].append(item_data)
            
            result.append(order_data)
        
        return jsonify({
            'success': True,
            'data': result,
            'total': total,
            'page': page,
            'page_size': page_size
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@purchase_bp.route('/orders/<order_id>', methods=['GET'])
def get_purchase_order(order_id):
    """获取采购订单详情"""
    try:
        order = PurchaseOrder.query.filter_by(purchase_order_id=order_id).first()
        
        if not order:
            return jsonify({
                'success': False,
                'error': '采购订单不存在'
            }), 404
        
        # 包含订单明细
        order_data = order.to_dict()
        order_data['status_text'] = get_status_text(order.status)
        order_data['items'] = []
        
        for item in order.items:
            item_data = item.to_dict()
            # 计算小计
            item_data['subtotal'] = item.quantity * item.unit_price
            order_data['items'].append(item_data)
        
        return jsonify({
            'success': True,
            'data': order_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@purchase_bp.route('/orders', methods=['POST'])
def create_purchase_order():
    """创建采购订单"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['supplier_id', 'items', 'expected_date']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必需字段: {field}'
                }), 400
        
        supplier_id = data['supplier_id']
        items_data = data['items']
        expected_date_str = data['expected_date']
        remark = data.get('remark', '')
        
        # 验证供应商是否存在
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return jsonify({
                'success': False,
                'error': '供应商不存在'
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
            unit_price = item_data.get('unit_price')
            
            if not product_id or quantity <= 0 or unit_price is None:
                return jsonify({
                    'success': False,
                    'error': '商品信息不完整'
                }), 400
        
        # 解析预期日期
        try:
            expected_date = datetime.strptime(expected_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': '预期日期格式错误，应为YYYY-MM-DD'
            }), 400
        
        # 生成订单号
        order_id = generate_purchase_order_id()
        
        # 计算订单金额
        total_amount = calculate_order_amount(items_data)
        
        # 创建订单
        order = PurchaseOrder(
            purchase_order_id=order_id,
            supplier_id=supplier_id,
            order_time=datetime.now(),
            expected_date=expected_date,
            status='pending',  # 待交付
            total_amount=total_amount,
            remark=remark
        )
        
        db.session.add(order)
        
        # 创建订单明细
        for item_data in items_data:
            order_item = PurchaseOrderItem(
                purchase_order_id=order_id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                received_quantity=0,
                unit_price=item_data['unit_price']
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'purchase_order_id': order_id,
                'order': order.to_dict()
            },
            'message': '采购订单创建成功'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@purchase_bp.route('/orders/<order_id>/receipt', methods=['POST'])
def receipt_order(order_id):
    """确认收货"""
    try:
        data = request.get_json()
        receipt_items = data.get('items', [])
        operator = data.get('operator', 'system')
        remark = data.get('remark', '')
        
        # 查询订单
        order = PurchaseOrder.query.filter_by(purchase_order_id=order_id).first()
        
        if not order:
            return jsonify({
                'success': False,
                'error': '采购订单不存在'
            }), 404
        
        # 检查订单状态（不能重复收货）
        if order.status == 'completed' or order.status == 2:
            return jsonify({
                'success': False,
                'error': '订单已完成，不能重复确认收货'
            }), 400
        
        # 验证收货商品
        if not receipt_items or len(receipt_items) == 0:
            return jsonify({
                'success': False,
                'error': '请指定收货商品'
            }), 400
        
        # 分离合格和不合格商品
        qualified_items = []  # 合格商品
        unqualified_items = []  # 不合格商品
        
        for receipt_item in receipt_items:
            quality_status = receipt_item.get('quality_status', '合格')
            if quality_status == '合格':
                qualified_items.append(receipt_item)
            else:
                unqualified_items.append(receipt_item)
        
        # 检查是否全部不合格
        all_unqualified = len(qualified_items) == 0
        
        # 验证并汇总合格商品的收货信息
        receipt_map = {}
        total_receive_amount = 0.0
        inventory_changes = []
        unqualified_amount = 0.0  # 不合格商品金额（需要退货）
        
        for receipt_item in qualified_items:
            product_id = receipt_item['product_id']
            received_quantity = receipt_item.get('received_quantity', 0)
            
            # 查找订单项
            order_item = next((item for item in order.items if item.product_id == product_id), None)
            
            if not order_item:
                return jsonify({
                    'success': False,
                    'error': f'商品不在采购订单中: {product_id}'
                }), 400
            
            # 检查是否已全部收货
            remaining = order_item.quantity - order_item.received_quantity
            if received_quantity > remaining:
                return jsonify({
                    'success': False,
                    'error': f'实收数量超过剩余数量: {order_item.product.product_name}'
                }), 400
            
            # 计算本次收货金额
            receive_amount = received_quantity * order_item.unit_price
            total_receive_amount += receive_amount
            
            receipt_map[product_id] = {
                'order_item': order_item,
                'received_quantity': received_quantity,
                'receive_amount': receive_amount,
                'quality_status': '合格'
            }
            
            # 检查商品是否存在
            product = Product.query.get(product_id)
            inventory_changes.append({
                'product_id': product_id,
                'product': product,
                'quantity': received_quantity,
                'unit_price': order_item.unit_price
            })
        
        # 计算不合格商品金额
        for receipt_item in unqualified_items:
            product_id = receipt_item['product_id']
            received_quantity = receipt_item.get('received_quantity', 0)
            
            order_item = next((item for item in order.items if item.product_id == product_id), None)
            if order_item:
                unqualified_amount += received_quantity * order_item.unit_price
                
                receipt_map[product_id] = {
                    'order_item': order_item,
                    'received_quantity': received_quantity,
                    'receive_amount': 0,  # 不合格商品不计入收货金额
                    'quality_status': '不合格'
                }
        
        # 使用事务确保原子性
        with db.session.begin_nested():
            # 处理库存变动（仅合格商品）
            for change in inventory_changes:
                product_id = change['product_id']
                quantity = change['quantity']
                unit_price = change['unit_price']
                product = change['product']
                
                if product:
                    # 商品存在，增加库存
                    before_quantity = product.current_stock
                    product.current_stock += quantity
                    after_quantity = product.current_stock
                else:
                    # 商品不存在，创建新商品
                    product = Product(
                        product_id=product_id,
                        product_name=f'新产品_{product_id}',
                        brand='未知',
                        model='未知',
                        category='其他',
                        retail_price=unit_price * 1.3,  # 零售价格=采购价*1.3
                        purchase_ref_price=unit_price,
                        current_stock=quantity,
                        threshold=10,
                        status=1
                    )
                    db.session.add(product)
                    db.session.flush()
                    before_quantity = 0
                    after_quantity = quantity
                
                # 记录库存日志
                inventory_log = InventoryLog(
                    product_id=product_id,
                    relate_order_id=order_id,
                    change_type='采购入库',
                    change_qty=quantity,
                    before_quantity=before_quantity,
                    after_quantity=after_quantity,
                    operator=operator,
                    remark=f'采购订单{order_id}入库{remark}'
                )
                db.session.add(inventory_log)
            
            # 更新订单项收货数量（仅合格商品）
            for product_id, receipt_data in receipt_map.items():
                if receipt_data['quality_status'] == '合格':
                    order_item = receipt_data['order_item']
                    received_quantity = receipt_data['received_quantity']
                    order_item.received_quantity += received_quantity
            
            # 创建收货记录
            receipt_id = generate_receipt_id()
            receipt = PurchaseReceipt(
                receipt_id=receipt_id,
                purchase_order_id=order_id,
                receipt_time=datetime.now(),
                operator=operator,
                remark=remark,
                status='completed'
            )
            db.session.add(receipt)
            db.session.flush()  # 获取receipt_id
            
            # 创建收货明细
            for product_id, receipt_data in receipt_map.items():
                order_item = receipt_data['order_item']
                received_quantity = receipt_data['received_quantity']
                
                # 查找对应的质检状态
                quality_status = '合格'
                for item in receipt_items:
                    if item.get('product_id') == product_id:
                        quality_status = item.get('quality_status', '合格')
                        break
                
                receipt_item = PurchaseReceiptItem(
                    receipt_id=receipt_id,
                    product_id=product_id,
                    product_name=order_item.product.product_name if order_item.product else f'产品{product_id}',
                    quantity=received_quantity,
                    unit_price=order_item.unit_price,
                    quality_status=quality_status
                )
                db.session.add(receipt_item)
            
            # 记录财务支出（类型type=2）- 仅合格商品
            if total_receive_amount > 0:
                financial_record = FinancialRecord(
                    type=2,  # 支出
                    amount=total_receive_amount,
                    relate_order_id=order_id,
                    occur_time=datetime.now(),
                    remark=f'采购订单{order_id}支出（合格商品）{remark}'
                )
                db.session.add(financial_record)
            
            # 如果有不合格商品，记录退款收入（供应商退回货款）
            if unqualified_amount > 0:
                refund_record = FinancialRecord(
                    type=1,  # 收入（退款）
                    amount=unqualified_amount,
                    relate_order_id=order_id,
                    occur_time=datetime.now(),
                    remark=f'采购订单{order_id}退货退款（不合格商品）{remark}'
                )
                db.session.add(refund_record)
            
            # 更新订单状态
            # 如果全部不合格，直接标记为已完成（跳过收货，触发退货）
            if all_unqualified:
                order.status = 'completed'  # 已完成
                order.received_time = datetime.now()
            else:
                # 检查是否全部完成
                all_completed = True
                for item in order.items:
                    if item.received_quantity < item.quantity:
                        all_completed = False
                        break
                
                if all_completed:
                    order.status = 'completed'  # 已完成
                    order.received_time = datetime.now()
                else:
                    order.status = 'partial'  # 部分交付
        
        db.session.commit()
        
        # 准备返回数据
        updated_order = PurchaseOrder.query.filter_by(purchase_order_id=order_id).first()
        order_data = updated_order.to_dict()
        order_data['status_text'] = get_status_text(updated_order.status)
        order_data['items'] = []
        
        for item in updated_order.items:
            item_data = item.to_dict()
            item_data['subtotal'] = item.quantity * item.unit_price
            order_data['items'].append(item_data)
        
        return jsonify({
            'success': True,
            'data': {
                'order': order_data,
                'received_amount': total_receive_amount,
                'unqualified_amount': unqualified_amount,
                'unqualified_count': len(unqualified_items),
                'qualified_count': len(qualified_items),
                'inventory_changes': [
                    {'product_id': c['product_id'], 'quantity': c['quantity']}
                    for c in inventory_changes
                ],
                'all_unqualified': all_unqualified
            },
            'message': '全部商品质检不合格，已自动触发退货流程，订单已完成' if all_unqualified else '收货成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@purchase_bp.route('/overdue', methods=['GET'])
def get_overdue_orders():
    """获取超期未完成订单"""
    try:
        today = date.today()
        
        # 查询条件：expected_date < 当前日期 且 status != completed
        query = PurchaseOrder.query.filter(
            PurchaseOrder.expected_date < today,
            PurchaseOrder.status != 'completed',
            PurchaseOrder.status != 2
        )
        
        orders = query.order_by(PurchaseOrder.expected_date.asc()).all()
        
        result = []
        for order in orders:
            order_data = order.to_dict()
            order_data['status_text'] = get_status_text(order.status)
            
            # 计算逾期天数
            days_overdue = (today - order.expected_date).days
            order_data['days_overdue'] = days_overdue
            
            result.append(order_data)
        
        return jsonify({
            'success': True,
            'data': result,
            'total': len(result)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@purchase_bp.route('/orders/<order_id>', methods=['PUT'])
def update_purchase_order(order_id):
    """更新采购订单"""
    try:
        order = PurchaseOrder.query.filter_by(purchase_order_id=order_id).first()
        
        if not order:
            return jsonify({
                'success': False,
                'error': '采购订单不存在'
            }), 404
        
        # 检查订单状态（已完成的订单不能修改）
        if order.status == 'completed' or order.status == 2:
            return jsonify({
                'success': False,
                'error': '已完成的订单不能修改'
            }), 400
        
        data = request.get_json()
        
        # 更新字段
        if 'supplier_id' in data:
            order.supplier_id = data['supplier_id']
        
        if 'expected_date' in data:
            try:
                order.expected_date = datetime.strptime(data['expected_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': '预期日期格式错误'
                }), 400
        
        if 'remark' in data:
            order.remark = data['remark']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': order.to_dict(),
            'message': '采购订单更新成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@purchase_bp.route('/orders/<order_id>', methods=['DELETE'])
def delete_purchase_order(order_id):
    """删除采购订单"""
    try:
        order = PurchaseOrder.query.filter_by(purchase_order_id=order_id).first()
        
        if not order:
            return jsonify({
                'success': False,
                'error': '采购订单不存在'
            }), 404
        
        # 检查订单状态（已完成的订单不能删除）
        if order.status == 'completed' or order.status == 2:
            return jsonify({
                'success': False,
                'error': '已完成的订单不能删除'
            }), 400
        
        # 检查是否有已收货记录
        for item in order.items:
            if item.received_quantity > 0:
                return jsonify({
                    'success': False,
                    'error': '已有部分收货，无法删除订单'
                }), 400
        
        # 删除订单（级联删除订单项）
        db.session.delete(order)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '采购订单删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@purchase_bp.route('/suppliers/<supplier_id>/orders', methods=['GET'])
def get_supplier_orders(supplier_id):
    """获取供应商的采购订单"""
    try:
        supplier = Supplier.query.get(supplier_id)
        
        if not supplier:
            return jsonify({
                'success': False,
                'error': '供应商不存在'
            }), 404
        
        orders = PurchaseOrder.query.filter_by(supplier_id=supplier_id)\
                                   .order_by(PurchaseOrder.order_time.desc())\
                                   .all()
        
        result = []
        for order in orders:
            order_data = order.to_dict()
            order_data['status_text'] = get_status_text(order.status)
            result.append(order_data)
        
        return jsonify({
            'success': True,
            'data': result,
            'total': len(result)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def generate_advice_id():
    """生成补货建议ID：RA + yyyymmdd + 4位流水号"""
    today_str = date.today().strftime('%Y%m%d')
    today_prefix = f'RA{today_str}'
    
    # 查询今天最大的建议ID
    today_advices = ReplenishmentAdvice.query.filter(ReplenishmentAdvice.advice_id.like(f'{today_prefix}%')).all()
    
    if not today_advices:
        sequence = 1
    else:
        max_seq = 0
        for advice in today_advices:
            seq_str = advice.advice_id[-4:]
            if seq_str.isdigit():
                seq = int(seq_str)
                if seq > max_seq:
                    max_seq = seq
        sequence = max_seq + 1
    
    advice_id = f'{today_prefix}{sequence:04d}'
    return advice_id


@purchase_bp.route('/replenishment-advice/generate', methods=['POST'])
def generate_replenishment_advice():
    """生成采购建议（保存到数据库）"""
    try:
        # 查询库存低于阈值的商品
        low_stock_products = Product.query.filter(
            Product.current_stock <= Product.threshold,
            Product.status == 1
        ).all()
        
        if not low_stock_products:
            return jsonify({
                'success': False,
                'error': '没有需要补货的商品（库存均高于安全库存）'
            }), 400
        
        total_amount = 0.0
        generated_count = 0
        
        # 清除之前的待处理建议（避免重复）
        ReplenishmentAdvice.query.filter(ReplenishmentAdvice.status == 0).delete()
        
        for product in low_stock_products:
            # 计算建议补货数量（建议补充到阈值的2倍）
            suggested_quantity = max(1, product.threshold * 2 - product.current_stock)
            
            # 计算预计金额
            unit_price = product.purchase_ref_price or product.retail_price * 0.7
            estimated_amount = suggested_quantity * unit_price
            total_amount += estimated_amount
            
            # 判断建议原因
            if product.current_stock == 0:
                reason = '库存为零，急需补货'
            elif product.current_stock <= product.threshold * 0.5:
                reason = '库存严重不足'
            else:
                reason = '库存低于安全库存'
            
            # 创建补货建议记录
            advice_id = generate_advice_id()
            advice = ReplenishmentAdvice(
                advice_id=advice_id,
                product_id=product.product_id,
                product_name=product.product_name,
                brand=product.brand,
                category=product.category,
                current_stock=product.current_stock,
                threshold=product.threshold,
                suggested_qty=suggested_quantity,
                daily_sales=5,  # 可以从销售数据计算
                reason=reason,
                estimated_amount=estimated_amount,
                status=0,
                generated_date=datetime.now()
            )
            db.session.add(advice)
            generated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'generated_count': generated_count,
                'total_amount': round(total_amount, 2),
                'message': f'成功生成 {generated_count} 条采购建议'
            },
            'message': f'成功生成 {generated_count} 条采购建议'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@purchase_bp.route('/replenishment-advice', methods=['GET'])
def get_replenishment_advice():
    """获取采购建议列表（从数据库读取）"""
    try:
        # 从数据库读取已生成的采购建议
        advices = ReplenishmentAdvice.query.order_by(ReplenishmentAdvice.generated_date.desc()).all()
        
        advice_list = [advice.to_dict() for advice in advices]
        
        # 计算总金额
        total_amount = sum(advice.estimated_amount for advice in advices)
        pending_count = sum(1 for advice in advices if advice.status == 0)
        
        return jsonify({
            'success': True,
            'data': advice_list,
            'total': len(advice_list),
            'total_amount': round(total_amount, 2),
            'pending_count': pending_count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@purchase_bp.route('/create-from-advice', methods=['POST'])
def create_purchase_from_advice():
    """根据补货建议创建采购订单"""
    try:
        data = request.get_json()
        
        advice_id = data.get('advice_id')
        supplier_id = data.get('supplier_id')
        
        if not supplier_id:
            return jsonify({
                'success': False,
                'error': '供应商ID不能为空'
            }), 400
        
        # 获取低库存商品作为采购项
        low_stock_products = Product.query.filter(
            Product.current_stock <= Product.threshold,
            Product.status == 1
        ).all()
        
        if not low_stock_products:
            return jsonify({
                'success': False,
                'error': '没有需要补货的商品'
            }), 400
        
        # 创建采购订单
        order_id = generate_purchase_order_id()
        today = datetime.now()
        
        new_order = PurchaseOrder(
            purchase_order_id=order_id,
            supplier_id=supplier_id,
            order_time=today,
            expected_date=today.date(),
            status='pending',
            remark='根据补货建议自动生成'
        )
        db.session.add(new_order)
        db.session.flush()
        
        # 添加订单项
        total_amount = 0.0
        for product in low_stock_products:
            suggested_quantity = max(1, product.threshold * 2 - product.current_stock)
            unit_price = product.purchase_ref_price or product.retail_price * 0.8
            
            order_item = PurchaseOrderItem(
                purchase_order_id=order_id,
                product_id=product.product_id,
                quantity=suggested_quantity,
                unit_price=unit_price,
                received_quantity=0
            )
            db.session.add(order_item)
            total_amount += unit_price * suggested_quantity
        
        new_order.total_amount = total_amount
        db.session.commit()
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'message': '采购订单创建成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@purchase_bp.route('/replenishment-advice/<advice_id>', methods=['DELETE'])
def cancel_replenishment_advice(advice_id):
    """取消补货建议（实际上不需要存储，直接返回成功）"""
    try:
        return jsonify({
            'success': True,
            'message': '补货建议已取消'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def generate_receipt_id():
    """生成收货单号：R + yyyymmdd + 4位流水号"""
    today_str = date.today().strftime('%Y%m%d')
    today_prefix = f'R{today_str}'
    
    # 查询今天最大的收货单号
    today_receipts = PurchaseReceipt.query.filter(PurchaseReceipt.receipt_id.like(f'{today_prefix}%')).all()
    
    if not today_receipts:
        sequence = 1
    else:
        max_seq = 0
        for receipt in today_receipts:
            seq_str = receipt.receipt_id[-4:]
            if seq_str.isdigit():
                seq = int(seq_str)
                if seq > max_seq:
                    max_seq = seq
        sequence = max_seq + 1
    
    receipt_id = f'{today_prefix}{sequence:04d}'
    return receipt_id


@purchase_bp.route('/receipts', methods=['GET'])
def get_purchase_receipts():
    """获取收货记录列表"""
    try:
        order_id = request.args.get('order_id')
        
        query = PurchaseReceipt.query
        
        if order_id:
            query = query.filter_by(purchase_order_id=order_id)
        
        receipts = query.order_by(PurchaseReceipt.receipt_time.desc()).all()
        
        result = []
        for receipt in receipts:
            receipt_data = receipt.to_dict()
            # 计算总数量和总金额
            total_qty = 0
            total_amount = 0.0
            for item in receipt.items:
                total_qty += item.quantity
                total_amount += item.quantity * item.unit_price
            receipt_data['total_qty'] = total_qty
            receipt_data['total_amount'] = total_amount
            result.append(receipt_data)
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@purchase_bp.route('/receipts/<receipt_id>', methods=['GET'])
def get_purchase_receipt(receipt_id):
    """获取收货记录详情"""
    try:
        receipt = PurchaseReceipt.query.filter_by(receipt_id=receipt_id).first()
        
        if not receipt:
            return jsonify({
                'success': False,
                'error': '收货记录不存在'
            }), 404
        
        receipt_data = receipt.to_dict()
        
        return jsonify({
            'success': True,
            'data': receipt_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@purchase_bp.route('/receipts/<receipt_id>/items', methods=['GET'])
def get_purchase_receipt_items(receipt_id):
    """获取收货记录明细"""
    try:
        receipt = PurchaseReceipt.query.filter_by(receipt_id=receipt_id).first()
        
        if not receipt:
            return jsonify({
                'success': False,
                'error': '收货记录不存在'
            }), 404
        
        items = []
        for item in receipt.items:
            items.append(item.to_dict())
        
        return jsonify({
            'success': True,
            'data': items
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
