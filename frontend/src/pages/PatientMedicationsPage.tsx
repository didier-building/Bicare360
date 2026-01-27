import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../api/client';
import toast from 'react-hot-toast';

interface Medication {
  id: number;
  name: string;
  generic_name: string;
  dosage: string;
  frequency: string;
  route: string;
  start_date: string;
  end_date: string | null;
  indication: string;
  status: string;
}

interface Prescription {
  id: number;
  medication: Medication;
  dosage: string;
  frequency: string;
  frequency_times_per_day: number;
  route: string;
  start_date: string;
  end_date: string | null;
  duration_days: number;
  days_remaining: number;
  refills_remaining: number;
  status: string;
  prescriber_name: string;
  indication: string;
}

interface AdherenceRecord {
  id: number;
  prescription: Prescription;
  scheduled_date: string;
  scheduled_time: string;
  status: string;
  taken_at: string | null;
  notes: string;
  reason_missed: string;
  reminder_sent: boolean;
}

export default function PatientMedicationsPage() {
  const navigate = useNavigate();
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
  const [adherenceRecords, setAdherenceRecords] = useState<AdherenceRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'current' | 'history' | 'adherence'>('current');
  const [selectedMonth, setSelectedMonth] = useState(new Date());
  const [adherenceStats, setAdherenceStats] = useState({
    total: 0,
    taken: 0,
    missed: 0,
    percentage: 0,
  });

  // Fetch patient's medications and adherence data
  useEffect(() => {
    const fetchMedicationData = async () => {
      try {
        setIsLoading(true);
        setError('');

        const patientId = localStorage.getItem('patient_id');
        if (!patientId) {
          navigate('/patient/login');
          return;
        }

        // Fetch prescriptions for this patient only
        const prescriptionsResponse = await client.get(`/v1/prescriptions/?patient_id=${patientId}`);
        const presc = prescriptionsResponse.data.results || prescriptionsResponse.data;
        setPrescriptions(presc);

        // Fetch adherence records for this patient only
        const adherenceResponse = await client.get(`/v1/adherence/?patient_id=${patientId}`);
        const records = adherenceResponse.data.results || adherenceResponse.data;
        setAdherenceRecords(records);

        // Calculate adherence stats
        if (records && records.length > 0) {
          const total = records.length;
          const taken = records.filter((r: AdherenceRecord) => r.status === 'taken').length;
          const missed = records.filter((r: AdherenceRecord) => r.status === 'missed').length;
          const percentage = Math.round((taken / total) * 100);

          setAdherenceStats({
            total,
            taken,
            missed,
            percentage,
          });
        }
      } catch (err) {
        console.error('Error fetching medication data:', err);
        setError('Failed to load medication data. Please refresh the page.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchMedicationData();
  }, [navigate]);

  const handleMarkTaken = async (adherenceId: number) => {
    try {
      await client.patch(`/v1/adherence/${adherenceId}/`, {
        status: 'taken',
        taken_at: new Date().toISOString(),
      });

      // Update local state
      setAdherenceRecords((prev) =>
        prev.map((record) =>
          record.id === adherenceId
            ? {
                ...record,
                status: 'taken',
                taken_at: new Date().toISOString(),
              }
            : record
        )
      );

      toast.success('✓ Marked as taken');
    } catch (error) {
      console.error('Error marking adherence:', error);
      toast.error('Failed to update adherence');
    }
  };

  const handleMarkMissed = async (adherenceId: number, reason: string) => {
    try {
      await client.patch(`/v1/adherence/${adherenceId}/`, {
        status: 'missed',
        reason_missed: reason,
      });

      // Update local state
      setAdherenceRecords((prev) =>
        prev.map((record) =>
          record.id === adherenceId
            ? {
                ...record,
                status: 'missed',
                reason_missed: reason,
              }
            : record
        )
      );

      toast.success('✓ Marked as missed');
    } catch (error) {
      console.error('Error marking adherence:', error);
      toast.error('Failed to update adherence');
    }
  };

  const filteredAdherenceRecords = adherenceRecords.filter((record) => {
    const recordDate = new Date(record.scheduled_date);
    return (
      recordDate.getMonth() === selectedMonth.getMonth() &&
      recordDate.getFullYear() === selectedMonth.getFullYear()
    );
  });

  const currentPrescriptions = prescriptions.filter((p) => p.status === 'active');
  const historicalPrescriptions = prescriptions.filter((p) => p.status !== 'active');

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-teal-50 to-cyan-50 dark:from-slate-950 dark:to-slate-900 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600 dark:border-teal-400 mb-4"></div>
          <p className="text-teal-700 dark:text-teal-200 font-medium">Loading your medications...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-950 pb-12">
      {/* Header */}
      <header className="bg-gradient-to-r from-teal-600 to-teal-500 dark:from-teal-900 dark:to-teal-800 shadow-lg sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-white">Medications</h1>
              <p className="text-teal-100 text-sm mt-1">Track your prescriptions and adherence</p>
            </div>
            <button
              onClick={() => navigate('/patient/dashboard')}
              className="px-3 sm:px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors text-sm sm:text-base"
            >
              ← Back
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-700 dark:text-red-200">{error}</p>
          </div>
        )}

        {/* Adherence Stats Card */}
        {adherenceRecords.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-8">
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Adherence Rate</p>
              <div className="flex items-center gap-2">
                <div className="text-3xl font-bold text-teal-600 dark:text-teal-400">
                  {adherenceStats.percentage}%
                </div>
              </div>
              <div className="w-full bg-gray-200 dark:bg-slate-700 rounded-full h-2 mt-3">
                <div
                  className="bg-teal-600 h-2 rounded-full transition-all"
                  style={{ width: `${adherenceStats.percentage}%` }}
                ></div>
              </div>
            </div>

            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Total Doses</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">{adherenceStats.total}</p>
            </div>

            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Doses Taken</p>
              <p className="text-3xl font-bold text-green-600 dark:text-green-400">{adherenceStats.taken}</p>
            </div>

            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Doses Missed</p>
              <p className="text-3xl font-bold text-red-600 dark:text-red-400">{adherenceStats.missed}</p>
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-2 mb-8 bg-white dark:bg-slate-800 rounded-xl shadow p-4">
          {(['current', 'history', 'adherence'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-2 rounded-lg font-medium transition-all duration-200 text-sm sm:text-base ${
                activeTab === tab
                  ? 'bg-teal-600 text-white shadow-lg'
                  : 'bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-slate-600'
              }`}
            >
              {tab === 'current' && '💊 Current'}
              {tab === 'history' && '📋 History'}
              {tab === 'adherence' && '📅 Adherence'}
            </button>
          ))}
        </div>

        {/* Current Prescriptions Tab */}
        {activeTab === 'current' && (
          <div className="space-y-4">
            {currentPrescriptions.length === 0 ? (
              <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-8 text-center">
                <p className="text-gray-600 dark:text-gray-400">No active medications</p>
              </div>
            ) : (
              currentPrescriptions.map((prescription) => (
                <div
                  key={prescription.id}
                  className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow"
                >
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                    <div>
                      <h3 className="text-lg sm:text-xl font-bold text-gray-900 dark:text-white">
                        {prescription.medication.name}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Generic: {prescription.medication.generic_name}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="inline-block px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300">
                        Active
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 py-4 border-t border-b border-gray-200 dark:border-slate-700">
                    <div>
                      <p className="text-xs text-gray-600 dark:text-gray-400 uppercase font-semibold mb-1">
                        Dosage
                      </p>
                      <p className="text-sm sm:text-base font-semibold text-gray-900 dark:text-white">
                        {prescription.dosage}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600 dark:text-gray-400 uppercase font-semibold mb-1">
                        Frequency
                      </p>
                      <p className="text-sm sm:text-base font-semibold text-gray-900 dark:text-white">
                        {prescription.frequency_times_per_day}x daily
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600 dark:text-gray-400 uppercase font-semibold mb-1">
                        Route
                      </p>
                      <p className="text-sm sm:text-base font-semibold text-gray-900 dark:text-white">
                        {prescription.route}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600 dark:text-gray-400 uppercase font-semibold mb-1">
                        Days Left
                      </p>
                      <p
                        className={`text-sm sm:text-base font-semibold ${
                          prescription.days_remaining <= 7
                            ? 'text-red-600 dark:text-red-400'
                            : 'text-teal-600 dark:text-teal-400'
                        }`}
                      >
                        {prescription.days_remaining} days
                      </p>
                    </div>
                  </div>

                  <div className="mt-4 space-y-2">
                    <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                      📋 Indication: {prescription.indication}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Prescribed by: {prescription.prescriber_name}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-500">
                      From {new Date(prescription.start_date).toLocaleDateString()} to{' '}
                      {prescription.end_date
                        ? new Date(prescription.end_date).toLocaleDateString()
                        : 'Ongoing'}
                    </p>
                  </div>

                  {prescription.refills_remaining > 0 && (
                    <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-lg">
                      <p className="text-sm text-blue-700 dark:text-blue-200">
                        💊 {prescription.refills_remaining} refill(s) remaining
                      </p>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {/* Historical Prescriptions Tab */}
        {activeTab === 'history' && (
          <div className="space-y-4">
            {historicalPrescriptions.length === 0 ? (
              <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-8 text-center">
                <p className="text-gray-600 dark:text-gray-400">No historical medications</p>
              </div>
            ) : (
              historicalPrescriptions.map((prescription) => (
                <div
                  key={prescription.id}
                  className="bg-white dark:bg-slate-800 rounded-xl shadow p-6 opacity-75"
                >
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                    <div>
                      <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                        {prescription.medication.name}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {prescription.dosage} - {prescription.frequency_times_per_day}x daily
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="inline-block px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800 dark:bg-slate-700 dark:text-gray-300">
                        Completed
                      </span>
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {new Date(prescription.start_date).toLocaleDateString()} to{' '}
                    {prescription.end_date
                      ? new Date(prescription.end_date).toLocaleDateString()
                      : 'N/A'}
                  </p>
                </div>
              ))
            )}
          </div>
        )}

        {/* Adherence Calendar Tab */}
        {activeTab === 'adherence' && (
          <div className="space-y-6">
            {/* Month Navigation */}
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <button
                  onClick={() =>
                    setSelectedMonth(new Date(selectedMonth.getFullYear(), selectedMonth.getMonth() - 1))
                  }
                  className="px-4 py-2 bg-gray-100 dark:bg-slate-700 hover:bg-gray-200 dark:hover:bg-slate-600 rounded-lg transition-colors"
                >
                  ← Prev
                </button>

                <h3 className="text-lg sm:text-xl font-bold text-gray-900 dark:text-white">
                  {selectedMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                </h3>

                <button
                  onClick={() =>
                    setSelectedMonth(new Date(selectedMonth.getFullYear(), selectedMonth.getMonth() + 1))
                  }
                  className="px-4 py-2 bg-gray-100 dark:bg-slate-700 hover:bg-gray-200 dark:hover:bg-slate-600 rounded-lg transition-colors"
                >
                  Next →
                </button>
              </div>

              {/* Adherence Records */}
              <div className="space-y-3">
                {filteredAdherenceRecords.length === 0 ? (
                  <p className="text-center text-gray-600 dark:text-gray-400">No records for this month</p>
                ) : (
                  filteredAdherenceRecords.map((record) => (
                    <div
                      key={record.id}
                      className={`p-4 border-l-4 rounded-lg ${
                        record.status === 'taken'
                          ? 'border-green-500 bg-green-50 dark:bg-green-900/20'
                          : record.status === 'missed'
                          ? 'border-red-500 bg-red-50 dark:bg-red-900/20'
                          : 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20'
                      }`}
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                        <div>
                          <p className="font-semibold text-gray-900 dark:text-white">
                            {new Date(record.scheduled_date).toLocaleDateString()} at {record.scheduled_time}
                          </p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {record.prescription.medication.name} - {record.prescription.dosage}
                          </p>
                        </div>
                        <div className="flex gap-2">
                          {record.status === 'scheduled' && (
                            <>
                              <button
                                onClick={() => handleMarkTaken(record.id)}
                                className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded-lg transition-colors"
                              >
                                ✓ Taken
                              </button>
                              <button
                                onClick={() => handleMarkMissed(record.id, 'User marked as missed')}
                                className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded-lg transition-colors"
                              >
                                ✕ Missed
                              </button>
                            </>
                          )}
                          {record.status === 'taken' && (
                            <span className="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 text-sm rounded-lg font-medium">
                              ✓ Taken
                            </span>
                          )}
                          {record.status === 'missed' && (
                            <span className="px-3 py-1 bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 text-sm rounded-lg font-medium">
                              ✕ Missed
                            </span>
                          )}
                        </div>
                      </div>
                      {record.notes && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">Note: {record.notes}</p>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
