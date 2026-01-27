import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import client from '../api/client';

interface RegistrationFormData {
  username: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  national_id: string;
  phone_number: string;
  email: string;
}

const PatientRegistrationPage: React.FC = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<RegistrationFormData>({
    username: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
    date_of_birth: '',
    gender: '',
    national_id: '',
    phone_number: '+250',
    email: '',
  });
  const [errors, setErrors] = useState<Partial<Record<keyof RegistrationFormData, string>>>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error for this field when user types
    if (errors[name as keyof RegistrationFormData]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof RegistrationFormData, string>> = {};

    if (!formData.username.trim()) newErrors.username = 'Username is required';
    if (!formData.password) newErrors.password = 'Password is required';
    else if (formData.password.length < 8) newErrors.password = 'Password must be at least 8 characters';
    if (!formData.password_confirm) newErrors.password_confirm = 'Please confirm your password';
    else if (formData.password !== formData.password_confirm) {
      newErrors.password_confirm = 'Passwords do not match';
    }
    if (!formData.first_name.trim()) newErrors.first_name = 'First name is required';
    if (!formData.last_name.trim()) newErrors.last_name = 'Last name is required';
    if (!formData.date_of_birth) newErrors.date_of_birth = 'Date of birth is required';
    if (!formData.gender) newErrors.gender = 'Gender is required';
    if (!formData.national_id.trim()) newErrors.national_id = 'National ID is required';
    else if (!/^\d{16}$/.test(formData.national_id)) {
      newErrors.national_id = 'National ID must be exactly 16 digits';
    }
    if (!formData.phone_number.trim()) newErrors.phone_number = 'Phone number is required';
    else if (!/^\+250\d{9}$/.test(formData.phone_number)) {
      newErrors.phone_number = 'Phone number must be in format +250XXXXXXXXX';
    }
    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      toast.error('Please fix the form errors');
      return;
    }

    setIsLoading(true);

    try {
      const response = await client.post('/v1/patients/register/', formData);
      
      // Store tokens in localStorage
      const { tokens, patient } = response.data;
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      localStorage.setItem('patient_data', JSON.stringify(patient));

      toast.success('Registration successful! Welcome to BiCare360');
      
      // Redirect to patient portal dashboard
      setTimeout(() => {
        navigate('/patient/dashboard');
      }, 500);
    } catch (err: any) {
      console.error('Registration failed:', err);
      
      if (err.response?.data) {
        const serverErrors = err.response.data;
        
        // Map server errors to form fields
        const mappedErrors: Partial<Record<keyof RegistrationFormData, string>> = {};
        Object.keys(serverErrors).forEach(key => {
          const errorMessages = serverErrors[key];
          const message = Array.isArray(errorMessages) ? errorMessages[0] : errorMessages;
          mappedErrors[key as keyof RegistrationFormData] = message;
        });
        
        setErrors(mappedErrors);
        
        toast.error('Registration failed. Please check the form for errors.', {
          duration: 5000,
        });
      } else {
        toast.error('Registration failed. Please try again.', {
          duration: 5000,
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-500 via-teal-500 to-primary-700 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <img src="/logo.png" alt="BiCare360 Logo" className="h-16 w-16 object-contain" />
          </div>
          <h1 className="text-3xl font-bold text-primary-600 dark:text-primary-400">BiCare360</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">Patient Portal Registration</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6" noValidate>
          {/* Account Information */}
          <div className="border-b border-gray-200 dark:border-gray-700 pb-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Account Information</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Username *
                </label>
                <input
                  id="username"
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 dark:border-gray-600 ${
                    errors.username ? 'border-red-300 dark:border-red-400' : 'border-gray-300'
                  }`}
                  disabled={isLoading}
                />
                {errors.username && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.username}</p>
                )}
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Email (Optional)
                </label>
                <input
                  id="email"
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 dark:border-gray-600 ${
                    errors.email ? 'border-red-300 dark:border-red-400' : 'border-gray-300'
                  }`}
                  disabled={isLoading}
                />
                {errors.email && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.email}</p>
                )}
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Password *
                </label>
                <input
                  id="password"
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 dark:border-gray-600 ${
                    errors.password ? 'border-red-300 dark:border-red-400' : 'border-gray-300'
                  }`}
                  disabled={isLoading}
                />
                {errors.password && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.password}</p>
                )}
              </div>

              <div>
                <label htmlFor="password_confirm" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Confirm Password *
                </label>
                <input
                  id="password_confirm"
                  type="password"
                  name="password_confirm"
                  value={formData.password_confirm}
                  onChange={handleChange}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 dark:border-gray-600 ${
                    errors.password_confirm ? 'border-red-300 dark:border-red-400' : 'border-gray-300'
                  }`}
                  disabled={isLoading}
                />
                {errors.password_confirm && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.password_confirm}</p>
                )}
              </div>
            </div>
          </div>

          {/* Personal Information */}
          <div className="border-b border-gray-200 dark:border-gray-700 pb-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Personal Information</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  First Name *
                </label>
                <input
                  id="first_name"
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 dark:border-gray-600 ${
                    errors.first_name ? 'border-red-300 dark:border-red-400' : 'border-gray-300'
                  }`}
                  disabled={isLoading}
                />
                {errors.first_name && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.first_name}</p>
                )}
              </div>

              <div>
                <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Last Name *
                </label>
                <input
                  id="last_name"
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 dark:border-gray-600 ${
                    errors.last_name ? 'border-red-300 dark:border-red-400' : 'border-gray-300'
                  }`}
                  disabled={isLoading}
                />
                {errors.last_name && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.last_name}</p>
                )}
              </div>

              <div>
                <label htmlFor="date_of_birth" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Date of Birth *
                </label>
                <input
                  id="date_of_birth"
                  type="date"
                  name="date_of_birth"
                  value={formData.date_of_birth}
                  onChange={handleChange}
                  max={new Date().toISOString().split('T')[0]}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 dark:border-gray-600 ${
                    errors.date_of_birth ? 'border-red-300 dark:border-red-400' : 'border-gray-300'
                  }`}
                  disabled={isLoading}
                />
                {errors.date_of_birth && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.date_of_birth}</p>
                )}
              </div>

              <div>
                <label htmlFor="gender" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Gender *
                </label>
                <select
                  id="gender"
                  name="gender"
                  value={formData.gender}
                  onChange={handleChange}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 dark:border-gray-600 ${
                    errors.gender ? 'border-red-300 dark:border-red-400' : 'border-gray-300'
                  }`}
                  disabled={isLoading}
                >
                  <option value="">Select Gender</option>
                  <option value="M">Male</option>
                  <option value="F">Female</option>
                </select>
                {errors.gender && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.gender}</p>
                )}
              </div>

              <div>
                <label htmlFor="national_id" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  National ID *
                </label>
                <input
                  id="national_id"
                  type="text"
                  name="national_id"
                  value={formData.national_id}
                  onChange={handleChange}
                  maxLength={16}
                  placeholder="1234567890123456"
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 dark:border-gray-600 ${
                    errors.national_id ? 'border-red-300 dark:border-red-400' : 'border-gray-300'
                  }`}
                  disabled={isLoading}
                />
                {errors.national_id && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.national_id}</p>
                )}
              </div>

              <div>
                <label htmlFor="phone_number" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Phone Number *
                </label>
                <input
                  id="phone_number"
                  type="tel"
                  name="phone_number"
                  value={formData.phone_number}
                  onChange={handleChange}
                  placeholder="+250788123456"
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-colors bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 dark:border-gray-600 ${
                    errors.phone_number ? 'border-red-300 dark:border-red-400' : 'border-gray-300'
                  }`}
                  disabled={isLoading}
                />
                {errors.phone_number && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.phone_number}</p>
                )}
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex flex-col space-y-4">
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-teal-500 hover:bg-teal-600 disabled:bg-gray-400 dark:disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg transition-all duration-200 shadow-md hover:shadow-lg flex items-center justify-center"
            >
              {isLoading ? (
                <>
                  <svg
                    className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
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
                  Creating Account...
                </>
              ) : (
                'Create Account'
              )}
            </button>

            <div className="text-center text-sm text-gray-600 dark:text-gray-400">
              Already have an account?{' '}
              <Link to="/patient/login" className="text-teal-600 dark:text-teal-400 hover:text-teal-700 dark:hover:text-teal-300 font-medium">
                Sign in here
              </Link>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PatientRegistrationPage;
