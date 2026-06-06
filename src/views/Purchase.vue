<template>
  <div class="purchase-container">
    <h2 class="page-title">采购管理</h2>
    
    <el-tabs v-model="activeTab" class="purchase-tabs">
      <!-- 标签1：采购订单列表 -->
      <el-tab-pane label="采购订单列表" name="orderList">
        <!-- 超期警告条 -->
        <el-alert
          v-if="overdueCount > 0"
          :title="`当前有 ${overdueCount} 个采购订单已超过预期交付日期`"
          type="warning"
          show-icon
          :closable="false"
          class="alert-bar"
        >
          <template #default>
            <el-button type="warning" link @click="filterOverdue = !filterOverdue">
              {{ filterOverdue ? '显示全部' : '只看超期' }}
            </el-button>
          </template>
        </el-alert>
        
        <div class="toolbar">
          <div class="filter-group">
            <el-select
              v-model="filterSupplier"
              placeholder="筛选供应商"
              clearable
              style="width: 180px"
              @change="handleFilterChange"
            >
              <el-option
                v-for="s in suppliers"
                :key="s.supplier_id"
                :label="s.supplier_name"
                :value="s.supplier_id"
              />
            </el-select>
            <el-select
              v-model="filterStatus"
              placeholder="筛选状态"
              clearable
              style="width: 120px; margin-left: 10px"
              @change="handleFilterChange"
            >
              <el-option label="待交付" :value="0" />
              <el-option label="部分交付" :value="1" />
              <el-option label="已完成" :value="2" />
            </el-select>
          </div>
        </div>
        
        <el-table :data="displayOrders" border stripe style="width: 100%">
          <el-table-column prop="purchase_order_id" label="采购单号" width="180" />
          <el-table-column label="供应商" width="180">
            <template #default="{ row }">
              {{ getSupplierName(row.supplier_id) }}
            </template>
          </el-table-column>
          <el-table-column prop="create_time" label="创建时间" width="170" />
          <el-table-column prop="expected_date" label="预期交付日期" width="130" />
          <el-table-column label="实际交付日期" width="130">
            <template #default="{ row }">
              {{ row.actual_delivery_date || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="采购数量/已收" width="150">
            <template #default="{ row }">
              {{ row.total_received_qty || 0 }} / {{ row.total_expected_qty || 0 }}
            </template>
          </el-table-column>
          <el-table-column label="总金额" width="120">
            <template #default="{ row }">
              ¥{{ calculateOrderTotal(row.purchase_order_id).toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="280" fixed="right">
            <template #default="{ row }">
              <el-button
                v-if="row.status < 2"
                type="primary"
                link
                size="small"
                @click="openReceiptDialog(row)"
              >
                确认收货
              </el-button>
              <el-button
                type="info"
                link
                size="small"
                @click="viewReceiptHistory(row)"
              >
                收货记录
              </el-button>
              <el-button 
                v-if="isAdmin && row.status === 0" 
                type="danger" 
                link 
                size="small" 
                @click="handleCancelOrder(row)"
              >
                取消订单
              </el-button>
              <span v-if="row.status >= 2 && !isAdmin" style="color: #909399">-</span>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="orderPage"
            v-model:page-size="orderPageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredOrders.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </el-tab-pane>
      
      <!-- 标签2：创建采购订单 -->
      <el-tab-pane label="创建采购订单" name="createOrder">
        <div class="create-order-form">
          <!-- 供应商信息 -->
          <el-card class="form-section" shadow="never">
            <template #header>
              <span>供应商信息</span>
            </template>
            <el-form label-width="120px">
              <el-form-item label="选择供应商">
                <el-select
                  v-model="selectedSupplierId"
                  placeholder="请选择供应商"
                  filterable
                  style="width: 300px"
                >
                  <el-option
                    v-for="s in suppliers"
                    :key="s.supplier_id"
                    :label="s.supplier_name"
                    :value="s.supplier_id"
                  >
                    <div style="display: flex; justify-content: space-between; width: 100%;">
                      <span>{{ s.supplier_name }}</span>
                      <span style="color: #909399; font-size: 12px;">
                        准时率: {{ s.on_time_rate || 0 }}% | 平均交付: {{ s.average_delivery_days || 0 }}天
                      </span>
                    </div>
                  </el-option>
                </el-select>
                <el-button type="primary" link style="margin-left: 16px" @click="activeTab = 'supplierManagement'">
                  前往供应商管理
                </el-button>
              </el-form-item>
              <el-form-item label="预期交付日期">
                <el-date-picker
                  v-model="expectedDate"
                  type="date"
                  placeholder="选择日期"
                  value-format="YYYY-MM-DD"
                  style="width: 200px"
                />
              </el-form-item>
            </el-form>
          </el-card>
          
          <!-- 商品明细 -->
          <el-card class="form-section" shadow="never">
            <template #header>
              <span>商品明细</span>
            </template>
            <el-table :data="orderItems" border style="width: 100%">
              <el-table-column label="产品" width="280">
                <template #default="{ row, $index }">
                  <el-select
                    v-model="row.product_id"
                    placeholder="请选择产品"
                    filterable
                    style="width: 100%"
                    @change="(val) => handleProductSelect(val, $index)"
                  >
                    <el-option
                      v-for="p in products"
                      :key="p.product_id"
                      :label="`${p.product_name} (当前库存: ${p.current_stock})`"
                      :value="p.product_id"
                    />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column label="采购数量" width="150">
                <template #default="{ row }">
                  <el-input-number
                    v-model="row.quantity"
                    :min="1"
                    :disabled="!row.product_id"
                    @change="calcSubtotal($index)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="采购单价" width="150">
                <template #default="{ row }">
                  <el-input-number
                    v-model="row.unit_price"
                    :min="0"
                    :precision="2"
                    :controls="false"
                    :disabled="!row.product_id"
                    style="width: 100%"
                    @change="calcSubtotal($index)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="小计" width="120">
                <template #default="{ row }">
                  <span class="subtotal">¥{{ (row.subtotal || 0).toFixed(2) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80">
                <template #default="{ $index }">
                  <el-button type="danger" link @click="removeItem($index)">
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <el-button type="primary" plain style="margin-top: 16px" @click="addItem">
              + 添加商品
            </el-button>
            
            <div class="order-summary">
              <span>合计金额：</span>
              <span class="total-amount">¥{{ totalAmount.toFixed(2) }}</span>
            </div>
          </el-card>
          
          <!-- 提交按钮 -->
          <div class="form-actions">
            <el-button @click="resetForm">重置</el-button>
            <el-button type="primary" :loading="submitting" @click="submitOrder">
              创建采购订单
            </el-button>
          </div>
        </div>
      </el-tab-pane>

      <!-- 标签4：采购建议 -->
      <el-tab-pane label="采购建议" name="replenishment">
        <div class="replenishment-advice">
          <div class="toolbar">
            <el-button type="primary" @click="generateAdvice" :loading="generatingAdvice">
              生成采购建议
            </el-button>
            <el-select v-model="adviceFilter" placeholder="筛选状态" clearable style="margin-left: 10px; width: 150px;">
              <el-option label="待处理" :value="0" />
              <el-option label="已生成订单" :value="1" />
              <el-option label="已取消" :value="2" />
            </el-select>
          </div>
          
          <el-table :data="adviceList" border stripe style="width: 100%">
            <el-table-column prop="product_name" label="商品名称" />
            <el-table-column label="当前库存/安全库存" width="180">
              <template #default="{ row }">
                {{ row.current_stock }} / {{ row.threshold }}
              </template>
            </el-table-column>
            <el-table-column prop="daily_sales" label="日均销量" width="120" />
            <el-table-column prop="suggested_qty" label="建议采购量" width="120">
              <template #default="{ row }">
                <el-input-number 
                  v-if="row.status === 0" 
                  v-model="row.manual_qty" 
                  :min="0" 
                  size="small"
                  :default-value="row.suggested_qty"
                />
                <span v-else>{{ row.suggested_qty }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="reason" label="建议原因" />
            <el-table-column prop="generated_date" label="生成日期" width="120" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getAdviceStatusType(row.status)" size="small">
                  {{ getAdviceStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="250" fixed="right">
              <template #default="{ row }">
                <el-button
                  v-if="row.status === 0"
                  type="primary"
                  link
                  size="small"
                  @click="createPurchaseFromAdvice(row)"
                >
                  生成采购单
                </el-button>
                <el-button
                  v-if="row.status === 0"
                  type="danger"
                  link
                  size="small"
                  @click="cancelAdvice(row)"
                >
                  取消
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- 标签5：供应商管理 -->
      <el-tab-pane label="供应商管理" name="supplierManagement">
        <div class="supplier-management">
          <div class="toolbar">
            <div class="filter-group">
              <el-input
                v-model="supplierSearchKeyword"
                placeholder="搜索供应商名称..."
                prefix-icon="Search"
                clearable
                style="width: 250px"
                @input="handleSupplierSearch"
              />
              <el-select v-model="supplierSortBy" placeholder="排序方式" style="width: 180px; margin-left: 10px" @change="handleSupplierSort">
                <el-option label="按准时率排序" value="on_time_rate" />
                <el-option label="按交付天数排序" value="delivery_days" />
                <el-option label="按名称排序" value="name" />
              </el-select>
            </div>
            <el-button type="primary" @click="openSupplierAddDialog">
              添加供应商
            </el-button>
          </div>
          
          <el-table :data="displaySupplierList" border stripe style="width: 100%">
            <el-table-column prop="supplier_id" label="供应商ID" width="100" />
            <el-table-column prop="supplier_name" label="供应商名称" width="180" />
            <el-table-column prop="contact_person" label="联系人" width="120" />
            <el-table-column prop="contact_phone" label="联系电话" width="150" />
            <el-table-column prop="address" label="地址" min-width="150" />
            <el-table-column label="准时率" width="120">
              <template #default="{ row }">
                <el-progress :percentage="row.on_time_rate || 0" :color="getRateColor(row.on_time_rate)" />
              </template>
            </el-table-column>
            <el-table-column label="平均交付天数" width="130">
              <template #default="{ row }">
                <span :style="getDeliveryDaysStyle(row.average_delivery_days)">
                  {{ row.average_delivery_days || 0 }} 天
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="last_order_date" label="最近采购日期" width="130">
              <template #default="{ row }">
                {{ row.last_order_date || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="160" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="openSupplierEditDialog(row)">
                  编辑
                </el-button>
                <el-button type="danger" link size="small" @click="handleSupplierDelete(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="pagination-wrapper">
            <el-pagination
              v-model:current-page="supplierPage"
              v-model:page-size="supplierPageSize"
              :page-sizes="[10, 20, 50]"
              :total="filteredSupplierList.length"
              layout="total, sizes, prev, pager, next"
            />
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 确认收货弹窗 -->
    <el-dialog v-model="receiptVisible" title="确认收货" width="700px">
      <div v-if="receivingOrder">
        <el-descriptions :column="2" border style="margin-bottom: 20px">
          <el-descriptions-item label="采购单号">{{ receivingOrder.purchase_order_id }}</el-descriptions-item>
          <el-descriptions-item label="供应商">{{ getSupplierName(receivingOrder.supplier_id) }}</el-descriptions-item>
          <el-descriptions-item label="期望日期">{{ receivingOrder.expected_date }}</el-descriptions-item>
          <el-descriptions-item label="已收数量/总数量">
            {{ receivingOrder.total_received_qty || 0 }} / {{ receivingOrder.total_expected_qty || 0 }}
          </el-descriptions-item>
        </el-descriptions>
        
        <el-form label-width="80px">
          <el-form-item label="收货备注">
            <el-input v-model="receiptRemark" type="textarea" :rows="2" placeholder="请输入收货备注" />
          </el-form-item>
        </el-form>
        
        <el-table :data="receivingItems" border>
          <el-table-column prop="product_name" label="产品名称" />
          <el-table-column label="订购数量" width="100">
            <template #default="{ row }">{{ row.quantity }}</template>
          </el-table-column>
          <el-table-column label="已收数量" width="100">
            <template #default="{ row }">{{ row.already_received || 0 }}</template>
          </el-table-column>
          <el-table-column label="本次实收数量" width="180">
            <template #default="{ row }">
              <el-input-number
                v-model="row.received_qty"
                :min="0"
                :max="row.quantity - (row.already_received || 0)"
                size="small"
                style="width: 100%"
              />
            </template>
          </el-table-column>
          <el-table-column label="质检状态" width="120">
            <template #default="{ row }">
              <el-select v-model="row.quality_status" size="small" style="width: 100%">
                <el-option label="合格" value="合格" />
                <el-option label="不合格" value="不合格" />
              </el-select>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="receiptVisible = false">取消</el-button>
        <el-button type="primary" :loading="receiving" @click="handleReceipt">
          确认收货
        </el-button>
      </template>
    </el-dialog>

    <!-- 收货历史记录弹窗 -->
    <el-dialog v-model="receiptHistoryVisible" title="收货历史记录" width="800px">
      <div v-if="currentOrder">
        <el-table :data="orderReceipts" border stripe>
          <el-table-column prop="receipt_id" label="收货单号" width="150" />
          <el-table-column prop="receipt_time" label="收货时间" width="180" />
          <el-table-column prop="operator" label="操作人" width="120" />
          <el-table-column prop="total_qty" label="收货总数" width="100" />
          <el-table-column prop="remark" label="备注" />
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewReceiptDetail(row)">
                查看明细
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="receiptHistoryVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 收货明细弹窗 -->
    <el-dialog v-model="receiptDetailVisible" title="收货明细" width="700px">
      <div v-if="currentReceipt">
        <el-descriptions :column="2" border style="margin-bottom: 20px">
          <el-descriptions-item label="收货单号">{{ currentReceipt.receipt_id }}</el-descriptions-item>
          <el-descriptions-item label="收货时间">{{ currentReceipt.receipt_time }}</el-descriptions-item>
          <el-descriptions-item label="操作人">{{ currentReceipt.operator }}</el-descriptions-item>
          <el-descriptions-item label="收货总数">{{ currentReceipt.total_qty }}</el-descriptions-item>
        </el-descriptions>
        
        <el-table :data="receiptDetailItems" border>
          <el-table-column prop="product_name" label="产品名称" />
          <el-table-column prop="quantity" label="收货数量" width="120" />
          <el-table-column prop="quality_status" label="质检状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.quality_status === '合格' ? 'success' : 'danger'" size="small">
                {{ row.quality_status }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="receiptDetailVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 从建议生成采购单弹窗 -->
    <el-dialog v-model="createPurchaseFromAdviceVisible" title="生成采购订单" width="600px">
      <div v-if="currentAdvice">
        <el-descriptions :column="2" border style="margin-bottom: 20px">
          <el-descriptions-item label="商品名称">{{ currentAdvice.product_name }}</el-descriptions-item>
          <el-descriptions-item label="建议采购数量">{{ currentAdvice.manual_qty || currentAdvice.suggested_qty }}</el-descriptions-item>
        </el-descriptions>
        
        <el-form label-width="120px">
          <el-form-item label="选择供应商" required>
            <el-select v-model="adviceSupplierId" placeholder="请选择供应商" style="width: 100%">
              <el-option
                v-for="s in suppliers"
                :key="s.supplier_id"
                :label="s.supplier_name"
                :value="s.supplier_id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="预期交付日期" required>
            <el-date-picker
              v-model="adviceExpectedDate"
              type="date"
              placeholder="选择日期"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="createPurchaseFromAdviceVisible = false">取消</el-button>
        <el-button type="primary" :loading="creatingPurchase" @click="submitCreatePurchaseFromAdvice">
          生成采购订单
        </el-button>
      </template>
    </el-dialog>

    <!-- 供应商管理弹窗 -->
    <el-dialog v-model="supplierDialogVisible" :title="isSupplierEdit ? '编辑供应商' : '添加供应商'" width="450px">
      <el-form ref="supplierFormRef" :model="supplierFormData" :rules="supplierFormRules" label-width="100px">
        <el-form-item label="供应商名称" prop="supplier_name">
          <el-input v-model="supplierFormData.supplier_name" placeholder="请输入供应商名称" />
        </el-form-item>
        <el-form-item label="联系人" prop="contact_person">
          <el-input v-model="supplierFormData.contact_person" placeholder="请输入联系人" />
        </el-form-item>
        <el-form-item label="联系电话" prop="contact_phone">
          <el-input v-model="supplierFormData.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="supplierFormData.address" placeholder="请输入地址" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="supplierDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSupplierSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useUserStore } from '../stores/user';
import {
  getPurchaseOrders,
  getSuppliers,
  addSupplier,
  getProducts,
  createPurchaseOrder,
  confirmReceipt,
  cancelPurchaseOrder,
  getOverduePurchaseOrders,
  getPurchaseReceipts,
  getPurchaseReceiptItems,
  generateReplenishmentAdvice,
  getReplenishmentAdvice,
  createPurchaseFromAdvice as createPurchaseFromAdviceApi,
  cancelReplenishmentAdvice,
  updateSupplier,
  deleteSupplier
} from '../api/mockApi';

const userStore = useUserStore();
const isAdmin = computed(() => userStore.role === 'admin');
const activeTab = ref('orderList');

// 采购订单列表相关
const orders = ref([]);
const suppliers = ref([]);
const products = ref([]);
const filterSupplier = ref(null);
const filterStatus = ref(null);
const filterOverdue = ref(false);
const orderPage = ref(1);
const orderPageSize = ref(10);
const receiptVisible = ref(false);
const receivingOrder = ref(null);
const receivingItems = ref([]);
const receiving = ref(false);
const overdueCount = ref(0);
const receiptRemark = ref('');
const receiptHistoryVisible = ref(false);
const receiptDetailVisible = ref(false);
const currentOrder = ref(null);
const currentReceipt = ref(null);
const orderReceipts = ref([]);
const receiptDetailItems = ref([]);

// 供应商评估相关
const supplierSortBy = ref('on_time_rate');

// 采购建议相关
const adviceList = ref([]);
const adviceFilter = ref(null);
const generatingAdvice = ref(false);
const createPurchaseFromAdviceVisible = ref(false);
const currentAdvice = ref(null);
const adviceSupplierId = ref(null);
const adviceExpectedDate = ref('');
const creatingPurchase = ref(false);

// 供应商管理相关
const supplierSearchKeyword = ref('');
const supplierPage = ref(1);
const supplierPageSize = ref(10);
const supplierDialogVisible = ref(false);
const isSupplierEdit = ref(false);
const supplierFormRef = ref(null);
const editingSupplierId = ref(null);

const supplierFormData = reactive({
  supplier_name: '',
  contact_person: '',
  contact_phone: '',
  address: ''
});

const supplierFormRules = {
  supplier_name: [{ required: true, message: '请输入供应商名称', trigger: 'blur' }],
  contact_person: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
  contact_phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
  address: [{ required: true, message: '请输入地址', trigger: 'blur' }]
};

// 创建订单相关
const selectedSupplierId = ref(null);
const expectedDate = ref('');
const orderItems = ref([]);
const submitting = ref(false);

const filteredOrders = computed(() => {
  let result = orders.value;
  
  if (filterOverdue.value) {
    const today = new Date().toISOString().slice(0, 10);
    result = result.filter(o => o.status !== 2 && o.expected_date < today);
  }
  
  if (filterSupplier.value) {
    result = result.filter(o => o.supplier_id === filterSupplier.value);
  }
  
  if (filterStatus.value !== null && filterStatus.value !== '') {
    result = result.filter(o => o.status === filterStatus.value);
  }
  
  return result;
});

const displayOrders = computed(() => {
  const start = (orderPage.value - 1) * orderPageSize.value;
  const end = start + orderPageSize.value;
  return filteredOrders.value.slice(start, end);
});

const totalAmount = computed(() => {
  return orderItems.value.reduce((sum, item) => sum + (item.subtotal || 0), 0);
});

// 供应商列表相关计算属性
const filteredSupplierList = computed(() => {
  let result = suppliers.value;
  
  // 搜索过滤
  if (supplierSearchKeyword.value) {
    const keyword = supplierSearchKeyword.value.toLowerCase();
    result = result.filter(s => 
      s.supplier_name.toLowerCase().includes(keyword)
    );
  }
  
  // 排序
  if (supplierSortBy.value === 'on_time_rate') {
    result = [...result].sort((a, b) => (b.on_time_rate || 0) - (a.on_time_rate || 0));
  } else if (supplierSortBy.value === 'delivery_days') {
    result = [...result].sort((a, b) => (a.average_delivery_days || 0) - (b.average_delivery_days || 0));
  } else if (supplierSortBy.value === 'name') {
    result = [...result].sort((a, b) => a.supplier_name.localeCompare(b.supplier_name));
  }
  
  return result;
});

const displaySupplierList = computed(() => {
  const start = (supplierPage.value - 1) * supplierPageSize.value;
  const end = start + supplierPageSize.value;
  return filteredSupplierList.value.slice(start, end);
});

function getSupplierName(supplierId) {
  const supplier = suppliers.value.find(s => s.supplier_id === supplierId);
  return supplier ? supplier.supplier_name : `供应商${supplierId}`;
}

function getStatusType(status) {
  const map = { 0: 'warning', 1: 'info', 2: 'success' };
  return map[status] || 'info';
}

function getStatusText(status) {
  const map = { 0: '待交付', 1: '部分交付', 2: '已完成' };
  return map[status] || '未知';
}

function calculateOrderTotal(purchaseOrderId) {
  const db = JSON.parse(localStorage.getItem('supermarket_db') || '{}');
  const orderItems = (db.purchase_order_items || []).filter(
    item => item.purchase_order_id === purchaseOrderId
  );
  return orderItems.reduce((sum, item) => sum + (item.unit_price || 0) * (item.quantity || 0), 0);
}

async function loadOrders() {
  try {
    orders.value = await getPurchaseOrders();
  } catch (error) {
    ElMessage.error('加载采购订单失败');
  }
}

async function loadSuppliers() {
  try {
    suppliers.value = await getSuppliers();
  } catch (error) {
    ElMessage.error('加载供应商失败');
  }
}

async function loadProducts() {
  try {
    products.value = await getProducts();
  } catch (error) {
    ElMessage.error('加载产品失败');
  }
}

function handleFilterChange() {
  orderPage.value = 1;
}

function handleSizeChange() {
  orderPage.value = 1;
}

function handlePageChange() {}

function handleProductSelect(productId, index) {
  const product = products.value.find(p => p.product_id === productId);
  if (product) {
    orderItems.value[index].product_id = productId;
    orderItems.value[index].product_name = product.product_name;
    orderItems.value[index].unit_price = product.purchase_ref_price || 0;
    calcSubtotal(index);
  }
}

function calcSubtotal(index) {
  const item = orderItems.value[index];
  if (item) {
    item.subtotal = (item.unit_price || 0) * (item.quantity || 0);
  }
}

function addItem() {
  orderItems.value.push({
    product_id: null,
    product_name: '',
    quantity: 1,
    unit_price: 0,
    subtotal: 0
  });
}

function removeItem(index) {
  orderItems.value.splice(index, 1);
}

async function openReceiptDialog(order) {
  receivingOrder.value = order;
  receiptRemark.value = '';
  
  // 获取订单明细
  const db = JSON.parse(localStorage.getItem('supermarket_db') || '{}');
  const orderItemsList = (db.purchase_order_items || []).filter(
    item => item.purchase_order_id === order.purchase_order_id
  );
  
  receivingItems.value = orderItemsList.map(item => {
    const product = products.value.find(p => p.product_id === item.product_id);
    return {
      product_id: item.product_id,
      product_name: product?.product_name || `产品${item.product_id}`,
      quantity: item.quantity,
      unit_price: item.unit_price,
      already_received: item.received_qty || 0,
      received_qty: 0,
      quality_status: '合格'
    };
  });
  
  receiptVisible.value = true;
}

async function handleReceipt() {
  if (!receivingOrder.value) return;
  
  // 验证收货数量
  const hasReceipt = receivingItems.value.some(item => item.received_qty > 0);
  if (!hasReceipt) {
    ElMessage.warning('请至少输入一个实收数量');
    return;
  }
  
  receiving.value = true;
  
  try {
    const actualItems = receivingItems.value
      .filter(item => item.received_qty > 0)
      .map(item => ({
        product_id: item.product_id,
        quantity: item.received_qty,
        quality_status: item.quality_status
      }));
    
    await confirmReceipt(
      receivingOrder.value.purchase_order_id, 
      actualItems, 
      userStore.userInfo?.username || 'system',
      receiptRemark.value
    );
    
    ElMessage.success('收货确认成功，库存已更新');
    receiptVisible.value = false;
    await loadOrders();
    await loadProducts();
    await loadSuppliers();
  } catch (error) {
    ElMessage.error(error.message || '收货确认失败');
  } finally {
    receiving.value = false;
  }
}

async function handleCancelOrder(row) {
  try {
    await ElMessageBox.confirm(
      `确定要取消采购订单 ${row.purchase_order_id} 吗？`,
      '确认取消',
      { type: 'warning' }
    );
    
    await cancelPurchaseOrder(row.purchase_order_id);
    ElMessage.success('采购订单已取消');
    await loadOrders();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '取消失败');
    }
  }
}

async function submitOrder() {
  if (!selectedSupplierId.value) {
    ElMessage.warning('请选择供应商');
    return;
  }
  
  if (!expectedDate.value) {
    ElMessage.warning('请选择期望交付日期');
    return;
  }
  
  const validItems = orderItems.value.filter(item => item.product_id && item.quantity > 0);
  if (validItems.length === 0) {
    ElMessage.warning('请添加至少一件商品');
    return;
  }
  
  submitting.value = true;
  
  try {
    const items = validItems.map(item => ({
      product_id: item.product_id,
      quantity: item.quantity,
      unit_price: item.unit_price
    }));
    
    const orderId = await createPurchaseOrder(
      userStore.userInfo?.user_id || 1,
      selectedSupplierId.value,
      items,
      expectedDate.value
    );
    
    ElMessage.success(`采购订单创建成功：${orderId}`);
    activeTab.value = 'orderList';
    await loadOrders();
    resetForm();
  } catch (error) {
    ElMessage.error(error.message || '创建采购订单失败');
  } finally {
    submitting.value = false;
  }
}

function resetForm() {
  selectedSupplierId.value = null;
  expectedDate.value = '';
  orderItems.value = [];
  addItem();
}

onMounted(() => {
  loadOrders();
  loadSuppliers();
  loadProducts();
  loadOverdueCount();
  addItem();
});

async function loadOverdueCount() {
  const overdueOrders = await getOverduePurchaseOrders();
  overdueCount.value = overdueOrders.length;
}

// 收货历史相关函数
async function viewReceiptHistory(order) {
  currentOrder.value = order;
  try {
    orderReceipts.value = await getPurchaseReceipts(order.purchase_order_id);
  } catch (error) {
    ElMessage.error('加载收货记录失败');
  }
  receiptHistoryVisible.value = true;
}

async function viewReceiptDetail(receipt) {
  currentReceipt.value = receipt;
  try {
    const items = await getPurchaseReceiptItems(receipt.receipt_id);
    receiptDetailItems.value = items.map(item => {
      const product = products.value.find(p => p.product_id === item.product_id);
      return {
        ...item,
        product_name: product?.product_name || `产品${item.product_id}`
      };
    });
  } catch (error) {
    ElMessage.error('加载收货明细失败');
  }
  receiptDetailVisible.value = true;
}

// 供应商评估相关函数
function getRateColor(rate) {
  if (rate >= 90) return '#67c23a';
  if (rate >= 70) return '#e6a23c';
  return '#f56c6c';
}

function getDeliveryDaysStyle(days) {
  if (!days) return {};
  if (days <= 3) return { color: '#67c23a' };
  if (days <= 5) return { color: '#e6a23c' };
  return { color: '#f56c6c' };
}

// 采购建议相关函数
async function generateAdvice() {
  generatingAdvice.value = true;
  try {
    await generateReplenishmentAdvice();
    await loadAdvice();
    ElMessage.success('采购建议生成成功');
  } catch (error) {
    ElMessage.error('生成采购建议失败');
  } finally {
    generatingAdvice.value = false;
  }
}

async function loadAdvice() {
  try {
    let advice = await getReplenishmentAdvice();
    if (adviceFilter.value !== null) {
      advice = advice.filter(a => a.status === adviceFilter.value);
    }
    adviceList.value = advice.map(a => ({
      ...a,
      manual_qty: a.suggested_qty
    }));
  } catch (error) {
    ElMessage.error('加载采购建议失败');
  }
}

function getAdviceStatusType(status) {
  const types = { 0: 'warning', 1: 'success', 2: 'info' };
  return types[status] || 'info';
}

function getAdviceStatusText(status) {
  const texts = { 0: '待处理', 1: '已生成订单', 2: '已取消' };
  return texts[status] || '未知';
}

async function createPurchaseFromAdvice(advice) {
  currentAdvice.value = advice;
  adviceSupplierId.value = null;
  adviceExpectedDate.value = '';
  createPurchaseFromAdviceVisible.value = true;
}

async function submitCreatePurchaseFromAdvice() {
  if (!adviceSupplierId.value) {
    ElMessage.warning('请选择供应商');
    return;
  }
  
  if (!adviceExpectedDate.value) {
    ElMessage.warning('请选择预期交付日期');
    return;
  }
  
  creatingPurchase.value = true;
  
  try {
    const qty = currentAdvice.value.manual_qty || currentAdvice.value.suggested_qty;
    // 修改建议的采购数量
    const tempAdvice = { ...currentAdvice.value, suggested_qty: qty };
    const orderId = await createPurchaseFromAdviceApi(
      tempAdvice.advice_id,
      adviceSupplierId.value,
      adviceExpectedDate.value
    );
    
    ElMessage.success(`采购订单创建成功：${orderId}`);
    createPurchaseFromAdviceVisible.value = false;
    activeTab.value = 'orderList';
    await loadOrders();
    await loadAdvice();
  } catch (error) {
    ElMessage.error(error.message || '创建采购订单失败');
  } finally {
    creatingPurchase.value = false;
  }
}

async function cancelAdvice(advice) {
  try {
    await ElMessageBox.confirm(
      '确定要取消这条采购建议吗？',
      '确认取消',
      { type: 'warning' }
    );
    
    await cancelReplenishmentAdvice(advice.advice_id);
    ElMessage.success('采购建议已取消');
    await loadAdvice();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消采购建议失败');
    }
  }
}

// 监听标签页切换，加载对应数据
watch(activeTab, (newTab) => {
  if (newTab === 'supplierManagement') {
    loadSuppliers();
  } else if (newTab === 'replenishment') {
    loadAdvice();
  }
});

// 监听建议筛选变化
watch(adviceFilter, () => {
  loadAdvice();
});

// 供应商管理相关函数
function handleSupplierSearch() {
  supplierPage.value = 1;
}

function openSupplierAddDialog() {
  isSupplierEdit.value = false;
  editingSupplierId.value = null;
  resetSupplierForm();
  supplierDialogVisible.value = true;
}

function openSupplierEditDialog(row) {
  isSupplierEdit.value = true;
  editingSupplierId.value = row.supplier_id;
  Object.assign(supplierFormData, {
    supplier_name: row.supplier_name,
    contact_person: row.contact_person,
    contact_phone: row.contact_phone,
    address: row.address
  });
  supplierDialogVisible.value = true;
}

function resetSupplierForm() {
  Object.assign(supplierFormData, {
    supplier_name: '',
    contact_person: '',
    contact_phone: '',
    address: ''
  });
  supplierFormRef.value?.clearValidate();
}

async function handleSupplierSubmit() {
  try {
    await supplierFormRef.value.validate();
  } catch {
    return;
  }
  
  try {
    if (isSupplierEdit.value) {
      await updateSupplier(editingSupplierId.value, { ...supplierFormData });
      ElMessage.success('更新成功');
    } else {
      await addSupplier({ ...supplierFormData });
      ElMessage.success('添加成功');
    }
    supplierDialogVisible.value = false;
    await loadSuppliers();
  } catch (error) {
    ElMessage.error(isSupplierEdit.value ? '更新失败' : '添加失败');
  }
}

async function handleSupplierDelete(row) {
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

function handleSupplierSort() {
  // 排序逻辑已在computed属性中实现
  // 这里只需要重置分页到第一页
  supplierPage.value = 1;
}
</script>

<style scoped>
.purchase-container {
  padding: 20px;
}

.page-title {
  margin: 0 0 20px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.purchase-tabs {
  background: #fff;
  padding: 16px;
  border-radius: 4px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.filter-group {
  display: flex;
  align-items: center;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.create-order-form {
  max-width: 900px;
}

.form-section {
  margin-bottom: 20px;
}

.subtotal {
  font-weight: 600;
  color: #409eff;
}

.order-summary {
  margin-top: 16px;
  text-align: right;
  font-size: 16px;
  padding: 10px 0;
}

.total-amount {
  font-size: 24px;
  font-weight: 700;
  color: #f56c6c;
  margin-left: 10px;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 20px 0;
}

.supplier-management {
  width: 100%;
}
</style>