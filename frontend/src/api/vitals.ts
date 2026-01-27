import client from './client';

export interface VitalReading {
  id: number;
  patient: number;
  reading_type: 'blood_pressure' | 'heart_rate' | 'temperature' | 'weight' | 'oxygen_saturation' | 'respiratory_rate' | 'blood_glucose';
  value: number;
  secondary_value?: number;
  unit: string;
  recorded_at: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface HealthGoal {
  id: number;
  patient: number;
  vital_type: string;
  goal_name: string;
  target_value: number;
  unit: string;
  start_date: string;
  target_date: string;
  status: 'active' | 'achieved' | 'abandoned';
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface HealthTrend {
  id: number;
  patient: number;
  vital_type: string;
  period: 'daily' | 'weekly' | 'monthly';
  period_start: string;
  period_end: string;
  reading_count: number;
  average_value: number;
  min_value: number;
  max_value: number;
  median_value: number;
  trend_direction: 'improving' | 'stable' | 'declining' | 'insufficient_data';
  created_at: string;
  updated_at: string;
}

export interface HealthSummary {
  patient_id: number;
  patient_name: string;
  latest_readings: VitalReading[];
  active_goals: number;
  total_readings: number;
}

export interface VitalTrend {
  readings: VitalReading[];
  trend_direction: 'improving' | 'stable' | 'declining' | 'insufficient_data';
  stats: {
    avg_value: number;
    min_value: number;
    max_value: number;
  };
  period_days: number;
}

export interface VitalSummary {
  [key: string]: VitalReading;
}

export interface HealthReport {
  patient_name: string;
  patient_id: number;
  period: string;
  total_readings: number;
  readings_by_type: {
    [key: string]: number;
  };
}

export interface VitalAlerts {
  abnormal_readings: Array<VitalReading & { alert_reason: string }>;
  total_abnormal: number;
}

const vitalsAPI = {
  // Vital Readings
  recordVital: (patientId: number, data: Partial<VitalReading>) =>
    client.post(`/v1/patients/${patientId}/vitals/`, data).then(res => res.data as VitalReading),

  getVitals: (patientId: number, filters?: Record<string, any>) =>
    client.get(`/v1/patients/${patientId}/vitals/`, { params: filters }).then(res => {
      const data = res.data;
      // Handle both array and paginated response
      return Array.isArray(data) ? data : (data.results || []);
    }),

  getLatestVitals: (patientId: number) =>
    client.get(`/v1/patients/${patientId}/vitals/latest/`).then(res => {
      const data = res.data;
      // Handle both array and paginated response
      return Array.isArray(data) ? data : (data.results || []);
    }),

  getVitalById: (patientId: number, vitalId: number) =>
    client.get(`/v1/patients/${patientId}/vitals/${vitalId}/`).then(res => res.data as VitalReading),

  // Health Goals
  createGoal: (patientId: number, data: Partial<HealthGoal>) =>
    client.post(`/v1/patients/${patientId}/health-goals/`, data).then(res => res.data as HealthGoal),

  getGoals: (patientId: number, filters?: Record<string, any>) =>
    client.get(`/v1/patients/${patientId}/health-goals/`, { params: filters }).then(res => {
      const data = res.data;
      // Handle both array and paginated response
      return Array.isArray(data) ? data : (data.results || []);
    }),

  updateGoal: (patientId: number, goalId: number, data: Partial<HealthGoal>) =>
    client.patch(`/v1/patients/${patientId}/health-goals/${goalId}/`, data).then(res => res.data as HealthGoal),

  // Health Progress
  getHealthSummary: (patientId: number) =>
    client.get(`/v1/patients/${patientId}/health-progress/health_summary/`).then(res => res.data as HealthSummary),

  getVitalTrends: (patientId: number, readingType: string = 'heart_rate', days: number = 7) =>
    client.get(`/v1/patients/${patientId}/health-progress/vital_trends/`, {
      params: { reading_type: readingType, days }
    }).then(res => res.data as VitalTrend),

  getVitalSummary: (patientId: number) =>
    client.get(`/v1/patients/${patientId}/health-progress/vital_summary/`).then(res => res.data as VitalSummary),

  getHealthReport: (patientId: number) =>
    client.get(`/v1/patients/${patientId}/health-progress/health_report/`).then(res => res.data as HealthReport),

  getVitalAlerts: (patientId: number) =>
    client.get(`/v1/patients/${patientId}/health-progress/vital_alerts/`).then(res => res.data as VitalAlerts),

  getHealthTrends: (patientId: number, period: 'daily' | 'weekly' | 'monthly' = 'daily') =>
    client.get(`/v1/patients/${patientId}/health-progress/health_trends/`, {
      params: { period }
    }).then(res => res.data as HealthTrend[]),
};

export default vitalsAPI;
