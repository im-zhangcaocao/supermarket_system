<template>
  <div class="login-container">
    <el-card class="login-card" style="width: 400px;">
      <div class="login-header">
        <h2>家电超市管理系统</h2>
        <p>欢迎登录</p>
      </div>
      
      <el-form :model="form" class="login-form">
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="form.username" 
            placeholder="请输入用户名" 
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="请输入密码" 
            prefix-icon="Lock"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            class="login-btn" 
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../stores/user';
import { ElMessage } from 'element-plus';

const router = useRouter();
const userStore = useUserStore();

const loading = ref(false);
const form = reactive({
  username: '',
  password: ''
});

async function handleLogin() {
  if (!form.username || !form.password) {
    ElMessage.error('请输入用户名和密码');
    return;
  }
  
  loading.value = true;
  
  try {
    const success = await userStore.login(form.username, form.password);
    if (success) {
      ElMessage.success('登录成功');
      const role = userStore.role;
      let redirectPath = '/dashboard/inventory';
      
      if (role === 'cashier') {
        redirectPath = '/dashboard/sales';
      } else if (role === 'purchaser') {
        redirectPath = '/dashboard/purchase';
      } else if (role === 'admin') {
        redirectPath = '/dashboard/inventory';
      }
      
      router.push(redirectPath);
    } else {
      ElMessage.error('用户名或密码错误');
    }
  } catch (error) {
    ElMessage.error('登录失败，请重试');
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.login-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.login-form {
  padding: 0 20px;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
}
</style>