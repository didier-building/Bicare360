import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  CalendarIcon,
  ClockIcon,
  UserIcon,
  MapPinIcon,
  PlusIcon,
  FunnelIcon,
  PencilIcon,
} from '@heroicons/react/24/outline';
import appointmentsAPI, { type Appointment } from '../api/appointments';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import CreateAppointmentModal from '../components/appointments/CreateAppointmentModal';
import EditAppointmentModal from '../components/appointments/EditAppointmentModal';

type StatusFilter = 'all' | 'upcoming' | 'completed' | 'cancelled';

const AppointmentsPage: React.FC = () => {
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('upcoming');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingAppointment, setEditingAppointment] = useState<Appointment | null>(null);

  // Fetch ALL appointments for statistics
  const { data: allAppointmentsData } = useQuery({
    queryKey: ['appointments', 'all'],
    queryFn: () => appointmentsAPI.getAppointments({ limit: 1000 }),
  });

  // Fetch filtered appointments for display
  const { data: appointmentsData, isLoading } = useQuery({
    queryKey: ['appointments', statusFilter],
    queryFn: () => {
      if (statusFilter === 'upcoming') {
        return appointmentsAPI.getUpcomingAppointments({ limit: 100 });
      }
      const statusMap: Record<StatusFilter, string | undefined> = {
        all: undefined,
        upcoming: undefined,
        completed: 'completed',
        cancelled: 'cancelled',
      };
      return appointmentsAPI.getAppointments({
        status: statusMap[statusFilter],
        limit: 100,
      });
    },
  });

  // Note: Appointment status changes (confirm/cancel/complete) are handled by patients or system, not nurses

  const appointments = appointmentsData?.results || [];
  const allAppointments = allAppointmentsData?.results || [];

  // Statistics - calculated from ALL appointments, not just filtered ones
  const stats = useMemo(() => {
    return {
      total: allAppointments.length,
      scheduled: allAppointments.filter((a: Appointment) => a.status === 'scheduled').length,
      confirmed: allAppointments.filter((a: Appointment) => a.status === 'confirmed').length,
      completed: allAppointments.filter((a: Appointment) => a.status === 'completed').length,
      cancelled: allAppointments.filter((a: Appointment) => a.status === 'cancelled').length,
      noShow: allAppointments.filter((a: Appointment) => a.status === 'no_show').length,
    };
  }, [allAppointments]);

  const getStatusBadge = (status: string) => {
    const badges = {
      scheduled: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
      confirmed: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
      completed: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
      cancelled: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
      no_show: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
      rescheduled: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
    };
    return badges[status as keyof typeof badges] || badges.scheduled;
  };

  const getTypeBadge = (type: string) => {
    const badges = {
      follow_up: 'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300',
      medication_review: 'bg-purple-50 text-purple-700 dark:bg-purple-900/20 dark:text-purple-300',
      consultation: 'bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-300',
      emergency: 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-300',
      routine_checkup: 'bg-gray-50 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
    };
    return badges[type as keyof typeof badges] || badges.consultation;
  };

  const formatDateTime = (datetime: string) => {
    const date = new Date(datetime);
    return {
      date: date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }),
      time: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    };
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Appointments</h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Schedule and manage patient appointments
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-teal-600 text-white rounded-md hover:bg-teal-700 transition-colors shadow-md hover:shadow-lg"
        >
          <PlusIcon className="w-5 h-5" />
          New Appointment
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-200 dark:border-gray-700">
          <p className="text-xs font-medium text-gray-600 dark:text-gray-400">Total</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{stats.total}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-200 dark:border-gray-700">
          <p className="text-xs font-medium text-gray-600 dark:text-gray-400">Scheduled</p>
          <p className="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-1">{stats.scheduled}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-200 dark:border-gray-700">
          <p className="text-xs font-medium text-gray-600 dark:text-gray-400">Confirmed</p>
          <p className="text-2xl font-bold text-green-600 dark:text-green-400 mt-1">{stats.confirmed}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-200 dark:border-gray-700">
          <p className="text-xs font-medium text-gray-600 dark:text-gray-400">Completed</p>
          <p className="text-2xl font-bold text-gray-600 dark:text-gray-400 mt-1">{stats.completed}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-200 dark:border-gray-700">
          <p className="text-xs font-medium text-gray-600 dark:text-gray-400">Cancelled</p>
          <p className="text-2xl font-bold text-red-600 dark:text-red-400 mt-1">{stats.cancelled}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-200 dark:border-gray-700">
          <p className="text-xs font-medium text-gray-600 dark:text-gray-400">No Show</p>
          <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400 mt-1">{stats.noShow}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-200 dark:border-gray-700">
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
          <div className="flex items-center gap-2">
            <FunnelIcon className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Filter:</span>
          </div>
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => setStatusFilter('all')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                statusFilter === 'all'
                  ? 'bg-teal-600 text-white shadow-md'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              All ({stats.total})
            </button>
            <button
              onClick={() => setStatusFilter('upcoming')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                statusFilter === 'upcoming'
                  ? 'bg-teal-600 text-white shadow-md'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              Upcoming ({stats.scheduled + stats.confirmed})
            </button>
            <button
              onClick={() => setStatusFilter('completed')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                statusFilter === 'completed'
                  ? 'bg-teal-600 text-white shadow-md'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              Completed ({stats.completed})
            </button>
            <button
              onClick={() => setStatusFilter('cancelled')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                statusFilter === 'cancelled'
                  ? 'bg-teal-600 text-white shadow-md'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              Cancelled ({stats.cancelled})
            </button>
          </div>
        </div>
      </div>

      {/* Appointments List */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
        <div className="p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            {statusFilter === 'upcoming' ? 'Upcoming Appointments' : 'All Appointments'}
          </h2>
          
          {appointments.length === 0 ? (
            <div className="text-center py-12">
              <CalendarIcon className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-600" />
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No appointments</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {statusFilter === 'upcoming' ? 'No upcoming appointments scheduled' : 'No appointments found'}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {appointments.map((appointment: Appointment) => {
                const { date, time } = formatDateTime(appointment.appointment_datetime);
                return (
                  <div
                    key={appointment.id}
                    className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex flex-col sm:flex-row justify-between gap-4">
                      {/* Left side - Info */}
                      <div className="flex-1 space-y-2">
                        <div className="flex items-start gap-3">
                          <div className="flex-shrink-0 h-10 w-10 bg-aqua-100 dark:bg-teal-900/30 rounded-full flex items-center justify-center">
                            <UserIcon className="w-6 h-6 text-teal-600 dark:text-teal-400" />
                          </div>
                          <div className="flex-1">
                            <h3 className="text-base font-semibold text-gray-900 dark:text-white">
                              {appointment.patient_name || `Patient #${appointment.patient}`}
                            </h3>
                            <p className="text-sm text-gray-600 dark:text-gray-400">{appointment.reason || 'No reason provided'}</p>
                          </div>
                        </div>

                        <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400">
                          <div className="flex items-center gap-1">
                            <CalendarIcon className="w-4 h-4" />
                            <span>{date}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <ClockIcon className="w-4 h-4" />
                            <span>{time}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <MapPinIcon className="w-4 h-4" />
                            <span>{appointment.location_type === 'hospital' ? 'Hospital Visit' : appointment.location_type === 'home_visit' ? 'Home Visit' : 'Telemedicine'}</span>
                          </div>
                          {appointment.provider_name && (
                            <div className="flex items-center gap-1">
                              <UserIcon className="w-4 h-4" />
                              <span>{appointment.provider_name}</span>
                            </div>
                          )}
                        </div>

                        <div className="flex gap-2">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusBadge(appointment.status)}`}>
                            {appointment.status.replace('_', ' ').toUpperCase()}
                          </span>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getTypeBadge(appointment.appointment_type)}`}>
                            {appointment.appointment_type.replace('_', ' ')}
                          </span>
                        </div>
                      </div>

                      <div className="flex sm:flex-col gap-2">
                        <button
                          onClick={() => setEditingAppointment(appointment)}
                          className="flex items-center gap-1 px-3 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 text-sm"
                        >
                          <PencilIcon className="w-4 h-4" />
                          Edit
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      {showCreateModal && (
        <CreateAppointmentModal onClose={() => setShowCreateModal(false)} />
      )}
      {editingAppointment && (
        <EditAppointmentModal
          appointment={editingAppointment}
          onClose={() => setEditingAppointment(null)}
        />
      )}
    </div>
  );
};

export default AppointmentsPage;
