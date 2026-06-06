"""
认证中间件
包含 JWT 验证和权限检查功能
"""
import jwt
import time
from flask import request, jsonify
from functools import wraps
from models import User

# JWT 配置（生产环境应使用环境变量）
SECRET_KEY = 'supermarket-jwt-secret-key-2026'
ALGORITHM = 'HS256'
TOKEN_EXPIRATION = 86400  # 24小时


def generate_token(user_id, username, role):
    """生成 JWT token"""
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': int(time.time()) + TOKEN_EXPIRATION
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_token(token):
    """解码 JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # 检查 token 是否过期
        if payload['exp'] < int(time.time()):
            return None
        return payload
    except jwt.InvalidTokenError:
        return None


def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({
                'success': False,
                'error': '未授权，请先登录',
                'code': 401
            }), 401
        
        # 移除 Bearer 前缀（如果存在）
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = decode_token(token)
        if not payload:
            return jsonify({
                'success': False,
                'error': 'token 无效或已过期',
                'code': 401
            }), 401
        
        # 将用户信息添加到请求对象中
        request.user = payload
        
        return f(*args, **kwargs)
    
    return decorated_function


def admin_required(f):
    """管理员权限验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({
                'success': False,
                'error': '未授权，请先登录',
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
        
        # 检查是否为管理员
        if payload['role'] != 'admin':
            return jsonify({
                'success': False,
                'error': '权限不足，需要管理员权限',
                'code': 403
            }), 403
        
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated_function


def get_current_user():
    """获取当前登录用户"""
    token = request.headers.get('Authorization')
    if not token:
        return None
    
    if token.startswith('Bearer '):
        token = token[7:]
    
    return decode_token(token)
