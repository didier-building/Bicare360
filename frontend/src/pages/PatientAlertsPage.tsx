import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../api/client';
import toast from 'react-hot-toast';

interface PatientAlert {
  id: number;
  alert_type: string;
  severity: string;
  title: string;
  description: string;
  status: string;
  created_at: string;
  resolved_at: string | null;
  discharge_summary?: {
    id: number;
    hospital: string;
  };
  appointment?: {
    id: number;
    appointment_datetime: string;
  };
}

const SEVERITY_COLORS = {
  low: { bg: 'bg-blue-50 dark:bg-blue-900/30', border: 'border-blue-200 dark:border-blue-800', text: 'text-blue-700 dark:text-blue-300', badge: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300' },
  medium: { bg: 'bg-yellow-50 dark:bg-yellow-900/30', border: 'border-yellow-200 dark:border-yellow-800', text: 'text-yellow-700 dark:text-yellow-300', badge: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300' },
  high: { bg: 'bg-orange-50 dark:bg-orange-900/30', border: 'border-orange-200 dark:border-orange-800', text: 'text-orange-700 dark:text-orange-300', badge: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300' },
  critical: { bg: 'bg-red-50 dark:bg-red-900/30', border: 'border-red-200 dark:border-red-800', text: 'text-red-700 dark:text-red-300', badge: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300' },
};

const ALERT_TYPE_ICONS: Record<string, string> = {
  missed_medication: '💊',
  missed_appointment: '📅',
  high_risk_discharge: '⚠️',
  symptom_report: '🤒',
  readmission_risk: '🏥',
  medication_side_effect: '⚡',
  emergency: '🚨',
  follow_up_needed: '👨‍⚕️',
};

const STATUS_COLORS: Record<string, string> = {
  new: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
  assigned: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
  in_progress: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
  resolved: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
  escalated: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
  closed: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
};

export default function PatientAlertsPage() {
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState<PatientAlert[]>([]);
  const [filteredAlerts, setFilteredAlerts] = useState<PatientAlert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [sortBy, setSortBy] = useState<'date' | 'severity'>('date');

  // Fetch alerts on component mount
  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        setIsLoading(true);
        setError('');

        // Fetch only current patient's alerts
        const response = await client.get('/v1/nursing/alerts/');
        const alertsData = response.data.results || response.data;
        
        setAlerts(alertsData);
        applyFilters(alertsData, filterStatus, filterSeverity, sortBy);
      } catch (err) {
        console.error('Failed to load alerts:', err);
        setError('Failed to load alerts');
        toast.error('Failed to load alerts');
      } finally {
        setIsLoading(false);
      }
    };

    fetchAlerts();
  }, []);

  // Apply filters and sorting
  const applyFilters = (
    alertsList: PatientAlert[],
    status: string,
    severity: string,
    sort: 'date' | 'severity'
  ) => {
    let filtered = [...alertsList];

    // Filter by status
    if (status !== 'all') {
      filtered = filtered.filter((a) => a.status === status);
    }

    // Filter by severity
    if (severity !== 'all') {
      filtered = filtered.filter((a) => a.severity === severity);
    }

    // Sort
    if (sort === 'date') {
      filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    } else if (sort === 'severity') {
      const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
      filtered.sort((a, b) => severityOrder[a.severity as keyof typeof severityOrder] - severityOrder[b.severity as keyof typeof severityOrder]);
    }

    setFilteredAlerts(filtered);
  };

  // Handle filter changes
  const handleStatusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newStatus = e.target.value;
    setFilterStatus(newStatus);
    applyFilters(alerts, newStatus, filterSeverity, sortBy);
  };

  const handleSeverityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newSeverity = e.target.value;
    setFilterSeverity(newSeverity);
    applyFilters(alerts, filterStatus, newSeverity, sortBy);
  };

  const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newSort = e.target.value as 'date' | 'severity';
    setSortBy(newSort);
    applyFilters(alerts, filterStatus, filterSeverity, newSort);
  };

  const getSeverityColor = (severity: string) => {
    return SEVERITY_COLORS[severity as keyof typeof SEVERITY_COLORS] || SEVERITY_COLORS.low;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const getAlertIcon = (type: string) => {
    return ALERT_TYPE_ICONS[type] || '📢';
  };

  const getAlertTypeLabel = (type: string) => {
    return type
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  // Statistics
  const stats = {
    total: alerts.length,
    critical: alerts.filter((a) => a.severity === 'critical').length,
    resolved: alerts.filter((a) => a.status === 'resolved').length,
    pending: alerts.filter((a) => a.status !== 'resolved' && a.status !== 'closed').length,
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-teal-50 to-cyan-50 dark:from-slate-950 dark:to-slate-900 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600 dark:border-teal-400 mb-4"></div>
          <p className="text-teal-700 dark:text-teal-200 font-medium">Loading your health alerts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-950 pb-12">
      {/* Header */}
      <header className="bg-gradient-to-r from-teal-600 to-teal-500 dark:from-teal-900 dark:to-teal-800 shadow-lg sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-white">Health Alerts</h1>
              <p className="text-teal-100 text-sm mt-1">Important health notifications & updates</p>
            </div>
            <button
              onClick={() => navigate('/patient/dashboard')}
              className="px-3 sm:px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors text-sm sm:text-base whitespace-nowrap"
            >
              ← Dashboard
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {/* Statistics Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 mb-8">
          <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-4 sm:p-6">
            <p className="text-gray-600 dark:text-gray-400 text-sm font-medium mb-1">Total Alerts</p>
            <p className="text-3xl font-bold text-teal-600 dark:text-teal-400">{stats.total}</p>
          </div>
          <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-4 sm:p-6 border-l-4 border-red-500">
            <p className="text-gray-600 dark:text-gray-400 text-sm font-medium mb-1">Critical</p>
            <p className="text-3xl font-bold text-red-600 dark:text-red-400">{stats.critical}</p>
          </div>
          <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-4 sm:p-6 border-l-4 border-yellow-500">
            <p className="text-gray-600 dark:text-gray-400 text-sm font-medium mb-1">Pending</p>
            <p className="text-3xl font-bold text-yellow-600 dark:text-yellow-400">{stats.pending}</p>
          </div>
          <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-4 sm:p-6 border-l-4 border-green-500">
            <p className="text-gray-600 dark:text-gray-400 text-sm font-medium mb-1">Resolved</p>
            <p className="text-3xl font-bold text-green-600 dark:text-green-400">{stats.resolved}</p>
          </div>
        </div>

        {/* Filters & Sorting */}
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-4 sm:p-6 mb-6">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Filter & Sort</h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Status
              </label>
              <select
                value={filterStatus}
                onChange={handleStatusChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              >
                <option value="all">All Statuses</option>
                <option value="new">New</option>
                <option value="assigned">Assigned</option>
                <option value="in_progress">In Progress</option>
                <option value="resolved">Resolved</option>
                <option value="escalated">Escalated</option>
                <option value="closed">Closed</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Severity
              </label>
              <select
                value={filterSeverity}
                onChange={handleSeverityChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              >
                <option value="all">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Sort By
              </label>
              <select
                value={sortBy}
                onChange={handleSortChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              >
                <option value="date">Most Recent</option>
                <option value="severity">By Severity</option>
              </select>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-700 dark:text-red-200">{error}</p>
          </div>
        )}

        {/* Alerts List */}
        {filteredAlerts.length === 0 ? (
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-8 sm:p-12 text-center">
            <p className="text-4xl mb-4">✨</p>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No Alerts</h3>
            <p className="text-gray-600 dark:text-gray-400">
              {filterStatus !== 'all' || filterSeverity !== 'all'
                ? 'No alerts match your filters'
                : 'You have no health alerts at this time. Keep up the good work!'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredAlerts.map((alert) => {
              const colors = getSeverityColor(alert.severity);
              return (
                <div
                  key={alert.id}
                  className={`border-2 rounded-lg p-4 sm:p-6 transition-all hover:shadow-md ${colors.bg} ${colors.border}`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
                    {/* Left Section */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start gap-3 mb-3">
                        <span className="text-2xl sm:text-3xl flex-shrink-0">
                          {getAlertIcon(alert.alert_type)}
                        </span>
                        <div className="flex-1 min-w-0">
                          <h3 className={`font-bold text-base sm:text-lg ${colors.text}`}>
                            {alert.title}
                          </h3>
                          <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-1">
                            {getAlertTypeLabel(alert.alert_type)}
                          </p>
                        </div>
                      </div>

                      <p className="text-sm sm:text-base text-gray-700 dark:text-gray-300 mb-3">
                        {alert.description}
                      </p>

                      {/* Related Info */}
                      {alert.appointment && (
                        <div className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-2">
                          📅 Appointment: {new Date(alert.appointment.appointment_datetime).toLocaleDateString()}
                        </div>
                      )}

                      {alert.discharge_summary && (
                        <div className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-2">
                          🏥 From: {alert.discharge_summary.hospital}
                        </div>
                      )}
                    </div>

                    {/* Right Section */}
                    <div className="flex flex-col gap-2 sm:items-end flex-shrink-0">
                      {/* Badges */}
                      <div className="flex flex-wrap gap-2 sm:justify-end">
                        <span className={`px-3 py-1 rounded-full text-xs sm:text-sm font-medium ${SEVERITY_COLORS[alert.severity as keyof typeof SEVERITY_COLORS].badge}`}>
                          {alert.severity.charAt(0).toUpperCase() + alert.severity.slice(1)}
                        </span>
                        <span className={`px-3 py-1 rounded-full text-xs sm:text-sm font-medium ${STATUS_COLORS[alert.status]}`}>
                          {alert.status.charAt(0).toUpperCase() + alert.status.slice(1)}
                        </span>
                      </div>

                      {/* Timestamps */}
                      <div className="text-right">
                        <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                          {formatDate(alert.created_at)}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-500">
                          {formatTime(alert.created_at)}
                        </p>
                        {alert.resolved_at && (
                          <p className="text-xs text-green-600 dark:text-green-400 font-medium mt-1">
                            Resolved: {formatDate(alert.resolved_at)}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Info Footer */}
        <div className="mt-8 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-xl p-4 sm:p-6">
          <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">💡 Understanding Alert Severity</h4>
          <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
            <li>🔴 <strong>Critical</strong> - Requires immediate attention</li>
            <li>🟠 <strong>High</strong> - Should be addressed soon</li>
            <li>🟡 <strong>Medium</strong> - Important but not urgent</li>
            <li>🔵 <strong>Low</strong> - General information or reminders</li>
          </ul>
        </div>
      </main>
    </div>
  );
}
