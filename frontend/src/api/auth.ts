import client from './client';
import { jwtDecode } from 'jwt-decode';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  date_joined?: string;
  role?: string;
}

interface JWTPayload {
  user_id: number;
  username: string;
  email?: string;
  exp: number;
}

export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<AuthTokens> => {
    const response = await client.post<AuthTokens>('/token/', credentials);
    return response.data;
  },

  refresh: async (refreshToken: string): Promise<{ access: string }> => {
    const response = await client.post<{ access: string }>('/token/refresh/', {
      refresh: refreshToken,
    });
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    try {
      // Try to fetch from the backend user profile endpoint
      const response = await client.get<User>('/v1/users/profile/');
      return response.data;
    } catch (error) {
      // Fallback to JWT token parsing if endpoint fails
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No access token found');
      }

      try {
        const decoded = jwtDecode<JWTPayload>(token);
        // Extract what we can from the JWT token
        return {
          id: decoded.user_id,
          username: decoded.username,
          email: decoded.email || '',
          first_name: '',
          last_name: '',
          role: 'Nurse', // Default for now
        };
      } catch (decodeError) {
        throw new Error('Invalid token');
      }
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};
