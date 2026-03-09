import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

export default function CaregiverProfilePage() {
  const navigate = useNavigate();
  const [caregiver, setCaregiver] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const caregiverData = localStorage.getItem('caregiver');
    if (caregiverData) {
      setCaregiver(JSON.parse(caregiverData));
    }
    setIsLoading(false);
  }, []);

  const handleUpdateAvailability = async (status: string) => {
    try {
      // This would call API to update availability
      toast.success(`Availability updated to: ${status}`);
    } catch (error) {
      toast.error('Failed to update availability');
    }
  };

  if (isLoading) {
    return <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600"></div>
    </div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">My Profile</h1>
          <button
            onClick={() => navigate('/caregiver/dashboard')}
            className="px-4 py-2 text-teal-600 hover:bg-teal-50 dark:hover:bg-teal-900/20 rounded-lg"
          >
            ← Back to Dashboard
          </button>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Personal Information
              </h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-600 dark:text-gray-400">Name</label>
                  <p className="font-medium text-gray-900 dark:text-white">
                    {caregiver?.full_name}
                  </p>
                </div>
                <div>
                  <label className="block text-sm text-gray-600 dark:text-gray-400">Email</label>
                  <p className="font-medium text-gray-900 dark:text-white">
                    {caregiver?.email}
                  </p>
                </div>
                <div>
                  <label className="block text-sm text-gray-600 dark:text-gray-400">Phone</label>
                  <p className="font-medium text-gray-900 dark:text-white">
                    {caregiver?.phone_number}
                  </p>
                </div>
                <div>
                  <label className="block text-sm text-gray-600 dark:text-gray-400">Profession</label>
                  <p className="font-medium text-gray-900 dark:text-white">
                    {caregiver?.profession}
                  </p>
                </div>
              </div>
            </div>

            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Availability Status
              </h2>
              <div className="flex gap-4">
                <button
                  onClick={() => handleUpdateAvailability('available')}
                  className={`px-4 py-2 rounded-lg ${
                    caregiver?.availability_status === 'available'
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-200 text-gray-700'
                  }`}
                >
                  Available
                </button>
                <button
                  onClick={() => handleUpdateAvailability('busy')}
                  className={`px-4 py-2 rounded-lg ${
                    caregiver?.availability_status === 'busy'
                      ? 'bg-yellow-600 text-white'
                      : 'bg-gray-200 text-gray-700'
                  }`}
                >
                  Busy
                </button>
                <button
                  onClick={() => handleUpdateAvailability('unavailable')}
                  className={`px-4 py-2 rounded-lg ${
                    caregiver?.availability_status === 'unavailable'
                      ? 'bg-red-600 text-white'
                      : 'bg-gray-200 text-gray-700'
                  }`}
                >
                  Unavailable
                </button>
              </div>
            </div>

            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Rating & Reviews
              </h2>
              <div className="flex items-center gap-4">
                <div className="text-4xl font-bold text-teal-600">
                  {caregiver?.rating?.toFixed(1)}
                </div>
                <div>
                  <div className="flex items-center gap-1">
                    {[...Array(5)].map((_, i) => (
                      <span key={i} className={i < Math.round(caregiver?.rating || 0) ? 'text-yellow-400' : 'text-gray-300'}>
                        ⭐
                      </span>
                    ))}
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {caregiver?.total_reviews} reviews
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
