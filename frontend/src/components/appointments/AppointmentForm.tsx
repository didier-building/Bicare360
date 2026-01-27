import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { patientsAPI } from '../../api/patients';
import hospitalsAPI from '../../api/hospitals';
import type { Appointment, AppointmentCreateData } from '../../api/appointments';

interface AppointmentFormProps {
  initialData?: Appointment;
  onSubmit: (data: AppointmentCreateData) => void;
  isSubmitting: boolean;
}

const APPOINTMENT_TYPES = [
  { value: 'follow_up', label: 'Follow-up' },
  { value: 'medication_review', label: 'Medication Review' },
  { value: 'consultation', label: 'Consultation' },
  { value: 'emergency', label: 'Emergency' },
  { value: 'routine_checkup', label: 'Routine Checkup' },
];

const LOCATION_TYPES = [
  { value: 'hospital', label: 'Hospital' },
  { value: 'home_visit', label: 'Home Visit' },
  { value: 'telemedicine', label: 'Telemedicine' },
];

const AppointmentForm: React.FC<AppointmentFormProps> = ({
  initialData,
  onSubmit,
  isSubmitting,
}) => {
  const [formData, setFormData] = useState<AppointmentCreateData>({
    patient: initialData?.patient || 0,
    hospital: initialData?.hospital || 0,
    appointment_datetime: initialData?.appointment_datetime
      ? new Date(initialData.appointment_datetime).toISOString().slice(0, 16)
      : '',
    appointment_type: initialData?.appointment_type || 'consultation',
    location_type: initialData?.location_type || 'hospital',
    provider_name: initialData?.provider_name || '',
    department: initialData?.department || '',
    reason: initialData?.reason || '',
    notes: initialData?.notes || '',
    duration_minutes: initialData?.duration_minutes || 30,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Fetch patients
  const { data: patientsData, isLoading: loadingPatients } = useQuery({
    queryKey: ['patients'],
    queryFn: () => patientsAPI.getPatients({ limit: 100 }),
  });

  // Fetch hospitals
  const { data: hospitalsData, isLoading: loadingHospitals } = useQuery({
    queryKey: ['hospitals'],
    queryFn: () => hospitalsAPI.getHospitals({ limit: 100 }),
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'patient' || name === 'hospital' || name === 'duration_minutes'
        ? parseInt(value, 10)
        : value,
    }));
    // Clear error when field is modified
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.patient) {
      newErrors.patient = 'Please select a patient';
    }

    if (!formData.hospital) {
      newErrors.hospital = 'Please select a hospital';
    }

    if (!formData.appointment_datetime) {
      newErrors.appointment_datetime = 'Please select date and time';
    } else {
      const appointmentDate = new Date(formData.appointment_datetime);
      const now = new Date();
      if (appointmentDate < now && !initialData) {
        newErrors.appointment_datetime = 'Appointment date must be in the future';
      }
    }

    if (!formData.appointment_type) {
      newErrors.appointment_type = 'Please select appointment type';
    }

    if (!formData.location_type) {
      newErrors.location_type = 'Please select location type';
    }

    if (formData.duration_minutes && formData.duration_minutes < 5) {
      newErrors.duration_minutes = 'Duration must be at least 5 minutes';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (validate()) {
      onSubmit(formData);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Patient Selection */}
      <div>
        <label htmlFor="patient" className="block text-sm font-medium text-gray-700 mb-1">
          Patient <span className="text-red-500">*</span>
        </label>
        <select
          id="patient"
          name="patient"
          value={formData.patient}
          onChange={handleChange}
          disabled={loadingPatients || isSubmitting}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.patient ? 'border-red-500' : 'border-gray-300'
          }`}
        >
          <option value="">Select a patient</option>
          {patientsData?.results.map((patient) => (
            <option key={patient.id} value={patient.id}>
              {patient.full_name} - {patient.phone_number}
            </option>
          ))}
        </select>
        {errors.patient && <p className="mt-1 text-sm text-red-500">{errors.patient}</p>}
      </div>

      {/* Hospital Selection */}
      <div>
        <label htmlFor="hospital" className="block text-sm font-medium text-gray-700 mb-1">
          Hospital <span className="text-red-500">*</span>
        </label>
        <select
          id="hospital"
          name="hospital"
          value={formData.hospital}
          onChange={handleChange}
          disabled={loadingHospitals || isSubmitting}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.hospital ? 'border-red-500' : 'border-gray-300'
          }`}
        >
          <option value="">Select a hospital</option>
          {hospitalsData?.results.map((hospital) => (
            <option key={hospital.id} value={hospital.id}>
              {hospital.name} - {hospital.district}
            </option>
          ))}
        </select>
        {errors.hospital && <p className="mt-1 text-sm text-red-500">{errors.hospital}</p>}
      </div>

      {/* Date and Time */}
      <div>
        <label htmlFor="appointment_datetime" className="block text-sm font-medium text-gray-700 mb-1">
          Date & Time <span className="text-red-500">*</span>
        </label>
        <input
          type="datetime-local"
          id="appointment_datetime"
          name="appointment_datetime"
          value={formData.appointment_datetime}
          onChange={handleChange}
          disabled={isSubmitting}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.appointment_datetime ? 'border-red-500' : 'border-gray-300'
          }`}
        />
        {errors.appointment_datetime && (
          <p className="mt-1 text-sm text-red-500">{errors.appointment_datetime}</p>
        )}
      </div>

      {/* Appointment Type */}
      <div>
        <label htmlFor="appointment_type" className="block text-sm font-medium text-gray-700 mb-1">
          Appointment Type <span className="text-red-500">*</span>
        </label>
        <select
          id="appointment_type"
          name="appointment_type"
          value={formData.appointment_type}
          onChange={handleChange}
          disabled={isSubmitting}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.appointment_type ? 'border-red-500' : 'border-gray-300'
          }`}
        >
          {APPOINTMENT_TYPES.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>
        {errors.appointment_type && (
          <p className="mt-1 text-sm text-red-500">{errors.appointment_type}</p>
        )}
      </div>

      {/* Location Type */}
      <div>
        <label htmlFor="location_type" className="block text-sm font-medium text-gray-700 mb-1">
          Location Type <span className="text-red-500">*</span>
        </label>
        <select
          id="location_type"
          name="location_type"
          value={formData.location_type}
          onChange={handleChange}
          disabled={isSubmitting}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.location_type ? 'border-red-500' : 'border-gray-300'
          }`}
        >
          {LOCATION_TYPES.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>
        {errors.location_type && (
          <p className="mt-1 text-sm text-red-500">{errors.location_type}</p>
        )}
      </div>

      {/* Duration */}
      <div>
        <label htmlFor="duration_minutes" className="block text-sm font-medium text-gray-700 mb-1">
          Duration (minutes)
        </label>
        <input
          type="number"
          id="duration_minutes"
          name="duration_minutes"
          value={formData.duration_minutes}
          onChange={handleChange}
          min="5"
          step="5"
          disabled={isSubmitting}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.duration_minutes ? 'border-red-500' : 'border-gray-300'
          }`}
        />
        {errors.duration_minutes && (
          <p className="mt-1 text-sm text-red-500">{errors.duration_minutes}</p>
        )}
      </div>

      {/* Provider Name */}
      <div>
        <label htmlFor="provider_name" className="block text-sm font-medium text-gray-700 mb-1">
          Provider Name
        </label>
        <input
          type="text"
          id="provider_name"
          name="provider_name"
          value={formData.provider_name}
          onChange={handleChange}
          placeholder="e.g., Dr. Smith"
          disabled={isSubmitting}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Department */}
      <div>
        <label htmlFor="department" className="block text-sm font-medium text-gray-700 mb-1">
          Department
        </label>
        <input
          type="text"
          id="department"
          name="department"
          value={formData.department}
          onChange={handleChange}
          placeholder="e.g., Cardiology, Pediatrics"
          disabled={isSubmitting}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Reason */}
      <div>
        <label htmlFor="reason" className="block text-sm font-medium text-gray-700 mb-1">
          Reason for Appointment
        </label>
        <input
          type="text"
          id="reason"
          name="reason"
          value={formData.reason}
          onChange={handleChange}
          placeholder="Brief reason for appointment"
          disabled={isSubmitting}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Notes */}
      <div>
        <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
          Additional Notes
        </label>
        <textarea
          id="notes"
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          rows={3}
          placeholder="Any additional information..."
          disabled={isSubmitting}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Submit Button */}
      <div className="flex justify-end gap-3 pt-4 border-t">
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? 'Saving...' : initialData ? 'Update Appointment' : 'Create Appointment'}
        </button>
      </div>
    </form>
  );
};

export default AppointmentForm;
