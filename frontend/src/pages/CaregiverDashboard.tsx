import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

interface DashboardStats {
  total_bookings: number;
  pending_bookings: number;
  confirmed_bookings: number;
  upcoming_bookings: number;
  completed_bookings: number;
  cancelled_bookings: number;
  total_earnings: number;
  this_week_earnings: number;
  this_month_earnings: number;
  rating: number;
  total_reviews: number;
  availability_status: string;
  is_verified: boolean;
  upcoming_bookings_list: Array<{
    id: number;
    patient_name: string;
    service_type: string;
    start_datetime: string;
    duration_hours: number;
    status: string;
    total_cost: number;
  }>;
  recent_reviews: Array<{
    id: number;
    patient_name: string;
    rating: number;
    title: string;
    comment: string;
    created_at: string;
  }>;
}

export default function CaregiverDashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [caregiver, setCaregiver] = useState<any>(null);

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('access_token');
    const caregiverData = localStorage.getItem('caregiver');
    
    if (!token || !caregiverData) {
      toast.error('Please login to continue');
      navigate('/caregiver/login');
      return;
    }

    setCaregiver(JSON.parse(caregiverData));
    fetchDashboardStats(token);
  }, [navigate]);

  const fetchDashboardStats = async (token: string) => {
    try {
      const response = await fetch('/api/v1/caregivers/dashboard-stats/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          toast.error('Session expired. Please login again.');
          localStorage.clear();
          navigate('/caregiver/login');
          return;
        }
        throw new Error('Failed to fetch dashboard stats');
      }

      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    toast.success('Logged out successfully');
    navigate('/caregiver/login');
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-RW', {
      style: 'currency',
      currency: 'RWF',
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Welcome, {caregiver?.first_name}!
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {caregiver?.profession} • {stats?.is_verified ? '✓ Verified' : 'Pending Verification'}
              </p>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/caregiver/messages')}
                className="px-4 py-2 text-teal-600 hover:bg-teal-50 dark:hover:bg-teal-900/20 rounded-lg transition-colors"
              >
                Messages
              </button>
              <button
                onClick={() => navigate('/caregiver/profile')}
                className="px-4 py-2 text-teal-600 hover:bg-teal-50 dark:hover:bg-teal-900/20 rounded-lg transition-colors"
              >
                Profile
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Bookings"
            value={stats?.total_bookings || 0}
            icon="📅"
            color="blue"
          />
          <StatCard
            title="Upcoming"
            value={stats?.upcoming_bookings || 0}
            icon="⏰"
            color="green"
          />
          <StatCard
            title="Rating"
            value={`${stats?.rating.toFixed(1)} ⭐`}
            icon="⭐"
            color="yellow"
            subtitle={`${stats?.total_reviews} reviews`}
          />
          <StatCard
            title="This Month"
            value={formatCurrency(stats?.this_month_earnings || 0)}
            icon="💰"
            color="teal"
          />
        </div>

        {/* Earnings Overview */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Earnings Overview
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Earnings</p>
              <p className="text-2xl font-bold text-teal-600 dark:text-teal-400">
                {formatCurrency(stats?.total_earnings || 0)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">This Week</p>
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                {formatCurrency(stats?.this_week_earnings || 0)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">This Month</p>
              <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {formatCurrency(stats?.this_month_earnings || 0)}
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upcoming Bookings */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Upcoming Bookings
              </h2>
              <button
                onClick={() => navigate('/caregiver/bookings')}
                className="text-sm text-teal-600 hover:text-teal-700 dark:text-teal-400"
              >
                View All →
              </button>
            </div>
            <div className="space-y-4">
              {stats?.upcoming_bookings_list && stats.upcoming_bookings_list.length > 0 ? (
                stats.upcoming_bookings_list.map((booking) => (
                  <div key={booking.id} className="border dark:border-gray-700 rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">
                          {booking.patient_name}
                        </p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {booking.service_type}
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
                          {formatDate(booking.start_datetime)} • {booking.duration_hours}h
                        </p>
                      </div>
                      <div className="text-right">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          booking.status === 'confirmed' 
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                            : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
                        }`}>
                          {booking.status}
                        </span>
                        <p className="text-sm font-medium text-gray-900 dark:text-white mt-2">
                          {formatCurrency(booking.total_cost)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                  No upcoming bookings
                </p>
              )}
            </div>
          </div>

          {/* Recent Reviews */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Recent Reviews
            </h2>
            <div className="space-y-4">
              {stats?.recent_reviews && stats.recent_reviews.length > 0 ? (
                stats.recent_reviews.map((review) => (
                  <div key={review.id} className="border-b dark:border-gray-700 pb-4 last:border-b-0">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900 dark:text-white">
                          {review.patient_name}
                        </p>
                        <div className="flex items-center gap-1 my-1">
                          {[...Array(5)].map((_, i) => (
                            <span key={i} className={i < review.rating ? 'text-yellow-400' : 'text-gray-300'}>
                              ⭐
                            </span>
                          ))}
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {review.comment}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                          {formatDate(review.created_at)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                  No reviews yet
                </p>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function StatCard({ title, value, icon, color, subtitle }: {
  title: string;
  value: string | number;
  icon: string;
  color: string;
  subtitle?: string;
}) {
  const colorClasses: Record<string, string> = {
    blue: 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400',
    green: 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400',
    yellow: 'bg-yellow-50 dark:bg-yellow-900/20 text-yellow-600 dark:text-yellow-400',
    teal: 'bg-teal-50 dark:bg-teal-900/20 text-teal-600 dark:text-teal-400',
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 dark:text-gray-400">{title}</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{value}</p>
          {subtitle && (
            <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">{subtitle}</p>
          )}
        </div>
        <div className={`text-3xl p-3 rounded-lg ${colorClasses[color]}`}>
          {icon}
        </div>
      </div>
    </div>
  );
}
