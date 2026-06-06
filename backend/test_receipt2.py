import requests

# 创建新的采购订单
print("=== 创建新的采购订单 ===")
new_order = {
    "supplier_id": 1,
    "items": [
        {"product_id": 3, "quantity": 5, "unit_price": 1500.0}
    ],
    "expected_date": "2026-06-10",
    "remark": "测试订单"
}
r = requests.post('http://127.0.0.1:5000/api/purchase/orders', json=new_order)
print(f"Create order - Status: {r.status_code}")
order_data = r.json()
order_id = order_data['data']['purchase_order_id']
print(f"Created order ID: {order_id}")

# 测试全部不合格的情况
print("\n=== 测试全部不合格情况 ===")
r = requests.post(f'http://127.0.0.1:5000/api/purchase/orders/{order_id}/receipt', 
                  json={'items': [{'product_id': 3, 'received_quantity': 5, 'quality_status': '不合格'}], 
                        'operator': 'test', 'remark': '全部不合格测试'})
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")

# 检查订单状态
print("\n=== 检查订单状态 ===")
r = requests.get(f'http://127.0.0.1:5000/api/purchase/orders/{order_id}')
print(f"Status: {r.status_code}")
order_info = r.json()
print(f"Order Status: {order_info['data']['status']}")
print(f"Order Status Text: {order_info['data']['status_text']}")

# 创建另一个订单测试部分合格
print("\n=== 创建第二个测试订单 ===")
new_order2 = {
    "supplier_id": 1,
    "items": [
        {"product_id": 3, "quantity": 5, "unit_price": 1500.0}
    ],
    "expected_date": "2026-06-10",
    "remark": "测试订单2"
}
r = requests.post('http://127.0.0.1:5000/api/purchase/orders', json=new_order2)
order_id2 = r.json()['data']['purchase_order_id']
print(f"Created order ID: {order_id2}")

# 测试部分合格的情况
print("\n=== 测试部分合格情况 ===")
r = requests.post(f'http://127.0.0.1:5000/api/purchase/orders/{order_id2}/receipt', 
                  json={'items': [{'product_id': 3, 'received_quantity': 3, 'quality_status': '合格'},
                                 {'product_id': 3, 'received_quantity': 2, 'quality_status': '不合格'}], 
                        'operator': 'test', 'remark': '部分合格测试'})
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")