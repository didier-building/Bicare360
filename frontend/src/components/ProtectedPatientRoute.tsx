import React, { useEffect, useState } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import PatientLayout from './layout/PatientLayout';
import LoadingSpinner from './ui/LoadingSpinner';

/**
 * ProtectedPatientRoute - Wraps patient routes with authentication check
 * Renders PatientLayout for authenticated patients
 */
const ProtectedPatientRoute: React.FC = () => {
  const { isAuthenticated, checkAuth } = useAuthStore();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const verifyAuth = async () => {
      await checkAuth();
      setIsChecking(false);
    };
    verifyAuth();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/patient/login" replace />;
  }

  return (
    <PatientLayout>
      <Outlet />
    </PatientLayout>
  );
};

export default ProtectedPatientRoute;
