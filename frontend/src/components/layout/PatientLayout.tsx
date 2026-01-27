import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';
import toast from 'react-hot-toast';
import {
  HomeIcon,
  HeartIcon,
  CalendarDaysIcon,
  BeakerIcon,
  BellAlertIcon,
  UserIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
} from '@heroicons/react/24/outline';

const PatientLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout, user } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isLogoutPending, setIsLogoutPending] = useState(false);

  const navigation = [
    { name: 'Dashboard', href: '/patient/dashboard', icon: HomeIcon },
    { name: 'Health Progress', href: '/patient/health', icon: HeartIcon },
    { name: 'Appointments', href: '/patient/appointments', icon: CalendarDaysIcon },
    { name: 'Medications', href: '/patient/medications', icon: BeakerIcon },
    { name: 'Alerts', href: '/patient/alerts', icon: BellAlertIcon },
    { name: 'Caregivers', href: '/patient/caregivers', icon: UserIcon },
    { name: 'Profile', href: '/patient/profile', icon: UserIcon },
    { name: 'Settings', href: '/patient/settings', icon: Cog6ToothIcon },
  ];

  const isActive = (href: string) => location.pathname === href;

  const handleLogout = () => {
    if (isLogoutPending) return;
    
    setIsLogoutPending(true);
    toast((t) => (
      <div className="flex flex-col gap-3">
        <p className="font-medium">Are you sure you want to logout?</p>
        <div className="flex gap-2">
          <button
            onClick={() => {
              logout();
              navigate('/patient/login');
              toast.dismiss(t.id);
              toast.success('Logged out successfully');
              setIsLogoutPending(false);
            }}
            className="px-3 py-1.5 bg-red-500 text-white rounded-md text-sm font-medium hover:bg-red-600"
          >
            Yes, Logout
          </button>
          <button
            onClick={() => {
              toast.dismiss(t.id);
              setIsLogoutPending(false);
            }}
            className="px-3 py-1.5 bg-gray-200 text-gray-800 rounded-md text-sm font-medium hover:bg-gray-300"
          >
            Cancel
          </button>
        </div>
      </div>
    ), {
      duration: 10000,
      style: {
        background: '#fff',
        color: '#1f2937',
      },
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-gray-600 bg-opacity-75 z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}

      {/* Sidebar */}
      <div
        className={`
          fixed inset-y-0 left-0 z-30 w-64 bg-white dark:bg-gray-900 shadow-lg transform transition-transform duration-300 ease-in-out
          lg:translate-x-0 lg:static lg:inset-0 lg:w-64
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h1 className="text-xl font-bold text-blue-600 dark:text-blue-400">BiCare360</h1>
              <button
                onClick={() => setSidebarOpen(false)}
                className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
              >
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Patient Portal</p>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`
                    flex items-center gap-3 px-4 py-2.5 rounded-lg transition-colors duration-200
                    ${
                      active
                        ? 'bg-blue-50 dark:bg-blue-900 text-blue-600 dark:text-blue-400 font-medium'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                    }
                  `}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* User section */}
          <div className="border-t border-gray-200 dark:border-gray-700 px-3 py-4 space-y-2">
            <div className="px-4 py-2">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {user?.first_name} {user?.last_name}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">{user?.email}</p>
            </div>
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors duration-200"
            >
              <ArrowRightOnRectangleIcon className="w-5 h-5" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:ml-64">
        {/* Top bar */}
        <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-4 py-4 lg:px-6">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <Bars3Icon className="w-6 h-6" />
          </button>
        </div>

        {/* Page content */}
        <main className="p-4 lg:p-6 dark:bg-gray-950 min-h-screen">
          {children}
        </main>
      </div>
    </div>
  );
};

export default PatientLayout;
