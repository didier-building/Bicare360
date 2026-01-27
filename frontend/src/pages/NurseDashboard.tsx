import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { medicationsAPI } from '../api/medications';
import { nursingAPI } from '../api/nursing';
import { Link } from 'react-router-dom';
import { ClockIcon, ExclamationCircleIcon, ExclamationTriangleIcon, BellAlertIcon } from '@heroicons/react/24/outline';

const NurseDashboard: React.FC = () => {
  // Fetch current prescriptions
  const { data: prescriptionsData, isLoading: loadingPrescriptions } = useQuery({
    queryKey: ['currentPrescriptions'],
    queryFn: () => medicationsAPI.getCurrentPrescriptions(),
  });

  // Fetch current alerts
  const { data: alertsData, isLoading: loadingAlerts } = useQuery({
    queryKey: ['currentAlerts'],
    queryFn: () => nursingAPI.getAlerts({ page_size: 10 }),
  });

  // Filter active alerts (non-resolved)
  const activeAlerts = alertsData?.results.filter((a: any) => a.status !== 'resolved') || [];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">Nurse Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        {/* Stats cards */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Alerts</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-gray-100 mt-2">
            {activeAlerts.length}
          </p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Prescriptions</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-gray-100 mt-2">
            {prescriptionsData?.count || 0}
          </p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Critical Alerts</p>
          <p className="text-3xl font-bold text-red-600 dark:text-red-400 mt-2">
            {activeAlerts.filter((a: any) => a.severity === 'critical').length}
          </p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Overdue Alerts</p>
          <p className="text-3xl font-bold text-orange-600 dark:text-orange-400 mt-2">
            {activeAlerts.filter((a: any) => a.is_overdue).length}
          </p>
        </div>
      </div>

      {/* Active Prescriptions Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Active Prescriptions Today
          </h2>
          <Link
            to="/medications"
            className="text-sm text-teal-600 dark:text-teal-400 hover:text-teal-700 dark:hover:text-teal-300 font-medium"
          >
            View All Medications →
          </Link>
        </div>

        {loadingPrescriptions ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            Loading prescriptions...
          </div>
        ) : prescriptionsData && prescriptionsData.results.length > 0 ? (
          <div className="space-y-3">
            {prescriptionsData.results.slice(0, 5).map((prescription: any) => (
              <div
                key={prescription.id}
                className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <div className="flex-shrink-0">
                      <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
                        <span className="text-blue-600 dark:text-blue-400 font-semibold text-sm">
                          {prescription.patient_name?.split(' ').map((n: string) => n[0]).join('').slice(0, 2) || 'PT'}
                        </span>
                      </div>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-gray-100">
                        {prescription.patient_name || `Patient ID: ${typeof prescription.patient === 'object' ? prescription.patient?.id : prescription.patient}`}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        <span className="font-semibold">{prescription.medication_name || 'Medication'}</span>
                        {' • '}
                        {prescription.dosage}
                        {' • '}
                        {prescription.frequency}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-xs text-gray-500 dark:text-gray-400">Route</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100 capitalize">
                      {prescription.route}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-500 dark:text-gray-400">Duration</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {prescription.duration_days} days
                    </p>
                  </div>
                  <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300">
                    <ClockIcon className="w-3 h-3 mr-1" />
                    Active
                  </span>
                </div>
              </div>
            ))}
            {prescriptionsData.count > 5 && (
              <div className="text-center pt-2">
                <Link
                  to="/medications"
                  className="text-sm text-teal-600 dark:text-teal-400 hover:text-teal-700 dark:hover:text-teal-300 font-medium"
                >
                  View {prescriptionsData.count - 5} more prescriptions
                </Link>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-8">
            <ExclamationCircleIcon className="w-12 h-12 text-gray-400 dark:text-gray-600 mx-auto mb-3" />
            <p className="text-gray-600 dark:text-gray-400">No active prescriptions for today</p>
            <Link
              to="/medications"
              className="mt-2 inline-block text-sm text-teal-600 dark:text-teal-400 hover:text-teal-700 dark:hover:text-teal-300 font-medium"
            >
              Browse Medication Catalog
            </Link>
          </div>
        )}
      </div>

      {/* Current Alerts Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Current Alerts
          </h2>
          <Link
            to="/alerts"
            className="text-sm text-teal-600 dark:text-teal-400 hover:text-teal-700 dark:hover:text-teal-300 font-medium"
          >
            View All Alerts →
          </Link>
        </div>

        {loadingAlerts ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            Loading alerts...
          </div>
        ) : activeAlerts.length > 0 ? (
          <div className="space-y-3">
            {activeAlerts.slice(0, 5).map((alert: any) => {
              const severityColors = {
                critical: 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 border-red-200 dark:border-red-800',
                high: 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300 border-orange-200 dark:border-orange-800',
                medium: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300 border-yellow-200 dark:border-yellow-800',
                low: 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 border-blue-200 dark:border-blue-800',
              };

              const statusColors = {
                new: 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300',
                assigned: 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300',
                in_progress: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300',
                resolved: 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300',
              };

              return (
                <div
                  key={alert.id}
                  className={`flex items-center justify-between p-4 border rounded-lg transition-colors ${severityColors[alert.severity as keyof typeof severityColors]}`}
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <div className="flex-shrink-0">
                        {alert.severity === 'critical' ? (
                          <ExclamationTriangleIcon className="w-6 h-6 text-red-600 dark:text-red-400" />
                        ) : (
                          <BellAlertIcon className="w-6 h-6" />
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <p className="font-semibold text-gray-900 dark:text-gray-100">
                            {alert.patient?.first_name} {alert.patient?.last_name}
                          </p>
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[alert.status as keyof typeof statusColors]}`}>
                            {alert.status.replace('_', ' ').toUpperCase()}
                          </span>
                          {alert.is_overdue && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300">
                              OVERDUE
                            </span>
                          )}
                        </div>
                        <p className="text-sm font-medium">
                          {alert.title || alert.alert_type.replace('_', ' ').toUpperCase()}
                        </p>
                        <p className="text-xs mt-1 opacity-90">
                          {alert.description}
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-2 ml-4">
                    <span className="text-xs font-medium uppercase">
                      {alert.severity}
                    </span>
                    <span className="text-xs text-gray-600 dark:text-gray-400">
                      {new Date(alert.created_at).toLocaleString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>
                </div>
              );
            })}
            {activeAlerts.length > 5 && (
              <div className="text-center pt-2">
                <Link
                  to="/alerts"
                  className="text-sm text-teal-600 dark:text-teal-400 hover:text-teal-700 dark:hover:text-teal-300 font-medium"
                >
                  View {activeAlerts.length - 5} more alerts
                </Link>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-8">
            <BellAlertIcon className="w-12 h-12 text-gray-400 dark:text-gray-600 mx-auto mb-3" />
            <p className="text-gray-600 dark:text-gray-400">No active alerts</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default NurseDashboard;
