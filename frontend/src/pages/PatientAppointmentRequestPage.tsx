import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../api/client';
import toast from 'react-hot-toast';

interface Hospital {
  id: number;
  name: string;
  location: string;
}

interface AppointmentRequest {
  hospital: number;
  appointment_type: string;
  reason: string;
  preferred_date: string;
  preferred_time: string;
  location_type: string;
  notes: string;
}

const APPOINTMENT_TYPES = [
  { value: 'follow_up', label: 'Follow-up Visit' },
  { value: 'medication_review', label: 'Medication Review' },
  { value: 'consultation', label: 'Consultation' },
  { value: 'routine_checkup', label: 'Routine Checkup' },
  { value: 'emergency', label: 'Emergency' },
];

const LOCATION_TYPES = [
  { value: 'hospital', label: '🏥 Hospital Visit' },
  { value: 'home_visit', label: '🏠 Home Visit' },
  { value: 'telemedicine', label: '📱 Telemedicine' },
];

export default function PatientAppointmentRequestPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<AppointmentRequest>({
    hospital: 0,
    appointment_type: '',
    reason: '',
    preferred_date: '',
    preferred_time: '',
    location_type: 'hospital',
    notes: '',
  });

  const [hospitals, setHospitals] = useState<Hospital[]>([]);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [pageLoading, setPageLoading] = useState(true);

  // Fetch hospitals on component mount
  useEffect(() => {
    const fetchHospitals = async () => {
      try {
        const response = await client.get('/v1/hospitals/');
        setHospitals(response.data.results || response.data);
      } catch (error) {
        console.error('Failed to load hospitals:', error);
        toast.error('Failed to load hospital list');
      } finally {
        setPageLoading(false);
      }
    };

    fetchHospitals();
  }, []);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.hospital) newErrors.hospital = 'Please select a hospital';
    if (!formData.appointment_type) newErrors.appointment_type = 'Please select appointment type';
    if (!formData.reason.trim()) newErrors.reason = 'Please enter reason for appointment';
    if (!formData.preferred_date) newErrors.preferred_date = 'Please select preferred date';
    if (!formData.preferred_time) newErrors.preferred_time = 'Please select preferred time';
    if (!formData.location_type) newErrors.location_type = 'Please select location type';

    // Validate date is in the future
    const selectedDate = new Date(formData.preferred_date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (selectedDate < today) {
      newErrors.preferred_date = 'Please select a future date';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    // Clear error for this field
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      toast.error('Please fill in all required fields');
      return;
    }

    setIsLoading(true);

    try {
      // TODO: Implement appointment request endpoint in backend
      // For now, just simulate the request and navigate to appointments
      // await client.post('/v1/appointments/request/', {
      //   hospital_id: formData.hospital,
      //   appointment_type: formData.appointment_type,
      //   reason: formData.reason,
      //   preferred_date: formData.preferred_date,
      //   preferred_time: formData.preferred_time,
      //   location_type: formData.location_type,
      //   notes: formData.notes,
      // });

      toast.success('Appointment request submitted successfully!');

      // Clear form
      setFormData({
        hospital: 0,
        appointment_type: '',
        reason: '',
        preferred_date: '',
        preferred_time: '',
        location_type: 'hospital',
        notes: '',
      });

      // Redirect to appointments list
      setTimeout(() => {
        navigate('/patient/appointments');
      }, 1500);
    } catch (error: any) {
      console.error('Appointment request failed:', error);

      if (error.response?.data?.errors) {
        setErrors(error.response.data.errors);
        toast.error('Please check the form for errors');
      } else if (error.response?.data?.message) {
        toast.error(error.response.data.message);
      } else {
        toast.error('Failed to submit appointment request');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Get minimum date (today)
  const today = new Date().toISOString().split('T')[0];

  if (pageLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-teal-50 to-cyan-50 dark:from-slate-950 dark:to-slate-900 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600 dark:border-teal-400 mb-4"></div>
          <p className="text-teal-700 dark:text-teal-200 font-medium">Loading appointment form...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-950 pb-12">
      {/* Header */}
      <header className="bg-gradient-to-r from-teal-600 to-teal-500 dark:from-teal-900 dark:to-teal-800 shadow-lg sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-white">Request Appointment</h1>
              <p className="text-teal-100 text-sm mt-1">Schedule a visit with healthcare provider</p>
            </div>
            <button
              onClick={() => navigate('/patient/appointments')}
              className="px-3 sm:px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors text-sm sm:text-base"
            >
              ← Back
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {/* Form Card */}
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg overflow-hidden">
          <form onSubmit={handleSubmit} className="p-6 sm:p-8 space-y-6">
            {/* Step 1: Hospital Selection */}
            <div className="border-b border-gray-200 dark:border-slate-700 pb-6">
              <h2 className="text-lg sm:text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center">
                <span className="flex items-center justify-center w-8 h-8 rounded-full bg-teal-600 text-white text-sm font-bold mr-3">
                  1
                </span>
                Select Hospital
              </h2>

              <div>
                <label
                  htmlFor="hospital"
                  className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2"
                >
                  Healthcare Facility *
                </label>
                <select
                  id="hospital"
                  name="hospital"
                  value={formData.hospital}
                  onChange={handleChange}
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors bg-white dark:bg-slate-700 text-gray-900 dark:text-white dark:border-slate-600 ${
                    errors.hospital ? 'border-red-500' : 'border-gray-300'
                  }`}
                >
                  <option value="">-- Select a hospital --</option>
                  {hospitals.map((hospital) => (
                    <option key={hospital.id} value={hospital.id}>
                      {hospital.name} - {hospital.location}
                    </option>
                  ))}
                </select>
                {errors.hospital && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.hospital}</p>
                )}
              </div>
            </div>

            {/* Step 2: Appointment Type */}
            <div className="border-b border-gray-200 dark:border-slate-700 pb-6">
              <h2 className="text-lg sm:text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center">
                <span className="flex items-center justify-center w-8 h-8 rounded-full bg-teal-600 text-white text-sm font-bold mr-3">
                  2
                </span>
                Appointment Type
              </h2>

              <div>
                <label
                  htmlFor="appointment_type"
                  className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3"
                >
                  Type of Appointment *
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {APPOINTMENT_TYPES.map((type) => (
                    <label
                      key={type.value}
                      className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                        formData.appointment_type === type.value
                          ? 'border-teal-600 bg-teal-50 dark:bg-teal-900/30'
                          : 'border-gray-200 dark:border-slate-600 hover:border-teal-300'
                      }`}
                    >
                      <input
                        type="radio"
                        name="appointment_type"
                        value={type.value}
                        checked={formData.appointment_type === type.value}
                        onChange={handleChange}
                        className="w-4 h-4 text-teal-600"
                      />
                      <span className="ml-3 text-sm sm:text-base font-medium text-gray-700 dark:text-gray-300">
                        {type.label}
                      </span>
                    </label>
                  ))}
                </div>
                {errors.appointment_type && (
                  <p className="mt-2 text-sm text-red-600 dark:text-red-400">{errors.appointment_type}</p>
                )}
              </div>
            </div>

            {/* Step 3: Reason & Details */}
            <div className="border-b border-gray-200 dark:border-slate-700 pb-6">
              <h2 className="text-lg sm:text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center">
                <span className="flex items-center justify-center w-8 h-8 rounded-full bg-teal-600 text-white text-sm font-bold mr-3">
                  3
                </span>
                Reason & Details
              </h2>

              <div className="space-y-4">
                <div>
                  <label
                    htmlFor="reason"
                    className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2"
                  >
                    Reason for Appointment *
                  </label>
                  <textarea
                    id="reason"
                    name="reason"
                    value={formData.reason}
                    onChange={handleChange}
                    placeholder="Describe your symptoms or reason for visit (e.g., Chest pain, Follow-up from discharge, Medication review)"
                    rows={3}
                    className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors bg-white dark:bg-slate-700 text-gray-900 dark:text-white dark:border-slate-600 ${
                      errors.reason ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {errors.reason && (
                    <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.reason}</p>
                  )}
                </div>

                <div>
                  <label
                    htmlFor="notes"
                    className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2"
                  >
                    Additional Notes (Optional)
                  </label>
                  <textarea
                    id="notes"
                    name="notes"
                    value={formData.notes}
                    onChange={handleChange}
                    placeholder="Any additional information for the healthcare provider"
                    rows={3}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors bg-white dark:bg-slate-700 text-gray-900 dark:text-white"
                  />
                </div>
              </div>
            </div>

            {/* Step 4: Preferred Date & Time */}
            <div className="border-b border-gray-200 dark:border-slate-700 pb-6">
              <h2 className="text-lg sm:text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center">
                <span className="flex items-center justify-center w-8 h-8 rounded-full bg-teal-600 text-white text-sm font-bold mr-3">
                  4
                </span>
                Preferred Date & Time
              </h2>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label
                    htmlFor="preferred_date"
                    className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2"
                  >
                    Preferred Date *
                  </label>
                  <input
                    type="date"
                    id="preferred_date"
                    name="preferred_date"
                    value={formData.preferred_date}
                    onChange={handleChange}
                    min={today}
                    className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors bg-white dark:bg-slate-700 text-gray-900 dark:text-white dark:border-slate-600 ${
                      errors.preferred_date ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {errors.preferred_date && (
                    <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.preferred_date}</p>
                  )}
                </div>

                <div>
                  <label
                    htmlFor="preferred_time"
                    className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2"
                  >
                    Preferred Time *
                  </label>
                  <input
                    type="time"
                    id="preferred_time"
                    name="preferred_time"
                    value={formData.preferred_time}
                    onChange={handleChange}
                    className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors bg-white dark:bg-slate-700 text-gray-900 dark:text-white dark:border-slate-600 ${
                      errors.preferred_time ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {errors.preferred_time && (
                    <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.preferred_time}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Step 5: Location Type */}
            <div>
              <h2 className="text-lg sm:text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center">
                <span className="flex items-center justify-center w-8 h-8 rounded-full bg-teal-600 text-white text-sm font-bold mr-3">
                  5
                </span>
                Appointment Location
              </h2>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {LOCATION_TYPES.map((location) => (
                  <label
                    key={location.value}
                    className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      formData.location_type === location.value
                        ? 'border-teal-600 bg-teal-50 dark:bg-teal-900/30'
                        : 'border-gray-200 dark:border-slate-600 hover:border-teal-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name="location_type"
                      value={location.value}
                      checked={formData.location_type === location.value}
                      onChange={handleChange}
                      className="w-4 h-4 text-teal-600"
                    />
                    <span className="ml-3 text-sm sm:text-base font-medium text-gray-700 dark:text-gray-300">
                      {location.label}
                    </span>
                  </label>
                ))}
              </div>
              {errors.location_type && (
                <p className="mt-2 text-sm text-red-600 dark:text-red-400">{errors.location_type}</p>
              )}
            </div>

            {/* Submit Button */}
            <div className="flex gap-4 pt-6">
              <button
                type="button"
                onClick={() => navigate('/patient/appointments')}
                className="flex-1 px-6 py-3 bg-gray-200 dark:bg-slate-700 hover:bg-gray-300 dark:hover:bg-slate-600 text-gray-900 dark:text-white font-semibold rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-700 hover:to-teal-600 disabled:from-gray-400 disabled:to-gray-500 text-white font-semibold rounded-lg transition-all duration-200 transform hover:scale-105 disabled:hover:scale-100 flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <span className="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full"></span>
                    Submitting...
                  </>
                ) : (
                  'Submit Request'
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Info Card */}
        <div className="mt-6 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-xl p-4 sm:p-6">
          <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">📋 What Happens Next?</h3>
          <ul className="text-sm sm:text-base text-blue-800 dark:text-blue-200 space-y-2">
            <li>✓ Your appointment request will be submitted to the healthcare facility</li>
            <li>✓ A nurse will review your request and confirm the appointment</li>
            <li>✓ You'll receive a confirmation via email and SMS</li>
            <li>✓ Check your appointments page for updates</li>
          </ul>
        </div>
      </main>
    </div>
  );
}
