<template>
  <div class="stats-container">
    <h2 class="page-title">统计报表</h2>
    
    <!-- 日期筛选 -->
    <div class="toolbar">
      <div class="filter-group">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          @change="loadReport"
        />
        <el-select
          v-model="groupBy"
          placeholder="分组方式"
          style="width: 120px; margin-left: 10px"
          @change="loadReport"
        >
          <el-option label="按日" value="day" />
          <el-option label="按月" value="month" />
          <el-option label="按年" value="year" />
        </el-select>
      </div>
      <div class="action-group">
        <el-button type="primary" @click="loadReport">查询</el-button>
        <el-button type="success" @click="handleExport">导出Excel</el-button>
      </div>
    </div>
    
    <!-- 汇总卡片 -->
    <el-row :gutter="20" class="summary-cards">
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="summary-card">
            <div class="summary-label">总销售额</div>
            <div class="summary-value">¥{{ totalSales.toFixed(2) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="summary-card">
            <div class="summary-label">总订单数</div>
            <div class="summary-value">{{ totalOrders }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="summary-card">
            <div class="summary-label">平均客单价</div>
            <div class="summary-value">¥{{ avgOrderValue.toFixed(2) }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 订单状态统计 -->
    <el-row :gutter="20" class="summary-cards">
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="summary-card status-card warning">
            <div class="summary-label">待支付订单</div>
            <div class="summary-value">{{ statusStats.pending }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="summary-card status-card success">
            <div class="summary-label">已完成订单</div>
            <div class="summary-value">{{ statusStats.completed }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="summary-card status-card danger">
            <div class="summary-label">已退货订单</div>
            <div class="summary-value">{{ statusStats.returned }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 销售趋势图 -->
    <el-card class="chart-card">
      <template #header>
        <span>销售趋势</span>
      </template>
      <div ref="chartRef" style="width: 100%; height: 350px;">
        <div v-if="chartData.dates.length === 0" class="empty-chart">
          暂无数据，请选择日期范围查询
        </div>
      </div>
    </el-card>
    
    <!-- 销售明细表格 -->
    <el-card class="table-card">
      <template #header>
        <span>销售明细</span>
      </template>
      <el-table :data="displayData" border stripe>
        <el-table-column :label="groupBy === 'day' ? '日期' : groupBy === 'month' ? '月份' : '年份'" prop="date" width="150" />
        <el-table-column label="订单数" prop="count" width="150" />
        <el-table-column label="销售额" width="150">
          <template #default="{ row }">
            ¥{{ row.amount.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column label="占比" width="150">
          <template #default="{ row }">
            {{ ((row.amount / totalSales) * 100).toFixed(1) }}%
          </template>
        </el-table-column>
        <el-table-column label="趋势">
          <template #default="{ row }">
            <div class="mini-bar">
              <div class="mini-bar-fill" :style="{ width: (row.amount / maxAmount * 100) + '%' }"></div>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="chartData.dates.length"
          layout="total, sizes, prev, pager, next"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { ElMessage } from 'element-plus';
import { generateSalesReport, getOrderHistory } from '../api/mockApi';
import { exportSalesReport } from '../utils/export';
import eventBus from '../utils/eventBus';

const dateRange = ref(null);
const groupBy = ref('day');
const chartData = reactive({
  dates: [],
  amounts: [],
  counts: []
});
const statusStats = reactive({
  pending: 0,
  completed: 0,
  returned: 0
});
const currentPage = ref(1);
const pageSize = ref(10);
const chartRef = ref(null);

let unsubscribeOrderDeleted = null;

const totalSales = computed(() => {
  return chartData.amounts.reduce((sum, a) => sum + a, 0);
});

const totalOrders = computed(() => {
  return chartData.counts.reduce((sum, c) => sum + c, 0);
});

const avgOrderValue = computed(() => {
  if (totalOrders.value === 0) return 0;
  return totalSales.value / totalOrders.value;
});

function getOrderStatus(order) {
  if (order.is_returned) return 'returned';
  if (order.payment_status === 1) return 'completed';
  return 'pending';
}

const maxAmount = computed(() => {
  if (chartData.amounts.length === 0) return 0;
  return Math.max(...chartData.amounts);
});

const tableData = computed(() => {
  return chartData.dates.map((date, i) => ({
    date,
    count: chartData.counts[i],
    amount: chartData.amounts[i]
  }));
});

const displayData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return tableData.value.slice(start, end);
});

async function loadReport() {
  try {
    const [start, end] = dateRange.value || [null, null];
    const result = await generateSalesReport(start, end, groupBy.value);
    
    chartData.dates = result.dates;
    chartData.amounts = result.amounts;
    chartData.counts = result.counts;
    
    await loadStatusStats();
    
    await nextTick();
    renderChart();
  } catch (error) {
    ElMessage.error('加载报表失败');
  }
}

async function loadStatusStats() {
  try {
    const orders = await getOrderHistory(null);
    
    statusStats.pending = orders.filter(o => getOrderStatus(o) === 'pending').length;
    statusStats.completed = orders.filter(o => getOrderStatus(o) === 'completed').length;
    statusStats.returned = orders.filter(o => getOrderStatus(o) === 'returned').length;
  } catch (error) {
    console.error('加载订单状态统计失败', error);
  }
}

function renderChart() {
  if (!chartRef.value || chartData.dates.length === 0) return;
  
  const container = chartRef.value;
  container.innerHTML = '';
  
  const maxVal = Math.max(...chartData.amounts);
  const barWidth = Math.max(20, Math.min(60, (container.clientWidth - 100) / chartData.dates.length - 10));
  
  let barsHtml = '';
  chartData.dates.forEach((date, i) => {
    const height = maxVal > 0 ? (chartData.amounts[i] / maxVal) * 280 : 0;
    const x = 50 + i * (barWidth + 10);
    barsHtml += `
      <g class="bar-group">
        <rect x="${x}" y="${300 - height}" width="${barWidth}" height="${height}" fill="#409eff" rx="4">
          <title>${date}: ¥${chartData.amounts[i].toFixed(2)}</title>
        </rect>
        <text x="${x + barWidth / 2}" y="320" text-anchor="middle" font-size="12" fill="#666">${date.slice(5)}</text>
        <text x="${x + barWidth / 2}" y="${295 - height}" text-anchor="middle" font-size="11" fill="#333">¥${chartData.amounts[i].toFixed(0)}</text>
      </g>
    `;
  });
  
  container.innerHTML = `
    <svg width="100%" height="350" viewBox="0 0 ${50 + chartData.dates.length * (barWidth + 10) + 20} 350">
      ${barsHtml}
    </svg>
  `;
}

function handleExport() {
  if (chartData.dates.length === 0) {
    ElMessage.warning('暂无数据可导出');
    return;
  }
  
  const filename = `销售报表_${new Date().toISOString().slice(0, 10)}`;
  const success = exportSalesReport(chartData.dates, chartData.amounts, chartData.counts, filename);
  
  if (success) {
    ElMessage.success('导出成功');
  } else {
    ElMessage.error('导出失败');
  }
}

onMounted(() => {
  loadReport();
  
  unsubscribeOrderDeleted = () => {
    loadReport();
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
.stats-container {
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
  margin-bottom: 20px;
}

.filter-group,
.action-group {
  display: flex;
  align-items: center;
}

.summary-cards {
  margin-bottom: 20px;
}

.summary-card {
  text-align: center;
  padding: 10px 0;
}

.summary-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 24px;
  font-weight: 700;
  color: #409eff;
}

.status-card.warning .summary-value {
  color: #e6a23c;
}

.status-card.success .summary-value {
  color: #67c23a;
}

.status-card.danger .summary-value {
  color: #f56c6c;
}

.status-card.info .summary-value {
  color: #909399;
}

.chart-card,
.table-card {
  margin-bottom: 20px;
}

.empty-chart {
  text-align: center;
  color: #909399;
  padding: 100px 0;
}

.mini-bar {
  width: 100%;
  height: 20px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.mini-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #409eff, #67c23a);
  border-radius: 4px;
  transition: width 0.3s;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>