import client from './client';

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  date_joined: string;
}

export interface PasswordChangeRequest {
  old_password: string;
  new_password: string;
  new_password_confirm: string;
}

export interface UserPreferences {
  theme: 'light' | 'dark';
  language: 'en' | 'kin' | 'fra';
  notifications_enabled: boolean;
  email_alerts: boolean;
  sms_alerts: boolean;
}

const BASE_URL = '/api';

export const usersAPI = {
  /**
   * Get current user profile
   */
  getProfile: async (): Promise<UserProfile> => {
    try {
      const response = await client.get<UserProfile>(`${BASE_URL}/auth/user/`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
      throw error;
    }
  },

  /**
   * Update user profile
   */
  updateProfile: async (data: Partial<UserProfile>): Promise<UserProfile> => {
    try {
      const response = await client.patch<UserProfile>(`${BASE_URL}/auth/user/`, data);
      return response.data;
    } catch (error) {
      console.error('Failed to update user profile:', error);
      throw error;
    }
  },

  /**
   * Change password
   */
  changePassword: async (data: PasswordChangeRequest): Promise<{ detail: string }> => {
    try {
      const response = await client.post<{ detail: string }>(
        `${BASE_URL}/auth/change-password/`,
        data
      );
      return response.data;
    } catch (error) {
      console.error('Failed to change password:', error);
      throw error;
    }
  },

  /**
   * Get user preferences
   */
  getPreferences: async (): Promise<UserPreferences> => {
    try {
      const prefs = localStorage.getItem('user_preferences');
      if (prefs) {
        return JSON.parse(prefs);
      }
      return {
        theme: 'light',
        language: 'en',
        notifications_enabled: true,
        email_alerts: true,
        sms_alerts: true,
      };
    } catch (error) {
      console.error('Failed to fetch preferences:', error);
      throw error;
    }
  },

  /**
   * Save user preferences
   */
  savePreferences: async (preferences: UserPreferences): Promise<UserPreferences> => {
    try {
      localStorage.setItem('user_preferences', JSON.stringify(preferences));
      return preferences;
    } catch (error) {
      console.error('Failed to save preferences:', error);
      throw error;
    }
  },
};

export default usersAPI;
