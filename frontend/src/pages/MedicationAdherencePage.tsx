import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  UsersIcon,
  CheckCircleIcon, 
  XCircleIcon,
  ClockIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon
} from '@heroicons/react/24/outline';
import adherenceAPI from '../api/adherence';
import { patientsAPI } from '../api/patients';
import LoadingSpinner from '../components/ui/LoadingSpinner';

interface PatientAdherence {
  patient_id: number;
  patient_name: string;
  adherence_rate: number;
  total_doses: number;
  taken: number;
  missed: number;
  scheduled: number;
  overdue: number;
  last_taken?: string;
}

const MedicationAdherencePage: React.FC = () => {
  const [selectedFilter, setSelectedFilter] = useState<'all' | 'critical' | 'low' | 'good'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'rate' | 'name' | 'missed'>('rate');

  // Fetch overall stats
  const { data: overallStats, isLoading: statsLoading } = useQuery({
    queryKey: ['adherence', 'stats'],
    queryFn: () => adherenceAPI.getAdherenceStats(),
  });

  // Fetch all adherence records to calculate per-patient stats
  const { data: adherenceData, isLoading: adherenceLoading } = useQuery({
    queryKey: ['adherence', 'all'],
    queryFn: () => adherenceAPI.getAdherenceRecords({ page_size: 1000 }),
  });

  // Fetch overdue records
  const { data: overdueData, isLoading: overdueLoading } = useQuery({
    queryKey: ['adherence', 'overdue'],
    queryFn: () => adherenceAPI.getOverdueRecords({ page_size: 100 }),
    refetchInterval: 60000, // Refetch every minute
  });

  // Fetch patients
  const { data: patientsData } = useQuery({
    queryKey: ['patients'],
    queryFn: () => patientsAPI.getPatients({ limit: 100 }),
  });

  // Calculate per-patient adherence stats
  const patientAdherenceStats = useMemo((): PatientAdherence[] => {
    if (!adherenceData?.results || !patientsData?.results) return [];

    const patientMap = new Map<number, PatientAdherence>();

    adherenceData.results.forEach((record) => {
      if (!record.prescription_details) return;
      
      const patientId = record.prescription_details.patient_id;
      const patientName = record.prescription_details.patient_name;

      if (!patientMap.has(patientId)) {
        patientMap.set(patientId, {
          patient_id: patientId,
          patient_name: patientName,
          adherence_rate: 0,
          total_doses: 0,
          taken: 0,
          missed: 0,
          scheduled: 0,
          overdue: 0,
        });
      }

      const stats = patientMap.get(patientId)!;
      stats.total_doses++;

      if (record.status === 'taken') {
        stats.taken++;
        stats.last_taken = record.actual_time || record.scheduled_time;
      } else if (record.status === 'missed') {
        stats.missed++;
      } else if (record.status === 'scheduled') {
        stats.scheduled++;
      }
    });

    // Count overdue per patient
    overdueData?.results?.forEach((record) => {
      if (!record.prescription_details) return;
      
      const patientId = record.prescription_details.patient_id;
      if (patientMap.has(patientId)) {
        patientMap.get(patientId)!.overdue++;
      }
    });

    // Calculate adherence rates
    patientMap.forEach((stats) => {
      const completedDoses = stats.taken + stats.missed;
      stats.adherence_rate = completedDoses > 0 
        ? Math.round((stats.taken / completedDoses) * 100) 
        : 0;
    });

    return Array.from(patientMap.values());
  }, [adherenceData, overdueData, patientsData]);

  // Filter and sort patients
  const filteredPatients = useMemo(() => {
    let filtered = patientAdherenceStats;

    // Apply filter
    if (selectedFilter === 'critical') {
      filtered = filtered.filter(p => p.adherence_rate < 50);
    } else if (selectedFilter === 'low') {
      filtered = filtered.filter(p => p.adherence_rate >= 50 && p.adherence_rate < 80);
    } else if (selectedFilter === 'good') {
      filtered = filtered.filter(p => p.adherence_rate >= 80);
    }

    // Apply search
    if (searchQuery) {
      filtered = filtered.filter(p => 
        p.patient_name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Apply sort
    filtered.sort((a, b) => {
      if (sortBy === 'rate') return a.adherence_rate - b.adherence_rate;
      if (sortBy === 'name') return a.patient_name.localeCompare(b.patient_name);
      if (sortBy === 'missed') return b.missed - a.missed;
      return 0;
    });

    return filtered;
  }, [patientAdherenceStats, selectedFilter, searchQuery, sortBy]);

  // Calculate alert counts
  const alertCounts = useMemo(() => {
    return {
      critical: patientAdherenceStats.filter(p => p.adherence_rate < 50).length,
      low: patientAdherenceStats.filter(p => p.adherence_rate >= 50 && p.adherence_rate < 80).length,
      good: patientAdherenceStats.filter(p => p.adherence_rate >= 80).length,
    };
  }, [patientAdherenceStats]);

  const isLoading = statsLoading || adherenceLoading || overdueLoading;

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const getAdherenceColor = (rate: number) => {
    if (rate >= 80) return 'text-green-600 dark:text-green-400';
    if (rate >= 50) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getAdherenceBadge = (rate: number) => {
    if (rate >= 80) return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
    if (rate >= 50) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
    return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Medication Adherence Monitoring
          </h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Track patient medication adherence and identify patients needing intervention
          </p>
        </div>
      </div>

      {/* Overall Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Overall Adherence</p>
              <p className={`text-3xl font-bold mt-2 ${getAdherenceColor(overallStats?.adherence_rate || 0)}`}>
                {overallStats?.adherence_rate || 0}%
              </p>
            </div>
            <ChartBarIcon className="w-12 h-12 text-purple-600 dark:text-purple-400" />
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
            {overallStats?.taken_count || 0} taken / {overallStats?.total_records || 0} total doses
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Patients Monitored</p>
              <p className="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-2">
                {patientAdherenceStats.length}
              </p>
            </div>
            <UsersIcon className="w-12 h-12 text-blue-600 dark:text-blue-400" />
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
            Active medication schedules
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Missed Doses</p>
              <p className="text-3xl font-bold text-red-600 dark:text-red-400 mt-2">
                {overallStats?.missed_count || 0}
              </p>
            </div>
            <XCircleIcon className="w-12 h-12 text-red-600 dark:text-red-400" />
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
            {((overallStats?.missed_count || 0) / (overallStats?.total_records || 1) * 100).toFixed(1)}% of total doses
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Overdue Doses</p>
              <p className="text-3xl font-bold text-orange-600 dark:text-orange-400 mt-2">
                {overdueData?.results?.length || 0}
              </p>
            </div>
            <ClockIcon className="w-12 h-12 text-orange-600 dark:text-orange-400" />
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
            Requires immediate attention
          </p>
        </div>
      </div>

      {/* Alert Summary */}
      {(alertCounts.critical > 0 || alertCounts.low > 0) && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <ExclamationTriangleIcon className="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-red-900 dark:text-red-200">
                Patients Requiring Intervention
              </h3>
              <div className="mt-2 space-y-1 text-sm text-red-800 dark:text-red-300">
                {alertCounts.critical > 0 && (
                  <p>• <span className="font-medium">{alertCounts.critical}</span> patient{alertCounts.critical !== 1 ? 's' : ''} with <strong>critical adherence</strong> (&lt;50%)</p>
                )}
                {alertCounts.low > 0 && (
                  <p>• <span className="font-medium">{alertCounts.low}</span> patient{alertCounts.low !== 1 ? 's' : ''} with <strong>low adherence</strong> (50-79%)</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters and Search */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-200 dark:border-gray-700">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Filter Buttons */}
          <div className="flex items-center gap-2 flex-wrap">
            <FunnelIcon className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            <button
              onClick={() => setSelectedFilter('all')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                selectedFilter === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              All ({patientAdherenceStats.length})
            </button>
            <button
              onClick={() => setSelectedFilter('critical')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                selectedFilter === 'critical'
                  ? 'bg-red-600 text-white'
                  : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 hover:bg-red-200 dark:hover:bg-red-900/50'
              }`}
            >
              Critical &lt;50% ({alertCounts.critical})
            </button>
            <button
              onClick={() => setSelectedFilter('low')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                selectedFilter === 'low'
                  ? 'bg-yellow-600 text-white'
                  : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 hover:bg-yellow-200 dark:hover:bg-yellow-900/50'
              }`}
            >
              Low 50-79% ({alertCounts.low})
            </button>
            <button
              onClick={() => setSelectedFilter('good')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                selectedFilter === 'good'
                  ? 'bg-green-600 text-white'
                  : 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 hover:bg-green-200 dark:hover:bg-green-900/50'
              }`}
            >
              Good ≥80% ({alertCounts.good})
            </button>
          </div>

          {/* Search */}
          <div className="flex-1 lg:max-w-xs">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search patients..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Sort */}
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Sort by:</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'rate' | 'name' | 'missed')}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="rate">Adherence Rate (Low → High)</option>
              <option value="name">Patient Name (A → Z)</option>
              <option value="missed">Missed Doses (High → Low)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Patients Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Patient
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Adherence Rate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Total Doses
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Taken
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Missed
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Overdue
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {filteredPatients.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                    No patients found
                  </td>
                </tr>
              ) : (
                filteredPatients.map((patient) => (
                  <tr key={patient.patient_id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
                          <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                            {patient.patient_name.split(' ').map(n => n[0]).join('').toUpperCase()}
                          </span>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {patient.patient_name}
                          </div>
                          {patient.last_taken && (
                            <div className="text-xs text-gray-500 dark:text-gray-400">
                              Last taken: {new Date(patient.last_taken).toLocaleString()}
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <span className={`text-2xl font-bold ${getAdherenceColor(patient.adherence_rate)}`}>
                          {patient.adherence_rate}%
                        </span>
                        {patient.adherence_rate >= 80 ? (
                          <ArrowTrendingUpIcon className="w-5 h-5 text-green-600 dark:text-green-400" />
                        ) : patient.adherence_rate < 50 ? (
                          <ArrowTrendingDownIcon className="w-5 h-5 text-red-600 dark:text-red-400" />
                        ) : null}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {patient.total_doses}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <CheckCircleIcon className="w-5 h-5 text-green-600 dark:text-green-400" />
                        <span className="text-sm font-medium text-gray-900 dark:text-white">{patient.taken}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <XCircleIcon className="w-5 h-5 text-red-600 dark:text-red-400" />
                        <span className="text-sm font-medium text-gray-900 dark:text-white">{patient.missed}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <ClockIcon className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                        <span className="text-sm font-medium text-gray-900 dark:text-white">{patient.overdue}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getAdherenceBadge(patient.adherence_rate)}`}>
                        {patient.adherence_rate >= 80 ? 'Good' : patient.adherence_rate >= 50 ? 'Low' : 'Critical'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Help Text */}
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-200 mb-2">
          Adherence Rate Guidelines
        </h3>
        <div className="space-y-1 text-sm text-blue-800 dark:text-blue-300">
          <p>• <strong>Good (≥80%):</strong> Patient is adhering well to medication schedule</p>
          <p>• <strong>Low (50-79%):</strong> Patient needs follow-up and support</p>
          <p>• <strong>Critical (&lt;50%):</strong> Immediate intervention required - schedule consultation</p>
          <p>• <strong>Overdue:</strong> Scheduled doses that have not been taken yet</p>
        </div>
      </div>
    </div>
  );
};

export default MedicationAdherencePage;
