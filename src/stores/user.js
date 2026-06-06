import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { login as mockLogin } from '../api/mockApi';

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || null);
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'));

  const isLoggedIn = computed(() => !!token.value);
  const role = computed(() => userInfo.value?.role || null);

  async function login(username, password) {
    const result = await mockLogin(username, password);
    if (result) {
      token.value = result.token;
      userInfo.value = result.user;
      localStorage.setItem('token', result.token);
      localStorage.setItem('userInfo', JSON.stringify(result.user));
      return true;
    }
    return false;
  }

  function logout() {
    token.value = null;
    userInfo.value = null;
    localStorage.removeItem('token');
    localStorage.removeItem('userInfo');
    window.location.href = '/login';
  }

  function restoreSession() {
    const savedToken = localStorage.getItem('token');
    const savedUserInfo = localStorage.getItem('userInfo');
    if (savedToken && savedUserInfo) {
      token.value = savedToken;
      userInfo.value = JSON.parse(savedUserInfo);
    }
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    role,
    login,
    logout,
    restoreSession
  };
});