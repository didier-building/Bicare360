import { create } from 'zustand';
import { authAPI } from '../api/auth';

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  date_joined?: string;
  role?: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (username: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const tokens = await authAPI.login({ username, password });
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);

      const user = await authAPI.getCurrentUser();
      // Store user role in localStorage for routing utilities
      if (user.role) {
        localStorage.setItem('user_role', user.role);
      }
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error: any) {
      console.error('Login error:', error.response?.data);
      let errorMessage = 'Login failed. Please try again.';
      
      if (error.response?.data) {
        // Handle different error formats from Django
        if (error.response.data.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.response.data.non_field_errors) {
          errorMessage = error.response.data.non_field_errors[0];
        } else if (error.response.data.message) {
          errorMessage = error.response.data.message;
        } else if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  logout: () => {
    authAPI.logout();
    // Clear all localStorage except theme
    const theme = localStorage.getItem('theme');
    localStorage.clear();
    if (theme) localStorage.setItem('theme', theme);
    sessionStorage.clear();
    set({ user: null, isAuthenticated: false });
  },

  checkAuth: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      set({ isAuthenticated: false, user: null });
      return;
    }

    try {
      const user = await authAPI.getCurrentUser();
      // Store user role in localStorage for routing utilities
      if (user.role) {
        localStorage.setItem('user_role', user.role);
      }
      set({ user, isAuthenticated: true });
    } catch (error) {
      set({ isAuthenticated: false, user: null });
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_role');
    }
  },

  clearError: () => set({ error: null }),
}));
