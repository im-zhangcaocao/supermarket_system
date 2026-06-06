/**
 * 数据迁移脚本 - 将 localStorage 数据迁移到后端 SQLite 数据库
 * 
 * 使用方法：
 * 1. 确保后端服务运行在 http://localhost:5000
 * 2. 导出 localStorage 数据为 JSON 文件（命名为 localStorage_data.json）
 * 3. 运行：node migrate.js
 */

const fs = require('fs');
const path = require('path');
const axios = require('axios');

const API_BASE_URL = 'http://localhost:5000/api';
const INPUT_FILE = 'localStorage_data.json';
const BACKUP_FILE = `backup_${Date.now()}.json`;
const FAILED_FILE = `failed_records_${Date.now()}.json`;
const LOG_FILE = `migration_log_${Date.now()}.log`;

const BATCH_SIZE = 50;
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

let migrationLog = [];
let totalSuccess = 0;
let totalFailed = 0;
let failedRecords = [];

async function log(message, type = 'info') {
  const timestamp = new Date().toISOString();
  const logEntry = `[${timestamp}] [${type.toUpperCase()}] ${message}`;
  console.log(logEntry);
  migrationLog.push(logEntry);
}

async function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function makeRequest(method, url, data = null, retries = 0) {
  try {
    const config = {
      method,
      url: `${API_BASE_URL}${url}`,
      data,
      timeout: 10000
    };
    
    const response = await axios(config);
    return { success: true, data: response.data };
  } catch (error) {
    if (retries < MAX_RETRIES) {
      await delay(RETRY_DELAY * (retries + 1));
      return makeRequest(method, url, data, retries + 1);
    }
    return { 
      success: false, 
      error: error.response?.data?.error || error.message 
    };
  }
}

async function backupData(data) {
  fs.writeFileSync(BACKUP_FILE, JSON.stringify(data, null, 2));
  log(`数据备份完成: ${BACKUP_FILE}`);
}

function validateData(data) {
  const requiredTables = ['users', 'products', 'suppliers', 'customers'];
  let valid = true;
  
  requiredTables.forEach(table => {
    if (!data[table] || !Array.isArray(data[table])) {
      log(`数据验证失败：缺少或格式错误的 ${table} 表`, 'error');
      valid = false;
    }
  });
  
  return valid;
}

async function migrateUsers(users) {
  log(`开始迁移用户数据，共 ${users.length} 条记录`);
  
  for (const user of users) {
    const result = await makeRequest('POST', '/employees', {
      username: user.username,
      password: user.password,
      role: user.role,
      status: user.status || 1
    });
    
    if (result.success) {
      totalSuccess++;
      log(`用户 ${user.username} 迁移成功`);
    } else {
      totalFailed++;
      failedRecords.push({ table: 'users', record: user, error: result.error });
      log(`用户 ${user.username} 迁移失败: ${result.error}`, 'error');
    }
  }
}

async function migrateProducts(products) {
  log(`开始迁移产品数据，共 ${products.length} 条记录`);
  
  for (const product of products) {
    const result = await makeRequest('POST', '/products', {
      product_name: product.product_name,
      brand: product.brand,
      model: product.model,
      category: product.category,
      retail_price: product.retail_price,
      purchase_ref_price: product.purchase_ref_price,
      current_stock: product.current_stock,
      threshold: product.threshold,
      status: product.status
    });
    
    if (result.success) {
      totalSuccess++;
      log(`产品 ${product.product_name} 迁移成功`);
    } else {
      totalFailed++;
      failedRecords.push({ table: 'products', record: product, error: result.error });
      log(`产品 ${product.product_name} 迁移失败: ${result.error}`, 'error');
    }
  }
}

async function migrateSuppliers(suppliers) {
  log(`开始迁移供应商数据，共 ${suppliers.length} 条记录`);
  
  for (const supplier of suppliers) {
    const result = await makeRequest('POST', '/suppliers', {
      supplier_name: supplier.supplier_name,
      contact_name: supplier.contact_name,
      phone: supplier.phone,
      address: supplier.address,
      on_time_rate: supplier.on_time_rate || 0,
      average_delivery_days: supplier.average_delivery_days || 7
    });
    
    if (result.success) {
      totalSuccess++;
      log(`供应商 ${supplier.supplier_name} 迁移成功`);
    } else {
      totalFailed++;
      failedRecords.push({ table: 'suppliers', record: supplier, error: result.error });
      log(`供应商 ${supplier.supplier_name} 迁移失败: ${result.error}`, 'error');
    }
  }
}

async function migrateCustomers(customers) {
  log(`开始迁移客户数据，共 ${customers.length} 条记录`);
  
  for (const customer of customers) {
    const result = await makeRequest('POST', '/customers', {
      name: customer.name || '',
      phone: customer.phone,
      email: customer.email || '',
      address: customer.address || ''
    });
    
    if (result.success) {
      totalSuccess++;
      log(`客户 ${customer.name || customer.phone} 迁移成功`);
    } else {
      totalFailed++;
      failedRecords.push({ table: 'customers', record: customer, error: result.error });
      log(`客户 ${customer.name || customer.phone} 迁移失败: ${result.error}`, 'error');
    }
  }
}

async function migrateSalesOrders(salesOrders, salesOrderItems) {
  log(`开始迁移销售订单数据，共 ${salesOrders.length} 条记录`);
  
  for (const order of salesOrders) {
    const items = salesOrderItems.filter(item => item.order_id === order.order_id);
    
    const orderItems = items.map(item => ({
      product_id: item.product_id,
      quantity: item.quantity,
      unit_price: item.unit_price
    }));
    
    const result = await makeRequest('POST', '/sales/orders', {
      customer_id: order.customer_id || null,
      items: orderItems,
      payment_method: order.payment_method,
      shipping_address: order.shipping_address || '',
      discount_amount: order.discount_amount || 0,
      earned_points: order.earned_points || 0,
      used_points: order.used_points || 0,
      final_amount: order.final_amount || order.total_amount
    });
    
    if (result.success) {
      totalSuccess++;
      log(`销售订单 ${order.order_id} 迁移成功`);
      
      if (order.payment_status === 1) {
        const payResult = await makeRequest('POST', `/sales/orders/${result.data.order_id || order.order_id}/pay`, { operator: 'migration' });
        if (payResult.success) {
          log(`销售订单 ${order.order_id} 支付状态同步成功`);
        } else {
          log(`销售订单 ${order.order_id} 支付状态同步失败: ${payResult.error}`, 'warning');
        }
      }
    } else {
      totalFailed++;
      failedRecords.push({ table: 'sales_orders', record: order, error: result.error });
      log(`销售订单 ${order.order_id} 迁移失败: ${result.error}`, 'error');
    }
  }
}

async function migratePurchaseOrders(purchaseOrders, purchaseOrderItems) {
  log(`开始迁移采购订单数据，共 ${purchaseOrders.length} 条记录`);
  
  for (const order of purchaseOrders) {
    const items = purchaseOrderItems.filter(item => item.purchase_order_id === order.purchase_order_id);
    
    const orderItems = items.map(item => ({
      product_id: item.product_id,
      quantity: item.quantity,
      unit_price: item.unit_price
    }));
    
    const result = await makeRequest('POST', '/purchase/orders', {
      supplier_id: order.supplier_id,
      items: orderItems,
      expected_date: order.expected_date
    });
    
    if (result.success) {
      totalSuccess++;
      log(`采购订单 ${order.purchase_order_id} 迁移成功`);
      
      if (order.status === 2) {
        const receiptItems = items.map(item => ({
          product_id: item.product_id,
          received_quantity: item.received_qty || item.quantity
        }));
        
        const receiptResult = await makeRequest('POST', `/purchase/orders/${result.data.purchase_order_id || order.purchase_order_id}/receipt`, { items: receiptItems });
        if (receiptResult.success) {
          log(`采购订单 ${order.purchase_order_id} 收货状态同步成功`);
        } else {
          log(`采购订单 ${order.purchase_order_id} 收货状态同步失败: ${receiptResult.error}`, 'warning');
        }
      }
    } else {
      totalFailed++;
      failedRecords.push({ table: 'purchase_orders', record: order, error: result.error });
      log(`采购订单 ${order.purchase_order_id} 迁移失败: ${result.error}`, 'error');
    }
  }
}

async function migrateFinancialRecords(financialRecords) {
  log(`开始迁移财务记录数据，共 ${financialRecords.length} 条记录`);
  
  for (const record of financialRecords) {
    if (record.type === 3 || record.type === 2) {
      const result = await makeRequest('POST', '/finance/other-expense', {
        category: record.remark || '其他支出',
        amount: record.amount,
        date: record.occur_time?.split(' ')[0] || new Date().toISOString().split('T')[0],
        note: record.remark || ''
      });
      
      if (result.success) {
        totalSuccess++;
      } else {
        totalFailed++;
        failedRecords.push({ table: 'financial_records', record, error: result.error });
        log(`财务记录迁移失败: ${result.error}`, 'error');
      }
    }
  }
  
  log('财务记录迁移完成（仅迁移其他支出类型，销售和采购记录由订单同步时自动生成）');
}

async function generateReport() {
  const report = `
========================================
          数据迁移报告
========================================
迁移时间: ${new Date().toISOString()}

【迁移统计】
总记录数: ${totalSuccess + totalFailed}
成功数: ${totalSuccess}
失败数: ${totalFailed}
成功率: ${((totalSuccess / (totalSuccess + totalFailed)) * 100).toFixed(2)}%

【失败记录统计】
${failedRecords.length > 0 ? `共 ${failedRecords.length} 条失败记录` : '无失败记录'}

【详细日志】
${migrationLog.join('\n')}
`;

  fs.writeFileSync(LOG_FILE, report);
  console.log(`\n${report}`);
  console.log(`迁移日志已保存到: ${LOG_FILE}`);
  
  if (failedRecords.length > 0) {
    fs.writeFileSync(FAILED_FILE, JSON.stringify(failedRecords, null, 2));
    console.log(`失败记录已保存到: ${FAILED_FILE}`);
  }
}

async function main() {
  try {
    log('数据迁移脚本开始执行');
    
    if (!fs.existsSync(INPUT_FILE)) {
      log(`错误：未找到输入文件 ${INPUT_FILE}`, 'error');
      process.exit(1);
    }
    
    const rawData = fs.readFileSync(INPUT_FILE, 'utf-8');
    const data = JSON.parse(rawData);
    
    log(`成功读取数据文件，包含 ${Object.keys(data).length} 个数据表`);
    
    backupData(data);
    
    if (!validateData(data)) {
      log('数据验证失败', 'error');
      process.exit(1);
    }
    
    log('数据验证通过，开始迁移...');
    
    await migrateUsers(data.users || []);
    await delay(500);
    
    await migrateProducts(data.products || []);
    await delay(500);
    
    await migrateSuppliers(data.suppliers || []);
    await delay(500);
    
    await migrateCustomers(data.customers || []);
    await delay(500);
    
    await migrateSalesOrders(data.sales_orders || [], data.sales_order_items || []);
    await delay(500);
    
    await migratePurchaseOrders(data.purchase_orders || [], data.purchase_order_items || []);
    await delay(500);
    
    await migrateFinancialRecords(data.financial_records || []);
    
    await generateReport();
    
    log('数据迁移脚本执行完成');
    
  } catch (error) {
    log(`迁移过程发生错误: ${error.message}`, 'error');
    await generateReport();
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = {
  main,
  makeRequest,
  validateData
};