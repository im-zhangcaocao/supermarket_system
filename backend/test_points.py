#!/usr/bin/env python
"""销售订单积分功能单元测试"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest
import json
from app import app, db
from models import Customer, SalesOrder, SalesOrderItem, Product

@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # 创建测试数据
            create_test_data()
        yield client
    
    with app.app_context():
        db.drop_all()

def create_test_data():
    """创建测试数据"""
    # 创建客户
    customer = Customer(
        name='测试客户',
        phone='13800138000',
        points=5000,
        membership_level='黄金会员',
        discount_rate=0.9
    )
    db.session.add(customer)
    
    # 创建商品
    product = Product(
        product_name='测试商品',
        retail_price=1000.00,
        current_stock=10,
        threshold=5
    )
    db.session.add(product)
    
    db.session.commit()

def test_create_order_with_points_discount(client):
    """测试创建订单时使用积分抵扣"""
    # 创建订单使用积分抵扣
    response = client.post(
        '/api/sales/orders',
        data=json.dumps({
            'customer_id': 1,
            'items': [{'product_id': 1, 'quantity': 1}],
            'payment_method': '微信支付',
            'points_used': 500
        }),
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    assert response.status_code == 201
    assert data['success'] == True
    assert 'order_id' in data['data']
    
    # 验证订单创建成功
    order_id = data['data']['order_id']
    response = client.get(f'/api/sales/orders/{order_id}')
    order_data = json.loads(response.data)['data']
    
    assert order_data['points_used'] == 500
    assert order_data['points_discount'] == 5.0  # 500积分 = 5元
    # 最终金额 = 商品价格 - 积分抵扣金额
    assert order_data['final_amount'] == order_data['total_amount'] - 5.0

def test_create_order_points_insufficient(client):
    """测试积分不足时创建订单失败"""
    # 尝试使用超过可用积分
    response = client.post(
        '/api/sales/orders',
        data=json.dumps({
            'customer_id': 1,
            'items': [{'product_id': 1, 'quantity': 1}],
            'payment_method': '微信支付',
            'points_used': 6000  # 超过可用积分5000
        }),
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    assert response.status_code == 400
    assert data['success'] == False
    assert '积分不足' in data['error']

def test_pay_order_earn_points(client):
    """测试支付订单后获得积分"""
    # 先创建订单（不使用积分抵扣）
    response = client.post(
        '/api/sales/orders',
        data=json.dumps({
            'customer_id': 1,
            'items': [{'product_id': 1, 'quantity': 1}],
            'payment_method': '微信支付',
            'points_used': 0
        }),
        content_type='application/json'
    )
    order_id = json.loads(response.data)['data']['order_id']
    
    # 支付订单
    response = client.post(
        f'/api/sales/orders/{order_id}/pay',
        data=json.dumps({'operator': 'test'}),
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['success'] == True
    
    # 验证获得积分（实付1000元 = 1000积分）
    assert data['data']['points_earned'] == 1000
    
    # 验证客户积分增加
    response = client.get('/api/customers/1')
    customer_data = json.loads(response.data)['data']
    assert customer_data['points'] == 5000 + 1000  # 5000初始 + 1000获得

def test_create_order_no_points(client):
    """测试不使用积分抵扣创建订单"""
    response = client.post(
        '/api/sales/orders',
        data=json.dumps({
            'customer_id': 1,
            'items': [{'product_id': 1, 'quantity': 1}],
            'payment_method': '微信支付'
        }),
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    assert response.status_code == 201
    assert data['success'] == True
    
    order_id = data['data']['order_id']
    response = client.get(f'/api/sales/orders/{order_id}')
    order_data = json.loads(response.data)['data']
    
    assert order_data['points_used'] == 0
    assert order_data['points_discount'] == 0.0
    assert order_data['final_amount'] == 1000.0

def test_points_discount_max_limit(client):
    """测试积分抵扣最大限制（订单金额的90%）"""
    # 创建订单使用大量积分
    response = client.post(
        '/api/sales/orders',
        data=json.dumps({
            'customer_id': 1,
            'items': [{'product_id': 1, 'quantity': 1}],
            'payment_method': '微信支付',
            'points_used': 5000  # 5000积分 = 50元
        }),
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    assert response.status_code == 201
    
    order_id = data['data']['order_id']
    response = client.get(f'/api/sales/orders/{order_id}')
    order_data = json.loads(response.data)['data']
    
    # 最大抵扣90% = 900元 = 90000积分，但商品只有1000元
    # 所以最大抵扣900元 = 90000积分，但客户只有5000积分
    # 所以实际抵扣50元
    assert order_data['points_discount'] == 50.0  # 5000积分 = 50元
    assert order_data['final_amount'] == 950.0  # 1000 - 50 = 950

def test_order_list_with_points_info(client):
    """测试订单列表正确显示积分信息"""
    # 创建多个订单（一个使用积分，一个不使用）
    response1 = client.post(
        '/api/sales/orders',
        data=json.dumps({
            'customer_id': 1,
            'items': [{'product_id': 1, 'quantity': 1}],
            'payment_method': '微信支付',
            'points_used': 1000
        }),
        content_type='application/json'
    )
    order1_id = json.loads(response1.data)['data']['order_id']
    
    response2 = client.post(
        '/api/sales/orders',
        data=json.dumps({
            'customer_id': 1,
            'items': [{'product_id': 1, 'quantity': 1}],
            'payment_method': '支付宝',
            'points_used': 0
        }),
        content_type='application/json'
    )
    order2_id = json.loads(response2.data)['data']['order_id']
    
    # 获取订单列表
    response = client.get('/api/sales/orders')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['success'] == True
    assert data['total'] >= 2
    
    # 验证积分信息在列表中正确显示
    orders = data['data']
    order1 = next(o for o in orders if o['order_id'] == order1_id)
    order2 = next(o for o in orders if o['order_id'] == order2_id)
    
    assert order1['points_used'] == 1000
    assert order1['points_discount'] == 10.0
    assert order1['points_earned'] == 0  # 未支付时为0
    
    assert order2['points_used'] == 0
    assert order2['points_discount'] == 0.0
    assert order2['points_earned'] == 0

def test_order_detail_with_points_info(client):
    """测试订单详情正确显示积分信息"""
    # 创建订单使用积分抵扣
    response = client.post(
        '/api/sales/orders',
        data=json.dumps({
            'customer_id': 1,
            'items': [{'product_id': 1, 'quantity': 1}],
            'payment_method': '微信支付',
            'points_used': 500
        }),
        content_type='application/json'
    )
    
    order_id = json.loads(response.data)['data']['order_id']
    
    # 获取订单详情
    response = client.get(f'/api/sales/orders/{order_id}')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['success'] == True
    
    order_data = data['data']
    
    # 验证订单详情中的积分信息
    assert order_data['points_used'] == 500
    assert order_data['points_discount'] == 5.0
    assert order_data['total_amount'] == 1000.0
    assert order_data['final_amount'] == 995.0  # 1000 - 5 = 995
    
    # 支付订单后验证获得积分
    response = client.post(
        f'/api/sales/orders/{order_id}/pay',
        data=json.dumps({'operator': 'test'}),
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['success'] == True
    assert data['data']['points_earned'] == 995  # 实付995元获得995积分
    
    # 再次获取订单详情验证积分已更新
    response = client.get(f'/api/sales/orders/{order_id}')
    order_data = json.loads(response.data)['data']
    
    assert order_data['points_earned'] == 995

def test_points_calculation_with_member_discount(client):
    """测试会员折扣与积分抵扣同时使用时的计算"""
    # 黄金会员9折 + 使用积分抵扣
    response = client.post(
        '/api/sales/orders',
        data=json.dumps({
            'customer_id': 1,
            'items': [{'product_id': 1, 'quantity': 1}],
            'payment_method': '微信支付',
            'discount_amount': 100.0,  # 1000 * 0.1 = 100元折扣
            'points_used': 1000  # 1000积分 = 10元
        }),
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    assert response.status_code == 201
    
    order_id = data['data']['order_id']
    response = client.get(f'/api/sales/orders/{order_id}')
    order_data = json.loads(response.data)['data']
    
    # 计算：1000 - 100(会员折扣) - 10(积分抵扣) = 890
    assert order_data['total_amount'] == 1000.0
    assert order_data['discount_amount'] == 100.0
    assert order_data['points_discount'] == 10.0
    assert order_data['final_amount'] == 890.0

if __name__ == '__main__':
    pytest.main([__file__, '-v'])