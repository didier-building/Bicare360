import { useEffect, useState } from 'react';
import { Navigate, Outlet } from 'react-router-dom';

/**
 * Protected route component for caregiver portal.
 * Checks if user is authenticated and has caregiver role.
 */
export default function ProtectedCaregiverRoute() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('access_token');
      const userStr = localStorage.getItem('user');
      
      if (!token || !userStr) {
        setIsAuthenticated(false);
        return;
      }

      try {
        const user = JSON.parse(userStr);
        // Check if user has caregiver role
        if (user.role === 'caregiver') {
          setIsAuthenticated(true);
        } else {
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error('Error parsing user data:', error);
        setIsAuthenticated(false);
      }
    };

    checkAuth();
  }, []);

  // Loading state
  if (isAuthenticated === null) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/caregiver/login" replace />;
  }

  // Render protected content
  return <Outlet />;
}
