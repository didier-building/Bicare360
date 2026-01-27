import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { PlusIcon, MagnifyingGlassIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import CreateDischargeSummaryModal from '../components/discharge/CreateDischargeSummaryModal';
import { dischargeAPI } from '../api/discharge';

const DischargeSummariesPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['dischargeSummaries', searchQuery, riskFilter],
    queryFn: () => dischargeAPI.getDischargeSummaries({
      search: searchQuery || undefined,
      risk_level: riskFilter || undefined,
    }),
  });

  const getRiskBadgeColor = (risk: string) => {
    switch (risk) {
      case 'critical': return 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 border-red-200 dark:border-red-800';
      case 'high': return 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300 border-orange-200 dark:border-orange-800';
      case 'medium': return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300 border-yellow-200 dark:border-yellow-800';
      case 'low': return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 border-green-200 dark:border-green-800';
      default: return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300';
    }
  };

  if (isLoading) return <LoadingSpinner />;

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 dark:text-red-400 mb-2">Failed to load discharge summaries</p>
        <button
          onClick={() => refetch()}
          className="mt-4 px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 shadow-md hover:shadow-lg transition-all"
        >
          Retry
        </button>
      </div>
    );
  }

  const summaries = data?.results || [];

  return (
    <div>
      {/* Header */}
      <div className="mb-6 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Discharge Summaries</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Manage patient discharge summaries and care plans
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 font-medium"
        >
          <PlusIcon className="w-5 h-5" />
          Create Discharge Summary
        </button>
      </div>

      {/* Stats */}
      {data && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
            <p className="text-sm text-gray-600 dark:text-gray-400">Total Summaries</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{data.count}</p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
            <p className="text-sm text-gray-600 dark:text-gray-400">Critical Risk</p>
            <p className="text-2xl font-bold text-red-600 dark:text-red-400">
              {summaries.filter((s: any) => s.risk_level === 'critical').length}
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
            <p className="text-sm text-gray-600 dark:text-gray-400">High Risk</p>
            <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">
              {summaries.filter((s: any) => s.risk_level === 'high').length}
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
            <p className="text-sm text-gray-600 dark:text-gray-400">This Month</p>
            <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {summaries.filter((s: any) => {
                const dischargeDate = new Date(s.discharge_date);
                const now = new Date();
                return dischargeDate.getMonth() === now.getMonth() && 
                       dischargeDate.getFullYear() === now.getFullYear();
              }).length}
            </p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Search
            </label>
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by patient name or MRN..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Risk Level
            </label>
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
            >
              <option value="">All Risks</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>
      </div>

      {/* Summaries List */}
      {summaries.length === 0 ? (
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow">
          <DocumentTextIcon className="w-16 h-16 text-gray-400 dark:text-gray-600 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400 text-lg mb-2">No discharge summaries found</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="mt-4 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 font-medium"
          >
            Create First Summary
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {summaries.map((summary: any) => (
            <div
              key={summary.id}
              className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition-shadow p-6"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
                      <DocumentTextIcon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        {summary.patient?.full_name || `Patient #${summary.patient?.id || 'Unknown'}`}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {summary.patient?.national_id ? `ID: ${summary.patient.national_id}` : 'No ID'} • {summary.hospital_name || `Hospital ID: ${summary.hospital}`}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Discharge Date</p>
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {new Date(summary.discharge_date).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Primary Diagnosis</p>
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {summary.primary_diagnosis}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Risk Level</p>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getRiskBadgeColor(summary.risk_level)}`}>
                        {summary.risk_level?.toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Follow-up</p>
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {summary.follow_up_required ? 
                          (summary.follow_up_timeframe || 'Required') 
                          : 'Not Required'}
                      </p>
                    </div>
                  </div>

                  {summary.discharge_instructions && (
                    <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3 mb-3">
                      <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Discharge Instructions</p>
                      <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-2">
                        {summary.discharge_instructions}
                      </p>
                    </div>
                  )}
                </div>
              </div>

              <div className="flex justify-end gap-2 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <button className="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 font-medium">
                  View Details
                </button>
                <button className="px-4 py-2 text-sm text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20 rounded-lg hover:bg-primary-100 dark:hover:bg-primary-900/30 font-medium">
                  Edit
                </button>
                <button className="px-4 py-2 text-sm text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 font-medium">
                  Print
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {data && data.count > summaries.length && (
        <div className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
          Showing {summaries.length} of {data.count} discharge summaries
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <CreateDischargeSummaryModal onClose={() => setShowCreateModal(false)} />
      )}
    </div>
  );
};

export default DischargeSummariesPage;
