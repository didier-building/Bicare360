import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { patientsAPI } from '../api/patients';
import type { PatientDetail } from '../api/patients';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import PatientDetailModal from '../components/PatientDetailModal';
import toast from 'react-hot-toast';
import { formatDistanceToNow } from 'date-fns';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

const PatientQueuePage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [genderFilter, setGenderFilter] = useState<string>('');
  const [selectedPatient, setSelectedPatient] = useState<PatientDetail | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['patients', searchQuery, genderFilter],
    queryFn: () =>
      patientsAPI.getPatients({
        search: searchQuery || undefined,
        gender: genderFilter || undefined,
        ordering: '-enrolled_date',
      }),
    refetchInterval: 60000, // Auto-refresh every 60 seconds
  });

  const filteredPatients = useMemo(() => {
    if (!data?.results) return [];
    return data.results;
  }, [data]);

  const handleViewDetails = async (patientId: number) => {
    try {
      const patient = await patientsAPI.getPatient(patientId);
      setSelectedPatient(patient);
      setShowDetailModal(true);
    } catch (err) {
      console.error('Failed to load patient details:', err);
      toast.error('Failed to load patient details');
    }
  };

  const handleCloseModal = () => {
    setShowDetailModal(false);
    setSelectedPatient(null);
  };

  const handlePatientUpdated = () => {
    refetch();
    handleCloseModal();
    toast.success('Patient information updated');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    console.error('Patient loading error:', error);
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-2">Failed to load patient queue. Please try again.</p>
        <p className="text-red-500 text-sm mb-4">{error instanceof Error ? error.message : 'Unknown error'}</p>
        <button
          onClick={() => refetch()}
          className="mt-4 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Patient Queue</h1>
        <p className="text-gray-600 mt-2">
          Manage and view patient enrollment records
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by name, ID, or phone..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          {/* Gender Filter */}
          <select
            value={genderFilter}
            onChange={(e) => setGenderFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="">All Genders</option>
            <option value="M">Male</option>
            <option value="F">Female</option>
            <option value="O">Other</option>
          </select>

          {/* Results Count */}
          <div className="flex items-center justify-end text-sm text-gray-600">
            {filteredPatients.length} patient{filteredPatients.length !== 1 ? 's' : ''} found
          </div>
        </div>
      </div>

      {/* Patient List */}
      {filteredPatients.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-600 text-lg">
            {searchQuery || genderFilter ? 'No patients found matching your filters' : 'No patients in queue'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredPatients.map((patient) => (
            <div
              key={patient.id}
              className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6"
            >
              {/* Patient Header */}
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">
                    {patient.full_name}
                  </h3>
                  <p className="text-sm text-gray-600">
                    National ID: {patient.national_id}
                  </p>
                </div>
                <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
                  patient.is_active
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {patient.is_active ? 'Active' : 'Inactive'}
                </div>
              </div>

              {/* Patient Info Grid */}
              <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                <div>
                  <p className="text-gray-600">Age</p>
                  <p className="font-semibold text-gray-900">{patient.age} years</p>
                </div>
                <div>
                  <p className="text-gray-600">Gender</p>
                  <p className="font-semibold text-gray-900">
                    {patient.gender === 'M' ? 'Male' : patient.gender === 'F' ? 'Female' : 'Other'}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Phone</p>
                  <p className="font-semibold text-gray-900">{patient.phone_number}</p>
                </div>
                <div>
                  <p className="text-gray-600">Enrolled</p>
                  <p className="font-semibold text-gray-900">
                    {formatDistanceToNow(new Date(patient.enrolled_date), {
                      addSuffix: true,
                    })}
                  </p>
                </div>
              </div>

              {/* Action Button */}
              <button
                onClick={() => handleViewDetails(patient.id)}
                className="w-full px-4 py-2 bg-primary-500 text-white rounded-lg font-medium hover:bg-primary-600 transition-colors"
              >
                View Details
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Patient Detail Modal */}
      {showDetailModal && selectedPatient && (
        <PatientDetailModal
          patient={selectedPatient}
          onClose={handleCloseModal}
          onPatientUpdated={handlePatientUpdated}
        />
      )}
    </div>
  );
};

export default PatientQueuePage;
