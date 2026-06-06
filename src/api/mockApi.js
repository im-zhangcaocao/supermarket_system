import {
  getDB,
  saveDB,
  getTable,
  saveTable,
  updateRecord,
  addRecord,
  deleteRecord,
  createBackup
} from '../utils/database.js';

function delay(ms = 200) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function generateOrderId(prefix) {
  const now = new Date();
  const dateStr = now.toISOString().slice(0, 10).replace(/-/g, '');
  const orders = getTable(prefix === 'SO' ? 'sales_orders' : 'purchase_orders');
  const todayOrders = orders.filter(o => o.order_id?.startsWith(prefix + dateStr) || o.purchase_order_id?.startsWith(prefix + dateStr));
  const maxSeq = todayOrders.length > 0 
    ? Math.max(...todayOrders.map(o => parseInt((o.order_id || o.purchase_order_id).slice(-4)))) 
    : 0;
  const seq = String(maxSeq + 1).padStart(4, '0');
  return `${prefix}${dateStr}${seq}`;
}

function generateId(tableName, idField) {
  const records = getTable(tableName);
  const maxId = records.length > 0 ? Math.max(...records.map(r => r[idField])) : 0;
  return maxId + 1;
}

function logProductEdit(productId, fieldName, oldValue, newValue, operator) {
  const logs = getTable('product_edit_logs');
  const newLog = {
    log_id: generateId('product_edit_logs', 'log_id'),
    product_id: productId,
    field_name: fieldName,
    old_value: String(oldValue ?? ''),
    new_value: String(newValue ?? ''),
    operator: operator || 'system',
    operate_time: new Date().toISOString().slice(0, 19).replace('T', ' ')
  };
  saveTable('product_edit_logs', [...logs, newLog]);
}

export async function login(username, password) {
  await delay();
  const users = getTable('users');
  const user = users.find(u => u.username === username && u.password === password && u.status === 1);
  if (!user) return null;
  
  const updatedUsers = users.map(u => 
    u.user_id === user.user_id 
      ? { ...u, last_login: new Date().toISOString().slice(0, 19).replace('T', ' ') }
      : u
  );
  saveTable('users', updatedUsers);
  
  return {
    token: 'fake-jwt-token',
    user: { user_id: user.user_id, username: user.username, role: user.role }
  };
}

export async function getUserInfo(userId) {
  await delay();
  const users = getTable('users');
  return users.find(u => u.user_id === userId) || null;
}

export async function updateProfile(userId, data) {
  await delay();
  const users = getTable('users');
  const index = users.findIndex(u => u.user_id === userId);
  if (index === -1) return false;
  
  const updatedUsers = [...users];
  updatedUsers[index] = { ...updatedUsers[index], ...data };
  saveTable('users', updatedUsers);
  return true;
}

export async function getProducts({ category, status } = {}) {
  await delay();
  let products = getTable('products');
  if (category !== undefined) {
    products = products.filter(p => p.category === category);
  }
  if (status !== undefined) {
    products = products.filter(p => p.status === status);
  }
  return products;
}

export async function getProductById(productId) {
  await delay();
  const products = getTable('products');
  return products.find(p => p.product_id === productId) || null;
}

export async function addProduct(productInfo) {
  await delay();
  const products = getTable('products');
  const newId = generateId('products', 'product_id');
  const newProduct = { product_id: newId, ...productInfo, status: productInfo.status ?? 1 };
  products.push(newProduct);
  saveTable('products', products);
  return newId;
}

export async function updateProduct(productId, updateData, operator = 'system') {
  await delay();
  const products = getTable('products');
  const index = products.findIndex(p => p.product_id === productId);
  if (index === -1) return false;
  
  const oldProduct = products[index];
  const updatedProducts = [...products];
  updatedProducts[index] = { ...updatedProducts[index], ...updateData };
  saveTable('products', updatedProducts);
  
  Object.keys(updateData).forEach(field => {
    if (oldProduct[field] !== updateData[field]) {
      logProductEdit(productId, field, oldProduct[field], updateData[field], operator);
    }
  });
  
  return true;
}

export async function disableProduct(productId) {
  await delay();
  return updateProduct(productId, { status: 0 });
}

export async function setThreshold(productId, minStock) {
  await delay();
  return updateProduct(productId, { threshold: minStock });
}

export async function enableProduct(productId) {
  await delay();
  return updateProduct(productId, { status: 1 });
}

export async function deleteProduct(productId) {
  await delay();
  const db = getDB();
  
  const salesItems = db.sales_order_items.filter(item => item.product_id === productId);
  const purchaseItems = db.purchase_order_items.filter(item => item.product_id === productId);
  
  if (salesItems.length > 0 || purchaseItems.length > 0) {
    return { canDelete: false, message: '该产品已有历史交易记录，无法删除，只能设为禁用' };
  }
  
  const products = db.products;
  const index = products.findIndex(p => p.product_id === productId);
  if (index === -1) return false;
  
  db.products.splice(index, 1);
  saveDB(db);
  return { canDelete: true };
}

export async function checkStock(productId) {
  await delay();
  const product = await getProductById(productId);
  return product ? product.current_stock : 0;
}

export async function deductStock(productId, quantity, relateOrderId) {
  await delay();
  const db = getDB();
  
  const productIndex = db.products.findIndex(p => p.product_id === productId);
  if (productIndex === -1 || db.products[productIndex].current_stock < quantity) {
    return false;
  }
  
  const beforeQty = db.products[productIndex].current_stock;
  db.products[productIndex] = {
    ...db.products[productIndex],
    current_stock: beforeQty - quantity
  };
  
  const newLog = {
    log_id: generateId('inventory_logs', 'log_id'),
    product_id: productId,
    relate_order_id: relateOrderId,
    change_type: 1,
    change_qty: -quantity,
    before_quantity: beforeQty,
    after_quantity: beforeQty - quantity,
    operator: 'system',
    operate_time: new Date().toISOString().slice(0, 19).replace('T', ' '),
    remark: '销售出库'
  };
  db.inventory_logs.push(newLog);
  
  saveDB(db);
  return true;
}

export async function addStock(productId, quantity, reason, operatorId, relateOrderId) {
  await delay();
  const db = getDB();
  
  const productIndex = db.products.findIndex(p => p.product_id === productId);
  if (productIndex === -1) return false;
  
  const beforeQty = db.products[productIndex].current_stock;
  db.products[productIndex] = {
    ...db.products[productIndex],
    current_stock: beforeQty + quantity
  };
  
  const changeType = relateOrderId?.startsWith('PO') ? 2 : 3;
  const newLog = {
    log_id: generateId('inventory_logs', 'log_id'),
    product_id: productId,
    relate_order_id: relateOrderId,
    change_type: changeType,
    change_qty: quantity,
    before_quantity: beforeQty,
    after_quantity: beforeQty + quantity,
    operator: operatorId.toString(),
    operate_time: new Date().toISOString().slice(0, 19).replace('T', ' '),
    remark: reason
  };
  db.inventory_logs.push(newLog);
  
  saveDB(db);
  return true;
}

export async function getAlertProducts() {
  await delay();
  const products = getTable('products');
  return products.filter(p => p.current_stock <= p.threshold && p.status === 1);
}

export async function getStockLog(productId, startTime, endTime) {
  await delay();
  let logs = getTable('inventory_logs');
  if (productId) {
    logs = logs.filter(l => l.product_id === productId);
  }
  if (startTime) {
    logs = logs.filter(l => l.operate_time >= startTime);
  }
  if (endTime) {
    logs = logs.filter(l => l.operate_time <= endTime);
  }
  return logs.sort((a, b) => new Date(b.operate_time) - new Date(a.operate_time));
}

export async function manualAdjust(operatorId, productId, delta, reason) {
  await delay();
  if (delta > 0) {
    return addStock(productId, delta, reason || '手动调整入库', operatorId, null);
  } else if (delta < 0) {
    const db = getDB();
    const product = db.products.find(p => p.product_id === productId);
    if (!product || product.current_stock < -delta) return false;
    
    const beforeQty = product.current_stock;
    db.products = db.products.map(p => 
      p.product_id === productId 
        ? { ...p, current_stock: beforeQty + delta }
        : p
    );
    
    const newLog = {
      log_id: generateId('inventory_logs', 'log_id'),
      product_id: productId,
      relate_order_id: null,
      change_type: 3,
      change_qty: delta,
      before_quantity: beforeQty,
      after_quantity: beforeQty + delta,
      operator: operatorId.toString(),
      operate_time: new Date().toISOString().slice(0, 19).replace('T', ' '),
      remark: reason || '手动调整出库'
    };
    db.inventory_logs.push(newLog);
    saveDB(db);
    return true;
  }
  return true;
}

export async function createOrder(customerId, cartItems, paymentMethod, shippingAddress, discountAmount = 0, earnedPoints = 0, usedPoints = 0, finalAmount = 0) {
  await delay();
  const db = getDB();
  
  const orderId = generateOrderId('SO');
  const orderTime = new Date().toISOString().slice(0, 19).replace('T', ' ');
  
  let totalAmount = 0;
  const items = cartItems.map((item, index) => {
    const product = db.products.find(p => p.product_id === item.product_id);
    if (!product) throw new Error(`商品不存在: ${item.product_id}`);
    
    const unitPrice = product.retail_price;
    const costPrice = product.purchase_ref_price;
    totalAmount += unitPrice * item.quantity;
    
    return {
      item_id: generateId('sales_order_items', 'item_id'),
      order_id: orderId,
      product_id: item.product_id,
      quantity: item.quantity,
      unit_price: unitPrice,
      cost_price: costPrice
    };
  });
  
  const order = {
    order_id: orderId,
    customer_id: customerId,
    order_time: orderTime,
    total_amount: totalAmount,
    discount_amount: discountAmount,
    earned_points: earnedPoints,
    used_points: usedPoints,
    final_amount: finalAmount > 0 ? finalAmount : totalAmount,
    payment_method: paymentMethod,
    payment_status: 0,
    shipping_address: shippingAddress
  };
  
  db.sales_orders.push(order);
  db.sales_order_items.push(...items);
  saveDB(db);
  
  return orderId;
}

export async function payOrder(orderId) {
  await delay();
  const db = getDB();
  
  const orderIndex = db.sales_orders.findIndex(o => o.order_id === orderId);
  if (orderIndex === -1) throw new Error('订单不存在');
  if (db.sales_orders[orderIndex].payment_status === 1) throw new Error('订单已支付');
  
  const order = db.sales_orders[orderIndex];
  
  const items = db.sales_order_items.filter(i => i.order_id === orderId);
  
  for (const item of items) {
    const product = db.products.find(p => p.product_id === item.product_id);
    if (!product || product.current_stock < item.quantity) {
      throw new Error(`库存不足: ${product?.product_name || item.product_id}`);
    }
  }
  
  for (const item of items) {
    const productIndex = db.products.findIndex(p => p.product_id === item.product_id);
    const beforeQty = db.products[productIndex].current_stock;
    db.products[productIndex] = {
      ...db.products[productIndex],
      current_stock: beforeQty - item.quantity
    };
    
    db.inventory_logs.push({
      log_id: generateId('inventory_logs', 'log_id'),
      product_id: item.product_id,
      relate_order_id: orderId,
      change_type: 1,
      change_qty: -item.quantity,
      before_quantity: beforeQty,
      after_quantity: beforeQty - item.quantity,
      operator: 'system',
      operate_time: new Date().toISOString().slice(0, 19).replace('T', ' '),
      remark: '销售出库'
    });
  }
  
  db.sales_orders[orderIndex] = {
    ...db.sales_orders[orderIndex],
    payment_status: 1
  };
  
  db.financial_records.push({
    record_id: generateId('financial_records', 'record_id'),
    type: 1,
    amount: order.final_amount || order.total_amount,
    relate_order_id: orderId,
    occur_time: new Date().toISOString().slice(0, 19).replace('T', ' '),
    remark: '销售收款'
  });
  
  if (order.customer_id) {
    const customerIndex = db.customers.findIndex(c => c.customer_id === order.customer_id);
    if (customerIndex !== -1) {
      const customer = db.customers[customerIndex];
      
      let newPoints = (customer.points || 0);
      
      if (order.used_points > 0) {
        newPoints -= order.used_points;
      }
      
      if (order.earned_points > 0) {
        newPoints += order.earned_points;
      }
      
      db.customers[customerIndex] = {
        ...customer,
        points: Math.max(0, newPoints)
      };
    }
  }
  
  saveDB(db);
  return true;
}

export async function getOrderHistory(customerId = null) {
  await delay();
  let orders = getTable('sales_orders');
  if (customerId !== null) {
    orders = orders.filter(o => o.customer_id === customerId);
  }
  return orders.sort((a, b) => new Date(b.order_time) - new Date(a.order_time));
}

export async function getOrderDetail(orderId) {
  await delay();
  const order = getTable('sales_orders').find(o => o.order_id === orderId);
  if (!order) return null;
  
  const items = getTable('sales_order_items').filter(i => i.order_id === orderId);
  const products = getTable('products');
  
  const detailItems = items.map(item => {
    const product = products.find(p => p.product_id === item.product_id);
    return { ...item, product_name: product?.product_name || '' };
  });
  
  return { ...order, items: detailItems };
}

export async function getCustomers() {
  await delay();
  return getTable('customers');
}

export async function addCustomer(customerInfo) {
  await delay();
  const customers = getTable('customers');
  const newId = generateId('customers', 'customer_id');
  
  const registerDate = new Date();
  const expiryDate = new Date();
  expiryDate.setFullYear(expiryDate.getFullYear() + 1);
  
  const newCustomer = { 
    customer_id: newId, 
    name: customerInfo.name,
    phone: customerInfo.phone || '',
    email: customerInfo.email || '',
    address: customerInfo.address || '',
    register_time: registerDate.toISOString().slice(0, 10),
    membership_level: customerInfo.membership_level || '普通会员',
    discount_rate: customerInfo.discount_rate || 1.0,
    points: customerInfo.points || 0,
    points_expiry_date: expiryDate.toISOString().slice(0, 10)
  };
  customers.push(newCustomer);
  saveTable('customers', customers);
  return newId;
}

export async function updateCustomer(customerId, data) {
  await delay();
  const customers = getTable('customers');
  const index = customers.findIndex(c => c.customer_id === customerId);
  if (index === -1) return false;
  
  customers[index] = { ...customers[index], ...data };
  saveTable('customers', customers);
  return true;
}

export async function deleteCustomer(customerId) {
  await delay();
  const db = getDB();
  
  const hasOrders = db.sales_orders.some(o => o.customer_id === customerId);
  if (hasOrders) {
    return { canDelete: false, message: '该客户有历史订单，无法删除' };
  }
  
  const customers = db.customers;
  const index = customers.findIndex(c => c.customer_id === customerId);
  if (index === -1) return false;
  
  customers.splice(index, 1);
  saveDB(db);
  return { canDelete: true };
}

export async function getAllOrders(filters = {}) {
  await delay();
  let orders = getTable('sales_orders');
  
  if (filters.customerId) {
    orders = orders.filter(o => o.customer_id === filters.customerId);
  }
  if (filters.status !== undefined) {
    orders = orders.filter(o => o.payment_status === filters.status);
  }
  if (filters.startDate) {
    orders = orders.filter(o => o.order_time >= filters.startDate);
  }
  if (filters.endDate) {
    orders = orders.filter(o => o.order_time <= filters.endDate);
  }
  
  return orders.sort((a, b) => new Date(b.order_time) - new Date(a.order_time));
}

// 获取客户购买偏好分析
export async function getCustomerPurchasePreference(customerId) {
  await delay();
  const db = getDB();
  
  // 获取该客户的所有已完成订单
  const customerOrders = db.sales_orders.filter(
    o => o.customer_id === customerId && o.payment_status === 1
  );
  
  if (customerOrders.length === 0) {
    return {
      totalOrders: 0,
      totalAmount: 0,
      categoryPreferences: [],
      brandPreferences: [],
      recentProducts: []
    };
  }
  
  // 获取所有订单项
  const orderIds = customerOrders.map(o => o.order_id);
  const orderItems = db.sales_order_items.filter(item => orderIds.includes(item.order_id));
  
  // 计算总金额
  const totalAmount = customerOrders.reduce((sum, order) => sum + (order.total_amount || 0), 0);
  
  // 按类别统计
  const categoryStats = {};
  const brandStats = {};
  const productStats = {};
  
  orderItems.forEach(item => {
    const product = db.products.find(p => p.product_id === item.product_id);
    if (!product) return;
    
    const quantity = item.quantity || 0;
    const subtotal = item.subtotal || 0;
    
    // 类别统计
    if (!categoryStats[product.category]) {
      categoryStats[product.category] = { count: 0, amount: 0, quantity: 0 };
    }
    categoryStats[product.category].count += 1;
    categoryStats[product.category].amount += subtotal;
    categoryStats[product.category].quantity += quantity;
    
    // 品牌统计
    if (!brandStats[product.brand]) {
      brandStats[product.brand] = { count: 0, amount: 0, quantity: 0 };
    }
    brandStats[product.brand].count += 1;
    brandStats[product.brand].amount += subtotal;
    brandStats[product.brand].quantity += quantity;
    
    // 产品统计
    if (!productStats[product.product_id]) {
      productStats[product.product_id] = {
        product_id: product.product_id,
        product_name: product.product_name,
        brand: product.brand,
        category: product.category,
        count: 0,
        amount: 0,
        quantity: 0
      };
    }
    productStats[product.product_id].count += 1;
    productStats[product.product_id].amount += subtotal;
    productStats[product.product_id].quantity += quantity;
  });
  
  // 转换为数组并排序
  const categoryPreferences = Object.entries(categoryStats)
    .map(([category, stats]) => ({
      category,
      ...stats,
      percentage: totalAmount > 0 ? ((stats.amount / totalAmount) * 100).toFixed(1) : 0
    }))
    .sort((a, b) => b.amount - a.amount);
  
  const brandPreferences = Object.entries(brandStats)
    .map(([brand, stats]) => ({
      brand,
      ...stats,
      percentage: totalAmount > 0 ? ((stats.amount / totalAmount) * 100).toFixed(1) : 0
    }))
    .sort((a, b) => b.amount - a.amount);
  
  const recentProducts = Object.values(productStats)
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 10); // 取前10个最常购买的产品
  
  return {
    totalOrders: customerOrders.length,
    totalAmount: totalAmount,
    categoryPreferences,
    brandPreferences,
    recentProducts
  };
}

export async function getSuppliers() {
  await delay();
  return getTable('suppliers');
}

export async function addSupplier(supplierInfo) {
  await delay();
  const suppliers = getTable('suppliers');
  const newId = generateId('suppliers', 'supplier_id');
  const newSupplier = { supplier_id: newId, ...supplierInfo };
  suppliers.push(newSupplier);
  saveTable('suppliers', suppliers);
  return newId;
}

export async function createPurchaseOrder(purchaserId, supplierId, items, expectedDate) {
  await delay();
  const db = getDB();
  
  const orderId = generateOrderId('PO');
  const createTime = new Date().toISOString().slice(0, 19).replace('T', ' ');
  
  const orderItems = items.map(item => ({
    item_id: generateId('purchase_order_items', 'item_id'),
    purchase_order_id: orderId,
    product_id: item.product_id,
    quantity: item.quantity,
    unit_price: item.unit_price,
    received_qty: 0
  }));
  
  const totalExpectedQty = items.reduce((sum, item) => sum + item.quantity, 0);
  
  const order = {
    purchase_order_id: orderId,
    supplier_id: supplierId,
    create_time: createTime,
    expected_date: expectedDate,
    actual_delivery_date: null,
    status: 0,
    total_expected_qty: totalExpectedQty,
    total_received_qty: 0
  };
  
  db.purchase_orders.push(order);
  db.purchase_order_items.push(...orderItems);
  
  // 更新供应商的最后下单时间
  const supplierIndex = db.suppliers.findIndex(s => s.supplier_id === supplierId);
  if (supplierIndex !== -1) {
    db.suppliers[supplierIndex].last_order_date = new Date().toISOString().slice(0, 10);
  }
  
  saveDB(db);
  return orderId;
}

export async function confirmReceipt(orderId, actualItems, operator = 'system', remark = '') {
  await delay();
  const db = getDB();
  
  const orderIndex = db.purchase_orders.findIndex(o => o.purchase_order_id === orderId);
  if (orderIndex === -1) throw new Error('采购订单不存在');
  if (db.purchase_orders[orderIndex].status === 2) throw new Error('订单已完成');
  
  const orderItems = db.purchase_order_items.filter(i => i.purchase_order_id === orderId);
  let totalAmount = 0;
  let totalReceiptQty = 0;
  
  // 创建收货单
  const receiptId = generateId('purchase_receipts', 'receipt_id');
  const receiptTime = new Date().toISOString().slice(0, 19).replace('T', ' ');
  
  // 处理收货明细
  const receiptItems = [];
  
  for (const actual of actualItems) {
    const orderItemIndex = db.purchase_order_items.findIndex(
      i => i.purchase_order_id === orderId && i.product_id === actual.product_id
    );
    if (orderItemIndex === -1) throw new Error(`订单中不存在商品: ${actual.product_id}`);
    
    const orderItem = db.purchase_order_items[orderItemIndex];
    const remainingQty = orderItem.quantity - orderItem.received_qty;
    
    if (actual.quantity > remainingQty) throw new Error(`收货数量超过剩余可收货数量: ${actual.product_id}`);
    
    if (actual.quantity <= 0) continue;
    
    const productIndex = db.products.findIndex(p => p.product_id === actual.product_id);
    if (productIndex === -1) throw new Error(`商品不存在: ${actual.product_id}`);
    
    // 更新库存
    const beforeQty = db.products[productIndex].current_stock;
    db.products[productIndex] = {
      ...db.products[productIndex],
      current_stock: beforeQty + actual.quantity
    };
    
    // 记录库存变更
    db.inventory_logs.push({
      log_id: generateId('inventory_logs', 'log_id'),
      product_id: actual.product_id,
      relate_order_id: orderId,
      change_type: 2,
      change_qty: actual.quantity,
      before_quantity: beforeQty,
      after_quantity: beforeQty + actual.quantity,
      operator: operator,
      operate_time: receiptTime,
      remark: '采购入库'
    });
    
    // 更新采购订单项的已收货数量
    db.purchase_order_items[orderItemIndex] = {
      ...orderItem,
      received_qty: orderItem.received_qty + actual.quantity
    };
    
    // 生成批次号
    const batchNo = `${orderId}-${Date.now().toString().slice(-6)}`;
    
    // 添加收货明细
    receiptItems.push({
      receipt_item_id: generateId('purchase_receipt_items', 'receipt_item_id'),
      receipt_id: receiptId,
      product_id: actual.product_id,
      quantity: actual.quantity,
      batch_no: batchNo,
      quality_status: actual.quality_status || '合格'
    });
    
    // 如果商品需要批次管理，添加批次记录
    if (db.products[productIndex].batch_managed) {
      db.product_batches.push({
        batch_id: generateId('product_batches', 'batch_id'),
        product_id: actual.product_id,
        batch_no: batchNo,
        purchase_price: orderItem.unit_price,
        quantity: actual.quantity,
        inbound_date: receiptTime.slice(0, 10),
        supplier_id: db.purchase_orders[orderIndex].supplier_id
      });
    }
    
    totalAmount += actual.quantity * (orderItem.unit_price || 0);
    totalReceiptQty += actual.quantity;
  }
  
  if (totalReceiptQty === 0) throw new Error('请至少收货一件商品');
  
  // 保存收货单
  db.purchase_receipts.push({
    receipt_id: receiptId,
    purchase_order_id: orderId,
    receipt_time: receiptTime,
    operator: operator,
    total_qty: totalReceiptQty,
    remark: remark
  });
  
  // 保存收货明细
  db.purchase_receipt_items.push(...receiptItems);
  
  // 更新采购订单状态
  const order = db.purchase_orders[orderIndex];
  const newTotalReceivedQty = order.total_received_qty + totalReceiptQty;
  
  let newStatus = order.status;
  if (newTotalReceivedQty >= order.total_expected_qty) {
    newStatus = 2; // 已完成
  } else if (newTotalReceivedQty > 0) {
    newStatus = 1; // 部分交付
  }
  
  db.purchase_orders[orderIndex] = {
    ...order,
    total_received_qty: newTotalReceivedQty,
    status: newStatus,
    actual_delivery_date: new Date().toISOString().slice(0, 10)
  };
  
  // 记录财务数据
  db.financial_records.push({
    record_id: generateId('financial_records', 'record_id'),
    type: 2,
    amount: totalAmount,
    relate_order_id: orderId,
    occur_time: receiptTime,
    remark: '采购付款'
  });
  
  // 更新供应商评估数据
  updateSupplierEvaluation(db, order.supplier_id, order.expected_date);
  
  saveDB(db);
  return { receiptId, receiptTime };
}

// 更新供应商评估数据
function updateSupplierEvaluation(db, supplierId, expectedDate) {
  const supplierIndex = db.suppliers.findIndex(s => s.supplier_id === supplierId);
  if (supplierIndex === -1) return;
  
  const supplier = db.suppliers[supplierIndex];
  const today = new Date().toISOString().slice(0, 10);
  
  // 计算交付天数
  const daysDiff = Math.ceil((new Date(today) - new Date(expectedDate)) / (1000 * 60 * 60 * 24));
  
  // 获取该供应商的历史订单
  const supplierOrders = db.purchase_orders.filter(
    o => o.supplier_id === supplierId && o.status === 2
  );
  
  if (supplierOrders.length === 0) return;
  
  // 计算准时率
  let onTimeCount = 0;
  let totalDeliveryDays = 0;
  
  for (const order of supplierOrders) {
    if (order.actual_delivery_date && order.expected_date) {
      const orderDaysDiff = Math.ceil(
        (new Date(order.actual_delivery_date) - new Date(order.expected_date)) / 
        (1000 * 60 * 60 * 24)
      );
      if (orderDaysDiff <= 0) onTimeCount++;
      totalDeliveryDays += Math.max(orderDaysDiff, 1);
    }
  }
  
  const onTimeRate = ((onTimeCount / supplierOrders.length) * 100).toFixed(1);
  const averageDeliveryDays = (totalDeliveryDays / supplierOrders.length).toFixed(1);
  
  db.suppliers[supplierIndex] = {
    ...supplier,
    on_time_rate: parseFloat(onTimeRate),
    average_delivery_days: parseFloat(averageDeliveryDays)
  };
}

// 获取收货单列表
export async function getPurchaseReceipts(orderId = null) {
  await delay();
  let receipts = getTable('purchase_receipts');
  if (orderId) {
    receipts = receipts.filter(r => r.purchase_order_id === orderId);
  }
  return receipts.sort((a, b) => new Date(b.receipt_time) - new Date(a.receipt_time));
}

// 获取收货单明细
export async function getPurchaseReceiptItems(receiptId) {
  await delay();
  return getTable('purchase_receipt_items').filter(i => i.receipt_id === receiptId);
}

export async function getSalesOrders() {
  await delay();
  const orders = getTable('sales_orders');
  const customers = getTable('customers');
  
  return orders.map(order => {
    const customer = customers.find(c => c.customer_id === order.customer_id);
    return {
      ...order,
      customer_name: customer ? customer.name : '散客'
    };
  }).sort((a, b) => new Date(b.order_time) - new Date(a.order_time));
}

export async function getPurchaseOrders(status = null) {
  await delay();
  let orders = getTable('purchase_orders');
  const suppliers = getTable('suppliers');
  
  if (status !== null) {
    orders = orders.filter(o => o.status === status);
  }
  
  return orders.map(order => {
    const supplier = suppliers.find(s => s.supplier_id === order.supplier_id);
    return {
      ...order,
      supplier_name: supplier ? supplier.supplier_name : '未知供应商'
    };
  }).sort((a, b) => new Date(b.order_time) - new Date(a.order_time));
}

export async function updateOrderStatus(orderId, status) {
  await delay();
  const orders = getTable('purchase_orders');
  const index = orders.findIndex(o => o.purchase_order_id === orderId);
  if (index === -1) return false;
  
  const updatedOrders = [...orders];
  updatedOrders[index] = { ...updatedOrders[index], status };
  saveTable('purchase_orders', updatedOrders);
  return true;
}

export async function recordIncome(amount, relateOrderId, remark) {
  await delay();
  const records = getTable('financial_records');
  const newId = generateId('financial_records', 'record_id');
  const newRecord = {
    record_id: newId,
    type: 1,
    amount,
    relate_order_id: relateOrderId,
    occur_time: new Date().toISOString().slice(0, 19).replace('T', ' '),
    remark: remark || '其他收入'
  };
  records.push(newRecord);
  saveTable('financial_records', records);
  return newId;
}

export async function recordExpense(amount, relateOrderId, category, remark) {
  await delay();
  const records = getTable('financial_records');
  const newId = generateId('financial_records', 'record_id');
  const newRecord = {
    record_id: newId,
    type: 2,
    amount,
    relate_order_id: relateOrderId,
    occur_time: new Date().toISOString().slice(0, 19).replace('T', ' '),
    remark: remark || category || '其他支出'
  };
  records.push(newRecord);
  saveTable('financial_records', records);
  return newId;
}

export async function recordOtherExpense(category, amount, date, note) {
  await delay();
  const records = getTable('financial_records');
  const newId = generateId('financial_records', 'record_id');
  const newRecord = {
    record_id: newId,
    type: 2,
    amount,
    relate_order_id: null,
    occur_time: date || new Date().toISOString().slice(0, 19).replace('T', ' '),
    remark: note || category || '其他支出'
  };
  records.push(newRecord);
  saveTable('financial_records', records);
  return newId;
}

export async function getFinancialFlow(startDate, endDate, type = null) {
  await delay();
  let records = getTable('financial_records');
  
  if (startDate) {
    records = records.filter(r => r.occur_time >= startDate);
  }
  if (endDate) {
    records = records.filter(r => r.occur_time <= endDate);
  }
  if (type !== null) {
    records = records.filter(r => r.type === type);
  }
  
  return records.sort((a, b) => new Date(b.occur_time) - new Date(a.occur_time));
}

export async function calculateProfit(startDate, endDate) {
  await delay();
  const records = await getFinancialFlow(startDate, endDate);
  const income = records.filter(r => r.type === 1).reduce((sum, r) => sum + r.amount, 0);
  const expense = records.filter(r => r.type === 2).reduce((sum, r) => sum + r.amount, 0);
  return income - expense;
}

export async function getFinancialSummary(startDate, endDate) {
  await delay();
  const records = await getFinancialFlow(startDate, endDate);
  const totalIncome = records.filter(r => r.type === 1).reduce((sum, r) => sum + r.amount, 0);
  const returnExpense = records.filter(r => r.type === 4).reduce((sum, r) => sum + r.amount, 0);
  const totalExpense = records.filter(r => r.type === 2 || r.type === 3).reduce((sum, r) => sum + r.amount, 0);
  
  // 计算毛利润：假设平均毛利率为 30%
  const grossProfit = (totalIncome - returnExpense) * 0.3;
  
  return {
    totalIncome: totalIncome - returnExpense,
    totalExpense,
    profit: totalIncome - returnExpense - totalExpense,
    grossProfit
  };
}

export async function generateSalesReport(startDate, endDate, groupBy = 'day') {
  await delay();
  const orders = getTable('sales_orders').filter(o => {
    const time = o.order_time;
    return (!startDate || time >= startDate) && (!endDate || time <= endDate);
  });
  
  const grouped = {};
  orders.forEach(order => {
    let key;
    if (groupBy === 'day') {
      key = order.order_time.slice(0, 10);
    } else if (groupBy === 'month') {
      key = order.order_time.slice(0, 7);
    } else {
      key = order.order_time.slice(0, 4);
    }
    
    if (!grouped[key]) {
      grouped[key] = { amount: 0, count: 0 };
    }
    grouped[key].amount += order.total_amount;
    grouped[key].count += 1;
  });
  
  const dates = Object.keys(grouped).sort();
  const amounts = dates.map(d => grouped[d].amount);
  const counts = dates.map(d => grouped[d].count);
  
  return { dates, amounts, counts };
}

export async function getSalesChartData(startDate, endDate) {
  await delay();
  const result = await generateSalesReport(startDate, endDate, 'day');
  return result;
}

export async function updateSupplier(supplierId, data) {
  await delay();
  const suppliers = getTable('suppliers');
  const index = suppliers.findIndex(s => s.supplier_id === supplierId);
  if (index === -1) return false;
  
  suppliers[index] = { ...suppliers[index], ...data };
  saveTable('suppliers', suppliers);
  return true;
}

export async function deleteSupplier(supplierId) {
  await delay();
  const db = getDB();
  
  const hasOrders = db.purchase_orders.some(o => o.supplier_id === supplierId);
  if (hasOrders) {
    return { canDelete: false, message: '该供应商已有采购订单，无法删除' };
  }
  
  const suppliers = db.suppliers;
  const index = suppliers.findIndex(s => s.supplier_id === supplierId);
  if (index === -1) return false;
  
  suppliers.splice(index, 1);
  saveDB(db);
  return { canDelete: true };
}

export async function getEmployees() {
  await delay();
  const users = getTable('users');
  return users.filter(u => ['cashier', 'purchaser', 'admin'].includes(u.role));
}

export async function addEmployee(username, password, role) {
  await delay();
  const users = getTable('users');
  const newId = generateId('users', 'user_id');
  const newUser = {
    user_id: newId,
    username,
    password,
    role: role || 'cashier',
    status: 1,
    last_login: null
  };
  users.push(newUser);
  saveTable('users', users);
  return newId;
}

export async function updateEmployee(userId, data) {
  await delay();
  const users = getTable('users');
  const index = users.findIndex(u => u.user_id === userId);
  if (index === -1) return false;
  
  const allowedFields = ['role', 'status'];
  const updateData = {};
  allowedFields.forEach(field => {
    if (data[field] !== undefined) {
      updateData[field] = data[field];
    }
  });
  
  users[index] = { ...users[index], ...updateData };
  saveTable('users', users);
  return true;
}

export async function resetPassword(userId, newPassword) {
  await delay();
  const users = getTable('users');
  const index = users.findIndex(u => u.user_id === userId);
  if (index === -1) return false;
  
  users[index] = { ...users[index], password: newPassword };
  saveTable('users', users);
  return true;
}

export async function deleteEmployee(userId) {
  await delay();
  const db = getDB();
  
  const hasSales = db.sales_orders.some(o => o.cashier_id === userId);
  const hasPurchases = db.purchase_orders.some(o => o.purchaser_id === userId);
  
  if (hasSales || hasPurchases) {
    return { canDelete: false, message: '该员工已有相关订单记录，无法删除' };
  }
  
  const users = db.users;
  const index = users.findIndex(u => u.user_id === userId);
  if (index === -1) return false;
  
  users.splice(index, 1);
  saveDB(db);
  return { canDelete: true };
}

export async function cancelOrder(orderId) {
  await delay();
  const db = getDB();
  
  const orderIndex = db.sales_orders.findIndex(o => o.order_id === orderId);
  if (orderIndex === -1) throw new Error('订单不存在');
  
  const order = db.sales_orders[orderIndex];
  if (order.payment_status === 2) throw new Error('订单已取消');
  
  if (order.payment_status === 1) {
    const items = db.sales_order_items.filter(i => i.order_id === orderId);
    for (const item of items) {
      const productIndex = db.products.findIndex(p => p.product_id === item.product_id);
      if (productIndex !== -1) {
        db.products[productIndex].current_stock += item.quantity;
        
        db.inventory_logs.push({
          log_id: generateId('inventory_logs', 'log_id'),
          product_id: item.product_id,
          relate_order_id: orderId,
          change_type: 3,
          change_qty: item.quantity,
          before_quantity: db.products[productIndex].current_stock - item.quantity,
          after_quantity: db.products[productIndex].current_stock,
          operator: 'system',
          operate_time: new Date().toISOString().slice(0, 19).replace('T', ' '),
          remark: '订单取消，库存恢复'
        });
      }
    }
  }
  
  db.sales_orders[orderIndex] = {
    ...order,
    payment_status: 2
  };
  
  saveDB(db);
  return true;
}

export async function cancelPurchaseOrder(orderId) {
  await delay();
  const db = getDB();
  
  const orderIndex = db.purchase_orders.findIndex(o => o.purchase_order_id === orderId);
  if (orderIndex === -1) throw new Error('采购订单不存在');
  
  const order = db.purchase_orders[orderIndex];
  if (order.status === 2) throw new Error('订单已完成');
  
  db.purchase_orders[orderIndex] = {
    ...order,
    status: 3
  };
  
  saveDB(db);
  return true;
}

export async function getProductEditLogs(productId) {
  await delay();
  const logs = getTable('product_edit_logs');
  const productLogs = logs.filter(log => log.product_id === productId);
  return productLogs.sort((a, b) => new Date(b.operate_time) - new Date(a.operate_time));
}

export async function deleteOrder(orderId, operator = 'admin') {
  await delay();
  const db = getDB();
  
  const orderIndex = db.sales_orders.findIndex(o => o.order_id === orderId);
  if (orderIndex === -1) throw new Error('订单不存在');
  
  const order = db.sales_orders[orderIndex];
  
  if (order.payment_status === 1) throw new Error('已支付订单无法删除，请使用退货功能');
  
  const orderItems = db.sales_order_items.filter(i => i.order_id === orderId);
  
  for (const item of orderItems) {
    const productIndex = db.products.findIndex(p => p.product_id === item.product_id);
    if (productIndex !== -1) {
      const beforeQuantity = db.products[productIndex].current_stock;
      db.products[productIndex].current_stock += item.quantity;
      
      if (!db.inventory_logs) db.inventory_logs = [];
      db.inventory_logs.push({
        log_id: generateId('inventory_logs', 'log_id'),
        product_id: item.product_id,
        relate_order_id: orderId,
        change_type: 4,
        change_qty: item.quantity,
        before_quantity: beforeQuantity,
        after_quantity: db.products[productIndex].current_stock,
        operator: operator,
        operate_time: new Date().toISOString().slice(0, 19).replace('T', ' '),
        remark: '订单删除，库存回滚'
      });
    }
  }
  
  if (!db.operation_logs) {
    db.operation_logs = [];
  }
  
  db.operation_logs.push({
    log_id: generateId('operation_logs', 'log_id'),
    order_id: orderId,
    operator: operator,
    operate_time: new Date().toISOString().slice(0, 19).replace('T', ' '),
    operation_type: 'delete_order',
    before_data: JSON.stringify({
      order_id: order.order_id,
      customer_id: order.customer_id,
      total_amount: order.total_amount,
      payment_status: order.payment_status,
      is_returned: order.is_returned,
      order_time: order.order_time,
      items: orderItems.map(i => ({
        product_id: i.product_id,
        product_name: db.products.find(p => p.product_id === i.product_id)?.product_name,
        quantity: i.quantity,
        unit_price: i.unit_price
      }))
    }),
    remark: '删除订单'
  });
  
  if (order.payment_status === 0 && db.financial_flows) {
    db.financial_flows = db.financial_flows.filter(f => 
      !(f.relate_order_id === orderId && f.flow_type === 1)
    );
  }
  
  db.sales_orders.splice(orderIndex, 1);
  db.sales_order_items = db.sales_order_items.filter(i => i.order_id !== orderId);
  
  saveDB(db);
  return true;
}

export async function returnOrder(orderId, items, returnReason, returnRemark = '') {
  await delay();
  const db = getDB();
  
  const orderIndex = db.sales_orders.findIndex(o => o.order_id === orderId);
  if (orderIndex === -1) throw new Error('订单不存在');
  
  const order = db.sales_orders[orderIndex];
  if (order.payment_status !== 1) throw new Error('订单未支付，无法退货');
  if (order.is_returned) throw new Error('订单已退货');
  
  const orderItems = db.sales_order_items.filter(i => i.order_id === orderId);
  
  let totalRefund = 0;
  
  for (const item of items) {
    const orderItem = orderItems.find(i => i.product_id === item.productId);
    if (!orderItem) throw new Error(`订单中不存在商品: ${item.productId}`);
    
    const productIndex = db.products.findIndex(p => p.product_id === item.productId);
    if (productIndex === -1) throw new Error(`商品不存在: ${item.productId}`);
    
    const beforeQty = db.products[productIndex].current_stock;
    db.products[productIndex].current_stock += item.quantity;
    
    db.inventory_logs.push({
      log_id: generateId('inventory_logs', 'log_id'),
      product_id: item.productId,
      relate_order_id: orderId,
      change_type: 4,
      change_qty: item.quantity,
      before_quantity: beforeQty,
      after_quantity: db.products[productIndex].current_stock,
      operator: 'system',
      operate_time: new Date().toISOString().slice(0, 19).replace('T', ' '),
      remark: '销售退货'
    });
    
    totalRefund += item.quantity * (orderItem.unit_price || 0);
  }
  
  db.financial_records.push({
    record_id: generateId('financial_records', 'record_id'),
    type: 4,
    amount: totalRefund,
    relate_order_id: orderId,
    occur_time: new Date().toISOString().slice(0, 19).replace('T', ' '),
    remark: `销售退货 - ${returnReason}`
  });
  
  db.sales_orders[orderIndex] = {
    ...order,
    is_returned: 1,
    return_time: new Date().toISOString().slice(0, 19).replace('T', ' '),
    return_reason: returnReason,
    return_remark: returnRemark,
    return_status: 1
  };
  
  saveDB(db);
  return true;
}

export async function getOverduePurchaseOrders() {
  await delay();
  const db = getDB();
  const today = new Date().toISOString().slice(0, 10);
  
  return db.purchase_orders.filter(order => {
    return order.status !== 2 && order.expected_date < today;
  });
}

// ====================================
// 供应商评估相关API
// ====================================

// 获取供应商评估数据
export async function getSupplierEvaluation(supplierId = null) {
  await delay();
  let suppliers = getTable('suppliers');
  
  if (supplierId) {
    const supplier = suppliers.find(s => s.supplier_id === supplierId);
    if (!supplier) return null;
    return supplier;
  }
  
  return suppliers.sort((a, b) => {
    // 按准时率降序
    const rateA = a.on_time_rate || 0;
    const rateB = b.on_time_rate || 0;
    return rateB - rateA;
  });
}

// 获取供应商排名
export async function getSupplierRanking(sortBy = 'on_time_rate') {
  await delay();
  const suppliers = getTable('suppliers');
  
  return suppliers.sort((a, b) => {
    switch (sortBy) {
      case 'delivery_days':
        return (a.average_delivery_days || 999) - (b.average_delivery_days || 999);
      case 'on_time_rate':
      default:
        return (b.on_time_rate || 0) - (a.on_time_rate || 0);
    }
  });
}

// ====================================
// 采购建议/自动补货相关API
// ====================================

// 生成采购建议
export async function generateReplenishmentAdvice() {
  await delay();
  const db = getDB();
  
  const adviceList = [];
  const today = new Date().toISOString().slice(0, 10);
  
  for (const product of db.products) {
    if (!product.status || product.threshold === undefined) continue;
    
    // 计算过去90天的日均销量
    const ninetyDaysAgo = new Date();
    ninetyDaysAgo.setDate(ninetyDaysAgo.getDate() - 90);
    const ninetyDaysAgoStr = ninetyDaysAgo.toISOString().slice(0, 10);
    
    const relatedSalesItems = db.sales_order_items.filter(item => {
      const order = db.sales_orders.find(o => o.order_id === item.order_id);
      return item.product_id === product.product_id && 
             order && 
             order.order_time >= ninetyDaysAgoStr &&
             order.is_cancelled !== 1;
    });
    
    const totalSold = relatedSalesItems.reduce((sum, item) => sum + item.quantity, 0);
    const dailySales = totalSold / 90;
    
    // 获取供应商平均交付天数
    const supplier = db.suppliers.find(s => {
      const supplierOrders = db.purchase_orders.filter(
        o => o.supplier_id === s.supplier_id && o.status === 2
      );
      const hasProductOrders = db.purchase_order_items.some(
        item => item.product_id === product.product_id && 
               supplierOrders.some(o => o.purchase_order_id === item.purchase_order_id)
      );
      return hasProductOrders;
    });
    
    const deliveryDays = supplier?.average_delivery_days || 7;
    
    // 计算建议采购量
    const recommendedQty = Math.max(
      0,
      Math.ceil((dailySales * deliveryDays * 1.2) - product.current_stock + product.threshold)
    );
    
    // 确定建议原因
    let reason = '';
    if (product.current_stock < product.threshold) {
      reason = '库存低于安全库存';
    } else if (recommendedQty > 0) {
      reason = '基于历史销量预测';
    } else {
      continue; // 不需要建议
    }
    
    adviceList.push({
      advice_id: generateId('replenishment_advice', 'advice_id'),
      product_id: product.product_id,
      product_name: product.product_name,
      current_stock: product.current_stock,
      threshold: product.threshold,
      daily_sales: dailySales.toFixed(2),
      suggested_qty: recommendedQty,
      generated_date: today,
      status: 0, // 0:待处理, 1:已生成订单, 2:已取消
      reason: reason
    });
  }
  
  // 保存建议到数据库
  db.replenishment_advice.push(...adviceList);
  saveDB(db);
  
  return adviceList;
}

// 获取采购建议列表
export async function getReplenishmentAdvice(status = null) {
  await delay();
  let advice = getTable('replenishment_advice');
  
  if (status !== null) {
    advice = advice.filter(a => a.status === status);
  }
  
  return advice.sort((a, b) => new Date(b.generated_date) - new Date(a.generated_date));
}

// 将采购建议转为采购订单
export async function createPurchaseFromAdvice(adviceId, supplierId, expectedDate) {
  await delay();
  const db = getDB();
  
  const adviceIndex = db.replenishment_advice.findIndex(a => a.advice_id === adviceId);
  if (adviceIndex === -1) throw new Error('采购建议不存在');
  
  const advice = db.replenishment_advice[adviceIndex];
  if (advice.status === 1) throw new Error('该建议已生成采购订单');
  
  // 获取商品信息
  const product = db.products.find(p => p.product_id === advice.product_id);
  if (!product) throw new Error('商品不存在');
  
  // 创建采购订单
  const items = [{
    product_id: advice.product_id,
    quantity: advice.suggested_qty,
    unit_price: product.purchase_ref_price || 0
  }];
  
  const orderId = await createPurchaseOrder(
    'system',
    supplierId,
    items,
    expectedDate
  );
  
  // 更新建议状态
  db.replenishment_advice[adviceIndex] = {
    ...advice,
    status: 1,
    processed_date: new Date().toISOString().slice(0, 10)
  };
  
  saveDB(db);
  return orderId;
}

// 取消采购建议
export async function cancelReplenishmentAdvice(adviceId) {
  await delay();
  const db = getDB();
  
  const adviceIndex = db.replenishment_advice.findIndex(a => a.advice_id === adviceId);
  if (adviceIndex === -1) throw new Error('采购建议不存在');
  
  db.replenishment_advice[adviceIndex] = {
    ...db.replenishment_advice[adviceIndex],
    status: 2
  };
  
  saveDB(db);
  return true;
}

// 考勤管理 API
export async function getAttendance(userId = null, startDate = null, endDate = null) {
  await delay();
  let attendance = getTable('attendance');
  
  if (userId) {
    attendance = attendance.filter(a => a.user_id === userId);
  }
  if (startDate) {
    attendance = attendance.filter(a => a.date >= startDate);
  }
  if (endDate) {
    attendance = attendance.filter(a => a.date <= endDate);
  }
  
  return attendance.sort((a, b) => new Date(b.date) - new Date(a.date));
}

export async function checkIn(userId, checkInTime = null) {
  await delay();
  const db = getDB();
  const today = new Date().toISOString().slice(0, 10);
  
  // 检查今天是否已经打卡
  const existingAttendance = db.attendance.find(a => a.user_id === userId && a.date === today);
  
  if (existingAttendance) {
    if (existingAttendance.check_in) {
      throw new Error('今天已经打卡上班了');
    }
    existingAttendance.check_in = checkInTime || new Date().toISOString().slice(0, 19).replace('T', ' ');
    existingAttendance.status = 'normal';
  } else {
    const newAttendance = {
      attendance_id: generateId('attendance', 'attendance_id'),
      user_id: userId,
      date: today,
      check_in: checkInTime || new Date().toISOString().slice(0, 19).replace('T', ' '),
      check_out: null,
      status: 'normal'
    };
    
    // 判断是否迟到（9:00之后打卡算迟到）
    const checkInHour = parseInt(newAttendance.check_in.split(' ')[1].split(':')[0]);
    if (checkInHour >= 9) {
      newAttendance.status = 'late';
    }
    
    db.attendance.push(newAttendance);
  }
  
  saveDB(db);
  return true;
}

export async function checkOut(userId, checkOutTime = null) {
  await delay();
  const db = getDB();
  const today = new Date().toISOString().slice(0, 10);
  
  const attendance = db.attendance.find(a => a.user_id === userId && a.date === today);
  
  if (!attendance) {
    throw new Error('今天还没有打卡上班');
  }
  
  if (attendance.check_out) {
    throw new Error('今天已经打卡下班了');
  }
  
  attendance.check_out = checkOutTime || new Date().toISOString().slice(0, 19).replace('T', ' ');
  
  saveDB(db);
  return true;
}

export async function calculateEmployeeSalary(userId, year, month) {
  await delay();
  const db = getDB();
  const user = db.users.find(u => u.user_id === userId);
  
  if (!user) {
    throw new Error('员工不存在');
  }
  
  const startDate = `${year}-${String(month).padStart(2, '0')}-01`;
  const endDate = `${year}-${String(month).padStart(2, '0')}-31`;
  
  const attendance = db.attendance.filter(a => 
    a.user_id === userId && 
    a.date >= startDate && 
    a.date <= endDate && 
    a.check_in && 
    a.check_out
  );
  
  let totalHours = 0;
  let totalDays = attendance.length;
  let lateDays = attendance.filter(a => a.status === 'late').length;
  
  for (const record of attendance) {
    const checkIn = new Date(record.check_in);
    const checkOut = new Date(record.check_out);
    const hours = (checkOut - checkIn) / (1000 * 60 * 60);
    totalHours += hours;
  }
  
  let salary = 0;
  
  if (user.salary_type === 'monthly') {
    salary = user.salary_rate;
    // 迟到扣款
    salary -= lateDays * 50;
  } else {
    salary = totalHours * user.salary_rate;
  }
  
  salary = Math.max(0, salary);
  
  return {
    user_id: userId,
    real_name: user.real_name,
    year,
    month,
    total_days: totalDays,
    late_days: lateDays,
    total_hours: totalHours.toFixed(2),
    salary_type: user.salary_type,
    salary_rate: user.salary_rate,
    salary: salary.toFixed(2)
  };
}