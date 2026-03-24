import React from 'react';
import { Link } from 'react-router-dom';
import { UserIcon, HeartIcon, UserGroupIcon } from '@heroicons/react/24/outline';

const LoginSelectionPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-950 dark:to-gray-900 flex items-center justify-center p-4">
      <div className="w-full max-w-6xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl lg:text-5xl font-bold text-gray-900 dark:text-white mb-2">
            BiCare360
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Home-Care Coordination and Caregiver Support Platform
          </p>
        </div>

        {/* Login cards */}
        <div className="grid md:grid-cols-3 gap-6">
          {/* Patient Login */}
          <Link
            to="/patient/login"
            className="group bg-white dark:bg-gray-800 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 p-8 hover:scale-105"
          >
            <div className="flex flex-col items-center text-center h-full">
              <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mb-6 group-hover:bg-blue-200 dark:group-hover:bg-blue-800 transition-colors">
                <HeartIcon className="w-8 h-8 text-blue-600 dark:text-blue-400" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Patient Portal
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-6 flex-1">
                Access your health records, appointments, medications, and track your vital signs
              </p>
              <span className="inline-block px-6 py-2 bg-blue-600 text-white rounded-lg font-medium group-hover:bg-blue-700 transition-colors">
                Login as Patient
              </span>
            </div>
          </Link>

          {/* Nurse/Staff Login */}
          <Link
            to="/login"
            className="group bg-white dark:bg-gray-800 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 p-8 hover:scale-105"
          >
            <div className="flex flex-col items-center text-center h-full">
              <div className="w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mb-6 group-hover:bg-green-200 dark:group-hover:bg-green-800 transition-colors">
                <UserIcon className="w-8 h-8 text-green-600 dark:text-green-400" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Staff Portal
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-6 flex-1">
                Manage patient care, view alerts, access analytics, and coordinate appointments
              </p>
              <span className="inline-block px-6 py-2 bg-green-600 text-white rounded-lg font-medium group-hover:bg-green-700 transition-colors">
                Login as Staff
              </span>
            </div>
          </Link>

          {/* Caregiver Login */}
          <Link
            to="/caregiver/login"
            className="group bg-white dark:bg-gray-800 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 p-8 hover:scale-105"
          >
            <div className="flex flex-col items-center text-center h-full">
              <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center mb-6 group-hover:bg-purple-200 dark:group-hover:bg-purple-800 transition-colors">
                <UserGroupIcon className="w-8 h-8 text-purple-600 dark:text-purple-400" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Caregiver Portal
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-6 flex-1">
                Manage your bookings, view appointments, and connect with patients for home care
              </p>
              <span className="inline-block px-6 py-2 bg-purple-600 text-white rounded-lg font-medium group-hover:bg-purple-700 transition-colors">
                Login as Caregiver
              </span>
            </div>
          </Link>
        </div>

        {/* Footer info */}
        <div className="mt-12 text-center text-gray-600 dark:text-gray-400 text-sm">
          <p className="mb-3 font-medium">Test Credentials:</p>
          <div className="mt-3 space-y-2 max-w-2xl mx-auto">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-3 shadow-sm">
              <p className="font-semibold text-blue-600 dark:text-blue-400">Patient:</p>
              <p className="text-xs mt-1">
                <strong>Username:</strong> patient1 | <strong>Password:</strong> Patient@2026
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg p-3 shadow-sm">
              <p className="font-semibold text-green-600 dark:text-green-400">Staff:</p>
              <p className="text-xs mt-1">
                <strong>Username:</strong> nurse1 | <strong>Password:</strong> Nurse@2026
              </p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg p-3 shadow-sm">
              <p className="font-semibold text-purple-600 dark:text-purple-400">Caregiver:</p>
              <p className="text-xs mt-1">
                <strong>Email:</strong> caregiver@test.com | <strong>Password:</strong> Caregiver@2026
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginSelectionPage;
