import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { medicationsAPI } from '../../api/medications';
import { patientsAPI } from '../../api/patients';
import toast from 'react-hot-toast';

interface CreatePrescriptionModalProps {
  onClose: () => void;
}

const ROUTE_OPTIONS = [
  { value: 'oral', label: 'Oral' },
  { value: 'topical', label: 'Topical' },
  { value: 'intravenous', label: 'Intravenous (IV)' },
  { value: 'intramuscular', label: 'Intramuscular (IM)' },
  { value: 'subcutaneous', label: 'Subcutaneous' },
  { value: 'inhalation', label: 'Inhalation' },
  { value: 'rectal', label: 'Rectal' },
  { value: 'transdermal', label: 'Transdermal' },
];

const CreatePrescriptionModal: React.FC<CreatePrescriptionModalProps> = ({ onClose }) => {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    patient: '',
    medication: '',
    dosage: '',
    frequency: '',
    frequency_times_per_day: 1,
    route: 'oral',
    duration_days: 7,
    instructions: '',
    instructions_kinyarwanda: '',
    start_date: new Date().toISOString().split('T')[0],
  });

  // Fetch patients
  const { data: patientsData, isLoading: loadingPatients } = useQuery({
    queryKey: ['patients'],
    queryFn: () => patientsAPI.getPatients({ limit: 100 }),
  });

  // Fetch active medications
  const { data: medicationsData, isLoading: loadingMedications } = useQuery({
    queryKey: ['activeMedications'],
    queryFn: () => medicationsAPI.getMedications({ is_active: true }),
  });

  // Create prescription mutation
  const createMutation = useMutation({
    mutationFn: (data: any) => medicationsAPI.createPrescription(data),
    onSuccess: () => {
      toast.success('Prescription created successfully!');
      queryClient.invalidateQueries({ queryKey: ['currentPrescriptions'] });
      queryClient.invalidateQueries({ queryKey: ['prescriptions'] });
      onClose();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to create prescription');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!formData.patient || !formData.medication) {
      toast.error('Please select patient and medication');
      return;
    }

    if (!formData.dosage || !formData.frequency) {
      toast.error('Please enter dosage and frequency');
      return;
    }

    // Calculate end date
    const startDate = new Date(formData.start_date);
    const endDate = new Date(startDate);
    endDate.setDate(endDate.getDate() + formData.duration_days);

    const prescriptionData = {
      ...formData,
      patient: parseInt(formData.patient),
      medication: parseInt(formData.medication),
      end_date: endDate.toISOString().split('T')[0],
      is_active: true,
    };

    createMutation.mutate(prescriptionData);
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
          <form onSubmit={handleSubmit} className="p-6">
            <div className="space-y-6">
              {/* Patient Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Patient <span className="text-red-500">*</span>
                </label>
                <select
                  value={formData.patient}
                  onChange={(e) => setFormData({ ...formData, patient: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                  required
                  disabled={loadingPatients}
                >
                  <option value="">Select Patient</option>
                  {patientsData?.results.map((patient: any) => (
                    <option key={patient.id} value={patient.id}>
                      {patient.first_name} {patient.last_name} - {patient.medical_record_number}
                    </option>
                  ))}
                </select>
              </div>

              {/* Medication Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Medication <span className="text-red-500">*</span>
                </label>
                <select
                  value={formData.medication}
                  onChange={(e) => setFormData({ ...formData, medication: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                  required
                  disabled={loadingMedications}
                >
                  <option value="">Select Medication</option>
                  {medicationsData?.results.map((med: any) => (
                    <option key={med.id} value={med.id}>
                      {med.name} - {med.strength} ({med.dosage_form})
                    </option>
                  ))}
                </select>
              </div>

              {/* Dosage and Frequency Row */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Dosage <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.dosage}
                    onChange={(e) => setFormData({ ...formData, dosage: e.target.value })}
                    placeholder="e.g., 500mg, 2 tablets"
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Frequency <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.frequency}
                    onChange={(e) => setFormData({ ...formData, frequency: e.target.value })}
                    placeholder="e.g., Three times daily"
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                    required
                  />
                </div>
              </div>

              {/* Times Per Day and Route Row */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Times Per Day <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="24"
                    value={formData.frequency_times_per_day}
                    onChange={(e) => setFormData({ ...formData, frequency_times_per_day: parseInt(e.target.value) })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Route <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={formData.route}
                    onChange={(e) => setFormData({ ...formData, route: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                    required
                  >
                    {ROUTE_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Duration and Start Date Row */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Duration (Days) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={formData.duration_days}
                    onChange={(e) => setFormData({ ...formData, duration_days: parseInt(e.target.value) })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Start Date <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                    required
                  />
                </div>
              </div>

              {/* Instructions (English) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Instructions (English)
                </label>
                <textarea
                  value={formData.instructions}
                  onChange={(e) => setFormData({ ...formData, instructions: e.target.value })}
                  placeholder="e.g., Take with food, avoid alcohol"
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                />
              </div>

              {/* Instructions (Kinyarwanda) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Instructions (Kinyarwanda)
                </label>
                <textarea
                  value={formData.instructions_kinyarwanda}
                  onChange={(e) => setFormData({ ...formData, instructions_kinyarwanda: e.target.value })}
                  placeholder="e.g., Nywa ufite ibiryo"
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                />
              </div>
            </div>

            {/* Footer */}
            <div className="flex justify-end gap-3 mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 font-medium"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="px-6 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 font-medium disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg transition-all"
              >
                {createMutation.isPending ? 'Creating...' : 'Create Prescription'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CreatePrescriptionModal;
