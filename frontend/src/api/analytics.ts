import client from './client';

export interface AlertDashboardStats {
  status_counts: {
    new: number;
    assigned: number;
    in_progress: number;
    resolved: number;
    escalated?: number;
  };
  severity_counts: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  overdue_count: number;
  avg_response_time_minutes: number | null;
  avg_resolution_time_minutes: number | null;
  total_active: number;
}

export interface PatientStats {
  total_patients: number;
  active_patients: number;
  inactive_patients: number;
  new_enrollments_today: number;
  new_enrollments_this_week: number;
}

export interface DashboardMetrics {
  alerts: AlertDashboardStats;
  patients: PatientStats;
  timestamp: string;
}

const BASE_URL = '/v1';

export const analyticsAPI = {
  /**
   * Get alert dashboard statistics
   */
  getAlertDashboard: async (): Promise<AlertDashboardStats> => {
    try {
      const response = await client.get<AlertDashboardStats>(
        `${BASE_URL}/nursing/alerts/dashboard/`
      );
      return response.data;
    } catch (error) {
      console.error('Failed to fetch alert dashboard:', error);
      throw error;
    }
  },

  /**
   * Get patient statistics
   */
  getPatientStats: async (): Promise<PatientStats> => {
    try {
      const response = await client.get<PatientStats>(
        `${BASE_URL}/patients/stats/`
      );
      return response.data;
    } catch (error) {
      console.error('Failed to fetch patient stats:', error);
      throw error;
    }
  },

  /**
   * Get combined dashboard metrics
   */
  getDashboardMetrics: async (): Promise<DashboardMetrics> => {
    try {
      const [alertsData, patientsData] = await Promise.all([
        analyticsAPI.getAlertDashboard(),
        analyticsAPI.getPatientStats().catch(() => ({
          total_patients: 0,
          active_patients: 0,
          inactive_patients: 0,
          new_enrollments_today: 0,
          new_enrollments_this_week: 0,
        })),
      ]);

      return {
        alerts: alertsData,
        patients: patientsData as PatientStats,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Failed to fetch dashboard metrics:', error);
      throw error;
    }
  },
};

export default analyticsAPI;
