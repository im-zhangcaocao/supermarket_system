"""
采购订单 API 测试脚本
"""
import requests
import json
from datetime import datetime, date, timedelta

BASE_URL = 'http://127.0.0.1:5000'


def print_separator(title):
    print("\n" + "="*60)
    print(title)
    print("="*60)


def test_purchase_api():
    """测试采购订单 API"""
    print_separator("采购订单 API 测试")
    
    # 1. 获取采购订单列表
    print("\n【测试 1】获取采购订单列表")
    response = requests.get(f'{BASE_URL}/api/purchase/orders')
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data['success']}, 订单数: {data['total']}")
    
    # 2. 创建新采购订单
    print("\n【测试 2】创建新采购订单")
    tomorrow = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
    new_order = {
        "supplier_id": 1,
        "expected_date": tomorrow,
        "remark": "测试采购订单",
        "items": [
            {"product_id": 1, "quantity": 5, "unit_price": 1500.00},
            {"product_id": 3, "quantity": 3, "unit_price": 1600.00}
        ]
    }
    response = requests.post(f'{BASE_URL}/api/purchase/orders', json=new_order)
    print(f"状态码: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"成功: {data['success']}")
        if data['success']:
            order_id = data['data']['purchase_order_id']
            print(f"采购订单号: {order_id}")
            
            # 3. 获取订单详情
            print(f"\n【测试 3】获取采购订单详情: {order_id}")
            response = requests.get(f'{BASE_URL}/api/purchase/orders/{order_id}')
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"成功: {data['success']}")
                if data['success']:
                    print(f"订单金额: {data['data']['total_amount']}")
                    print(f"商品数: {len(data['data']['items'])}")
            
            # 4. 确认收货（部分收货）
            print(f"\n【测试 4】确认收货（部分收货）: {order_id}")
            receipt_data = {
                "items": [
                    {"product_id": 1, "received_quantity": 3},
                    {"product_id": 3, "received_quantity": 3}
                ],
                "operator": "buyer",
                "remark": "部分收货"
            }
            response = requests.post(f'{BASE_URL}/api/purchase/orders/{order_id}/receipt',
                                    json=receipt_data)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"成功: {data['success']}")
                if data['success']:
                    print(f"收货金额: {data['data']['received_amount']}")
                    print(f"订单状态: {data['data']['order']['status']}")
    
    # 5. 获取超期订单
    print("\n【测试 5】获取超期订单")
    response = requests.get(f'{BASE_URL}/api/purchase/overdue')
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data['success']}, 超期订单数: {data['total']}")
    
    # 6. 获取供应商采购订单
    print("\n【测试 6】获取供应商采购订单")
    response = requests.get(f'{BASE_URL}/api/purchase/suppliers/1/orders')
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data['success']}, 订单数: {data['total']}")


def main():
    print("\n" + "="*60)
    print("家电超市管理系统 - 采购订单 API 测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        test_purchase_api()
        
        print("\n" + "="*60)
        print("✓ 测试完成！")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ 错误: 无法连接到后端服务")
        print("请确保后端服务已启动: cd backend && python app.py")
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
