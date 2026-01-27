import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { medicationsAPI } from '../../api/medications';
import { patientsAPI } from '../../api/patients';
import toast from 'react-hot-toast';

interface CreatePrescriptionModalProps {
  onClose: () => void;
  preselectedMedicationId?: number;
}

const CreatePrescriptionModal: React.FC<CreatePrescriptionModalProps> = ({ 
  onClose, 
  preselectedMedicationId 
}) => {
  const queryClient = useQueryClient();
  
  const [formData, setFormData] = useState({
    patient: '',
    medication: preselectedMedicationId?.toString() || '',
    dosage: '',
    frequency: '',
    frequency_times_per_day: '1',
    route: 'oral',
    duration_days: '',
    quantity: '',
    instructions: '',
    instructions_kinyarwanda: '',
    start_date: new Date().toISOString().split('T')[0],
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Fetch patients
  const { data: patientsData } = useQuery({
    queryKey: ['patients'],
    queryFn: () => patientsAPI.getPatients({}),
  });

  // Fetch medications
  const { data: medicationsData } = useQuery({
    queryKey: ['activeMedications'],
    queryFn: () => medicationsAPI.getMedications({ is_active: true }),
  });

  // Create prescription mutation
  const createPrescription = useMutation({
    mutationFn: (data: any) => medicationsAPI.createPrescription(data),
    onSuccess: () => {
      toast.success('Prescription created successfully!');
      queryClient.invalidateQueries({ queryKey: ['currentPrescriptions'] });
      queryClient.invalidateQueries({ queryKey: ['prescriptions'] });
      onClose();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to create prescription');
      console.error('Error creating prescription:', error);
    },
  });

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.patient) newErrors.patient = 'Patient is required';
    if (!formData.medication) newErrors.medication = 'Medication is required';
    if (!formData.dosage) newErrors.dosage = 'Dosage is required';
    if (!formData.frequency) newErrors.frequency = 'Frequency is required';
    if (!formData.frequency_times_per_day || parseInt(formData.frequency_times_per_day) < 1) {
      newErrors.frequency_times_per_day = 'Must be at least 1';
    }
    if (!formData.duration_days || parseInt(formData.duration_days) < 1) {
      newErrors.duration_days = 'Must be at least 1 day';
    }
    if (!formData.start_date) newErrors.start_date = 'Start date is required';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      toast.error('Please fill in all required fields');
      return;
    }

    // Calculate end_date
    const startDate = new Date(formData.start_date);
    const endDate = new Date(startDate);
    endDate.setDate(endDate.getDate() + parseInt(formData.duration_days));

    const prescriptionData = {
      patient: parseInt(formData.patient),
      medication: parseInt(formData.medication),
      dosage: formData.dosage,
      frequency: formData.frequency,
      frequency_times_per_day: parseInt(formData.frequency_times_per_day),
      route: formData.route,
      duration_days: parseInt(formData.duration_days),
      quantity: formData.quantity ? parseInt(formData.quantity) : undefined,
      instructions: formData.instructions || undefined,
      instructions_kinyarwanda: formData.instructions_kinyarwanda || undefined,
      start_date: formData.start_date,
      end_date: endDate.toISOString().split('T')[0],
      is_active: true,
    };

    createPrescription.mutate(prescriptionData);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative w-full max-w-3xl bg-white dark:bg-gray-800 rounded-lg shadow-xl">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Create New Prescription
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
            >
              <XMarkIcon className="w-6 h-6" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 max-h-[70vh] overflow-y-auto">
            <div className="space-y-6">
              {/* Patient Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Patient <span className="text-red-500">*</span>
                </label>
                <select
                  name="patient"
                  value={formData.patient}
                  onChange={handleChange}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 ${
                    errors.patient ? 'border-red-500' : 'border-gray-300'
                  }`}
                >
                  <option value="">Select a patient</option>
                  {patientsData?.results.map((patient: any) => (
                    <option key={patient.id} value={patient.id}>
                      {patient.first_name} {patient.last_name} - {patient.medical_record_number}
                    </option>
                  ))}
                </select>
                {errors.patient && <p className="mt-1 text-sm text-red-500">{errors.patient}</p>}
              </div>

              {/* Medication Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Medication <span className="text-red-500">*</span>
                </label>
                <select
                  name="medication"
                  value={formData.medication}
                  onChange={handleChange}
                  disabled={!!preselectedMedicationId}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 ${
                    errors.medication ? 'border-red-500' : 'border-gray-300'
                  } ${preselectedMedicationId ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <option value="">Select a medication</option>
                  {medicationsData?.results.map((med: any) => (
                    <option key={med.id} value={med.id}>
                      {med.name} - {med.strength} ({med.dosage_form})
                    </option>
                  ))}
                </select>
                {errors.medication && <p className="mt-1 text-sm text-red-500">{errors.medication}</p>}
              </div>

              {/* Dosage & Frequency Row */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Dosage <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    name="dosage"
                    value={formData.dosage}
                    onChange={handleChange}
                    placeholder="e.g., 500mg, 2 tablets"
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 ${
                      errors.dosage ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {errors.dosage && <p className="mt-1 text-sm text-red-500">{errors.dosage}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Times Per Day <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    name="frequency_times_per_day"
                    value={formData.frequency_times_per_day}
                    onChange={handleChange}
                    min="1"
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 ${
                      errors.frequency_times_per_day ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {errors.frequency_times_per_day && <p className="mt-1 text-sm text-red-500">{errors.frequency_times_per_day}</p>}
                </div>
              </div>

              {/* Frequency Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Frequency Description <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="frequency"
                  value={formData.frequency}
                  onChange={handleChange}
                  placeholder="e.g., Three times daily, Every 8 hours"
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 ${
                    errors.frequency ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {errors.frequency && <p className="mt-1 text-sm text-red-500">{errors.frequency}</p>}
              </div>

              {/* Route & Duration Row */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Route <span className="text-red-500">*</span>
                  </label>
                  <select
                    name="route"
                    value={formData.route}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                  >
                    <option value="oral">Oral</option>
                    <option value="topical">Topical</option>
                    <option value="intravenous">Intravenous (IV)</option>
                    <option value="intramuscular">Intramuscular (IM)</option>
                    <option value="subcutaneous">Subcutaneous</option>
                    <option value="inhalation">Inhalation</option>
                    <option value="rectal">Rectal</option>
                    <option value="transdermal">Transdermal</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Duration (days) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    name="duration_days"
                    value={formData.duration_days}
                    onChange={handleChange}
                    min="1"
                    placeholder="e.g., 7"
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 ${
                      errors.duration_days ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {errors.duration_days && <p className="mt-1 text-sm text-red-500">{errors.duration_days}</p>}
                </div>
              </div>

              {/* Start Date & Quantity Row */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Start Date <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="date"
                    name="start_date"
                    value={formData.start_date}
                    onChange={handleChange}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 ${
                      errors.start_date ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {errors.start_date && <p className="mt-1 text-sm text-red-500">{errors.start_date}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Total Quantity (optional)
                  </label>
                  <input
                    type="number"
                    name="quantity"
                    value={formData.quantity}
                    onChange={handleChange}
                    min="1"
                    placeholder="e.g., 21 tablets"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                  />
                </div>
              </div>

              {/* Instructions - English */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Instructions (English)
                </label>
                <textarea
                  name="instructions"
                  value={formData.instructions}
                  onChange={handleChange}
                  rows={3}
                  placeholder="e.g., Take with food, Avoid alcohol"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                />
              </div>

              {/* Instructions - Kinyarwanda */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Instructions (Kinyarwanda)
                </label>
                <textarea
                  name="instructions_kinyarwanda"
                  value={formData.instructions_kinyarwanda}
                  onChange={handleChange}
                  rows={3}
                  placeholder="e.g., Nywa ufite ibiryo"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                />
              </div>
            </div>
          </form>

          {/* Footer */}
          <div className="flex justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 font-medium"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={createPrescription.isPending}
              className="px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 font-medium disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg transition-all"
            >
              {createPrescription.isPending ? 'Creating...' : 'Create Prescription'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreatePrescriptionModal;
