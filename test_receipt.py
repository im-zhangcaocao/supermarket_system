import requests
import json

# 创建测试订单
order_data = {
    "supplier_id": 3,
    "expected_date": "2026-06-10",
    "remark": "测试订单",
    "items": [
        {"product_id": 1, "quantity": 2, "unit_price": 1800},
        {"product_id": 2, "quantity": 3, "unit_price": 2500}
    ]
}

print("创建订单...")
response = requests.post("http://localhost:5000/api/purchase/orders", json=order_data)
print("创建订单响应:", response.json())
order_id = response.json()["data"]["purchase_order_id"]

# 测试全部合格
print("\n=== 测试全部合格 ===")
receipt_data = {
    "items": [
        {"product_id": 1, "received_quantity": 2, "quality_status": "合格"},
        {"product_id": 2, "received_quantity": 3, "quality_status": "合格"}
    ],
    "operator": "admin",
    "remark": "全部合格测试"
}

response = requests.post(f"http://localhost:5000/api/purchase/orders/{order_id}/receipt", json=receipt_data)
result = response.json()
print("响应:", json.dumps(result, ensure_ascii=False, indent=2))

# 检查库存变化
print("\n库存状态:")
products = requests.get("http://localhost:5000/api/products").json()
for p in products["data"]:
    print(f"产品 {p['product_id']}: {p['product_name']} - 当前库存: {p['current_stock']}")

# 创建另一个订单测试混合情况
order_data2 = {
    "supplier_id": 3,
    "expected_date": "2026-06-10",
    "remark": "测试混合订单",
    "items": [
        {"product_id": 3, "quantity": 5, "unit_price": 3000}
    ]
}

print("\n创建混合测试订单...")
response = requests.post("http://localhost:5000/api/purchase/orders", json=order_data2)
order_id2 = response.json()["data"]["purchase_order_id"]

# 测试不合格
print("\n=== 测试全部不合格 ===")
receipt_data2 = {
    "items": [
        {"product_id": 3, "received_quantity": 5, "quality_status": "不合格"}
    ],
    "operator": "admin",
    "remark": "全部不合格测试"
}

response = requests.post(f"http://localhost:5000/api/purchase/orders/{order_id2}/receipt", json=receipt_data2)
result = response.json()
print("响应:", json.dumps(result, ensure_ascii=False, indent=2))

# 检查库存变化
print("\n库存状态:")
products = requests.get("http://localhost:5000/api/products").json()
for p in products["data"]:
    print(f"产品 {p['product_id']}: {p['product_name']} - 当前库存: {p['current_stock']}")