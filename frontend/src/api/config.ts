const PROD_API_FALLBACK = 'https://bicare360.onrender.com/api';
const PROD_WS_FALLBACK = 'wss://bicare360.onrender.com';

export const API_URL = import.meta.env.VITE_API_URL
  || (import.meta.env.PROD ? PROD_API_FALLBACK : 'http://localhost:8000/api');

export const WS_URL = import.meta.env.VITE_WS_URL
  || (import.meta.env.PROD ? PROD_WS_FALLBACK : 'ws://localhost:8000');
