<template>
  <div class="users-container">
    <h2 class="page-title">客户管理</h2>
    
    <div class="toolbar">
      <div class="filter-group">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索姓名/电话"
          prefix-icon="Search"
          clearable
          style="width: 200px"
          @input="handleSearch"
        />
        <el-select v-model="levelFilter" placeholder="会员等级" clearable style="width: 140px; margin-left: 10px">
          <el-option label="普通会员" value="普通会员" />
          <el-option label="白银会员" value="白银会员" />
          <el-option label="黄金会员" value="黄金会员" />
        </el-select>
      </div>
      <el-button type="primary" @click="openAddDialog">
        添加客户
      </el-button>
    </div>
    
    <el-table :data="displayCustomers" border stripe style="width: 100%">
      <el-table-column prop="customer_id" label="客户ID" width="90" />
      <el-table-column label="姓名" width="120">
        <template #default="{ row }">
          {{ row.name || '——' }}
        </template>
      </el-table-column>
      <el-table-column prop="phone" label="电话" width="130" />
      <el-table-column prop="membership_level" label="会员等级" width="120">
        <template #default="{ row }">
          <el-tag :type="getMemberLevelType(row.membership_level)" size="small">
            {{ row.membership_level || '普通会员' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="折扣率" width="90">
        <template #default="{ row }">
          {{ ((row.discount_rate || 1) * 100).toFixed(0) }}%
        </template>
      </el-table-column>
      <el-table-column prop="points" label="积分" width="100" />
      <el-table-column prop="register_time" label="注册时间" width="120" />
      <el-table-column label="累计消费" width="120">
        <template #default="{ row }">
          ¥{{ getCustomerTotalSpent(row.customer_id).toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="openDetailDialog(row)">
            详情
          </el-button>
          <el-button type="warning" link size="small" @click="openUpgradeDialog(row)">
            会员升级
          </el-button>
          <el-button type="info" link size="small" @click="openHistoryDialog(row)">
            购买历史
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
        :total="filteredCustomers.length"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
    
    <!-- 添加/编辑客户弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑客户' : '添加客户'"
      width="450px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="80px"
      >
        <el-form-item label="姓名">
          <el-input v-model="form.name" placeholder="姓名（非必填）" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入联系电话（必填）" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" placeholder="请输入地址" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="会员等级">
          <el-select v-model="form.membership_level" placeholder="请选择会员等级" style="width: 100%">
            <el-option label="普通会员" value="普通会员" />
            <el-option label="白银会员" value="白银会员" />
            <el-option label="黄金会员" value="黄金会员" />
          </el-select>
        </el-form-item>
        <el-form-item label="初始积分">
          <el-input-number v-model="form.points" :min="0" :max="999999" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 客户详情弹窗 -->
    <el-dialog v-model="detailVisible" title="客户详情" width="900px">
      <div v-if="selectedCustomer" class="customer-detail">
        <el-descriptions :column="2" border style="margin-bottom: 20px">
          <el-descriptions-item label="客户姓名">{{ selectedCustomer.name || '——' }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ selectedCustomer.phone }}</el-descriptions-item>
          <el-descriptions-item label="会员等级">
            <el-tag :type="getMemberLevelType(selectedCustomer.membership_level)">
              {{ selectedCustomer.membership_level || '普通会员' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="折扣率">
            {{ ((selectedCustomer.discount_rate || 1) * 100).toFixed(0) }}%
          </el-descriptions-item>
          <el-descriptions-item label="当前积分">{{ selectedCustomer.points || 0 }}</el-descriptions-item>
          <el-descriptions-item label="积分到期日">{{ selectedCustomer.points_expiry_date || '——' }}</el-descriptions-item>
          <el-descriptions-item label="注册时间">{{ selectedCustomer.register_time }}</el-descriptions-item>
          <el-descriptions-item label="收货地址" :span="2">{{ selectedCustomer.address || '——' }}</el-descriptions-item>
        </el-descriptions>
        
        <!-- 购买偏好分析 -->
        <el-divider content-position="left">
          <span>购买偏好分析</span>
        </el-divider>
        
        <div v-if="customerPreference">
          <el-row :gutter="20" style="margin-bottom: 20px">
            <el-col :span="6">
              <el-statistic title="累计订单" :value="customerPreference.totalOrders" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="累计消费" :value="customerPreference.totalAmount" prefix="¥" :precision="2" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="偏好类别数" :value="customerPreference.categoryPreferences.length" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="偏好品牌数" :value="customerPreference.brandPreferences.length" />
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card shadow="hover">
                <template #header>
                  <div class="card-header">
                    <span>品类偏好排行榜</span>
                  </div>
                </template>
                <div v-if="customerPreference.categoryPreferences.length > 0">
                  <div v-for="(cat, index) in customerPreference.categoryPreferences" :key="cat.category" class="preference-item">
                    <div class="preference-rank">{{ index + 1 }}</div>
                    <div class="preference-info">
                      <div class="preference-name">{{ cat.category }}</div>
                      <div class="preference-stats">
                        购买 {{ cat.count }} 次 | 金额 ¥{{ cat.amount.toFixed(2) }}
                      </div>
                    </div>
                    <div class="preference-bar">
                      <el-progress :percentage="parseFloat(cat.percentage)" :color="getCategoryColor(index)" />
                    </div>
                  </div>
                </div>
                <el-empty v-else description="暂无购买记录" />
              </el-card>
            </el-col>
            
            <el-col :span="12">
              <el-card shadow="hover">
                <template #header>
                  <div class="card-header">
                    <span>品牌偏好排行榜</span>
                  </div>
                </template>
                <div v-if="customerPreference.brandPreferences.length > 0">
                  <div v-for="(brand, index) in customerPreference.brandPreferences" :key="brand.brand" class="preference-item">
                    <div class="preference-rank">{{ index + 1 }}</div>
                    <div class="preference-info">
                      <div class="preference-name">{{ brand.brand }}</div>
                      <div class="preference-stats">
                        购买 {{ brand.count }} 次 | 金额 ¥{{ brand.amount.toFixed(2) }}
                      </div>
                    </div>
                    <div class="preference-bar">
                      <el-progress :percentage="parseFloat(brand.percentage)" :color="getBrandColor(index)" />
                    </div>
                  </div>
                </div>
                <el-empty v-else description="暂无购买记录" />
              </el-card>
            </el-col>
          </el-row>
          
          <el-card shadow="hover" style="margin-top: 20px">
            <template #header>
              <div class="card-header">
                <span>常购产品 TOP 10</span>
              </div>
            </template>
            <el-table :data="customerPreference.recentProducts" border>
              <el-table-column type="index" label="排名" width="60" />
              <el-table-column prop="product_name" label="产品名称" />
              <el-table-column prop="brand" label="品牌" width="120" />
              <el-table-column prop="category" label="类别" width="100" />
              <el-table-column prop="quantity" label="累计购买数量" width="130" />
              <el-table-column label="累计消费金额" width="130">
                <template #default="{ row }">
                  ¥{{ row.amount.toFixed(2) }}
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
        <el-skeleton v-else loading animated />
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="warning" @click="openUpgradeFromDetail">
          会员升级
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 会员升级弹窗 -->
    <el-dialog v-model="upgradeVisible" title="会员升级" width="500px">
      <div v-if="upgradeCustomer">
        <el-descriptions :column="1" border style="margin-bottom: 20px">
          <el-descriptions-item label="客户姓名">{{ upgradeCustomer.name || '——' }}</el-descriptions-item>
          <el-descriptions-item label="当前等级">
            <el-tag :type="getMemberLevelType(upgradeCustomer.membership_level)">
              {{ upgradeCustomer.membership_level || '普通会员' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="累计消费">
            ¥{{ getCustomerTotalSpent(upgradeCustomer.customer_id).toFixed(2) }}
          </el-descriptions-item>
        </el-descriptions>
        
        <el-form label-width="100px">
          <el-form-item label="新会员等级" required>
            <el-select v-model="newMembershipLevel" placeholder="请选择新会员等级" style="width: 100%">
              <el-option label="普通会员（100%）" value="普通会员" />
              <el-option label="白银会员（95折）" value="白银会员" />
              <el-option label="黄金会员（90折）" value="黄金会员" />
            </el-select>
          </el-form-item>
          <el-form-item label="升级原因">
            <el-input v-model="upgradeReason" type="textarea" :rows="3" placeholder="请输入升级原因（可选）" />
          </el-form-item>
        </el-form>
        
        <el-alert
          v-if="getUpgradeSuggestion"
          :title="getUpgradeSuggestion"
          type="info"
          :closable="false"
          style="margin-top: 10px"
        />
      </div>
      <template #footer>
        <el-button @click="upgradeVisible = false">取消</el-button>
        <el-button type="primary" :loading="upgradeLoading" @click="handleUpgrade">
          确认升级
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 积分管理弹窗 -->
    <el-dialog v-model="pointsVisible" title="积分管理" width="450px">
      <div v-if="pointsCustomer">
        <el-descriptions :column="1" border style="margin-bottom: 20px">
          <el-descriptions-item label="客户姓名">{{ pointsCustomer.name || '——' }}</el-descriptions-item>
          <el-descriptions-item label="当前积分">{{ pointsCustomer.points || 0 }}</el-descriptions-item>
          <el-descriptions-item label="积分到期日">{{ pointsCustomer.points_expiry_date || '——' }}</el-descriptions-item>
        </el-descriptions>
        
        <el-form label-width="100px">
          <el-form-item label="积分操作" required>
            <el-radio-group v-model="pointsOperation">
              <el-radio label="add">增加积分</el-radio>
              <el-radio label="reduce">减少积分</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="积分数量" required>
            <el-input-number v-model="pointsAmount" :min="0" :max="999999" style="width: 100%" />
          </el-form-item>
          <el-form-item label="操作原因">
            <el-input v-model="pointsReason" type="textarea" :rows="3" placeholder="请输入操作原因（可选）" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="pointsVisible = false">取消</el-button>
        <el-button type="primary" :loading="pointsLoading" @click="handlePointsChange">
          确认操作
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 购买历史弹窗 -->
    <el-dialog
      v-model="historyVisible"
      :title="`${selectedCustomer?.name || '客户'} - 购买历史`"
      width="800px"
    >
      <el-table
        v-if="customerOrders.length > 0"
        :data="customerOrders"
        border
        style="width: 100%"
      >
        <el-table-column prop="order_id" label="订单号" width="180" />
        <el-table-column prop="order_time" label="订单时间" width="170" />
        <el-table-column label="总金额" width="120">
          <template #default="{ row }">
            ¥{{ row.total_amount.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" />
        <el-table-column label="支付状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.payment_status)" size="small">
              {{ getStatusText(row.payment_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewOrderDetail(row)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="暂无购买记录" />
      <div v-if="customerOrders.length > 0" class="history-summary">
        <span>累计消费：</span>
        <span class="total-spent">¥{{ totalSpent.toFixed(2) }}</span>
      </div>
    </el-dialog>
    
    <!-- 订单详情弹窗 -->
    <el-dialog v-model="orderDetailVisible" title="订单详情" width="600px">
      <div v-if="orderDetail" class="order-detail">
        <el-descriptions :column="2" border style="margin-bottom: 20px">
          <el-descriptions-item label="订单号">{{ orderDetail.order_id }}</el-descriptions-item>
          <el-descriptions-item label="订单时间">{{ orderDetail.order_time }}</el-descriptions-item>
          <el-descriptions-item label="支付方式">{{ orderDetail.payment_method }}</el-descriptions-item>
          <el-descriptions-item label="支付状态">
            <el-tag :type="getStatusType(orderDetail.payment_status)">
              {{ getStatusText(orderDetail.payment_status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="收货地址" :span="2">{{ orderDetail.shipping_address }}</el-descriptions-item>
        </el-descriptions>
        
        <el-table :data="orderDetail.items" border>
          <el-table-column prop="product_name" label="产品名称" />
          <el-table-column prop="quantity" label="数量" width="80" />
          <el-table-column label="单价" width="100">
            <template #default="{ row }">¥{{ row.unit_price.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="小计" width="100">
            <template #default="{ row }">¥{{ (row.quantity * row.unit_price).toFixed(2) }}</template>
          </el-table-column>
        </el-table>
        
        <div class="detail-total">
          订单总金额：<span>¥{{ orderDetail.total_amount.toFixed(2) }}</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="orderDetailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  getCustomers,
  addCustomer,
  updateCustomer,
  deleteCustomer,
  getOrderHistory,
  getOrderDetail as getOrderDetailApi,
  getCustomerPurchasePreference
} from '../api/realApi';

const customers = ref([]);
const orders = ref([]);
const searchKeyword = ref('');
const levelFilter = ref('');
const currentPage = ref(1);
const pageSize = ref(10);
const dialogVisible = ref(false);
const historyVisible = ref(false);
const detailVisible = ref(false);
const orderDetailVisible = ref(false);
const upgradeVisible = ref(false);
const pointsVisible = ref(false);
const isEdit = ref(false);
const submitLoading = ref(false);
const formRef = ref(null);
const editingId = ref(null);
const selectedCustomer = ref(null);
const customerOrders = ref([]);
const orderDetail = ref(null);
const customerPreference = ref(null);
const upgradeCustomer = ref(null);
const newMembershipLevel = ref('');
const upgradeReason = ref('');
const upgradeLoading = ref(false);
const pointsCustomer = ref(null);
const pointsOperation = ref('add');
const pointsAmount = ref(0);
const pointsReason = ref('');
const pointsLoading = ref(false);

const form = reactive({
  name: '',
  phone: '',
  email: '',
  address: '',
  membership_level: '普通会员',
  points: 0
});

const formRules = {
  phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的11位手机号码', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
};

const filteredCustomers = computed(() => {
  let result = customers.value;
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase();
    result = result.filter(c =>
      (c.name && c.name.toLowerCase().includes(keyword)) ||
      (c.phone && c.phone.includes(keyword))
    );
  }
  
  if (levelFilter.value) {
    result = result.filter(c => c.membership_level === levelFilter.value);
  }
  
  return result;
});

const displayCustomers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredCustomers.value.slice(start, end);
});

const totalSpent = computed(() => {
  return customerOrders.value.reduce((sum, o) => sum + o.total_amount, 0);
});

const getUpgradeSuggestion = computed(() => {
  if (!upgradeCustomer.value || !newMembershipLevel.value) return '';
  
  const total = getCustomerTotalSpent(upgradeCustomer.value.customer_id);
  const currentLevel = upgradeCustomer.value.membership_level || '普通会员';
  const newLevel = newMembershipLevel.value;
  
  if (currentLevel === newLevel) {
    return '提示：会员等级未发生变化';
  }
  
  if (newLevel === '白银会员' && total >= 1000) {
    return '提示：客户累计消费已满1000元，符合白银会员标准';
  } else if (newLevel === '黄金会员' && total >= 5000) {
    return '提示：客户累计消费已满5000元，符合黄金会员标准';
  } else if (newLevel === '白银会员') {
    return `提示：客户累计消费${total.toFixed(2)}元，还差${(1000 - total).toFixed(2)}元可升级为白银会员`;
  } else if (newLevel === '黄金会员') {
    return `提示：客户累计消费${total.toFixed(2)}元，还差${(5000 - total).toFixed(2)}元可升级为黄金会员`;
  }
  
  return '';
});

function getCustomerTotalSpent(customerId) {
  return orders.value
    .filter(o => o.customer_id === customerId && o.payment_status === 1)
    .reduce((sum, o) => sum + o.total_amount, 0);
}

function getMemberLevelType(level) {
  const map = {
    '普通会员': 'info',
    '白银会员': 'warning',
    '黄金会员': 'success'
  };
  return map[level] || 'info';
}

function getStatusType(status) {
  const map = { 0: 'warning', 1: 'success', 2: 'danger' };
  return map[status] || 'info';
}

function getStatusText(status) {
  const map = { 0: '待支付', 1: '已支付', 2: '已取消' };
  return map[status] || '未知';
  return map[status] || '未知';
}

async function loadCustomers() {
  try {
    customers.value = await getCustomers();
  } catch (error) {
    ElMessage.error('加载客户列表失败');
  }
}

async function loadOrders() {
  try {
    orders.value = await getOrderHistory();
  } catch (error) {
    console.error('加载订单失败', error);
  }
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
  editingId.value = row.customer_id;
  Object.assign(form, {
    name: row.name || '',
    phone: row.phone || '',
    email: row.email || '',
    address: row.address || ''
  });
  dialogVisible.value = true;
}

function resetForm() {
  Object.assign(form, {
    name: '',
    phone: '',
    email: '',
    address: ''
  });
  formRef.value?.clearValidate();
}

async function handleSubmit() {
  if (!formRef.value) return;
  
  try {
    await formRef.value.validate();
  } catch {
    return;
  }
  
  submitLoading.value = true;
  
  try {
    const submitData = { ...form };
    
    // 设置折扣率
    if (submitData.membership_level === '白银会员') {
      submitData.discount_rate = 0.95;
    } else if (submitData.membership_level === '黄金会员') {
      submitData.discount_rate = 0.9;
    } else {
      submitData.discount_rate = 1.0;
    }
    
    // 设置积分过期日（默认1年后）
    if (!submitData.points_expiry_date) {
      const expiryDate = new Date();
      expiryDate.setFullYear(expiryDate.getFullYear() + 1);
      submitData.points_expiry_date = expiryDate.toISOString().slice(0, 10);
    }
    
    if (isEdit.value) {
      await updateCustomer(editingId.value, submitData);
      ElMessage.success('更新成功');
    } else {
      submitData.register_time = new Date().toISOString().slice(0, 10);
      await addCustomer(submitData);
      ElMessage.success('添加成功');
    }
    dialogVisible.value = false;
    await loadCustomers();
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '添加失败');
  } finally {
    submitLoading.value = false;
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除客户吗？`,
      '确认删除',
      { type: 'warning' }
    );
    
    const result = await deleteCustomer(row.customer_id);
    
    if (!result.canDelete) {
      ElMessage.warning(result.message);
      return;
    }
    
    ElMessage.success('删除成功');
    await loadCustomers();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败');
    }
  }
}

async function openHistoryDialog(row) {
  selectedCustomer.value = row;
  customerOrders.value = orders.value.filter(o => o.customer_id === row.customer_id);
  historyVisible.value = true;
}

async function viewOrderDetail(row) {
  try {
    orderDetail.value = await getOrderDetailApi(row.order_id);
    orderDetailVisible.value = true;
  } catch (error) {
    ElMessage.error('加载订单详情失败');
  }
}

async function openDetailDialog(row) {
  selectedCustomer.value = row;
  customerPreference.value = null;
  detailVisible.value = true;
  
  try {
    customerPreference.value = await getCustomerPurchasePreference(row.customer_id);
  } catch (error) {
    ElMessage.error('加载购买偏好数据失败');
  }
}

function openUpgradeDialog(row) {
  upgradeCustomer.value = row;
  newMembershipLevel.value = row.membership_level || '普通会员';
  upgradeReason.value = '';
  upgradeVisible.value = true;
}

function openUpgradeFromDetail() {
  detailVisible.value = false;
  upgradeCustomer.value = selectedCustomer.value;
  newMembershipLevel.value = upgradeCustomer.value?.membership_level || '普通会员';
  upgradeReason.value = '';
  upgradeVisible.value = true;
}

async function handleUpgrade() {
  if (!newMembershipLevel.value) {
    ElMessage.warning('请选择新会员等级');
    return;
  }
  
  upgradeLoading.value = true;
  
  try {
    const newLevel = newMembershipLevel.value;
    const discountRate = newLevel === '白银会员' ? 0.95 : newLevel === '黄金会员' ? 0.9 : 1.0;
    
    await updateCustomer(upgradeCustomer.value.customer_id, {
      membership_level: newLevel,
      discount_rate: discountRate
    });
    
    ElMessage.success(`会员已升级为${newLevel}`);
    upgradeVisible.value = false;
    await loadCustomers();
    
    // 更新详情弹窗中的数据
    if (detailVisible.value) {
      selectedCustomer.value = customers.value.find(c => c.customer_id === upgradeCustomer.value.customer_id);
    }
  } catch (error) {
    ElMessage.error('会员升级失败');
  } finally {
    upgradeLoading.value = false;
  }
}

function openPointsDialog(row) {
  pointsCustomer.value = row;
  pointsOperation.value = 'add';
  pointsAmount.value = 0;
  pointsReason.value = '';
  pointsVisible.value = true;
}

async function handlePointsChange() {
  if (pointsAmount.value <= 0) {
    ElMessage.warning('请输入有效的积分数量');
    return;
  }
  
  pointsLoading.value = true;
  
  try {
    const currentPoints = pointsCustomer.value.points || 0;
    let newPoints;
    
    if (pointsOperation.value === 'add') {
      newPoints = currentPoints + pointsAmount.value;
    } else {
      newPoints = Math.max(0, currentPoints - pointsAmount.value);
    }
    
    await updateCustomer(pointsCustomer.value.customer_id, {
      points: newPoints
    });
    
    ElMessage.success(`积分${pointsOperation.value === 'add' ? '增加' : '减少'}成功`);
    pointsVisible.value = false;
    await loadCustomers();
    
    // 更新详情弹窗中的数据
    if (detailVisible.value && selectedCustomer.value?.customer_id === pointsCustomer.value.customer_id) {
      selectedCustomer.value = customers.value.find(c => c.customer_id === pointsCustomer.value.customer_id);
    }
  } catch (error) {
    ElMessage.error('积分操作失败');
  } finally {
    pointsLoading.value = false;
  }
}

function getCategoryColor(index) {
  const colors = ['#67c23a', '#409eff', '#e6a23c', '#909399', '#f56c6c'];
  return colors[index % colors.length];
}

function getBrandColor(index) {
  const colors = ['#f56c6c', '#67c23a', '#409eff', '#e6a23c', '#909399'];
  return colors[index % colors.length];
}

onMounted(() => {
  loadCustomers();
  loadOrders();
});
</script>

<style scoped>
.users-container {
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

.history-summary {
  margin-top: 20px;
  text-align: right;
  font-size: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.total-spent {
  font-size: 20px;
  font-weight: 700;
  color: #f56c6c;
  margin-left: 8px;
}

.order-detail {
  padding: 10px 0;
}

.detail-total {
  text-align: right;
  font-size: 18px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.detail-total span {
  font-size: 24px;
  font-weight: 700;
  color: #f56c6c;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.customer-detail {
  padding: 10px 0;
}

.preference-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.preference-item:last-child {
  border-bottom: none;
}

.preference-rank {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  margin-right: 12px;
  flex-shrink: 0;
}

.preference-item:nth-child(2) .preference-rank {
  background: #67c23a;
}

.preference-item:nth-child(3) .preference-rank {
  background: #e6a23c;
}

.preference-info {
  flex: 1;
  margin-right: 12px;
}

.preference-name {
  font-weight: 600;
  font-size: 15px;
  color: #303133;
  margin-bottom: 4px;
}

.preference-stats {
  font-size: 12px;
  color: #909399;
}

.preference-bar {
  width: 150px;
  flex-shrink: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>