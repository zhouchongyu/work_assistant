import axios from 'axios';

// 创建axios实例
const apiClient = axios.create({
  baseURL: '/api/v1', // 使用代理到后端API
  timeout: 30000,
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 添加认证token
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // 添加request_id
    const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    config.headers['x-request-id'] = requestId;
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    // 检查业务状态码
    const { code, message } = response.data;
    if (code !== 1000) {
      // 业务错误处理
      console.error(`业务错误 [${code}]: ${message}`);
      return Promise.reject(new Error(message || '请求失败'));
    }
    return response.data;
  },
  (error) => {
    // HTTP错误处理
    if (error.response?.status === 401) {
      // 未授权，跳转到登录页
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    } else if (error.response?.status === 403) {
      console.error('权限不足');
    } else if (error.response?.status >= 500) {
      console.error('服务器内部错误');
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;