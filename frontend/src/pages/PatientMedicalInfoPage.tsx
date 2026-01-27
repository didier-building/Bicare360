import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../api/client';

interface MedicationItem {
  id: number;
  name: string;
  dosage: string;
  frequency: string;
  reason: string;
  start_date: string;
  end_date?: string;
  is_active: boolean;
}

interface HealthCondition {
  id: number;
  name: string;
  diagnosed_date: string;
  status: string;
}

interface Allergy {
  id: number;
  name: string;
  severity: string;
  reaction: string;
}

export default function PatientMedicalInfoPage() {
  const navigate = useNavigate();
  const [medications, setMedications] = useState<MedicationItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'medications' | 'conditions' | 'allergies'>('medications');

  // Demo data for health conditions and allergies (in real app, would come from API)
  const [conditions] = useState<HealthCondition[]>([
    {
      id: 1,
      name: 'Hypertension',
      diagnosed_date: '2020-05-15',
      status: 'Active',
    },
    {
      id: 2,
      name: 'Type 2 Diabetes',
      diagnosed_date: '2019-03-20',
      status: 'Active',
    },
  ]);

  const [allergies] = useState<Allergy[]>([
    {
      id: 1,
      name: 'Penicillin',
      severity: 'Severe',
      reaction: 'Anaphylaxis',
    },
    {
      id: 2,
      name: 'Shellfish',
      severity: 'Moderate',
      reaction: 'Itching and swelling',
    },
  ]);

  useEffect(() => {
    fetchMedications();
  }, []);

  const fetchMedications = async () => {
    try {
      const response = await client.get('/v1/tracking/');
      const medicationData = Array.isArray(response.data) ? response.data : response.data.results || [];
      setMedications(medicationData);
    } catch (err) {
      console.error('Failed to fetch medications:', err);
      setError('Failed to load medical information');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900 py-8">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={() => navigate('/patient/dashboard')}
            className="flex items-center gap-2 text-teal-600 dark:text-teal-400 hover:text-teal-700"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Dashboard
          </button>
        </div>

        {/* Alerts */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-700 dark:text-red-200">{error}</p>
          </div>
        )}

        {/* Medical Info Container */}
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg overflow-hidden">
          {/* Tabs */}
          <div className="flex border-b border-gray-200 dark:border-slate-700">
            <button
              onClick={() => setActiveTab('medications')}
              className={`flex-1 px-6 py-4 font-medium text-center transition-colors ${
                activeTab === 'medications'
                  ? 'border-b-2 border-teal-600 text-teal-600 dark:text-teal-400'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-300'
              }`}
            >
              <span className="flex items-center justify-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.452a6 6 0 00-3.86.454l-.312.104a6 6 0 01-3.864-.454l-2.387.452a2 2 0 00-1.021.547m19.428 0A6 6 0 009.172 12m19.428 0l-.063-.373a2 2 0 00-1.942-1.651H4.605a2 2 0 00-1.942 1.651l-.063.373m19.428 0A6.001 6.001 0 009.172 12m0 0a6.001 6.001 0 01-3.356 5.557M9.172 12a3 3 0 015.364 0"
                  />
                </svg>
                Medications
              </span>
            </button>
            <button
              onClick={() => setActiveTab('conditions')}
              className={`flex-1 px-6 py-4 font-medium text-center transition-colors ${
                activeTab === 'conditions'
                  ? 'border-b-2 border-teal-600 text-teal-600 dark:text-teal-400'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-300'
              }`}
            >
              <span className="flex items-center justify-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                Health Conditions
              </span>
            </button>
            <button
              onClick={() => setActiveTab('allergies')}
              className={`flex-1 px-6 py-4 font-medium text-center transition-colors ${
                activeTab === 'allergies'
                  ? 'border-b-2 border-teal-600 text-teal-600 dark:text-teal-400'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-300'
              }`}
            >
              <span className="flex items-center justify-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4v.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Allergies
              </span>
            </button>
          </div>

          {/* Tab Content */}
          <div className="p-8">
            {/* Medications Tab */}
            {activeTab === 'medications' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Current Medications</h2>

                {medications.length === 0 ? (
                  <div className="text-center py-12">
                    <svg
                      className="mx-auto h-12 w-12 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 14l-7 7m0 0l-7-7m7 7V3"
                      />
                    </svg>
                    <p className="mt-4 text-gray-600 dark:text-gray-400">No medications recorded yet</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {medications.map((med) => (
                      <div
                        key={med.id}
                        className="p-4 border border-gray-200 dark:border-slate-700 rounded-lg hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <h3 className="font-semibold text-gray-900 dark:text-white text-lg">{med.name}</h3>
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-medium ${
                              med.is_active
                                ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200'
                                : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'
                            }`}
                          >
                            {med.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </div>

                        <div className="space-y-2 text-sm">
                          <div>
                            <p className="text-gray-600 dark:text-gray-400">Dosage</p>
                            <p className="font-medium text-gray-900 dark:text-white">{med.dosage}</p>
                          </div>
                          <div>
                            <p className="text-gray-600 dark:text-gray-400">Frequency</p>
                            <p className="font-medium text-gray-900 dark:text-white">{med.frequency}</p>
                          </div>
                          <div>
                            <p className="text-gray-600 dark:text-gray-400">Reason</p>
                            <p className="font-medium text-gray-900 dark:text-white">{med.reason}</p>
                          </div>
                          <div>
                            <p className="text-gray-600 dark:text-gray-400">Started</p>
                            <p className="font-medium text-gray-900 dark:text-white">
                              {new Date(med.start_date).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Health Conditions Tab */}
            {activeTab === 'conditions' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Health Conditions</h2>

                {conditions.length === 0 ? (
                  <div className="text-center py-12">
                    <svg
                      className="mx-auto h-12 w-12 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 14l-7 7m0 0l-7-7m7 7V3"
                      />
                    </svg>
                    <p className="mt-4 text-gray-600 dark:text-gray-400">No health conditions recorded</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {conditions.map((condition) => (
                      <div
                        key={condition.id}
                        className="p-4 border border-gray-200 dark:border-slate-700 rounded-lg hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <h3 className="font-semibold text-gray-900 dark:text-white text-lg">{condition.name}</h3>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                              Diagnosed: {new Date(condition.diagnosed_date).toLocaleDateString()}
                            </p>
                          </div>
                          <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200">
                            {condition.status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Allergies Tab */}
            {activeTab === 'allergies' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Allergies</h2>

                {allergies.length === 0 ? (
                  <div className="text-center py-12">
                    <svg
                      className="mx-auto h-12 w-12 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 14l-7 7m0 0l-7-7m7 7V3"
                      />
                    </svg>
                    <p className="mt-4 text-gray-600 dark:text-gray-400">No allergies recorded</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {allergies.map((allergy) => (
                      <div
                        key={allergy.id}
                        className={`p-4 border rounded-lg ${
                          allergy.severity === 'Severe'
                            ? 'border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20'
                            : 'border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-900/20'
                        }`}
                      >
                        <div className="flex items-start justify-between mb-3">
                          <h3 className="font-semibold text-gray-900 dark:text-white text-lg">{allergy.name}</h3>
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-medium ${
                              allergy.severity === 'Severe'
                                ? 'bg-red-200 dark:bg-red-800 text-red-800 dark:text-red-200'
                                : 'bg-yellow-200 dark:bg-yellow-800 text-yellow-800 dark:text-yellow-200'
                            }`}
                          >
                            {allergy.severity}
                          </span>
                        </div>

                        <div>
                          <p className="text-sm text-gray-600 dark:text-gray-400">Reaction</p>
                          <p className="font-medium text-gray-900 dark:text-white">{allergy.reaction}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}