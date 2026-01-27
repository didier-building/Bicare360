import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

interface Caregiver {
  id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  specialization: string;
  experience_years: number;
  hourly_rate: number;
  rating: number;
  total_reviews: number;
  avatar: string | null;
  bio: string;
  services: string[];
  availability: {
    available: boolean;
    next_available: string | null;
  };
  location: {
    city: string;
    distance_km: number | null;
  };
  verified: boolean;
  languages: string[];
}

interface CaregiverFilters {
  service_type: string;
  max_hourly_rate: number | null;
  min_rating: number | null;
  availability: string;
  distance: number | null;
  experience_years: number | null;
}

export default function PatientCaregiversPage() {
  const navigate = useNavigate();
  const [caregivers, setCaregivers] = useState<Caregiver[]>([]);
  const [filteredCaregivers, setFilteredCaregivers] = useState<Caregiver[]>([]);
  const [filters, setFilters] = useState<CaregiverFilters>({
    service_type: '',
    max_hourly_rate: null,
    min_rating: null,
    availability: '',
    distance: null,
    experience_years: null
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('rating'); // rating, price, distance, experience

  const serviceTypes = [
    'Personal Care',
    'Medical Support',
    'Companionship', 
    'Housekeeping',
    'Meal Preparation',
    'Transportation',
    'Physical Therapy',
    'Mental Health Support'
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
  }, [caregivers, filters, searchTerm, sortBy]);

  const fetchCaregivers = async () => {
    try {
      setIsLoading(true);
      setError('');
      
      // For now, we'll create mock data since the backend caregiver endpoints don't exist yet
      const mockCaregivers: Caregiver[] = [
        {
          id: 1,
          first_name: 'Sarah',
          last_name: 'Johnson',
          full_name: 'Sarah Johnson',
          specialization: 'Home Health Aide',
          experience_years: 8,
          hourly_rate: 25,
          rating: 4.9,
          total_reviews: 127,
          avatar: null,
          bio: 'Experienced home health aide with expertise in elderly care, medication management, and mobility assistance.',
          services: ['Personal Care', 'Medical Support', 'Companionship'],
          availability: { available: true, next_available: null },
          location: { city: 'Kigali', distance_km: 2.5 },
          verified: true,
          languages: ['English', 'Kinyarwanda']
        },
        {
          id: 2,
          first_name: 'Michael',
          last_name: 'Uwimana',
          full_name: 'Michael Uwimana',
          specialization: 'Licensed Practical Nurse',
          experience_years: 12,
          hourly_rate: 35,
          rating: 4.8,
          total_reviews: 89,
          avatar: null,
          bio: 'Licensed nurse specializing in post-discharge care, wound care, and medication administration.',
          services: ['Medical Support', 'Physical Therapy', 'Personal Care'],
          availability: { available: false, next_available: '2026-01-27T09:00:00Z' },
          location: { city: 'Kigali', distance_km: 5.2 },
          verified: true,
          languages: ['English', 'Kinyarwanda', 'French']
        },
        {
          id: 3,
          first_name: 'Grace',
          last_name: 'Mukamana',
          full_name: 'Grace Mukamana',
          specialization: 'Certified Nursing Assistant',
          experience_years: 5,
          hourly_rate: 20,
          rating: 4.7,
          total_reviews: 156,
          avatar: null,
          bio: 'Compassionate CNA with experience in dementia care, mobility assistance, and daily living activities.',
          services: ['Personal Care', 'Companionship', 'Housekeeping', 'Meal Preparation'],
          availability: { available: true, next_available: null },
          location: { city: 'Kigali', distance_km: 1.8 },
          verified: true,
          languages: ['English', 'Kinyarwanda']
        },
        {
          id: 4,
          first_name: 'David',
          last_name: 'Nkurunziza',
          full_name: 'David Nkurunziza',
          specialization: 'Physical Therapist',
          experience_years: 10,
          hourly_rate: 40,
          rating: 4.9,
          total_reviews: 73,
          avatar: null,
          bio: 'Licensed physical therapist specializing in post-surgical recovery and mobility rehabilitation.',
          services: ['Physical Therapy', 'Medical Support'],
          availability: { available: true, next_available: null },
          location: { city: 'Kigali', distance_km: 7.1 },
          verified: true,
          languages: ['English', 'Kinyarwanda', 'French', 'Swahili']
        }
      ];

      setCaregivers(mockCaregivers);
      
      // In production, this would be:
      // const response = await client.get('/v1/caregivers/');
      // setCaregivers(response.data.results || response.data);
      
    } catch (err) {
      console.error('Error fetching caregivers:', err);
      setError('Failed to load caregivers');
      toast.error('Failed to load caregivers');
    } finally {
      setIsLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...caregivers];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(caregiver =>
        caregiver.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        caregiver.specialization.toLowerCase().includes(searchTerm.toLowerCase()) ||
        caregiver.services.some(service => 
          service.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    // Service type filter
    if (filters.service_type) {
      filtered = filtered.filter(caregiver =>
        caregiver.services.includes(filters.service_type)
      );
    }

    // Hourly rate filter
    if (filters.max_hourly_rate) {
      filtered = filtered.filter(caregiver => 
        caregiver.hourly_rate <= filters.max_hourly_rate!
      );
    }

    // Rating filter
    if (filters.min_rating) {
      filtered = filtered.filter(caregiver => 
        caregiver.rating >= filters.min_rating!
      );
    }

    // Availability filter
    if (filters.availability === 'available') {
      filtered = filtered.filter(caregiver => caregiver.availability.available);
    }

    // Distance filter
    if (filters.distance) {
      filtered = filtered.filter(caregiver => 
        caregiver.location.distance_km !== null && 
        caregiver.location.distance_km <= filters.distance!
      );
    }

    // Experience filter
    if (filters.experience_years) {
      filtered = filtered.filter(caregiver => 
        caregiver.experience_years >= filters.experience_years!
      );
    }

    // Sorting
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'rating':
          return b.rating - a.rating;
        case 'price':
          return a.hourly_rate - b.hourly_rate;
        case 'distance':
          return (a.location.distance_km || 999) - (b.location.distance_km || 999);
        case 'experience':
          return b.experience_years - a.experience_years;
        default:
          return 0;
      }
    });

    setFilteredCaregivers(filtered);
  };

  const handleFilterChange = (key: keyof CaregiverFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const resetFilters = () => {
    setFilters({
      service_type: '',
      max_hourly_rate: null,
      min_rating: null,
      availability: '',
      distance: null,
      experience_years: null
    });
    setSearchTerm('');
    setSortBy('rating');
  };

  const renderStars = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    for (let i = 0; i < fullStars; i++) {
      stars.push(
        <span key={i} className="text-yellow-400">★</span>
      );
    }

    if (hasHalfStar) {
      stars.push(
        <span key="half" className="text-yellow-400">☆</span>
      );
    }

    const remainingStars = 5 - Math.ceil(rating);
    for (let i = 0; i < remainingStars; i++) {
      stars.push(
        <span key={`empty-${i}`} className="text-gray-300 dark:text-gray-600">☆</span>
      );
    }

    return <div className="flex items-center">{stars}</div>;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-teal-50 to-cyan-50 dark:from-slate-950 dark:to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600 dark:border-teal-400 mb-4"></div>
          <p className="text-teal-700 dark:text-teal-200 font-medium">Loading caregivers...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 to-cyan-50 dark:from-slate-950 dark:to-slate-900">
      {/* Header */}
      <header className="bg-white dark:bg-slate-800 shadow-sm border-b border-gray-200 dark:border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/patient/dashboard')}
                className="flex items-center text-teal-600 dark:text-teal-400 hover:text-teal-700 dark:hover:text-teal-300 font-medium"
              >
                ← Back to Dashboard
              </button>
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Find Caregivers</h1>
                <p className="text-gray-600 dark:text-gray-400">Browse and book professional caregivers</p>
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

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 sticky top-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-bold text-gray-900 dark:text-white">Filters</h2>
                <button
                  onClick={resetFilters}
                  className="text-teal-600 dark:text-teal-400 text-sm hover:underline"
                >
                  Reset All
                </button>
              </div>

              {/* Search */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Search
                </label>
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search by name or service..."
                  className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 dark:bg-slate-700 dark:text-white"
                />
              </div>

              {/* Service Type */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Service Type
                </label>
                <select
                  value={filters.service_type}
                  onChange={(e) => handleFilterChange('service_type', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 dark:bg-slate-700 dark:text-white"
                >
                  <option value="">All Services</option>
                  {serviceTypes.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>

              {/* Max Hourly Rate */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Max Hourly Rate (RWF)
                </label>
                <input
                  type="number"
                  value={filters.max_hourly_rate || ''}
                  onChange={(e) => handleFilterChange('max_hourly_rate', e.target.value ? Number(e.target.value) : null)}
                  placeholder="e.g. 30"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 dark:bg-slate-700 dark:text-white"
                />
              </div>

              {/* Min Rating */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Minimum Rating
                </label>
                <select
                  value={filters.min_rating || ''}
                  onChange={(e) => handleFilterChange('min_rating', e.target.value ? Number(e.target.value) : null)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 dark:bg-slate-700 dark:text-white"
                >
                  <option value="">Any Rating</option>
                  <option value="4.5">4.5+ Stars</option>
                  <option value="4.0">4.0+ Stars</option>
                  <option value="3.5">3.5+ Stars</option>
                  <option value="3.0">3.0+ Stars</option>
                </select>
              </div>

              {/* Availability */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Availability
                </label>
                <select
                  value={filters.availability}
                  onChange={(e) => handleFilterChange('availability', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 dark:bg-slate-700 dark:text-white"
                >
                  <option value="">Any Availability</option>
                  <option value="available">Available Now</option>
                </select>
              </div>

              {/* Distance */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Max Distance (km)
                </label>
                <select
                  value={filters.distance || ''}
                  onChange={(e) => handleFilterChange('distance', e.target.value ? Number(e.target.value) : null)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 dark:bg-slate-700 dark:text-white"
                >
                  <option value="">Any Distance</option>
                  <option value="5">Within 5 km</option>
                  <option value="10">Within 10 km</option>
                  <option value="20">Within 20 km</option>
                </select>
              </div>

              {/* Experience */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Min Experience (years)
                </label>
                <select
                  value={filters.experience_years || ''}
                  onChange={(e) => handleFilterChange('experience_years', e.target.value ? Number(e.target.value) : null)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 dark:bg-slate-700 dark:text-white"
                >
                  <option value="">Any Experience</option>
                  <option value="1">1+ years</option>
                  <option value="3">3+ years</option>
                  <option value="5">5+ years</option>
                  <option value="10">10+ years</option>
                </select>
              </div>
            </div>
          </div>

          {/* Results */}
          <div className="lg:col-span-3">
            {/* Results Header */}
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 mb-6">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                  {filteredCaregivers.length} Caregiver{filteredCaregivers.length !== 1 ? 's' : ''} Found
                </h2>
                <div className="flex items-center gap-2">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Sort by:</label>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-teal-500 dark:bg-slate-700 dark:text-white"
                  >
                    <option value="rating">Rating</option>
                    <option value="price">Price (Low to High)</option>
                    <option value="distance">Distance</option>
                    <option value="experience">Experience</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Caregiver Cards */}
            <div className="space-y-6">
              {filteredCaregivers.length === 0 ? (
                <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-8 text-center">
                  <p className="text-gray-500 dark:text-gray-400">
                    No caregivers match your filters. Try adjusting your search criteria.
                  </p>
                </div>
              ) : (
                filteredCaregivers.map((caregiver) => (
                  <div key={caregiver.id} className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                      {/* Avatar & Basic Info */}
                      <div className="lg:col-span-1">
                        <div className="flex flex-col items-center text-center">
                          <div className="w-24 h-24 bg-teal-100 dark:bg-teal-900/30 rounded-full flex items-center justify-center mb-4">
                            {caregiver.avatar ? (
                              <img src={caregiver.avatar} alt={caregiver.full_name} className="w-24 h-24 rounded-full object-cover" />
                            ) : (
                              <span className="text-2xl font-bold text-teal-600 dark:text-teal-400">
                                {caregiver.first_name[0]}{caregiver.last_name[0]}
                              </span>
                            )}
                          </div>
                          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">
                            {caregiver.full_name}
                          </h3>
                          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                            {caregiver.specialization}
                          </p>
                          {caregiver.verified && (
                            <span className="inline-flex items-center px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 text-xs font-medium rounded-full">
                              ✓ Verified
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Details */}
                      <div className="lg:col-span-2">
                        <div className="space-y-4">
                          {/* Rating & Experience */}
                          <div className="flex flex-wrap items-center gap-4">
                            <div className="flex items-center gap-1">
                              {renderStars(caregiver.rating)}
                              <span className="text-sm text-gray-600 dark:text-gray-400 ml-1">
                                {caregiver.rating} ({caregiver.total_reviews} reviews)
                              </span>
                            </div>
                            <div className="text-sm text-gray-600 dark:text-gray-400">
                              {caregiver.experience_years} years experience
                            </div>
                          </div>

                          {/* Bio */}
                          <p className="text-gray-700 dark:text-gray-300 text-sm">
                            {caregiver.bio}
                          </p>

                          {/* Services */}
                          <div>
                            <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Services:</p>
                            <div className="flex flex-wrap gap-2">
                              {caregiver.services.map((service) => (
                                <span
                                  key={service}
                                  className="inline-block px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 text-xs rounded-full"
                                >
                                  {service}
                                </span>
                              ))}
                            </div>
                          </div>

                          {/* Languages & Location */}
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="font-medium text-gray-700 dark:text-gray-300">Languages: </span>
                              <span className="text-gray-600 dark:text-gray-400">{caregiver.languages.join(', ')}</span>
                            </div>
                            <div>
                              <span className="font-medium text-gray-700 dark:text-gray-300">Location: </span>
                              <span className="text-gray-600 dark:text-gray-400">
                                {caregiver.location.city}
                                {caregiver.location.distance_km && (
                                  <span className="text-teal-600 dark:text-teal-400"> ({caregiver.location.distance_km} km away)</span>
                                )}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Pricing & Actions */}
                      <div className="lg:col-span-1">
                        <div className="flex flex-col items-end text-right space-y-4">
                          {/* Price */}
                          <div>
                            <div className="text-2xl font-bold text-gray-900 dark:text-white">
                              {caregiver.hourly_rate} RWF
                            </div>
                            <div className="text-sm text-gray-600 dark:text-gray-400">per hour</div>
                          </div>

                          {/* Availability */}
                          <div className="text-sm">
                            {caregiver.availability.available ? (
                              <span className="text-green-600 dark:text-green-400 font-medium">
                                Available Now
                              </span>
                            ) : (
                              <span className="text-orange-600 dark:text-orange-400 font-medium">
                                Next available: {new Date(caregiver.availability.next_available!).toLocaleDateString()}
                              </span>
                            )}
                          </div>

                          {/* Actions */}
                          <div className="space-y-2 w-full">
                            <button
                              onClick={() => navigate(`/patient/caregivers/${caregiver.id}`)}
                              className="w-full px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white font-medium rounded-lg transition-colors"
                            >
                              View Profile
                            </button>
                            <button
                              onClick={() => navigate(`/patient/caregivers/${caregiver.id}/book`)}
                              className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
                            >
                              Book Now
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}