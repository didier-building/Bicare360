import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../api/client';
import toast from 'react-hot-toast';

interface Appointment {
  id: number;
  appointment_datetime: string;
  appointment_type: string;
  status: string;
  location_type: string;
  provider_name: string;
  hospital_name: string;
  department: string;
  reason: string;
  duration_minutes: number;
  is_upcoming: boolean;
  days_until_appointment: number;
  notes?: string;
  notes_kinyarwanda?: string;
}

interface AppointmentDetail extends Appointment {
  hospital_phone?: string;
  hospital_address?: {
    province: string;
    district: string;
    sector: string;
  };
  is_cancellable: boolean;
  is_reschedulable: boolean;
}

type FilterStatus = 'all' | 'confirmed' | 'scheduled' | 'completed' | 'cancelled' | 'no_show';
type FilterType = 'all' | 'follow_up' | 'medication_review' | 'consultation' | 'emergency' | 'routine_checkup';

const STATUS_COLORS: Record<string, string> = {
  confirmed: 'bg-green-100 text-green-800 border-green-300',
  scheduled: 'bg-blue-100 text-blue-800 border-blue-300',
  completed: 'bg-gray-100 text-gray-800 border-gray-300',
  cancelled: 'bg-red-100 text-red-800 border-red-300',
  no_show: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  rescheduled: 'bg-purple-100 text-purple-800 border-purple-300',
};

const APPOINTMENT_TYPE_ICONS: Record<string, string> = {
  follow_up: '🔍',
  medication_review: '💊',
  consultation: '👨‍⚕️',
  emergency: '🚨',
  routine_checkup: '🩺',
};

export default function PatientAppointmentsPage() {
  const navigate = useNavigate();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [selectedAppointment, setSelectedAppointment] = useState<AppointmentDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [filterStatus, setFilterStatus] = useState<FilterStatus>('all');
  const [filterType, setFilterType] = useState<FilterType>('all');
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showRescheduleModal, setShowRescheduleModal] = useState(false);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [newDateTime, setNewDateTime] = useState('');
  const [cancellationReason, setCancellationReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    fetchAppointments();
  }, [filterStatus, filterType]);

  const fetchAppointments = async () => {
    try {
      setIsLoading(true);
      const params = new URLSearchParams();
      
      if (filterStatus !== 'all') params.append('status', filterStatus);
      if (filterType !== 'all') params.append('appointment_type', filterType);

      const response = await client.get(`/v1/appointments/my-appointments/?${params}`);
      setAppointments(response.data);
    } catch (error) {
      console.error('Error fetching appointments:', error);
      toast.error('Failed to load appointments');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchAppointmentDetail = async (id: number) => {
    try {
      const response = await client.get(`/v1/appointments/my-appointments/${id}/`);
      setSelectedAppointment(response.data);
      setShowDetailModal(true);
    } catch (error) {
      console.error('Error fetching appointment detail:', error);
      toast.error('Failed to load appointment details');
    }
  };

  const handleReschedule = async () => {
    if (!selectedAppointment || !newDateTime) {
      toast.error('Please select a new date and time');
      return;
    }

    try {
      setIsSubmitting(true);
      const newDateObj = new Date(newDateTime);
      const isoDateTime = newDateObj.toISOString();

      await client.patch(
        `/v1/appointments/my-appointments/${selectedAppointment.id}/reschedule/`,
        { appointment_datetime: isoDateTime }
      );

      toast.success('Appointment rescheduled successfully');
      setShowRescheduleModal(false);
      setNewDateTime('');
      setShowDetailModal(false);
      fetchAppointments();
    } catch (error: any) {
      console.error('Error rescheduling appointment:', error);
      const message = error.response?.data?.detail || error.response?.data?.appointment_datetime?.[0] || 'Failed to reschedule appointment';
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = async () => {
    if (!selectedAppointment) return;

    try {
      setIsSubmitting(true);
      await client.post(
        `/v1/appointments/my-appointments/${selectedAppointment.id}/cancel/`,
        { cancellation_reason: cancellationReason || null }
      );

      toast.success('Appointment cancelled successfully');
      setShowCancelModal(false);
      setCancellationReason('');
      setShowDetailModal(false);
      fetchAppointments();
    } catch (error: any) {
      console.error('Error cancelling appointment:', error);
      const message = error.response?.data?.detail || 'Failed to cancel appointment';
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatDateTime = (dateTimeString: string) => {
    const date = new Date(dateTimeString);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getMinDateTime = () => {
    const now = new Date();
    now.setMinutes(now.getMinutes() + 30);
    return now.toISOString().slice(0, 16);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4 md:p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            📅 My Appointments
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            View, reschedule, or cancel your appointments
          </p>
        </div>

        {/* Action Buttons */}
        <div className="mb-6 flex gap-3 flex-wrap">
          <button
            onClick={() => navigate('/patient/appointment-request')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
          >
            + Request New Appointment
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Status
              </label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value as FilterStatus)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="all">All Statuses</option>
                <option value="confirmed">Confirmed</option>
                <option value="scheduled">Scheduled</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
                <option value="no_show">No Show</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Type
              </label>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value as FilterType)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="all">All Types</option>
                <option value="follow_up">Follow-up</option>
                <option value="medication_review">Medication Review</option>
                <option value="consultation">Consultation</option>
                <option value="emergency">Emergency</option>
                <option value="routine_checkup">Routine Checkup</option>
              </select>
            </div>
          </div>
        </div>

        {/* Appointments List */}
        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : appointments.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center">
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              No appointments found matching your filters
            </p>
            <button
              onClick={() => navigate('/patient/appointment-request')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Request an Appointment
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {appointments.map((appointment) => (
              <div
                key={appointment.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition cursor-pointer p-4"
                onClick={() => fetchAppointmentDetail(appointment.id)}
              >
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  {/* Left Section */}
                  <div className="flex-1">
                    <div className="flex items-start gap-3">
                      <span className="text-2xl">
                        {APPOINTMENT_TYPE_ICONS[appointment.appointment_type] || '📋'}
                      </span>
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          {appointment.appointment_type.replace(/_/g, ' ').toUpperCase()}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {appointment.hospital_name}
                        </p>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          👨‍⚕️ Dr. {appointment.provider_name}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Middle Section */}
                  <div className="text-center md:text-right">
                    <div className="text-lg font-semibold text-gray-900 dark:text-white">
                      📅 {formatDateTime(appointment.appointment_datetime).split(',')[0]}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      ⏰ {formatDateTime(appointment.appointment_datetime).split(',')[1].trim()}
                    </div>
                    {appointment.is_upcoming && appointment.days_until_appointment > 0 && (
                      <div className="text-xs text-blue-600 dark:text-blue-400 font-medium mt-1">
                        In {appointment.days_until_appointment} day{appointment.days_until_appointment !== 1 ? 's' : ''}
                      </div>
                    )}
                  </div>

                  {/* Right Section - Status */}
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-medium border ${
                        STATUS_COLORS[appointment.status] || 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {appointment.status.replace(/_/g, ' ').toUpperCase()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {showDetailModal && selectedAppointment && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6 flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Appointment Details
              </h2>
              <button
                onClick={() => setShowDetailModal(false)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-2xl"
              >
                ×
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6 space-y-6">
              {/* Appointment Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Appointment Type
                  </label>
                  <p className="text-gray-900 dark:text-white">
                    {selectedAppointment.appointment_type.replace(/_/g, ' ').toUpperCase()}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Status
                  </label>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium border inline-block ${
                      STATUS_COLORS[selectedAppointment.status] || 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {selectedAppointment.status.replace(/_/g, ' ').toUpperCase()}
                  </span>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Date & Time
                  </label>
                  <p className="text-gray-900 dark:text-white">
                    {formatDateTime(selectedAppointment.appointment_datetime)}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Duration
                  </label>
                  <p className="text-gray-900 dark:text-white">
                    {selectedAppointment.duration_minutes} minutes
                  </p>
                </div>
              </div>

              {/* Provider & Hospital Info */}
              <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Healthcare Provider
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Provider Name
                    </label>
                    <p className="text-gray-900 dark:text-white">
                      Dr. {selectedAppointment.provider_name}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Department
                    </label>
                    <p className="text-gray-900 dark:text-white">
                      {selectedAppointment.department}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Hospital
                    </label>
                    <p className="text-gray-900 dark:text-white">
                      {selectedAppointment.hospital_name}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Location Type
                    </label>
                    <p className="text-gray-900 dark:text-white">
                      {selectedAppointment.location_type.replace(/_/g, ' ').toUpperCase()}
                    </p>
                  </div>
                </div>
              </div>

              {/* Hospital Location */}
              {selectedAppointment.hospital_address && (
                <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Location Details
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Province
                      </label>
                      <p className="text-gray-900 dark:text-white">
                        {selectedAppointment.hospital_address.province}
                      </p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        District
                      </label>
                      <p className="text-gray-900 dark:text-white">
                        {selectedAppointment.hospital_address.district}
                      </p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Sector
                      </label>
                      <p className="text-gray-900 dark:text-white">
                        {selectedAppointment.hospital_address.sector}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Reason & Notes */}
              {selectedAppointment.reason && (
                <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Reason for Appointment
                  </label>
                  <p className="text-gray-900 dark:text-white">
                    {selectedAppointment.reason}
                  </p>
                </div>
              )}

              {selectedAppointment.notes && (
                <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Notes (English)
                  </label>
                  <p className="text-gray-900 dark:text-white whitespace-pre-wrap">
                    {selectedAppointment.notes}
                  </p>
                </div>
              )}

              {selectedAppointment.notes_kinyarwanda && (
                <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Ibigambi (Kinyarwanda)
                  </label>
                  <p className="text-gray-900 dark:text-white whitespace-pre-wrap">
                    {selectedAppointment.notes_kinyarwanda}
                  </p>
                </div>
              )}

              {/* Action Buttons */}
              <div className="border-t border-gray-200 dark:border-gray-700 pt-6 flex gap-3 justify-end">
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition"
                >
                  Close
                </button>
                {selectedAppointment.is_reschedulable && (
                  <button
                    onClick={() => {
                      setShowDetailModal(false);
                      setShowRescheduleModal(true);
                    }}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                  >
                    📅 Reschedule
                  </button>
                )}
                {selectedAppointment.is_cancellable && (
                  <button
                    onClick={() => {
                      setShowDetailModal(false);
                      setShowCancelModal(true);
                    }}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
                  >
                    ❌ Cancel
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Reschedule Modal */}
      {showRescheduleModal && selectedAppointment && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full">
            <div className="border-b border-gray-200 dark:border-gray-700 p-6 flex justify-between items-center">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                📅 Reschedule Appointment
              </h2>
              <button
                onClick={() => setShowRescheduleModal(false)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-2xl"
              >
                ×
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  New Date & Time
                </label>
                <input
                  type="datetime-local"
                  value={newDateTime}
                  onChange={(e) => setNewDateTime(e.target.value)}
                  min={getMinDateTime()}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Current: {formatDateTime(selectedAppointment.appointment_datetime)}
                </p>
              </div>

              <div className="flex gap-3 justify-end pt-4 border-t border-gray-200 dark:border-gray-700">
                <button
                  onClick={() => setShowRescheduleModal(false)}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition"
                  disabled={isSubmitting}
                >
                  Cancel
                </button>
                <button
                  onClick={handleReschedule}
                  disabled={isSubmitting || !newDateTime}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {isSubmitting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Rescheduling...
                    </>
                  ) : (
                    'Confirm Reschedule'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Cancel Modal */}
      {showCancelModal && selectedAppointment && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full">
            <div className="border-b border-gray-200 dark:border-gray-700 p-6 flex justify-between items-center">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                ❌ Cancel Appointment
              </h2>
              <button
                onClick={() => setShowCancelModal(false)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-2xl"
              >
                ×
              </button>
            </div>

            <div className="p-6 space-y-4">
              <p className="text-gray-700 dark:text-gray-300">
                Are you sure you want to cancel this appointment on{' '}
                <strong>{formatDateTime(selectedAppointment.appointment_datetime)}</strong>?
              </p>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Reason for Cancellation (Optional)
                </label>
                <textarea
                  value={cancellationReason}
                  onChange={(e) => setCancellationReason(e.target.value)}
                  placeholder="E.g., Unable to attend due to work..."
                  maxLength={500}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {cancellationReason.length}/500 characters
                </p>
              </div>

              <div className="flex gap-3 justify-end pt-4 border-t border-gray-200 dark:border-gray-700">
                <button
                  onClick={() => setShowCancelModal(false)}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition"
                  disabled={isSubmitting}
                >
                  Keep Appointment
                </button>
                <button
                  onClick={handleCancel}
                  disabled={isSubmitting}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {isSubmitting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Cancelling...
                    </>
                  ) : (
                    'Cancel Appointment'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
