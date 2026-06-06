<template>
  <div class="layout-container">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2 class="sidebar-title">家电超市</h2>
      </div>
      
      <el-menu
        router
        :default-active="$route.path"
        class="sidebar-menu"
        mode="vertical"
      >
        <el-menu-item index="/dashboard/inventory">
          <span>库存管理</span>
        </el-menu-item>
        
        <el-menu-item index="/dashboard/sales" v-if="canAccessSales">
          <span>销售管理</span>
        </el-menu-item>
        
        <el-menu-item index="/dashboard/purchase" v-if="canAccessPurchase">
          <span>采购管理</span>
        </el-menu-item>
        
        <el-menu-item index="/dashboard/users" v-if="canAccessUsers">
          <span>客户管理</span>
        </el-menu-item>
        
        <el-menu-item index="/dashboard/employees" v-if="canAccessEmployees">
          <span>员工管理</span>
        </el-menu-item>
        
        <el-menu-item index="/dashboard/finance" v-if="canAccessFinance">
          <span>财务管理</span>
        </el-menu-item>
        
        <el-menu-item index="/dashboard/stats" v-if="canAccessStats">
          <span>统计报表</span>
        </el-menu-item>
        
        <el-menu-item index="/dashboard/database" v-if="canAccessDatabase">
          <span>数据管理</span>
        </el-menu-item>
      </el-menu>
    </aside>
    
    <main class="main-content">
      <header class="top-header">
        <div class="header-left">
          <h1 class="page-title">{{ pageTitle }}</h1>
        </div>
        
        <div class="header-right">
          <div class="user-info">
            <span class="user-name">{{ userStore.userInfo?.username }}</span>
            <span class="user-role">({{ roleText }})</span>
          </div>
          <router-link to="/dashboard/profile" class="profile-link">
            <el-button type="text" class="profile-btn">
              个人信息
            </el-button>
          </router-link>
          <el-button
            type="text"
            class="logout-btn"
            @click="handleLogout"
          >
            登出
          </el-button>
        </div>
      </header>
      
      <div class="page-content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '../stores/user';
import { ElMessage } from 'element-plus';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const pageTitle = computed(() => {
  const titles = {
    '/inventory': '库存管理',
    '/sales': '销售管理',
    '/purchase': '采购管理',
    '/users': '客户管理',
    '/suppliers': '供应商管理',
    '/employees': '员工管理',
    '/finance': '财务管理',
    '/stats': '统计报表',
    '/database': '数据管理'
  };
  return titles[route.path] || '家电超市';
});

const roleText = computed(() => {
  const roles = {
    cashier: '收银员',
    purchaser: '采购员',
    admin: '管理员'
  };
  return roles[userStore.role] || '';
});

const canAccessSales = computed(() => {
  return ['cashier', 'admin'].includes(userStore.role);
});

const canAccessPurchase = computed(() => {
  return ['purchaser', 'admin'].includes(userStore.role);
});

const canAccessUsers = computed(() => {
  return userStore.role === 'admin';
});

const canAccessEmployees = computed(() => {
  return userStore.role === 'admin';
});

const canAccessFinance = computed(() => {
  return userStore.role === 'admin';
});

const canAccessStats = computed(() => {
  return userStore.role === 'admin';
});

const canAccessDatabase = computed(() => {
  return userStore.role === 'admin';
});

async function handleLogout() {
  await userStore.logout();
  ElMessage.success('登出成功');
  router.push('/login');
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    router.push('/login');
  }
});

watch(
  () => route.path,
  () => {
    if (!userStore.isLoggedIn && route.path !== '/login') {
      router.push('/login');
    }
  }
);
</script>

<style scoped>
.layout-container {
  display: flex;
  height: 100vh;
  background: #f5f7fa;
}

.sidebar {
  width: 200px;
  background: #2f4050;
  color: #fff;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px;
  background: #1f2d3d;
  text-align: center;
}

.sidebar-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
}

.sidebar-menu :deep(.el-menu-item) {
  color: #a7b1c2;
  height: 48px;
  line-height: 48px;
  margin: 0 10px;
  border-radius: 4px;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: #1f2d3d;
  color: #fff;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: #19aa8d;
  color: #fff;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.top-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  background: #fff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
}

.page-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.user-name {
  font-weight: 600;
  color: #303133;
}

.user-role {
  color: #909399;
}

.logout-btn {
  color: #67c23a;
  padding: 8px 16px;
}

.logout-btn:hover {
  color: #85ce61;
}

.page-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
</style>