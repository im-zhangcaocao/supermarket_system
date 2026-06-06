"""
财务管理 API 测试脚本
"""
import requests
import json
from datetime import datetime, date

BASE_URL = 'http://127.0.0.1:5000'


def print_separator(title):
    print("\n" + "="*60)
    print(title)
    print("="*60)


def test_finance_api():
    """测试财务管理 API"""
    print_separator("财务管理 API 测试")
    
    # 1. 获取财务流水
    print("\n【测试 1】获取财务流水")
    response = requests.get(f'{BASE_URL}/api/finance/records')
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data['success']}, 记录数: {data['total']}")
    
    # 2. 获取财务汇总
    print("\n【测试 2】获取财务汇总")
    response = requests.get(f'{BASE_URL}/api/finance/summary')
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data['success']}")
        if data['success']:
            print(f"销售收入: {data['data']['sales_income']}")
            print(f"采购支出: {data['data']['purchase_expense']}")
            print(f"其他支出: {data['data']['other_expense']}")
            print(f"退货退款: {data['data']['return_refund']}")
            print(f"实际收入: {data['data']['total_income']}")
            print(f"总支出: {data['data']['total_expense']}")
            print(f"净利润: {data['data']['profit']}")
            print(f"毛利率: {data['data']['gross_profit_margin']}%")
            print(f"\n计算公式:")
            print(f"  总收入 = {data['formula']['total_income']}")
            print(f"  总支出 = {data['formula']['total_expense']}")
            print(f"  利润 = {data['formula']['profit']}")
    
    # 3. 获取利润
    print("\n【测试 3】获取利润数值")
    response = requests.get(f'{BASE_URL}/api/finance/profit')
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data['success']}")
        if data['success']:
            print(f"净利润: {data['data']['profit']}")
            print(f"计算公式: {data['formula']}")
    
    # 4. 录入其他支出
    print("\n【测试 4】录入其他支出")
    expense_data = {
        "category": "水电费",
        "amount": 500.00,
        "note": "2024年6月水电费",
        "date": date.today().strftime('%Y-%m-%d')
    }
    response = requests.post(f'{BASE_URL}/api/finance/other-expense', json=expense_data)
    print(f"状态码: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"成功: {data['success']}, 消息: {data['message']}")
    
    # 5. 获取每日汇总
    print("\n【测试 5】获取每日财务汇总")
    response = requests.get(f'{BASE_URL}/api/finance/daily-summary')
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data['success']}, 天数: {data['total_days']}")
    
    # 6. 获取类别统计
    print("\n【测试 6】获取类别统计")
    response = requests.get(f'{BASE_URL}/api/finance/category-summary')
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data['success']}, 类别数: {data['total_categories']}")
    
    # 7. 按类型筛选财务流水
    print("\n【测试 7】按类型筛选财务流水（销售收入）")
    response = requests.get(f'{BASE_URL}/api/finance/records?type=1')
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data['success']}, 销售记录数: {data['total']}")


def main():
    print("\n" + "="*60)
    print("家电超市管理系统 - 财务管理 API 测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        test_finance_api()
        
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
