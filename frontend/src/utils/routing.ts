/**
 * Utility to get the correct dashboard route based on user role
 */

export const getDashboardRoute = (userRole?: string): string => {
  if (!userRole) {
    // Try to get from localStorage as fallback
    const storedRole = localStorage.getItem('user_role');
    if (storedRole) {
      userRole = storedRole;
    }
  }

  switch (userRole?.toLowerCase()) {
    case 'nurse':
    case 'staff':
      return '/dashboard';
    case 'caregiver':
      return '/caregiver/dashboard';
    case 'patient':
      return '/patient/dashboard';
    default:
      return '/';
  }
};
