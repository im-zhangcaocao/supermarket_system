"""
财务管理 API 路由
"""
from flask import Blueprint, request, jsonify
from models import db, FinancialRecord, SalesOrder, PurchaseOrder
from datetime import datetime, date

finance_bp = Blueprint('finance', __name__, url_prefix='/api/finance')


def get_type_text(record_type):
    """获取财务记录类型文本"""
    type_map = {
        1: '销售收入',
        2: '采购支出',
        3: '其他支出',
        4: '退货退款',
        '1': '销售收入',
        '2': '采购支出',
        '3': '其他支出',
        '4': '退货退款'
    }
    return type_map.get(record_type, '未知')


@finance_bp.route('/records', methods=['GET'])
def get_financial_records():
    """获取财务流水"""
    try:
        # 获取查询参数
        record_type = request.args.get('type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 构建查询
        query = FinancialRecord.query
        
        # 按类型筛选
        if record_type:
            query = query.filter(FinancialRecord.type == int(record_type))
        
        # 按日期筛选
        if start_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(FinancialRecord.occur_time >= start_datetime)
        
        if end_date:
            end_datetime = datetime.strptime(f'{end_date} 23:59:59', '%Y-%m-%d %H:%M:%S')
            query = query.filter(FinancialRecord.occur_time <= end_datetime)
        
        # 按时间倒序排列
        total = query.count()
        records = query.order_by(FinancialRecord.occur_time.desc())\
                       .offset((page - 1) * page_size)\
                       .limit(page_size)\
                       .all()
        
        # 转换结果
        result = []
        for record in records:
            record_data = record.to_dict()
            record_data['type_text'] = get_type_text(record.type)
            result.append(record_data)
        
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
            'error': str(e),
            'code': 500
        }), 500


@finance_bp.route('/other-expense', methods=['POST'])
def add_other_expense():
    """录入其他支出"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['category', 'amount', 'note']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必需字段: {field}',
                    'code': 400
                }), 400
        
        category = data['category']
        amount = float(data['amount'])
        remark = data['note']
        
        # 验证金额
        if amount <= 0:
            return jsonify({
                'success': False,
                'error': '金额必须大于0',
                'code': 400
            }), 400
        
        # 获取日期（默认为今天）
        if 'date' in data:
            try:
                occur_date = datetime.strptime(data['date'], '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': '日期格式错误，应为YYYY-MM-DD',
                    'code': 400
                }), 400
        else:
            occur_date = datetime.now()
        
        # 创建财务记录（type=5 表示其他支出）
        record = FinancialRecord(
            type=5,  # 其他支出
            amount=amount,
            category=category,
            remark=remark,
            occur_time=occur_date
        )
        
        db.session.add(record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': record.to_dict(),
            'message': '其他支出录入成功',
            'code': 201
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@finance_bp.route('/summary', methods=['GET'])
def get_financial_summary():
    """获取财务汇总（收入、支出、利润）"""
    try:
        # 获取日期参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 构建查询
        query = FinancialRecord.query
        
        # 按日期筛选
        if start_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(FinancialRecord.occur_time >= start_datetime)
        
        if end_date:
            end_datetime = datetime.strptime(f'{end_date} 23:59:59', '%Y-%m-%d %H:%M:%S')
            query = query.filter(FinancialRecord.occur_time <= end_datetime)
        
        records = query.all()
        
        # 计算各项金额
        # type=1: 销售收入
        # type=2: 采购支出
        # type=3: 成本
        # type=4: 退货退款
        # type=5: 其他支出
        
        sales_income = sum(r.amount for r in records if r.type == 1)      # 销售收入
        purchase_expense = sum(r.amount for r in records if r.type == 2)  # 采购支出
        other_expense = sum(r.amount for r in records if r.type == 5)     # 其他支出
        return_refund = sum(r.amount for r in records if r.type == 4)     # 退货退款
        
        # 利润计算公式：
        # 总收入 = 销售收入 - 退货退款
        # 总支出 = 采购支出 + 其他支出
        # 利润 = 总收入 - 总支出 = (销售收入 - 退货退款) - (采购支出 + 其他支出)
        #      = 销售收入 - 采购支出 - 其他支出 - 退货退款
        
        total_income = sales_income - return_refund  # 实际收入（扣除退货）
        total_expense = purchase_expense + other_expense  # 总支出
        profit = total_income - total_expense  # 净利润
        
        # 计算毛利率（粗略估算，基于销售和采购）
        # 毛利率 = (销售收入 - 采购成本) / 销售收入 * 100%
        gross_profit_margin = ((sales_income - purchase_expense) / sales_income * 100) if sales_income > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'sales_income': round(sales_income, 2),        # 销售收入
                'purchase_expense': round(purchase_expense, 2),# 采购支出
                'other_expense': round(other_expense, 2),       # 其他支出
                'return_refund': round(return_refund, 2),       # 退货退款
                'total_income': round(total_income, 2),         # 实际收入（销售收入 - 退货）
                'total_expense': round(total_expense, 2),       # 总支出（采购 + 其他）
                'profit': round(profit, 2),                     # 净利润
                'gross_profit_margin': round(gross_profit_margin, 2),  # 毛利率(%)
                'record_count': len(records)                    # 记录数
            },
            'formula': {
                'total_income': '销售收入 - 退货退款',
                'total_expense': '采购支出 + 其他支出',
                'profit': '(销售收入 - 退货退款) - (采购支出 + 其他支出)'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@finance_bp.route('/profit', methods=['GET'])
def get_profit():
    """获取利润数值"""
    try:
        # 获取日期参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 构建查询
        query = FinancialRecord.query
        
        # 按日期筛选
        if start_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(FinancialRecord.occur_time >= start_datetime)
        
        if end_date:
            end_datetime = datetime.strptime(f'{end_date} 23:59:59', '%Y-%m-%d %H:%M:%S')
            query = query.filter(FinancialRecord.occur_time <= end_datetime)
        
        records = query.all()
        
        # 计算利润
        # 利润 = 销售收入 - 采购支出 - 其他支出 - 退货退款
        sales_income = sum(r.amount for r in records if r.type == 1)      # 销售收入
        purchase_expense = sum(r.amount for r in records if r.type == 2)  # 采购支出
        other_expense = sum(r.amount for r in records if r.type == 3)     # 其他支出
        return_refund = sum(r.amount for r in records if r.type == 4)     # 退货退款
        
        profit = sales_income - purchase_expense - other_expense - return_refund
        
        return jsonify({
            'success': True,
            'data': {
                'profit': round(profit, 2),
                'sales_income': round(sales_income, 2),
                'purchase_expense': round(purchase_expense, 2),
                'other_expense': round(other_expense, 2),
                'return_refund': round(return_refund, 2)
            },
            'formula': '利润 = 销售收入 - 采购支出 - 其他支出 - 退货退款'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@finance_bp.route('/daily-summary', methods=['GET'])
def get_daily_summary():
    """获取每日财务汇总"""
    try:
        # 获取日期范围
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date:
            start_date = date.today().strftime('%Y-%m-%d')
        if not end_date:
            end_date = date.today().strftime('%Y-%m-%d')
        
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(f'{end_date} 23:59:59', '%Y-%m-%d %H:%M:%S')
        
        records = FinancialRecord.query.filter(
            FinancialRecord.occur_time >= start_datetime,
            FinancialRecord.occur_time <= end_datetime
        ).order_by(FinancialRecord.occur_time).all()
        
        # 按日期分组统计
        daily_data = {}
        for record in records:
            date_str = record.occur_time.strftime('%Y-%m-%d')
            if date_str not in daily_data:
                daily_data[date_str] = {
                    'date': date_str,
                    'sales_income': 0,
                    'purchase_expense': 0,
                    'other_expense': 0,
                    'return_refund': 0,
                    'profit': 0
                }
            
            if record.type == 1:
                daily_data[date_str]['sales_income'] += record.amount
            elif record.type == 2:
                daily_data[date_str]['purchase_expense'] += record.amount
            elif record.type == 3:
                daily_data[date_str]['other_expense'] += record.amount
            elif record.type == 4:
                daily_data[date_str]['return_refund'] += record.amount
        
        # 计算每日利润
        for date_str in daily_data:
            day = daily_data[date_str]
            day['profit'] = day['sales_income'] - day['purchase_expense'] - day['other_expense'] - day['return_refund']
            day['sales_income'] = round(day['sales_income'], 2)
            day['purchase_expense'] = round(day['purchase_expense'], 2)
            day['other_expense'] = round(day['other_expense'], 2)
            day['return_refund'] = round(day['return_refund'], 2)
            day['profit'] = round(day['profit'], 2)
        
        # 转换为列表并按日期排序
        result = sorted(daily_data.values(), key=lambda x: x['date'])
        
        return jsonify({
            'success': True,
            'data': result,
            'total_days': len(result)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@finance_bp.route('/category-summary', methods=['GET'])
def get_category_summary():
    """按类别统计支出"""
    try:
        # 获取日期参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 构建查询（只查询其他支出 type=3）
        query = FinancialRecord.query.filter(FinancialRecord.type == 3)
        
        if start_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(FinancialRecord.occur_time >= start_datetime)
        
        if end_date:
            end_datetime = datetime.strptime(f'{end_date} 23:59:59', '%Y-%m-%d %H:%M:%S')
            query = query.filter(FinancialRecord.occur_time <= end_datetime)
        
        records = query.all()
        
        # 按类别分组统计
        category_data = {}
        for record in records:
            category = record.category or '未分类'
            if category not in category_data:
                category_data[category] = {
                    'category': category,
                    'amount': 0,
                    'count': 0
                }
            category_data[category]['amount'] += record.amount
            category_data[category]['count'] += 1
        
        # 转换为列表并按金额降序排序
        result = sorted(category_data.values(), key=lambda x: x['amount'], reverse=True)
        
        # 格式化金额
        for item in result:
            item['amount'] = round(item['amount'], 2)
        
        return jsonify({
            'success': True,
            'data': result,
            'total_categories': len(result),
            'total_amount': round(sum(r['amount'] for r in result), 2)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500
