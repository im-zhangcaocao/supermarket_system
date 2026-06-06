"""
报表和仪表盘 API 路由
"""
from flask import Blueprint, request, jsonify
from models import db, SalesOrder, SalesOrderItem, Product, Supplier, PurchaseOrder, \
                   PurchaseOrderItem, InventoryLog, FinancialRecord
from datetime import datetime, date, timedelta
from sqlalchemy import func, extract, case

reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


@reports_bp.route('/sales-trend', methods=['GET'])
def get_sales_trend():
    """
    获取销售趋势
    参数:
        start_date: 起始日期 (YYYY-MM-DD，必填)
        end_date: 结束日期 (YYYY-MM-DD，必填)
        group_by: 分组方式 (可选，默认 'day'，支持 'day'|'week'|'month')
    """
    try:
        # 获取参数
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        group_by = request.args.get('group_by', 'day')
        
        # 验证必填参数
        if not start_date_str or not end_date_str:
            return jsonify({
                'success': False,
                'error': 'start_date 和 end_date 为必填参数',
                'code': 400
            }), 400
        
        # 解析日期
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': '日期格式错误，应为 YYYY-MM-DD',
                'code': 400
            }), 400
        
        if start_date > end_date:
            return jsonify({
                'success': False,
                'error': '起始日期不能大于结束日期',
                'code': 400
            }), 400
        
        # 根据分组方式构建查询
        if group_by == 'month':
            # 按月分组
            sales_data = db.session.query(
                func.strftime('%Y-%m', SalesOrder.order_time).label('period'),
                func.sum(SalesOrder.final_amount).label('total_amount'),
                func.count(SalesOrder.order_id).label('order_count')
            ).filter(
                func.date(SalesOrder.order_time) >= start_date,
                func.date(SalesOrder.order_time) <= end_date,
                SalesOrder.payment_status == 1  # 已支付
            ).group_by('period').order_by('period').all()
            
            # 生成所有月份
            dates = []
            current_date = start_date.replace(day=1)
            while current_date <= end_date:
                dates.append(current_date.strftime('%Y-%m'))
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        
        elif group_by == 'week':
            # 按周分组（周一为一周开始）
            sales_data = db.session.query(
                func.strftime('%Y-%W', SalesOrder.order_time).label('period'),
                func.sum(SalesOrder.final_amount).label('total_amount'),
                func.count(SalesOrder.order_id).label('order_count')
            ).filter(
                func.date(SalesOrder.order_time) >= start_date,
                func.date(SalesOrder.order_time) <= end_date,
                SalesOrder.payment_status == 1
            ).group_by('period').order_by('period').all()
            
            # 生成所有周
            dates = []
            current_date = start_date - timedelta(days=start_date.weekday())
            while current_date <= end_date:
                dates.append(current_date.strftime('%Y-%W'))
                current_date += timedelta(weeks=1)
        
        else:  # day
            # 按天分组
            sales_data = db.session.query(
                func.date(SalesOrder.order_time).label('period'),
                func.sum(SalesOrder.final_amount).label('total_amount'),
                func.count(SalesOrder.order_id).label('order_count')
            ).filter(
                func.date(SalesOrder.order_time) >= start_date,
                func.date(SalesOrder.order_time) <= end_date,
                SalesOrder.payment_status == 1
            ).group_by('period').order_by('period').all()
            
            # 生成所有日期
            dates = []
            current_date = start_date
            while current_date <= end_date:
                dates.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)
        
        # 将查询结果转换为字典
        sales_dict = {str(row[0]): {'amount': float(row[1] or 0), 'count': int(row[2] or 0)} for row in sales_data}
        
        # 填充所有日期的数据（确保连续性）
        amounts = [round(sales_dict.get(d, {}).get('amount', 0), 2) for d in dates]
        counts = [sales_dict.get(d, {}).get('count', 0) for d in dates]
        
        return jsonify({
            'success': True,
            'data': {
                'dates': dates,
                'amounts': amounts,
                'counts': counts,
                'group_by': group_by
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@reports_bp.route('/category-sales', methods=['GET'])
def get_category_sales():
    """
    获取类别销售占比
    返回各品类的销售总额和占比
    """
    try:
        # 查询各品类销售金额
        category_data = db.session.query(
            Product.category,
            func.sum(SalesOrderItem.quantity * SalesOrderItem.unit_price).label('total_amount')
        ).join(SalesOrderItem, Product.product_id == SalesOrderItem.product_id)\
         .join(SalesOrder, SalesOrderItem.order_id == SalesOrder.order_id)\
         .filter(SalesOrder.payment_status == 1)\
         .group_by(Product.category)\
         .order_by(func.sum(SalesOrderItem.quantity * SalesOrderItem.unit_price).desc())\
         .all()
        
        # 计算总销售额
        total_sales = sum(row[1] or 0 for row in category_data)
        
        # 构建结果
        result = []
        for category, amount in category_data:
            amount = float(amount or 0)
            percentage = round((amount / total_sales * 100), 2) if total_sales > 0 else 0
            result.append({
                'category': category or '未分类',
                'total_amount': round(amount, 2),
                'percentage': percentage
            })
        
        return jsonify({
            'success': True,
            'data': result,
            'total_sales': round(total_sales, 2)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@reports_bp.route('/supplier-ranking', methods=['GET'])
def get_supplier_ranking():
    """
    获取供应商采购金额排名
    参数:
        limit: 排名数量 (可选，默认 10)
        start_date: 起始日期 (YYYY-MM-DD，可选)
        end_date: 结束日期 (YYYY-MM-DD，可选)
    """
    try:
        # 获取参数
        limit = request.args.get('limit', 10, type=int)
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # 构建查询
        query = db.session.query(
            Supplier.supplier_name,
            func.sum(PurchaseOrderItem.quantity * PurchaseOrderItem.unit_price).label('total_purchase')
        ).join(PurchaseOrderItem, PurchaseOrder.purchase_order_id == PurchaseOrderItem.purchase_order_id)\
         .join(Supplier, PurchaseOrder.supplier_id == Supplier.supplier_id)\
         .filter(PurchaseOrder.status != 'cancelled')
        
        # 日期筛选
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                query = query.filter(func.date(PurchaseOrder.order_time) >= start_date)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': '日期格式错误',
                    'code': 400
                }), 400
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                query = query.filter(func.date(PurchaseOrder.order_time) <= end_date)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': '日期格式错误',
                    'code': 400
                }), 400
        
        # 执行查询
        supplier_data = query.group_by(Supplier.supplier_name)\
                            .order_by(func.sum(PurchaseOrderItem.quantity * PurchaseOrderItem.unit_price).desc())\
                            .limit(limit)\
                            .all()
        
        # 构建结果
        result = []
        rank = 1
        for supplier_name, amount in supplier_data:
            result.append({
                'rank': rank,
                'supplier': supplier_name,
                'total_purchase': round(float(amount or 0), 2)
            })
            rank += 1
        
        return jsonify({
            'success': True,
            'data': result,
            'limit': limit
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@reports_bp.route('/inventory-trend', methods=['GET'])
def get_inventory_trend():
    """
    获取库存变化趋势
    参数:
        start_date: 起始日期 (YYYY-MM-DD，必填)
        end_date: 结束日期 (YYYY-MM-DD，必填)
    """
    try:
        # 获取参数
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # 验证必填参数
        if not start_date_str or not end_date_str:
            return jsonify({
                'success': False,
                'error': 'start_date 和 end_date 为必填参数',
                'code': 400
            }), 400
        
        # 解析日期
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': '日期格式错误，应为 YYYY-MM-DD',
                'code': 400
            }), 400
        
        if start_date > end_date:
            return jsonify({
                'success': False,
                'error': '起始日期不能大于结束日期',
                'code': 400
            }), 400
        
        # 查询入库数量（change_qty > 0）
        in_stock_data = db.session.query(
            func.date(InventoryLog.operate_time).label('period'),
            func.sum(InventoryLog.change_qty).label('total_in')
        ).filter(
            func.date(InventoryLog.operate_time) >= start_date,
            func.date(InventoryLog.operate_time) <= end_date,
            InventoryLog.change_qty > 0
        ).group_by('period').order_by('period').all()
        
        # 查询出库数量（change_qty < 0，取绝对值）
        out_stock_data = db.session.query(
            func.date(InventoryLog.operate_time).label('period'),
            func.sum(func.abs(InventoryLog.change_qty)).label('total_out')
        ).filter(
            func.date(InventoryLog.operate_time) >= start_date,
            func.date(InventoryLog.operate_time) <= end_date,
            InventoryLog.change_qty < 0
        ).group_by('period').order_by('period').all()
        
        # 生成所有日期
        dates = []
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        
        # 转换为字典
        in_stock_dict = {str(row[0]): int(row[1] or 0) for row in in_stock_data}
        out_stock_dict = {str(row[0]): int(row[1] or 0) for row in out_stock_data}
        
        # 填充所有日期的数据
        in_stock = [in_stock_dict.get(d, 0) for d in dates]
        out_stock = [out_stock_dict.get(d, 0) for d in dates]
        
        return jsonify({
            'success': True,
            'data': {
                'dates': dates,
                'in_stock': in_stock,
                'out_stock': out_stock
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@dashboard_bp.route('/stats', methods=['GET'])
def get_dashboard_stats():
    """
    获取仪表盘统计数据
    返回:
        today_sales: 今日销售总额
        low_stock_count: 库存低于阈值的产品数量
        monthly_purchase_orders: 本月采购订单总数
        monthly_profit: 本月净利润
        update_time: 数据更新时间戳
    """
    try:
        today = date.today()
        month_start = today.replace(day=1)
        
        # 今日销售总额
        today_sales = db.session.query(
            func.sum(SalesOrder.final_amount)
        ).filter(
            func.date(SalesOrder.order_time) == today,
            SalesOrder.payment_status == 1
        ).scalar() or 0
        
        # 库存低于阈值的产品数量
        low_stock_count = db.session.query(
            func.count(Product.product_id)
        ).filter(
            Product.current_stock <= Product.threshold,
            Product.status == 1
        ).scalar() or 0
        
        # 本月采购订单总数
        monthly_purchase_orders = db.session.query(
            func.count(PurchaseOrder.purchase_order_id)
        ).filter(
            func.date(PurchaseOrder.order_time) >= month_start,
            func.date(PurchaseOrder.order_time) <= today
        ).scalar() or 0
        
        # 本月净利润
        # 净利润 = 销售总收入 - 采购总成本 - 其他支出 - 退货退款
        monthly_financial = db.session.query(
            func.sum(case((FinancialRecord.type == 1, FinancialRecord.amount), else_=0)).label('sales'),
            func.sum(case((FinancialRecord.type == 2, FinancialRecord.amount), else_=0)).label('purchase'),
            func.sum(case((FinancialRecord.type == 3, FinancialRecord.amount), else_=0)).label('other'),
            func.sum(case((FinancialRecord.type == 4, FinancialRecord.amount), else_=0)).label('refund')
        ).filter(
            func.date(FinancialRecord.occur_time) >= month_start,
            func.date(FinancialRecord.occur_time) <= today
        ).first()
        
        sales_income = float(monthly_financial.sales or 0)
        purchase_expense = float(monthly_financial.purchase or 0)
        other_expense = float(monthly_financial.other or 0)
        return_refund = float(monthly_financial.refund or 0)
        
        monthly_profit = sales_income - purchase_expense - other_expense - return_refund
        
        return jsonify({
            'success': True,
            'data': {
                'today_sales': round(float(today_sales), 2),
                'low_stock_count': int(low_stock_count),
                'monthly_purchase_orders': int(monthly_purchase_orders),
                'monthly_profit': round(monthly_profit, 2),
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@dashboard_bp.route('/quick-stats', methods=['GET'])
def get_quick_stats():
    """
    获取快速统计数据（简化版仪表盘）
    """
    try:
        today = date.today()
        
        # 产品总数
        product_count = db.session.query(func.count(Product.product_id)).scalar() or 0
        
        # 供应商总数
        supplier_count = db.session.query(func.count(Supplier.supplier_id)).scalar() or 0
        
        # 客户总数
        from models import Customer
        customer_count = db.session.query(func.count(Customer.customer_id)).scalar() or 0
        
        # 今日订单数
        today_orders = db.session.query(func.count(SalesOrder.order_id)).filter(
            func.date(SalesOrder.order_time) == today
        ).scalar() or 0
        
        return jsonify({
            'success': True,
            'data': {
                'product_count': int(product_count),
                'supplier_count': int(supplier_count),
                'customer_count': int(customer_count),
                'today_orders': int(today_orders),
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500
