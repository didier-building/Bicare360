import React, { useState } from 'react';
import { useAuthStore } from '../stores/authStore';
import { useNavigate, Link } from 'react-router-dom';
import toast from 'react-hot-toast';

const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [validationErrors, setValidationErrors] = useState<{ username?: string; password?: string }>({});
  const { login, isLoading, clearError } = useAuthStore();
  const navigate = useNavigate();

  const validateForm = (): boolean => {
    const errors: { username?: string; password?: string } = {};

    if (!username.trim()) {
      errors.username = 'Username is required';
    }

    if (!password) {
      errors.password = 'Password is required';
    } else if (password.length < 6) {
      errors.password = 'Password must be at least 6 characters';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    e.stopPropagation();
    clearError();
    setValidationErrors({});

    if (!validateForm()) {
      toast.error('Please fix the form errors', { duration: 6000 });
      return;
    }

    try {
      await login(username, password);
      toast.success('Welcome back!');
      // Small delay to ensure toast is visible before navigation
      setTimeout(() => {
        navigate('/dashboard');
      }, 300);
    } catch (err: any) {
      console.error('Login failed - showing toast:', err);
      let errorMessage = 'Invalid username or password';
      
      if (err.response?.data) {
        if (err.response.data.detail) {
          errorMessage = err.response.data.detail;
        } else if (err.response.data.non_field_errors) {
          errorMessage = err.response.data.non_field_errors[0];
        } else if (err.response.data.message) {
          errorMessage = err.response.data.message;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }

      if (err.response?.status === 401) {
        // Check if this is a role mismatch error
        const responseData = err.response?.data || {};
        if (responseData.user_role && responseData.user_role !== 'staff') {
          const roleDisplayMap: { [key: string]: string } = {
            'patient': 'patient',
            'caregiver': 'caregiver'
          };
          const detectedRole = roleDisplayMap[responseData.user_role] || responseData.user_role;
          const portalMap: { [key: string]: string } = {
            'patient': '/patient/login',
            'caregiver': '/caregiver/login'
          };
          
          errorMessage = `This account belongs to a ${detectedRole}. Please use the ${detectedRole} login page instead.`;
          
          // Show role-mismatch-specific toast with link suggestion
          toast.error((t) => (
            <div className="flex flex-col gap-2">
              <p>{errorMessage}</p>
              <Link 
                to={portalMap[responseData.user_role] || '/'}
                className="text-blue-200 underline font-semibold text-sm hover:text-blue-100"
              >
                Go to {detectedRole} portal →
              </Link>
            </div>
          ), {
            duration: 20000,
            style: {
              background: '#dc2626',
              color: '#fff',
              fontSize: '15px',
              fontWeight: '600',
              padding: '20px 28px',
              minWidth: '350px',
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.3)',
            },
            icon: '❌',
          });
        } else {
          errorMessage = 'Invalid credentials. Please check your username and password and try again.';
          toast.error(errorMessage, {
            duration: 15000,
            style: {
              background: '#dc2626',
              color: '#fff',
              fontSize: '15px',
              fontWeight: '600',
              padding: '20px 28px',
              minWidth: '350px',
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.3)',
            },
            icon: '❌',
          });
        }
      }
      
      console.log('Showing error toast with message:', errorMessage);
      
      // Clear password field on error
      setPassword('');
      
      // Do NOT navigate or reload - stay on login page
      return false;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-500 via-teal-500 to-primary-700 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md p-8">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <img src="/logo.png" alt="BiCare360 Logo" className="h-20 w-20 object-contain" />
          </div>
          <h1 className="text-3xl font-bold text-primary-600 dark:text-primary-400">BiCare360</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Post-Discharge Home-Care Coordination</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6" noValidate>
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => {
                setUsername(e.target.value);
                if (validationErrors.username) {
                  setValidationErrors({ ...validationErrors, username: undefined });
                }
              }}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 dark:border-gray-600 ${
                validationErrors.username ? 'border-red-300 dark:border-red-400 focus:ring-red-500' : 'border-gray-300'
              }`}
              placeholder="Enter your username"
              aria-label="Username"
              aria-invalid={!!validationErrors.username}
              aria-describedby={validationErrors.username ? 'username-error' : undefined}
              autoComplete="username"
              disabled={isLoading}
            />
            {validationErrors.username && (
              <p id="username-error" className="mt-1 text-sm text-red-600 dark:text-red-400" role="alert">
                {validationErrors.username}
              </p>
            )}
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (validationErrors.password) {
                  setValidationErrors({ ...validationErrors, password: undefined });
                }
              }}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 dark:border-gray-600 ${
                validationErrors.password ? 'border-red-300 dark:border-red-400 focus:ring-red-500' : 'border-gray-300'
              }`}
              placeholder="Enter your password"
              aria-label="Password"
              aria-invalid={!!validationErrors.password}
              aria-describedby={validationErrors.password ? 'password-error' : undefined}
              autoComplete="current-password"
              disabled={isLoading}
            />
            {validationErrors.password && (
              <p id="password-error" className="mt-1 text-sm text-red-600 dark:text-red-400" role="alert">
                {validationErrors.password}
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-teal-500 hover:bg-teal-600 disabled:bg-gray-400 dark:disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium py-2.5 px-4 rounded-lg transition-all duration-200 flex items-center justify-center shadow-md hover:shadow-lg"
            aria-busy={isLoading}
          >
            {isLoading ? (
              <>
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Signing in...
              </>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
          <p>
            Use your assigned staff account credentials. If you need access, contact your organization administrator.
          </p>
          <p className="mt-4">
            Not a nurse?{' '}
            <Link to="/patient/register" className="text-teal-600 dark:text-teal-400 hover:text-teal-700 dark:hover:text-teal-300 font-medium">
              Register as a patient
            </Link>
            {' / '}
            <Link to="/patient/login" className="text-teal-600 dark:text-teal-400 hover:text-teal-700 dark:hover:text-teal-300 font-medium">
              Login as patient
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
