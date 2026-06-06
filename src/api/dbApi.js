import client from './client';

export async function getDatabaseStatus() {
  try {
    const data = await client.get('/db/status');
    if (data && typeof data === 'object') {
      return {
        version: '1.0',
        size: JSON.stringify(data).length,
        tables: Object.keys(data).map(key => ({
          name: key,
          count: data[key]
        })),
        backup: null
      };
    }
    return null;
  } catch (error) {
    console.error('获取数据库状态失败:', error);
    return null;
  }
}

export async function createBackup() {
  try {
    const res = await client.post('/db/backup');
    return res && (res.success === true || res.success === 'true');
  } catch (error) {
    console.error('创建备份失败:', error);
    return false;
  }
}

export async function restoreBackup(backupData) {
  try {
    const res = await client.post('/db/restore', { backup_data: backupData });
    return res && (res.success === true || res.success === 'true');
  } catch (error) {
    console.error('恢复备份失败:', error);
    return false;
  }
}

export async function exportDatabase() {
  try {
    const data = await client.get('/db/export');
    if (data && typeof data === 'object') {
      return data;
    }
    return null;
  } catch (error) {
    console.error('导出数据库失败:', error);
    return null;
  }
}

export async function importDatabase(data) {
  try {
    const res = await client.post('/db/import', data);
    return res && (res.success === true || res.success === 'true');
  } catch (error) {
    console.error('导入数据库失败:', error);
    return false;
  }
}

export async function clearDatabase() {
  try {
    const res = await client.post('/db/clear');
    return res && (res.success === true || res.success === 'true');
  } catch (error) {
    console.error('清空数据库失败:', error);
    return false;
  }
}

export async function reinitializeDatabase() {
  try {
    const res = await client.post('/db/reinit');
    return res && (res.success === true || res.success === 'true');
  } catch (error) {
    console.error('重新初始化数据库失败:', error);
    return false;
  }
}