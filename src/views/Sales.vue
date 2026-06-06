<template>
  <div class="sales-container">
    <h2 class="page-title">销售管理</h2>
    
    <el-tabs v-model="activeTab" class="sales-tabs">
      <!-- 标签1：销售订单列表 -->
      <el-tab-pane label="销售订单列表" name="orderList">
        <div class="toolbar">
          <div class="filter-panel">
            <div class="filter-row">
              <el-select
                v-model="quickDateRange"
                placeholder="选择时间范围"
                style="width: 140px"
                @change="handleQuickDateChange"
              >
                <el-option label="全部时间" value="" />
                <el-option label="今日" value="today" />
                <el-option label="本周" value="week" />
                <el-option label="本月" value="month" />
                <el-option label="本季度" value="quarter" />
                <el-option label="本年" value="year" />
                <el-option label="自定义" value="custom" />
              </el-select>
              
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
                style="width: 250px; margin-left: 10px"
                :disabled="quickDateRange !== 'custom' && quickDateRange !== ''"
                @change="handleDateChange"
              />
            </div>
            
            <div class="filter-row">
              <el-select
                v-model="filterStatus"
                placeholder="订单状态"
                clearable
                style="width: 140px"
                @change="handleFilterChange"
              >
                <el-option label="全部状态" value="" />
                <el-option label="待支付" value="pending" />
                <el-option label="订单已完成" value="completed" />
                <el-option label="已退货" value="returned" />
              </el-select>
              
              <el-select
                v-model="filterCategory"
                placeholder="产品类别"
                clearable
                style="width: 140px; margin-left: 10px"
                @change="handleFilterChange"
              >
                <el-option label="全部类别" value="" />
                <el-option label="冰箱" value="冰箱" />
                <el-option label="空调" value="空调" />
                <el-option label="电视" value="电视" />
                <el-option label="洗衣机" value="洗衣机" />
                <el-option label="热水器" value="热水器" />
                <el-option label="其他" value="其他" />
              </el-select>
              
              <el-select
                v-model="filterPaymentMethod"
                placeholder="支付方式"
                clearable
                style="width: 140px; margin-left: 10px"
                @change="handleFilterChange"
              >
                <el-option label="全部方式" value="" />
                <el-option label="微信支付" value="微信支付" />
                <el-option label="支付宝" value="支付宝" />
                <el-option label="银行卡" value="银行卡" />
                <el-option label="现金" value="现金" />
              </el-select>
            </div>
            
            <div class="filter-row">
              <el-input
                v-model="orderSearch"
                placeholder="搜索订单号/客户名"
                prefix-icon="Search"
                clearable
                style="width: 250px"
                @input="handleOrderSearch"
              />
              
              <el-button
                type="primary"
                style="margin-left: 10px"
                @click="applyFilters"
              >
                筛选
              </el-button>
              
              <el-button
                style="margin-left: 10px"
                @click="clearFilters"
              >
                重置
              </el-button>
            </div>
          </div>
        </div>
        
        <el-table :data="displayOrders" border stripe style="width: 100%">
      <el-table-column prop="order_id" label="订单号" width="180" />
      <el-table-column label="客户名称" width="140">
        <template #default="{ row }">
          {{ getCustomerName(row.customer_id) }}
        </template>
      </el-table-column>
      <el-table-column prop="order_time" label="订单时间" width="170" />
      <el-table-column label="商品总额" width="120">
        <template #default="{ row }">
          ¥{{ row.total_amount.toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column label="会员折扣" width="110">
        <template #default="{ row }">
          <span v-if="row.discount_amount > 0" style="color: #f56c6c">
            -¥{{ row.discount_amount.toFixed(2) }}
          </span>
          <span v-else style="color: #909399">-</span>
        </template>
      </el-table-column>
      <el-table-column label="积分抵扣" width="110">
        <template #default="{ row }">
          <span v-if="row.points_used > 0" style="color: #e6a23c">
            {{ row.points_used }}积分抵¥{{ (row.points_discount || row.points_used / 100).toFixed(2) }}
          </span>
          <span v-else style="color: #909399">-</span>
        </template>
      </el-table-column>
      <el-table-column label="实付金额" width="120">
        <template #default="{ row }">
          <span style="font-weight: bold; color: #67c23a">
            ¥{{ (row.final_amount || row.total_amount).toFixed(2) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="获得积分" width="100">
        <template #default="{ row }">
          <span v-if="row.points_earned > 0" style="color: #409eff">
            +{{ row.points_earned }}
          </span>
          <span v-else style="color: #909399">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="payment_method" label="支付方式" width="100" />
      <el-table-column prop="remark" label="备注" min-width="150" />
      <el-table-column label="订单状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getOrderStatusType(row)" size="small">
            {{ getOrderStatusText(row) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="320" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="viewOrderDetail(row)">
            查看详情
          </el-button>
          <el-button 
            v-if="getOrderStatus(row) === 'pending'" 
            type="success" 
            link 
            size="small" 
            @click="handlePayOrder(row)"
          >
            支付
          </el-button>
          <el-button 
            v-if="getOrderStatus(row) === 'completed' && !row.is_returned" 
            type="warning" 
            link 
            size="small" 
            @click="handleReturnOrder(row)"
          >
            退货
          </el-button>
          <el-button 
            v-if="hasDeletePermission" 
            type="danger" 
            link 
            size="small" 
            :disabled="getOrderStatus(row) === 'completed'"
            @click="handleDeleteOrder(row)"
          >
            删除订单
          </el-button>
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
            @size-change="handleOrderSizeChange"
            @current-change="handleOrderPageChange"
          />
        </div>
      </el-tab-pane>
      
      <!-- 标签2：创建销售订单 -->
      <el-tab-pane label="创建销售订单" name="createOrder">
        <div class="create-order-form">
          <!-- 客户信息 -->
          <el-card class="form-section" shadow="never">
            <template #header>
              <span>客户信息</span>
            </template>
            <el-form label-width="100px">
              <el-form-item label="选择客户">
                <el-select
                  v-model="selectedCustomerId"
                  placeholder="请选择客户"
                  filterable
                  style="width: 300px"
                  @change="handleCustomerChange"
                >
                  <el-option
                    v-for="c in customers"
                    :key="c.customer_id"
                    :label="`${c.name} - ${c.phone}${c.membership_level !== '普通会员' ? ` (${c.membership_level})` : ''}`"
                    :value="c.customer_id"
                  />
                </el-select>
                <el-button type="primary" link style="margin-left: 16px" @click="showAddCustomer = true">
                  新增客户
                </el-button>
              </el-form-item>
              <el-form-item v-if="selectedCustomer" label="客户姓名">
                {{ selectedCustomer.name }}
              </el-form-item>
              <el-form-item v-if="selectedCustomer" label="联系电话">
                {{ selectedCustomer.phone }}
              </el-form-item>
              <el-form-item v-if="selectedCustomer" label="收货地址">
                {{ selectedCustomer.address }}
              </el-form-item>
            </el-form>
            
            <!-- 会员信息展示 -->
            <div v-if="selectedCustomer && selectedCustomer.membership_level" class="member-info-card">
              <el-divider content-position="left">会员信息</el-divider>
              <el-descriptions :column="2" border size="small">
                <el-descriptions-item label="会员等级">
                  <el-tag :type="getMemberLevelType(selectedCustomer.membership_level)" size="small">
                    {{ selectedCustomer.membership_level }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="折扣率">
                  {{ (selectedCustomer.discount_rate * 100).toFixed(0) }}折
                </el-descriptions-item>
                <el-descriptions-item label="当前积分">
                  <el-tag type="warning" size="small">{{ selectedCustomer.points }} 积分</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="积分过期">
                  {{ selectedCustomer.points_expiry_date }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </el-card>
          
          <!-- 商品选择 -->
          <el-card class="form-section" shadow="never">
            <template #header>
              <span>商品选择</span>
              <el-input
                v-model="quickSearchKeyword"
                placeholder="输入产品编号快速搜索..."
                class="quick-search-input"
                clearable
                @keyup.enter="handleQuickSearch"
              />
            </template>
            <el-table :data="cartItems" border style="width: 100%">
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
                      v-for="p in availableProducts(row.product_id)"
                      :key="p.product_id"
                      :label="`${p.product_name} (库存:${p.current_stock})`"
                      :value="p.product_id"
                      :disabled="p.current_stock <= 0"
                    />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column label="数量" width="150">
                <template #default="{ row }">
                  <el-input-number
                    v-model="row.quantity"
                    :min="1"
                    :max="row.maxStock || 999"
                    :disabled="!row.product_id"
                    @change="calcSubtotal($index)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="单价" width="120">
                <template #default="{ row }">
                  ¥{{ (row.unit_price || 0).toFixed(2) }}
                </template>
              </el-table-column>
              <el-table-column label="小计" width="120">
                <template #default="{ row }">
                  <span class="subtotal">¥{{ (row.subtotal || 0).toFixed(2) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80">
                <template #default="{ $index }">
                  <el-button type="danger" link @click="removeCartItem($index)">
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <el-button type="primary" plain style="margin-top: 16px" @click="addCartItem">
              + 添加商品
            </el-button>
            
            <!-- 会员优惠计算 -->
            <div v-if="selectedCustomer && selectedCustomer.membership_level" class="member-discount-section">
              <el-divider content-position="left">会员优惠</el-divider>
              <el-form label-width="140px">
                <el-form-item label="会员等级">
                  <el-tag :type="getMemberLevelType(selectedCustomer.membership_level)" size="small">
                    {{ selectedCustomer.membership_level }}
                  </el-tag>
                  <span style="margin-left: 10px; color: #909399">
                    折扣率: {{ (selectedCustomer.discount_rate * 100).toFixed(0) }}%
                  </span>
                </el-form-item>
                <el-form-item label="当前积分">
                  <el-tag type="warning" size="small">
                    {{ selectedCustomer.points }} 积分
                  </el-tag>
                  <span style="margin-left: 10px; color: #909399">
                    有效期至: {{ selectedCustomer.points_expiry_date }}
                  </span>
                </el-form-item>
                <el-form-item label="会员折扣优惠">
                  <span class="discount-amount">
                    ¥{{ memberDiscountAmount.toFixed(2) }}
                  </span>
                </el-form-item>
                <el-form-item label="积分抵扣">
                  <el-checkbox v-model="usePoints" :disabled="!canUsePoints">
                    使用积分抵扣（当前可用 {{ maxPointsToUse }} 积分抵 ¥{{ maxPointsDiscount }}）
                  </el-checkbox>
                </el-form-item>
                <el-form-item v-if="usePoints" label="使用积分">
                  <el-input-number
                    v-model="pointsToUse"
                    :min="100"
                    :max="maxPointsToUse"
                    :step="100"
                    @change="calcPointsDiscount"
                    style="margin-right: 10px"
                  />
                  <el-button-group>
                    <el-button size="small" @click="setPoints(100)">100积分</el-button>
                    <el-button size="small" @click="setPoints(500)">500积分</el-button>
                    <el-button size="small" @click="setPoints(1000)">1000积分</el-button>
                    <el-button size="small" @click="setPoints(maxPointsToUse)">全部</el-button>
                  </el-button-group>
                  <span style="margin-left: 10px">
                    可抵金额：¥{{ pointsDiscount.toFixed(2) }}
                  </span>
                </el-form-item>
              </el-form>
            </div>
            
            <div class="cart-summary">
              <div class="summary-item">
                <span>商品总价：</span>
                <span>¥{{ totalAmount.toFixed(2) }}</span>
              </div>
              <div v-if="memberDiscountAmount > 0" class="summary-item discount">
                <span>会员折扣：</span>
                <span>-¥{{ memberDiscountAmount.toFixed(2) }}</span>
              </div>
              <div v-if="pointsDiscount > 0" class="summary-item points">
                <span>积分抵扣：</span>
                <span>-¥{{ pointsDiscount.toFixed(2) }}</span>
              </div>
              <div class="summary-item final">
                <span>应付金额：</span>
                <span class="final-amount">¥{{ finalAmount.toFixed(2) }}</span>
              </div>
            </div>
          </el-card>
          
          <!-- 支付信息 -->
          <el-card class="form-section" shadow="never">
            <template #header>
              <span>支付信息</span>
            </template>
            <el-form label-width="100px">
              <el-form-item label="支付方式">
                <el-radio-group v-model="paymentMethod">
                  <el-radio label="微信支付">微信支付</el-radio>
                  <el-radio label="支付宝">支付宝</el-radio>
                  <el-radio label="现金">现金</el-radio>
                  <el-radio label="银行卡">银行卡</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item label="收货地址">
                <el-input
                  v-model="shippingAddress"
                  type="textarea"
                  :rows="2"
                  placeholder="请输入收货地址"
                  style="width: 400px"
                />
              </el-form-item>
            </el-form>
          </el-card>
          
          <!-- 提交按钮 -->
          <div class="form-actions">
            <el-button @click="resetForm">重置</el-button>
            <el-button type="primary" :loading="submitting" @click="submitOrder">
              确认下单
            </el-button>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 订单详情弹窗 -->
    <el-dialog v-model="detailVisible" title="订单详情" width="700px">
      <div v-if="orderDetail" class="order-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单号">{{ orderDetail.order_id }}</el-descriptions-item>
          <el-descriptions-item label="订单时间">{{ orderDetail.order_time }}</el-descriptions-item>
          <el-descriptions-item label="客户名称">{{ getCustomerName(orderDetail.customer_id) }}</el-descriptions-item>
          <el-descriptions-item label="支付方式">{{ orderDetail.payment_method }}</el-descriptions-item>
          <el-descriptions-item label="订单状态">
            <el-tag :type="getOrderStatusType(orderDetail)">
              {{ getOrderStatusText(orderDetail) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="收货地址" :span="2">{{ orderDetail.shipping_address }}</el-descriptions-item>
        </el-descriptions>
        
        <div v-if="orderDetail.is_returned" class="return-info-section">
          <el-divider content-position="left">
            <span>退货信息</span>
          </el-divider>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="退货状态">
              <el-tag type="danger">已退货</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="退货时间">{{ orderDetail.return_time }}</el-descriptions-item>
            <el-descriptions-item label="退货原因" :span="2">{{ orderDetail.return_reason }}</el-descriptions-item>
            <el-descriptions-item label="退货说明" :span="2">{{ orderDetail.return_remark || '-' }}</el-descriptions-item>
          </el-descriptions>
        </div>
        
        <h4 style="margin: 20px 0 10px">商品明细</h4>
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
        
        <!-- 会员优惠信息 -->
        <div v-if="orderDetail.discount_amount > 0 || orderDetail.points_used > 0 || orderDetail.points_earned > 0" class="member-discount-detail">
          <el-divider content-position="left">会员优惠</el-divider>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item v-if="orderDetail.discount_amount > 0" label="会员折扣">
              <span class="discount-text">-¥{{ orderDetail.discount_amount.toFixed(2) }}</span>
            </el-descriptions-item>
            <el-descriptions-item v-if="orderDetail.points_used > 0" label="积分抵扣">
              <div>
                <span class="points-text">{{ orderDetail.points_used }}积分抵¥{{ (orderDetail.points_discount || orderDetail.points_used / 100).toFixed(2) }}</span>
                <div style="font-size: 12px; color: #909399; margin-top: 4px">
                  抵扣比例：100积分 = 1元
                </div>
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="获得积分">
              <el-tag type="success" size="small">+{{ orderDetail.points_earned || 0 }} 积分</el-tag>
            </el-descriptions-item>
            <el-descriptions-item v-if="orderDetail.points_earned > 0" label="积分规则">
              <span style="font-size: 12px; color: #909399">消费1元获得1积分</span>
            </el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="detail-total">
          商品总价：<span>¥{{ orderDetail.total_amount.toFixed(2) }}</span>
        </div>
        <div v-if="orderDetail.discount_amount > 0" class="detail-total discount">
          会员折扣：<span>-¥{{ orderDetail.discount_amount.toFixed(2) }}</span>
        </div>
        <div v-if="orderDetail.points_used > 0" class="detail-total points">
          积分抵扣：<span>-¥{{ (orderDetail.points_discount || orderDetail.points_used / 100).toFixed(2) }}</span>
        </div>
        <div class="detail-total final">
          实际支付：<span class="final-amount">¥{{ (orderDetail.final_amount || orderDetail.total_amount).toFixed(2) }}</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        
        <el-button
          v-if="orderDetail && getOrderStatus(orderDetail) === 'pending'"
          type="primary"
          :loading="paying"
          @click="handlePay"
        >
          <span class="btn-icon">💰</span>
          立即支付
        </el-button>
        
        <el-button
          v-if="orderDetail && getOrderStatus(orderDetail) === 'pending' && hasDeletePermission"
          type="danger"
          @click="handleDeleteFromDetail"
        >
          <span class="btn-icon">🗑️</span>
          删除订单
        </el-button>
        
        <el-button
          v-if="orderDetail && getOrderStatus(orderDetail) === 'completed' && !orderDetail.is_returned"
          type="warning"
          @click="handleReturnFromDetail"
        >
          <span class="btn-icon">🔄</span>
          申请退货
        </el-button>
        
        <el-button
          v-if="orderDetail && getOrderStatus(orderDetail) === 'completed'"
          type="info"
          @click="openPrintReceipt"
        >
          <span class="btn-icon">🖨️</span>
          打印收据
        </el-button>
        
        <el-button
          v-if="orderDetail && getOrderStatus(orderDetail) === 'returned'"
          type="success"
          disabled
        >
          <span class="btn-icon">✅</span>
          已退货
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 打印收据弹窗 -->
    <PrintReceipt
      v-model="printVisible"
      :order="printOrder"
    />
    
    <!-- 新增客户弹窗 -->
    <el-dialog v-model="showAddCustomer" title="新增客户" width="450px">
      <el-form ref="customerFormRef" :model="customerForm" :rules="customerRules" label-width="100px">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="customerForm.name" placeholder="请输入客户姓名" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="customerForm.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="customerForm.address" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="customerForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-divider content-position="left">会员信息</el-divider>
        <el-form-item label="会员等级">
          <el-select v-model="customerForm.membership_level" placeholder="请选择会员等级">
            <el-option label="普通会员" value="普通会员" />
            <el-option label="白银会员" value="白银会员" />
            <el-option label="黄金会员" value="黄金会员" />
          </el-select>
        </el-form-item>
        <el-form-item label="初始积分">
          <el-input-number v-model="customerForm.points" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddCustomer = false">取消</el-button>
        <el-button type="primary" @click="handleAddCustomer">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus';
import PrintReceipt from '../components/PrintReceipt.vue';
import { useUserStore } from '../stores/user';
import { useRouter } from 'vue-router';
import eventBus from '../utils/eventBus';
import {
  getOrderHistory,
  getOrderDetail,
  createOrder as createOrderApi,
  payOrder as payOrderApi,
  deleteOrder,
  getCustomers,
  addCustomer as addCustomerApi,
  getProducts
} from '../api/realApi';

const userStore = useUserStore();
const isAdmin = computed(() => userStore.role === 'admin');
const hasDeletePermission = computed(() => userStore.role === 'admin');
const router = useRouter();

const activeTab = ref('orderList');

// 订单列表相关
const orders = ref([]);
const customers = ref([]);
const orderSearch = ref('');
const dateRange = ref(null);
const orderPage = ref(1);
const orderPageSize = ref(10);
const detailVisible = ref(false);
const orderDetail = ref(null);
const paying = ref(false);
const submitting = ref(false);
const printVisible = ref(false);
const printOrder = ref(null);

// 筛选条件
const quickDateRange = ref('');
const filterStatus = ref('');
const filterCategory = ref('');
const filterPaymentMethod = ref('');

// 创建订单相关
const selectedCustomerId = ref(null);
const cartItems = ref([]);
const paymentMethod = ref('微信支付');
const shippingAddress = ref('');
const showAddCustomer = ref(false);
const customerFormRef = ref(null);
const quickSearchKeyword = ref('');

const customerForm = reactive({
  name: '',
  phone: '',
  address: '',
  email: '',
  membership_level: '普通会员',
  points: 0
});

const customerRules = {
  name: [{ required: true, message: '请输入客户姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }]
};

const selectedCustomer = computed(() => {
  if (!selectedCustomerId.value) return null;
  return customers.value.find(c => c.customer_id === selectedCustomerId.value) || null;
});

// 会员优惠相关
const usePoints = ref(false);
const pointsToUse = ref(0);
const pointsDiscount = ref(0);

const memberDiscountAmount = computed(() => {
  if (!selectedCustomer.value) return 0;
  const discountRate = selectedCustomer.value.discount_rate || 1;
  return totalAmount.value * (1 - discountRate);
});

const canUsePoints = computed(() => {
  if (!selectedCustomer.value) return false;
  return selectedCustomer.value.points >= 100 && totalAmount.value > 0;
});

const maxPointsToUse = computed(() => {
  if (!selectedCustomer.value) return 0;
  const maxPointsByDiscount = Math.floor(totalAmount.value * 100); // 最多抵扣全额
  return Math.min(selectedCustomer.value.points, maxPointsByDiscount, 1000); // 单笔最多1000积分 = 10元
});

const maxPointsDiscount = computed(() => {
  return (maxPointsToUse.value / 100);
});

const calcPointsDiscount = () => {
  if (usePoints.value && pointsToUse.value > 0) {
    pointsDiscount.value = pointsToUse.value / 100;
  } else {
    pointsDiscount.value = 0;
  }
};

const finalAmount = computed(() => {
  let amount = totalAmount.value;
  if (selectedCustomer.value) {
    amount -= memberDiscountAmount.value;
  }
  amount -= pointsDiscount.value;
  return Math.max(0, amount);
});

const totalAmount = computed(() => {
  return cartItems.value.reduce((sum, item) => sum + (item.subtotal || 0), 0);
});

const filteredOrders = computed(() => {
  let result = orders.value;
  
  if (orderSearch.value) {
    const keyword = orderSearch.value.toLowerCase();
    result = result.filter(o => {
      const customerName = getCustomerName(o.customer_id).toLowerCase();
      return o.order_id.toLowerCase().includes(keyword) || customerName.includes(keyword);
    });
  }
  
  if (filterStatus.value) {
    result = result.filter(o => getOrderStatus(o) === filterStatus.value);
  }
  
  if (filterPaymentMethod.value) {
    result = result.filter(o => o.payment_method === filterPaymentMethod.value);
  }
  
  const effectiveDateRange = getEffectiveDateRange();
  if (effectiveDateRange && effectiveDateRange.length === 2) {
    const [start, end] = effectiveDateRange;
    result = result.filter(o => {
      const orderDate = o.order_time.slice(0, 10);
      return orderDate >= start && orderDate <= end;
    });
  }
  
  if (filterCategory.value) {
    result = result.filter(o => {
      if (!o.items || o.items.length === 0) return false;
      return o.items.some(item => {
        const product = products.value.find(p => p.product_id === item.product_id);
        return product && product.category === filterCategory.value;
      });
    });
  }
  
  return result;
});

function getEffectiveDateRange() {
  if (dateRange.value && dateRange.value.length === 2) {
    return dateRange.value;
  }
  
  const now = new Date();
  let startDate;
  
  switch (quickDateRange.value) {
    case 'today':
      startDate = now;
      break;
    case 'week':
      startDate = new Date(now);
      startDate.setDate(now.getDate() - now.getDay() + (now.getDay() === 0 ? -6 : 1));
      break;
    case 'month':
      startDate = new Date(now.getFullYear(), now.getMonth(), 1);
      break;
    case 'quarter':
      const quarter = Math.floor(now.getMonth() / 3);
      startDate = new Date(now.getFullYear(), quarter * 3, 1);
      break;
    case 'year':
      startDate = new Date(now.getFullYear(), 0, 1);
      break;
    default:
      return null;
  }
  
  const formatDate = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };
  
  return [formatDate(startDate), formatDate(now)];
}

const displayOrders = computed(() => {
  const start = (orderPage.value - 1) * orderPageSize.value;
  const end = start + orderPageSize.value;
  return filteredOrders.value.slice(start, end);
});

function getCustomerName(customerId) {
  const customer = customers.value.find(c => c.customer_id === customerId);
  return customer ? customer.name : `客户${customerId}`;
}

function getOrderStatus(row) {
  if (row.is_returned) return 'returned';
  if (row.payment_status === 1) return 'completed';
  return 'pending';
}

function getOrderStatusType(row) {
  const status = getOrderStatus(row);
  const map = {
    pending: 'warning',
    completed: 'success',
    returned: 'danger'
  };
  return map[status] || 'info';
}

function getOrderStatusText(row) {
  const status = getOrderStatus(row);
  const map = {
    pending: '待支付',
    completed: '订单已完成',
    returned: '已退货'
  };
  return map[status] || '未知';
}

function getMemberLevelType(level) {
  const map = {
    '普通会员': 'info',
    '白银会员': 'warning',
    '黄金会员': 'success'
  };
  return map[level] || 'info';
}

function availableProducts(currentProductId) {
  return products.value.filter(p => {
    if (!currentProductId) return p.status === 1 && p.current_stock > 0;
    if (p.product_id === currentProductId) return true;
    return p.status === 1 && p.current_stock > 0;
  });
}

async function loadOrders() {
  try {
    orders.value = await getOrderHistory(null);
  } catch (error) {
    ElMessage.error('加载订单失败');
  }
}

async function loadCustomers() {
  try {
    customers.value = await getCustomers();
  } catch (error) {
    ElMessage.error('加载客户列表失败');
  }
}

async function loadProducts() {
  try {
    products.value = await getProducts();
  } catch (error) {
    ElMessage.error('加载产品失败');
  }
}

const products = ref([]);

function handleOrderSearch() {
  orderPage.value = 1;
}

function handleDateChange() {
  orderPage.value = 1;
  quickDateRange.value = '';
}

function handleQuickDateChange() {
  orderPage.value = 1;
  if (quickDateRange.value !== 'custom') {
    dateRange.value = null;
  }
}

function handleFilterChange() {
  orderPage.value = 1;
}

function applyFilters() {
  orderPage.value = 1;
  ElMessage.success('筛选条件已应用');
}

function clearFilters() {
  quickDateRange.value = '';
  dateRange.value = null;
  filterStatus.value = '';
  filterCategory.value = '';
  filterPaymentMethod.value = '';
  orderSearch.value = '';
  orderPage.value = 1;
  ElMessage.success('筛选条件已重置');
}

function handleOrderSizeChange() {
  orderPage.value = 1;
}

function handleOrderPageChange() {}

async function viewOrderDetail(row) {
  try {
    orderDetail.value = await getOrderDetail(row.order_id);
    detailVisible.value = true;
  } catch (error) {
    ElMessage.error('加载订单详情失败');
  }
}

function openPrintReceipt() {
  printOrder.value = {
    ...orderDetail.value,
    customer_name: getCustomerName(orderDetail.value.customer_id)
  };
  printVisible.value = true;
}

async function handlePay() {
  if (!orderDetail.value) return;
  
  try {
    await ElMessageBox.confirm('确定要支付该订单吗？', '确认支付', { type: 'info' });
    
    paying.value = true;
    await payOrderApi(orderDetail.value.order_id);
    
    ElMessage.success('支付成功');
    detailVisible.value = false;
    await loadOrders();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '支付失败');
    }
  } finally {
    paying.value = false;
  }
}

async function handleDeleteFromDetail() {
  if (!orderDetail.value) return;
  await handleDeleteOrder(orderDetail.value);
}

function handleReturnFromDetail() {
  if (!orderDetail.value) return;
  router.push(`/dashboard/return/${orderDetail.value.order_id}`);
  detailVisible.value = false;
}

async function handlePayOrder(row) {
  try {
    await ElMessageBox.confirm(
      `确定要支付订单 ${row.order_id} 吗？`,
      '确认支付',
      { type: 'info' }
    );
    
    await payOrderApi(row.order_id);
    ElMessage.success('支付成功');
    await loadOrders();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '支付失败');
    }
  }
}

async function handleDeleteOrder(row) {
  try {
    if (!hasDeletePermission.value) {
      ElMessage.error('您没有删除订单的权限');
      return;
    }
    
    const customerName = getCustomerName(row.customer_id);
    const orderStatus = getOrderStatus(row);
    
    if (orderStatus === 'completed') {
      ElMessage.warning('已完成订单不能直接删除，请使用退货功能');
      return;
    }
    
    const orderItems = await getOrderItems(row.order_id);
    
    await ElMessageBox.confirm(
      `<div style="padding: 15px;">
        <h4 style="margin: 0 0 15px 0; color: #303133;">订单删除确认</h4>
        <div style="background: #f5f7fa; padding: 15px; border-radius: 4px; margin-bottom: 15px;">
          <p style="margin: 8px 0;"><strong>订单编号：</strong>${row.order_id}</p>
          <p style="margin: 8px 0;"><strong>客户名称：</strong>${customerName}</p>
          <p style="margin: 8px 0;"><strong>订单金额：</strong>¥${row.total_amount.toFixed(2)}</p>
          <p style="margin: 8px 0;"><strong>订单状态：</strong>${getOrderStatusText(row)}</p>
          <p style="margin: 8px 0;"><strong>订单时间：</strong>${row.order_time}</p>
        </div>
        ${orderItems.length > 0 ? `
        <div style="margin-bottom: 15px;">
          <p style="margin: 8px 0;"><strong>包含商品：</strong></p>
          <ul style="margin: 5px 0 0 20px; padding: 0;">
            ${orderItems.map(item => `<li>${item.product_name} × ${item.quantity}</li>`).join('')}
          </ul>
        </div>
        ` : ''}
        <div style="background: #fef0f0; border: 1px solid #fde2e2; padding: 12px; border-radius: 4px;">
          <p style="margin: 0; color: #f56c6c; font-weight: 500;">⚠️ 重要提示</p>
          <ul style="margin: 8px 0 0 20px; padding: 0; color: #f56c6c;">
            <li>此操作将永久删除该订单及所有关联数据</li>
            <li>删除后订单信息无法恢复</li>
            <li>库存数量将自动回滚</li>
            <li>财务统计数据将同步更新</li>
          </ul>
        </div>
      </div>`,
      '确认删除订单',
      { 
        type: 'warning',
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        confirmButtonClass: 'el-button--danger',
        dangerouslyUseHTMLString: true
      }
    );
    
    await deleteOrder(row.order_id, userStore.username || 'admin');
    
    ElMessage.success({
      message: `订单 ${row.order_id} 删除成功，数据已同步更新`,
      type: 'success',
      duration: 3000
    });
    
    detailVisible.value = false;
    await loadOrders();
    eventBus.emit('orderDeleted', { orderId: row.order_id });
  } catch (error) {
    if (error === 'cancel') {
      return;
    }
    
    if (error.message === '您没有删除订单的权限') {
      ElMessage.error('权限验证失败：您没有删除订单的权限');
    } else if (error.message === '已支付订单无法删除，请使用退货功能') {
      ElMessage.warning('已支付订单不能直接删除，请使用退货功能');
    } else if (error.message === '订单不存在') {
      ElMessage.error('订单不存在或已被删除');
    } else {
      ElMessage.error(error.message || '删除订单失败，请稍后重试');
    }
  }
}

async function getOrderItems(orderId) {
  try {
    const orderDetail = await getOrderDetail(orderId);
    if (orderDetail && orderDetail.items) {
      return orderDetail.items.map(item => ({
        ...item,
        product_name: item.product_name || `商品${item.product_id}`
      }));
    }
    return [];
  } catch {
    return [];
  }
}

function handleReturnOrder(row) {
  router.push(`/dashboard/return/${row.order_id}`);
}

function handleCustomerChange(customerId) {
  const customer = customers.value.find(c => c.customer_id === customerId);
  if (customer) {
    shippingAddress.value = customer.address || '';
    usePoints.value = false;
    pointsToUse.value = 0;
    pointsDiscount.value = 0;
  }
}

function setPoints(amount) {
  const actualAmount = Math.min(amount, maxPointsToUse.value);
  if (actualAmount < 100) {
    ElMessage.warning('积分抵扣最低需要100积分');
    return;
  }
  pointsToUse.value = actualAmount;
  calcPointsDiscount();
}

function handleProductSelect(productId, index) {
  const product = products.value.find(p => p.product_id === productId);
  if (product) {
    cartItems.value[index].product_id = productId;
    cartItems.value[index].product_name = product.product_name;
    cartItems.value[index].unit_price = product.retail_price;
    cartItems.value[index].maxStock = product.current_stock;
    cartItems.value[index].quantity = 1;
    calcSubtotal(index);
  }
}

function calcSubtotal(index) {
  const item = cartItems.value[index];
  if (item) {
    item.subtotal = (item.unit_price || 0) * (item.quantity || 0);
  }
}

function addCartItem() {
  cartItems.value.push({
    product_id: null,
    product_name: '',
    quantity: 1,
    unit_price: 0,
    maxStock: 0,
    subtotal: 0
  });
}

function handleQuickSearch() {
  const keyword = quickSearchKeyword.value.trim();
  if (!keyword) return;
  
  const product = products.value.find(p => 
    String(p.product_id) === keyword || 
    p.product_name.toLowerCase().includes(keyword.toLowerCase())
  );
  
  if (product) {
    if (product.current_stock <= 0) {
      ElMessage.warning(`商品 ${product.product_name} 库存不足`);
      return;
    }
    
    cartItems.value.push({
      product_id: product.product_id,
      product_name: product.product_name,
      quantity: 1,
      unit_price: product.retail_price,
      maxStock: product.current_stock,
      subtotal: product.retail_price
    });
    
    quickSearchKeyword.value = '';
    ElMessage.success(`已添加商品：${product.product_name}`);
  } else {
    ElMessage.warning(`未找到产品编号或名称包含 "${keyword}" 的商品`);
  }
}

function removeCartItem(index) {
  cartItems.value.splice(index, 1);
}

async function handleAddCustomer() {
  try {
    await customerFormRef.value.validate();
  } catch {
    return;
  }
  
  try {
    const customerData = { ...customerForm };
    if (customerData.membership_level === '普通会员') {
      customerData.discount_rate = 1.0;
    } else if (customerData.membership_level === '白银会员') {
      customerData.discount_rate = 0.95;
    } else if (customerData.membership_level === '黄金会员') {
      customerData.discount_rate = 0.9;
    }
    
    const newId = await addCustomerApi(customerData);
    await loadCustomers();
    selectedCustomerId.value = newId;
    handleCustomerChange(newId);
    showAddCustomer.value = false;
    
    customerForm.name = '';
    customerForm.phone = '';
    customerForm.address = '';
    customerForm.email = '';
    customerForm.membership_level = '普通会员';
    customerForm.points = 0;
    
    ElMessage.success('新增客户成功');
  } catch (error) {
    ElMessage.error('新增客户失败');
  }
}

async function submitOrder() {
  if (!selectedCustomerId.value) {
    ElMessage.warning('请选择客户');
    return;
  }
  
  const validItems = cartItems.value.filter(item => item.product_id && item.quantity > 0);
  if (validItems.length === 0) {
    ElMessage.warning('请添加至少一件商品');
    return;
  }
  
  submitting.value = true;
  
  try {
    const cartData = validItems.map(item => ({
      product_id: item.product_id,
      quantity: item.quantity
    }));
    
    const discountAmount = memberDiscountAmount.value;
    const earnedPoints = Math.floor(finalAmount.value); // 消费1元积1分
    const usedPoints = usePoints.value ? pointsToUse.value : 0;
    
    const orderId = await createOrderApi(
      selectedCustomerId.value,
      cartData,
      paymentMethod.value,
      shippingAddress.value || selectedCustomer.value?.address || '',
      discountAmount,
      earnedPoints,
      usedPoints,
      finalAmount.value
    );
    
    ElMessage.success(`订单创建成功：${orderId}`);
    
    const needPay = await ElMessageBox.confirm(
      `订单 ${orderId} 已创建，是否立即支付？`,
      '订单已创建',
      {
        confirmButtonText: '立即支付',
        cancelButtonText: '稍后支付',
        type: 'info'
      }
    ).then(() => true).catch(() => false);
    
    if (needPay) {
      try {
        await payOrderApi(orderId);
        ElMessage.success('支付成功');
      } catch (error) {
        ElMessage.error(error.message || '支付失败，请稍后手动支付');
      }
    }
    
    resetForm();
    
    await navigateToOrderDetail(orderId);
  } catch (error) {
    ElMessage.error(error.message || '创建订单失败');
  } finally {
    submitting.value = false;
  }
}

async function navigateToOrderDetail(orderId) {
  const loading = ElLoading.service({
    lock: true,
    text: '正在跳转到订单详情...',
    spinner: 'el-icon-loading',
    background: 'rgba(0, 0, 0, 0.7)'
  });
  
  try {
    await new Promise(resolve => setTimeout(resolve, 500));
    
    await router.push({
      path: '/dashboard/sales',
      query: { orderId }
    });
    
    activeTab.value = 'orderList';
    await loadOrders();
    
    const order = orders.value.find(o => o.order_id === orderId);
    if (order) {
      viewOrderDetail(order);
    }
  } catch (error) {
    console.error('跳转失败:', error);
    ElMessage.error({
      message: `跳转失败：${error.message || '网络异常'}，请手动查看订单详情`,
      duration: 5000
    });
    
    const retry = await ElMessageBox.confirm(
      '是否重新尝试跳转到订单详情？',
      '跳转失败',
      {
        confirmButtonText: '重试',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(() => true).catch(() => false);
    
    if (retry) {
      loading.close();
      await navigateToOrderDetail(orderId);
      return;
    }
    
    activeTab.value = 'orderList';
    await loadOrders();
  } finally {
    loading.close();
  }
}

function resetForm() {
  selectedCustomerId.value = null;
  cartItems.value = [];
  paymentMethod.value = '微信支付';
  shippingAddress.value = '';
  usePoints.value = false;
  pointsToUse.value = 0;
  pointsDiscount.value = 0;
}

onMounted(async () => {
  loadOrders();
  loadCustomers();
  loadProducts();
  addCartItem();
  
  const orderId = router.currentRoute.value.query.orderId;
  if (orderId) {
    setTimeout(async () => {
      await loadOrders();
      const order = orders.value.find(o => o.order_id === orderId);
      if (order) {
        viewOrderDetail(order);
      }
    }, 300);
  }
});
</script>

<style scoped>
.sales-container {
  padding: 20px;
}

.page-title {
  margin: 0 0 20px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.sales-tabs {
  background: #fff;
  padding: 16px;
  border-radius: 4px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.search-group {
  display: flex;
  align-items: center;
}

.filter-panel {
  background: #fff;
  padding: 16px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.filter-row {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.filter-row:last-child {
  margin-bottom: 0;
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

.quick-search-input {
  width: 250px;
  margin-left: auto;
}

.cart-summary {
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
  
  .return-info-section {
    margin-top: 20px;
    padding: 10px;
    background: #fef0f0;
    border-radius: 4px;
  }
  
  .member-info-card {
    margin-top: 16px;
    padding: 12px;
    background: #f0f9ff;
    border-radius: 4px;
    border: 1px solid #b3e0ff;
  }
  
  .member-discount-section {
    margin-top: 16px;
    padding: 16px;
    background: #fff7e6;
    border-radius: 4px;
  }
  
  .discount-amount {
    font-size: 20px;
    font-weight: 700;
    color: #e6a23c;
  }
  
  .member-discount-detail {
    margin-bottom: 16px;
  }
  
  .discount-text {
    color: #f56c6c;
    font-weight: 600;
  }
  
  .points-text {
    color: #e6a23c;
    font-weight: 600;
  }
  
  .summary-item {
    margin-bottom: 8px;
    font-size: 16px;
  }
  
  .summary-item.discount,
  .summary-item.points {
    color: #f56c6c;
  }
  
  .summary-item.final {
    padding-top: 12px;
    border-top: 1px solid #eee;
    font-weight: 600;
  }
  
  .final-amount {
    font-size: 28px;
    font-weight: 700;
    color: #67c23a;
    margin-left: 10px;
  }
  
  .return-info-section .el-divider__text {
    font-weight: 600;
    color: #f56c6c;
  }
  
  .btn-icon {
    margin-right: 4px;
    font-size: 14px;
  }
</style>