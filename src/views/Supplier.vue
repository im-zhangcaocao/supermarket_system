<template>
  <div class="supplier-container">
    <h2 class="page-title">供应商管理</h2>
    
    <div class="toolbar">
      <div class="filter-group">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索供应商名称..."
          prefix-icon="Search"
          clearable
          style="width: 250px; margin-right: 10px"
          @input="handleSearch"
        />
        <el-select v-model="sortBy" placeholder="排序字段" style="width: 140px; margin-right: 10px">
          <el-option label="供应商ID" value="supplier_id" />
          <el-option label="供应商名称" value="supplier_name" />
          <el-option label="准时交付率" value="on_time_rate" />
          <el-option label="平均交付天数" value="average_delivery_days" />
          <el-option label="合格率" value="quality_rate" />
        </el-select>
        <el-button-group>
          <el-button 
            :type="sortOrder === 'asc' ? 'primary' : 'default'" 
            size="small"
            @click="setSortOrder('asc')"
          >
            <el-icon><ArrowUp /></el-icon>
            升序
          </el-button>
          <el-button 
            :type="sortOrder === 'desc' ? 'primary' : 'default'" 
            size="small"
            @click="setSortOrder('desc')"
          >
            <el-icon><ArrowDown /></el-icon>
            降序
          </el-button>
        </el-button-group>
      </div>
      <el-button type="primary" @click="openAddDialog">
        添加供应商
      </el-button>
    </div>
    
    <el-table :data="displaySuppliers" border stripe style="width: 100%">
      <el-table-column prop="supplier_id" label="供应商ID" width="100" />
      <el-table-column prop="supplier_name" label="供应商名称" width="180" />
      <el-table-column prop="contact_person" label="联系人" width="100" />
      <el-table-column prop="contact_phone" label="联系电话" width="130" />
      <el-table-column prop="address" label="地址" min-width="150" />
      <el-table-column label="准时交付率" width="140">
        <template #default="{ row }">
          <div class="kpi-cell">
            <el-progress 
              :percentage="row.on_time_rate || 0" 
              :color="getRateColor(row.on_time_rate)"
              :show-text="false"
              stroke-width="8"
            />
            <span :style="{ color: getRateColor(row.on_time_rate) }">
              {{ row.on_time_rate || 0 }}%
            </span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="average_delivery_days" label="平均交付天数" width="120">
        <template #default="{ row }">
          <span :class="{ 'highlight': row.average_delivery_days > 0 }">
            {{ row.average_delivery_days || 0 }} 天
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="last_order_date" label="最近采购日期" width="140">
        <template #default="{ row }">
          {{ row.last_order_date || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="产品合格率" width="140">
        <template #default="{ row }">
          <div class="kpi-cell">
            <el-progress 
              :percentage="row.quality_rate || 0" 
              :color="getQualityRateColor(row.quality_rate)"
              :show-text="false"
              stroke-width="8"
            />
            <span :style="{ color: getQualityRateColor(row.quality_rate) }">
              {{ row.quality_rate || 0 }}%
            </span>
            <span v-if="row.total_inspected > 0" class="inspected-count">
              ({{ row.quality_count }}/{{ row.total_inspected }})
            </span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">
            {{ row.status === 1 ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="openEditDialog(row)">
            编辑
          </el-button>
          <el-button type="danger" link size="small" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50]"
        :total="filteredSuppliers.length"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
    
    <!-- 添加/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑供应商' : '添加供应商'"
      width="450px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="供应商名称" prop="supplier_name">
          <el-input v-model="form.supplier_name" placeholder="请输入供应商名称" />
        </el-form-item>
        <el-form-item label="联系人" prop="contact_person">
          <el-input v-model="form.contact_person" placeholder="请输入联系人" />
        </el-form-item>
        <el-form-item label="联系电话" prop="contact_phone">
          <el-input v-model="form.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="form.address" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :label="1">启用</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox, ElTag } from 'element-plus';
import { ArrowUp, ArrowDown } from '@element-plus/icons-vue';
import { getSuppliers, addSupplier, updateSupplier, deleteSupplier } from '../api/realApi';

const suppliers = ref([]);
const searchKeyword = ref('');
const currentPage = ref(1);
const pageSize = ref(10);
const sortBy = ref('supplier_id');
const sortOrder = ref('desc');
const dialogVisible = ref(false);
const isEdit = ref(false);
const formRef = ref(null);
const editingId = ref(null);

const form = reactive({
  supplier_name: '',
  contact_person: '',
  contact_phone: '',
  address: '',
  status: 1
});

const formRules = {
  supplier_name: [{ required: true, message: '请输入供应商名称', trigger: 'blur' }],
  contact_person: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
  contact_phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
  address: [{ required: true, message: '请输入地址', trigger: 'blur' }]
};

const filteredSuppliers = computed(() => {
  let result = suppliers.value;
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase();
    result = result.filter(s => 
      s.supplier_name.toLowerCase().includes(keyword)
    );
  }
  
  return result;
});

const displaySuppliers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredSuppliers.value.slice(start, end);
});

function getRateColor(rate) {
  if (!rate || rate < 60) return '#f56c6c';
  if (rate < 80) return '#e6a23c';
  return '#67c23a';
}

function getQualityRateColor(rate) {
  return getRateColor(rate);
}

async function loadSuppliers() {
  try {
    const data = await getSuppliers({
      sort_by: sortBy.value,
      sort_order: sortOrder.value
    });
    suppliers.value = data;
  } catch (error) {
    ElMessage.error('加载供应商失败');
  }
}

function setSortOrder(order) {
  sortOrder.value = order;
  loadSuppliers();
}

function handleSearch() {
  currentPage.value = 1;
}

function handleSizeChange() {
  currentPage.value = 1;
}

function handlePageChange() {}

function openAddDialog() {
  isEdit.value = false;
  editingId.value = null;
  resetForm();
  dialogVisible.value = true;
}

function openEditDialog(row) {
  isEdit.value = true;
  editingId.value = row.supplier_id;
  Object.assign(form, {
    supplier_name: row.supplier_name,
    contact_person: row.contact_person,
    contact_phone: row.contact_phone,
    address: row.address,
    status: row.status
  });
  dialogVisible.value = true;
}

function resetForm() {
  Object.assign(form, {
    supplier_name: '',
    contact_person: '',
    contact_phone: '',
    address: '',
    status: 1
  });
  formRef.value?.clearValidate();
}

async function handleSubmit() {
  try {
    await formRef.value.validate();
  } catch {
    return;
  }
  
  try {
    if (isEdit.value) {
      await updateSupplier(editingId.value, { ...form });
      ElMessage.success('更新成功');
    } else {
      await addSupplier({ ...form });
      ElMessage.success('添加成功');
    }
    dialogVisible.value = false;
    await loadSuppliers();
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '添加失败');
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除供应商 "${row.supplier_name}" 吗？`,
      '确认删除',
      { type: 'warning' }
    );
    
    const result = await deleteSupplier(row.supplier_id);
    
    if (!result.canDelete) {
      ElMessage.warning(result.message);
      return;
    }
    
    ElMessage.success('删除成功');
    await loadSuppliers();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败');
    }
  }
}

onMounted(() => {
  loadSuppliers();
});
</script>

<style scoped>
.supplier-container {
  padding: 20px;
}

.page-title {
  margin: 0 0 20px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.filter-group {
  display: flex;
  align-items: center;
}

.kpi-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.inspected-count {
  font-size: 12px;
  color: #909399;
}

.highlight {
  color: #67c23a;
  font-weight: 500;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>