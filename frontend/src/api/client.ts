import axios, { AxiosError } from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const client = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor - Add JWT token to requests
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log(`📤 Request: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`, config.params || config.data || '');
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor - Handle 401 and token refresh
client.interceptors.response.use(
  (response) => {
    console.log(`📥 Response: ${response.status} ${response.config.method?.toUpperCase()} ${response.config.url}`);
    return response;
  },
  async (error: AxiosError) => {
    console.error('❌ Response Error:', {
      status: error.response?.status,
      url: error.config?.url,
      method: error.config?.method,
      message: error.message,
      data: error.response?.data
    });

    const originalRequest = error.config;

    if (error.response?.status === 401 && originalRequest && !(originalRequest as any)._retry) {
      (originalRequest as any)._retry = true;

      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          console.log('🔄 Refreshing access token...');
          const { data } = await axios.post(`${API_URL}/token/refresh/`, {
            refresh: refreshToken,
          });
          localStorage.setItem('access_token', data.access);
          console.log('✅ Token refreshed successfully');
          
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${data.access}`;
          }
          
          return client(originalRequest);
        } catch (refreshError) {
          // Refresh failed - clear tokens and redirect to login
          console.error('❌ Token refresh failed, redirecting to login');
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token - redirect to login
        console.warn('⚠️ No refresh token found, redirecting to login');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export default client;
