"""
测试供应商KPI功能
"""
import requests

# 获取供应商列表
print("=== 获取供应商列表 ===")
r = requests.get('http://127.0.0.1:5000/api/suppliers')
data = r.json()

print(f"状态码: {r.status_code}")
print(f"供应商总数: {data.get('total')}")
print()

# 打印每个供应商的KPI信息
suppliers = data.get('data', [])
for supplier in suppliers:
    print(f"供应商: {supplier['supplier_name']}")
    print(f"  准时交付率: {supplier['on_time_rate']}%")
    print(f"  平均交付天数: {supplier['average_delivery_days']} 天")
    print(f"  最近采购日期: {supplier['last_order_date'] or '无'}")
    print()

# 测试单个供应商详情
if suppliers:
    print("=== 测试单个供应商详情 ===")
    supplier_id = suppliers[0]['supplier_id']
    r = requests.get(f'http://127.0.0.1:5000/api/suppliers/{supplier_id}')
    detail = r.json()
    print(f"供应商ID: {supplier_id}")
    print(f"供应商名称: {detail['data']['supplier_name']}")
    print(f"状态: {'启用' if detail['data']['status'] == 1 else '禁用'}")