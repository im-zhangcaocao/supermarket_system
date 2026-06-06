export default {
  users: [
    { user_id: 1, username: 'cashier', password: '123', role: 'cashier', status: 1, last_login: null },
    { user_id: 2, username: 'buyer', password: '123', role: 'purchaser', status: 1, last_login: null },
    { user_id: 3, username: 'admin', password: '123', role: 'admin', status: 1, last_login: null }
  ],
  customers: [
    { customer_id: 1, name: '张三', phone: '13800138000', email: 'zhangsan@example.com', address: '成都高新区', register_time: '2026-01-01' },
    { customer_id: 2, name: '李四', phone: '13900139000', email: 'lisi@example.com', address: '成都武侯区', register_time: '2026-02-15' }
  ],
  products: [
    { product_id: 1, product_name: '海尔冰箱 BCD-216', brand: '海尔', model: 'BCD-216', category: '冰箱', retail_price: 1899, purchase_ref_price: 1500, current_stock: 10, threshold: 5, status: 1 },
    { product_id: 2, product_name: '美的空调 KFR-35', brand: '美的', model: 'KFR-35', category: '空调', retail_price: 2599, purchase_ref_price: 2000, current_stock: 3, threshold: 5, status: 1 },
    { product_id: 3, product_name: '小米电视 4A 55寸', brand: '小米', model: '4A55', category: '电视', retail_price: 1899, purchase_ref_price: 1600, current_stock: 8, threshold: 5, status: 1 }
  ],
  suppliers: [
    { supplier_id: 1, supplier_name: '海尔电器有限公司', contact_person: '王经理', contact_phone: '0532-1234567', address: '青岛' },
    { supplier_id: 2, supplier_name: '美的集团', contact_person: '李经理', contact_phone: '0757-1234567', address: '佛山' }
  ],
  sales_orders: [
    { order_id: 'SO202606010001', customer_id: 1, order_time: '2026-06-01 10:30:00', total_amount: 3798, payment_method: '微信支付', payment_status: 1, shipping_address: '成都高新区天府大道100号', is_cancelled: 0, is_returned: 0 }
  ],
  sales_order_items: [
    { item_id: 1, order_id: 'SO202606010001', product_id: 1, quantity: 2, unit_price: 1899, cost_price: 1500 }
  ],
  purchase_orders: [
    { purchase_order_id: 'PO202606010001', supplier_id: 2, create_time: '2026-06-01 14:00:00', expected_date: '2026-06-05', status: '待收货' }
  ],
  purchase_order_items: [
    { item_id: 1, purchase_order_id: 'PO202606010001', product_id: 2, quantity: 10, unit_price: 2000 }
  ],
  inventory_logs: [
    { log_id: 1, product_id: 1, relate_order_id: 'SO202606010001', change_type: '销售出库', change_qty: -2, before_quantity: 12, after_quantity: 10, operator: 'cashier', operate_time: '2026-06-01 10:35:00', remark: '销售订单出库' }
  ],
  financial_records: [
    { record_id: 1, type: '收入', amount: 3798, relate_order_id: 'SO202606010001', occur_time: '2026-06-01 10:35:00', remark: '销售收款' }
  ],
  product_edit_logs: []
};