import React from 'react';

const NurseDashboard: React.FC = () => {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Nurse Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        {/* Stats cards */}
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm font-medium text-gray-600">Active Alerts</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">12</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm font-medium text-gray-600">Assigned Patients</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">8</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm font-medium text-gray-600">Overdue</p>
          <p className="text-3xl font-bold text-red-600 mt-2">3</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-sm font-medium text-gray-600">Resolved Today</p>
          <p className="text-3xl font-bold text-green-600 mt-2">15</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Alerts</h2>
        <p className="text-gray-600">Alert list will be implemented in Week 10</p>
      </div>
    </div>
  );
};

export default NurseDashboard;
