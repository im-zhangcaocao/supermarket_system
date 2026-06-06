import mockData from '../api/mockData.js';

const DB_KEY = 'supermarket_db';

function initDB() {
  const db = {
    users: mockData.users || [],
    customers: mockData.customers || [],
    products: mockData.products || [],
    suppliers: mockData.suppliers || [],
    sales_orders: mockData.sales_orders || [],
    sales_order_items: mockData.sales_order_items || [],
    purchase_orders: mockData.purchase_orders || [],
    purchase_order_items: mockData.purchase_order_items || [],
    inventory_logs: mockData.inventory_logs || [],
    financial_records: mockData.financial_records || []
  };
  localStorage.setItem(DB_KEY, JSON.stringify(db));
  return db;
}

function getDB() {
  const data = localStorage.getItem(DB_KEY);
  if (!data) {
    return initDB();
  }
  try {
    return JSON.parse(data);
  } catch {
    return initDB();
  }
}

function saveDB(data) {
  localStorage.setItem(DB_KEY, JSON.stringify(data));
}

function getTable(tableName) {
  const db = getDB();
  return db[tableName] || [];
}

function saveTable(tableName, data) {
  const db = getDB();
  db[tableName] = data;
  saveDB(db);
}

export {
  getDB,
  saveDB,
  getTable,
  saveTable,
  initDB
};