import axios from 'axios';
import router from '../router';

const client = axios.create({
  baseURL: 'http://localhost:5001/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

client.interceptors.response.use(
  (response) => {
    if (response.data && response.data.data) {
      return response.data.data;
    }
    return response.data;
  },
  (error) => {
    if (error.response) {
      const { status } = error.response;
      
      if (status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        router.push('/login');
        console.error('未授权，已跳转到登录页');
      } else if (status === 403) {
        console.error('权限不足');
      } else if (status >= 500) {
        console.error('服务器内部错误');
      }
    } else if (error.request) {
      console.error('网络请求失败，请检查网络连接');
    } else {
      console.error('请求配置错误:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export default client;