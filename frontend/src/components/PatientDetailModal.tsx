import React, { useState } from 'react';
import type { PatientDetail } from '../api/patients';
import { patientsAPI } from '../api/patients';
import toast from 'react-hot-toast';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface PatientDetailModalProps {
  patient: PatientDetail;
  onClose: () => void;
  onPatientUpdated: () => void;
}

const PatientDetailModal: React.FC<PatientDetailModalProps> = ({
  patient,
  onClose,
  onPatientUpdated,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [editData, setEditData] = useState({
    first_name: patient.first_name,
    last_name: patient.last_name,
    email: patient.email || '',
    phone_number: patient.phone_number,
    alt_phone_number: patient.alt_phone_number || '',
    blood_type: patient.blood_type || '',
    language_preference: patient.language_preference,
    prefers_sms: patient.prefers_sms,
    prefers_whatsapp: patient.prefers_whatsapp,
  });

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await patientsAPI.updatePatient(patient.id, editData);
      onPatientUpdated();
      setIsEditing(false);
    } catch (err) {
      console.error('Failed to update patient:', err);
      toast.error('Failed to save patient information');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-96 overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">Patient Details</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Basic Info */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Basic Information
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  First Name
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    value={editData.first_name}
                    onChange={(e) =>
                      setEditData({ ...editData, first_name: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                ) : (
                  <p className="text-gray-900 font-semibold">{patient.first_name}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Last Name
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    value={editData.last_name}
                    onChange={(e) =>
                      setEditData({ ...editData, last_name: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                ) : (
                  <p className="text-gray-900 font-semibold">{patient.last_name}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  National ID
                </label>
                <p className="text-gray-900 font-semibold">{patient.national_id}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Age
                </label>
                <p className="text-gray-900 font-semibold">{patient.age} years</p>
              </div>
            </div>
          </div>

          {/* Contact Info */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Contact Information
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone Number
                </label>
                {isEditing ? (
                  <input
                    type="tel"
                    value={editData.phone_number}
                    onChange={(e) =>
                      setEditData({ ...editData, phone_number: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                ) : (
                  <p className="text-gray-900 font-semibold">{patient.phone_number}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Alt Phone Number
                </label>
                {isEditing ? (
                  <input
                    type="tel"
                    value={editData.alt_phone_number}
                    onChange={(e) =>
                      setEditData({ ...editData, alt_phone_number: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                ) : (
                  <p className="text-gray-900 font-semibold">
                    {patient.alt_phone_number || '—'}
                  </p>
                )}
              </div>

              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                {isEditing ? (
                  <input
                    type="email"
                    value={editData.email}
                    onChange={(e) =>
                      setEditData({ ...editData, email: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                ) : (
                  <p className="text-gray-900 font-semibold">{patient.email || '—'}</p>
                )}
              </div>
            </div>
          </div>

          {/* Medical Info */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Medical Information
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Blood Type
                </label>
                {isEditing ? (
                  <select
                    value={editData.blood_type}
                    onChange={(e) =>
                      setEditData({ ...editData, blood_type: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">Not specified</option>
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                  </select>
                ) : (
                  <p className="text-gray-900 font-semibold">{patient.blood_type || '—'}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Language Preference
                </label>
                {isEditing ? (
                  <select
                    value={editData.language_preference}
                    onChange={(e) =>
                      setEditData({
                        ...editData,
                        language_preference: e.target.value,
                      })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="kin">Kinyarwanda</option>
                    <option value="eng">English</option>
                    <option value="fra">French</option>
                  </select>
                ) : (
                  <p className="text-gray-900 font-semibold">
                    {patient.language_preference === 'kin'
                      ? 'Kinyarwanda'
                      : patient.language_preference === 'eng'
                      ? 'English'
                      : 'French'}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Preferences */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Communication Preferences
            </h3>
            <div className="space-y-3">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={editData.prefers_sms}
                  onChange={(e) =>
                    setEditData({ ...editData, prefers_sms: e.target.checked })
                  }
                  disabled={!isEditing}
                  className="rounded text-primary-500 focus:ring-primary-500"
                />
                <span className="text-sm text-gray-700">Prefers SMS</span>
              </label>
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={editData.prefers_whatsapp}
                  onChange={(e) =>
                    setEditData({ ...editData, prefers_whatsapp: e.target.checked })
                  }
                  disabled={!isEditing}
                  className="rounded text-primary-500 focus:ring-primary-500"
                />
                <span className="text-sm text-gray-700">Prefers WhatsApp</span>
              </label>
            </div>
          </div>

          {/* Enrollment Info */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Enrollment Information
            </h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Enrolled By</p>
                <p className="font-semibold text-gray-900">{patient.enrolled_by_username}</p>
              </div>
              <div>
                <p className="text-gray-600">Enrolled Date</p>
                <p className="font-semibold text-gray-900">
                  {new Date(patient.enrolled_date).toLocaleDateString()}
                </p>
              </div>
              <div>
                <p className="text-gray-600">Status</p>
                <p
                  className={`font-semibold ${
                    patient.is_active ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {patient.is_active ? 'Active' : 'Inactive'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer / Actions */}
        <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 p-6 flex justify-end gap-3">
          {isEditing ? (
            <>
              <button
                onClick={() => setIsEditing(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={isSaving}
                className="px-4 py-2 bg-primary-500 text-white rounded-lg font-medium hover:bg-primary-600 disabled:opacity-50"
              >
                {isSaving ? 'Saving...' : 'Save Changes'}
              </button>
            </>
          ) : (
            <>
              <button
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50"
              >
                Close
              </button>
              <button
                onClick={() => setIsEditing(true)}
                className="px-4 py-2 bg-primary-500 text-white rounded-lg font-medium hover:bg-primary-600"
              >
                Edit Patient
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default PatientDetailModal;
