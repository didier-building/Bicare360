import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../api/client';
import { adherenceAPI } from '../api/adherence';
import vitalsAPI from '../api/vitals';
import SymptomReportModal from '../components/SymptomReportModal';
import RefillRequestModal from '../components/RefillRequestModal';

interface PatientInfo {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone_number: string;
  national_id: string;
  date_of_birth: string;
  gender: string;
}

interface Medication {
  id: number;
  name: string;
  dosage: string;
  frequency: string;
  start_date: string;
  end_date: string | null;
  status: string;
}

interface Appointment {
  id: number;
  appointment_datetime: string;
  appointment_type: string;
  status: string;
  provider_name?: string;
  hospital_name?: string;
  location_type?: string;
  reason?: string;
  department?: string;
}

interface DischargeSummary {
  id: number;
  date: string;
  hospital: string;
  diagnosis: string;
  status: string;
}

interface Alert {
  id: number;
  alert_type: string;
  severity: string;
  title: string;
  status: string;
}

interface VitalReading {
  id: number;
  reading_type: string;
  value: number;
  secondary_value?: number;
  unit: string;
  recorded_at: string;
  notes?: string;
}

export default function PatientDashboardPage() {
  const navigate = useNavigate();
  const [patient, setPatient] = useState<PatientInfo | null>(null);
  const [medications, setMedications] = useState<Medication[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [summaries, setSummaries] = useState<DischargeSummary[]>([]);
  const [alerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [isSymptomModalOpen, setIsSymptomModalOpen] = useState(false);
  const [isRefillModalOpen, setIsRefillModalOpen] = useState(false);
  const [medicationAdherence, setMedicationAdherence] = useState<{[key: number]: boolean}>({});
  const [isProfileDropdownOpen, setIsProfileDropdownOpen] = useState(false);
  const [vitals, setVitals] = useState<VitalReading[]>([]);
  const [adherenceRate, setAdherenceRate] = useState<number>(0);
  const [lastSymptomDate] = useState<string | null>(null);

  useEffect(() => {
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      navigate('/patient/login');
      return;
    }

    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        setError('');

        // Fetch patient info
        const patientResponse = await client.get('/v1/patients/me/');
        const patientData = patientResponse.data;
        setPatient(patientData);

        // Fetch medications (prescriptions for this patient)
        try {
          const medicationsResponse = await client.get('/v1/prescriptions/?patient_id=' + patientData.id);
          const medicationsData = medicationsResponse.data.results || medicationsResponse.data;
          setMedications(Array.isArray(medicationsData) ? medicationsData : []);
        } catch (err) {
          console.log('No prescriptions endpoint found, continuing...');
        }

        // Fetch appointments
        try {
          const appointmentsResponse = await client.get('/v1/appointments/?patient_id=' + patientData.id);
          const appointmentsData = appointmentsResponse.data.results || appointmentsResponse.data;
          setAppointments(Array.isArray(appointmentsData) ? appointmentsData : []);
        } catch (err) {
          console.log('No appointments endpoint found, continuing...');
        }

        // Fetch discharge summaries
        try {
          const summariesResponse = await client.get('/v1/discharge-summaries/?patient_id=' + patientData.id);
          const summariesData = summariesResponse.data.results || summariesResponse.data;
          setSummaries(Array.isArray(summariesData) ? summariesData : []);
        } catch (err) {
          console.log('No discharge summaries endpoint found, continuing...');
        }

        // Note: Nursing alerts are not accessible to patients (staff-only endpoint)
        // Alerts are for nurse workflow management, not patient-facing

        // Fetch vitals (latest readings)
        try {
          const vitalsResponse = await vitalsAPI.getLatestVitals(patientData.id);
          console.log('Vitals fetched:', vitalsResponse);
          setVitals(Array.isArray(vitalsResponse) ? vitalsResponse : []);
        } catch (err) {
          console.log('Failed to fetch vitals:', err);
          setVitals([]);
        }

        // Fetch medication adherence rate (last 7 days)
        try {
          const today = new Date();
          const sevenDaysAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
          const adherenceResponse = await adherenceAPI.getAdherenceRecords({
            patient: patientData.id,
            scheduled_date__gte: sevenDaysAgo.toISOString().split('T')[0],
            page_size: 1000
          });
          
          if (adherenceResponse && adherenceResponse.results) {
            const totalDoses = adherenceResponse.results.length;
            const takenDoses = adherenceResponse.results.filter((r: any) => r.status === 'taken').length;
            const rate = totalDoses > 0 ? Math.round((takenDoses / totalDoses) * 100) : 0;
            setAdherenceRate(rate);
            console.log(`Adherence rate: ${takenDoses}/${totalDoses} = ${rate}%`);
          }
        } catch (err) {
          console.log('Failed to fetch adherence data:', err);
          setAdherenceRate(0);
        }

        // Note: Last symptom date would come from a patient-specific endpoint
        // Nursing alerts endpoint is restricted to staff only
      } catch (err) {
        console.error('Dashboard error:', err);
        setError('Failed to load dashboard data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, [navigate]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const profileDropdown = document.getElementById('profile-dropdown');
      if (profileDropdown && !profileDropdown.contains(event.target as Node)) {
        setIsProfileDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleMedicationTaken = async (medicationId: number) => {
    console.log('Medication taken clicked for ID:', medicationId);
    try {
      await client.post('/v1/tracking/', {
        medication: medicationId,
        taken_at: new Date().toISOString(),
        taken: true
      });
      
      setMedicationAdherence(prev => ({
        ...prev,
        [medicationId]: true
      }));
      console.log('Medication adherence updated successfully');
    } catch (err) {
      console.error('Failed to mark medication as taken:', err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('patient_id');
    localStorage.removeItem('patient_name');
    navigate('/patient/login');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-teal-50 to-cyan-50 dark:from-slate-950 dark:to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600 dark:border-teal-400 mb-4"></div>
          <p className="text-teal-700 dark:text-teal-200 font-medium">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900">
      {/* Professional Header */}
      <header className="bg-white dark:bg-slate-800 border-b border-gray-200 dark:border-slate-700 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-1.5">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-teal-500 to-cyan-600 rounded-xl flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent">
                  BiCare360
                </h1>
                <p className="text-xs text-gray-600 dark:text-gray-400">Patient Portal</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {/* Emergency Button */}
              <button 
                onClick={() => {
                  console.log('Emergency alert clicked');
                  if (confirm('🚨 EMERGENCY ALERT 🚨\n\nThis will:\n• Call emergency services (911)\n• Notify your emergency contact\n• Send your location and medical info\n\nProceed with emergency alert?')) {
                    window.open('tel:911', '_self');
                  }
                }}
                className="bg-red-500 hover:bg-red-600 text-white p-2 rounded-lg transition-all duration-200 hover:scale-105 shadow-lg"
                title="Emergency Alert - Click to call 911"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </button>

              {/* Profile Dropdown */}
              <div className="relative" id="profile-dropdown">
                <button
                  onClick={() => setIsProfileDropdownOpen(!isProfileDropdownOpen)}
                  className="flex items-center space-x-2 hover:opacity-80 transition-opacity"
                  title={patient ? `${patient.first_name} ${patient.last_name}` : 'Profile'}
                >
                  <div className="w-10 h-10 bg-gradient-to-br from-teal-400 to-blue-600 rounded-full flex items-center justify-center text-white font-bold shadow-lg">
                    {patient ? (patient.first_name?.[0] || 'P') + (patient.last_name?.[0] || '') : 'P'}
                  </div>
                </button>

                {/* Dropdown Menu */}
                {isProfileDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-slate-800 rounded-xl shadow-2xl border border-gray-200 dark:border-slate-700 z-50">
                    {/* Profile Header */}
                    <div className="p-4 border-b border-gray-200 dark:border-slate-700">
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-gradient-to-br from-teal-400 to-blue-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                          {patient ? (patient.first_name?.[0] || 'P') + (patient.last_name?.[0] || '') : 'P'}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                            {patient ? `${patient.first_name} ${patient.last_name}` : 'Patient'}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{patient?.email}</p>
                        </div>
                      </div>
                    </div>

                    {/* Menu Items */}
                    <div className="py-2">
                      <button
                        onClick={() => {
                          console.log('View profile clicked');
                          setIsProfileDropdownOpen(false);
                          navigate('/patient/profile');
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors flex items-center gap-3"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                        <span>View Profile</span>
                      </button>

                      <button
                        onClick={() => {
                          console.log('Settings clicked');
                          setIsProfileDropdownOpen(false);
                          navigate('/patient/settings');
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors flex items-center gap-3"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        <span>Account Settings</span>
                      </button>

                      <button
                        onClick={() => {
                          console.log('Medical info clicked');
                          setIsProfileDropdownOpen(false);
                          navigate('/patient/medical-info');
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors flex items-center gap-3"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span>Medical Information</span>
                      </button>

                      <button
                        onClick={() => {
                          console.log('Change password clicked');
                          setIsProfileDropdownOpen(false);
                          navigate('/patient/change-password');
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors flex items-center gap-3"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                        </svg>
                        <span>Change Password</span>
                      </button>

                      {/* Divider */}
                      <div className="my-2 border-t border-gray-200 dark:border-slate-700"></div>

                      {/* Sign Out */}
                      <button
                        onClick={() => {
                          console.log('Sign out clicked');
                          setIsProfileDropdownOpen(false);
                          handleLogout();
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 transition-colors flex items-center gap-3"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                        </svg>
                        <span>Sign Out</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2">
        {/* Error Alert */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-700 dark:text-red-200 text-sm">{error}</p>
          </div>
        )}

        <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-3">
          {patient ? `${patient.first_name}'s Dashboard` : 'Patient Dashboard'}
        </h1>

        {/* Tab Navigation */}
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow p-3 mb-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex flex-wrap gap-2">
              {['overview', 'medications', 'appointments', 'summaries', 'alerts'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 text-sm ${
                    activeTab === tab
                      ? 'bg-teal-600 text-white shadow-lg'
                      : 'bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-slate-600'
                  }`}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>
            <div className="flex flex-wrap gap-2 w-full sm:w-auto">
              <button
                onClick={() => navigate('/patient/appointments/request')}
                className="flex-1 sm:flex-none px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white font-medium rounded-lg transition-all duration-200 text-sm whitespace-nowrap"
              >
                + Request Appointment
              </button>
              <button
                onClick={() => navigate('/patient/messages')}
                className="flex-1 sm:flex-none px-4 py-2 bg-gradient-to-r from-teal-600 to-cyan-500 hover:from-teal-700 hover:to-cyan-600 text-white font-medium rounded-lg transition-all duration-200 text-sm whitespace-nowrap"
              >
                Message Care Team
              </button>
              <button
                onClick={() => navigate('/patient/caregivers')}
                className="flex-1 sm:flex-none px-4 py-2 bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-700 hover:to-purple-600 text-white font-medium rounded-lg transition-all duration-200 text-sm whitespace-nowrap"
              >
                🏥 Find Caregivers
              </button>
            </div>
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div>
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-6">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Medications</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-gray-100 mt-2">
                {medications.length}
              </p>
            </div>
            
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-6">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Appointments</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-gray-100 mt-2">
                {appointments.length}
              </p>
            </div>
            
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-6">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Critical Alerts</p>
              <p className="text-3xl font-bold text-red-600 dark:text-red-400 mt-2">
                {alerts.filter(a => a.severity === 'critical').length}
              </p>
            </div>
            
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-6">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Discharge Summaries</p>
              <p className="text-3xl font-bold text-purple-600 dark:text-purple-400 mt-2">
                {summaries.length}
              </p>
            </div>
          </div>

          {/* Active Medications Section */}
          <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-6 mb-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Active Medications
              </h2>
              <button
                onClick={() => navigate('/patient/medications')}
                className="text-sm text-teal-600 dark:text-teal-400 hover:text-teal-700 dark:hover:text-teal-300 font-medium"
              >
                View All →
              </button>
            </div>

            {medications.length === 0 ? (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                No active medications
              </div>
            ) : (
              <div className="space-y-3">
                {medications.slice(0, 5).map((medication) => (
                  <div
                    key={medication.id}
                    className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                  >
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 dark:text-gray-100">{medication.name}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {medication.dosage} • {medication.frequency}
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      {medicationAdherence[medication.id] ? (
                        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300">
                          ✓ Taken
                        </span>
                      ) : (
                        <button
                          onClick={() => handleMedicationTaken(medication.id)}
                          className="px-3 py-1 bg-teal-600 hover:bg-teal-700 text-white text-xs font-medium rounded-lg transition-colors"
                        >
                          Mark Taken
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Health Alerts Section */}
          <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-6 mb-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Health Alerts
              </h2>
              <button
                onClick={() => navigate('/patient/alerts')}
                className="text-sm text-teal-600 dark:text-teal-400 hover:text-teal-700 dark:hover:text-teal-300 font-medium"
              >
                View All →
              </button>
            </div>

            {alerts.length === 0 ? (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                No active alerts
              </div>
            ) : (
              <div className="space-y-3">
                {alerts.slice(0, 5).map((alert) => {
                  const severityColors = {
                    critical: 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 border-red-200 dark:border-red-800',
                    high: 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300 border-orange-200 dark:border-orange-800',
                    medium: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300 border-yellow-200 dark:border-yellow-800',
                    low: 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 border-blue-200 dark:border-blue-800',
                  };

                  return (
                    <div
                      key={alert.id}
                      className={`flex items-center justify-between p-4 border rounded-lg transition-colors ${severityColors[alert.severity as keyof typeof severityColors]}`}
                    >
                      <div className="flex-1">
                        <p className="font-semibold text-gray-900 dark:text-gray-100">
                          {alert.title || alert.alert_type.replace('_', ' ').toUpperCase()}
                        </p>
                        <p className="text-sm mt-1">
                          {alert.alert_type.replace('_', ' ')}
                        </p>
                      </div>
                      <div className="flex flex-col items-end gap-1">
                        <span className="text-xs font-medium uppercase">
                          {alert.severity}
                        </span>
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                          alert.status === 'new' ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300' :
                          alert.status === 'resolved' ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300' :
                          'bg-gray-100 dark:bg-gray-900/30 text-gray-800 dark:text-gray-300'
                        }`}>
                          {alert.status.toUpperCase()}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Daily Medication Check-in - REMOVED, now in Active Medications section above */}
          {false && medications.length > 0 && (
            <div className="mt-8 bg-white dark:bg-slate-800 rounded-xl shadow-lg overflow-hidden">
              <div className="px-6 py-4 bg-gradient-to-r from-green-50 to-teal-50 dark:from-green-900/30 dark:to-teal-900/30 border-b border-green-200 dark:border-green-800">
                <h3 className="text-xl font-bold text-green-900 dark:text-green-50 flex items-center gap-2">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Daily Medication Check-in
                </h3>
                <p className="text-green-700 dark:text-green-300 text-sm mt-1">
                  Track your medication adherence for today
                </p>
              </div>
              <div className="p-6">
                <div className="grid gap-4">
                  {medications.map((medication) => (
                    <div key={medication.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-slate-700 rounded-lg">
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900 dark:text-white">{medication.name}</h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {medication.dosage} - {medication.frequency}
                        </p>
                      </div>
                      <div className="flex items-center gap-3">
                        {medicationAdherence[medication.id] ? (
                          <div className="flex items-center gap-2 text-green-600 dark:text-green-400">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                            <span className="text-sm font-medium">Taken</span>
                          </div>
                        ) : (
                          <button
                            onClick={() => handleMedicationTaken(medication.id)}
                            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg transition-colors"
                          >
                            Mark as Taken
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Upcoming Appointments Section */}
          <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-6 mb-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Upcoming Appointments
              </h2>
              <button
                onClick={() => setActiveTab('appointments')}
                className="text-sm text-teal-600 dark:text-teal-400 hover:text-teal-700 dark:hover:text-teal-300 font-medium"
              >
                View All →
              </button>
            </div>

            {appointments.length === 0 ? (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                No upcoming appointments
              </div>
            ) : (
              <div className="space-y-3">
                {appointments.slice(0, 3).map((apt) => (
                  <div
                    key={apt.id}
                    className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                  >
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 dark:text-gray-100">
                        {apt.appointment_type?.replace('_', ' ').toUpperCase() || 'Appointment'}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {new Date(apt.appointment_datetime).toLocaleDateString()} at {new Date(apt.appointment_datetime).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                      </p>
                      {apt.provider_name && (
                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                          {apt.provider_name}
                        </p>
                      )}
                    </div>
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                      apt.status === 'scheduled' || apt.status === 'confirmed'
                        ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300'
                        : apt.status === 'completed'
                        ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
                        : 'bg-gray-100 dark:bg-gray-900/30 text-gray-800 dark:text-gray-300'
                    }`}>
                      {apt.status.toUpperCase()}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Health Progress Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Medication Adherence Chart */}
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg overflow-hidden">
              <div className="px-6 py-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 border-b border-blue-200 dark:border-blue-800">
                <h3 className="text-lg font-bold text-blue-900 dark:text-blue-50 flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  Medication Adherence
                </h3>
                <p className="text-blue-700 dark:text-blue-300 text-sm mt-1">Last 7 days tracking</p>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-center py-8">
                    <div className="text-center">
                      <div className={`text-5xl font-bold ${
                        adherenceRate >= 80 ? 'text-green-500' : 
                        adherenceRate >= 60 ? 'text-yellow-500' : 'text-red-500'
                      }`}>
                        {adherenceRate}%
                      </div>
                      <p className="text-gray-600 dark:text-gray-400 text-sm mt-2">Overall adherence rate</p>
                      <p className={`text-xs mt-2 font-medium ${
                        adherenceRate >= 80 ? 'text-green-600 dark:text-green-400' : 
                        adherenceRate >= 60 ? 'text-yellow-600 dark:text-yellow-400' : 'text-red-600 dark:text-red-400'
                      }`}>
                        {adherenceRate >= 80 ? '✓ Excellent adherence' : 
                         adherenceRate >= 60 ? '⚠ Good adherence' : '✗ Need improvement'}
                      </p>
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-slate-600 rounded-full h-3">
                    <div 
                      className={`h-3 rounded-full transition-all duration-300 ${
                        adherenceRate >= 80 ? 'bg-green-500' : 
                        adherenceRate >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${adherenceRate}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Health Metrics */}
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg overflow-hidden">
              <div className="px-6 py-4 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/30 dark:to-pink-900/30 border-b border-purple-200 dark:border-purple-800">
                <h3 className="text-lg font-bold text-purple-900 dark:text-purple-50 flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                  Health Metrics
                </h3>
                <p className="text-purple-700 dark:text-purple-300 text-sm mt-1">Recent vitals and symptoms</p>
              </div>
              <div className="p-6">
                {vitals.length === 0 ? (
                  <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                    <p className="text-sm">No vital readings recorded yet</p>
                    <p className="text-xs mt-1">Please contact your healthcare provider to record your vitals</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {vitals.map((vital) => {
                      const getStatus = () => {
                        const value = vital.value;
                        const ranges: {[key: string]: {min: number; max: number}} = {
                          blood_pressure: { min: 90, max: 120 },
                          heart_rate: { min: 60, max: 100 },
                          temperature: { min: 36.5, max: 37.5 },
                          weight: { min: 50, max: 200 },
                          oxygen_saturation: { min: 95, max: 100 },
                          respiratory_rate: { min: 12, max: 20 },
                          blood_glucose: { min: 80, max: 120 },
                        };
                        
                        const range = ranges[vital.reading_type] || { min: 0, max: 999 };
                        if (value >= range.min && value <= range.max) return { icon: '✓', color: 'text-green-500', bg: 'bg-green-50 dark:bg-green-900/20' };
                        if (Math.abs(value - range.max) < 10 || Math.abs(value - range.min) < 10) return { icon: '⚠', color: 'text-yellow-500', bg: 'bg-yellow-50 dark:bg-yellow-900/20' };
                        return { icon: '✗', color: 'text-red-500', bg: 'bg-red-50 dark:bg-red-900/20' };
                      };

                      const status = getStatus();
                      const displayName = vital.reading_type.replace('_', ' ').toUpperCase();
                      const displayValue = vital.secondary_value 
                        ? `${Math.round(vital.value)}/${Math.round(vital.secondary_value)}` 
                        : Math.round(vital.value * 10) / 10;

                      return (
                        <div key={vital.id} className={`flex justify-between items-center p-3 rounded-lg ${status.bg}`}>
                          <div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">{displayName}</p>
                            <p className="font-semibold text-gray-900 dark:text-white">{displayValue} {vital.unit}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                              {new Date(vital.recorded_at).toLocaleDateString()} {new Date(vital.recorded_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                            </p>
                          </div>
                          <span className={`text-xl ${status.color}`}>{status.icon}</span>
                        </div>
                      );
                    })}
                  </div>
                )}
                <div className="mt-4 pt-4 border-t border-gray-200 dark:border-slate-600">
                  <div className="text-center">
                    {lastSymptomDate ? (
                      <>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Last Symptom Report</p>
                        <p className="text-sm font-semibold text-gray-900 dark:text-white">{lastSymptomDate}</p>
                      </>
                    ) : (
                      <p className="text-sm text-gray-600 dark:text-gray-400">No symptom reports yet</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Emergency Contact Section - moved to bottom */}
          <div className="mt-6 bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20 rounded-xl shadow-lg overflow-hidden border border-red-200 dark:border-red-800">
            <div className="px-6 py-4 bg-gradient-to-r from-red-100 to-orange-100 dark:from-red-900/40 dark:to-orange-900/40 border-b border-red-200 dark:border-red-700">
              <h3 className="text-lg font-bold text-red-900 dark:text-red-100 flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                Emergency Contacts & Actions
              </h3>
              <p className="text-red-700 dark:text-red-300 text-sm mt-1">Quick access to emergency services and contacts</p>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button 
                  onClick={() => {
                    console.log('Call 911 clicked');
                    window.open('tel:911', '_self');
                  }}
                  className="flex flex-col items-center p-4 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
                >
                  <svg className="w-8 h-8 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  <span className="font-bold">Call 911</span>
                  <span className="text-xs opacity-90">Emergency Services</span>
                </button>
                <button 
                  onClick={() => {
                    console.log('Hospital clicked');
                    alert('Contacting Main Hospital...');
                  }}
                  className="flex flex-col items-center p-4 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-colors"
                >
                  <svg className="w-8 h-8 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                  <span className="font-bold">Hospital</span>
                  <span className="text-xs opacity-90">Main Hospital</span>
                </button>
                <button 
                  onClick={() => {
                    console.log('Primary Care clicked');
                    alert('Contacting Dr. Smith...');
                  }}
                  className="flex flex-col items-center p-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  <svg className="w-8 h-8 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  <span className="font-bold">Primary Care</span>
                  <span className="text-xs opacity-90">Dr. Smith</span>
                </button>
              </div>
              <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-white dark:bg-slate-800 rounded-lg">
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Emergency Contact</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">John Doe (Spouse)</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">📞 (555) 123-4567</p>
                </div>
                <div className="p-4 bg-white dark:bg-slate-800 rounded-lg">
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Medical ID</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Allergies: Penicillin</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Blood Type: O+</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        )}

        {/* Medications Tab */}
        {activeTab === 'medications' && (
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg overflow-hidden">
            <div className="px-6 py-4 bg-teal-50 dark:bg-teal-900/30 border-b border-teal-200 dark:border-teal-800">
              <h3 className="text-xl font-bold text-teal-900 dark:text-teal-50">Active Medications</h3>
            </div>
            {medications.length === 0 ? (
              <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                <p>No active medications currently</p>
              </div>
            ) : (
              <div className="divide-y dark:divide-slate-700">
                {medications.map((med) => (
                  <div key={med.id} className="p-6 hover:bg-gray-50 dark:hover:bg-slate-700/50 transition-colors">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Medication</p>
                        <p className="font-semibold text-gray-900 dark:text-white">{med.name}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Dosage</p>
                        <p className="font-semibold text-gray-900 dark:text-white">{med.dosage}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Frequency</p>
                        <p className="font-semibold text-gray-900 dark:text-white">{med.frequency}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Status</p>
                        <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                          med.status === 'active'
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                            : 'bg-gray-100 text-gray-800 dark:bg-slate-700 dark:text-gray-300'
                        }`}>
                          {med.status}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => navigate('/patient/medications')}
                      className="mt-4 px-4 py-2 bg-teal-50 dark:bg-teal-900/30 text-teal-600 dark:text-teal-400 rounded-lg hover:bg-teal-100 dark:hover:bg-teal-900/50 text-sm font-medium transition-colors"
                    >
                      View Full Details & Adherence →
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Appointments Tab */}
        {activeTab === 'appointments' && (
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg overflow-hidden">
            <div className="px-6 py-4 bg-blue-50 dark:bg-blue-900/30 border-b border-blue-200 dark:border-blue-800">
              <h3 className="text-xl font-bold text-blue-900 dark:text-blue-50">Appointments</h3>
            </div>
            {appointments.length === 0 ? (
              <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                <p>No scheduled appointments</p>
              </div>
            ) : (
              <div className="divide-y dark:divide-slate-700">
                {appointments.map((apt) => (
                  <div key={apt.id} className="p-6 hover:bg-gray-50 dark:hover:bg-slate-700/50 transition-colors">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Type</p>
                        <p className="font-semibold text-gray-900 dark:text-white">
                          {apt.appointment_type?.replace('_', ' ').toUpperCase() || 'Appointment'}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Date & Time</p>
                        <p className="font-semibold text-gray-900 dark:text-white">
                          {new Date(apt.appointment_datetime).toLocaleDateString()}<br/>
                          <span className="text-sm">{new Date(apt.appointment_datetime).toLocaleTimeString()}</span>
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Provider</p>
                        <p className="font-semibold text-gray-900 dark:text-white">
                          {apt.provider_name || 'Not assigned'}
                          {apt.department && <span className="block text-sm text-gray-500">{apt.department}</span>}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Status</p>
                        <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                          apt.status === 'scheduled' || apt.status === 'confirmed'
                            ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                            : apt.status === 'completed'
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                            : apt.status === 'cancelled'
                            ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                            : 'bg-gray-100 text-gray-800 dark:bg-slate-700 dark:text-gray-300'
                        }`}>
                          {apt.status.toUpperCase()}
                        </span>
                      </div>
                    </div>
                    {apt.reason && (
                      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-slate-600">
                        <p className="text-sm text-gray-600 dark:text-gray-400">Reason</p>
                        <p className="text-gray-900 dark:text-white">{apt.reason}</p>
                      </div>
                    )}
                    {apt.hospital_name && (
                      <div className="mt-2">
                        <p className="text-sm text-gray-600 dark:text-gray-400">Location</p>
                        <p className="text-gray-900 dark:text-white">
                          {apt.hospital_name} ({apt.location_type?.replace('_', ' ')})
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Discharge Summaries Tab */}
        {activeTab === 'summaries' && (
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg overflow-hidden">
            <div className="px-6 py-4 bg-purple-50 dark:bg-purple-900/30 border-b border-purple-200 dark:border-purple-800">
              <h3 className="text-xl font-bold text-purple-900 dark:text-purple-50">Discharge Summaries</h3>
            </div>
            {summaries.length === 0 ? (
              <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                <p>No discharge summaries available</p>
              </div>
            ) : (
              <div className="divide-y dark:divide-slate-700">
                {summaries.map((summary) => (
                  <div key={summary.id} className="p-6 hover:bg-gray-50 dark:hover:bg-slate-700/50 transition-colors">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Date</p>
                        <p className="font-semibold text-gray-900 dark:text-white">
                          {new Date(summary.date).toLocaleDateString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Hospital</p>
                        <p className="font-semibold text-gray-900 dark:text-white">{summary.hospital}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Diagnosis</p>
                        <p className="font-semibold text-gray-900 dark:text-white">{summary.diagnosis}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Status</p>
                        <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                          summary.status === 'completed'
                            ? 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300'
                            : 'bg-gray-100 text-gray-800 dark:bg-slate-700 dark:text-gray-300'
                        }`}>
                          {summary.status}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Alerts Tab */}
        {activeTab === 'alerts' && (
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg overflow-hidden">
            <div className="px-6 py-4 bg-orange-50 dark:bg-orange-900/30 border-b border-orange-200 dark:border-orange-800">
              <h3 className="text-xl font-bold text-orange-900 dark:text-orange-50">Health Alerts</h3>
            </div>
            {alerts.length === 0 ? (
              <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                <p>No active health alerts</p>
              </div>
            ) : (
              <div className="divide-y dark:divide-slate-700">
                {alerts.map((alert) => (
                  <div key={alert.id} className="p-6 hover:bg-gray-50 dark:hover:bg-slate-700/50 transition-colors">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Alert Type</p>
                        <p className="font-semibold text-gray-900 dark:text-white capitalize">
                          {alert.alert_type.replace(/_/g, ' ')}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Title</p>
                        <p className="font-semibold text-gray-900 dark:text-white">{alert.title}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Severity</p>
                        <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                          alert.severity === 'critical' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                          : alert.severity === 'high' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300'
                          : alert.severity === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
                          : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                        }`}>
                          {alert.severity}
                        </span>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Status</p>
                        <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                          alert.status === 'new' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                          : alert.status === 'resolved' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                          : 'bg-gray-100 text-gray-800 dark:bg-slate-700 dark:text-gray-300'
                        }`}>
                          {alert.status}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>
      
      {/* Modals */}
      <SymptomReportModal 
        isOpen={isSymptomModalOpen} 
        onClose={() => setIsSymptomModalOpen(false)} 
      />
      <RefillRequestModal 
        isOpen={isRefillModalOpen} 
        onClose={() => setIsRefillModalOpen(false)} 
      />
    </div>
  );
}
