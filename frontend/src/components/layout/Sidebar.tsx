import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';
import toast from 'react-hot-toast';
import {
  HomeIcon,
  BellAlertIcon,
  UsersIcon,
  BeakerIcon,
  DocumentTextIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  CalendarDaysIcon,
  HeartIcon,
} from '@heroicons/react/24/outline';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuthStore();
  const [isLogoutPending, setIsLogoutPending] = React.useState(false);

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    { name: 'Alerts', href: '/alerts', icon: BellAlertIcon },
    { name: 'Health', href: '/health', icon: HeartIcon },
    { name: 'Patients', href: '/patients', icon: UsersIcon },
    { name: 'Patient Search', href: '/patients/search', icon: UsersIcon },
    { name: 'Medications', href: '/medications', icon: BeakerIcon },
    { name: 'Med Adherence', href: '/adherence', icon: CalendarDaysIcon },
    { name: 'Appointments', href: '/appointments', icon: CalendarDaysIcon },
    { name: 'Discharge Summaries', href: '/discharge-summaries', icon: DocumentTextIcon },
    { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
    { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
  ];

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
              navigate('/login');
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
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-gray-600 bg-opacity-75 z-20 lg:hidden"
          onClick={onClose}
        ></div>
      )}

      {/* Sidebar */}
      <div
        className={`
          fixed inset-y-0 left-0 z-30 w-64 bg-white dark:bg-gray-900 shadow-lg transform transition-transform duration-300 ease-in-out
          lg:translate-x-0 lg:static lg:inset-0
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-3">
              <img src="/logo.png" alt="BiCare360 Logo" className="h-10 w-10 object-contain" />
              <h1 className="text-xl font-bold text-primary-600 dark:text-primary-400">BiCare360</h1>
            </div>
            <button onClick={onClose} className="lg:hidden text-gray-700 dark:text-gray-300 hover:text-teal-600 dark:hover:text-teal-400 transition-colors">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors
                    ${
                      isActive
                        ? 'bg-aqua-50 dark:bg-teal-900/20 text-teal-700 dark:text-teal-300 border-l-4 border-teal-500'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-aqua-50 dark:hover:bg-gray-800 hover:text-teal-600 dark:hover:text-teal-400'
                    }
                  `}
                  onClick={() => {
                    if (window.innerWidth < 1024) {
                      onClose();
                    }
                  }}
                >
                  <item.icon className="w-5 h-5 mr-3" />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* Logout */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={handleLogout}
              className="flex items-center w-full px-4 py-3 text-sm font-medium text-gray-700 dark:text-gray-300 rounded-lg hover:bg-aqua-50 dark:hover:bg-gray-800 hover:text-teal-600 dark:hover:text-teal-400 transition-colors"
            >
              <ArrowRightOnRectangleIcon className="w-5 h-5 mr-3" />
              Logout
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
