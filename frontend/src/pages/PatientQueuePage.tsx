import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { patientsAPI } from '../api/patients';
import type { PatientDetail } from '../api/patients';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import PatientDetailModal from '../components/PatientDetailModal';
import toast from 'react-hot-toast';
import { formatDistanceToNow } from 'date-fns';
import { MagnifyingGlassIcon, FunnelIcon, XMarkIcon, UsersIcon } from '@heroicons/react/24/outline';
import { useDebounce } from '../hooks/useDebounce';

const PatientQueuePage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [genderFilter, setGenderFilter] = useState<string>('');
  const [bloodTypeFilter, setBloodTypeFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('active');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState<PatientDetail | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  // Debounce search query to avoid refetching on every keystroke
  const debouncedSearchQuery = useDebounce(searchQuery, 1000);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['patients', debouncedSearchQuery, genderFilter, statusFilter, bloodTypeFilter],
    queryFn: () =>
      patientsAPI.getPatients({
        search: debouncedSearchQuery || undefined,
        gender: genderFilter || undefined,
        is_active: statusFilter === 'all' ? undefined : statusFilter === 'active',
        blood_type: bloodTypeFilter || undefined,
        ordering: '-enrolled_date',
      }),
    staleTime: 1000 * 60, // Data is fresh for 1 minute
    refetchOnWindowFocus: false, // Don't refetch when window regains focus
  });

  const filteredPatients = useMemo(() => {
    if (!data?.results) return [];
    return data.results;
  }, [data]);

  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (searchQuery) count++;
    if (statusFilter !== 'active') count++;
    if (genderFilter) count++;
    if (bloodTypeFilter) count++;
    return count;
  }, [searchQuery, statusFilter, genderFilter, bloodTypeFilter]);

  const handleResetFilters = () => {
    setSearchQuery('');
    setGenderFilter('');
    setBloodTypeFilter('');
    setStatusFilter('active');
  };

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

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getGenderLabel = (gender: string) => {
    switch (gender) {
      case 'M': return 'Male';
      case 'F': return 'Female';
      case 'O': return 'Other';
      default: return gender;
    }
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
          className="mt-4 px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 shadow-md hover:shadow-lg transition-all"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <UsersIcon className="w-8 h-8 text-teal-600 dark:text-teal-400" />
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Patients</h1>
        </div>
        <p className="text-gray-600 dark:text-gray-400">
          View and manage patient enrollment records
        </p>
      </div>

      {/* Search & Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 sm:p-6 mb-6">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search Input */}
          <div className="flex-1">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by name, ID, email, or phone..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>

          {/* Filter Button */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2 px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg transition-colors relative"
          >
            <FunnelIcon className="w-5 h-5" />
            <span>Filters</span>
            {activeFilterCount > 0 && (
              <span className="ml-2 px-2 py-0.5 bg-teal-400 rounded-full text-sm font-semibold">
                {activeFilterCount}
              </span>
            )}
          </button>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
              {/* Status Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Status
                </label>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value="all">All Patients</option>
                  <option value="active">Active Only</option>
                  <option value="inactive">Inactive Only</option>
                </select>
              </div>

              {/* Gender Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Gender
                </label>
                <select
                  value={genderFilter}
                  onChange={(e) => setGenderFilter(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value="">All Genders</option>
                  <option value="M">Male</option>
                  <option value="F">Female</option>
                  <option value="O">Other</option>
                </select>
              </div>

              {/* Blood Type Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Blood Type
                </label>
                <select
                  value={bloodTypeFilter}
                  onChange={(e) => setBloodTypeFilter(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value="">All Blood Types</option>
                  <option value="A+">A+</option>
                  <option value="A-">A-</option>
                  <option value="B+">B+</option>
                  <option value="B-">B-</option>
                  <option value="AB+">AB+</option>
                  <option value="AB-">AB-</option>
                  <option value="O+">O+</option>
                  <option value="O-">O-</option>
                </select>
              </div>
            </div>

            {/* Reset Filters Button */}
            {activeFilterCount > 0 && (
              <button
                onClick={handleResetFilters}
                className="flex items-center gap-2 px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 transition-colors"
              >
                <XMarkIcon className="w-4 h-4" />
                <span>Clear all filters</span>
              </button>
            )}
          </div>
        )}
      </div>

      {/* Results */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="lg" />
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <p className="text-red-600 mb-2">Failed to load patients. Please try again.</p>
          <p className="text-red-500 text-sm mb-4">{error instanceof Error ? error.message : 'Unknown error'}</p>
          <button
            onClick={() => refetch()}
            className="mt-4 px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 shadow-md hover:shadow-lg transition-all"
          >
            Retry
          </button>
        </div>
      ) : (
        <>
          {/* Results Header */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 sm:p-6 mb-6">
            <p className="text-gray-600 dark:text-gray-400">
              Found <span className="font-semibold text-gray-900 dark:text-white">{filteredPatients.length}</span> patient{filteredPatients.length !== 1 ? 's' : ''}
            </p>
          </div>

          {/* Results Table */}
          {filteredPatients.length > 0 ? (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700">
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                        Patient
                      </th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                        Contact
                      </th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                        Demographics
                      </th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                        Enrolled
                      </th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredPatients.map((patient) => (
                      <tr
                        key={patient.id}
                        onClick={() => handleViewDetails(patient.id)}
                        className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors cursor-pointer"
                      >
                        {/* Patient Name & ID */}
                        <td className="px-6 py-4">
                          <div>
                            <p className="font-medium text-gray-900 dark:text-white">
                              {patient.full_name}
                            </p>
                            <p className="text-sm text-gray-500 dark:text-gray-400">
                              ID: {patient.national_id}
                            </p>
                          </div>
                        </td>

                        {/* Contact Info */}
                        <td className="px-6 py-4">
                          <div>
                            <p className="text-sm text-gray-900 dark:text-white">
                              {patient.phone_number}
                            </p>
                            {patient.email && (
                              <p className="text-sm text-gray-500 dark:text-gray-400 truncate max-w-xs">
                                {patient.email}
                              </p>
                            )}
                          </div>
                        </td>

                        {/* Demographics */}
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-gray-700 dark:text-gray-300">
                              {patient.age}y, {getGenderLabel(patient.gender)}
                            </span>
                            {patient.blood_type && (
                              <span className="text-sm px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded font-medium">
                                {patient.blood_type}
                              </span>
                            )}
                          </div>
                        </td>

                        {/* Enrollment Date */}
                        <td className="px-6 py-4">
                          <div>
                            <p className="text-sm text-gray-900 dark:text-white">
                              {formatDate(patient.enrolled_date)}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              {formatDistanceToNow(new Date(patient.enrolled_date), { addSuffix: true })}
                            </p>
                          </div>
                        </td>

                        {/* Status */}
                        <td className="px-6 py-4">
                          <span
                            className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                              patient.is_active
                                ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                                : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                            }`}
                          >
                            {patient.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8 text-center">
              <MagnifyingGlassIcon className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400 text-lg">
                {searchQuery || genderFilter || bloodTypeFilter || statusFilter !== 'active'
                  ? 'No patients found matching your filters'
                  : 'No patients in queue'}
              </p>
            </div>
          )}
        </>
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
