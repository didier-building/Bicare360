import React, { useState, useCallback, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  XMarkIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline';
import patientsAPI, { type SearchPatient } from '../api/patients';
import LoadingSpinner from '../components/ui/LoadingSpinner';

interface FilterState {
  q: string;
  is_active: boolean | 'all';
  gender: string | 'all';
  blood_type: string | 'all';
  enrolled_after: string;
  enrolled_before: string;
  sort: 'name' | 'age' | 'enrolled_date';
  order: 'asc' | 'desc';
  limit: number;
}

const GENDERS = [
  { value: 'M', label: 'Male' },
  { value: 'F', label: 'Female' },
  { value: 'O', label: 'Other' },
];

const BLOOD_TYPES = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];

const NursePatientSearchPage: React.FC = () => {
  const [filters, setFilters] = useState<FilterState>({
    q: '',
    is_active: true,
    gender: 'all',
    blood_type: 'all',
    enrolled_after: '',
    enrolled_before: '',
    sort: 'enrolled_date',
    order: 'desc',
    limit: 50,
  });

  const [showFilters, setShowFilters] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState<SearchPatient | null>(null);

  // Build query parameters
  const queryParams = useMemo(() => {
    const params: Record<string, any> = {};

    if (filters.q) params.q = filters.q;
    if (filters.is_active !== 'all') params.is_active = filters.is_active;
    if (filters.gender !== 'all') params.gender = filters.gender;
    if (filters.blood_type !== 'all') params.blood_type = filters.blood_type;
    if (filters.enrolled_after) params.enrolled_after = filters.enrolled_after;
    if (filters.enrolled_before) params.enrolled_before = filters.enrolled_before;

    params.sort = filters.sort;
    params.order = filters.order;
    params.limit = filters.limit;

    return params;
  }, [filters]);

  // Fetch search results
  const { data: patients = [], isLoading, error } = useQuery({
    queryKey: ['patients', 'search', queryParams],
    queryFn: () => patientsAPI.searchPatients(queryParams),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  const handleSearchChange = useCallback((value: string) => {
    setFilters(prev => ({ ...prev, q: value }));
  }, []);

  const handleFilterChange = useCallback(
    (key: keyof FilterState, value: any) => {
      setFilters(prev => ({ ...prev, [key]: value }));
    },
    []
  );

  const handleResetFilters = useCallback(() => {
    setFilters({
      q: '',
      is_active: true,
      gender: 'all',
      blood_type: 'all',
      enrolled_after: '',
      enrolled_before: '',
      sort: 'enrolled_date',
      order: 'desc',
      limit: 50,
    });
  }, []);

  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.q) count++;
    if (filters.is_active !== true) count++;
    if (filters.gender !== 'all') count++;
    if (filters.blood_type !== 'all') count++;
    if (filters.enrolled_after) count++;
    if (filters.enrolled_before) count++;
    return count;
  }, [filters]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getGenderLabel = (gender: string) => {
    const g = GENDERS.find(g => g.value === gender);
    return g?.label || gender;
  };

  const getStatusBadge = (isActive: boolean) => {
    return isActive
      ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
      : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <UserGroupIcon className="w-8 h-8 text-blue-600 dark:text-blue-400" />
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Patient Search
            </h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400">
            Search and filter patients across the system
          </p>
        </div>

        {/* Search Bar */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 sm:p-6 mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search Input */}
            <div className="flex-1">
              <label htmlFor="search" className="sr-only">
                Search patients
              </label>
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                <input
                  id="search"
                  type="text"
                  placeholder="Search by name, email, phone, or ID..."
                  value={filters.q}
                  onChange={e => handleSearchChange(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>

            {/* Filter Button */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors relative"
            >
              <FunnelIcon className="w-5 h-5" />
              <span>Filters</span>
              {activeFilterCount > 0 && (
                <span className="ml-2 px-2 py-0.5 bg-blue-400 rounded-full text-sm font-semibold">
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
                    value={filters.is_active === 'all' ? 'all' : filters.is_active ? 'active' : 'inactive'}
                    onChange={e => {
                      const value = e.target.value;
                      handleFilterChange(
                        'is_active',
                        value === 'all' ? 'all' : value === 'active'
                      );
                    }}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
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
                    value={filters.gender}
                    onChange={e => handleFilterChange('gender', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="all">All Genders</option>
                    {GENDERS.map(g => (
                      <option key={g.value} value={g.value}>
                        {g.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Blood Type Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Blood Type
                  </label>
                  <select
                    value={filters.blood_type}
                    onChange={e => handleFilterChange('blood_type', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="all">All Blood Types</option>
                    {BLOOD_TYPES.map(type => (
                      <option key={type} value={type}>
                        {type}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Enrolled After */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Enrolled After
                  </label>
                  <input
                    type="date"
                    value={filters.enrolled_after}
                    onChange={e => handleFilterChange('enrolled_after', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>

                {/* Enrolled Before */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Enrolled Before
                  </label>
                  <input
                    type="date"
                    value={filters.enrolled_before}
                    onChange={e => handleFilterChange('enrolled_before', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>

                {/* Limit */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Results Per Page
                  </label>
                  <select
                    value={filters.limit}
                    onChange={e => handleFilterChange('limit', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option value={10}>10</option>
                    <option value={25}>25</option>
                    <option value={50}>50</option>
                    <option value={100}>100</option>
                  </select>
                </div>
              </div>

              {/* Sorting Options */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Sort By
                  </label>
                  <select
                    value={filters.sort}
                    onChange={e =>
                      handleFilterChange('sort', e.target.value as 'name' | 'age' | 'enrolled_date')
                    }
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="enrolled_date">Enrollment Date</option>
                    <option value="name">Patient Name</option>
                    <option value="age">Age</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Order
                  </label>
                  <select
                    value={filters.order}
                    onChange={e => handleFilterChange('order', e.target.value as 'asc' | 'desc')}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="desc">Descending</option>
                    <option value="asc">Ascending</option>
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

        {/* Results Section */}
        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <LoadingSpinner />
          </div>
        ) : error ? (
          <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <p className="text-red-700 dark:text-red-400">
              Error loading search results. Please try again.
            </p>
          </div>
        ) : (
          <>
            {/* Results Header */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 sm:p-6 mb-6">
              <p className="text-gray-600 dark:text-gray-400">
                Found <span className="font-semibold text-gray-900 dark:text-white">{patients.length}</span> patient{patients.length !== 1 ? 's' : ''}
              </p>
            </div>

            {/* Results Table */}
            {patients.length > 0 ? (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700">
                        <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                          Name
                        </th>
                        <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                          Contact
                        </th>
                        <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                          Demographics
                        </th>
                        <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                          Enrollment
                        </th>
                        <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                          Status
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {patients.map(patient => (
                        <tr
                          key={patient.id}
                          onClick={() => setSelectedPatient(patient)}
                          className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors cursor-pointer"
                        >
                          {/* Name */}
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

                          {/* Contact */}
                          <td className="px-6 py-4">
                            <div>
                              <p className="text-sm text-gray-900 dark:text-white">
                                {patient.phone_number}
                              </p>
                              {patient.email && (
                                <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
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
                                <span className="text-sm px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-gray-700 dark:text-gray-300">
                                  {patient.blood_type}
                                </span>
                              )}
                            </div>
                          </td>

                          {/* Enrollment Date */}
                          <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">
                            {formatDate(patient.enrolled_date)}
                          </td>

                          {/* Status */}
                          <td className="px-6 py-4">
                            <span
                              className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${getStatusBadge(
                                patient.is_active
                              )}`}
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
                  No patients found. Try adjusting your search or filters.
                </p>
              </div>
            )}
          </>
        )}

        {/* Patient Detail Modal */}
        {selectedPatient && (
          <div className="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center p-4 z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                  Patient Details
                </h2>
                <button
                  onClick={() => setSelectedPatient(null)}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  <XMarkIcon className="w-6 h-6" />
                </button>
              </div>
              <div className="p-6 space-y-4">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Name</p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white">
                    {selectedPatient.full_name}
                  </p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Age</p>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white">
                      {selectedPatient.age}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Gender</p>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white">
                      {getGenderLabel(selectedPatient.gender)}
                    </p>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">National ID</p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white">
                    {selectedPatient.national_id}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Phone</p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white">
                    {selectedPatient.phone_number}
                  </p>
                </div>
                {selectedPatient.email && (
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Email</p>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white break-all">
                      {selectedPatient.email}
                    </p>
                  </div>
                )}
                {selectedPatient.blood_type && (
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Blood Type</p>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white">
                      {selectedPatient.blood_type}
                    </p>
                  </div>
                )}
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Enrolled</p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white">
                    {formatDate(selectedPatient.enrolled_date)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Status</p>
                  <span
                    className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${getStatusBadge(
                      selectedPatient.is_active
                    )}`}
                  >
                    {selectedPatient.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
              <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex gap-3">
                <button
                  onClick={() => setSelectedPatient(null)}
                  className="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                >
                  Close
                </button>
                <button className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
                  View Details
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default NursePatientSearchPage;
