/**
 * 数据库重置脚本
 * 用于清理现有数据并重新初始化新的模拟数据
 */

import mockData from '../src/api/newMockData.js';

const DB_KEY = 'supermarket_db';
const DB_BACKUP_KEY = 'supermarket_db_backup';
const DB_VERSION_KEY = 'supermarket_db_version';

/**
 * 清理所有数据库数据
 */
function clearAllData() {
  console.log('开始清理数据库...');
  
  // 删除主数据库
  localStorage.removeItem(DB_KEY);
  console.log('✓ 删除主数据库');
  
  // 删除备份
  localStorage.removeItem(DB_BACKUP_KEY);
  console.log('✓ 删除备份');
  
  // 删除版本信息
  localStorage.removeItem(DB_VERSION_KEY);
  console.log('✓ 删除版本信息');
  
  console.log('数据库清理完成！');
}

/**
 * 初始化新的模拟数据
 */
function initializeNewData() {
  console.log('开始初始化新数据...');
  
  const db = {
    version: 1,
    ...mockData
  };
  
  localStorage.setItem(DB_KEY, JSON.stringify(db));
  localStorage.setItem(DB_VERSION_KEY, '1');
  
  console.log('✓ 初始化完成');
}

/**
 * 验证数据完整性
 */
function validateData() {
  console.log('开始验证数据...');
  
  const data = localStorage.getItem(DB_KEY);
  if (!data) {
    console.error('✗ 数据库为空');
    return false;
  }
  
  let db;
  try {
    db = JSON.parse(data);
  } catch (e) {
    console.error('✗ 数据库解析失败:', e);
    return false;
  }
  
  const expectedTables = [
    'users', 'customers', 'products', 'suppliers', 
    'sales_orders', 'sales_order_items', 
    'purchase_orders', 'purchase_order_items',
    'inventory_logs', 'financial_records', 
    'product_edit_logs', 'operation_logs'
  ];
  
  let allValid = true;
  
  expectedTables.forEach(tableName => {
    if (!db[tableName]) {
      console.error(`✗ 缺少表: ${tableName}`);
      allValid = false;
    } else if (!Array.isArray(db[tableName])) {
      console.error(`✗ 表 ${tableName} 不是数组`);
      allValid = false;
    } else if (db[tableName].length !== 10) {
      console.warn(`⚠ 表 ${tableName} 记录数: ${db[tableName].length} (期望: 10)`);
    } else {
      console.log(`✓ 表 ${tableName}: ${db[tableName].length} 条记录`);
    }
  });
  
  // 验证数据关系
  console.log('\n验证数据关系...');
  
  // 验证销售订单与客户的关系
  const invalidOrders = db.sales_orders.filter(order => 
    !db.customers.some(c => c.customer_id === order.customer_id)
  );
  if (invalidOrders.length > 0) {
    console.error(`✗ 存在无效客户ID的订单: ${invalidOrders.length} 条`);
    allValid = false;
  } else {
    console.log('✓ 销售订单与客户关系验证通过');
  }
  
  // 验证订单明细与订单的关系
  const invalidOrderItems = db.sales_order_items.filter(item => 
    !db.sales_orders.some(o => o.order_id === item.order_id)
  );
  if (invalidOrderItems.length > 0) {
    console.error(`✗ 存在无效订单ID的明细: ${invalidOrderItems.length} 条`);
    allValid = false;
  } else {
    console.log('✓ 订单明细与订单关系验证通过');
  }
  
  // 验证订单明细与商品的关系
  const invalidProductItems = db.sales_order_items.filter(item => 
    !db.products.some(p => p.product_id === item.product_id)
  );
  if (invalidProductItems.length > 0) {
    console.error(`✗ 存在无效商品ID的明细: ${invalidProductItems.length} 条`);
    allValid = false;
  } else {
    console.log('✓ 订单明细与商品关系验证通过');
  }
  
  // 验证采购订单与供应商的关系
  const invalidPurchaseOrders = db.purchase_orders.filter(order => 
    !db.suppliers.some(s => s.supplier_id === order.supplier_id)
  );
  if (invalidPurchaseOrders.length > 0) {
    console.error(`✗ 存在无效供应商ID的采购订单: ${invalidPurchaseOrders.length} 条`);
    allValid = false;
  } else {
    console.log('✓ 采购订单与供应商关系验证通过');
  }
  
  if (allValid) {
    console.log('\n✓✓✓ 所有数据验证通过！');
  } else {
    console.log('\n✗✗✗ 数据验证失败！');
  }
  
  return allValid;
}

/**
 * 显示数据统计
 */
function showStatistics() {
  console.log('\n=== 数据统计 ===');
  
  const data = localStorage.getItem(DB_KEY);
  const db = JSON.parse(data);
  
  const totalRecords = Object.keys(db).reduce((sum, key) => {
    if (Array.isArray(db[key])) {
      return sum + db[key].length;
    }
    return sum;
  }, 0);
  
  console.log(`数据库版本: ${db.version}`);
  console.log(`数据表数量: ${Object.keys(db).filter(k => Array.isArray(db[k])).length}`);
  console.log(`总记录数: ${totalRecords}`);
  console.log(`数据大小: ${(JSON.stringify(db).length / 1024).toFixed(2)} KB`);
  
  console.log('\n各表记录数:');
  Object.keys(db).filter(k => Array.isArray(db[k])).forEach(key => {
    console.log(`  - ${key}: ${db[key].length} 条`);
  });
}

/**
 * 执行完整的数据库重置
 */
function resetDatabase() {
  console.log('\n========================================');
  console.log('   数据库重置脚本');
  console.log('========================================\n');
  
  // 步骤1: 清理数据
  clearAllData();
  
  // 步骤2: 初始化新数据
  initializeNewData();
  
  // 步骤3: 验证数据
  const isValid = validateData();
  
  // 步骤4: 显示统计
  showStatistics();
  
  if (isValid) {
    console.log('\n✅ 数据库重置成功！');
    return true;
  } else {
    console.log('\n❌ 数据库重置失败！');
    return false;
  }
}

// 如果在浏览器环境中运行
if (typeof window !== 'undefined') {
  // 提供给页面调用
  window.resetDatabase = resetDatabase;
  console.log('数据库重置脚本已加载');
}

// 如果在Node.js环境中运行
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    resetDatabase,
    clearAllData,
    initializeNewData,
    validateData,
    showStatistics
  };
}
