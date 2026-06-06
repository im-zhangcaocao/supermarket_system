<template>
  <div class="profile-container">
    <h2 class="page-title">个人信息</h2>
    
    <el-tabs v-model="activeTab" type="card">
      <el-tab-pane label="基本信息" name="basic">
        <div class="form-container">
          <el-form :model="profileForm" label-width="120px" ref="basicForm">
            <el-form-item label="用户名" :disabled="true">
              <el-input v-model="profileForm.username" disabled />
            </el-form-item>
            <el-form-item label="真实姓名" prop="real_name">
              <el-input v-model="profileForm.real_name" placeholder="请输入真实姓名" />
            </el-form-item>
            <el-form-item label="手机号码" prop="phone">
              <el-input v-model="profileForm.phone" placeholder="请输入手机号码" />
            </el-form-item>
            <el-form-item label="电子邮箱" prop="email">
              <el-input v-model="profileForm.email" placeholder="请输入电子邮箱" />
            </el-form-item>
            <el-form-item label="居住地址" prop="address">
              <el-input v-model="profileForm.address" placeholder="请输入居住地址" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveProfile" :disabled="!isProfileDirty">保存修改</el-button>
              <el-button @click="resetForm" :disabled="!isProfileDirty">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="修改密码" name="password">
        <div class="form-container">
          <el-form :model="passwordForm" label-width="120px" ref="passwordFormRef">
            <el-form-item label="旧密码" prop="old_password">
              <el-input v-model="passwordForm.old_password" type="password" placeholder="请输入旧密码" />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="passwordForm.new_password" type="password" placeholder="请输入新密码（至少6位，包含字母和数字）" />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm_password">
              <el-input v-model="passwordForm.confirm_password" type="password" placeholder="请再次输入新密码" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="changePassword" :disabled="!isPasswordDirty">修改密码</el-button>
              <el-button @click="resetPasswordForm" :disabled="!isPasswordDirty">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { getProfile, updateProfile, changePassword as apiChangePassword } from '../api/realApi';

const activeTab = ref('basic');

const profileForm = reactive({
  username: '',
  real_name: '',
  phone: '',
  email: '',
  address: ''
});

const originalProfile = reactive({
  username: '',
  real_name: '',
  phone: '',
  email: '',
  address: ''
});

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
});

const basicForm = ref(null);
const passwordFormRef = ref(null);

const isProfileDirty = computed(() => {
  return profileForm.real_name !== originalProfile.real_name ||
         profileForm.phone !== originalProfile.phone ||
         profileForm.email !== originalProfile.email ||
         profileForm.address !== originalProfile.address;
});

const isPasswordDirty = computed(() => {
  return passwordForm.old_password !== '' ||
         passwordForm.new_password !== '' ||
         passwordForm.confirm_password !== '';
});

onMounted(() => {
  loadProfile();
});

async function loadProfile() {
  try {
    const result = await getProfile();
    if (result.success && result.data) {
      const data = result.data;
      profileForm.username = data.username || '';
      profileForm.real_name = data.real_name || '';
      profileForm.phone = data.phone || '';
      profileForm.email = data.email || '';
      profileForm.address = data.address || '';
      
      originalProfile.username = data.username || '';
      originalProfile.real_name = data.real_name || '';
      originalProfile.phone = data.phone || '';
      originalProfile.email = data.email || '';
      originalProfile.address = data.address || '';
    }
  } catch (error) {
    console.error('获取个人信息失败:', error);
    ElMessage.error('获取个人信息失败');
  }
}

function resetForm() {
  loadProfile();
}

function resetPasswordForm() {
  passwordForm.old_password = '';
  passwordForm.new_password = '';
  passwordForm.confirm_password = '';
}

async function saveProfile() {
  try {
    const data = {
      real_name: profileForm.real_name,
      phone: profileForm.phone,
      email: profileForm.email,
      address: profileForm.address
    };
    
    const result = await updateProfile(data);
    if (result.success) {
      ElMessage.success('个人信息更新成功');
      originalProfile.real_name = profileForm.real_name;
      originalProfile.phone = profileForm.phone;
      originalProfile.email = profileForm.email;
      originalProfile.address = profileForm.address;
    } else {
      ElMessage.error(result.message || '更新失败');
    }
  } catch (error) {
    console.error('更新个人信息失败:', error);
    ElMessage.error('更新个人信息失败');
  }
}

async function changePassword() {
  if (!passwordForm.old_password) {
    ElMessage.warning('请输入旧密码');
    return;
  }
  if (!passwordForm.new_password) {
    ElMessage.warning('请输入新密码');
    return;
  }
  if (!passwordForm.confirm_password) {
    ElMessage.warning('请确认新密码');
    return;
  }
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    ElMessage.warning('两次输入的密码不一致');
    return;
  }
  if (passwordForm.new_password.length < 6) {
    ElMessage.warning('密码长度至少6位');
    return;
  }
  if (!/^(?=.*[a-zA-Z])(?=.*\d)/.test(passwordForm.new_password)) {
    ElMessage.warning('密码必须包含字母和数字');
    return;
  }
  
  try {
    const result = await apiChangePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password,
      confirm_password: passwordForm.confirm_password
    });
    
    if (result.success) {
      ElMessage.success('密码修改成功');
      resetPasswordForm();
    } else {
      ElMessage.error(result.message || '密码修改失败');
    }
  } catch (error) {
    console.error('修改密码失败:', error);
    ElMessage.error('修改密码失败');
  }
}
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 20px;
}

.form-container {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}
</style>