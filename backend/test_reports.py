"""
报表和仪表盘 API 测试脚本
"""
import requests
import json
from datetime import datetime, date, timedelta

BASE_URL = 'http://127.0.0.1:5000'


def print_separator(title):
    print("\n" + "="*60)
    print(title)
    print("="*60)


def test_reports_api():
    """测试报表 API"""
    print_separator("报表 API 测试")
    
    # 1. 销售趋势
    print("\n【测试 1】销售趋势（按天）")
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    response = requests.get(f'{BASE_URL}/api/reports/sales-trend', params={
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'group_by': 'day'
    })
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data['success']}")
        if data['success']:
            print(f"日期数量: {len(data['data']['dates'])}")
            print(f"金额总和: {sum(data['data']['amounts'])}")
    
    # 2. 类别销售占比
    print("\n【测试 2】类别销售占比")
    response = requests.get(f'{BASE_URL}/api/reports/category-sales')
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data['success']}")
        if data['success']:
            print(f"品类数量: {len(data['data'])}")
            print(f"总销售额: {data['total_sales']}")
            for item in data['data'][:3]:
                print(f"  - {item['category']}: {item['total_amount']} ({item['percentage']}%)")
    
    # 3. 供应商采购排名
    print("\n【测试 3】供应商采购排名")
    response = requests.get(f'{BASE_URL}/api/reports/supplier-ranking', params={'limit': 5})
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data['success']}")
        if data['success']:
            print(f"供应商数量: {len(data['data'])}")
            for item in data['data']:
                print(f"  {item['rank']}. {item['supplier']}: {item['total_purchase']}")
    
    # 4. 库存变化趋势
    print("\n【测试 4】库存变化趋势")
    response = requests.get(f'{BASE_URL}/api/reports/inventory-trend', params={
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d')
    })
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data['success']}")
        if data['success']:
            print(f"入库总数: {sum(data['data']['in_stock'])}")
            print(f"出库总数: {sum(data['data']['out_stock'])}")


def test_dashboard_api():
    """测试仪表盘 API"""
    print_separator("仪表盘 API 测试")
    
    # 1. 统计数据
    print("\n【测试 1】仪表盘统计数据")
    response = requests.get(f'{BASE_URL}/api/dashboard/stats')
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data['success']}")
        if data['success']:
            print(f"今日销售: {data['data']['today_sales']}")
            print(f"低库存产品数: {data['data']['low_stock_count']}")
            print(f"本月采购订单: {data['data']['monthly_purchase_orders']}")
            print(f"本月净利润: {data['data']['monthly_profit']}")
            print(f"更新时间: {data['data']['update_time']}")
    
    # 2. 快速统计
    print("\n【测试 2】快速统计")
    response = requests.get(f'{BASE_URL}/api/dashboard/quick-stats')
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"成功: {data['success']}")
        if data['success']:
            print(f"产品总数: {data['data']['product_count']}")
            print(f"供应商总数: {data['data']['supplier_count']}")
            print(f"客户总数: {data['data']['customer_count']}")
            print(f"今日订单数: {data['data']['today_orders']}")


def main():
    print("\n" + "="*60)
    print("家电超市管理系统 - 报表和仪表盘 API 测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        test_reports_api()
        test_dashboard_api()
        
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
