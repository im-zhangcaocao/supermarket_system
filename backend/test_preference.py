import requests

# 获取客户订单
print("=== 获取客户订单 ===")
r = requests.get('http://127.0.0.1:5000/api/customers/1/orders')
data = r.json()
orders = data['data']

print(f"订单数量: {len(orders)}")

if orders:
    first_order = orders[0]
    print(f"\n第一个订单: {first_order['order_id']}")
    items = first_order.get('items', [])
    print(f"订单项数量: {len(items)}")
    
    if items:
        first_item = items[0]
        print("\n第一个订单项详情:")
        print(f"  product_id: {first_item.get('product_id')}")
        print(f"  product_name: {first_item.get('product_name')}")
        print(f"  quantity: {first_item.get('quantity')}")
        print(f"  unit_price: {first_item.get('unit_price')}")
        print(f"  category: {first_item.get('category')}")
        print(f"  brand: {first_item.get('brand')}")
        print(f"  subtotal: {first_item.get('subtotal')}")

# 测试前端的偏好计算逻辑
print("\n=== 测试偏好计算 ===")
totalAmount = sum(order.get('total_paid', order.get('total_amount', 0)) for order in orders)
print(f"总消费金额: {totalAmount}")

categoryStats = {}
brandStats = {}

for order in orders:
    for item in order.get('items', []):
        category = item.get('category') or '未分类'
        brand = item.get('brand') or '未知'
        subtotal = item.get('subtotal') or (item.get('quantity', 0) * item.get('unit_price', 0))
        
        categoryStats[category] = categoryStats.get(category, {'count': 0, 'amount': 0})
        categoryStats[category]['count'] += 1
        categoryStats[category]['amount'] += subtotal
        
        brandStats[brand] = brandStats.get(brand, {'count': 0, 'amount': 0})
        brandStats[brand]['count'] += 1
        brandStats[brand]['amount'] += subtotal

print("\n品类偏好:")
for category, stats in sorted(categoryStats.items(), key=lambda x: x[1]['amount'], reverse=True):
    percentage = (stats['amount'] / totalAmount * 100) if totalAmount > 0 else 0
    print(f"  {category}: {stats['count']}次, ¥{stats['amount']:.2f}, {percentage:.1f}%")

print("\n品牌偏好:")
for brand, stats in sorted(brandStats.items(), key=lambda x: x[1]['amount'], reverse=True):
    percentage = (stats['amount'] / totalAmount * 100) if totalAmount > 0 else 0
    print(f"  {brand}: {stats['count']}次, ¥{stats['amount']:.2f}, {percentage:.1f}%")