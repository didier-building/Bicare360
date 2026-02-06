import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import client from '../api/client';
import {
  ChartBarIcon,
  HeartIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
} from '@heroicons/react/24/outline';
import vitalsAPI from '../api/vitals';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import VitalTrendsChart from '../components/health/VitalTrendsChart';
import HealthSummaryCard from '../components/health/HealthSummaryCard';
import HealthGoalsPanel from '../components/health/HealthGoalsPanel';
import VitalAlertsPanel from '../components/health/VitalAlertsPanel';
import VitalReadingsList from '../components/health/VitalReadingsList';

interface TabType {
  id: string;
  label: string;
  icon: React.ReactNode;
}

const TABS: TabType[] = [
  { id: 'summary', label: 'Summary', icon: <ChartBarIcon className="w-5 h-5" /> },
  { id: 'trends', label: 'Trends', icon: <ArrowTrendingUpIcon className="w-5 h-5" /> },
  { id: 'goals', label: 'Goals', icon: <CheckCircleIcon className="w-5 h-5" /> },
  { id: 'alerts', label: 'Alerts', icon: <ExclamationTriangleIcon className="w-5 h-5" /> },
  { id: 'readings', label: 'Readings', icon: <HeartIcon className="w-5 h-5" /> },
];

const VITAL_TYPES = [
  { value: 'blood_pressure', label: 'Blood Pressure', unit: 'mmHg' },
  { value: 'heart_rate', label: 'Heart Rate', unit: 'bpm' },
  { value: 'temperature', label: 'Temperature', unit: '°C' },
  { value: 'weight', label: 'Weight', unit: 'kg' },
  { value: 'oxygen_saturation', label: 'O2 Saturation', unit: '%' },
  { value: 'respiratory_rate', label: 'Respiratory Rate', unit: 'breaths/min' },
  { value: 'blood_glucose', label: 'Blood Glucose', unit: 'mg/dL' },
];

const HealthProgressChartPage: React.FC = () => {
  const { patientId: patientIdParam } = useParams<{ patientId: string }>();
  const [activeTab, setActiveTab] = useState('summary');
  const [selectedVitalType, setSelectedVitalType] = useState('heart_rate');
  const [trendDays, setTrendDays] = useState(7);
  const [patientId, setPatientId] = useState<number | null>(patientIdParam ? parseInt(patientIdParam) : null);
  const [isLoadingPatientId, setIsLoadingPatientId] = useState(!patientIdParam);
  const [error, setError] = useState<string | null>(null);

  // Fetch patient ID from /patients/me/ if not in URL
  useEffect(() => {
    if (patientIdParam) {
      setPatientId(parseInt(patientIdParam));
      setIsLoadingPatientId(false);
      return;
    }

    // Only fetch /patients/me/ if user is a patient (has patient role)
    const userRole = localStorage.getItem('user_role');
    if (userRole !== 'patient') {
      setError('Health progress is only available for patients.');
      setIsLoadingPatientId(false);
      return;
    }

    const fetchPatientId = async () => {
      try {
        const response = await client.get('/v1/patients/me/');
        setPatientId(response.data.id);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch patient ID:', err);
        setError('Failed to load patient information. Please log in first.');
      } finally {
        setIsLoadingPatientId(false);
      }
    };

    fetchPatientId();
  }, [patientIdParam]);

  // All hooks must be called before any return
  const { 
    data: healthSummary, 
    isLoading: summaryLoading, 
    error: summaryError 
  } = useQuery({
    queryKey: ['health-summary', patientId],
    queryFn: () => patientId ? vitalsAPI.getHealthSummary(parseInt(patientId.toString())) : Promise.reject('No patient ID'),
    enabled: !!patientId,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  const { 
    data: vitalTrends, 
    isLoading: trendsLoading 
  } = useQuery({
    queryKey: ['vital-trends', patientId, selectedVitalType, trendDays],
    queryFn: () => patientId ? vitalsAPI.getVitalTrends(parseInt(patientId.toString()), selectedVitalType, trendDays) : Promise.reject('No patient ID'),
    enabled: !!patientId,
    staleTime: 1000 * 60 * 5,
  });

  const { 
    data: vitalSummary, 
    isLoading: vitalSummaryLoading 
  } = useQuery({
    queryKey: ['vital-summary', patientId],
    queryFn: () => patientId ? vitalsAPI.getVitalSummary(parseInt(patientId.toString())) : Promise.reject('No patient ID'),
    enabled: !!patientId,
    staleTime: 1000 * 60 * 5,
  });

  const { 
    data: goals = [], 
    isLoading: goalsLoading 
  } = useQuery({
    queryKey: ['health-goals', patientId],
    queryFn: () => patientId ? vitalsAPI.getGoals(parseInt(patientId.toString())) : Promise.reject('No patient ID'),
    enabled: !!patientId,
    staleTime: 1000 * 60 * 5,
  });

  const { 
    data: alerts, 
    isLoading: alertsLoading 
  } = useQuery({
    queryKey: ['vital-alerts', patientId],
    queryFn: () => patientId ? vitalsAPI.getVitalAlerts(parseInt(patientId.toString())) : Promise.reject('No patient ID'),
    enabled: !!patientId,
    staleTime: 1000 * 60 * 2, // 2 minutes
  });

  const { 
    data: vitals = [], 
    isLoading: vitalsLoading 
  } = useQuery({
    queryKey: ['vitals', patientId],
    queryFn: () => patientId ? vitalsAPI.getVitals(parseInt(patientId.toString()), { limit: 50 }) : Promise.reject('No patient ID'),
    enabled: !!patientId,
    staleTime: 1000 * 60 * 5,
  });

  // Early returns for loading/error states (AFTER all hooks)
  if (error) {
    return (
      <div className="p-8 text-center text-red-600 font-semibold">
        {error}
      </div>
    );
  }
  if (isLoadingPatientId) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-gray-600">Loading patient information...</div>
      </div>
    );
  }
  if (!patientId) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-red-600 text-lg font-semibold">Patient ID not found</p>
          <p className="text-gray-600 mt-2">{error || 'Please log in first'}</p>
        </div>
      </div>
    );
  }
  if (isLoading) {
    return <LoadingSpinner />;
  }
  if (summaryError) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-800">Error loading health progress data</p>
      </div>
    );
  }

  if (!patientId) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-red-600 text-lg font-semibold">Patient ID not found</p>
          <p className="text-gray-600 mt-2">{error || 'Please log in first'}</p>
        </div>
      </div>
    );
  }

  const isLoading = summaryLoading || trendsLoading || vitalSummaryLoading || goalsLoading || alertsLoading || vitalsLoading;

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (summaryError) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-800">Error loading health progress data</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Health Progress & Charts
          </h1>
          {healthSummary && (
            <p className="mt-2 text-sm text-gray-600">
              Patient: <span className="font-semibold">{healthSummary.patient_name}</span>
            </p>
          )}
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="flex overflow-x-auto border-b border-gray-200">
            {TABS.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-6 py-4 whitespace-nowrap font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-indigo-50 text-indigo-700 border-b-2 border-indigo-600'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'summary' && (
              <div className="space-y-6">
                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
                    <p className="text-gray-600 text-sm">Total Readings</p>
                    <p className="text-3xl font-bold text-blue-700 mt-2">
                      {healthSummary?.total_readings || 0}
                    </p>
                  </div>
                  <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
                    <p className="text-gray-600 text-sm">Active Goals</p>
                    <p className="text-3xl font-bold text-green-700 mt-2">
                      {healthSummary?.active_goals || 0}
                    </p>
                  </div>
                  <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4 border border-purple-200">
                    <p className="text-gray-600 text-sm">Last Updated</p>
                    <p className="text-sm font-semibold text-purple-700 mt-2">
                      {healthSummary?.latest_readings?.[0]?.recorded_at 
                        ? new Date(healthSummary.latest_readings[0].recorded_at).toLocaleDateString()
                        : 'N/A'
                      }
                    </p>
                  </div>
                </div>

                {/* Latest Vitals */}
                <HealthSummaryCard vitals={vitalSummary} />
              </div>
            )}

            {activeTab === 'trends' && (
              <div className="space-y-6">
                {/* Controls */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Vital Type
                    </label>
                    <select
                      value={selectedVitalType}
                      onChange={(e) => setSelectedVitalType(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    >
                      {VITAL_TYPES.map(type => (
                        <option key={type.value} value={type.value}>
                          {type.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Time Period
                    </label>
                    <select
                      value={trendDays}
                      onChange={(e) => setTrendDays(parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    >
                      <option value={7}>Last 7 days</option>
                      <option value={14}>Last 14 days</option>
                      <option value={30}>Last 30 days</option>
                      <option value={90}>Last 90 days</option>
                    </select>
                  </div>
                </div>

                {/* Trend Chart */}
                <VitalTrendsChart vitalType={selectedVitalType} vitalTrends={vitalTrends} />

                {/* Trend Indicator */}
                {vitalTrends && (
                  <div className="bg-gradient-to-r from-indigo-50 to-blue-50 rounded-lg p-4 border border-indigo-200">
                    <div className="flex items-center gap-2">
                      {vitalTrends.trend_direction === 'improving' && (
                        <>
                          <ArrowTrendingDownIcon className="w-6 h-6 text-green-600" />
                          <div>
                            <p className="font-semibold text-green-700">Improving</p>
                            <p className="text-sm text-gray-600">Values trending in a positive direction</p>
                          </div>
                        </>
                      )}
                      {vitalTrends.trend_direction === 'stable' && (
                        <>
                          <ChartBarIcon className="w-6 h-6 text-blue-600" />
                          <div>
                            <p className="font-semibold text-blue-700">Stable</p>
                            <p className="text-sm text-gray-600">Values remain consistent</p>
                          </div>
                        </>
                      )}
                      {vitalTrends.trend_direction === 'declining' && (
                        <>
                          <ArrowTrendingUpIcon className="w-6 h-6 text-red-600" />
                          <div>
                            <p className="font-semibold text-red-700">Declining</p>
                            <p className="text-sm text-gray-600">Values trending in a negative direction</p>
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                )}

                {/* Statistics */}
                {vitalTrends && vitalTrends.stats && (
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-white p-4 rounded-lg border border-gray-200">
                      <p className="text-gray-600 text-sm">Average</p>
                      <p className="text-2xl font-bold text-indigo-600 mt-2">
                        {vitalTrends.stats.avg_value?.toFixed(1) || 'N/A'}
                      </p>
                    </div>
                    <div className="bg-white p-4 rounded-lg border border-gray-200">
                      <p className="text-gray-600 text-sm">Minimum</p>
                      <p className="text-2xl font-bold text-green-600 mt-2">
                        {vitalTrends.stats.min_value?.toFixed(1) || 'N/A'}
                      </p>
                    </div>
                    <div className="bg-white p-4 rounded-lg border border-gray-200">
                      <p className="text-gray-600 text-sm">Maximum</p>
                      <p className="text-2xl font-bold text-red-600 mt-2">
                        {vitalTrends.stats.max_value?.toFixed(1) || 'N/A'}
                      </p>
                    </div>
                    <div className="bg-white p-4 rounded-lg border border-gray-200">
                      <p className="text-gray-600 text-sm">Readings</p>
                      <p className="text-2xl font-bold text-gray-700 mt-2">
                        {vitalTrends.readings.length}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'goals' && (
              <HealthGoalsPanel goals={goals} patientId={patientId!} />
            )}

            {activeTab === 'alerts' && (
              <VitalAlertsPanel alerts={alerts} />
            )}

            {activeTab === 'readings' && (
              <VitalReadingsList vitals={vitals} patientId={patientId!} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default HealthProgressChartPage;
