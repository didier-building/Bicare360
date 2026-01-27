import apiClient from './client';

export interface DischargeSummary {
  id: number;
  patient: {
    id: number;
    full_name: string;
    national_id?: string;
    phone_number?: string;
    age?: number;
    gender?: string;
  };
  hospital: number;
  hospital_name?: string;
  hospital_code?: string;
  admission_date: string;
  discharge_date: string;
  length_of_stay_days?: number;
  primary_diagnosis: string;
  secondary_diagnoses: string;
  icd10_primary: string;
  icd10_secondary: string;
  procedures_performed: string;
  treatment_summary: string;
  discharge_condition: 'improved' | 'stable' | 'unchanged' | 'deteriorated';
  discharge_instructions: string;
  discharge_instructions_kinyarwanda: string;
  diet_instructions: string;
  activity_restrictions: string;
  follow_up_required: boolean;
  follow_up_timeframe: string;
  follow_up_with: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  risk_factors: string;
  warning_signs: string;
  warning_signs_kinyarwanda: string;
  attending_physician: string;
  discharge_nurse: string;
  additional_notes: string;
  is_high_risk?: boolean;
  days_since_discharge?: number;
  created_by?: number;
  created_at?: string;
  updated_at?: string;
}

export interface DischargeSummaryCreateData {
  patient: number;
  hospital: number;
  admission_date: string;
  discharge_date: string;
  primary_diagnosis: string;
  secondary_diagnoses?: string;
  icd10_primary?: string;
  icd10_secondary?: string;
  procedures_performed?: string;
  treatment_summary: string;
  discharge_condition: string;
  discharge_instructions: string;
  discharge_instructions_kinyarwanda?: string;
  diet_instructions?: string;
  activity_restrictions?: string;
  follow_up_required: boolean;
  follow_up_timeframe?: string;
  follow_up_with?: string;
  risk_level: string;
  risk_factors?: string;
  warning_signs?: string;
  warning_signs_kinyarwanda?: string;
  attending_physician: string;
  discharge_nurse?: string;
  additional_notes?: string;
}

export interface DischargeSummaryListParams {
  search?: string;
  risk_level?: string;
  patient?: number;
  hospital?: number;
  page?: number;
  page_size?: number;
}

export interface DischargeSummaryListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: DischargeSummary[];
}

/**
 * Discharge Summaries API Client
 */
export const dischargeAPI = {
  /**
   * Get list of discharge summaries with optional filters
   */
  async getDischargeSummaries(params: DischargeSummaryListParams = {}): Promise<DischargeSummaryListResponse> {
    console.log('🔵 API: Fetching discharge summaries with params:', params);
    try {
      const response = await apiClient.get<DischargeSummaryListResponse>('/v1/discharge-summaries/', { params });
      console.log('✅ API: Fetched discharge summaries:', response.data.count, 'records');
      return response.data;
    } catch (error) {
      console.error('❌ API: Failed to fetch discharge summaries:', error);
      throw error;
    }
  },

  /**
   * Get a single discharge summary by ID
   */
  async getDischargeSummary(id: number): Promise<DischargeSummary> {
    console.log('🔵 API: Fetching discharge summary ID:', id);
    try {
      const response = await apiClient.get<DischargeSummary>(`/v1/discharge-summaries/${id}/`);
      console.log('✅ API: Fetched discharge summary:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ API: Failed to fetch discharge summary:', error);
      throw error;
    }
  },

  /**
   * Create a new discharge summary
   */
  async createDischargeSummary(data: DischargeSummaryCreateData): Promise<DischargeSummary> {
    console.log('🔵 API: Creating discharge summary:', data);
    try {
      const response = await apiClient.post<DischargeSummary>('/v1/discharge-summaries/', data);
      console.log('✅ API: Created discharge summary:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ API: Failed to create discharge summary:', error);
      throw error;
    }
  },

  /**
   * Update an existing discharge summary
   */
  async updateDischargeSummary(id: number, data: Partial<DischargeSummaryCreateData>): Promise<DischargeSummary> {
    console.log('🔵 API: Updating discharge summary ID:', id, 'with data:', data);
    try {
      const response = await apiClient.patch<DischargeSummary>(`/v1/discharge-summaries/${id}/`, data);
      console.log('✅ API: Updated discharge summary:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ API: Failed to update discharge summary:', error);
      throw error;
    }
  },

  /**
   * Delete a discharge summary
   */
  async deleteDischargeSummary(id: number): Promise<void> {
    console.log('🔵 API: Deleting discharge summary ID:', id);
    try {
      await apiClient.delete(`/v1/discharge-summaries/${id}/`);
      console.log('✅ API: Deleted discharge summary ID:', id);
    } catch (error) {
      console.error('❌ API: Failed to delete discharge summary:', error);
      throw error;
    }
  },

  /**
   * Get discharge summaries for a specific patient
   */
  async getPatientDischargeSummaries(patientId: number): Promise<DischargeSummary[]> {
    console.log('🔵 API: Fetching discharge summaries for patient ID:', patientId);
    try {
      const response = await apiClient.get<DischargeSummaryListResponse>('/v1/discharge-summaries/', {
        params: { patient: patientId }
      });
      console.log('✅ API: Fetched patient discharge summaries:', response.data.results.length, 'records');
      return response.data.results;
    } catch (error) {
      console.error('❌ API: Failed to fetch patient discharge summaries:', error);
      throw error;
    }
  },

  /**
   * Get discharge summaries by risk level
   */
  async getDischargeSummariesByRisk(riskLevel: string): Promise<DischargeSummary[]> {
    console.log('🔵 API: Fetching discharge summaries with risk level:', riskLevel);
    try {
      const response = await apiClient.get<DischargeSummaryListResponse>('/v1/discharge-summaries/', {
        params: { risk_level: riskLevel }
      });
      console.log('✅ API: Fetched discharge summaries by risk:', response.data.results.length, 'records');
      return response.data.results;
    } catch (error) {
      console.error('❌ API: Failed to fetch discharge summaries by risk:', error);
      throw error;
    }
  },
};
