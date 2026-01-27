import React from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { XMarkIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import appointmentsAPI, { type Appointment, type AppointmentCreateData } from '../../api/appointments';
import AppointmentForm from './AppointmentForm';

interface EditAppointmentModalProps {
  appointment: Appointment;
  onClose: () => void;
}

const EditAppointmentModal: React.FC<EditAppointmentModalProps> = ({ appointment, onClose }) => {
  const queryClient = useQueryClient();

  const updateMutation = useMutation({
    mutationFn: (data: AppointmentCreateData) => 
      appointmentsAPI.updateAppointment(appointment.id, data),
    onSuccess: () => {
      toast.success('Appointment updated successfully!');
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      queryClient.invalidateQueries({ queryKey: ['upcomingAppointments'] });
      onClose();
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.detail ||
                          'Failed to update appointment';
      toast.error(errorMessage);
    },
  });

  const handleSubmit = (data: AppointmentCreateData) => {
    updateMutation.mutate(data);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Edit Appointment</h2>
            <p className="text-sm text-gray-500 mt-1">
              Patient: {appointment.patient_name || 'Unknown'}
            </p>
          </div>
          <button
            onClick={onClose}
            disabled={updateMutation.isPending}
            className="text-gray-400 hover:text-gray-600 disabled:opacity-50"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-4 overflow-y-auto max-h-[calc(90vh-8rem)]">
          <AppointmentForm
            initialData={appointment}
            onSubmit={handleSubmit}
            isSubmitting={updateMutation.isPending}
          />
        </div>
      </div>
    </div>
  );
};

export default EditAppointmentModal;
