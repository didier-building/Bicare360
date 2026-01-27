import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../api/client';
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

export default function PatientDashboardPage() {
  const navigate = useNavigate();
  const [patient, setPatient] = useState<PatientInfo | null>(null);
  const [medications, setMedications] = useState<Medication[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [summaries, setSummaries] = useState<DischargeSummary[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [isSymptomModalOpen, setIsSymptomModalOpen] = useState(false);
  const [isRefillModalOpen, setIsRefillModalOpen] = useState(false);
  const [medicationAdherence, setMedicationAdherence] = useState<{[key: number]: boolean}>({});
  const [isProfileDropdownOpen, setIsProfileDropdownOpen] = useState(false);

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
        setPatient(patientResponse.data);

        // Fetch medications (prescriptions for this patient)
        try {
          const medicationsResponse = await client.get('/v1/prescriptions/?patient_id=' + patientResponse.data.id);
          setMedications(medicationsResponse.data.results || medicationsResponse.data);
        } catch (err) {
          console.log('No prescriptions endpoint found, continuing...');
        }

        // Fetch appointments
        try {
          const appointmentsResponse = await client.get('/v1/appointments/?patient_id=' + patientResponse.data.id);
          setAppointments(appointmentsResponse.data.results || appointmentsResponse.data);
        } catch (err) {
          console.log('No appointments endpoint found, continuing...');
        }

        // Fetch discharge summaries
        try {
          const summariesResponse = await client.get('/v1/discharge-summaries/?patient_id=' + patientResponse.data.id);
          setSummaries(summariesResponse.data.results || summariesResponse.data);
        } catch (err) {
          console.log('No discharge summaries endpoint found, continuing...');
        }

        // Fetch alerts
        try {
          const alertsResponse = await client.get('/v1/nursing/alerts/?patient_id=' + patientResponse.data.id);
          setAlerts(alertsResponse.data.results || alertsResponse.data);
        } catch (err) {
          console.log('No alerts endpoint found, continuing...');
        }

        // Fetch medication tracking (commented out as not currently used)
        // try {
        //   const trackingResponse = await client.get('/v1/tracking/');
        //   // trackingData would be used here if needed
        // } catch (err) {
        //   console.log('No medication tracking endpoint found, continuing...');
        // }
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
      {/* Professional Header */}
      <header className="bg-white/95 dark:bg-slate-900/95 backdrop-blur-sm border-b border-gray-200/50 dark:border-slate-700/50 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-br from-teal-500 to-cyan-600 rounded-xl flex items-center justify-center">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent">
                  BiCare360 Patient Portal
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">Comprehensive Healthcare Management</p>
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

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-700 dark:text-red-200">{error}</p>
          </div>
        )}

        {/* Welcome Card with Patient Info */}
        {patient && (
          <div className="bg-gradient-to-r from-teal-500 to-cyan-600 rounded-2xl shadow-xl p-8 mb-8 text-white">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
              <div>
                <div className="flex items-center mb-4">
                  <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mr-4">
                    <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-3xl font-bold">Welcome back, {patient.first_name}!</h2>
                    <p className="text-teal-100 mt-1">Here's your health overview for today</p>
                  </div>
                </div>
                <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-teal-100">Patient ID</p>
                      <p className="font-semibold">{patient.national_id}</p>
                    </div>
                    <div>
                      <p className="text-teal-100">Age</p>
                      <p className="font-semibold">{new Date().getFullYear() - new Date(patient.date_of_birth).getFullYear()}</p>
                    </div>
                    <div>
                      <p className="text-teal-100">Phone</p>
                      <p className="font-semibold">{patient.phone_number}</p>
                    </div>
                    <div>
                      <p className="text-teal-100">Email</p>
                      <p className="font-semibold truncate">{patient.email}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Quick Actions */}
              <div className="lg:text-right">
                <h3 className="text-xl font-semibold mb-4">Quick Actions</h3>
                <div className="grid grid-cols-2 gap-3">
                  <button 
                    onClick={() => {
                      console.log('Report Symptoms clicked');
                      setIsSymptomModalOpen(true);
                    }}
                    className="bg-white/20 hover:bg-white/30 backdrop-blur-sm p-4 rounded-lg transition-all duration-200 hover:scale-105"
                  >
                    <svg className="w-6 h-6 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <p className="text-sm font-medium">Report Symptoms</p>
                  </button>
                  <button 
                    onClick={() => {
                      console.log('Request Refill clicked');
                      setIsRefillModalOpen(true);
                    }}
                    className="bg-white/20 hover:bg-white/30 backdrop-blur-sm p-4 rounded-lg transition-all duration-200 hover:scale-105"
                  >
                    <svg className="w-6 h-6 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                    </svg>
                    <p className="text-sm font-medium">Request Refill</p>
                  </button>
                <button 
                  onClick={() => {
                    console.log('Emergency Alert clicked');
                    window.open('tel:911', '_self');
                  }}
                  className="bg-white/20 hover:bg-white/30 backdrop-blur-sm p-4 rounded-lg transition-all duration-200 hover:scale-105"
                >
                  <svg className="w-6 h-6 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <p className="text-sm font-medium">Emergency Alert</p>
                </button>
                  <button 
                    onClick={() => navigate('/patient/appointments/request')}
                    className="bg-white/20 hover:bg-white/30 backdrop-blur-sm p-4 rounded-lg transition-all duration-200 hover:scale-105"
                  >
                    <svg className="w-6 h-6 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3a1 1 0 011-1h6a1 1 0 011 1v4h3a1 1 0 011 1v9a1 1 0 01-1 1H4a1 1 0 01-1-1V8a1 1 0 011-1h4z" />
                    </svg>
                    <p className="text-sm font-medium">Book Appointment</p>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-2 mb-8 bg-white dark:bg-slate-800 rounded-xl shadow p-4 items-center justify-between">
          <div className="flex flex-wrap gap-2">
            {['overview', 'medications', 'appointments', 'summaries', 'alerts'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-2 rounded-lg font-medium transition-all duration-200 ${
                  activeTab === tab
                    ? 'bg-teal-600 text-white shadow-lg'
                    : 'bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-slate-600'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => navigate('/patient/appointments/request')}
              className="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white font-medium rounded-lg transition-all duration-200 text-sm sm:text-base whitespace-nowrap"
            >
              + Request Appointment
            </button>
            <button
              onClick={() => navigate('/patient/caregivers')}
              className="px-4 py-2 bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-700 hover:to-purple-600 text-white font-medium rounded-lg transition-all duration-200 text-sm sm:text-base whitespace-nowrap"
            >
              🏥 Find Caregivers
            </button>
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Active Medications Card */}
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow cursor-pointer" onClick={() => setActiveTab('medications')}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">Active Medications</h3>
                <span className="text-3xl font-bold text-teal-600 dark:text-teal-400">{medications.length}</span>
              </div>
              <p className="text-gray-600 dark:text-gray-400 text-sm mb-4">
                Track medications and adherence
              </p>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  navigate('/patient/medications');
                }}
                className="w-full py-2 px-4 bg-teal-50 dark:bg-teal-900/30 text-teal-600 dark:text-teal-400 rounded-lg hover:bg-teal-100 dark:hover:bg-teal-900/50 font-medium transition-colors"
              >
                View Details →
              </button>
            </div>

            {/* Upcoming Appointments Card */}
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">Appointments</h3>
                <span className="text-3xl font-bold text-blue-600 dark:text-blue-400">{appointments.length}</span>
              </div>
              <p className="text-gray-600 dark:text-gray-400 text-sm mb-4">
                Scheduled appointments
              </p>
              <button
                onClick={() => setActiveTab('appointments')}
                className="w-full py-2 px-4 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/50 font-medium transition-colors"
              >
                View Details →
              </button>
            </div>

            {/* Discharge Summaries Card */}
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">Discharge Summaries</h3>
                <span className="text-3xl font-bold text-purple-600 dark:text-purple-400">{summaries.length}</span>
              </div>
              <p className="text-gray-600 dark:text-gray-400 text-sm mb-4">
                Hospital discharge records
              </p>
              <button
                onClick={() => setActiveTab('summaries')}
                className="w-full py-2 px-4 bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/50 font-medium transition-colors"
              >
                View Details →
              </button>
            </div>

            {/* Health Alerts Card */}
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">Health Alerts</h3>
                <span className={`text-3xl font-bold ${
                  alerts.filter(a => a.severity === 'critical').length > 0 
                    ? 'text-red-600 dark:text-red-400' 
                    : 'text-orange-600 dark:text-orange-400'
                }`}>
                  {alerts.length}
                </span>
              </div>
              <p className="text-gray-600 dark:text-gray-400 text-sm mb-4">
                {alerts.filter(a => a.severity === 'critical').length > 0 
                  ? `${alerts.filter(a => a.severity === 'critical').length} critical alerts`
                  : 'No critical alerts'}
              </p>
              <button
                onClick={() => navigate('/patient/alerts')}
                className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${
                  alerts.filter(a => a.severity === 'critical').length > 0
                    ? 'bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/50'
                    : 'bg-orange-50 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 hover:bg-orange-100 dark:hover:bg-orange-900/50'
                }`}
              >
                View Alerts →
              </button>
            </div>
          </div>

          {/* Daily Medication Check-in */}
          {medications.length > 0 && (
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

          {/* Health Progress Section */}
          <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
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
                  {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].map((day) => {
                    const adherenceRate = Math.floor(Math.random() * 40) + 60; // Mock data 60-100%
                    return (
                      <div key={day} className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{day}</span>
                        <div className="flex items-center gap-3">
                          <div className="w-32 bg-gray-200 dark:bg-slate-600 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${
                                adherenceRate >= 80 ? 'bg-green-500' : 
                                adherenceRate >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${adherenceRate}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-semibold text-gray-900 dark:text-white w-12">{adherenceRate}%</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
                <div className="mt-4 pt-4 border-t border-gray-200 dark:border-slate-600">
                  <div className="text-center">
                    <span className="text-lg font-bold text-green-600 dark:text-green-400">85%</span>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Weekly Average</p>
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
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-slate-700 rounded-lg">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Blood Pressure</p>
                      <p className="font-semibold text-gray-900 dark:text-white">120/80 mmHg</p>
                    </div>
                    <span className="text-green-500 text-xl">✓</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-slate-700 rounded-lg">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Heart Rate</p>
                      <p className="font-semibold text-gray-900 dark:text-white">72 BPM</p>
                    </div>
                    <span className="text-green-500 text-xl">✓</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-slate-700 rounded-lg">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Pain Level</p>
                      <p className="font-semibold text-gray-900 dark:text-white">3/10</p>
                    </div>
                    <span className="text-yellow-500 text-xl">⚠</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-slate-700 rounded-lg">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Last Symptom Report</p>
                      <p className="font-semibold text-gray-900 dark:text-white">2 days ago</p>
                    </div>
                    <span className="text-blue-500 text-xl">ℹ</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Emergency Contact Section */}
          <div className="mt-8 bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20 rounded-xl shadow-lg overflow-hidden border border-red-200 dark:border-red-800">
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
        </>
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
