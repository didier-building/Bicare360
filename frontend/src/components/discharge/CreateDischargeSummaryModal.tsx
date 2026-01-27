import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { XMarkIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { patientsAPI } from '../../api/patients';
import { dischargeAPI } from '../../api/discharge';
import type { DischargeSummaryCreateData } from '../../api/discharge';

interface CreateDischargeSummaryModalProps {
  onClose: () => void;
}

interface Hospital {
  id: number;
  name: string;
  hospital_type: string;
}

const CreateDischargeSummaryModal: React.FC<CreateDischargeSummaryModalProps> = ({ onClose }) => {
  const queryClient = useQueryClient();
  
  const [formData, setFormData] = useState({
    patient: '',
    hospital: '',
    admission_date: '',
    discharge_date: new Date().toISOString().split('T')[0],
    primary_diagnosis: '',
    secondary_diagnoses: '',
    icd10_primary: '',
    icd10_secondary: '',
    procedures_performed: '',
    treatment_summary: '',
    discharge_condition: 'improved',
    discharge_instructions: '',
    discharge_instructions_kinyarwanda: '',
    diet_instructions: '',
    activity_restrictions: '',
    follow_up_required: true,
    follow_up_timeframe: '',
    follow_up_with: '',
    risk_level: 'low',
    risk_factors: '',
    warning_signs: '',
    warning_signs_kinyarwanda: '',
    attending_physician: '',
    discharge_nurse: '',
    additional_notes: '',
  });

  // Fetch patients
  const { data: patientsData } = useQuery({
    queryKey: ['patients'],
    queryFn: () => patientsAPI.getPatients({}),
  });

  // Fetch hospitals from API
  const { data: hospitalsData } = useQuery<{ results: Hospital[] }>({
    queryKey: ['hospitals'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8000/api/v1/hospitals/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch hospitals');
      return response.json();
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: DischargeSummaryCreateData) => dischargeAPI.createDischargeSummary(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dischargeSummaries'] });
      toast.success('Discharge summary created successfully!');
      onClose();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || error.message || 'Failed to create discharge summary');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!formData.patient || !formData.hospital || !formData.admission_date) {
      toast.error('Please fill in all required fields');
      return;
    }

    if (!formData.primary_diagnosis || !formData.treatment_summary) {
      toast.error('Primary diagnosis and treatment summary are required');
      return;
    }

    if (!formData.discharge_instructions || !formData.attending_physician) {
      toast.error('Discharge instructions and attending physician are required');
      return;
    }

    // Convert string IDs to numbers
    const submitData: DischargeSummaryCreateData = {
      ...formData,
      patient: Number(formData.patient),
      hospital: Number(formData.hospital),
    };

    createMutation.mutate(submitData);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
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
        <div className="relative w-full max-w-4xl bg-white dark:bg-gray-800 rounded-lg shadow-xl">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Create Discharge Summary
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
              {/* Basic Information */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  Basic Information
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Patient <span className="text-red-500">*</span>
                    </label>
                    <select
                      name="patient"
                      value={formData.patient}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                    >
                      <option value="">Select Patient</option>
                      {patientsData?.results.map((patient: any) => (
                        <option key={patient.id} value={patient.id}>
                          {patient.first_name} {patient.last_name} - {patient.medical_record_number}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Hospital <span className="text-red-500">*</span>
                    </label>
                    <select
                      name="hospital"
                      value={formData.hospital}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                    >
                      <option value="">Select Hospital</option>
                      {hospitalsData?.results.map((hospital) => (
                        <option key={hospital.id} value={hospital.id}>
                          {hospital.name} ({hospital.hospital_type})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Admission Date <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="date"
                      name="admission_date"
                      value={formData.admission_date}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Discharge Date <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="date"
                      name="discharge_date"
                      value={formData.discharge_date}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                    />
                  </div>
                </div>
              </section>

              {/* Diagnosis */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  Diagnosis
                </h3>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Primary Diagnosis <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        name="primary_diagnosis"
                        value={formData.primary_diagnosis}
                        onChange={handleInputChange}
                        required
                        placeholder="e.g., Pneumonia"
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Primary ICD-10 Code
                      </label>
                      <input
                        type="text"
                        name="icd10_primary"
                        value={formData.icd10_primary}
                        onChange={handleInputChange}
                        placeholder="e.g., J18.9"
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Secondary Diagnoses
                    </label>
                    <textarea
                      name="secondary_diagnoses"
                      value={formData.secondary_diagnoses}
                      onChange={handleInputChange}
                      rows={2}
                      placeholder="Other diagnoses, one per line"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Secondary ICD-10 Codes
                    </label>
                    <input
                      type="text"
                      name="icd10_secondary"
                      value={formData.icd10_secondary}
                      onChange={handleInputChange}
                      placeholder="e.g., E11.9, I10"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                    />
                  </div>
                </div>
              </section>

              {/* Procedures Performed */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  Procedures Performed
                </h3>
                <textarea
                  name="procedures_performed"
                  value={formData.procedures_performed}
                  onChange={handleInputChange}
                  rows={3}
                  placeholder="List any surgeries, procedures, or interventions performed"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                />
              </section>

              {/* Risk Assessment */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  Risk Assessment & Discharge Condition
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Risk Level <span className="text-red-500">*</span>
                    </label>
                    <select
                      name="risk_level"
                      value={formData.risk_level}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                    >
                      <option value="low">Low Risk</option>
                      <option value="medium">Medium Risk</option>
                      <option value="high">High Risk</option>
                      <option value="critical">Critical Risk</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Discharge Condition <span className="text-red-500">*</span>
                    </label>
                    <select
                      name="discharge_condition"
                      value={formData.discharge_condition}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                    >
                      <option value="improved">Improved</option>
                      <option value="stable">Stable</option>
                      <option value="unchanged">Unchanged</option>
                      <option value="deteriorated">Deteriorated</option>
                    </select>
                  </div>

                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Risk Factors
                    </label>
                    <textarea
                      name="risk_factors"
                      value={formData.risk_factors}
                      onChange={handleInputChange}
                      rows={2}
                      placeholder="Specific risk factors (e.g., social determinants, compliance concerns)"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                    />
                  </div>
                </div>
              </section>

              {/* Treatment Summary */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  Treatment Summary <span className="text-red-500">*</span>
                </h3>
                <textarea
                  name="treatment_summary"
                  value={formData.treatment_summary}
                  onChange={handleInputChange}
                  required
                  rows={4}
                  placeholder="Overview of treatment provided during hospital stay"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                />
              </section>

              {/* Discharge Instructions - Bilingual */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  Discharge Instructions (Bilingual)
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Discharge Instructions (English) <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      name="discharge_instructions"
                      value={formData.discharge_instructions}
                      onChange={handleInputChange}
                      required
                      rows={3}
                      placeholder="Instructions for the patient to follow at home"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Amabwiriza yo gusubira mu rugo (Kinyarwanda)
                    </label>
                    <textarea
                      name="discharge_instructions_kinyarwanda"
                      value={formData.discharge_instructions_kinyarwanda}
                      onChange={handleInputChange}
                      rows={3}
                      placeholder="Amabwiriza umurwayi akurikiza mu rugo"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                    />
                  </div>
                </div>
              </section>

              {/* Follow-up Care */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  Follow-up Care
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      name="follow_up_required"
                      checked={formData.follow_up_required}
                      onChange={handleInputChange}
                      className="h-4 w-4 text-teal-600 focus:ring-teal-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                      Follow-up Required
                    </label>
                  </div>

                  {formData.follow_up_required && (
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Follow-up Timeframe <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          name="follow_up_timeframe"
                          value={formData.follow_up_timeframe}
                          onChange={handleInputChange}
                          placeholder="e.g., 1 week, 2 weeks, 1 month"
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Follow-up With
                        </label>
                        <input
                          type="text"
                          name="follow_up_with"
                          value={formData.follow_up_with}
                          onChange={handleInputChange}
                          placeholder="e.g., Cardiology, Dr. Smith"
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                        />
                      </div>
                    </div>
                  )}
                </div>
              </section>

              {/* Diet & Activity */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  Diet & Activity Instructions
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Diet Instructions
                    </label>
                    <textarea
                      name="diet_instructions"
                      value={formData.diet_instructions}
                      onChange={handleInputChange}
                      rows={3}
                      placeholder="Special dietary requirements or restrictions"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Activity Restrictions
                    </label>
                    <textarea
                      name="activity_restrictions"
                      value={formData.activity_restrictions}
                      onChange={handleInputChange}
                      rows={3}
                      placeholder="Physical activity limitations"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                    />
                  </div>
                </div>
              </section>

              {/* Warning Signs - Bilingual */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  Warning Signs (Bilingual)
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Warning Signs (English)
                    </label>
                    <textarea
                      name="warning_signs"
                      value={formData.warning_signs}
                      onChange={handleInputChange}
                      rows={3}
                      placeholder="Symptoms that require immediate medical attention"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Ibimenyetso by'akaga (Kinyarwanda)
                    </label>
                    <textarea
                      name="warning_signs_kinyarwanda"
                      value={formData.warning_signs_kinyarwanda}
                      onChange={handleInputChange}
                      rows={3}
                      placeholder="Ibimenyetso bisaba kwita vuba ku burwayi"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                    />
                  </div>
                </div>
              </section>

              {/* Provider Information */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  Provider Information
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Attending Physician <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      name="attending_physician"
                      value={formData.attending_physician}
                      onChange={handleInputChange}
                      required
                      placeholder="Dr. Name"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Discharge Nurse
                    </label>
                    <input
                      type="text"
                      name="discharge_nurse"
                      value={formData.discharge_nurse}
                      onChange={handleInputChange}
                      placeholder="Nurse Name"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                    />
                  </div>
                </div>
              </section>

              {/* Additional Notes */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  Additional Notes
                </h3>
                <textarea
                  name="additional_notes"
                  value={formData.additional_notes}
                  onChange={handleInputChange}
                  rows={3}
                  placeholder="Any other relevant information"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-gray-100"
                />
              </section>
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
                className="px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 font-medium disabled:opacity-50 shadow-md hover:shadow-lg transition-all"
              >
                {createMutation.isPending ? 'Creating...' : 'Create Discharge Summary'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CreateDischargeSummaryModal;
