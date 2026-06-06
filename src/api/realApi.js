import client from './client';

export async function login(username, password) {
  try {
    const res = await client.post('/auth/login', { username, password });
    if (res.token) {
      localStorage.setItem('token', res.token);
      localStorage.setItem('user', JSON.stringify(res.user));
    }
    return res;
  } catch (error) {
    console.error('登录失败:', error);
    return null;
  }
}

export async function getUserInfo(userId) {
  try {
    const res = await client.get(`/employees/${userId}`);
    return res;
  } catch (error) {
    console.error('获取用户信息失败:', error);
    return null;
  }
}

export async function getProfile() {
  try {
    const res = await client.get('/employees/profile');
    if (res && res.success !== undefined) {
      return res;
    }
    return { success: true, data: res };
  } catch (error) {
    console.error('获取个人信息失败:', error);
    return { success: false, error: '获取失败' };
  }
}

export async function updateProfile(data) {
  try {
    const res = await client.put('/employees/profile', data);
    if (res && res.success !== undefined) {
      return res;
    }
    return { success: true, data: res };
  } catch (error) {
    console.error('更新个人信息失败:', error);
    return { success: false, error: '更新失败' };
  }
}

export async function changePassword(data) {
  try {
    const res = await client.post('/employees/profile/change-password', data);
    if (res && res.success !== undefined) {
      return res;
    }
    return { success: true, data: res };
  } catch (error) {
    console.error('修改密码失败:', error);
    return { success: false, error: '修改失败' };
  }
}

export async function resetUserPassword(userId) {
  try {
    const res = await client.post(`/employees/${userId}/reset-password`);
    if (res && res.success !== undefined) {
      return res;
    }
    return { success: true, data: res };
  } catch (error) {
    console.error('重置密码失败:', error);
    return { success: false, error: '重置失败' };
  }
}

export async function updateEmployee(userId, data) {
  try {
    const res = await client.put(`/employees/${userId}`, data);
    return res;
  } catch (error) {
    console.error('更新员工信息失败:', error);
    return { success: false, error: '更新失败' };
  }
}

export async function getProducts({ category, status, sort_by, sort_order } = {}) {
  try {
    const params = {};
    if (category !== undefined) params.category = category;
    if (status !== undefined) params.status = status;
    if (sort_by !== undefined) params.sort_by = sort_by;
    if (sort_order !== undefined) params.sort_order = sort_order;
    const res = await client.get('/products', { params });
    const data = res.data || res;
    return Array.isArray(data) ? data : (data.data || []);
  } catch (error) {
    console.error('获取产品列表失败:', error);
    return [];
  }
}

export async function getProductById(productId) {
  try {
    const res = await client.get(`/products/${productId}`);
    return res;
  } catch (error) {
    console.error('获取产品详情失败:', error);
    return null;
  }
}

export async function addProduct(productInfo) {
  try {
    const res = await client.post('/products', productInfo);
    return res.product_id || res.id;
  } catch (error) {
    console.error('添加产品失败:', error);
    return null;
  }
}

export async function updateProduct(productId, updateData, operator = 'system') {
  try {
    const res = await client.put(`/products/${productId}`, updateData);
    return res.success;
  } catch (error) {
    console.error('更新产品失败:', error);
    return false;
  }
}

export async function disableProduct(productId) {
  try {
    const res = await client.patch(`/products/${productId}/disable`);
    return res.success;
  } catch (error) {
    console.error('禁用产品失败:', error);
    return false;
  }
}

export async function setThreshold(productId, minStock) {
  try {
    const res = await client.patch(`/products/${productId}/threshold`, { threshold: minStock });
    return res.success;
  } catch (error) {
    console.error('设置阈值失败:', error);
    return false;
  }
}

export async function enableProduct(productId) {
  try {
    const res = await client.put(`/products/${productId}`, { status: 1 });
    return res.success;
  } catch (error) {
    console.error('启用产品失败:', error);
    return false;
  }
}

export async function deleteProduct(productId) {
  try {
    const res = await client.delete(`/products/${productId}`);
    return res;
  } catch (error) {
    console.error('删除产品失败:', error);
    return { canDelete: false, message: error.response?.data?.error || '删除失败' };
  }
}

export async function checkStock(productId) {
  try {
    const res = await client.get(`/stock/${productId}`);
    return res.current_stock || 0;
  } catch (error) {
    console.error('查询库存失败:', error);
    return 0;
  }
}

export async function deductStock(productId, quantity, relateOrderId) {
  try {
    const res = await client.post('/stock/deduct', {
      product_id: productId,
      quantity,
      relate_order_id: relateOrderId
    });
    return res.success;
  } catch (error) {
    console.error('扣减库存失败:', error);
    return false;
  }
}

export async function addStock(productId, quantity, reason, operatorId, relateOrderId) {
  try {
    const res = await client.post('/stock/add', {
      product_id: productId,
      quantity,
      reason,
      operator_id: operatorId,
      relate_order_id: relateOrderId
    });
    return res.success;
  } catch (error) {
    console.error('增加库存失败:', error);
    return false;
  }
}

export async function getAlertProducts() {
  try {
    const res = await client.get('/stock/alerts');
    return res.data || res;
  } catch (error) {
    console.error('获取低库存预警失败:', error);
    return [];
  }
}

export async function getStockLog(params) {
  try {
    let queryParams = {};
    
    // 支持旧的调用方式（向后兼容）
    if (typeof params === 'number') {
      queryParams.product_id = params;
    } else if (typeof params === 'object') {
      // 新的调用方式
      Object.keys(params).forEach(key => {
        if (params[key]) {
          queryParams[key] = params[key];
        }
      });
    }
    
    const res = await client.get('/stock/logs', { params: queryParams });
    return res;
  } catch (error) {
    console.error('获取库存日志失败:', error);
    return { data: [], total: 0 };
  }
}

export async function manualAdjust(operatorId, productId, delta, reason) {
  try {
    const res = await client.post('/stock/adjust', {
      product_id: productId,
      delta,
      reason,
      operator_id: operatorId
    });
    return res.success;
  } catch (error) {
    console.error('手动调整库存失败:', error);
    return false;
  }
}

export async function createOrder(customerId, cartItems, paymentMethod, shippingAddress, 
                                  discountAmount = 0, earnedPoints = 0, usedPoints = 0, finalAmount = 0) {
  try {
    const items = cartItems.map(item => ({
      product_id: item.product_id,
      quantity: item.quantity
    }));
    
    const res = await client.post('/sales/orders', {
      customer_id: customerId,
      items,
      payment_method: paymentMethod,
      shipping_address: shippingAddress,
      discount_amount: discountAmount,
      points_used: usedPoints,
      final_amount: finalAmount
    });
    
    return res.order_id || res.id;
  } catch (error) {
    console.error('创建订单失败:', error);
    throw error;
  }
}

export async function payOrder(orderId) {
  try {
    const res = await client.post(`/sales/orders/${orderId}/pay`, { operator: 'system' });
    return res.success;
  } catch (error) {
    console.error('支付订单失败:', error);
    throw error;
  }
}

export async function getOrderHistory(customerId = null) {
  try {
    const params = customerId !== null ? { customer_id: customerId } : {};
    const res = await client.get('/sales/orders', { params });
    return res.data || res;
  } catch (error) {
    console.error('获取订单历史失败:', error);
    return [];
  }
}

export async function getOrderDetail(orderId) {
  try {
    const res = await client.get(`/sales/orders/${orderId}`);
    return res;
  } catch (error) {
    console.error('获取订单详情失败:', error);
    return null;
  }
}

export async function getCustomers() {
  try {
    const res = await client.get('/customers');
    return res.data || res;
  } catch (error) {
    console.error('获取客户列表失败:', error);
    return [];
  }
}

export async function addCustomer(customerInfo) {
  try {
    const res = await client.post('/customers', {
      name: customerInfo.name,
      phone: customerInfo.phone,
      email: customerInfo.email,
      address: customerInfo.address
    });
    return res.customer_id || res.id;
  } catch (error) {
    console.error('添加客户失败:', error);
    return null;
  }
}

export async function updateCustomer(customerId, data) {
  try {
    const res = await client.put(`/customers/${customerId}`, data);
    return res.success;
  } catch (error) {
    console.error('更新客户失败:', error);
    return false;
  }
}

export async function deleteCustomer(customerId) {
  try {
    const res = await client.delete(`/customers/${customerId}`);
    return res;
  } catch (error) {
    console.error('删除客户失败:', error);
    return { canDelete: false, message: error.response?.data?.error || '删除失败' };
  }
}

export async function getAllOrders(filters = {}) {
  try {
    const params = {};
    if (filters.customerId) params.customer_id = filters.customerId;
    if (filters.status !== undefined) params.status = filters.status;
    if (filters.startDate) params.start_date = filters.startDate;
    if (filters.endDate) params.end_date = filters.endDate;
    
    const res = await client.get('/sales/orders', { params });
    return res.data || res;
  } catch (error) {
    console.error('获取所有订单失败:', error);
    return [];
  }
}

export async function getCustomerPurchasePreference(customerId) {
  try {
    const res = await client.get(`/customers/${customerId}/orders`);
    const orders = res.data || res;
    
    const totalOrders = orders.length;
    const totalAmount = orders.reduce((sum, order) => sum + (order.total_paid || order.total_amount || 0), 0);
    
    const categoryStats = {};
    const brandStats = {};
    const productStats = {};
    
    orders.forEach(order => {
      (order.items || []).forEach(item => {
        const category = item.category || '未分类';
        const brand = item.brand || '未知';
        const productId = item.product_id;
        const quantity = item.quantity || 0;
        const subtotal = item.subtotal || (item.quantity * item.unit_price || 0);
        
        categoryStats[category] = categoryStats[category] || { count: 0, amount: 0, quantity: 0 };
        categoryStats[category].count++;
        categoryStats[category].amount += subtotal;
        categoryStats[category].quantity += quantity;
        
        brandStats[brand] = brandStats[brand] || { count: 0, amount: 0, quantity: 0 };
        brandStats[brand].count++;
        brandStats[brand].amount += subtotal;
        brandStats[brand].quantity += quantity;
        
        if (!productStats[productId]) {
          productStats[productId] = {
            product_id: productId,
            product_name: item.product_name || '',
            brand,
            category,
            count: 0,
            amount: 0,
            quantity: 0
          };
        }
        productStats[productId].count++;
        productStats[productId].amount += subtotal;
        productStats[productId].quantity += quantity;
      });
    });
    
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
      .slice(0, 10);
    
    return {
      totalOrders,
      totalAmount,
      categoryPreferences,
      brandPreferences,
      recentProducts
    };
  } catch (error) {
    console.error('获取客户购买偏好失败:', error);
    return {
      totalOrders: 0,
      totalAmount: 0,
      categoryPreferences: [],
      brandPreferences: [],
      recentProducts: []
    };
  }
}

export async function getSuppliers({ status, sort_by, sort_order } = {}) {
  try {
    const params = {};
    if (status !== undefined) params.status = status;
    if (sort_by !== undefined) params.sort_by = sort_by;
    if (sort_order !== undefined) params.sort_order = sort_order;
    const res = await client.get('/suppliers', { params });
    const data = res.data || res;
    return Array.isArray(data) ? data : (data.data || []);
  } catch (error) {
    console.error('获取供应商列表失败:', error);
    return [];
  }
}

export async function addSupplier(supplierInfo) {
  try {
    const res = await client.post('/suppliers', supplierInfo);
    return res.supplier_id || res.id;
  } catch (error) {
    console.error('添加供应商失败:', error);
    return null;
  }
}

export async function createPurchaseOrder(purchaserId, supplierId, items, expectedDate) {
  try {
    const orderItems = items.map(item => ({
      product_id: item.product_id,
      quantity: item.quantity,
      unit_price: item.unit_price
    }));
    
    const res = await client.post('/purchase/orders', {
      supplier_id: supplierId,
      items: orderItems,
      expected_date: expectedDate
    });
    
    return res.order_id || res.purchase_order_id || res.id;
  } catch (error) {
    console.error('创建采购订单失败:', error);
    throw error;
  }
}

export async function confirmReceipt(orderId, actualItems, operator = 'system', remark = '') {
  try {
    const items = actualItems.map(item => ({
      product_id: item.product_id,
      received_quantity: item.received_quantity,
      quality_status: item.quality_status || '合格'
    }));
    
    const res = await client.post(`/purchase/orders/${orderId}/receipt`, { items, operator, remark });
    return res;
  } catch (error) {
    console.error('确认收货失败:', error);
    throw error;
  }
}

export async function getPurchaseReceipts(orderId = null) {
  try {
    const params = orderId ? { order_id: orderId } : {};
    const res = await client.get('/purchase/receipts', { params });
    return res.data || res;
  } catch (error) {
    console.error('获取收货单失败:', error);
    return [];
  }
}

export async function getPurchaseReceiptItems(receiptId) {
  try {
    const res = await client.get(`/purchase/receipts/${receiptId}/items`);
    return res.data || res;
  } catch (error) {
    console.error('获取收货单明细失败:', error);
    return [];
  }
}

export async function getSalesOrders() {
  try {
    const res = await client.get('/sales/orders');
    return res.data || res;
  } catch (error) {
    console.error('获取销售订单失败:', error);
    return [];
  }
}

export async function getPurchaseOrders(status = null) {
  try {
    const params = status !== null ? { status } : {};
    const res = await client.get('/purchase/orders', { params });
    return res.data || res;
  } catch (error) {
    console.error('获取采购订单失败:', error);
    return [];
  }
}

export async function updateOrderStatus(orderId, status) {
  try {
    const res = await client.put(`/purchase/orders/${orderId}`, { status });
    return res.success;
  } catch (error) {
    console.error('更新订单状态失败:', error);
    return false;
  }
}

export async function recordIncome(amount, relateOrderId, remark) {
  try {
    const res = await client.post('/finance/other-expense', {
      category: remark || '其他收入',
      amount,
      note: remark
    });
    return res.record_id || res.id;
  } catch (error) {
    console.error('记录收入失败:', error);
    return null;
  }
}

export async function recordExpense(amount, relateOrderId, category, remark) {
  try {
    const res = await client.post('/finance/other-expense', {
      category: category || remark || '其他支出',
      amount,
      note: remark
    });
    return res.record_id || res.id;
  } catch (error) {
    console.error('记录支出失败:', error);
    return null;
  }
}

export async function recordOtherExpense(category, amount, date, note) {
  try {
    const res = await client.post('/finance/other-expense', {
      category,
      amount,
      date,
      note
    });
    return res.record_id || res.id;
  } catch (error) {
    console.error('记录其他支出失败:', error);
    return null;
  }
}

export async function getFinancialFlow(startDate, endDate, type = null) {
  try {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    if (type !== null) params.type = type;
    
    const res = await client.get('/finance/records', { params });
    return res.data || res;
  } catch (error) {
    console.error('获取财务流水失败:', error);
    return [];
  }
}

export async function calculateProfit(startDate, endDate) {
  try {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    
    const res = await client.get('/finance/profit', { params });
    return res.profit || 0;
  } catch (error) {
    console.error('计算利润失败:', error);
    return 0;
  }
}

export async function getFinancialSummary(startDate, endDate) {
  try {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    
    const res = await client.get('/finance/summary', { params });
    return {
      totalIncome: res.total_income || 0,
      totalExpense: res.total_expense || 0,
      profit: res.profit || 0,
      grossProfit: res.gross_profit_margin || 0
    };
  } catch (error) {
    console.error('获取财务汇总失败:', error);
    return {
      totalIncome: 0,
      totalExpense: 0,
      profit: 0,
      grossProfit: 0
    };
  }
}

export async function generateSalesReport(startDate, endDate, groupBy = 'day') {
  try {
    const res = await client.get('/reports/sales-trend', {
      params: {
        start_date: startDate,
        end_date: endDate,
        group_by: groupBy
      }
    });
    
    const data = res.data || res;
    
    return {
      dates: data.dates || [],
      amounts: data.amounts || [],
      counts: data.counts || []
    };
  } catch (error) {
    console.error('生成销售报表失败:', error);
    return { dates: [], amounts: [], counts: [] };
  }
}

export async function getSalesChartData(startDate, endDate) {
  try {
    const res = await generateSalesReport(startDate, endDate, 'day');
    return res;
  } catch (error) {
    console.error('获取销售图表数据失败:', error);
    return { dates: [], amounts: [], counts: [] };
  }
}

export async function updateSupplier(supplierId, data) {
  try {
    const res = await client.put(`/suppliers/${supplierId}`, data);
    return res.success;
  } catch (error) {
    console.error('更新供应商失败:', error);
    return false;
  }
}

export async function deleteSupplier(supplierId) {
  try {
    const res = await client.delete(`/suppliers/${supplierId}`);
    return res;
  } catch (error) {
    console.error('删除供应商失败:', error);
    return { canDelete: false, message: error.response?.data?.error || '删除失败' };
  }
}

export async function getEmployees() {
  try {
    const res = await client.get('/employees');
    return res.data || res;
  } catch (error) {
    console.error('获取员工列表失败:', error);
    return [];
  }
}

export async function addEmployee(formData) {
  try {
    const res = await client.post('/employees', {
      username: formData.username,
      password: formData.password,
      role: formData.role,
      real_name: formData.real_name,
      phone: formData.phone,
      hire_date: formData.hire_date,
      salary_type: formData.salary_type,
      salary_rate: formData.salary_rate
    });
    return res.user_id || res.id || res.data?.user_id;
  } catch (error) {
    console.error('添加员工失败:', error);
    throw error;
  }
}

export async function resetPassword(userId, newPassword) {
  try {
    const res = await client.post(`/employees/${userId}/reset-password`, { new_password: newPassword });
    return res.success;
  } catch (error) {
    console.error('重置密码失败:', error);
    return false;
  }
}

export async function deleteEmployee(userId) {
  try {
    const res = await client.delete(`/employees/${userId}`);
    return res;
  } catch (error) {
    console.error('删除员工失败:', error);
    return { canDelete: false, message: error.response?.data?.error || '删除失败' };
  }
}

export async function cancelOrder(orderId) {
  try {
    const res = await client.post(`/sales/orders/${orderId}/cancel`);
    return res.success;
  } catch (error) {
    console.error('取消订单失败:', error);
    throw error;
  }
}

export async function cancelPurchaseOrder(orderId) {
  try {
    const res = await client.put(`/purchase/orders/${orderId}`, { status: 3 });
    return res.success;
  } catch (error) {
    console.error('取消采购订单失败:', error);
    throw error;
  }
}

export async function getProductEditLogs(productId) {
  try {
    const res = await client.get(`/products/${productId}/logs`);
    return res.data || res;
  } catch (error) {
    console.error('获取产品编辑日志失败:', error);
    return [];
  }
}

export async function deleteOrder(orderId, operator = 'admin') {
  try {
    const res = await client.delete(`/sales/orders/${orderId}`);
    return res.success;
  } catch (error) {
    console.error('删除订单失败:', error);
    throw error;
  }
}

export async function returnOrder(orderId, items, returnReason, returnRemark = '') {
  try {
    const returnItems = items.map(item => ({
      product_id: item.productId,
      quantity: item.quantity
    }));
    
    await client.post(`/sales/orders/${orderId}/return`, {
      items: returnItems,
      reason: returnReason,
      remark: returnRemark,
      operator: 'system'
    });
    return true;
  } catch (error) {
    console.error('退货失败:', error);
    throw error;
  }
}

export async function getOverduePurchaseOrders() {
  try {
    const res = await client.get('/purchase/overdue');
    return res.data || res;
  } catch (error) {
    console.error('获取超期采购订单失败:', error);
    return [];
  }
}

export async function getSupplierEvaluation(supplierId = null) {
  try {
    if (supplierId) {
      const res = await client.get(`/suppliers/${supplierId}`);
      return res;
    } else {
      const res = await client.get('/suppliers');
      return (res.data || res).sort((a, b) => (b.on_time_rate || 0) - (a.on_time_rate || 0));
    }
  } catch (error) {
    console.error('获取供应商评估失败:', error);
    return supplierId ? null : [];
  }
}

export async function getSupplierRanking(sortBy = 'on_time_rate') {
  try {
    const res = await client.get('/suppliers');
    const suppliers = res.data || res;
    
    return suppliers.sort((a, b) => {
      switch (sortBy) {
        case 'delivery_days':
          return (a.average_delivery_days || 999) - (b.average_delivery_days || 999);
        case 'on_time_rate':
        default:
          return (b.on_time_rate || 0) - (a.on_time_rate || 0);
      }
    });
  } catch (error) {
    console.error('获取供应商排名失败:', error);
    return [];
  }
}

export async function getDashboardStats() {
  try {
    const res = await client.get('/dashboard/stats');
    return res;
  } catch (error) {
    console.error('获取仪表盘统计失败:', error);
    return {
      today_sales: 0,
      low_stock_count: 0,
      monthly_purchase_orders: 0,
      monthly_profit: 0,
      update_time: new Date().toISOString()
    };
  }
}

export async function getCategorySales() {
  try {
    const res = await client.get('/reports/category-sales');
    return res.data || res;
  } catch (error) {
    console.error('获取类别销售数据失败:', error);
    return [];
  }
}

export async function getSupplierRankingReport(limit = 10) {
  try {
    const res = await client.get('/reports/supplier-ranking', { params: { limit } });
    return res.data || res;
  } catch (error) {
    console.error('获取供应商排名报告失败:', error);
    return [];
  }
}

export async function getInventoryTrend(startDate, endDate) {
  try {
    const res = await client.get('/reports/inventory-trend', {
      params: { start_date: startDate, end_date: endDate }
    });
    return res;
  } catch (error) {
    console.error('获取库存趋势失败:', error);
    return { dates: [], in_stock: [], out_stock: [] };
  }
}

export async function logout() {
  try {
    await client.post('/auth/logout');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    return true;
  } catch (error) {
    console.error('退出登录失败:', error);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    return true;
  }
}

export async function generateReplenishmentAdvice() {
  try {
    const res = await client.post('/purchase/replenishment-advice/generate');
    return res.data || res;
  } catch (error) {
    console.error('生成补货建议失败:', error);
    throw error;
  }
}

export async function getReplenishmentAdvice() {
  try {
    const res = await client.get('/purchase/replenishment-advice');
    const data = res.data || res;
    // 返回数据数组，如果后端返回的是对象则提取data字段
    return Array.isArray(data) ? data : (data.data || []);
  } catch (error) {
    console.error('获取补货建议失败:', error);
    return [];
  }
}

export async function createPurchaseFromAdvice(adviceId, supplierId) {
  try {
    const res = await client.post('/purchase/create-from-advice', {
      advice_id: adviceId,
      supplier_id: supplierId
    });
    return res.order_id || res.id;
  } catch (error) {
    console.error('根据补货建议创建采购订单失败:', error);
    throw error;
  }
}

export async function cancelReplenishmentAdvice(adviceId) {
  try {
    const res = await client.delete(`/purchase/replenishment-advice/${adviceId}`);
    return res.success;
  } catch (error) {
    console.error('取消补货建议失败:', error);
    throw error;
  }
}