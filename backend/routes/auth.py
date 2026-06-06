"""
认证 API 路由
"""
from flask import Blueprint, request, jsonify
from models import db, User
from middleware.auth import generate_token, decode_token
import bcrypt

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def hash_password(password):
    """密码哈希（使用 bcrypt）"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(password, hashed_password):
    """验证密码"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def init_admin_passwords():
    """初始化管理员密码（开发阶段，如果密码是明文则转换为哈希）"""
    with db.app.app_context():
        users = User.query.all()
        for user in users:
            # 检查密码是否已经是哈希（bcrypt哈希长度通常为60左右）
            if len(user.password) < 50:
                # 假设是明文密码，转换为哈希
                user.password = hash_password(user.password)
        db.session.commit()


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': '用户名和密码为必填项',
                'code': 400
            }), 400
        
        # 查询用户
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return jsonify({
                'success': False,
                'error': '用户名或密码错误',
                'code': 401
            }), 401
        
        # 检查用户状态
        if user.status == 0:
            return jsonify({
                'success': False,
                'error': '用户已被禁用',
                'code': 401
            }), 401
        
        # 验证密码
        # 兼容明文密码（开发阶段）和哈希密码（生产环境）
        if len(user.password) >= 50:
            # 假设是哈希密码
            if not check_password(password, user.password):
                return jsonify({
                    'success': False,
                    'error': '用户名或密码错误',
                    'code': 401
                }), 401
        else:
            # 假设是明文密码（仅开发阶段）
            if user.password != password:
                return jsonify({
                    'success': False,
                    'error': '用户名或密码错误',
                    'code': 401
                }), 401
            # 如果是明文密码，自动转换为哈希（开发阶段）
            user.password = hash_password(password)
            db.session.commit()
        
        # 更新最后登录时间
        from datetime import datetime
        user.last_login = datetime.now()
        db.session.commit()
        
        # 生成 token
        token = generate_token(user.user_id, user.username, user.role)
        
        # 返回用户信息（排除密码字段）
        user_data = {
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role,
            'role_text': {
                'cashier': '收银员',
                'purchaser': '采购员',
                'admin': '管理员'
            }.get(user.role, user.role),
            'status': user.status,
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
        
        return jsonify({
            'success': True,
            'data': {
                'token': token,
                'user': user_data
            },
            'message': '登录成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户退出登录"""
    try:
        # 在无状态认证中，logout 主要由前端处理（清除 token）
        # 这里可以记录退出日志或实现 token 黑名单（可选）
        
        return jsonify({
            'success': True,
            'message': '退出成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 500
        }), 500


@auth_bp.route('/verify', methods=['POST'])
def verify_token():
    """验证 token 有效性"""
    try:
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({
                'success': False,
                'error': '未提供 token',
                'code': 401
            }), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = decode_token(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'error': 'token 无效或已过期',
                'code': 401
            }), 401
        
        # 查询用户信息
        user = User.query.get(payload['user_id'])
        
        if not user:
            return jsonify({
                'success': False,
                'error': '用户不存在',
                'code': 401
            }), 401
        
        # 返回用户信息（排除密码字段）
        user_data = {
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role,
            'role_text': {
                'cashier': '收银员',
                'purchaser': '采购员',
                'admin': '管理员'
            }.get(user.role, user.role),
            'status': user.status
        }
        
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
