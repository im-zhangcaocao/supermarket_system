"""
销售订单 API 测试脚本
"""
import requests
import json
from datetime import datetime, date

BASE_URL = 'http://127.0.0.1:5000'


def print_separator(title):
    print("\n" + "="*60)
    print(title)
    print("="*60)


def test_sales_api():
    """测试销售订单 API"""
    print_separator("销售订单 API 测试")
    
    # 1. 获取所有订单
    print("\n【测试 1】获取所有订单")
    response = requests.get(f'{BASE_URL}/api/sales/orders')
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data['success']}, 订单数: {data['total']}")
        if data['data']:
            print(f"第一个订单: {data['data'][0]['order_id']}")
    
    # 2. 创建新订单
    print("\n【测试 2】创建新订单")
    new_order = {
        "customer_id": 1,
        "payment_method": "微信支付",
        "shipping_address": "测试地址",
        "discount_amount": 0,
        "items": [
            {"product_id": 1, "quantity": 1},
            {"product_id": 3, "quantity": 1}
        ]
    }
    response = requests.post(f'{BASE_URL}/api/sales/orders', json=new_order)
    print(f"状态码: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"成功: {data['success']}")
        if data['success']:
            order_id = data['data']['order_id']
            print(f"订单号: {order_id}")
            
            # 3. 获取单个订单详情
            print(f"\n【测试 3】获取订单详情: {order_id}")
            response = requests.get(f'{BASE_URL}/api/sales/orders/{order_id}')
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"成功: {data['success']}")
                if data['success']:
                    print(f"订单金额: {data['data']['final_amount']}")
                    print(f"商品数: {len(data['data']['items'])}")
            
            # 4. 支付订单
            print(f"\n【测试 4】支付订单: {order_id}")
            response = requests.post(f'{BASE_URL}/api/sales/orders/{order_id}/pay', 
                                    json={"operator": "test"})
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"成功: {data['success']}")
                if data['success']:
                    print(f"支付状态: {data['data']['payment_status']}")
            
            # 5. 标记交付
            print(f"\n【测试 5】标记订单交付: {order_id}")
            response = requests.post(f'{BASE_URL}/api/sales/orders/{order_id}/deliver',
                                    json={"operator": "test", "remark": "测试交付"})
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"成功: {data['success']}")
                if data['success']:
                    print(f"交付状态: {data['data']['delivery_status']}")
            
            # 6. 退货
            print(f"\n【测试 6】订单退货: {order_id}")
            return_data = {
                "items": [{"product_id": 1, "quantity": 1}],
                "operator": "test",
                "remark": "测试退货"
            }
            response = requests.post(f'{BASE_URL}/api/sales/orders/{order_id}/return',
                                    json=return_data)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"成功: {data['success']}")
                if data['success']:
                    print(f"退货金额: {data['data']['return_amount']}")
    
    # 7. 按条件查询订单
    print("\n【测试 7】按客户查询订单")
    response = requests.get(f'{BASE_URL}/api/sales/orders?customer_id=1')
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data['success']}, 订单数: {data['total']}")


def main():
    print("\n" + "="*60)
    print("家电超市管理系统 - 销售订单 API 测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        test_sales_api()
        
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
