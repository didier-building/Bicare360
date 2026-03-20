/**
 * Utility to clear all application caches
 */

export const clearAllCache = () => {
  // Clear localStorage
  const keysToKeep = ['theme']; // Keep theme preference
  const storage = { ...localStorage };
  
  Object.keys(storage).forEach(key => {
    if (!keysToKeep.includes(key)) {
      localStorage.removeItem(key);
    }
  });
  
  // Clear sessionStorage
  sessionStorage.clear();
  
  console.log('✅ All caches cleared');
};

export const clearAuthCache = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  sessionStorage.clear();
  console.log('✅ Auth cache cleared');
};

export const forceReload = () => {
  clearAllCache();
  window.location.href = '/';
};
