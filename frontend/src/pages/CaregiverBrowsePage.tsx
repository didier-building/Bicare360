import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

interface Caregiver {
  id: number;
  name: string;
  profession: string;
  specializations: string[];
  experience_years: number;
  rating: number;
  total_reviews: number;
  hourly_rate: number;
  location: string;
  availability_status: string;
  bio: string;
  profile_image: string | null;
  languages: string[];
  certifications: string[];
  services: string[];
}

interface FilterOptions {
  service_type: string;
  location: string;
  min_rating: string;
  max_hourly_rate: string;
  availability: string;
  experience_level: string;
}

export default function CaregiverBrowsePage() {
  const navigate = useNavigate();
  const [caregivers, setCaregivers] = useState<Caregiver[]>([]);
  const [filteredCaregivers, setFilteredCaregivers] = useState<Caregiver[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<FilterOptions>({
    service_type: '',
    location: '',
    min_rating: '',
    max_hourly_rate: '',
    availability: '',
    experience_level: '',
  });
  const [showFilters, setShowFilters] = useState(false);

  // Service types for filtering
  const serviceTypes = [
    'Home Care', 'Medical Care', 'Companion Care', 'Personal Care',
    'Hospice Care', 'Respite Care', 'Alzheimer\'s Care', 'Disability Support',
    'Child Care', 'Elderly Care', 'Post-Surgery Care', 'Chronic Disease Management'
  ];

  const experienceLevels = [
    { value: '0-2', label: '0-2 years' },
    { value: '3-5', label: '3-5 years' },
    { value: '6-10', label: '6-10 years' },
    { value: '10+', label: '10+ years' }
  ];

  useEffect(() => {
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      navigate('/patient/login');
      return;
    }

    fetchCaregivers();
  }, [navigate]);

  useEffect(() => {
    applyFilters();
  }, [caregivers, searchQuery, filters]);

  const fetchCaregivers = async () => {
    try {
      setIsLoading(true);
      setError('');

      // For demo purposes, create mock caregiver data
      // In production, this would be: const response = await client.get('/v1/caregivers/');
      const mockCaregivers: Caregiver[] = [
        {
          id: 1,
          name: "Sarah Johnson",
          profession: "Registered Nurse",
          specializations: ["Chronic Disease Management", "Medication Administration"],
          experience_years: 8,
          rating: 4.9,
          total_reviews: 127,
          hourly_rate: 45,
          location: "Kigali, Rwanda",
          availability_status: "available",
          bio: "Experienced RN specializing in chronic disease management and medication supervision. Fluent in Kinyarwanda, French, and English.",
          profile_image: null,
          languages: ["English", "French", "Kinyarwanda"],
          certifications: ["RN License", "CPR Certified", "Diabetes Management"],
          services: ["Medical Care", "Medication Management", "Health Monitoring"]
        },
        {
          id: 2,
          name: "Jean Claude Uwimana",
          profession: "Certified Nursing Assistant",
          specializations: ["Elder Care", "Personal Care"],
          experience_years: 5,
          rating: 4.7,
          total_reviews: 89,
          hourly_rate: 25,
          location: "Kigali, Rwanda",
          availability_status: "available",
          bio: "Compassionate CNA with extensive experience in elderly care. Specializes in personal care and daily living assistance.",
          profile_image: null,
          languages: ["Kinyarwanda", "French", "English"],
          certifications: ["CNA License", "First Aid", "Mobility Assistance"],
          services: ["Personal Care", "Elderly Care", "Companion Care"]
        },
        {
          id: 3,
          name: "Marie Uwimana",
          profession: "Home Health Aide",
          specializations: ["Post-Surgery Care", "Physical Therapy Support"],
          experience_years: 6,
          rating: 4.8,
          total_reviews: 156,
          hourly_rate: 35,
          location: "Kigali, Rwanda",
          availability_status: "busy",
          bio: "Dedicated home health aide with experience in post-operative care and rehabilitation support.",
          profile_image: null,
          languages: ["Kinyarwanda", "French"],
          certifications: ["HHA License", "Physical Therapy Assistant", "Wound Care"],
          services: ["Post-Surgery Care", "Home Care", "Medical Care"]
        },
        {
          id: 4,
          name: "David Mukamana",
          profession: "Licensed Practical Nurse",
          specializations: ["Wound Care", "IV Therapy"],
          experience_years: 12,
          rating: 4.9,
          total_reviews: 203,
          hourly_rate: 55,
          location: "Kigali, Rwanda",
          availability_status: "available",
          bio: "Highly experienced LPN with expertise in advanced wound care and IV therapy. Available for complex medical cases.",
          profile_image: null,
          languages: ["English", "French", "Kinyarwanda"],
          certifications: ["LPN License", "IV Therapy", "Wound Care Specialist", "Pain Management"],
          services: ["Medical Care", "Wound Care", "IV Therapy", "Chronic Disease Management"]
        }
      ];

      setCaregivers(mockCaregivers);
    } catch (err) {
      console.error('Failed to fetch caregivers:', err);
      setError('Failed to load caregivers');
      toast.error('Failed to load caregivers');
    } finally {
      setIsLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...caregivers];

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(caregiver =>
        caregiver.name.toLowerCase().includes(query) ||
        caregiver.profession.toLowerCase().includes(query) ||
        caregiver.specializations.some(spec => spec.toLowerCase().includes(query)) ||
        caregiver.services.some(service => service.toLowerCase().includes(query))
      );
    }

    // Service type filter
    if (filters.service_type) {
      filtered = filtered.filter(caregiver =>
        caregiver.services.includes(filters.service_type)
      );
    }

    // Location filter
    if (filters.location) {
      filtered = filtered.filter(caregiver =>
        caregiver.location.toLowerCase().includes(filters.location.toLowerCase())
      );
    }

    // Rating filter
    if (filters.min_rating) {
      filtered = filtered.filter(caregiver =>
        caregiver.rating >= parseFloat(filters.min_rating)
      );
    }

    // Hourly rate filter
    if (filters.max_hourly_rate) {
      filtered = filtered.filter(caregiver =>
        caregiver.hourly_rate <= parseFloat(filters.max_hourly_rate)
      );
    }

    // Availability filter
    if (filters.availability) {
      filtered = filtered.filter(caregiver =>
        caregiver.availability_status === filters.availability
      );
    }

    // Experience level filter
    if (filters.experience_level) {
      const [min, max] = filters.experience_level.includes('+') 
        ? [10, Infinity] 
        : filters.experience_level.split('-').map(Number);
      
      filtered = filtered.filter(caregiver =>
        caregiver.experience_years >= min && caregiver.experience_years <= (max || min + 2)
      );
    }

    setFilteredCaregivers(filtered);
  };

  const handleFilterChange = (key: keyof FilterOptions, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      service_type: '',
      location: '',
      min_rating: '',
      max_hourly_rate: '',
      availability: '',
      experience_level: '',
    });
    setSearchQuery('');
  };

  const handleBookCaregiver = (caregiver: Caregiver) => {
    // Navigate to caregiver detail page or booking page
    navigate(`/patient/caregivers/${caregiver.id}/book`, { 
      state: { caregiver } 
    });
  };

  const renderStars = (rating: number, totalReviews: number) => {
    return (
      <div className="flex items-center">
        {[1, 2, 3, 4, 5].map(star => (
          <svg
            key={star}
            className={`h-4 w-4 ${
              star <= rating ? 'text-yellow-400' : 'text-gray-300'
            }`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        ))}
        <span className="ml-1 text-sm text-gray-600 dark:text-gray-400">
          ({totalReviews})
        </span>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-teal-50 to-cyan-50 dark:from-slate-950 dark:to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600 dark:border-teal-400 mb-4"></div>
          <p className="text-teal-700 dark:text-teal-200 font-medium">Finding caregivers...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 to-cyan-50 dark:from-slate-950 dark:to-slate-900">
      {/* Header */}
      <header className="bg-white dark:bg-slate-800 shadow-sm border-b border-gray-200 dark:border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => {
                  const role = localStorage.getItem('user_role');
                  const dashboardRoute = role?.toLowerCase() === 'patient' ? '/patient/dashboard' : '/dashboard';
                  navigate(dashboardRoute);
                }}
                className="flex items-center text-teal-600 dark:text-teal-400 hover:text-teal-700 dark:hover:text-teal-300 font-medium"
              >
                <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Back to Dashboard
              </button>
              <div className="h-6 w-px bg-gray-300 dark:bg-slate-600"></div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Find Caregivers</h1>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-700 dark:text-red-200">{error}</p>
          </div>
        )}

        {/* Search and Filter Bar */}
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 mb-8">
          <div className="flex flex-col sm:flex-row gap-4 mb-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search by name, profession, or service..."
                className="w-full px-4 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 dark:bg-slate-700 dark:text-white"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="px-4 py-2 bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-slate-600 transition-colors flex items-center"
            >
              <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.207A1 1 0 013 6.5V4z" />
              </svg>
              Filters
            </button>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <div className="border-t border-gray-200 dark:border-slate-600 pt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Service Type
                </label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 dark:bg-slate-700 dark:text-white"
                  value={filters.service_type}
                  onChange={(e) => handleFilterChange('service_type', e.target.value)}
                >
                  <option value="">All Services</option>
                  {serviceTypes.map(service => (
                    <option key={service} value={service}>{service}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Location
                </label>
                <input
                  type="text"
                  placeholder="Enter location"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 dark:bg-slate-700 dark:text-white"
                  value={filters.location}
                  onChange={(e) => handleFilterChange('location', e.target.value)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Min Rating
                </label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 dark:bg-slate-700 dark:text-white"
                  value={filters.min_rating}
                  onChange={(e) => handleFilterChange('min_rating', e.target.value)}
                >
                  <option value="">Any Rating</option>
                  <option value="4.5">4.5+ Stars</option>
                  <option value="4.0">4.0+ Stars</option>
                  <option value="3.5">3.5+ Stars</option>
                  <option value="3.0">3.0+ Stars</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Max Hourly Rate (RWF)
                </label>
                <input
                  type="number"
                  placeholder="Max rate"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 dark:bg-slate-700 dark:text-white"
                  value={filters.max_hourly_rate}
                  onChange={(e) => handleFilterChange('max_hourly_rate', e.target.value)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Availability
                </label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 dark:bg-slate-700 dark:text-white"
                  value={filters.availability}
                  onChange={(e) => handleFilterChange('availability', e.target.value)}
                >
                  <option value="">Any Availability</option>
                  <option value="available">Available Now</option>
                  <option value="busy">Busy</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Experience Level
                </label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 dark:bg-slate-700 dark:text-white"
                  value={filters.experience_level}
                  onChange={(e) => handleFilterChange('experience_level', e.target.value)}
                >
                  <option value="">Any Experience</option>
                  {experienceLevels.map(level => (
                    <option key={level.value} value={level.value}>{level.label}</option>
                  ))}
                </select>
              </div>

              <div className="sm:col-span-2 lg:col-span-3 flex justify-end">
                <button
                  onClick={clearFilters}
                  className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
                >
                  Clear All Filters
                </button>
              </div>
            </div>
          )}

          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Showing {filteredCaregivers.length} of {caregivers.length} caregivers
            </p>
          </div>
        </div>

        {/* Caregivers Grid */}
        {filteredCaregivers.length === 0 ? (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No caregivers found</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Try adjusting your search criteria or filters.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCaregivers.map(caregiver => (
              <div
                key={caregiver.id}
                className="bg-white dark:bg-slate-800 rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
              >
                <div className="p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">
                        {caregiver.name}
                      </h3>
                      <p className="text-teal-600 dark:text-teal-400 font-medium">
                        {caregiver.profession}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400 flex items-center mt-1">
                        <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        {caregiver.location}
                      </p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      caregiver.availability_status === 'available'
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                        : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
                    }`}>
                      {caregiver.availability_status === 'available' ? 'Available' : 'Busy'}
                    </span>
                  </div>

                  {/* Rating and Experience */}
                  <div className="flex items-center justify-between mb-4">
                    {renderStars(caregiver.rating, caregiver.total_reviews)}
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {caregiver.experience_years} years exp.
                    </span>
                  </div>

                  {/* Bio */}
                  <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-3">
                    {caregiver.bio}
                  </p>

                  {/* Services */}
                  <div className="mb-4">
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Services:</p>
                    <div className="flex flex-wrap gap-1">
                      {caregiver.services.slice(0, 3).map(service => (
                        <span
                          key={service}
                          className="px-2 py-1 bg-teal-50 dark:bg-teal-900/30 text-teal-700 dark:text-teal-300 text-xs rounded-full"
                        >
                          {service}
                        </span>
                      ))}
                      {caregiver.services.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 dark:bg-slate-700 text-gray-600 dark:text-gray-400 text-xs rounded-full">
                          +{caregiver.services.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Languages */}
                  <div className="mb-4">
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Languages:</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {caregiver.languages.join(', ')}
                    </p>
                  </div>

                  {/* Footer */}
                  <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-slate-600">
                    <div>
                      <span className="text-2xl font-bold text-gray-900 dark:text-white">
                        RWF {caregiver.hourly_rate}
                      </span>
                      <span className="text-sm text-gray-600 dark:text-gray-400">/hour</span>
                    </div>
                    <button
                      onClick={() => handleBookCaregiver(caregiver)}
                      disabled={caregiver.availability_status === 'busy'}
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                        caregiver.availability_status === 'available'
                          ? 'bg-teal-600 hover:bg-teal-700 text-white'
                          : 'bg-gray-300 dark:bg-slate-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
                      }`}
                    >
                      {caregiver.availability_status === 'available' ? 'Book Now' : 'Unavailable'}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}