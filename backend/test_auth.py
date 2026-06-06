"""
客户、员工和认证 API 测试脚本
"""
import requests
import json
from datetime import datetime

BASE_URL = 'http://127.0.0.1:5000'


def print_separator(title):
    print("\n" + "="*60)
    print(title)
    print("="*60)


def test_auth_api():
    """测试认证 API"""
    print_separator("认证 API 测试")
    
    # 1. 登录测试（管理员）
    print("\n【测试 1】管理员登录")
    login_data = {
        "username": "admin",
        "password": "123"
    }
    response = requests.post(f'{BASE_URL}/api/auth/login', json=login_data)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data['success']}")
        if data['success']:
            admin_token = data['data']['token']
            print(f"Token 获取成功")
            return admin_token
    return None


def test_customers_api(admin_token):
    """测试客户管理 API"""
    print_separator("客户管理 API 测试")
    
    # 1. 获取客户列表
    print("\n【测试 1】获取客户列表")
    response = requests.get(f'{BASE_URL}/api/customers')
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data['success']}, 客户数: {data['total']}")
    
    # 2. 添加客户
    print("\n【测试 2】添加客户")
    new_customer = {
        "name": "测试客户",
        "phone": "13800138001",
        "email": "test@example.com",
        "address": "测试地址"
    }
    response = requests.post(f'{BASE_URL}/api/customers', json=new_customer)
    print(f"状态码: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"成功: {data['success']}")
        if data['success']:
            customer_id = data['data']['customer_id']
            print(f"客户ID: {customer_id}")
            
            # 3. 更新客户
            print(f"\n【测试 3】更新客户信息")
            update_data = {
                "name": "测试客户(已更新)",
                "address": "新地址"
            }
            response = requests.put(f'{BASE_URL}/api/customers/{customer_id}', json=update_data)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                print("成功更新")
            
            # 4. 获取客户详情
            print(f"\n【测试 4】获取客户详情")
            response = requests.get(f'{BASE_URL}/api/customers/{customer_id}')
            print(f"状态码: {response.status_code}")
            
            # 5. 获取客户订单
            print(f"\n【测试 5】获取客户购买历史")
            response = requests.get(f'{BASE_URL}/api/customers/{customer_id}/orders')
            print(f"状态码: {response.status_code}")


def test_employees_api(admin_token):
    """测试员工管理 API（需要管理员权限）"""
    print_separator("员工管理 API 测试（管理员）")
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    # 1. 获取员工列表
    print("\n【测试 1】获取员工列表")
    response = requests.get(f'{BASE_URL}/api/employees', headers=headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data['success']}, 员工数: {data['total']}")
    
    # 2. 添加员工
    print("\n【测试 2】添加员工")
    new_employee = {
        "username": "test_employee",
        "password": "123456",
        "role": "cashier",
        "status": 1
    }
    response = requests.post(f'{BASE_URL}/api/employees', json=new_employee, headers=headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"成功: {data['success']}")
        if data['success']:
            user_id = data['data']['user_id']
            print(f"员工ID: {user_id}")
            
            # 3. 更新员工角色
            print(f"\n【测试 3】更新员工角色")
            update_data = {
                "role": "purchaser"
            }
            response = requests.put(f'{BASE_URL}/api/employees/{user_id}', json=update_data, headers=headers)
            print(f"状态码: {response.status_code}")
            
            # 4. 重置密码
            print(f"\n【测试 4】重置密码")
            reset_data = {
                "new_password": "654321"
            }
            response = requests.post(f'{BASE_URL}/api/employees/{user_id}/reset-password', 
                                    json=reset_data, headers=headers)
            print(f"状态码: {response.status_code}")
            
            # 5. 删除员工
            print(f"\n【测试 5】删除员工")
            response = requests.delete(f'{BASE_URL}/api/employees/{user_id}', headers=headers)
            print(f"状态码: {response.status_code}")


def main():
    print("\n" + "="*60)
    print("家电超市管理系统 - 客户、员工和认证 API 测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 测试认证 API
        admin_token = test_auth_api()
        
        # 测试客户管理 API
        test_customers_api(admin_token)
        
        # 测试员工管理 API（需要管理员权限）
        if admin_token:
            test_employees_api(admin_token)
        
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
