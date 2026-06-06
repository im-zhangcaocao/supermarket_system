import mockData from '../api/newMockData.js';

const DB_KEY = 'supermarket_db';
const DB_BACKUP_KEY = 'supermarket_db_backup';
const DB_VERSION_KEY = 'supermarket_db_version';

// 当前数据库版本
const CURRENT_VERSION = 1;

// 自动保存延迟（毫秒）
const AUTO_SAVE_DELAY = 500;

// 保存超时
let saveTimeout = null;

// 数据库初始化状态
let dbInitialized = false;

// 默认数据表结构
const defaultTables = {
  users: [],
  customers: [],
  products: [],
  suppliers: [],
  sales_orders: [],
  sales_order_items: [],
  purchase_orders: [],
  purchase_order_items: [],
  purchase_receipts: [],
  purchase_receipt_items: [],
  replenishment_advice: [],
  inventory_logs: [],
  financial_records: [],
  product_edit_logs: [],
  operation_logs: []
};

/**
 * 初始化数据库
 */
function initDB() {
  try {
    // 检查是否需要备份现有数据
    const existingData = localStorage.getItem(DB_KEY);
    if (existingData) {
      try {
        const parsedData = JSON.parse(existingData);
        localStorage.setItem(DB_BACKUP_KEY, JSON.stringify({
          timestamp: new Date().toISOString(),
          data: parsedData
        }));
        console.log('Database backup created');
      } catch (e) {
        console.warn('Failed to create backup:', e);
      }
    }

    // 初始化新数据库
    const db = {
      version: CURRENT_VERSION,
      ...defaultTables,
      ...mockData
    };
    
    // 合并现有数据（如果有）
    if (existingData) {
      try {
        const existingDb = JSON.parse(existingData);
        // 保留用户数据，但使用新的结构
        Object.keys(defaultTables).forEach(key => {
          if (existingDb[key] && existingDb[key].length > 0) {
            db[key] = existingDb[key];
          }
        });
      } catch (e) {
        console.warn('Failed to merge existing data:', e);
      }
    }

    saveDB(db);
    dbInitialized = true;
    console.log('Database initialized successfully');
    return db;
  } catch (error) {
    console.error('Failed to initialize database:', error);
    throw new Error('Database initialization failed');
  }
}

/**
 * 获取数据库
 */
function getDB() {
  try {
    const data = localStorage.getItem(DB_KEY);
    
    if (!data) {
      return initDB();
    }

    try {
      const db = JSON.parse(data);
      
      // 检查版本并升级
      if (!db.version || db.version < CURRENT_VERSION) {
        return upgradeDB(db);
      }
      
      // 确保所有表都存在
      Object.keys(defaultTables).forEach(key => {
        if (!Array.isArray(db[key])) {
          db[key] = defaultTables[key];
        }
      });
      
      dbInitialized = true;
      return db;
    } catch (parseError) {
      console.warn('Database corrupted, trying to restore from backup:', parseError);
      
      // 尝试从备份恢复
      const backup = localStorage.getItem(DB_BACKUP_KEY);
      if (backup) {
        try {
          const backupData = JSON.parse(backup);
          console.log('Restoring from backup created at:', backupData.timestamp);
          saveDB(backupData.data);
          return backupData.data;
        } catch (backupError) {
          console.error('Failed to restore backup:', backupError);
        }
      }
      
      // 重新初始化
      return initDB();
    }
  } catch (error) {
    console.error('Failed to get database:', error);
    throw new Error('Failed to access database');
  }
}

/**
 * 升级数据库
 */
function upgradeDB(oldDb) {
  console.log('Upgrading database from version', oldDb.version || 0, 'to', CURRENT_VERSION);
  
  const newDb = {
    version: CURRENT_VERSION,
    ...defaultTables,
    ...oldDb
  };
  
  // 确保所有表都存在
  Object.keys(defaultTables).forEach(key => {
    if (!Array.isArray(newDb[key])) {
      newDb[key] = defaultTables[key];
    }
  });
  
  saveDB(newDb);
  return newDb;
}

/**
 * 保存数据库（同步）
 */
function saveDB(data) {
  try {
    // 验证数据完整性
    if (!data || typeof data !== 'object') {
      throw new Error('Invalid database data');
    }

    const serializedData = JSON.stringify(data);
    
    // 检查数据大小（localStorage 限制约 5MB）
    if (serializedData.length > 4 * 1024 * 1024) { // 4MB 警告
      console.warn('Database size is approaching localStorage limit');
    }
    
    localStorage.setItem(DB_KEY, serializedData);
    localStorage.setItem(DB_VERSION_KEY, String(CURRENT_VERSION));
    
    return true;
  } catch (error) {
    console.error('Failed to save database:', error);
    throw new Error('Failed to save database');
  }
}

/**
 * 延迟保存（防抖）
 */
function saveDBAsync(data) {
  if (saveTimeout) {
    clearTimeout(saveTimeout);
  }
  
  saveTimeout = setTimeout(() => {
    try {
      saveDB(data);
      console.log('Database saved successfully');
    } catch (error) {
      console.error('Async save failed:', error);
    }
  }, AUTO_SAVE_DELAY);
}

/**
 * 获取表
 */
function getTable(tableName) {
  const db = getDB();
  return db[tableName] || [];
}

/**
 * 保存表（同步）
 */
function saveTable(tableName, data) {
  try {
    if (!Array.isArray(data)) {
      throw new Error('Table data must be an array');
    }

    const db = getDB();
    db[tableName] = data;
    saveDB(db);
    
    return true;
  } catch (error) {
    console.error(`Failed to save table ${tableName}:`, error);
    throw new Error(`Failed to save ${tableName}`);
  }
}

/**
 * 保存表（异步延迟）
 */
function saveTableAsync(tableName, data) {
  if (!Array.isArray(data)) {
    throw new Error('Table data must be an array');
  }

  const db = getDB();
  db[tableName] = data;
  saveDBAsync(db);
}

/**
 * 更新单个记录
 */
function updateRecord(tableName, idField, recordId, updates) {
  const table = getTable(tableName);
  const index = table.findIndex(r => r[idField] === recordId);
  
  if (index === -1) {
    throw new Error(`Record not found in ${tableName}`);
  }

  const updatedTable = [...table];
  updatedTable[index] = { ...updatedTable[index], ...updates };
  saveTable(tableName, updatedTable);
  
  return updatedTable[index];
}

/**
 * 添加记录
 */
function addRecord(tableName, record) {
  const table = getTable(tableName);
  const newTable = [...table, record];
  saveTable(tableName, newTable);
  return record;
}

/**
 * 删除记录
 */
function deleteRecord(tableName, idField, recordId) {
  const table = getTable(tableName);
  const filteredTable = table.filter(r => r[idField] !== recordId);
  saveTable(tableName, filteredTable);
  return true;
}

/**
 * 创建备份
 */
function createBackup() {
  try {
    const db = getDB();
    const backup = {
      timestamp: new Date().toISOString(),
      version: CURRENT_VERSION,
      data: db
    };
    localStorage.setItem(DB_BACKUP_KEY, JSON.stringify(backup));
    console.log('Manual backup created');
    return backup;
  } catch (error) {
    console.error('Failed to create backup:', error);
    throw new Error('Failed to create backup');
  }
}

/**
 * 从备份恢复
 */
function restoreFromBackup() {
  try {
    const backupData = localStorage.getItem(DB_BACKUP_KEY);
    if (!backupData) {
      throw new Error('No backup found');
    }
    
    const backup = JSON.parse(backupData);
    saveDB(backup.data);
    console.log('Database restored from backup:', backup.timestamp);
    return backup;
  } catch (error) {
    console.error('Failed to restore backup:', error);
    throw new Error('Failed to restore backup');
  }
}

/**
 * 导出数据库
 */
function exportDatabase() {
  try {
    const db = getDB();
    const exportData = {
      exportTime: new Date().toISOString(),
      version: CURRENT_VERSION,
      data: db
    };
    return JSON.stringify(exportData, null, 2);
  } catch (error) {
    console.error('Failed to export database:', error);
    throw new Error('Failed to export database');
  }
}

/**
 * 导入数据库
 */
function importDatabase(importDataStr) {
  try {
    const importData = JSON.parse(importDataStr);
    
    if (!importData.data) {
      throw new Error('Invalid import format');
    }
    
    // 创建备份
    createBackup();
    
    // 验证数据结构
    const db = {
      version: CURRENT_VERSION,
      ...defaultTables,
      ...importData.data
    };
    
    saveDB(db);
    console.log('Database imported successfully');
    return true;
  } catch (error) {
    console.error('Failed to import database:', error);
    throw new Error('Failed to import database');
  }
}

/**
 * 清空数据库（用于测试）
 */
function clearDatabase() {
  try {
    createBackup(); // 先备份
    localStorage.removeItem(DB_KEY);
    localStorage.removeItem(DB_VERSION_KEY);
    dbInitialized = false;
    initDB();
    console.log('Database cleared and reinitialized');
    return true;
  } catch (error) {
    console.error('Failed to clear database:', error);
    throw new Error('Failed to clear database');
  }
}

/**
 * 获取数据库状态
 */
function getDatabaseStatus() {
  const db = getDB();
  const backupData = localStorage.getItem(DB_BACKUP_KEY);
  let backupInfo = null;
  
  if (backupData) {
    try {
      const backup = JSON.parse(backupData);
      backupInfo = {
        timestamp: backup.timestamp,
        version: backup.version
      };
    } catch (e) {
      // 忽略
    }
  }
  
  return {
    version: db.version || CURRENT_VERSION,
    size: JSON.stringify(db).length,
    tables: Object.keys(defaultTables).map(key => ({
      name: key,
      count: (db[key] || []).length
    })),
    backup: backupInfo
  };
}

// 页面卸载前强制保存
window.addEventListener('beforeunload', (event) => {
  if (saveTimeout) {
    clearTimeout(saveTimeout);
    try {
      const db = getDB();
      saveDB(db);
      console.log('Database saved before unload');
    } catch (error) {
      console.error('Failed to save database before unload:', error);
    }
  }
});

// 监听 storage 变化（多标签页同步）
window.addEventListener('storage', (event) => {
  if (event.key === DB_KEY && event.newValue !== event.oldValue) {
    console.log('Database updated from another tab');
    // 可以在这里触发数据刷新事件
  }
});

export {
  getDB,
  saveDB,
  saveDBAsync,
  getTable,
  saveTable,
  saveTableAsync,
  updateRecord,
  addRecord,
  deleteRecord,
  initDB,
  createBackup,
  restoreFromBackup,
  exportDatabase,
  importDatabase,
  clearDatabase,
  getDatabaseStatus
};
