/**
 * Hospitals API Client
 * Handles all hospital-related endpoints
 */
import apiClient from './client';

export interface Hospital {
  id: number;
  name: string;
  code: string;
  hospital_type: 'public' | 'private' | 'ngo';
  province: string;
  district: string;
  sector: string;
  phone_number?: string;
  email?: string;
  emr_integration_type?: string;
  emr_system_name?: string;
  status: 'active' | 'inactive';
  created_at?: string;
  updated_at?: string;
}

export interface HospitalListParams {
  search?: string;
  district?: string;
  province?: string;
  hospital_type?: string;
  status?: string;
  ordering?: string;
  limit?: number;
  offset?: number;
}

export interface HospitalListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Hospital[];
}

const hospitalsAPI = {
  /**
   * Get list of hospitals with optional filters
   */
  async getHospitals(params?: HospitalListParams): Promise<HospitalListResponse> {
    try {
      const response = await apiClient.get<HospitalListResponse>('/v1/hospitals/', { params });
      return response.data;
    } catch (error) {
      console.error('❌ Error fetching hospitals:', error);
      throw error;
    }
  },

  /**
   * Get a single hospital by ID
   */
  async getHospital(id: number): Promise<Hospital> {
    try {
      const response = await apiClient.get<Hospital>(`/v1/hospitals/${id}/`);
      return response.data;
    } catch (error) {
      console.error('❌ Error fetching hospital:', error);
      throw error;
    }
  },
};

export default hospitalsAPI;
