import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { login as realLogin } from '../api/realApi';

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || null);
  const userInfo = ref(JSON.parse(localStorage.getItem('user') || 'null'));

  const isLoggedIn = computed(() => !!token.value);
  const role = computed(() => userInfo.value?.role || null);

  async function login(username, password) {
    const result = await realLogin(username, password);
    if (result) {
      token.value = result.token;
      userInfo.value = result.user;
      localStorage.setItem('token', result.token);
      localStorage.setItem('user', JSON.stringify(result.user));
      return true;
    }
    return false;
  }

  function logout() {
    token.value = null;
    userInfo.value = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  }

  function restoreSession() {
    const savedToken = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    if (savedToken && savedUser) {
      token.value = savedToken;
      userInfo.value = JSON.parse(savedUser);
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