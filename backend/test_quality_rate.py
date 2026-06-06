"""
测试产品合格率功能
"""
import requests

# 获取产品列表
print("=== 获取产品列表（包含合格率） ===")
r = requests.get('http://127.0.0.1:5000/api/products')
data = r.json()

print(f"状态码: {r.status_code}")
print(f"产品总数: {data.get('total')}")
print()

# 打印产品信息（包含合格率）
products = data.get('data', [])
for product in products[:5]:
    print(f"产品: {product['product_name']}")
    print(f"  品牌: {product['brand']}")
    print(f"  类别: {product['category']}")
    print(f"  当前库存: {product['current_stock']}")
    print(f"  合格率: {product['quality_rate']}%")
    print(f"  合格数量/总检验数量: {product['quality_count']}/{product['total_inspected']}")
    print()

# 测试按合格率排序
print("=== 按合格率降序排序 ===")
r = requests.get('http://127.0.0.1:5000/api/products?sort_by=quality_rate&sort_order=desc')
data = r.json()
products = data.get('data', [])
for product in products[:3]:
    print(f"{product['product_name']}: {product['quality_rate']}%")

print()

print("=== 按合格率升序排序 ===")
r = requests.get('http://127.0.0.1:5000/api/products?sort_by=quality_rate&sort_order=asc')
data = r.json()
products = data.get('data', [])
for product in products[:3]:
    print(f"{product['product_name']}: {product['quality_rate']}%")