<template>
  <el-dialog
    v-model="visible"
    title="收据打印预览"
    width="400px"
    :close-on-click-modal="false"
  >
    <div class="receipt" ref="receiptRef">
      <div class="receipt-header">
        <h2>家电超市管理系统</h2>
        <p>地址：成都高新区天府大道100号</p>
        <p>电话：028-12345678</p>
      </div>
      
      <div class="receipt-info">
        <p><span>收据编号：</span>{{ order?.order_id }}</p>
        <p><span>交易时间：</span>{{ order?.order_time }}</p>
        <p><span>收银员：</span>{{ cashier }}</p>
        <p><span>客户：</span>{{ customerName }}</p>
      </div>
      
      <table class="receipt-table">
        <thead>
          <tr>
            <th>商品名称</th>
            <th>数量</th>
            <th>单价</th>
            <th>小计</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in order?.items" :key="item.item_id">
            <td>{{ item.product_name }}</td>
            <td>{{ item.quantity }}</td>
            <td>¥{{ item.unit_price?.toFixed(2) }}</td>
            <td>¥{{ (item.quantity * item.unit_price)?.toFixed(2) }}</td>
          </tr>
        </tbody>
      </table>
      
      <div class="receipt-discount" v-if="hasPointsDiscount">
        <div class="discount-header">
          <span class="discount-icon">🎁</span>
          <span class="discount-title">积分抵扣</span>
        </div>
        <div class="discount-content">
          <div class="discount-row">
            <span>使用积分：</span>
            <span class="points-value">{{ order?.points_used }} 积分</span>
          </div>
          <div class="discount-row">
            <span>抵扣金额：</span>
            <span class="discount-amount">-¥{{ pointsDiscountAmount.toFixed(2) }}</span>
          </div>
          <div class="discount-row">
            <span>抵扣比例：</span>
            <span>100积分 = 1元</span>
          </div>
          <div class="discount-rule">
            <span>★ 消费1元获得1积分</span>
          </div>
        </div>
      </div>
      
      <div class="receipt-total">
        <div class="total-row">
          <span>商品总价：</span>
          <span>¥{{ order?.total_amount?.toFixed(2) }}</span>
        </div>
        <div class="total-row" v-if="order?.discount_amount > 0">
          <span>会员折扣：</span>
          <span class="discount-text">-¥{{ order?.discount_amount?.toFixed(2) }}</span>
        </div>
        <div class="total-row points-discount" v-if="hasPointsDiscount">
          <span>积分抵扣：</span>
          <span class="points-text">-¥{{ pointsDiscountAmount.toFixed(2) }}</span>
        </div>
        <div class="total-row final">
          <span>实际支付：</span>
          <span class="final-amount">¥{{ finalAmount.toFixed(2) }}</span>
        </div>
        <div class="total-row" v-if="order?.points_earned > 0">
          <span>获得积分：</span>
          <span class="earned-points">+{{ order?.points_earned }} 积分</span>
        </div>
        <div class="total-row">
          <span>支付方式：</span>
          <span>{{ order?.payment_method }}</span>
        </div>
        <div class="total-row">
          <span>收货地址：</span>
          <span>{{ order?.shipping_address }}</span>
        </div>
      </div>
      
      <div class="receipt-footer">
        <p>------------------------</p>
        <p>感谢您的惠顾！</p>
        <p>欢迎下次光临！</p>
      </div>
    </div>
    
    <template #footer>
      <el-button @click="handlePrint">打印收据</el-button>
      <el-button type="primary" @click="handleReprint">补打收据</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useUserStore } from '../stores/user';

const props = defineProps({
  modelValue: Boolean,
  order: Object
});

const emit = defineEmits(['update:modelValue', 'reprint']);

const userStore = useUserStore();
const receiptRef = ref(null);

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
});

const cashier = computed(() => userStore.userInfo?.username || '未知');

const customerName = computed(() => {
  if (!props.order) return '';
  return props.order.customer_name || `客户${props.order.customer_id}`;
});

const hasPointsDiscount = computed(() => {
  return props.order && props.order.points_used > 0;
});

const pointsDiscountAmount = computed(() => {
  if (!props.order) return 0;
  return props.order.points_discount || (props.order.points_used / 100);
});

const finalAmount = computed(() => {
  if (!props.order) return 0;
  return props.order.final_amount || props.order.total_amount;
});

function handlePrint() {
  try {
    const printContent = receiptRef.value.innerHTML;
    const printWindow = window.open('', '_blank', 'width=400,height=600');
    printWindow.document.write(`
      <html>
        <head>
          <title>收据打印</title>
          <style>
            body { font-family: 'SimSun', monospace; padding: 20px; margin: 0; }
            .receipt { width: 280px; margin: 0 auto; }
            .receipt-header { text-align: center; margin-bottom: 15px; border-bottom: 1px dashed #000; padding-bottom: 10px; }
            .receipt-header h2 { margin: 0 0 5px 0; font-size: 18px; }
            .receipt-header p { margin: 2px 0; font-size: 12px; color: #666; }
            .receipt-info { margin-bottom: 15px; font-size: 13px; }
            .receipt-info p { margin: 3px 0; display: flex; justify-content: space-between; }
            .receipt-info span { font-weight: bold; }
            .receipt-table { width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 15px; }
            .receipt-table th, .receipt-table td { border-bottom: 1px dashed #000; padding: 5px 3px; text-align: left; }
            .receipt-table th { border-bottom: 1px solid #000; font-weight: bold; }
            .receipt-table td:nth-child(2),
            .receipt-table td:nth-child(3),
            .receipt-table td:nth-child(4) { text-align: right; }
            .receipt-discount { background: #fff7e6; border: 2px dashed #e6a23c; border-radius: 8px; padding: 10px; margin-bottom: 15px; }
            .discount-header { display: flex; align-items: center; justify-content: center; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px dashed #e6a23c; }
            .discount-icon { font-size: 18px; margin-right: 8px; }
            .discount-title { font-size: 16px; font-weight: bold; color: #d48806; }
            .discount-content { font-size: 13px; }
            .discount-row { display: flex; justify-content: space-between; margin: 4px 0; }
            .points-value { font-weight: bold; color: #e6a23c; font-size: 14px; }
            .discount-amount { font-weight: bold; color: #f56c6c; font-size: 14px; }
            .discount-rule { margin-top: 8px; padding-top: 8px; border-top: 1px dashed #e6a23c; text-align: center; font-size: 12px; color: #d48806; }
            .receipt-total { margin-bottom: 15px; font-size: 14px; border-top: 1px dashed #000; padding-top: 10px; }
            .total-row { display: flex; justify-content: space-between; margin: 5px 0; }
            .total-row.final { margin-top: 10px; padding-top: 10px; border-top: 1px solid #000; }
            .discount-text { color: #f56c6c; }
            .points-discount { background: #fff7e6; padding: 4px 8px; border-radius: 4px; margin: 6px 0; }
            .points-text { color: #e6a23c; font-weight: bold; }
            .final-amount { font-weight: bold; font-size: 22px; color: #67c23a; }
            .earned-points { color: #409eff; font-weight: bold; }
            .receipt-footer { text-align: center; font-size: 12px; color: #666; }
          </style>
        </head>
        <body>
          ${printContent}
          <script>window.onload = function() { window.print(); window.close(); }<\/script>
        </body>
      </html>
    `);
    printWindow.document.close();
  } catch (error) {
    console.error('打印失败', error);
    alert('打印功能暂不可用，请稍后补打');
  }
}

function handleReprint() {
  emit('reprint', props.order);
  handlePrint();
}
</script>

<style scoped>
.receipt {
  background: #fff;
  padding: 10px;
  font-family: 'SimSun', '宋体', serif;
  font-size: 14px;
}

.receipt-header {
  text-align: center;
  margin-bottom: 15px;
  border-bottom: 1px dashed #333;
  padding-bottom: 10px;
}

.receipt-header h2 {
  margin: 0 0 5px 0;
  font-size: 18px;
}

.receipt-header p {
  margin: 2px 0;
  font-size: 12px;
  color: #666;
}

.receipt-info {
  margin-bottom: 15px;
  font-size: 13px;
}

.receipt-info p {
  margin: 3px 0;
  display: flex;
  justify-content: space-between;
}

.receipt-info span {
  font-weight: bold;
}

.receipt-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  margin-bottom: 15px;
}

.receipt-table th,
.receipt-table td {
  border-bottom: 1px dashed #999;
  padding: 5px 3px;
  text-align: left;
}

.receipt-table th {
  border-bottom: 1px solid #333;
  font-weight: bold;
}

.receipt-table td:nth-child(2),
.receipt-table td:nth-child(3),
.receipt-table td:nth-child(4) {
  text-align: right;
}

.receipt-discount {
  background: linear-gradient(135deg, #fff7e6 0%, #fff3cd 100%);
  border: 2px dashed #e6a23c;
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 15px;
}

.discount-header {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px dashed #e6a23c;
}

.discount-icon {
  font-size: 18px;
  margin-right: 8px;
}

.discount-title {
  font-size: 16px;
  font-weight: bold;
  color: #d48806;
}

.discount-content {
  font-size: 13px;
}

.discount-row {
  display: flex;
  justify-content: space-between;
  margin: 4px 0;
}

.points-value {
  font-weight: bold;
  color: #e6a23c;
  font-size: 14px;
}

.discount-amount {
  font-weight: bold;
  color: #f56c6c;
  font-size: 14px;
}

.discount-rule {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #e6a23c;
  text-align: center;
  font-size: 12px;
  color: #d48806;
}

.receipt-total {
  margin-bottom: 15px;
  font-size: 14px;
  border-top: 1px dashed #333;
  padding-top: 10px;
}

.total-row {
  display: flex;
  justify-content: space-between;
  margin: 5px 0;
}

.total-row.final {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #333;
}

.discount-text {
  color: #f56c6c;
}

.points-discount {
  background: #fff7e6;
  padding: 4px 8px;
  border-radius: 4px;
  margin: 6px 0;
}

.points-text {
  color: #e6a23c;
  font-weight: bold;
}

.final-amount {
  font-weight: bold;
  font-size: 22px;
  color: #67c23a;
}

.earned-points {
  color: #409eff;
  font-weight: bold;
}

.receipt-footer {
  text-align: center;
  font-size: 12px;
  color: #666;
}
</style>