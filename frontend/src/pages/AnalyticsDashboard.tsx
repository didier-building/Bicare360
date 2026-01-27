import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { analyticsAPI } from '../api/analytics';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import toast from 'react-hot-toast';

const AnalyticsDashboard: React.FC = () => {
  const [autoRefresh, setAutoRefresh] = useState(true);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: () => analyticsAPI.getDashboardMetrics(),
    refetchInterval: autoRefresh ? 60000 : false, // Refresh every 60 seconds
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-2">Failed to load analytics dashboard.</p>
        <p className="text-red-500 text-sm mb-4">{error instanceof Error ? error.message : 'Unknown error'}</p>
        <button
          onClick={() => refetch()}
          className="mt-4 px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 shadow-md hover:shadow-lg"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!data) {
    return <div className="text-center py-12">No data available</div>;
  }

  // Prepare chart data - dynamically from backend
  const statusColorMap: { [key: string]: string } = {
    new: '#3b82f6',
    assigned: '#8b5cf6',
    in_progress: '#f59e0b',
    resolved: '#10b981',
    escalated: '#ef4444',
  };

  const statusChartData = Object.entries(data.alerts.status_counts)
    .map(([status, value]) => ({
      name: status.replace('_', ' ').toUpperCase(),
      value,
      fill: statusColorMap[status] || '#6b7280',
    }));

  const severityChartData = [
    { name: 'Critical', value: data.alerts.severity_counts.critical, fill: '#ef4444' },
    { name: 'High', value: data.alerts.severity_counts.high, fill: '#f97316' },
    {
      name: 'Medium',
      value: data.alerts.severity_counts.medium,
      fill: '#eab308',
    },
    { name: 'Low', value: data.alerts.severity_counts.low, fill: '#10b981' },
  ];

  const statusDistributionData = statusChartData;

  const COLORS = ['#3b82f6', '#8b5cf6', '#f59e0b', '#10b981', '#ef4444', '#6b7280'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 dark:text-gray-100">Analytics Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Real-time system metrics and performance indicators
          </p>
        </div>
        <div className="flex gap-3 items-center">
          <label className="flex items-center gap-2 px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded text-teal-500 focus:ring-teal-500"
            />
            <span className="text-sm font-medium">Auto-refresh (60s)</span>
          </label>
          <button
            onClick={() => {
              refetch();
              toast.success('Data refreshed');
            }}
            className="px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 font-medium shadow-md hover:shadow-lg"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Alerts */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 dark:text-gray-400 text-sm font-medium">Total Alerts</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-gray-100 mt-2">
                {Object.values(data.alerts.status_counts).reduce((a, b) => a + b, 0)}
              </p>
            </div>
            <div className="text-3xl text-blue-500">🚨</div>
          </div>
        </div>

        {/* Active Alerts */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 dark:text-gray-400 text-sm font-medium">Active Alerts</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-gray-100 mt-2">
                {data.alerts.total_active}
              </p>
            </div>
            <div className="text-3xl text-orange-500">⚡</div>
          </div>
        </div>

        {/* Overdue Alerts */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 dark:text-gray-400 text-sm font-medium">Overdue Alerts</p>
              <p className={`text-3xl font-bold mt-2 ${data.alerts.overdue_count > 0 ? 'text-red-600' : 'text-green-600'}`}>
                {data.alerts.overdue_count}
              </p>
            </div>
            <div className="text-3xl text-red-500">⏰</div>
          </div>
        </div>

        {/* Total Patients */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 dark:text-gray-400 text-sm font-medium">Total Patients</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-gray-100 mt-2">
                {data.patients.total_patients}
              </p>
            </div>
            <div className="text-3xl text-green-500">👥</div>
          </div>
        </div>
      </div>

      {/* Response Time Info */}
      {(data.alerts.avg_response_time_minutes || data.alerts.avg_resolution_time_minutes) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.alerts.avg_response_time_minutes && (
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <p className="text-blue-900 text-sm font-medium">Avg Response Time</p>
              <p className="text-2xl font-bold text-blue-600 mt-1">
                {Math.round(data.alerts.avg_response_time_minutes)} min
              </p>
            </div>
          )}
          {data.alerts.avg_resolution_time_minutes && (
            <div className="bg-green-50 rounded-lg p-4 border border-green-200">
              <p className="text-green-900 text-sm font-medium">Avg Resolution Time</p>
              <p className="text-2xl font-bold text-green-600 mt-1">
                {Math.round(data.alerts.avg_resolution_time_minutes)} min
              </p>
            </div>
          )}
        </div>
      )}

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Alert Status Distribution */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Alert Status Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusDistributionData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={false}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {COLORS.map((color, index) => (
                  <Cell key={`cell-${index}`} fill={color} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none', color: '#f3f4f6' }} formatter={(value) => `${value} alerts`} />
            </PieChart>
          </ResponsiveContainer>
          {/* Legend */}
          <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
            {statusChartData.map((item) => (
              <div key={item.name} className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: item.fill }}
                ></div>
                <span className="text-gray-700 dark:text-gray-300">
                  {item.name}: <strong>{item.value}</strong>
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Alert Severity Distribution */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Alert Severity Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={severityChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none', color: '#f3f4f6' }} />
              <Bar dataKey="value" fill="#8884d8" radius={[8, 8, 0, 0]}>
                {severityChartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Status Summary Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Alert Status Summary</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Count</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Percentage</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {statusChartData.map((item) => {
                const total = statusChartData.reduce((sum, s) => sum + s.value, 0);
                const percentage = total > 0 ? ((item.value / total) * 100).toFixed(1) : '0';
                return (
                  <tr key={item.name} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: item.fill }}
                        ></div>
                        <span className="text-sm font-medium text-gray-900">{item.name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {item.value}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {percentage}%
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Patient Stats Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Patient Statistics</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <tbody className="divide-y divide-gray-200">
              <tr className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">Total Patients</td>
                <td className="px-6 py-4 text-sm text-gray-600">{data.patients.total_patients}</td>
              </tr>
              <tr className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">Active Patients</td>
                <td className="px-6 py-4 text-sm text-gray-600">{data.patients.active_patients}</td>
              </tr>
              <tr className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">Inactive Patients</td>
                <td className="px-6 py-4 text-sm text-gray-600">{data.patients.inactive_patients}</td>
              </tr>
              <tr className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">New Enrollments (Today)</td>
                <td className="px-6 py-4 text-sm text-gray-600">{data.patients.new_enrollments_today}</td>
              </tr>
              <tr className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">New Enrollments (This Week)</td>
                <td className="px-6 py-4 text-sm text-gray-600">{data.patients.new_enrollments_this_week}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Last Updated */}
      <div className="text-center text-sm text-gray-600 pb-4">
        Last updated: {new Date(data.timestamp).toLocaleString()}
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
