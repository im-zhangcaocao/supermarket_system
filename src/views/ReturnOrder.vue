<template>
  <div class="return-container">
    <div class="return-header">
      <el-button type="primary" @click="goBack">
        <span>返回订单列表</span>
      </el-button>
      <h2 class="page-title">退货申请</h2>
    </div>
    
    <div v-if="orderDetail" class="return-content">
      <el-card class="order-info-card" shadow="never">
        <template #header>
          <span>订单基本信息</span>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单号">{{ orderDetail.order_id }}</el-descriptions-item>
          <el-descriptions-item label="订单时间">{{ orderDetail.order_time }}</el-descriptions-item>
          <el-descriptions-item label="客户名称">{{ customerName }}</el-descriptions-item>
          <el-descriptions-item label="支付方式">{{ orderDetail.payment_method }}</el-descriptions-item>
          <el-descriptions-item label="订单金额" :span="2">¥{{ orderDetail.total_amount.toFixed(2) }}</el-descriptions-item>
        </el-descriptions>
        
        <h4 style="margin: 20px 0 10px">商品明细</h4>
        <el-table :data="orderDetail.items" border style="width: 100%">
          <el-table-column prop="product_name" label="产品名称" />
          <el-table-column prop="quantity" label="购买数量" width="100" />
          <el-table-column label="单价" width="100">
            <template #default="{ row }">¥{{ row.unit_price.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="退货数量" width="150">
            <template #default="{ row }">
              <el-input-number
                v-model="row.return_qty"
                :min="0"
                :max="row.quantity"
                size="small"
                @change="validateForm"
              />
            </template>
          </el-table-column>
        </el-table>
      </el-card>
      
      <el-card class="return-form-card" shadow="never">
        <template #header>
          <span>退货信息</span>
        </template>
        <el-form ref="returnFormRef" :model="returnForm" :rules="returnRules" label-width="120px">
          <el-form-item label="退货原因" prop="reason_type">
            <el-select
              v-model="returnForm.reason_type"
              placeholder="请选择退货原因"
              style="width: 300px"
              @change="handleReasonChange"
            >
              <el-option label="商品质量问题" value="quality" />
              <el-option label="商品与描述不符" value="description" />
              <el-option label="尺寸/型号错误" value="size" />
              <el-option label="重复下单" value="duplicate" />
              <el-option label="买家后悔/不想要了" value="regret" />
              <el-option label="其他原因" value="other" />
            </el-select>
          </el-form-item>
          
          <el-form-item v-if="returnForm.reason_type === 'other'" label="具体原因" prop="custom_reason">
            <el-input
              v-model="returnForm.custom_reason"
              type="textarea"
              :rows="3"
              placeholder="请详细描述退货原因"
              style="width: 400px"
              @blur="validateForm"
            />
          </el-form-item>
          
          <el-form-item label="退货说明" prop="remark">
            <el-input
              v-model="returnForm.remark"
              type="textarea"
              :rows="3"
              placeholder="请输入其他需要说明的信息（选填）"
              style="width: 400px"
            />
          </el-form-item>
        </el-form>
      </el-card>
      
      <div class="form-actions">
        <el-button @click="goBack">取消</el-button>
        <el-button
          type="primary"
          :loading="submitting"
          :disabled="!canSubmit"
          @click="submitReturn"
        >
          提交退货申请
        </el-button>
      </div>
    </div>
    
    <div v-else class="loading-state">
      <el-loading text="加载订单信息中..." />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { getOrderDetail, returnOrder, getCustomers } from '../api/realApi';

const route = useRoute();
const router = useRouter();

const orderDetail = ref(null);
const customers = ref([]);
const submitting = ref(false);
const returnFormRef = ref(null);

const returnForm = reactive({
  reason_type: '',
  custom_reason: '',
  remark: ''
});

const returnRules = {
  reason_type: [{ required: true, message: '请选择退货原因', trigger: 'change' }],
  custom_reason: [{ required: true, message: '请输入具体原因', trigger: 'blur' }]
};

const customerName = computed(() => {
  if (!orderDetail.value) return '';
  const customer = customers.value.find(c => c.customer_id === orderDetail.value.customer_id);
  return customer ? customer.name : `客户${orderDetail.value.customer_id}`;
});

const hasReturnQty = computed(() => {
  if (!orderDetail.value || !orderDetail.value.items) return false;
  return orderDetail.value.items.some(item => (item.return_qty || 0) > 0);
});

const canSubmit = computed(() => {
  if (!returnForm.reason_type || !hasReturnQty.value) return false;
  if (returnForm.reason_type === 'other' && !returnForm.custom_reason.trim()) return false;
  return true;
});

function handleReasonChange() {
  if (returnForm.reason_type !== 'other') {
    returnForm.custom_reason = '';
  }
}

function validateForm() {
}

async function loadOrderDetail() {
  const orderId = route.params.orderId;
  if (!orderId) {
    ElMessage.error('订单ID不能为空');
    router.push('/dashboard/sales');
    return;
  }
  
  try {
    orderDetail.value = await getOrderDetail(orderId);
    if (!orderDetail.value) {
      ElMessage.error('订单不存在');
      router.push('/dashboard/sales');
      return;
    }
    
    orderDetail.value.items.forEach(item => {
      item.return_qty = item.quantity;
    });
    
    await loadCustomers();
  } catch (error) {
    ElMessage.error(error.message || '加载订单失败');
    router.push('/dashboard/sales');
  }
}

async function loadCustomers() {
  try {
    customers.value = await getCustomers();
  } catch (error) {
    ElMessage.error('加载客户列表失败');
  }
}

function goBack() {
  router.push('/dashboard/sales');
}

async function submitReturn() {
  if (!canSubmit.value) return;
  
  try {
    await ElMessageBox.confirm(
      '确定要提交退货申请吗？退货后库存将恢复，收入将扣除。',
      '确认退货',
      { type: 'warning' }
    );
    
    submitting.value = true;
    
    const returnItems = orderDetail.value.items
      .filter(item => item.return_qty > 0)
      .map(item => ({
        productId: item.product_id,
        quantity: item.return_qty
      }));
    
    const reasonText = returnForm.reason_type === 'other' 
      ? returnForm.custom_reason 
      : getReasonText(returnForm.reason_type);
    
    await returnOrder(orderDetail.value.order_id, returnItems, reasonText, returnForm.remark);
    
    ElMessage.success('退货申请提交成功');
    router.push('/dashboard/sales');
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '提交退货申请失败');
    }
  } finally {
    submitting.value = false;
  }
}

function getReasonText(reasonType) {
  const map = {
    quality: '商品质量问题',
    description: '商品与描述不符',
    size: '尺寸/型号错误',
    duplicate: '重复下单',
    regret: '买家后悔/不想要了',
    other: '其他原因'
  };
  return map[reasonType] || '其他原因';
}

onMounted(() => {
  loadOrderDetail();
});
</script>

<style scoped>
.return-container {
  padding: 20px;
}

.return-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.return-content {
  max-width: 800px;
}

.order-info-card,
.return-form-card {
  margin-bottom: 20px;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 20px 0;
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}
</style>