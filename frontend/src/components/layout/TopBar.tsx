import React from 'react';
import { useAuthStore } from '../../stores/authStore';
import { Bars3Icon, BellIcon } from '@heroicons/react/24/outline';

interface TopBarProps {
  onMenuClick: () => void;
}

const TopBar: React.FC<TopBarProps> = ({ onMenuClick }) => {
  const { user } = useAuthStore();

  return (
    <div className="bg-white dark:bg-gray-900 shadow-sm border-b border-gray-200 dark:border-gray-700 h-16">
      <div className="flex items-center justify-between h-full px-4 lg:px-6">
        {/* Left side - Menu button */}
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 rounded-md text-gray-500 dark:text-gray-400 hover:text-teal-600 dark:hover:text-teal-400 hover:bg-aqua-50 dark:hover:bg-gray-800"
        >
          <Bars3Icon className="w-6 h-6" />
        </button>

        {/* Center - Page title (can be updated dynamically) */}
        <div className="flex-1 lg:flex-none"></div>

        {/* Right side - Notifications & User */}
        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <button className="relative p-2 rounded-md text-gray-500 dark:text-gray-400 hover:text-teal-600 dark:hover:text-teal-400 hover:bg-aqua-50 dark:hover:bg-gray-800">
            <BellIcon className="w-6 h-6" />
            <span className="absolute top-1 right-1 block h-2 w-2 rounded-full bg-teal-500 ring-2 ring-white dark:ring-gray-900"></span>
          </button>

          {/* User menu */}
          <div className="flex items-center space-x-3">
            <div className="hidden md:block text-right">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-200">
                {user?.first_name} {user?.last_name}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">{user?.role || 'Nurse'}</p>
            </div>
            <div className="w-10 h-10 rounded-full bg-teal-500 flex items-center justify-center text-white font-medium">
              {user?.first_name?.[0]}
              {user?.last_name?.[0]}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TopBar;
