<template>
  <div class="finance-container">
    <h2 class="page-title">财务管理</h2>
    
    <!-- 财务汇总卡片 -->
    <el-row :gutter="20" class="summary-cards">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="summary-card">
            <div class="summary-label">总收入</div>
            <div class="summary-value income">¥{{ summary.totalIncome.toFixed(2) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="summary-card">
            <div class="summary-label">总支出</div>
            <div class="summary-value expense">¥{{ summary.totalExpense.toFixed(2) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="summary-card">
            <div class="summary-label">净利润</div>
            <div class="summary-value" :class="summary.profit >= 0 ? 'income' : 'expense'">
              ¥{{ summary.profit.toFixed(2) }}
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="summary-card">
            <div class="summary-label">毛利率</div>
            <div class="summary-value margin">
              {{ summary.totalIncome > 0 ? ((summary.grossProfit / summary.totalIncome) * 100).toFixed(2) : 0 }}%
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 标签页 -->
    <el-tabs v-model="activeTab" class="finance-tabs">
      <!-- 资金流水 -->
      <el-tab-pane label="资金流水" name="flow">
        <div class="toolbar">
          <div class="filter-group">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              @change="loadData"
            />
            <el-select
              v-model="filterType"
              placeholder="类型筛选"
              clearable
              style="width: 120px; margin-left: 10px"
              @change="loadData"
            >
              <el-option label="全部" :value="null" />
              <el-option label="收入" :value="1" />
              <el-option label="支出" :value="2" />
            </el-select>
          </div>
          <div class="action-group">
            <el-button type="primary" @click="showAddDialog = true">
              录入其他支出
            </el-button>
            <el-button type="success" @click="handleExport">
              导出Excel
            </el-button>
          </div>
        </div>
        
        <el-table :data="displayRecords" border stripe style="width: 100%">
          <el-table-column prop="record_id" label="记录ID" width="80" />
          <el-table-column label="类型" width="80">
            <template #default="{ row }">
              <el-tag :type="row.type === 1 ? 'success' : 'danger'" size="small">
                {{ row.type === 1 ? '收入' : '支出' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="金额" width="120">
            <template #default="{ row }">
              <span :class="row.type === 1 ? 'income-text' : 'expense-text'">
                {{ row.type === 1 ? '+' : '-' }}¥{{ row.amount.toFixed(2) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="relate_order_id" label="关联订单" width="180" />
          <el-table-column prop="occur_time" label="发生时间" width="170" />
          <el-table-column prop="remark" label="备注" min-width="150" />
        </el-table>
        
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredRecords.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </el-tab-pane>

      <!-- 收入分析 -->
      <el-tab-pane label="收入分析" name="income">
        <el-card shadow="hover">
          <template #header>
            <span>销售订单详情</span>
          </template>
          <el-table :data="incomeOrders" border stripe style="width: 100%">
            <el-table-column prop="order_id" label="订单号" width="160" />
            <el-table-column prop="customer_name" label="客户" width="120" />
            <el-table-column label="订单金额" width="120">
              <template #default="{ row }">
                ¥{{ row.total_amount?.toFixed(2) || '0.00' }}
              </template>
            </el-table-column>
            <el-table-column label="折扣金额" width="100">
              <template #default="{ row }">
                ¥{{ row.discount_amount?.toFixed(2) || '0.00' }}
              </template>
            </el-table-column>
            <el-table-column label="实收金额" width="120">
              <template #default="{ row }">
                ¥{{ row.final_amount?.toFixed(2) || '0.00' }}
              </template>
            </el-table-column>
            <el-table-column prop="order_time" label="订单时间" width="170" />
            <el-table-column prop="payment_method" label="支付方式" width="100" />
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 支出分析 -->
      <el-tab-pane label="支出分析" name="expense">
        <el-card shadow="hover">
          <template #header>
            <span>采购订单详情</span>
          </template>
          <el-table :data="expenseOrders" border stripe style="width: 100%">
            <el-table-column prop="purchase_order_id" label="采购单号" width="180" />
            <el-table-column prop="supplier_name" label="供应商" width="200" />
            <el-table-column label="采购金额" width="120">
              <template #default="{ row }">
                ¥{{ row.total_amount?.toFixed(2) || '0.00' }}
              </template>
            </el-table-column>
            <el-table-column prop="order_time" label="订单时间" width="170" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="remark" label="备注" min-width="150" />
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 利润分析 -->
      <el-tab-pane label="利润分析" name="profit">
        <el-row :gutter="20" style="margin-top: 20px">
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <span>利润构成</span>
              </template>
              <el-descriptions :column="1" border>
                <el-descriptions-item label="商品销售利润">
                  <span class="income-text">¥{{ productProfit.toFixed(2) }}</span>
                </el-descriptions-item>
                <el-descriptions-item label="采购总成本">
                  <span class="expense-text">¥{{ totalPurchaseCost.toFixed(2) }}</span>
                </el-descriptions-item>
                <el-descriptions-item label="运营成本">
                  <span class="expense-text">¥{{ operatingCost.toFixed(2) }}</span>
                </el-descriptions-item>
                <el-descriptions-item label="净利润率">
                  <el-tag type="success" v-if="summary.totalIncome > 0">
                    {{ ((summary.profit / summary.totalIncome) * 100).toFixed(2) }}%
                  </el-tag>
                  <el-tag type="info" v-else>0.00%</el-tag>
                </el-descriptions-item>
              </el-descriptions>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- 成本核算 -->
      <el-tab-pane label="成本核算" name="cost">
        <el-card shadow="hover">
          <template #header>
            <span>商品成本分析</span>
          </template>
          <el-table :data="productCosts" border stripe style="width: 100%">
            <el-table-column prop="product_name" label="商品名称" width="180" />
            <el-table-column prop="category" label="类别" width="100" />
            <el-table-column label="采购价" width="100">
              <template #default="{ row }">
                ¥{{ row.purchase_price?.toFixed(2) || '0.00' }}
              </template>
            </el-table-column>
            <el-table-column label="零售价" width="100">
              <template #default="{ row }">
                ¥{{ row.retail_price?.toFixed(2) || '0.00' }}
              </template>
            </el-table-column>
            <el-table-column label="毛利" width="100">
              <template #default="{ row }">
                ¥{{ (row.retail_price - row.purchase_price).toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="毛利率" width="100">
              <template #default="{ row }">
                <el-tag :type="getMarginType(row.gross_margin)" size="small">
                  {{ row.gross_margin.toFixed(2) }}%
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="sales_quantity" label="销售数量" width="100" />
            <el-table-column label="总利润" width="120">
              <template #default="{ row }">
                <span class="income-text">¥{{ row.total_profit.toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="current_stock" label="当前库存" width="100" />
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 录入其他支出弹窗 -->
    <el-dialog v-model="showAddDialog" title="录入其他支出" width="400px">
      <el-form ref="expenseFormRef" :model="expenseForm" :rules="expenseRules" label-width="100px">
        <el-form-item label="支出类型" prop="category">
          <el-select v-model="expenseForm.category" placeholder="请选择类型" style="width: 100%">
            <el-option label="房租" value="房租" />
            <el-option label="水电费" value="水电费" />
            <el-option label="工资" value="工资" />
            <el-option label="运输费" value="运输费" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="金额" prop="amount">
          <el-input-number
            v-model="expenseForm.amount"
            :min="0"
            :precision="2"
            :controls="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="日期" prop="date">
          <el-date-picker
            v-model="expenseForm.date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="选择日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="expenseForm.note"
            type="textarea"
            :rows="2"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddExpense">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import {
  getFinancialFlow,
  getFinancialSummary,
  recordOtherExpense,
  getSalesOrders,
  getPurchaseOrders,
  getProducts
} from '../api/mockApi';
import { exportFinancialRecords } from '../utils/export';

const activeTab = ref('flow');
const records = ref([]);
const salesOrders = ref([]);
const purchaseOrders = ref([]);
const products = ref([]);
const summary = reactive({
  totalIncome: 0,
  totalExpense: 0,
  profit: 0,
  grossProfit: 0
});
const dateRange = ref(null);
const filterType = ref(null);
const currentPage = ref(1);
const pageSize = ref(10);
const showAddDialog = ref(false);
const expenseFormRef = ref(null);

const expenseForm = reactive({
  category: '',
  amount: 0,
  date: '',
  note: ''
});

const expenseRules = {
  category: [{ required: true, message: '请选择支出类型', trigger: 'change' }],
  amount: [{ required: true, message: '请输入金额', trigger: 'blur' }],
  date: [{ required: true, message: '请选择日期', trigger: 'change' }]
};

const filteredRecords = computed(() => {
  let result = records.value || [];
  
  if (dateRange.value && dateRange.value.length === 2) {
    const [start, end] = dateRange.value;
    result = result.filter(r => {
      if (!r.occur_time) return false;
      const occurDate = r.occur_time.slice(0, 10);
      return occurDate >= start && occurDate <= end;
    });
  }
  
  if (filterType.value !== null) {
    result = result.filter(r => r.type === filterType.value);
  }
  
  return result;
});

const displayRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredRecords.value.slice(start, end);
});

const incomeOrders = computed(() => {
  return (salesOrders.value || []).filter(o => !o.is_cancelled && o.payment_status === 1);
});

const expenseOrders = computed(() => {
  return purchaseOrders.value || [];
});

const productCosts = computed(() => {
  return (products.value || []).map(p => {
    const purchasePrice = p.purchase_ref_price || 0;
    const retailPrice = p.retail_price || 0;
    const grossMargin = retailPrice > 0 ? ((retailPrice - purchasePrice) / retailPrice) * 100 : 0;
    const totalProfit = (retailPrice - purchasePrice) * 0;

    return {
      product_name: p.product_name,
      category: p.category,
      purchase_price: purchasePrice,
      retail_price: retailPrice,
      gross_margin: grossMargin,
      sales_quantity: 0,
      total_profit: totalProfit,
      current_stock: p.current_stock
    };
  });
});

const productProfit = computed(() => {
  let totalProfit = 0;
  (salesOrders.value || []).forEach(order => {
    if (!order.is_cancelled && order.payment_status === 1) {
      totalProfit += (order.final_amount || 0) * 0.3;
    }
  });
  return totalProfit;
});

const totalPurchaseCost = computed(() => {
  let total = 0;
  (purchaseOrders.value || []).forEach(order => {
    if (order.status === 'completed') {
      total += order.total_amount || 0;
    }
  });
  return total;
});

const operatingCost = computed(() => {
  return summary.totalExpense - totalPurchaseCost.value;
});

async function loadData() {
  try {
    await Promise.all([
      loadFinancialFlow(),
      loadSalesOrders(),
      loadPurchaseOrders(),
      loadProductData()
    ]);
  } catch (error) {
    console.error('加载数据失败:', error);
    ElMessage.error('加载数据失败');
  }
}

async function loadFinancialFlow() {
  try {
    const [start, end] = dateRange.value || [null, null];
    records.value = await getFinancialFlow(start, end, filterType.value) || [];
    
    const sum = await getFinancialSummary(start, end) || {};
    summary.totalIncome = sum.totalIncome || 0;
    summary.totalExpense = sum.totalExpense || 0;
    summary.profit = sum.profit || 0;
    summary.grossProfit = sum.grossProfit || 0;
  } catch (error) {
    console.error('加载财务流水失败:', error);
    ElMessage.error('加载财务流水失败');
  }
}

async function loadSalesOrders() {
  try {
    salesOrders.value = await getSalesOrders() || [];
  } catch (error) {
    console.error('加载销售订单失败:', error);
    ElMessage.error('加载销售订单失败');
  }
}

async function loadPurchaseOrders() {
  try {
    purchaseOrders.value = await getPurchaseOrders() || [];
  } catch (error) {
    console.error('加载采购订单失败:', error);
    ElMessage.error('加载采购订单失败');
  }
}

async function loadProductData() {
  try {
    products.value = await getProducts() || [];
  } catch (error) {
    console.error('加载商品数据失败:', error);
    ElMessage.error('加载商品数据失败');
  }
}

function getMarginType(margin) {
  if (margin >= 40) return 'success';
  if (margin >= 20) return 'warning';
  return 'danger';
}

function getStatusType(status) {
  const typeMap = {
    pending: 'info',
    partial: 'warning',
    completed: 'success'
  };
  return typeMap[status] || 'info';
}

function getStatusText(status) {
  const textMap = {
    pending: '待收货',
    partial: '部分收货',
    completed: '已完成'
  };
  return textMap[status] || status;
}

async function handleAddExpense() {
  try {
    if (!expenseFormRef.value) return;
    await expenseFormRef.value.validate();
  } catch {
    return;
  }
  
  try {
    await recordOtherExpense(
      expenseForm.category,
      expenseForm.amount,
      expenseForm.date,
      expenseForm.note
    );
    ElMessage.success('支出录入成功');
    showAddDialog.value = false;
    expenseForm.category = '';
    expenseForm.amount = 0;
    expenseForm.date = '';
    expenseForm.note = '';
    await loadData();
  } catch (error) {
    console.error('支出录入失败:', error);
    ElMessage.error('支出录入失败');
  }
}

function handleExport() {
  if (filteredRecords.value.length === 0) {
    ElMessage.warning('暂无数据可导出');
    return;
  }
  
  const filename = `财务流水_${new Date().toISOString().slice(0, 10)}`;
  const success = exportFinancialRecords(filteredRecords.value, filename);
  
  if (success) {
    ElMessage.success('导出成功');
  } else {
    ElMessage.error('导出失败');
  }
}

function handleSizeChange() {
  currentPage.value = 1;
}

function handlePageChange() {
}

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.finance-container {
  padding: 20px;
}

.page-title {
  margin: 0 0 20px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.summary-cards {
  margin-bottom: 20px;
}

.summary-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
}

.summary-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 24px;
  font-weight: 700;
}

.summary-value.income {
  color: #67c23a;
}

.summary-value.expense {
  color: #f56c6c;
}

.summary-value.margin {
  color: #e6a23c;
}

.finance-tabs {
  margin-top: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.filter-group,
.action-group {
  display: flex;
  align-items: center;
}

.income-text {
  color: #67c23a;
  font-weight: 600;
}

.expense-text {
  color: #f56c6c;
  font-weight: 600;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
