<template>
  <div class="supplier-container">
    <h2 class="page-title">供应商管理</h2>
    
    <div class="toolbar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索供应商名称..."
        prefix-icon="Search"
        clearable
        style="width: 250px"
        @input="handleSearch"
      />
      <el-button type="primary" @click="openAddDialog">
        添加供应商
      </el-button>
    </div>
    
    <el-table :data="displaySuppliers" border stripe style="width: 100%">
      <el-table-column prop="supplier_id" label="供应商ID" width="100" />
      <el-table-column prop="supplier_name" label="供应商名称" width="180" />
      <el-table-column prop="contact_person" label="联系人" width="120" />
      <el-table-column prop="contact_phone" label="联系电话" width="150" />
      <el-table-column prop="address" label="地址" min-width="150" />
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
import { ElMessage, ElMessageBox } from 'element-plus';
import { getSuppliers, addSupplier, updateSupplier, deleteSupplier } from '../api/mockApi';

const suppliers = ref([]);
const searchKeyword = ref('');
const currentPage = ref(1);
const pageSize = ref(10);
const dialogVisible = ref(false);
const isEdit = ref(false);
const formRef = ref(null);
const editingId = ref(null);

const form = reactive({
  supplier_name: '',
  contact_person: '',
  contact_phone: '',
  address: ''
});

const formRules = {
  supplier_name: [{ required: true, message: '请输入供应商名称', trigger: 'blur' }],
  contact_person: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
  contact_phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
  address: [{ required: true, message: '请输入地址', trigger: 'blur' }]
};

const filteredSuppliers = computed(() => {
  if (!searchKeyword.value) return suppliers.value;
  const keyword = searchKeyword.value.toLowerCase();
  return suppliers.value.filter(s => 
    s.supplier_name.toLowerCase().includes(keyword)
  );
});

const displaySuppliers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredSuppliers.value.slice(start, end);
});

async function loadSuppliers() {
  try {
    suppliers.value = await getSuppliers();
  } catch (error) {
    ElMessage.error('加载供应商失败');
  }
}

function handleSearch() {
  currentPage.value = 1;
}

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
    address: row.address
  });
  dialogVisible.value = true;
}

function resetForm() {
  Object.assign(form, {
    supplier_name: '',
    contact_person: '',
    contact_phone: '',
    address: ''
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
  margin-bottom: 16px;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>