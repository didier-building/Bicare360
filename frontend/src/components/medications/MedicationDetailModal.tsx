import React from 'react';
import { XMarkIcon, BeakerIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

interface Medication {
  id: number;
  name: string;
  generic_name: string;
  dosage_form: string;
  strength: string;
  manufacturer: string;
  requires_prescription: boolean;
  description: string;
  indications: string;
  contraindications: string;
  side_effects: string;
  storage_conditions: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface MedicationDetailModalProps {
  medication: Medication;
  onClose: () => void;
}

const MedicationDetailModal: React.FC<MedicationDetailModalProps> = ({ medication, onClose }) => {
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
          <div className="flex items-start justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
                  <BeakerIcon className="w-6 h-6 text-teal-600 dark:text-teal-400" />
                </div>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {medication.name}
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  {medication.generic_name}
                </p>
                <div className="flex items-center gap-2 mt-2">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300">
                    {medication.dosage_form}
                  </span>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300">
                    {medication.strength}
                  </span>
                  {medication.requires_prescription && (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300">
                      Prescription Required
                    </span>
                  )}
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    medication.is_active 
                      ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'
                  }`}>
                    {medication.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
            >
              <XMarkIcon className="w-6 h-6" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 max-h-[70vh] overflow-y-auto">
            <div className="space-y-6">
              {/* Basic Information */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
                  Basic Information
                </h3>
                <div className="grid grid-cols-2 gap-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Manufacturer</p>
                    <p className="text-base font-medium text-gray-900 dark:text-gray-100 mt-1">
                      {medication.manufacturer || 'Not specified'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Dosage Form</p>
                    <p className="text-base font-medium text-gray-900 dark:text-gray-100 mt-1">
                      {medication.dosage_form}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Strength</p>
                    <p className="text-base font-medium text-gray-900 dark:text-gray-100 mt-1">
                      {medication.strength}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Status</p>
                    <p className="text-base font-medium text-gray-900 dark:text-gray-100 mt-1">
                      {medication.is_active ? 'Active' : 'Inactive'}
                    </p>
                  </div>
                </div>
              </section>

              {/* Description */}
              {medication.description && (
                <section>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
                    Description
                  </h3>
                  <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                    {medication.description}
                  </p>
                </section>
              )}

              {/* Indications */}
              {medication.indications && (
                <section>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
                    Indications & Usage
                  </h3>
                  <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                    <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                      {medication.indications}
                    </p>
                  </div>
                </section>
              )}

              {/* Contraindications */}
              {medication.contraindications && (
                <section>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center">
                    <ExclamationTriangleIcon className="w-5 h-5 text-red-500 mr-2" />
                    Contraindications
                  </h3>
                  <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                    <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                      {medication.contraindications}
                    </p>
                  </div>
                </section>
              )}

              {/* Side Effects */}
              {medication.side_effects && (
                <section>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
                    Possible Side Effects
                  </h3>
                  <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                    <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                      {medication.side_effects}
                    </p>
                  </div>
                </section>
              )}

              {/* Storage */}
              {medication.storage_conditions && (
                <section>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
                    Storage Conditions
                  </h3>
                  <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4">
                    <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                      {medication.storage_conditions}
                    </p>
                  </div>
                </section>
              )}

              {/* Metadata */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
                  Record Information
                </h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600 dark:text-gray-400">Created</p>
                    <p className="text-gray-900 dark:text-gray-100 mt-1">
                      {new Date(medication.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      })}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600 dark:text-gray-400">Last Updated</p>
                    <p className="text-gray-900 dark:text-gray-100 mt-1">
                      {new Date(medication.updated_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      })}
                    </p>
                  </div>
                </div>
              </section>
            </div>
          </div>

          {/* Footer */}
          <div className="flex justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 font-medium"
            >
              Close
            </button>
            <button
              className="px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 font-medium shadow-md hover:shadow-lg transition-all"
              onClick={() => alert('Edit functionality coming soon!')}
            >
              Edit Medication
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MedicationDetailModal;
