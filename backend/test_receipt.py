import requests

# 获取订单列表
print("=== 获取采购订单列表 ===")
r = requests.get('http://127.0.0.1:5000/api/purchase/orders')
data = r.json()
for o in data['data'][:5]:
    print(f"ID: {o['purchase_order_id']}, Status: {o['status']}, Text: {o['status_text']}")

# 测试全部不合格的情况
print("\n=== 测试全部不合格情况 ===")
r = requests.post('http://127.0.0.1:5000/api/purchase/orders/PO202606030001/receipt', 
                  json={'items': [{'product_id': 3, 'received_quantity': 1, 'quality_status': '不合格'}], 
                        'operator': 'test', 'remark': '全部不合格测试'})
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")

# 测试部分合格的情况
print("\n=== 测试部分合格情况 ===")
r = requests.post('http://127.0.0.1:5000/api/purchase/orders/PO202606030002/receipt', 
                  json={'items': [{'product_id': 3, 'received_quantity': 2, 'quality_status': '合格'},
                                 {'product_id': 3, 'received_quantity': 1, 'quality_status': '不合格'}], 
                        'operator': 'test', 'remark': '部分合格测试'})
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")