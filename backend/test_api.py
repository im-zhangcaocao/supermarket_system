"""
API 测试脚本
测试产品、库存、供应商 API
"""
import requests
import json
from datetime import datetime

BASE_URL = 'http://127.0.0.1:5000'


def print_separator(title):
    print("\n" + "="*60)
    print(title)
    print("="*60)


def test_health():
    """测试健康检查"""
    print_separator("1. 测试健康检查")
    response = requests.get(f'{BASE_URL}/health')
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_products():
    """测试产品 API"""
    print_separator("2. 测试产品 API")
    
    # 2.1 获取所有产品
    print("\n【2.1】获取所有产品")
    response = requests.get(f'{BASE_URL}/api/products')
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"成功: {data['success']}, 总数: {data['total']}")
    
    # 2.2 按分类查询
    print("\n【2.2】按分类查询 (category=空调)")
    response = requests.get(f'{BASE_URL}/api/products?category=空调')
    data = response.json()
    print(f"成功: {data['success']}, 总数: {data['total']}")
    
    # 2.3 获取单个产品
    print("\n【2.3】获取单个产品 (id=1)")
    response = requests.get(f'{BASE_URL}/api/products/1')
    print(f"状态码: {response.status_code}")
    data = response.json()
    if data['success']:
        print(f"产品: {data['data']['product_name']}")
    
    # 2.4 添加产品
    print("\n【2.4】添加新产品")
    new_product = {
        'product_name': '测试商品',
        'brand': '测试品牌',
        'model': 'TEST-001',
        'category': '其他',
        'retail_price': 999.00,
        'purchase_ref_price': 700.00,
        'current_stock': 20,
        'threshold': 5,
        'operator': 'test'
    }
    response = requests.post(f'{BASE_URL}/api/products', json=new_product)
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"成功: {data['success']}, 消息: {data.get('message', data.get('error'))}")
    
    # 2.5 更新产品
    print("\n【2.5】更新产品")
    update_data = {
        'retail_price': 1099.00,
        'operator': 'test'
    }
    response = requests.put(f'{BASE_URL}/api/products/6', json=update_data)
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"成功: {data['success']}, 新价格: {data['data']['retail_price']}")
    
    # 2.6 设置预警阈值
    print("\n【2.6】设置预警阈值")
    response = requests.patch(f'{BASE_URL}/api/products/6/threshold', json={'threshold': 8, 'operator': 'test'})
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"成功: {data['success']}, 新阈值: {data['data']['threshold']}")


def test_stock():
    """测试库存 API"""
    print_separator("3. 测试库存 API")
    
    # 3.1 查询库存
    print("\n【3.1】查询库存 (product_id=1)")
    response = requests.get(f'{BASE_URL}/api/stock/1')
    print(f"状态码: {response.status_code}")
    data = response.json()
    if data['success']:
        print(f"产品: {data['data']['product_name']}")
        print(f"当前库存: {data['data']['current_stock']}")
        print(f"预警阈值: {data['data']['threshold']}")
        print(f"是否低库存: {data['data']['is_low_stock']}")
    
    # 3.2 扣减库存
    print("\n【3.2】扣减库存")
    deduct_data = {
        'product_id': 1,
        'quantity': 2,
        'relate_order_id': 'SO-TEST-001',
        'operator': 'test',
        'remark': '测试扣减'
    }
    response = requests.post(f'{BASE_URL}/api/stock/deduct', json=deduct_data)
    print(f"状态码: {response.status_code}")
    data = response.json()
    if data['success']:
        print(f"成功: 库存从 {data['data']['before_quantity']} 变为 {data['data']['after_quantity']}")
    
    # 3.3 增加库存
    print("\n【3.3】增加库存")
    add_data = {
        'product_id': 1,
        'quantity': 5,
        'reason': '采购入库',
        'operator_id': 'test',
        'relate_order_id': 'PO-TEST-001',
        'remark': '测试增加'
    }
    response = requests.post(f'{BASE_URL}/api/stock/add', json=add_data)
    print(f"状态码: {response.status_code}")
    data = response.json()
    if data['success']:
        print(f"成功: 库存从 {data['data']['before_quantity']} 变为 {data['data']['after_quantity']}")
    
    # 3.4 低库存预警
    print("\n【3.4】低库存预警列表")
    response = requests.get(f'{BASE_URL}/api/stock/alerts')
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"成功: {data['success']}, 预警数量: {data['total']}")
    
    # 3.5 库存流水
    print("\n【3.5】库存流水")
    response = requests.get(f'{BASE_URL}/api/stock/logs?product_id=1')
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"成功: {data['success']}, 日志数量: {data['total']}")
    
    # 3.6 手动调整库存
    print("\n【3.6】手动调整库存")
    adjust_data = {
        'product_id': 1,
        'delta': -3,
        'reason': '盘点调整',
        'operator_id': 'admin',
        'remark': '库存盘点调整'
    }
    response = requests.post(f'{BASE_URL}/api/stock/adjust', json=adjust_data)
    print(f"状态码: {response.status_code}")
    data = response.json()
    if data['success']:
        print(f"成功: 库存从 {data['data']['before_quantity']} 变为 {data['data']['after_quantity']}")


def test_suppliers():
    """测试供应商 API"""
    print_separator("4. 测试供应商 API")
    
    # 4.1 获取所有供应商
    print("\n【4.1】获取所有供应商")
    response = requests.get(f'{BASE_URL}/api/suppliers')
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"成功: {data['success']}, 总数: {data['total']}")
    
    # 4.2 获取单个供应商
    print("\n【4.2】获取单个供应商 (id=1)")
    response = requests.get(f'{BASE_URL}/api/suppliers/1')
    print(f"状态码: {response.status_code}")
    data = response.json()
    if data['success']:
        print(f"供应商: {data['data']['supplier_name']}")
    
    # 4.3 添加供应商
    print("\n【4.3】添加供应商")
    new_supplier = {
        'supplier_name': '测试供应商有限公司',
        'contact_person': '测试联系人',
        'contact_phone': '400-123-4567',
        'address': '测试地址'
    }
    response = requests.post(f'{BASE_URL}/api/suppliers', json=new_supplier)
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"成功: {data['success']}, 消息: {data.get('message', data.get('error'))}")
    
    # 4.4 更新供应商
    print("\n【4.4】更新供应商")
    update_data = {
        'contact_person': '新联系人',
        'contact_phone': '400-654-3210'
    }
    response = requests.put(f'{BASE_URL}/api/suppliers/4', json=update_data)
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"成功: {data['success']}, 新联系人: {data['data']['contact_person']}")
    
    # 4.5 供应商统计
    print("\n【4.5】供应商统计")
    response = requests.get(f'{BASE_URL}/api/suppliers/2/statistics')
    print(f"状态码: {response.status_code}")
    data = response.json()
    if data['success']:
        print(f"供应商: {data['data']['supplier_name']}")
        print(f"总订单: {data['data']['total_orders']}")
        print(f"总金额: ¥{data['data']['total_amount']}")


def main():
    print("\n" + "="*60)
    print("家电超市管理系统 API 测试")
    print("="*60)
    print(f"测试地址: {BASE_URL}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        test_health()
        test_products()
        test_stock()
        test_suppliers()
        
        print("\n" + "="*60)
        print("✓ 所有测试完成！")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ 错误: 无法连接到后端服务")
        print("请确保后端服务已启动: python app.py")
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")


if __name__ == '__main__':
    main()
