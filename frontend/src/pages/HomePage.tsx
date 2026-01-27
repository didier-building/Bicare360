import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import LoadingSpinner from '../components/ui/LoadingSpinner';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user, checkAuth } = useAuthStore();

  useEffect(() => {
    const route = async () => {
      // Check authentication status
      await checkAuth();
      
      // Route based on authentication and role
      if (!isAuthenticated) {
        // Show login selection
        navigate('/login-selection', { replace: true });
      } else {
        // Route based on user role
        if (user?.role === 'nurse' || user?.role === 'staff') {
          navigate('/dashboard', { replace: true });
        } else {
          navigate('/patient/dashboard', { replace: true });
        }
      }
    };

    route();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <LoadingSpinner size="lg" />
        <p className="mt-4 text-gray-600">Loading...</p>
      </div>
    </div>
  );
};

export default HomePage;
