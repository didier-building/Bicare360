import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import { useTheme } from '../contexts/ThemeContext';
import { usersAPI } from '../api/users';
import type { UserPreferences } from '../api/users';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import toast from 'react-hot-toast';

const SettingsPage: React.FC = () => {
  const { user } = useAuthStore();
  const { theme, setTheme } = useTheme();
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<'profile' | 'password' | 'preferences'>('profile');
  const [currentTheme, setCurrentTheme] = useState<'light' | 'dark'>(theme);

  // Update local theme state when context theme changes
  useEffect(() => {
    setCurrentTheme(theme);
  }, [theme]);

  // Profile state
  const [profileForm, setProfileForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
  });

  // Password state
  const [passwordForm, setPasswordForm] = useState({
    old_password: '',
    new_password: '',
    new_password_confirm: '',
  });
  const [passwordError, setPasswordError] = useState('');

  // Preferences state
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);

  // Load initial data
  useEffect(() => {
    const loadData = async () => {
      try {
        setIsLoading(true);
        // Use user data from auth store
        if (user) {
          setProfileForm({
            first_name: user.first_name || '',
            last_name: user.last_name || '',
            email: user.email || '',
          });
        }
        
        // Load preferences
        const prefsData = await usersAPI.getPreferences();
        setPreferences(prefsData);
      } catch (error) {
        console.error('Failed to load settings:', error);
        toast.error('Failed to load preferences');
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [user]);

  // Handle profile update
  const handleProfileSave = async () => {
    setIsSaving(true);
    try {
      await usersAPI.updateProfile({
        first_name: profileForm.first_name,
        last_name: profileForm.last_name,
        email: profileForm.email,
      });
      toast.success('Profile updated successfully');
    } catch (error: unknown) {
      console.error('Failed to update profile:', error);
      let errorMessage = 'Failed to update profile';
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as Record<string, unknown>;
        const data = (axiosError.response as Record<string, unknown>)?.data as Record<string, unknown>;
        errorMessage = (data?.error as string) || errorMessage;
      }
      toast.error(errorMessage);
    } finally {
      setIsSaving(false);
    }
  };

  // Handle password change
  const handlePasswordChange = async () => {
    setPasswordError('');

    if (!passwordForm.old_password || !passwordForm.new_password || !passwordForm.new_password_confirm) {
      setPasswordError('All fields are required');
      return;
    }

    if (passwordForm.new_password !== passwordForm.new_password_confirm) {
      setPasswordError('New passwords do not match');
      return;
    }

    if (passwordForm.new_password.length < 8) {
      setPasswordError('New password must be at least 8 characters long');
      return;
    }

    setIsSaving(true);
    try {
      await usersAPI.changePassword({
        old_password: passwordForm.old_password,
        new_password: passwordForm.new_password,
        new_password_confirm: passwordForm.new_password_confirm,
      });
      setPasswordForm({
        old_password: '',
        new_password: '',
        new_password_confirm: '',
      });
      toast.success('Password changed successfully');
    } catch (error: unknown) {
      console.error('Failed to change password:', error);
      let errorMessage = 'Failed to change password';
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as Record<string, unknown>;
        const data = (axiosError.response as Record<string, unknown>)?.data as Record<string, unknown>;
        errorMessage = (data?.error as string) || errorMessage;
      }
      setPasswordError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsSaving(false);
    }
  };

  // Handle preferences update
  const handlePreferenceChange = async (key: keyof UserPreferences, value: string | boolean) => {
    console.log('handlePreferenceChange called:', { key, value });
    if (!preferences) {
      console.log('No preferences loaded, skipping');
      return;
    }

    const updated = { ...preferences, [key]: value };
    setPreferences(updated);

    // Update theme if theme preference changed
    if (key === 'theme') {
      console.log('Theme changed, calling setTheme with:', value);
      const newTheme = value as 'light' | 'dark';
      setTheme(newTheme);
      setCurrentTheme(newTheme);
      console.log('setTheme called, new theme:', newTheme);
    }

    try {
      await usersAPI.savePreferences(updated);
      toast.success('Preferences saved');
    } catch (error) {
      console.error('Failed to save preferences:', error);
      toast.error('Failed to save preferences');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Settings</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">Manage your account and preferences</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <div className="flex gap-8">
          <button
            onClick={() => setActiveTab('profile')}
            className={`pb-4 px-1 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'profile'
                ? 'text-teal-600 border-teal-600'
                : 'text-gray-600 dark:text-gray-400 border-transparent hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            Profile
          </button>
          <button
            onClick={() => setActiveTab('password')}
            className={`pb-4 px-1 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'password'
                ? 'text-teal-600 border-teal-600'
                : 'text-gray-600 dark:text-gray-400 border-transparent hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            Change Password
          </button>
          <button
            onClick={() => setActiveTab('preferences')}
            className={`pb-4 px-1 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'preferences'
                ? 'text-teal-600 border-teal-600'
                : 'text-gray-600 dark:text-gray-400 border-transparent hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            Preferences
          </button>
        </div>
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6 max-w-2xl">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-6">Profile Settings</h2>
          
          <div className="space-y-4">
            {/* Username (read-only) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Username</label>
              <input
                type="text"
                value={user?.username || ''}
                disabled
                className="w-full px-4 py-2 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-600 dark:text-gray-400 cursor-not-allowed"
              />
            </div>

            {/* First Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">First Name</label>
              <input
                type="text"
                value={profileForm.first_name}
                onChange={(e) =>
                  setProfileForm({ ...profileForm, first_name: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            {/* Last Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Last Name</label>
              <input
                type="text"
                value={profileForm.last_name}
                onChange={(e) =>
                  setProfileForm({ ...profileForm, last_name: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
              <input
                type="email"
                value={profileForm.email}
                onChange={(e) =>
                  setProfileForm({ ...profileForm, email: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            {/* Account Status */}
            <div className="pt-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Account Status:{' '}
                <span className="font-semibold text-green-600 dark:text-green-400">
                  Active
                </span>
              </p>
              {user?.date_joined && (
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                  Created On:{' '}
                  <span className="font-semibold dark:text-gray-300">
                    {new Date(user.date_joined).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                </p>
              )}
            </div>

            {/* Save Button */}
            <div className="flex gap-3 pt-4">
              <button
                onClick={handleProfileSave}
                disabled={isSaving}
                className="px-6 py-2 bg-teal-500 text-white rounded-lg font-medium hover:bg-teal-600 disabled:opacity-50 shadow-md hover:shadow-lg"
              >
                {isSaving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Password Tab */}
      {activeTab === 'password' && (
        <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6 max-w-2xl">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-6">Change Password</h2>

          {passwordError && (
            <div className="mb-4 p-3 bg-red-100 dark:bg-red-900 border border-red-300 dark:border-red-700 rounded-lg text-red-700 dark:text-red-200 text-sm">
              {passwordError}
            </div>
          )}

          <div className="space-y-4">
            {/* Current Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Current Password
              </label>
              <input
                type="password"
                value={passwordForm.old_password}
                onChange={(e) =>
                  setPasswordForm({ ...passwordForm, old_password: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            {/* New Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                New Password
              </label>
              <input
                type="password"
                value={passwordForm.new_password}
                onChange={(e) =>
                  setPasswordForm({ ...passwordForm, new_password: e.target.value })
                }
                placeholder="At least 8 characters"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            {/* Confirm New Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Confirm New Password
              </label>
              <input
                type="password"
                value={passwordForm.new_password_confirm}
                onChange={(e) =>
                  setPasswordForm({
                    ...passwordForm,
                    new_password_confirm: e.target.value,
                  })
                }
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            {/* Change Button */}
            <div className="flex gap-3 pt-4">
              <button
                onClick={handlePasswordChange}
                disabled={isSaving}
                className="px-6 py-2 bg-teal-500 text-white rounded-lg font-medium hover:bg-teal-600 disabled:opacity-50 shadow-md hover:shadow-lg"
              >
                {isSaving ? 'Changing...' : 'Change Password'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Preferences Tab */}
      {activeTab === 'preferences' && preferences && (
        <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6 max-w-2xl">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-6">Preferences</h2>

          <div className="space-y-6">
            {/* Theme */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Theme</label>
              <div className="flex gap-4">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="radio"
                    name="theme"
                    value="light"
                    checked={currentTheme === 'light'}
                    onChange={(e) => {
                      console.log('Light mode radio clicked, value:', e.target.value);
                      handlePreferenceChange('theme', e.target.value);
                    }}
                    className="text-teal-500 focus:ring-teal-500"
                  />
                  <span className="text-gray-700 dark:text-gray-300">Light Mode</span>
                </label>
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="radio"
                    name="theme"
                    value="dark"
                    checked={currentTheme === 'dark'}
                    onChange={(e) => {
                      console.log('Dark mode radio clicked, value:', e.target.value);
                      handlePreferenceChange('theme', e.target.value);
                    }}
                    className="text-teal-500 focus:ring-teal-500"
                  />
                  <span className="text-gray-700 dark:text-gray-300">Dark Mode</span>
                </label>
              </div>
            </div>

            {/* Language */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Language</label>
              <select
                value={preferences.language}
                onChange={(e) =>
                  handlePreferenceChange(
                    'language',
                    e.target.value as 'en' | 'kin' | 'fra'
                  )
                }
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="en">English</option>
                <option value="kin">Kinyarwanda</option>
                <option value="fra">French</option>
              </select>
            </div>

            {/* Notifications */}
            <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
              <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-4">Notifications</h3>

              <div className="space-y-4">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={preferences.notifications_enabled}
                    onChange={(e) =>
                      handlePreferenceChange('notifications_enabled', e.target.checked)
                    }
                    className="rounded text-teal-500 focus:ring-teal-500"
                  />
                  <span className="text-gray-700 dark:text-gray-300">Enable all notifications</span>
                </label>

                <label className="flex items-center gap-3 cursor-pointer ml-6">
                  <input
                    type="checkbox"
                    checked={preferences.email_alerts}
                    onChange={(e) =>
                      handlePreferenceChange('email_alerts', e.target.checked)
                    }
                    disabled={!preferences.notifications_enabled}
                    className="rounded text-teal-500 focus:ring-teal-500 disabled:opacity-50"
                  />
                  <span className="text-gray-700 dark:text-gray-300">Email alerts</span>
                </label>

                <label className="flex items-center gap-3 cursor-pointer ml-6">
                  <input
                    type="checkbox"
                    checked={preferences.sms_alerts}
                    onChange={(e) =>
                      handlePreferenceChange('sms_alerts', e.target.checked)
                    }
                    disabled={!preferences.notifications_enabled}
                    className="rounded text-teal-500 focus:ring-teal-500 disabled:opacity-50"
                  />
                  <span className="text-gray-700 dark:text-gray-300">SMS alerts</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SettingsPage;
