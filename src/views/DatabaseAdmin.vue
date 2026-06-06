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
          <el-tag type="success">后端存储</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="存储方式">
          <el-tag type="info">SQLite 数据库</el-tag>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  getDatabaseStatus,
  createBackup,
  exportDatabase,
  importDatabase,
  clearDatabase,
  reinitializeDatabase
} from '../api/dbApi';

const dbStatus = ref(null);
const loading = ref({
  backup: false,
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

async function loadDatabaseStatus() {
  try {
    dbStatus.value = await getDatabaseStatus();
  } catch (error) {
    ElMessage.error('获取数据库状态失败');
    console.error(error);
  }
}

async function handleCreateBackup() {
  try {
    loading.value.backup = true;
    const success = await createBackup();
    if (success) {
      ElMessage.success('备份创建成功（已保存到服务器）');
    } else {
      ElMessage.error('备份创建失败');
    }
  } catch (error) {
    ElMessage.error('备份创建失败');
    console.error(error);
  } finally {
    loading.value.backup = false;
  }
}

async function handleExportDatabase() {
  try {
    loading.value.export = true;
    const data = await exportDatabase();
    
    if (data) {
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `supermarket-backup-${new Date().toISOString().slice(0, 10)}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      ElMessage.success('数据库导出成功');
    } else {
      ElMessage.error('导出失败');
    }
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
    let importData;
    
    try {
      importData = JSON.parse(text);
    } catch {
      ElMessage.error('无效的JSON文件');
      return false;
    }
    
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
    
    const importDataForBackend = importData.tables ? importData : importData.data;
    const success = await importDatabase(importDataForBackend);
    
    if (success) {
      ElMessage.success('数据库导入成功');
      loadDatabaseStatus();
    } else {
      ElMessage.error('导入失败');
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('导入失败');
      console.error(error);
    }
  } finally {
    loading.value.import = false;
  }
  return false;
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
    const success = await clearDatabase();
    
    if (success) {
      ElMessage.success('数据库清空成功');
      loadDatabaseStatus();
    } else {
      ElMessage.error('清空失败');
    }
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
      '确定要重新初始化数据库吗？\n\n此操作将：\n1. 清除所有现有数据\n2. 重新创建示例数据记录\n\n所有数据表将被重置为初始状态！',
      '重新初始化确认',
      {
        confirmButtonText: '确定初始化',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    );
    
    loading.value.reinit = true;
    const success = await reinitializeDatabase();
    
    if (success) {
      ElMessage.success('数据库重新初始化成功！');
      loadDatabaseStatus();
    } else {
      ElMessage.error('初始化失败');
    }
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
.operations-card {
  margin-bottom: 20px;
}
</style>