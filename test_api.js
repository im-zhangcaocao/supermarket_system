/**
 * 系统联调测试脚本
 * 
 * 使用方法：
 * 1. 确保后端服务运行在 http://localhost:5000
 * 2. 运行：node test_api.js
 */

const axios = require('axios');

const API_BASE_URL = 'http://localhost:5000/api';
let token = null;
let userId = null;

async function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function test(description, fn) {
  try {
    await fn();
    console.log(`✅ ${description}`);
    return { success: true };
  } catch (error) {
    console.log(`❌ ${description}`);
    console.log(`   错误: ${error.message}`);
    return { success: false, error: error.message };
  }
}

async function login(username, password) {
  const response = await axios.post(`${API_BASE_URL}/auth/login`, { username, password });
  token = response.data.data.token;
  userId = response.data.data.user.user_id;
  return response.data;
}

async function getWithAuth(url) {
  return axios.get(`${API_BASE_URL}${url}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
}

async function postWithAuth(url, data) {
  return axios.post(`${API_BASE_URL}${url}`, data, {
    headers: { Authorization: `Bearer ${token}` }
  });
}

async function runTests() {
  console.log('='.repeat(60));
  console.log('系统联调测试开始');
  console.log('='.repeat(60));
  
  let passed = 0;
  let failed = 0;
  const results = [];
  
  console.log('\n--- 1. 用户认证测试 ---');
  
  const loginResult = await test('管理员登录', async () => {
    const result = await login('admin', '123');
    if (!result.data.token) throw new Error('登录失败');
  });
  results.push({ test: '管理员登录', ...loginResult });
  loginResult.success ? passed++ : failed++;
  
  if (token) {
    console.log('\n--- 2. 产品管理测试 ---');
    
    const productsResult = await test('获取产品列表', async () => {
      const response = await axios.get(`${API_BASE_URL}/products`);
      if (!response.data.data || !Array.isArray(response.data.data)) {
        throw new Error('产品列表获取失败');
      }
    });
    results.push({ test: '获取产品列表', ...productsResult });
    productsResult.success ? passed++ : failed++;
    
    const addProductResult = await test('添加产品', async () => {
      const response = await axios.post(`${API_BASE_URL}/products`, {
        product_name: '测试产品',
        brand: '测试品牌',
        category: '其他',
        retail_price: 100.00,
        current_stock: 10,
        threshold: 5
      });
      if (!response.data.data) throw new Error('产品添加失败');
    });
    results.push({ test: '添加产品', ...addProductResult });
    addProductResult.success ? passed++ : failed++;
    
    console.log('\n--- 3. 库存管理测试 ---');
    
    const stockResult = await test('查询库存', async () => {
      const response = await axios.get(`${API_BASE_URL}/stock/1`);
      if (!response.data.data) throw new Error('库存查询失败');
    });
    results.push({ test: '查询库存', ...stockResult });
    stockResult.success ? passed++ : failed++;
    
    const alertResult = await test('获取低库存预警', async () => {
      const response = await axios.get(`${API_BASE_URL}/stock/alerts`);
      if (!response.data.data) throw new Error('预警获取失败');
    });
    results.push({ test: '获取低库存预警', ...alertResult });
    alertResult.success ? passed++ : failed++;
    
    console.log('\n--- 4. 客户管理测试 ---');
    
    const customersResult = await test('获取客户列表', async () => {
      const response = await axios.get(`${API_BASE_URL}/customers`);
      if (!response.data.data || !Array.isArray(response.data.data)) {
        throw new Error('客户列表获取失败');
      }
    });
    results.push({ test: '获取客户列表', ...customersResult });
    customersResult.success ? passed++ : failed++;
    
    const addCustomerResult = await test('添加客户', async () => {
      const response = await axios.post(`${API_BASE_URL}/customers`, {
        name: '测试客户',
        phone: '13900139000'
      });
      if (!response.data.data) throw new Error('客户添加失败');
    });
    results.push({ test: '添加客户', ...addCustomerResult });
    addCustomerResult.success ? passed++ : failed++;
    
    console.log('\n--- 5. 供应商管理测试 ---');
    
    const suppliersResult = await test('获取供应商列表', async () => {
      const response = await axios.get(`${API_BASE_URL}/suppliers`);
      if (!response.data.data || !Array.isArray(response.data.data)) {
        throw new Error('供应商列表获取失败');
      }
    });
    results.push({ test: '获取供应商列表', ...suppliersResult });
    suppliersResult.success ? passed++ : failed++;
    
    console.log('\n--- 6. 销售订单测试 ---');
    
    const salesOrdersResult = await test('获取销售订单列表', async () => {
      const response = await axios.get(`${API_BASE_URL}/sales/orders`);
      if (!response.data.data) throw new Error('订单列表获取失败');
    });
    results.push({ test: '获取销售订单列表', ...salesOrdersResult });
    salesOrdersResult.success ? passed++ : failed++;
    
    console.log('\n--- 7. 采购订单测试 ---');
    
    const purchaseOrdersResult = await test('获取采购订单列表', async () => {
      const response = await axios.get(`${API_BASE_URL}/purchase/orders`);
      if (!response.data.data) throw new Error('采购订单列表获取失败');
    });
    results.push({ test: '获取采购订单列表', ...purchaseOrdersResult });
    purchaseOrdersResult.success ? passed++ : failed++;
    
    const overdueResult = await test('获取超期订单', async () => {
      const response = await axios.get(`${API_BASE_URL}/purchase/overdue`);
      if (!response.data.data) throw new Error('超期订单获取失败');
    });
    results.push({ test: '获取超期订单', ...overdueResult });
    overdueResult.success ? passed++ : failed++;
    
    console.log('\n--- 8. 财务管理测试 ---');
    
    const financeRecordsResult = await test('获取财务流水', async () => {
      const response = await axios.get(`${API_BASE_URL}/finance/records`);
      if (!response.data.data) throw new Error('财务流水获取失败');
    });
    results.push({ test: '获取财务流水', ...financeRecordsResult });
    financeRecordsResult.success ? passed++ : failed++;
    
    const financeSummaryResult = await test('获取财务汇总', async () => {
      const response = await axios.get(`${API_BASE_URL}/finance/summary`);
      if (!response.data.data) throw new Error('财务汇总获取失败');
    });
    results.push({ test: '获取财务汇总', ...financeSummaryResult });
    financeSummaryResult.success ? passed++ : failed++;
    
    console.log('\n--- 9. 报表测试 ---');
    
    const salesTrendResult = await test('获取销售趋势', async () => {
      const today = new Date().toISOString().split('T')[0];
      const response = await axios.get(`${API_BASE_URL}/reports/sales-trend`, {
        params: { start_date: today, end_date: today }
      });
      if (!response.data.data) throw new Error('销售趋势获取失败');
    });
    results.push({ test: '获取销售趋势', ...salesTrendResult });
    salesTrendResult.success ? passed++ : failed++;
    
    const dashboardResult = await test('获取仪表盘统计', async () => {
      const response = await axios.get(`${API_BASE_URL}/dashboard/stats`);
      if (!response.data.data) throw new Error('仪表盘统计获取失败');
    });
    results.push({ test: '获取仪表盘统计', ...dashboardResult });
    dashboardResult.success ? passed++ : failed++;
    
    console.log('\n--- 10. 员工管理测试（管理员权限）---');
    
    const employeesResult = await test('获取员工列表（管理员）', async () => {
      const response = await getWithAuth('/employees');
      if (!response.data.data || !Array.isArray(response.data.data)) {
        throw new Error('员工列表获取失败');
      }
    });
    results.push({ test: '获取员工列表（管理员）', ...employeesResult });
    employeesResult.success ? passed++ : failed++;
  }
  
  console.log('\n' + '='.repeat(60));
  console.log('测试结果汇总');
  console.log('='.repeat(60));
  console.log(`通过: ${passed}`);
  console.log(`失败: ${failed}`);
  console.log(`通过率: ${((passed / (passed + failed)) * 100).toFixed(2)}%`);
  
  if (failed > 0) {
    console.log('\n失败的测试项:');
    results.filter(r => !r.success).forEach(r => {
      console.log(`  - ${r.test}: ${r.error}`);
    });
    process.exit(1);
  } else {
    console.log('\n🎉 所有测试通过！');
  }
}

runTests();