import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../api/client';

export default function PatientSettingsPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'account' | 'password' | 'notifications'>('account');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Password change state
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [passwordLoading, setPasswordLoading] = useState(false);

  // Notification preferences state
  const [notifications, setNotifications] = useState({
    email_alerts: true,
    sms_alerts: false,
    medication_reminders: true,
    appointment_reminders: true,
    health_updates: true,
  });

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (passwordData.new_password !== passwordData.confirm_password) {
      setError('New passwords do not match');
      return;
    }

    if (passwordData.new_password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    try {
      setPasswordLoading(true);
      await client.post('/v1/patients/change-password/', {
        current_password: passwordData.current_password,
        new_password: passwordData.new_password,
      });
      setSuccess('Password changed successfully!');
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to change password');
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleNotificationChange = (key: keyof typeof notifications) => {
    setNotifications((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
    setSuccess('Notification preferences updated!');
    setTimeout(() => setSuccess(''), 3000);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={() => {
              const role = localStorage.getItem('user_role');
              const dashboardRoute = role?.toLowerCase() === 'patient' ? '/patient/dashboard' : '/dashboard';
              navigate(dashboardRoute);
            }}
            className="flex items-center gap-2 text-teal-600 dark:text-teal-400 hover:text-teal-700"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Dashboard
          </button>
        </div>

        {/* Alerts */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-700 dark:text-red-200">{error}</p>
          </div>
        )}
        {success && (
          <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-lg">
            <p className="text-green-700 dark:text-green-200">{success}</p>
          </div>
        )}

        {/* Settings Container */}
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg overflow-hidden">
          {/* Tabs */}
          <div className="flex border-b border-gray-200 dark:border-slate-700">
            <button
              onClick={() => setActiveTab('account')}
              className={`flex-1 px-6 py-4 font-medium text-center transition-colors ${
                activeTab === 'account'
                  ? 'border-b-2 border-teal-600 text-teal-600 dark:text-teal-400'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-300'
              }`}
            >
              Account Settings
            </button>
            <button
              onClick={() => setActiveTab('password')}
              className={`flex-1 px-6 py-4 font-medium text-center transition-colors ${
                activeTab === 'password'
                  ? 'border-b-2 border-teal-600 text-teal-600 dark:text-teal-400'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-300'
              }`}
            >
              Change Password
            </button>
            <button
              onClick={() => setActiveTab('notifications')}
              className={`flex-1 px-6 py-4 font-medium text-center transition-colors ${
                activeTab === 'notifications'
                  ? 'border-b-2 border-teal-600 text-teal-600 dark:text-teal-400'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-300'
              }`}
            >
              Notifications
            </button>
          </div>

          {/* Tab Content */}
          <div className="p-8">
            {/* Account Settings Tab */}
            {activeTab === 'account' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Account Settings</h2>
                <div className="bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <p className="text-blue-700 dark:text-blue-200">
                    To edit your profile information like name, email, and contact details, please visit your Profile page.
                  </p>
                </div>
                <button
                  onClick={() => navigate('/patient/profile')}
                  className="px-6 py-3 bg-teal-600 hover:bg-teal-700 text-white rounded-lg font-medium transition-colors"
                >
                  Go to Profile
                </button>
              </div>
            )}

            {/* Change Password Tab */}
            {activeTab === 'password' && (
              <div className="space-y-6 max-w-md">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Change Password</h2>
                <form onSubmit={handlePasswordChange} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Current Password
                    </label>
                    <input
                      type="password"
                      value={passwordData.current_password}
                      onChange={(e) =>
                        setPasswordData({ ...passwordData, current_password: e.target.value })
                      }
                      className="w-full px-4 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      New Password
                    </label>
                    <input
                      type="password"
                      value={passwordData.new_password}
                      onChange={(e) =>
                        setPasswordData({ ...passwordData, new_password: e.target.value })
                      }
                      className="w-full px-4 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
                      required
                    />
                    <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                      Must be at least 8 characters long
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Confirm New Password
                    </label>
                    <input
                      type="password"
                      value={passwordData.confirm_password}
                      onChange={(e) =>
                        setPasswordData({ ...passwordData, confirm_password: e.target.value })
                      }
                      className="w-full px-4 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
                      required
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={passwordLoading}
                    className="w-full px-6 py-3 bg-teal-600 hover:bg-teal-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {passwordLoading ? 'Updating...' : 'Update Password'}
                  </button>
                </form>
              </div>
            )}

            {/* Notifications Tab */}
            {activeTab === 'notifications' && (
              <div className="space-y-6 max-w-md">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Notification Preferences</h2>

                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 border border-gray-200 dark:border-slate-700 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">Email Alerts</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Receive alerts via email</p>
                    </div>
                    <button
                      onClick={() => handleNotificationChange('email_alerts')}
                      className={`relative w-14 h-8 rounded-full transition-colors ${
                        notifications.email_alerts ? 'bg-teal-600' : 'bg-gray-300'
                      }`}
                    >
                      <div
                        className={`absolute top-1 w-6 h-6 bg-white rounded-full transition-transform ${
                          notifications.email_alerts ? 'translate-x-7' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>

                  <div className="flex items-center justify-between p-4 border border-gray-200 dark:border-slate-700 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">SMS Alerts</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Receive alerts via SMS</p>
                    </div>
                    <button
                      onClick={() => handleNotificationChange('sms_alerts')}
                      className={`relative w-14 h-8 rounded-full transition-colors ${
                        notifications.sms_alerts ? 'bg-teal-600' : 'bg-gray-300'
                      }`}
                    >
                      <div
                        className={`absolute top-1 w-6 h-6 bg-white rounded-full transition-transform ${
                          notifications.sms_alerts ? 'translate-x-7' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>

                  <div className="flex items-center justify-between p-4 border border-gray-200 dark:border-slate-700 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">Medication Reminders</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Get reminders for your medications</p>
                    </div>
                    <button
                      onClick={() => handleNotificationChange('medication_reminders')}
                      className={`relative w-14 h-8 rounded-full transition-colors ${
                        notifications.medication_reminders ? 'bg-teal-600' : 'bg-gray-300'
                      }`}
                    >
                      <div
                        className={`absolute top-1 w-6 h-6 bg-white rounded-full transition-transform ${
                          notifications.medication_reminders ? 'translate-x-7' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>

                  <div className="flex items-center justify-between p-4 border border-gray-200 dark:border-slate-700 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">Appointment Reminders</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Get reminders for your appointments</p>
                    </div>
                    <button
                      onClick={() => handleNotificationChange('appointment_reminders')}
                      className={`relative w-14 h-8 rounded-full transition-colors ${
                        notifications.appointment_reminders ? 'bg-teal-600' : 'bg-gray-300'
                      }`}
                    >
                      <div
                        className={`absolute top-1 w-6 h-6 bg-white rounded-full transition-transform ${
                          notifications.appointment_reminders ? 'translate-x-7' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>

                  <div className="flex items-center justify-between p-4 border border-gray-200 dark:border-slate-700 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">Health Updates</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Receive health tips and updates</p>
                    </div>
                    <button
                      onClick={() => handleNotificationChange('health_updates')}
                      className={`relative w-14 h-8 rounded-full transition-colors ${
                        notifications.health_updates ? 'bg-teal-600' : 'bg-gray-300'
                      }`}
                    >
                      <div
                        className={`absolute top-1 w-6 h-6 bg-white rounded-full transition-transform ${
                          notifications.health_updates ? 'translate-x-7' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}