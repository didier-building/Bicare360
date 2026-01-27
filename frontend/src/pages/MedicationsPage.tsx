import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { medicationsAPI } from '../api/medications';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { PlusIcon, MagnifyingGlassIcon, BeakerIcon } from '@heroicons/react/24/outline';
import MedicationDetailModal from '../components/medications/MedicationDetailModal';
import CreatePrescriptionModal from '../components/prescriptions/CreatePrescriptionModal';

const MedicationsPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [dosageFilter, setDosageFilter] = useState('');
  const [prescriptionFilter, setPrescriptionFilter] = useState('');
  const [selectedMedication, setSelectedMedication] = useState<any>(null);
  const [showCreatePrescription, setShowCreatePrescription] = useState(false);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['medications', searchQuery, dosageFilter, prescriptionFilter],
    queryFn: async () => {
      console.log('🔵 Fetching medications with params:', {
        search: searchQuery || undefined,
        dosage_form: dosageFilter || undefined,
        requires_prescription: prescriptionFilter ? prescriptionFilter === 'true' : undefined,
      });
      const result = await medicationsAPI.getMedications({
        search: searchQuery || undefined,
        dosage_form: dosageFilter || undefined,
        requires_prescription: prescriptionFilter ? prescriptionFilter === 'true' : undefined,
      });
      console.log('✅ Medications fetched:', result);
      return result;
    },
  });

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
        <p className="text-red-600 dark:text-red-400 mb-2">Failed to load medications</p>
        <button
          onClick={() => refetch()}
          className="mt-4 px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 shadow-md hover:shadow-lg"
        >
          Retry
        </button>
      </div>
    );
  }

  const medications = data?.results || [];

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
          Medication Management
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          View and manage the hospital's medication catalog. Search medications, check availability, 
          and review prescription requirements before administering to patients.
        </p>
      </div>

      {/* Purpose Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <div className="flex items-center mb-2">
            <BeakerIcon className="h-6 w-6 text-blue-600 dark:text-blue-400 mr-2" />
            <h3 className="font-semibold text-blue-900 dark:text-blue-100">Quick Reference</h3>
          </div>
          <p className="text-sm text-blue-700 dark:text-blue-300">
            Instantly look up medications by name or type before administering to verify dosage forms and strength.
          </p>
        </div>

        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
          <div className="flex items-center mb-2">
            <svg className="h-6 w-6 text-green-600 dark:text-green-400 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="font-semibold text-green-900 dark:text-green-100">Prescription Check</h3>
          </div>
          <p className="text-sm text-green-700 dark:text-green-300">
            Verify which medications require prescriptions to ensure proper authorization before dispensing.
          </p>
        </div>

        <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
          <div className="flex items-center mb-2">
            <svg className="h-6 w-6 text-purple-600 dark:text-purple-400 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <h3 className="font-semibold text-purple-900 dark:text-purple-100">Inventory Awareness</h3>
          </div>
          <p className="text-sm text-purple-700 dark:text-purple-300">
            View available medications catalog to coordinate with pharmacy for patient care needs.
          </p>
        </div>
      </div>

      {/* Stats Summary */}
      {data && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
            <p className="text-sm text-gray-600 dark:text-gray-400">Total Medications</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{data.count}</p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
            <p className="text-sm text-gray-600 dark:text-gray-400">Prescription Required</p>
            <p className="text-2xl font-bold text-red-600 dark:text-red-400">
              {medications.filter((m: any) => m.requires_prescription).length}
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
            <p className="text-sm text-gray-600 dark:text-gray-400">OTC Available</p>
            <p className="text-2xl font-bold text-green-600 dark:text-green-400">
              {medications.filter((m: any) => !m.requires_prescription).length}
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
            <p className="text-sm text-gray-600 dark:text-gray-400">Active Medications</p>
            <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {medications.filter((m: any) => m.is_active).length}
            </p>
          </div>
        </div>
      )}

      {/* Action Button */}
      <div className="mb-6 flex justify-end">
        <button
          onClick={() => setShowCreatePrescription(true)}
          className="flex items-center gap-2 px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 font-medium shadow-md hover:shadow-lg transition-all"
        >
          <PlusIcon className="w-5 h-5" />
          Create Prescription
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative col-span-2">
            <MagnifyingGlassIcon className="absolute left-3 top-3 w-5 h-5 text-gray-400 dark:text-gray-500" />
            <input
              type="text"
              placeholder="Search medications..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>

          {/* Dosage Form */}
          <select
            value={dosageFilter}
            onChange={(e) => setDosageFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-primary-500"
          >
            <option value="">All Forms</option>
            <option value="tablet">Tablet</option>
            <option value="capsule">Capsule</option>
            <option value="syrup">Syrup</option>
            <option value="injection">Injection</option>
            <option value="cream">Cream</option>
            <option value="inhaler">Inhaler</option>
          </select>

          {/* Prescription Required */}
          <select
            value={prescriptionFilter}
            onChange={(e) => setPrescriptionFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-primary-500"
          >
            <option value="">All Medications</option>
            <option value="true">Prescription Required</option>
            <option value="false">Over the Counter</option>
          </select>
        </div>
      </div>

      {/* Medications Grid */}
      {medications.length === 0 ? (
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow">
          <p className="text-gray-600 dark:text-gray-400 text-lg">No medications found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {medications.map((medication) => (
            <div
              key={medication.id}
              className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition-shadow p-6"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
                    {medication.name}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {medication.generic_name}
                  </p>
                </div>
                <span
                  className={`px-2 py-1 rounded-full text-xs font-semibold ${
                    medication.is_active
                      ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                      : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                  }`}
                >
                  {medication.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Form:</span>
                  <span className="font-medium text-gray-900 dark:text-gray-100 capitalize">
                    {medication.dosage_form}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Strength:</span>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    {medication.strength} {medication.unit}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Prescription:</span>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    {medication.requires_prescription ? 'Required' : 'Not Required'}
                  </span>
                </div>
              </div>

              {medication.side_effects && (
                <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    <strong>Side Effects:</strong> {medication.side_effects}
                  </p>
                </div>
              )}

              <div className="flex gap-2 mt-4">
                <button
                  onClick={() => setSelectedMedication(medication)}
                  className="flex-1 px-4 py-2 border border-teal-500 text-teal-500 dark:border-teal-400 dark:text-teal-400 rounded-lg hover:bg-aqua-50 dark:hover:bg-gray-700 font-medium transition-colors"
                >
                  View Details
                </button>
                <button
                  onClick={() => setShowCreatePrescription(true)}
                  className="flex-1 px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 font-medium transition-colors shadow-md hover:shadow-lg"
                >
                  Prescribe
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination Info */}
      {data && (
        <div className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
          Showing {medications.length} of {data.count} medication{data.count !== 1 ? 's' : ''}
        </div>
      )}

      {/* Medication Detail Modal */}
      {selectedMedication && (
        <MedicationDetailModal
          medication={selectedMedication}
          onClose={() => setSelectedMedication(null)}
        />
      )}

      {/* Create Prescription Modal */}
      {showCreatePrescription && (
        <CreatePrescriptionModal
          onClose={() => setShowCreatePrescription(false)}
        />
      )}
    </div>
  );
};

export default MedicationsPage;
