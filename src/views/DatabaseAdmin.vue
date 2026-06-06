<template>
  <div class="data-admin">
    <h2 class="page-title">数据管理</h2>
    
    <el-card class="status-card">
      <template #header>
        <div class="card-header">
          <span>数据库状态</span>
        </div>
      </template>
      
      <el-descriptions :column="2" border v-if="dbStatus">
        <el-descriptions-item label="数据库版本">{{ dbStatus.version }}</el-descriptions-item>
        <el-descriptions-item label="数据大小">
          {{ formatSize(dbStatus.size) }}
        </el-descriptions-item>
        <el-descriptions-item label="备份状态">
          <el-tag v-if="dbStatus.backup" type="success">已有备份</el-tag>
          <el-tag v-else type="info">无备份</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="备份时间">
          {{ dbStatus.backup ? formatDate(dbStatus.backup.timestamp) : '-' }}
        </el-descriptions-item>
      </el-descriptions>
      
      <el-divider></el-divider>
      
      <h4>数据表统计</h4>
      <el-table :data="dbStatus?.tables || []" border style="width: 100%; margin-top: 10px;">
        <el-table-column prop="name" label="表名" width="200"></el-table-column>
        <el-table-column prop="count" label="记录数" width="150">
          <template #default="{ row }">
            <el-tag type="info">{{ row.count }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-card class="operations-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>数据库操作</span>
        </div>
      </template>
      
      <el-space wrap>
        <el-button type="primary" @click="handleCreateBackup" :loading="loading.backup">
          <span class="btn-icon">💾</span>
          创建备份
        </el-button>
        
        <el-button type="warning" @click="handleRestoreBackup" :disabled="!dbStatus?.backup" :loading="loading.restore">
          <span class="btn-icon">↩️</span>
          恢复备份
        </el-button>
        
        <el-button type="info" @click="handleExportDatabase" :loading="loading.export">
          <span class="btn-icon">📤</span>
          导出数据
        </el-button>
        
        <el-upload
          class="upload-demo"
          :show-file-list="false"
          :before-upload="handleImportDatabase"
          :auto-upload="false"
          accept=".json"
        >
          <el-button type="success" :loading="loading.import">
            <span class="btn-icon">📥</span>
            导入数据
          </el-button>
        </el-upload>
        
        <el-button type="danger" @click="handleClearDatabase" :loading="loading.clear">
          <span class="btn-icon">🗑️</span>
          清空数据库
        </el-button>
        
        <el-button type="warning" @click="handleReinitializeData" :loading="loading.reinit">
          <span class="btn-icon">🔄</span>
          重新初始化数据
        </el-button>
      </el-space>
    </el-card>
    
    <el-card class="logs-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>操作日志</span>
        </div>
      </template>
      
      <el-table :data="operationLogs" border style="width: 100%;" max-height="400">
        <el-table-column prop="operate_time" label="时间" width="180"></el-table-column>
        <el-table-column prop="operator" label="操作人" width="120"></el-table-column>
        <el-table-column prop="operation_type" label="操作类型" width="150"></el-table-column>
        <el-table-column prop="remark" label="备注"></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  getDatabaseStatus,
  createBackup,
  restoreFromBackup,
  exportDatabase,
  importDatabase,
  clearDatabase,
  getTable
} from '../utils/database.js';

const dbStatus = ref(null);
const operationLogs = ref([]);
const loading = ref({
  backup: false,
  restore: false,
  export: false,
  import: false,
  clear: false,
  reinit: false
});

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

function formatDate(dateStr) {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
  return date.toLocaleString('zh-CN');
}

function loadDatabaseStatus() {
  try {
    dbStatus.value = getDatabaseStatus();
    loadOperationLogs();
  } catch (error) {
    ElMessage.error('获取数据库状态失败');
    console.error(error);
  }
}

function loadOperationLogs() {
  try {
    const logs = getTable('operation_logs');
    operationLogs.value = logs.slice(-50).reverse(); // 显示最新的50条
  } catch (error) {
    console.error('加载操作日志失败', error);
  }
}

async function handleCreateBackup() {
  try {
    loading.value.backup = true;
    await createBackup();
    ElMessage.success('备份创建成功');
    loadDatabaseStatus();
  } catch (error) {
    ElMessage.error('备份创建失败');
    console.error(error);
  } finally {
    loading.value.backup = false;
  }
}

async function handleRestoreBackup() {
  try {
    await ElMessageBox.confirm(
      '确定要从备份恢复数据库吗？此操作将覆盖当前数据！',
      '恢复确认',
      {
        confirmButtonText: '确定恢复',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    );
    
    loading.value.restore = true;
    await restoreFromBackup();
    ElMessage.success('数据库恢复成功');
    loadDatabaseStatus();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('恢复失败');
      console.error(error);
    }
  } finally {
    loading.value.restore = false;
  }
}

async function handleExportDatabase() {
  try {
    loading.value.export = true;
    const data = exportDatabase();
    
    // 创建下载
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `supermarket-backup-${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    ElMessage.success('数据库导出成功');
  } catch (error) {
    ElMessage.error('导出失败');
    console.error(error);
  } finally {
    loading.value.export = false;
  }
}

async function handleImportDatabase(file) {
  try {
    const text = await file.text();
    
    await ElMessageBox.confirm(
      '确定要导入此文件吗？此操作将覆盖当前数据！',
      '导入确认',
      {
        confirmButtonText: '确定导入',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    );
    
    loading.value.import = true;
    await importDatabase(text);
    ElMessage.success('数据库导入成功');
    loadDatabaseStatus();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('导入失败');
      console.error(error);
    }
  } finally {
    loading.value.import = false;
  }
  return false; // 阻止默认上传行为
}

async function handleClearDatabase() {
  try {
    await ElMessageBox.confirm(
      '确定要清空数据库吗？此操作将删除所有数据，需要手动重新初始化！',
      '清空确认',
      {
        confirmButtonText: '确定清空',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    );
    
    loading.value.clear = true;
    localStorage.removeItem('supermarket_db');
    localStorage.removeItem('supermarket_db_backup');
    localStorage.removeItem('supermarket_db_version');
    ElMessage.success('数据库清空成功');
    loadDatabaseStatus();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空失败');
      console.error(error);
    }
  } finally {
    loading.value.clear = false;
  }
}

async function handleReinitializeData() {
  try {
    await ElMessageBox.confirm(
      '确定要重新初始化数据库吗？\n\n此操作将：\n1. 清除所有现有数据\n2. 重新创建10条模拟数据记录\n3. 验证数据完整性\n\n所有数据表将被重置为初始状态！',
      '重新初始化确认',
      {
        confirmButtonText: '确定初始化',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    );
    
    loading.value.reinit = true;
    
    // 清除现有数据
    localStorage.removeItem('supermarket_db');
    localStorage.removeItem('supermarket_db_backup');
    localStorage.removeItem('supermarket_db_version');
    
    // 重新初始化（会自动加载新的mock数据）
    const db = getDatabaseStatus();
    
    ElMessage.success('数据库重新初始化成功！');
    loadDatabaseStatus();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('初始化失败');
      console.error(error);
    }
  } finally {
    loading.value.reinit = false;
  }
}

onMounted(() => {
  loadDatabaseStatus();
});
</script>

<style scoped>
.data-admin {
  padding: 20px;
}

.page-title {
  margin: 0 0 20px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-icon {
  margin-right: 4px;
}

.status-card,
.operations-card,
.logs-card {
  margin-bottom: 20px;
}
</style>
