<template>
  <div class="inventory-container">
    <h2 class="page-title">库存管理</h2>
    
    <!-- 库存预警提示条 -->
    <el-alert
      v-if="alertProducts.length > 0"
      :title="`当前有 ${alertProducts.length} 个产品库存低于阈值`"
      type="warning"
      show-icon
      :closable="false"
      class="alert-bar"
    >
      <template #default>
        <span>当前有 <strong>{{ alertProducts.length }}</strong> 个产品库存低于阈值</span>
        <el-button type="warning" link @click="showOnlyAlert = !showOnlyAlert">
          {{ showOnlyAlert ? '显示全部' : '只看预警' }}
        </el-button>
      </template>
    </el-alert>
    
    <!-- 顶部操作栏 -->
    <div class="toolbar">
      <div class="filter-group">
        <el-select
          v-model="filterCategory"
          placeholder="筛选类别"
          clearable
          style="width: 120px; margin-right: 10px"
          @change="handleFilterChange"
        >
          <el-option label="冰箱" value="冰箱" />
          <el-option label="空调" value="空调" />
          <el-option label="电视" value="电视" />
          <el-option label="洗衣机" value="洗衣机" />
          <el-option label="热水器" value="热水器" />
          <el-option label="其他" value="其他" />
        </el-select>
        <el-select
          v-model="filterBrand"
          placeholder="筛选品牌"
          clearable
          style="width: 120px; margin-right: 10px"
          @change="handleFilterChange"
        >
          <el-option
            v-for="brand in availableBrands"
            :key="brand"
            :label="brand"
            :value="brand"
          />
        </el-select>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索产品名称/编号..."
          prefix-icon="Search"
          clearable
          class="search-input"
          @input="handleSearch"
        />
      </div>
      <el-button v-if="isAdmin" type="primary" @click="openAddDialog">
        添加产品
      </el-button>
    </div>
    
    <!-- 表格区域 -->
    <el-table
      :data="displayProducts"
      border
      stripe
      style="width: 100%"
      :row-class-name="getRowClassName"
    >
      <el-table-column prop="product_id" label="产品ID" width="80" />
      <el-table-column prop="product_name" label="产品名称" min-width="150" />
      <el-table-column prop="brand" label="品牌" width="100" />
      <el-table-column prop="model" label="型号" width="120" />
      <el-table-column prop="category" label="类别" width="100" />
      <el-table-column prop="retail_price" label="零售价" width="100">
        <template #default="{ row }">
          ¥{{ row.retail_price.toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column prop="current_stock" label="当前库存" width="100">
        <template #default="{ row }">
          <span :class="{ 'low-stock': row.current_stock <= row.threshold }">
            {{ row.current_stock }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="threshold" label="预警阈值" width="100" />
      <el-table-column prop="unit" label="单位" width="80">
        <template #default="{ row }">
          {{ row.unit || '台' }}
        </template>
      </el-table-column>
      <el-table-column prop="shelf_no" label="货位" width="120">
        <template #default="{ row }">
          {{ row.shelf_no || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="warehouse_zone" label="仓库区域" width="100">
        <template #default="{ row }">
          {{ row.warehouse_zone || '-' }}
        </template>
      </el-table-column>

      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">
            {{ row.status === 1 ? '上架' : '下架' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="300" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="openDetailDrawer(row)">
            详情
          </el-button>
          <template v-if="isAdmin">
            <el-button type="success" link size="small" @click="openEditDialog(row)">
              编辑
            </el-button>
            <el-button 
              v-if="row.status === 1" 
              type="warning" 
              link 
              size="small" 
              @click="handleDisable(row)"
            >
              禁用
            </el-button>
            <el-button 
              v-else 
              type="info" 
              link 
              size="small" 
              @click="handleEnable(row)"
            >
              启用
            </el-button>
            <el-button type="info" link size="small" @click="openAdjustDialog(row)">
              调整库存
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="totalProducts"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
    
    <!-- 添加/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑产品' : '添加产品'"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="产品名称" prop="product_name">
          <el-input v-model="form.product_name" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="品牌" prop="brand">
          <el-input v-model="form.brand" placeholder="请输入品牌" />
        </el-form-item>
        <el-form-item label="型号" prop="model">
          <el-input v-model="form.model" placeholder="请输入型号" />
        </el-form-item>
        <el-form-item label="类别" prop="category">
          <el-select v-model="form.category" placeholder="请选择类别" style="width: 100%">
            <el-option label="冰箱" value="冰箱" />
            <el-option label="空调" value="空调" />
            <el-option label="电视" value="电视" />
            <el-option label="洗衣机" value="洗衣机" />
            <el-option label="热水器" value="热水器" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="零售价" prop="retail_price">
          <el-input-number 
            v-model="form.retail_price" 
            :min="0" 
            :precision="2" 
            :controls="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="采购参考价" prop="purchase_ref_price">
          <el-input-number 
            v-model="form.purchase_ref_price" 
            :min="0" 
            :precision="2" 
            :controls="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="当前库存" prop="current_stock">
          <el-input-number 
            v-model="form.current_stock" 
            :min="0" 
            :precision="0"
            :controls="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="预警阈值" prop="threshold">
          <el-input-number 
            v-model="form.threshold" 
            :min="0" 
            :precision="0"
            :controls="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="销售单位" prop="unit">
          <el-input v-model="form.unit" placeholder="如：台、套、件" />
        </el-form-item>
        <el-form-item label="货位" prop="shelf_no">
          <el-input v-model="form.shelf_no" placeholder="如：A-01-03" />
        </el-form-item>
        <el-form-item label="仓库区域" prop="warehouse_zone">
          <el-select v-model="form.warehouse_zone" placeholder="请选择仓库区域" clearable>
            <el-option label="常温区" value="常温区" />
            <el-option label="大件区" value="大件区" />
            <el-option label="冷藏区" value="冷藏区" />
            <el-option label="特殊区" value="特殊区" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :label="1">上架</el-radio>
            <el-radio :label="0">下架</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 手动调整库存弹窗 -->
    <el-dialog
      v-model="adjustDialogVisible"
      title="手动调整库存"
      width="450px"
    >
      <el-form ref="adjustFormRef" :model="adjustForm" :rules="adjustRules" label-width="100px">
        <el-form-item label="产品名称">
          {{ adjustingProduct?.product_name }}
        </el-form-item>
        <el-form-item label="当前库存">
          {{ adjustingProduct?.current_stock }}
        </el-form-item>
        <el-form-item label="调整类型" prop="type">
          <el-radio-group v-model="adjustForm.type">
            <el-radio label="add">增加</el-radio>
            <el-radio label="reduce">减少</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="调整数量" prop="quantity">
          <el-input-number
            v-model="adjustForm.quantity"
            :min="1"
            :max="adjustForm.type === 'reduce' ? adjustingProduct?.current_stock : 9999"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="调整后库存">
          {{ getAfterStock() }}
        </el-form-item>
        <el-form-item label="原因" prop="reason">
          <el-input
            v-model="adjustForm.reason"
            type="textarea"
            :rows="3"
            placeholder="请输入调整原因（必填）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="adjustDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="adjustLoading" @click="handleAdjust">
          确认调整
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 详情抽屉 -->
    <el-drawer
      v-model="detailDrawerVisible"
      title="商品详情"
      direction="rtl"
      :size="600"
    >
      <template #header>
        <div class="drawer-header">
          <h3>{{ detailProduct?.product_name }}</h3>
          <span class="product-id">ID: {{ detailProduct?.product_id }}</span>
        </div>
      </template>
      
      <div class="detail-content">
        <!-- 基本信息 -->
        <div class="info-section">
          <h4 class="section-title">基本信息</h4>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">品牌：</span>
              <span>{{ detailProduct?.brand }}</span>
            </div>
            <div class="info-item">
              <span class="label">型号：</span>
              <span>{{ detailProduct?.model }}</span>
            </div>
            <div class="info-item">
              <span class="label">类别：</span>
              <span>{{ detailProduct?.category }}</span>
            </div>
            <div class="info-item">
              <span class="label">零售价：</span>
              <span>¥{{ detailProduct?.retail_price.toFixed(2) }}</span>
            </div>
            <div class="info-item">
              <span class="label">采购参考价：</span>
              <span>¥{{ detailProduct?.purchase_ref_price.toFixed(2) }}</span>
            </div>
            <div class="info-item">
              <span class="label">当前库存：</span>
              <span :class="{ 'low-stock': detailProduct?.current_stock <= detailProduct?.threshold }">
                {{ detailProduct?.current_stock }}
              </span>
            </div>
            <div class="info-item">
              <span class="label">预警阈值：</span>
              <span>{{ detailProduct?.threshold }}</span>
            </div>
            <div class="info-item">
              <span class="label">销售单位：</span>
              <span>{{ detailProduct?.unit || '台' }}</span>
            </div>
            <div class="info-item">
              <span class="label">货位：</span>
              <span>{{ detailProduct?.shelf_no || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">仓库区域：</span>
              <span>{{ detailProduct?.warehouse_zone || '-' }}</span>
            </div>

            <div class="info-item">
              <span class="label">状态：</span>
              <el-tag :type="detailProduct?.status === 1 ? 'success' : 'info'" size="small">
                {{ detailProduct?.status === 1 ? '上架' : '下架' }}
              </el-tag>
            </div>
          </div>
        </div>
        

        
        <!-- 标签页 -->
        <el-tabs v-model="activeTab" class="detail-tabs">
          <!-- 库存流水 -->
          <el-tab-pane label="库存流水" name="stock">
            <el-table :data="stockLogs" border stripe>
              <el-table-column prop="change_type" label="变动类型" width="120">
                <template #default="{ row }">
                  <el-tag :type="getChangeTypeTag(row.change_type)">
                    {{ getChangeTypeName(row.change_type) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="change_qty" label="变动数量" width="100" />
              <el-table-column prop="before_quantity" label="变动前库存" width="120" />
              <el-table-column prop="after_quantity" label="变动后库存" width="120" />
              <el-table-column prop="operator" label="操作人" width="100" />
              <el-table-column prop="operate_time" label="操作时间" width="160" />
              <el-table-column prop="remark" label="备注" />
            </el-table>
            <div v-if="stockLogs.length === 0" class="empty-tip">暂无库存流水记录</div>
          </el-tab-pane>
          
          <!-- 修改记录 -->
          <el-tab-pane label="修改记录" name="edit">
            <el-table :data="editLogs" border stripe>
              <el-table-column prop="field_name" label="修改字段" width="120">
                <template #default="{ row }">{{ getFieldDisplayName(row.field_name) }}</template>
              </el-table-column>
              <el-table-column prop="old_value" label="旧值" width="150" />
              <el-table-column prop="new_value" label="新值" width="150" />
              <el-table-column prop="operator" label="操作人" width="100" />
              <el-table-column prop="operate_time" label="操作时间" width="160" />
            </el-table>
            <div v-if="editLogs.length === 0" class="empty-tip">暂无修改记录</div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue';
import { ElMessage, ElMessageBox, ElTag } from 'element-plus';
import { useUserStore } from '../stores/user';
import eventBus from '../utils/eventBus';
import { 
  getProducts, 
  addProduct, 
  updateProduct, 
  disableProduct, 
  enableProduct,
  deleteProduct,
  getAlertProducts,
  manualAdjust,
  getStockLog,
  getProductEditLogs
} from '../api/mockApi';

const userStore = useUserStore();

const isAdmin = computed(() => userStore.role === 'admin');

let unsubscribeOrderDeleted = null;

const products = ref([]);
const alertProducts = ref([]);
const searchKeyword = ref('');
const filterCategory = ref(null);
const filterBrand = ref(null);
const showOnlyAlert = ref(false);
const currentPage = ref(1);
const pageSize = ref(10);
const dialogVisible = ref(false);
const isEdit = ref(false);
const submitLoading = ref(false);
const formRef = ref(null);
const editingId = ref(null);

const adjustDialogVisible = ref(false);
const adjustFormRef = ref(null);
const adjustingProduct = ref(null);
const adjustLoading = ref(false);

const adjustForm = reactive({
  type: 'add',
  quantity: 1,
  reason: ''
});

// 详情抽屉
const detailDrawerVisible = ref(false);
const detailProduct = ref(null);
const activeTab = ref('stock');
const stockLogs = ref([]);
const editLogs = ref([]);

const adjustRules = {
  type: [{ required: true, message: '请选择调整类型', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入调整数量', trigger: 'blur' }],
  reason: [{ required: true, message: '请输入调整原因', trigger: 'blur' }]
};

const form = reactive({
  product_name: '',
  brand: '',
  model: '',
  category: '',
  retail_price: 0,
  purchase_ref_price: 0,
  current_stock: 0,
  threshold: 5,
  unit: '台',
  shelf_no: '',
  warehouse_zone: '',
  status: 1
});

const formRules = {
  product_name: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
  brand: [{ required: true, message: '请输入品牌', trigger: 'blur' }],
  model: [{ required: true, message: '请输入型号', trigger: 'blur' }],
  category: [{ required: true, message: '请选择类别', trigger: 'change' }],
  retail_price: [{ required: true, message: '请输入零售价', trigger: 'blur' }],
  current_stock: [{ required: true, message: '请输入库存', trigger: 'blur' }],
  threshold: [{ required: true, message: '请输入预警阈值', trigger: 'blur' }]
};

const availableBrands = computed(() => {
  const brands = [...new Set(products.value.map(p => p.brand))];
  return brands.sort();
});

const totalProducts = computed(() => {
  return showOnlyAlert.value ? alertProducts.value.length : filteredProducts.value.length;
});

const filteredProducts = computed(() => {
  let result = products.value;
  
  if (filterCategory.value) {
    result = result.filter(p => p.category === filterCategory.value);
  }
  
  if (filterBrand.value) {
    result = result.filter(p => p.brand === filterBrand.value);
  }
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase();
    result = result.filter(p => 
      p.product_name.toLowerCase().includes(keyword) ||
      String(p.product_id).includes(keyword)
    );
  }
  
  return result;
});

const displayProducts = computed(() => {
  const list = showOnlyAlert.value ? alertProducts.value : filteredProducts.value;
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return list.slice(start, end);
});

function getRowClassName({ row }) {
  return row.current_stock <= row.threshold ? 'low-stock-row' : '';
}

function getAfterStock() {
  if (!adjustingProduct.value) return 0;
  const delta = adjustForm.type === 'add' ? adjustForm.quantity : -adjustForm.quantity;
  return adjustingProduct.value.current_stock + delta;
}

function handleFilterChange() {
  currentPage.value = 1;
}

let searchTimer = null;
function handleSearch() {
  if (searchTimer) clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    currentPage.value = 1;
  }, 300);
}

function handleSizeChange() {
  currentPage.value = 1;
}

function handlePageChange() {}

async function loadProducts() {
  try {
    products.value = await getProducts();
  } catch (error) {
    ElMessage.error('加载产品列表失败');
  }
}

async function loadAlertProducts() {
  try {
    alertProducts.value = await getAlertProducts();
  } catch (error) {
    console.error('加载预警产品失败', error);
  }
}

function openAddDialog() {
  isEdit.value = false;
  editingId.value = null;
  resetForm();
  dialogVisible.value = true;
}

function openEditDialog(row) {
  isEdit.value = true;
  editingId.value = row.product_id;
  Object.assign(form, {
    product_name: row.product_name,
    brand: row.brand,
    model: row.model,
    category: row.category,
    retail_price: row.retail_price,
    purchase_ref_price: row.purchase_ref_price,
    current_stock: row.current_stock,
    threshold: row.threshold,
    unit: row.unit || '台',
    shelf_no: row.shelf_no || '',
    warehouse_zone: row.warehouse_zone || '',
    status: row.status
  });
  dialogVisible.value = true;
}

function resetForm() {
  Object.assign(form, {
    product_name: '',
    brand: '',
    model: '',
    category: '',
    retail_price: 0,
    purchase_ref_price: 0,
    current_stock: 0,
    threshold: 5,
    unit: '台',
    shelf_no: '',
    warehouse_zone: '',
    status: 1
  });
  formRef.value?.clearValidate();
}

function handleDialogClose() {
  resetForm();
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
    if (isEdit.value) {
      await updateProduct(editingId.value, { ...form });
      ElMessage.success('更新成功');
    } else {
      await addProduct({ ...form });
      ElMessage.success('添加成功');
    }
    dialogVisible.value = false;
    await loadProducts();
    await loadAlertProducts();
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '添加失败');
  } finally {
    submitLoading.value = false;
  }
}

async function handleDisable(row) {
  try {
    await ElMessageBox.confirm(
      `确定要禁用产品 "${row.product_name}" 吗？`,
      '确认禁用',
      { type: 'warning' }
    );
    await disableProduct(row.product_id);
    ElMessage.success('禁用成功');
    await loadProducts();
    await loadAlertProducts();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('禁用失败');
    }
  }
}

async function handleEnable(row) {
  try {
    await enableProduct(row.product_id);
    ElMessage.success('启用成功');
    await loadProducts();
    await loadAlertProducts();
  } catch (error) {
    ElMessage.error('启用失败');
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除产品 "${row.product_name}" 吗？`,
      '确认删除',
      { type: 'warning' }
    );
    
    const result = await deleteProduct(row.product_id);
    
    if (!result.canDelete) {
      await ElMessageBox.alert(
        result.message,
        '无法删除',
        {
          type: 'warning',
          confirmButtonText: '设为禁用',
          cancelButtonText: '取消'
        }
      ).then(() => {
        disableProduct(row.product_id).then(() => {
          ElMessage.success('已设为禁用');
          loadProducts();
          loadAlertProducts();
        });
      }).catch(() => {});
      return;
    }
    
    ElMessage.success('删除成功');
    await loadProducts();
    await loadAlertProducts();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败');
    }
  }
}

function openAdjustDialog(row) {
  adjustingProduct.value = row;
  adjustForm.type = 'add';
  adjustForm.quantity = 1;
  adjustForm.reason = '';
  adjustDialogVisible.value = true;
}

async function handleAdjust() {
  if (!adjustFormRef.value) return;
  
  try {
    await adjustFormRef.value.validate();
  } catch {
    return;
  }
  
  adjustLoading.value = true;
  
  try {
    const delta = adjustForm.type === 'add' ? adjustForm.quantity : -adjustForm.quantity;
    const operatorId = userStore.userInfo?.user_id || 1;
    
    await manualAdjust(operatorId, adjustingProduct.value.product_id, delta, adjustForm.reason);
    
    ElMessage.success('库存调整成功');
    adjustDialogVisible.value = false;
    await loadProducts();
    await loadAlertProducts();
  } catch (error) {
    ElMessage.error('库存调整失败：' + (error.message || '库存不足'));
  } finally {
    adjustLoading.value = false;
  }
}

async function openDetailDrawer(row) {
  detailProduct.value = row;
  detailDrawerVisible.value = true;
  activeTab.value = 'stock';
  
  await loadStockLogs(row.product_id);
  await loadEditLogs(row.product_id);
}



async function loadStockLogs(productId) {
  try {
    const logs = await getStockLog(productId);
    stockLogs.value = logs;
  } catch (error) {
    ElMessage.error('加载库存流水失败');
    stockLogs.value = [];
  }
}

async function loadEditLogs(productId) {
  try {
    const logs = await getProductEditLogs(productId);
    editLogs.value = logs;
  } catch (error) {
    ElMessage.error('加载修改记录失败');
    editLogs.value = [];
  }
}

function getChangeTypeName(type) {
  const typeMap = {
    1: '手动调整',
    2: '采购入库',
    3: '销售出库',
    4: '盘盈',
    5: '盘亏',
    6: '调拨出库',
    7: '调拨入库',
    8: '退货'
  };
  return typeMap[type] || '未知';
}

function getChangeTypeTag(type) {
  const typeMap = {
    1: 'warning',
    2: 'success',
    3: 'danger',
    4: 'success',
    5: 'danger',
    6: 'warning',
    7: 'success',
    8: 'info'
  };
  return typeMap[type] || 'info';
}

function getFieldDisplayName(fieldName) {
  const fieldMap = {
    product_name: '产品名称',
    brand: '品牌',
    model: '型号',
    category: '类别',
    retail_price: '零售价',
    purchase_ref_price: '采购参考价',
    current_stock: '当前库存',
    threshold: '预警阈值',
    unit: '销售单位',
    shelf_no: '货位',
    warehouse_zone: '仓库区域',
    status: '状态'
  };
  return fieldMap[fieldName] || fieldName;
}

onMounted(() => {
  loadProducts();
  loadAlertProducts();
  
  unsubscribeOrderDeleted = () => {
    loadProducts();
    loadAlertProducts();
  };
  eventBus.on('orderDeleted', unsubscribeOrderDeleted);
});

onUnmounted(() => {
  if (unsubscribeOrderDeleted) {
    eventBus.off('orderDeleted', unsubscribeOrderDeleted);
  }
});
</script>

<style scoped>
.inventory-container {
  padding: 20px;
}

.page-title {
  margin: 0 0 20px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.alert-bar {
  margin-bottom: 16px;
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

.search-input {
  width: 300px;
}

.low-stock {
  color: #f56c6c;
  font-weight: 600;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.low-stock-row) {
  background-color: #fef0f0 !important;
}

:deep(.low-stock-row:hover > td) {
  background-color: #fee !important;
}

.readonly-tip {
  color: #909399;
  font-size: 12px;
}

/* 详情抽屉样式 */
.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.product-id {
  font-size: 14px;
  color: #909399;
}

.detail-content {
  padding: 20px 0;
}

.info-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeeef;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-item .label {
  color: #909399;
  margin-right: 8px;
}

.detail-tabs {
  margin-top: 0;
}

.empty-tip {
  text-align: center;
  color: #909399;
  padding: 40px;
}
</style>