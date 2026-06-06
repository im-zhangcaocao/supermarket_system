"""
员工管理 API 路由
"""
from flask import Blueprint, request, jsonify
from models import db, User, SalesOrder, PurchaseOrder
from middleware.auth import admin_required, login_required
from datetime import datetime
import bcrypt
import re

employees_bp = Blueprint('employees', __name__, url_prefix='/api/employees')

# 允许的角色列表
ALLOWED_ROLES = ['cashier', 'purchaser', 'admin']


def hash_password(password):
    """密码哈希（使用 bcrypt）"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(password, hashed_password):
    """验证密码"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


@employees_bp.route('', methods=['GET'])
@admin_required
def get_employees():
    """获取员工列表（仅管理员）"""
    try:
        # 获取查询参数
        role = request.args.get('role')
        status = request.args.get('status', type=int)
        
        # 构建查询
        query = User.query
        
        # 筛选角色（仅允许指定角色）
        if role and role in ALLOWED_ROLES:
            query = query.filter(User.role == role)
        
        if status is not None:
            query = query.filter(User.status == status)
        
        employees = query.order_by(User.user_id.desc()).all()
        
        # 返回员工信息（排除密码字段）
        result = []
        for employee in employees:
            emp_data = employee.to_dict()
            # 移除密码字段
            emp_data.pop('password', None)
            emp_data['role_text'] = {
                'cashier': '收银员',
                'purchaser': '采购员',
                'admin': '管理员'
            }.get(employee.role, employee.role)
            emp_data['status_text'] = '启用' if employee.status == 1 else '禁用'
            result.append(emp_data)
        
        return jsonify({
            'success': True,
            'data': result,
            'total': len(result)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@employees_bp.route('/<int:user_id>', methods=['GET'])
@admin_required
def get_employee(user_id):
    """获取单个员工信息（仅管理员）"""
    try:
        employee = User.query.get(user_id)
        
        if not employee:
            return jsonify({
                'success': False,
                'error': '员工不存在',
                'code': 404
            }), 404
        
        # 返回员工信息（排除密码字段）
        emp_data = employee.to_dict()
        emp_data.pop('password', None)
        emp_data['role_text'] = {
            'cashier': '收银员',
            'purchaser': '采购员',
            'admin': '管理员'
        }.get(employee.role, employee.role)
        emp_data['status_text'] = '启用' if employee.status == 1 else '禁用'
        
        return jsonify({
            'success': True,
            'data': emp_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@employees_bp.route('', methods=['POST'])
@admin_required
def create_employee():
    """添加员工（仅管理员）"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['username', 'password', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'{field} 为必填项',
                    'code': 400
                }), 400
        
        username = data['username']
        password = data['password']
        role = data['role']
        
        # 验证角色
        if role not in ALLOWED_ROLES:
            return jsonify({
                'success': False,
                'error': f'角色必须是 {ALLOWED_ROLES} 之一',
                'code': 400
            }), 400
        
        # 检查用户名是否已存在
        existing = User.query.filter_by(username=username).first()
        if existing:
            return jsonify({
                'success': False,
                'error': '用户名已存在',
                'code': 400
            }), 400
        
        # 处理日期字段
        hire_date = data.get('hire_date')
        if hire_date:
            hire_date = datetime.strptime(hire_date, '%Y-%m-%d').date()
        
        # 创建员工（密码哈希存储）
        employee = User(
            username=username,
            password=hash_password(password),
            role=role,
            status=data.get('status', 1),
            real_name=data.get('real_name'),
            phone=data.get('phone'),
            hire_date=hire_date,
            salary_type=data.get('salary_type', 'monthly'),
            salary_rate=data.get('salary_rate', 0)
        )
        
        db.session.add(employee)
        db.session.commit()
        
        # 返回员工信息（排除密码字段）
        emp_data = employee.to_dict()
        emp_data.pop('password', None)
        
        return jsonify({
            'success': True,
            'data': emp_data,
            'message': '员工添加成功',
            'code': 201
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@employees_bp.route('/<int:user_id>', methods=['PUT'])
@admin_required
def update_employee(user_id):
    """更新员工信息（仅管理员）"""
    try:
        employee = User.query.get(user_id)
        
        if not employee:
            return jsonify({
                'success': False,
                'error': '员工不存在',
                'code': 404
            }), 404
        
        data = request.get_json()
        
        # 更新角色
        if 'role' in data:
            role = data['role']
            if role not in ALLOWED_ROLES:
                return jsonify({
                    'success': False,
                    'error': f'角色必须是 {ALLOWED_ROLES} 之一',
                    'code': 400
                }), 400
            employee.role = role
        
        # 更新状态
        if 'status' in data:
            employee.status = int(data['status'])
        
        # 更新其他字段
        if 'username' in data:
            # 检查新用户名是否已被使用
            existing = User.query.filter(
                User.username == data['username'],
                User.user_id != user_id
            ).first()
            if existing:
                return jsonify({
                    'success': False,
                    'error': '用户名已被使用',
                    'code': 400
                }), 400
            employee.username = data['username']
        
        if 'real_name' in data:
            employee.real_name = data['real_name']
        
        if 'phone' in data:
            employee.phone = data['phone']
        
        if 'hire_date' in data:
            employee.hire_date = data['hire_date']
        
        if 'salary_type' in data:
            employee.salary_type = data['salary_type']
        
        if 'salary_rate' in data:
            employee.salary_rate = data['salary_rate']
        
        db.session.commit()
        
        # 返回员工信息（排除密码字段）
        emp_data = employee.to_dict()
        emp_data.pop('password', None)
        
        return jsonify({
            'success': True,
            'data': emp_data,
            'message': '员工信息更新成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@employees_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """获取当前登录用户的个人信息"""
    try:
        user_id = request.user['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': '用户不存在',
                'code': 404
            }), 404
        
        user_data = user.to_dict()
        user_data.pop('password', None)
        
        return jsonify({
            'success': True,
            'data': user_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@employees_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """更新当前登录用户的个人信息（仅本人）"""
    try:
        user_id = request.user['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': '用户不存在',
                'code': 404
            }), 404
        
        data = request.get_json()
        
        # 验证手机号码格式
        if 'phone' in data and data['phone']:
            phone = data['phone']
            if not re.match(r'^1[3-9]\d{9}$', phone):
                return jsonify({
                    'success': False,
                    'error': '手机号码格式不正确',
                    'code': 400
                }), 400
            user.phone = phone
        
        # 验证邮箱格式
        if 'email' in data and data['email']:
            email = data['email']
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                return jsonify({
                    'success': False,
                    'error': '邮箱格式不正确',
                    'code': 400
                }), 400
            user.email = email
        
        # 更新地址
        if 'address' in data:
            user.address = data['address']
        
        # 更新真实姓名
        if 'real_name' in data:
            user.real_name = data['real_name']
        
        db.session.commit()
        
        user_data = user.to_dict()
        user_data.pop('password', None)
        
        return jsonify({
            'success': True,
            'data': user_data,
            'message': '个人信息更新成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@employees_bp.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    """修改当前登录用户的密码（仅本人）"""
    try:
        user_id = request.user['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': '用户不存在',
                'code': 404
            }), 404
        
        data = request.get_json()
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        # 验证必填字段
        if not old_password or not new_password or not confirm_password:
            return jsonify({
                'success': False,
                'error': '请填写所有密码字段',
                'code': 400
            }), 400
        
        # 验证旧密码
        if not check_password(old_password, user.password):
            return jsonify({
                'success': False,
                'error': '旧密码不正确',
                'code': 400
            }), 400
        
        # 验证两次新密码是否一致
        if new_password != confirm_password:
            return jsonify({
                'success': False,
                'error': '两次输入的新密码不一致',
                'code': 400
            }), 400
        
        # 验证密码安全策略：至少6位，包含数字和字母
        if len(new_password) < 6:
            return jsonify({
                'success': False,
                'error': '密码长度至少6位',
                'code': 400
            }), 400
        
        if not re.match(r'^(?=.*[a-zA-Z])(?=.*\d)', new_password):
            return jsonify({
                'success': False,
                'error': '密码必须包含字母和数字',
                'code': 400
            }), 400
        
        # 更新密码
        user.password = hash_password(new_password)
        user.reset_password_required = 0  # 清除强制重置标记
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '密码修改成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@employees_bp.route('/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def reset_password(user_id):
    """重置密码（仅管理员）"""
    try:
        employee = User.query.get(user_id)
        
        if not employee:
            return jsonify({
                'success': False,
                'error': '员工不存在',
                'code': 404
            }), 404
        
        # 生成默认密码：用户名 + "123456"
        new_password = employee.username + "123456"
        
        # 更新密码（哈希存储）
        employee.password = hash_password(new_password)
        employee.reset_password_required = 1  # 标记需要强制重置密码
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '密码重置成功',
            'new_password': new_password
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@employees_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_employee(user_id):
    """删除员工（仅管理员）"""
    try:
        employee = User.query.get(user_id)
        
        if not employee:
            return jsonify({
                'success': False,
                'error': '员工不存在',
                'code': 404
            }), 404
        
        # 检查是否为最后一个管理员
        admin_count = User.query.filter_by(role='admin', status=1).count()
        if employee.role == 'admin' and admin_count <= 1:
            return jsonify({
                'success': False,
                'error': '不能删除最后一个管理员',
                'code': 400
            }), 400
        
        # 删除员工
        db.session.delete(employee)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '员工删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500
