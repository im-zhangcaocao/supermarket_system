"""
产品管理 API 路由
"""
from flask import Blueprint, request, jsonify
from models import db, Product, InventoryLog, ProductEditLog, SalesOrderItem, PurchaseOrderItem
from datetime import datetime

products_bp = Blueprint('products', __name__, url_prefix='/api/products')


@products_bp.route('', methods=['GET'])
def get_products():
    """获取所有产品"""
    try:
        # 获取查询参数
        category = request.args.get('category')
        status = request.args.get('status')
        sort_by = request.args.get('sort_by', 'product_id')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 构建查询
        query = Product.query
        
        if category:
            query = query.filter(Product.category == category)
        
        if status is not None:
            query = query.filter(Product.status == int(status))
        
        # 排序处理
        sort_columns = {
            'product_id': Product.product_id,
            'product_name': Product.product_name,
            'category': Product.category,
            'current_stock': Product.current_stock,
            'retail_price': Product.retail_price
        }
        
        if sort_by in sort_columns:
            if sort_order == 'asc':
                query = query.order_by(sort_columns[sort_by].asc())
            else:
                query = query.order_by(sort_columns[sort_by].desc())
        else:
            query = query.order_by(Product.product_id.desc())
        
        products = query.all()
        
        product_data = [product.to_dict() for product in products]
        
        return jsonify({
            'success': True,
            'data': product_data,
            'total': len(product_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """获取单个产品"""
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({
                'success': False,
                'error': '产品不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': product.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@products_bp.route('', methods=['POST'])
def create_product():
    """添加产品"""
    try:
        data = request.get_json()
        
        # 基本验证
        required_fields = ['product_name', 'retail_price']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必需字段: {field}'
                }), 400
        
        # 创建产品
        product = Product(
            product_name=data['product_name'],
            brand=data.get('brand'),
            model=data.get('model'),
            category=data.get('category'),
            retail_price=float(data['retail_price']),
            purchase_ref_price=float(data.get('purchase_ref_price', 0)),
            current_stock=int(data.get('current_stock', 0)),
            threshold=int(data.get('threshold', 10)),
            status=int(data.get('status', 1)),
            unit=data.get('unit', '台'),
            warehouse=data.get('warehouse'),
            shelf_no=data.get('shelf_no')
        )
        
        db.session.add(product)
        db.session.flush()
        
        # 记录操作日志
        operator = data.get('operator', 'system')
        log = ProductEditLog(
            product_id=product.product_id,
            edit_type='create',
            new_value=str(data),
            operator=operator,
            remark='创建产品'
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': product.to_dict(),
            'message': '产品添加成功'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@products_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """更新产品"""
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({
                'success': False,
                'error': '产品不存在'
            }), 404
        
        data = request.get_json()
        operator = data.pop('operator', 'system')
        
        # 记录修改前的值
        old_values = {}
        
        # 更新字段（数值类型）
        for field in ['retail_price', 'purchase_ref_price', 'threshold', 'status', 'current_stock']:
            if field in data:
                old_values[field] = getattr(product, field)
                if field in ['retail_price', 'purchase_ref_price']:
                    setattr(product, field, float(data[field]))
                else:
                    setattr(product, field, int(data[field]))
        
        # 更新字段（字符串类型）
        for field in ['product_name', 'brand', 'model', 'category', 'unit', 'warehouse', 'shelf_no']:
            if field in data:
                old_values[field] = getattr(product, field)
                setattr(product, field, data[field])
        
        # 记录操作日志
        log = ProductEditLog(
            product_id=product_id,
            edit_type='update',
            old_value=str(old_values),
            new_value=str(data),
            operator=operator,
            remark='更新产品'
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': product.to_dict(),
            'message': '产品更新成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@products_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """删除产品"""
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({
                'success': False,
                'error': '产品不存在'
            }), 404
        
        # 检查关联订单
        sales_items = SalesOrderItem.query.filter_by(product_id=product_id).count()
        purchase_items = PurchaseOrderItem.query.filter_by(product_id=product_id).count()
        
        if sales_items > 0 or purchase_items > 0:
            return jsonify({
                'success': False,
                'error': f'该产品存在关联订单，无法删除（销售订单项: {sales_items}, 采购订单项: {purchase_items}）'
            }), 400
        
        # 记录删除日志
        log = ProductEditLog(
            product_id=product_id,
            edit_type='delete',
            old_value=str(product.to_dict()),
            operator=request.get_json().get('operator', 'system') if request.get_json() else 'system',
            remark='删除产品'
        )
        db.session.add(log)
        
        # 删除产品
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '产品删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@products_bp.route('/<int:product_id>/disable', methods=['PATCH'])
def disable_product(product_id):
    """禁用产品"""
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({
                'success': False,
                'error': '产品不存在'
            }), 404
        
        product.status = 0
        
        # 记录日志
        log = ProductEditLog(
            product_id=product_id,
            edit_type='update',
            edit_field='status',
            old_value='1',
            new_value='0',
            operator=request.get_json().get('operator', 'system') if request.get_json() else 'system',
            remark='禁用产品'
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': product.to_dict(),
            'message': '产品已禁用'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@products_bp.route('/<int:product_id>/threshold', methods=['PATCH'])
def set_threshold(product_id):
    """设置预警阈值"""
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({
                'success': False,
                'error': '产品不存在'
            }), 404
        
        data = request.get_json()
        
        if 'threshold' not in data:
            return jsonify({
                'success': False,
                'error': '缺少阈值参数'
            }), 400
        
        old_threshold = product.threshold
        new_threshold = int(data['threshold'])
        
        product.threshold = new_threshold
        
        # 记录日志
        log = ProductEditLog(
            product_id=product_id,
            edit_type='update',
            edit_field='threshold',
            old_value=str(old_threshold),
            new_value=str(new_threshold),
            operator=data.get('operator', 'system'),
            remark='设置预警阈值'
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': product.to_dict(),
            'message': f'预警阈值已更新为 {new_threshold}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@products_bp.route('/<int:product_id>/logs', methods=['GET'])
def get_product_edit_logs(product_id):
    """获取产品修改记录"""
    try:
        # 查询该产品的所有修改记录，按时间倒序
        logs = ProductEditLog.query.filter_by(product_id=product_id)\
                                   .order_by(ProductEditLog.operate_time.desc())\
                                   .all()
        
        result = []
        for log in logs:
            log_data = log.to_dict()
            
            # 解析修改字段和值
            if log.edit_field:
                # 如果有明确的修改字段，直接使用
                log_data['field_name'] = log.edit_field
                log_data['field_label'] = get_field_display_name(log.edit_field)
            elif log.edit_type == 'create':
                # 创建记录
                log_data['field_name'] = 'create'
                log_data['field_label'] = '创建产品'
                log_data['old_value'] = '-'
                log_data['new_value'] = '产品已创建'
            elif log.edit_type == 'delete':
                # 删除记录
                log_data['field_name'] = 'delete'
                log_data['field_label'] = '删除产品'
                log_data['new_value'] = '-'
            elif log.edit_type == 'update' and log.old_value and log.new_value:
                # 尝试解析更新记录中的字段变化
                try:
                    old_values = eval(log.old_value) if log.old_value else {}
                    new_values = eval(log.new_value) if log.new_value else {}
                    
                    # 找出所有变化的字段
                    for field, new_val in new_values.items():
                        old_val = old_values.get(field, '-')
                        if str(old_val) != str(new_val):
                            field_log = log_data.copy()
                            field_log['field_name'] = field
                            field_log['field_label'] = get_field_display_name(field)
                            field_log['old_value'] = str(old_val) if old_val != '-' else '-'
                            field_log['new_value'] = str(new_val)
                            result.append(field_log)
                    continue
                except:
                    # 如果解析失败，使用原始数据
                    log_data['field_name'] = 'unknown'
                    log_data['field_label'] = '未知字段'
            
            result.append(log_data)
        
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


def get_field_display_name(field_name):
    """获取字段显示名称"""
    field_map = {
        'product_name': '产品名称',
        'brand': '品牌',
        'model': '型号',
        'category': '类别',
        'retail_price': '零售价',
        'purchase_ref_price': '采购参考价',
        'current_stock': '当前库存',
        'threshold': '预警阈值',
        'unit': '销售单位',
        'warehouse': '仓库',
        'shelf_no': '货位',
        'status': '状态',
        'create': '创建',
        'delete': '删除'
    }
    return field_map.get(field_name, field_name)
