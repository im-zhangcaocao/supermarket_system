"""
库存管理 API 路由
"""
from flask import Blueprint, request, jsonify
from models import db, Product, InventoryLog
from datetime import datetime

stock_bp = Blueprint('stock', __name__, url_prefix='/api/stock')


@stock_bp.route('/<int:product_id>', methods=['GET'])
def get_stock(product_id):
    """查询当前库存"""
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({
                'success': False,
                'error': '产品不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'product_id': product.product_id,
                'product_name': product.product_name,
                'current_stock': product.current_stock,
                'threshold': product.threshold,
                'is_low_stock': product.current_stock <= product.threshold
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@stock_bp.route('/deduct', methods=['POST'])
def deduct_stock():
    """扣减库存"""
    try:
        data = request.get_json()
        
        # 验证必需参数
        required_fields = ['product_id', 'quantity', 'relate_order_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必需参数: {field}'
                }), 400
        
        product_id = int(data['product_id'])
        quantity = int(data['quantity'])
        relate_order_id = data['relate_order_id']
        operator = data.get('operator', 'system')
        remark = data.get('remark', '库存扣减')
        
        # 获取产品
        product = Product.query.get(product_id)
        if not product:
            return jsonify({
                'success': False,
                'error': '产品不存在'
            }), 404
        
        # 检查库存是否足够
        if product.current_stock < quantity:
            return jsonify({
                'success': False,
                'error': f'库存不足，当前库存: {product.current_stock}，需要扣减: {quantity}'
            }), 400
        
        # 扣减库存
        before_quantity = product.current_stock
        product.current_stock -= quantity
        after_quantity = product.current_stock
        
        # 记录库存日志
        log = InventoryLog(
            product_id=product_id,
            relate_order_id=relate_order_id,
            change_type='销售出库',
            change_qty=-quantity,
            before_quantity=before_quantity,
            after_quantity=after_quantity,
            operator=operator,
            operate_time=datetime.now(),
            remark=remark
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '库存扣减成功',
            'data': {
                'product_id': product_id,
                'product_name': product.product_name,
                'before_quantity': before_quantity,
                'after_quantity': after_quantity,
                'change_qty': -quantity
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@stock_bp.route('/add', methods=['POST'])
def add_stock():
    """增加库存"""
    try:
        data = request.get_json()
        
        # 验证必需参数
        required_fields = ['product_id', 'quantity', 'reason']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必需参数: {field}'
                }), 400
        
        product_id = int(data['product_id'])
        quantity = int(data['quantity'])
        reason = data['reason']
        operator = data.get('operator_id', 'system')
        relate_order_id = data.get('relate_order_id')
        remark = data.get('remark', '库存增加')
        
        # 获取产品
        product = Product.query.get(product_id)
        if not product:
            return jsonify({
                'success': False,
                'error': '产品不存在'
            }), 404
        
        # 增加库存
        before_quantity = product.current_stock
        product.current_stock += quantity
        after_quantity = product.current_stock
        
        # 记录库存日志
        log = InventoryLog(
            product_id=product_id,
            relate_order_id=relate_order_id,
            change_type=reason,
            change_qty=quantity,
            before_quantity=before_quantity,
            after_quantity=after_quantity,
            operator=operator,
            operate_time=datetime.now(),
            remark=remark
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '库存增加成功',
            'data': {
                'product_id': product_id,
                'product_name': product.product_name,
                'before_quantity': before_quantity,
                'after_quantity': after_quantity,
                'change_qty': quantity
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@stock_bp.route('/alerts', methods=['GET'])
def get_stock_alerts():
    """获取低库存预警列表"""
    try:
        # 查询所有低于阈值的商品
        low_stock_products = Product.query.filter(
            Product.current_stock <= Product.threshold,
            Product.status == 1
        ).order_by(Product.current_stock.asc()).all()
        
        alerts = []
        for product in low_stock_products:
            alerts.append({
                'product_id': product.product_id,
                'product_name': product.product_name,
                'brand': product.brand,
                'category': product.category,
                'current_stock': product.current_stock,
                'threshold': product.threshold,
                'shortage': product.threshold - product.current_stock
            })
        
        return jsonify({
            'success': True,
            'data': alerts,
            'total': len(alerts)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@stock_bp.route('/logs', methods=['GET'])
def get_stock_logs():
    """获取库存流水（支持筛选和分页）"""
    try:
        # 获取查询参数
        product_id = request.args.get('product_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        change_type = request.args.get('change_type')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 构建查询
        query = InventoryLog.query
        
        if product_id:
            query = query.filter(InventoryLog.product_id == product_id)
        
        if start_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(InventoryLog.operate_time >= start_datetime)
        
        if end_date:
            end_datetime = datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
            query = query.filter(InventoryLog.operate_time <= end_datetime)
        
        if change_type:
            query = query.filter(InventoryLog.change_type == change_type)
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        logs = query.order_by(InventoryLog.operate_time.desc()).offset(offset).limit(page_size).all()
        
        return jsonify({
            'success': True,
            'data': [log.to_dict() for log in logs],
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@stock_bp.route('/change-types', methods=['GET'])
def get_change_types():
    """获取所有库存变动类型"""
    change_types = [
        {'value': '销售出库', 'label': '销售出库', 'icon': 'trending-down', 'color': 'danger'},
        {'value': '采购入库', 'label': '采购入库', 'icon': 'trending-up', 'color': 'success'},
        {'value': '退货入库', 'label': '退货入库', 'icon': 'refresh-cw', 'color': 'warning'},
        {'value': '损耗', 'label': '损耗', 'icon': 'alert-circle', 'color': 'danger'},
        {'value': '调拨入库', 'label': '调拨入库', 'icon': 'arrow-down-left', 'color': 'primary'},
        {'value': '调拨出库', 'label': '调拨出库', 'icon': 'arrow-up-right', 'color': 'info'},
        {'value': '盘点调整', 'label': '盘点调整', 'icon': 'clipboard-list', 'color': 'success'}
    ]
    
    return jsonify({
        'success': True,
        'data': change_types
    })


@stock_bp.route('/adjust', methods=['POST'])
def adjust_stock():
    """手动调整库存"""
    try:
        data = request.get_json()
        
        # 验证必需参数
        required_fields = ['product_id', 'delta', 'reason', 'operator_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必需参数: {field}'
                }), 400
        
        product_id = int(data['product_id'])
        delta = int(data['delta'])  # 正数增加，负数减少
        reason = data['reason']
        operator = data['operator_id']
        remark = data.get('remark', '手动调整')
        
        # 获取产品
        product = Product.query.get(product_id)
        if not product:
            return jsonify({
                'success': False,
                'error': '产品不存在'
            }), 404
        
        # 检查调整后库存是否合法
        if product.current_stock + delta < 0:
            return jsonify({
                'success': False,
                'error': f'调整后库存不能为负数，当前库存: {product.current_stock}，调整量: {delta}'
            }), 400
        
        # 调整库存
        before_quantity = product.current_stock
        product.current_stock += delta
        after_quantity = product.current_stock
        
        # 记录库存日志
        log = InventoryLog(
            product_id=product_id,
            relate_order_id=None,
            change_type=reason,
            change_qty=delta,
            before_quantity=before_quantity,
            after_quantity=after_quantity,
            operator=operator,
            operate_time=datetime.now(),
            remark=remark
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '库存调整成功',
            'data': {
                'product_id': product_id,
                'product_name': product.product_name,
                'before_quantity': before_quantity,
                'after_quantity': after_quantity,
                'change_qty': delta
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
