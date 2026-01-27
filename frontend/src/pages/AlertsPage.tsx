import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { nursingAPI } from '../api/nursing';
import type { Alert } from '../api/nursing';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import AlertDetailModal from '../components/AlertDetailModal';
import toast from 'react-hot-toast';
import { formatDistanceToNow } from 'date-fns';

const AlertsPage: React.FC = () => {
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [assignedToMe, setAssignedToMe] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['alerts', statusFilter, severityFilter, assignedToMe],
    queryFn: () => nursingAPI.getAlerts({
      status: statusFilter || undefined,
      severity: severityFilter || undefined,
      assigned_to_me: assignedToMe || undefined,
      ordering: '-created_at',
    }),
    refetchInterval: 30000, // Auto-refresh every 30 seconds
    refetchIntervalInBackground: false,
  });

  // Check for new critical alerts
  useEffect(() => {
    if (data?.results) {
      const criticalAlerts = data.results.filter(
        alert => alert.severity === 'critical' && alert.status === 'new'
      );
      
      if (criticalAlerts.length > 0) {
        // Show toast for new critical alerts (with deduplication)
        criticalAlerts.forEach(alert => {
          const toastId = `alert-${alert.id}`;
          if (!sessionStorage.getItem(toastId)) {
            toast.error(
              `New Critical Alert: ${alert.title || alert.alert_type}`,
              {
                duration: 10000,
                icon: '🚨',
              }
            );
            sessionStorage.setItem(toastId, 'shown');
          }
        });
      }
    }
  }, [data]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'new': return 'bg-blue-100 text-blue-800';
      case 'assigned': return 'bg-purple-100 text-purple-800';
      case 'in_progress': return 'bg-yellow-100 text-yellow-800';
      case 'resolved': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleAcknowledge = async (alertId: number) => {
    try {
      await nursingAPI.acknowledgeAlert(alertId);
      toast.success('Alert acknowledged');
      refetch();
    } catch (err) {
      console.error('Failed to acknowledge:', err);
      toast.error('Failed to acknowledge alert');
    }
  };

  const handleAssignToSelf = async (alertId: number) => {
    try {
      await nursingAPI.assignAlertToSelf(alertId);
      toast.success('Alert assigned to you');
      refetch();
    } catch (err) {
      console.error('Failed to assign:', err);
      toast.error('Failed to assign alert');
    }
  };

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
        <p className="text-red-600">Failed to load alerts. Please try again.</p>
        <button
          onClick={() => refetch()}
          className="mt-4 px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 shadow-md hover:shadow-lg"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Alerts</h1>
        <div className="flex flex-wrap gap-3">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg text-sm focus:ring-2 focus:ring-primary-500"
          >
            <option value="">All Statuses</option>
            <option value="new">New</option>
            <option value="assigned">Assigned</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
          </select>

          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg text-sm focus:ring-2 focus:ring-primary-500"
          >
            <option value="">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          <label className="flex items-center gap-2 px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg text-sm cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700">
            <input
              type="checkbox"
              checked={assignedToMe}
              onChange={(e) => setAssignedToMe(e.target.checked)}
              className="rounded text-teal-500 focus:ring-teal-500"
            />
            <span>My Alerts</span>
          </label>
        </div>
      </div>

      {data?.results.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-600">No alerts found</p>
        </div>
      ) : (
        <div className="space-y-4">
          {data?.results.map((alert) => (
            <div
              key={alert.id}
              className="bg-white rounded-lg shadow hover:shadow-md transition-shadow p-6"
            >
              <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-start gap-3 mb-3">
                    <div className={`px-3 py-1 rounded-full text-xs font-semibold border ${getSeverityColor(alert.severity)}`}>
                      {alert.severity.toUpperCase()}
                    </div>
                    <div className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(alert.status)}`}>
                      {alert.status.replace('_', ' ').toUpperCase()}
                    </div>
                  </div>

                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {alert.title || alert.alert_type}
                  </h3>

                  <p className="text-gray-600 mb-3">{alert.description}</p>

                  <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                    <span className="flex items-center gap-1">
                      👤 {alert.patient.first_name} {alert.patient.last_name}
                    </span>
                    <span>MRN: {alert.patient.medical_record_number}</span>
                    <span>🕒 {formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}</span>
                    {alert.assigned_nurse && (
                      <span>
                        Assigned to: {alert.assigned_nurse.user.first_name} {alert.assigned_nurse.user.last_name}
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex lg:flex-col gap-2">
                  {alert.status === 'new' && (
                    <>
                      <button
                        onClick={() => handleAcknowledge(alert.id)}
                        className="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm font-medium hover:bg-blue-600 transition-colors"
                      >
                        Acknowledge
                      </button>
                      {!alert.assigned_nurse && (
                        <button
                          onClick={() => handleAssignToSelf(alert.id)}
                          className="px-4 py-2 bg-purple-500 text-white rounded-lg text-sm font-medium hover:bg-purple-600 transition-colors"
                        >
                          Assign to Me
                        </button>
                      )}
                    </>
                  )}
                  <button
                    onClick={() => setSelectedAlert(alert)}
                    className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg text-sm font-medium hover:bg-gray-300 transition-colors"
                  >
                    View Details
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {data && data.count > 0 && (
        <div className="mt-6 flex items-center justify-between">
          <p className="text-sm text-gray-600">
            Showing {data.results.length} of {data.count} alerts
          </p>
          <div className="flex gap-2">
            {data.previous && (
              <button
                onClick={() => {/* TODO: Handle pagination */}}
                className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50"
              >
                Previous
              </button>
            )}
            {data.next && (
              <button
                onClick={() => {/* TODO: Handle pagination */}}
                className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50"
              >
                Next
              </button>
            )}
          </div>
        </div>
      )}
      
      {/* Alert Detail Modal */}
      {selectedAlert && (
        <AlertDetailModal
          alert={selectedAlert}
          isOpen={true}
          onClose={() => setSelectedAlert(null)}
          onUpdate={() => refetch()}
        />
      )}
    </div>
  );
};

export default AlertsPage;
