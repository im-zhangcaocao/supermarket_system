<template>
  <div class="employee-container">
    <h2 class="page-title">员工管理</h2>
    
    <div class="toolbar">
      <div class="filter-group">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索用户名或姓名..."
          prefix-icon="Search"
          clearable
          style="width: 250px"
          @input="handleSearch"
        />
        <el-select v-model="roleFilter" placeholder="角色" clearable style="width: 120px; margin-left: 10px">
          <el-option label="收银员" value="cashier" />
          <el-option label="采购员" value="purchaser" />
          <el-option label="管理员" value="admin" />
        </el-select>
      </div>
      <el-button type="primary" @click="openAddDialog">
        添加员工
      </el-button>
    </div>
    
    <el-table :data="displayEmployees" border stripe style="width: 100%">
      <el-table-column prop="user_id" label="用户ID" width="80" />
      <el-table-column prop="username" label="用户名" width="120" />
      <el-table-column prop="real_name" label="真实姓名" width="120" />
      <el-table-column prop="phone" label="联系电话" width="140" />
      <el-table-column label="角色" width="100">
        <template #default="{ row }">
          <el-tag :type="getRoleType(row.role)" size="small">
            {{ getRoleText(row.role) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="薪资类型" width="100">
        <template #default="{ row }">
          {{ row.salary_type === 'hourly' ? '时薪' : '月薪' }}
        </template>
      </el-table-column>
      <el-table-column label="薪资标准" width="120">
        <template #default="{ row }">
          ¥{{ row.salary_rate || 0 }}
          {{ row.salary_type === 'hourly' ? '/小时' : '/月' }}
        </template>
      </el-table-column>
      <el-table-column prop="hire_date" label="入职日期" width="120" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">
            {{ row.status === 1 ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="last_login" label="最后登录" width="160">
        <template #default="{ row }">
          {{ row.last_login || '从未登录' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="300" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="viewDetail(row)">
            详情
          </el-button>
          <el-button type="warning" link size="small" @click="openEditDialog(row)">
            编辑
          </el-button>
          <el-button 
            :type="row.status === 1 ? 'danger' : 'success'" 
            link 
            size="small" 
            @click="toggleStatus(row)"
          >
            {{ row.status === 1 ? '禁用' : '启用' }}
          </el-button>
          <el-button 
            type="info" 
            link 
            size="small" 
            @click="handleResetPassword(row)"
          >
            重置密码
          </el-button>
          <el-button 
            type="danger" 
            link 
            size="small" 
            @click="handleDelete(row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="[10, 20, 50, 100]"
      :total="employees.length"
      layout="total, sizes, prev, pager, next, jumper"
      style="margin-top: 20px; justify-content: flex-end"
    />

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingEmployee ? '编辑员工' : '添加员工'"
      width="500px"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="formData.username" :disabled="!!editingEmployee" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!editingEmployee">
          <el-input v-model="formData.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="formData.real_name" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="formData.phone" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="formData.role" style="width: 100%">
            <el-option label="收银员" value="cashier" />
            <el-option label="采购员" value="purchaser" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="入职日期" prop="hire_date">
          <el-date-picker
            v-model="formData.hire_date"
            type="date"
            placeholder="选择入职日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="薪资类型" prop="salary_type">
          <el-radio-group v-model="formData.salary_type">
            <el-radio value="hourly">时薪</el-radio>
            <el-radio value="monthly">月薪</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="薪资标准" prop="salary_rate">
          <el-input-number v-model="formData.salary_rate" :min="0" :step="10" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="员工详情" width="500px">
      <div v-if="selectedEmployee" class="detail-content">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="用户ID">{{ selectedEmployee.user_id }}</el-descriptions-item>
          <el-descriptions-item label="用户名">{{ selectedEmployee.username }}</el-descriptions-item>
          <el-descriptions-item label="真实姓名">{{ selectedEmployee.real_name }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ selectedEmployee.phone }}</el-descriptions-item>
          <el-descriptions-item label="角色">{{ getRoleText(selectedEmployee.role) }}</el-descriptions-item>
          <el-descriptions-item label="入职日期">{{ selectedEmployee.hire_date }}</el-descriptions-item>
          <el-descriptions-item label="薪资类型">
            {{ selectedEmployee.salary_type === 'hourly' ? '时薪' : '月薪' }}
          </el-descriptions-item>
          <el-descriptions-item label="薪资标准">
            ¥{{ selectedEmployee.salary_rate }}
            {{ selectedEmployee.salary_type === 'hourly' ? '/小时' : '/月' }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="selectedEmployee.status === 1 ? 'success' : 'info'" size="small">
              {{ selectedEmployee.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="最后登录">{{ selectedEmployee.last_login || '从未登录' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { 
  getEmployees, 
  addEmployee, 
  updateEmployee,
  resetUserPassword,
  deleteEmployee
} from '../api/realApi';

const employees = ref([]);
const searchKeyword = ref('');
const roleFilter = ref('');
const currentPage = ref(1);
const pageSize = ref(10);
const dialogVisible = ref(false);
const detailDialogVisible = ref(false);
const editingEmployee = ref(null);
const selectedEmployee = ref(null);
const formRef = ref(null);

const formData = reactive({
  username: '',
  password: '',
  real_name: '',
  phone: '',
  role: 'cashier',
  hire_date: '',
  salary_type: 'monthly',
  salary_rate: 5000
});

const formRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  real_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  hire_date: [{ required: true, message: '请选择入职日期', trigger: 'change' }],
  salary_rate: [{ required: true, message: '请输入薪资标准', trigger: 'blur' }]
};

const displayEmployees = computed(() => {
  let filtered = employees.value;
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase();
    filtered = filtered.filter(emp => 
      emp.username.toLowerCase().includes(keyword) || 
      emp.real_name.toLowerCase().includes(keyword)
    );
  }
  
  if (roleFilter.value) {
    filtered = filtered.filter(emp => emp.role === roleFilter.value);
  }
  
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filtered.slice(start, end);
});

async function loadEmployees() {
  try {
    const data = await getEmployees();
    employees.value = data;
  } catch (error) {
    ElMessage.error('加载员工列表失败');
  }
}

function getRoleText(role) {
  const roleMap = {
    'cashier': '收银员',
    'purchaser': '采购员',
    'admin': '管理员'
  };
  return roleMap[role] || role;
}

function getRoleType(role) {
  const typeMap = {
    'cashier': '',
    'purchaser': 'warning',
    'admin': 'danger'
  };
  return typeMap[role] || '';
}

function handleSearch() {
  currentPage.value = 1;
}

function openAddDialog() {
  editingEmployee.value = null;
  Object.assign(formData, {
    username: '',
    password: '',
    real_name: '',
    phone: '',
    role: 'cashier',
    hire_date: '',
    salary_type: 'monthly',
    salary_rate: 5000
  });
  dialogVisible.value = true;
}

function openEditDialog(employee) {
  editingEmployee.value = employee;
  Object.assign(formData, {
    username: employee.username,
    password: '',
    real_name: employee.real_name,
    phone: employee.phone,
    role: employee.role,
    hire_date: employee.hire_date,
    salary_type: employee.salary_type || 'monthly',
    salary_rate: employee.salary_rate || 5000
  });
  dialogVisible.value = true;
}

async function submitForm() {
  if (!formRef.value) return;
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (editingEmployee.value) {
          await updateEmployee(editingEmployee.value.user_id, formData);
          ElMessage.success('更新成功');
        } else {
          await addEmployee(formData);
          ElMessage.success('添加成功');
        }
        dialogVisible.value = false;
        loadEmployees();
      } catch (error) {
        ElMessage.error(error.message || '操作失败');
      }
    }
  });
}

async function toggleStatus(employee) {
  try {
    const newStatus = employee.status === 1 ? 0 : 1;
    await updateEmployee(employee.user_id, { status: newStatus });
    ElMessage.success(`已${newStatus === 1 ? '启用' : '禁用'}该员工`);
    loadEmployees();
  } catch (error) {
    ElMessage.error('操作失败');
  }
}

async function handleResetPassword(employee) {
  try {
    const result = await ElMessageBox.confirm(
      `确定要重置员工「${employee.real_name || employee.username}」的密码吗？\n重置后的密码为：用户名+123456\n用户首次登录时将强制要求修改密码。`,
      '确认重置密码',
      {
        confirmButtonText: '确定重置',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    
    if (result === 'confirm') {
      const response = await resetUserPassword(employee.user_id);
      if (response.success) {
        ElMessage.success(`密码重置成功！\n新密码：${response.new_password}\n请告知用户首次登录需修改密码`);
        loadEmployees();
      } else {
        ElMessage.error(response.message || '密码重置失败');
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败');
    }
  }
}

async function handleDelete(employee) {
  try {
    const result = await ElMessageBox.confirm(
      `确定要删除员工「${employee.real_name || employee.username}」吗？\n此操作将无法撤销！`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'danger'
      }
    );
    
    if (result === 'confirm') {
      const response = await deleteEmployee(employee.user_id);
      if (response.success) {
        ElMessage.success('删除成功');
        loadEmployees();
      } else {
        ElMessage.error(response.message || '删除失败');
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败');
    }
  }
}

function viewDetail(employee) {
  selectedEmployee.value = employee;
  detailDialogVisible.value = true;
}

onMounted(() => {
  loadEmployees();
});
</script>

<style scoped>
.employee-container {
  padding: 20px;
}

.page-title {
  margin-bottom: 20px;
  color: #333;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.filter-group {
  display: flex;
  align-items: center;
}

.detail-content {
  padding: 10px 0;
}
</style>
