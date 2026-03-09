import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { ThemeProvider } from './contexts/ThemeContext';
import HomePage from './pages/HomePage';
import LoginSelectionPage from './pages/LoginSelectionPage';
import LoginPage from './pages/LoginPage';
import PatientRegistrationPage from './pages/PatientRegistrationPage';
import PatientLoginPage from './pages/PatientLoginPage';
import PatientDashboardPage from './pages/PatientDashboardPage';
import PatientAppointmentRequestPage from './pages/PatientAppointmentRequestPage';
import PatientAppointmentsPage from './pages/PatientAppointmentsPage';
import PatientMedicationsPage from './pages/PatientMedicationsPage';
import PatientAlertsPage from './pages/PatientAlertsPage';
import CaregiverBrowsePage from './pages/CaregiverBrowsePage';
import PatientCaregiversPage from './pages/PatientCaregiversPage';
import NurseDashboard from './pages/NurseDashboard';
import AlertsPage from './pages/AlertsPage';
import PatientQueuePage from './pages/PatientQueuePage';
import AnalyticsDashboard from './pages/AnalyticsDashboard';
import MedicationsPage from './pages/MedicationsPage';
import PatientProfilePage from './pages/PatientProfilePage';
import PatientSettingsPage from './pages/PatientSettingsPage';
import PatientMedicalInfoPage from './pages/PatientMedicalInfoPage';
import MedicationAdherencePage from './pages/MedicationAdherencePage';
import AppointmentsPage from './pages/AppointmentsPage';
import DischargeSummariesPage from './pages/DischargeSummariesPage';
import SettingsPage from './pages/SettingsPage';
import NursePatientSearchPage from './pages/NursePatientSearchPage';
import HealthProgressChartPage from './pages/HealthProgressChartPage';
import DailyGoalsPage from './pages/DailyGoalsPage';
import ChatPage from './pages/ChatPage';
import CaregiverLoginPage from './pages/CaregiverLoginPage';
import CaregiverDashboard from './pages/CaregiverDashboard';
import CaregiverBookingsPage from './pages/CaregiverBookingsPage';
import CaregiverProfilePage from './pages/CaregiverProfilePage';
import ProtectedPatientRoute from './components/ProtectedPatientRoute';
import ProtectedCaregiverRoute from './components/ProtectedCaregiverRoute';
import RoleBasedRoute from './components/RoleBasedRoute';
import DashboardLayout from './components/layout/DashboardLayout';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
                fontSize: '14px',
                padding: '12px 20px',
              },
              success: {
                duration: 3000,
                iconTheme: {
                  primary: '#10b981',
                  secondary: '#fff',
                },
              },
              error: {
                duration: 8000,
                style: {
                  background: '#ef4444',
                  color: '#fff',
                  fontSize: '14px',
                  fontWeight: '500',
                  padding: '16px 24px',
                },
                iconTheme: {
                  primary: '#fff',
                  secondary: '#ef4444',
                },
              },
            }}
          />
          <Routes>
            {/* HOME - Routes users based on auth status and role */}
            <Route path="/" element={<HomePage />} />

            {/* LOGIN SELECTION - Clear entry point for new users */}
            <Route path="/login-selection" element={<LoginSelectionPage />} />

            {/* PUBLIC AUTH ROUTES */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/patient/login" element={<PatientLoginPage />} />
            <Route path="/patient/register" element={<PatientRegistrationPage />} />
            <Route path="/caregiver/login" element={<CaregiverLoginPage />} />

            {/* PROTECTED PATIENT ROUTES - Authenticated patients with PatientLayout */}
            <Route element={<ProtectedPatientRoute />}>
              <Route path="/patient/dashboard" element={<PatientDashboardPage />} />
              <Route path="/patient/health" element={<HealthProgressChartPage />} />
              <Route path="/patient/goals" element={<DailyGoalsPage />} />
              <Route path="/patient/appointments" element={<PatientAppointmentsPage />} />
              <Route path="/patient/appointments/request" element={<PatientAppointmentRequestPage />} />
              <Route path="/patient/medications" element={<PatientMedicationsPage />} />
              <Route path="/patient/alerts" element={<PatientAlertsPage />} />
              <Route path="/patient/caregivers" element={<CaregiverBrowsePage />} />
              <Route path="/patient/caregivers/:id/book" element={<PatientCaregiversPage />} />
              <Route path="/patient/messages" element={<ChatPage />} />
              <Route path="/patient/profile" element={<PatientProfilePage />} />
              <Route path="/patient/settings" element={<PatientSettingsPage />} />
              <Route path="/patient/medical-info" element={<PatientMedicalInfoPage />} />
            </Route>

            {/* PROTECTED CAREGIVER ROUTES - Authenticated caregivers */}
            <Route element={<ProtectedCaregiverRoute />}>
              <Route path="/caregiver/dashboard" element={<CaregiverDashboard />} />
              <Route path="/caregiver/bookings" element={<CaregiverBookingsPage />} />
              <Route path="/caregiver/profile" element={<CaregiverProfilePage />} />
              <Route path="/caregiver/messages" element={<ChatPage />} />
            </Route>

            {/* PROTECTED NURSE/STAFF ROUTES - Authenticated staff with DashboardLayout and role checking */} 
            {/* PROTECTED NURSE/STAFF ROUTES - Authenticated staff with DashboardLayout and role checking */}
            <Route element={<RoleBasedRoute allowedRoles={['nurse', 'staff']} fallbackPath="/patient/login" />}>
              <Route element={<DashboardLayout />}>
                <Route path="/dashboard" element={<NurseDashboard />} />
                <Route path="/alerts" element={<AlertsPage />} />
                <Route path="/patients" element={<PatientQueuePage />} />
                <Route path="/patients/search" element={<NursePatientSearchPage />} />
                <Route path="/health" element={<HealthProgressChartPage />} />
                <Route path="/health/:patientId" element={<HealthProgressChartPage />} />
                <Route path="/medications" element={<MedicationsPage />} />
                <Route path="/adherence" element={<MedicationAdherencePage />} />
                <Route path="/appointments" element={<AppointmentsPage />} />
                <Route path="/discharge-summaries" element={<DischargeSummariesPage />} />
                <Route path="/messages" element={<ChatPage />} />
                <Route path="/analytics" element={<AnalyticsDashboard />} />
                <Route path="/settings" element={<SettingsPage />} />
              </Route>
            </Route>

            {/* FALLBACK - Redirect unknown routes to home */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;
