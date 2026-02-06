import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import SidebarContent from './SidebarContent';
import TopBar from './TopBar';

const DashboardLayout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-950">
      {/* Desktop Sidebar - Fixed width on large screens */}
      <div className="hidden lg:block fixed left-0 top-0 w-64 h-screen bg-white dark:bg-gray-900 shadow-lg border-r border-gray-200 dark:border-gray-700 z-40">
        <SidebarContent />
      </div>

      {/* Mobile Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main Content Area - Adjusted for sidebar on desktop */}
      <div className="flex flex-col flex-1 lg:ml-64 overflow-hidden">
        {/* Top bar */}
        <TopBar onMenuClick={() => setSidebarOpen(true)} />

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-6 bg-gray-50 dark:bg-gray-950">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
