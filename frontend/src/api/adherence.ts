/**
 * Medication Adherence API Client
 * Handles all adherence tracking endpoints
 */
import apiClient from './client';

export interface AdherenceRecord {
  id: number;
  prescription: number;
  prescription_details?: {
    id: number;
    medication_name: string;
    dosage: string;
    frequency: string;
    frequency_times_per_day: number;
    patient_id: number;
    patient_name: string;
  };
  patient: number;
  patient_name?: string;
  scheduled_date: string;
  scheduled_time: string;
  actual_time?: string | null;
  status: 'scheduled' | 'taken' | 'missed' | 'skipped' | 'late';
  taken_at?: string | null;
  notes?: string;
  reason_missed?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface AdherenceStats {
  total: number;
  total_records: number;
  taken: number;
  taken_count: number;
  missed: number;
  missed_count: number;
  skipped: number;
  skipped_count: number;
  scheduled: number;
  scheduled_count: number;
  late: number;
  late_count: number;
  adherence_rate: number;
}

export interface AdherenceListParams {
  prescription?: number;
  patient?: number;
  status?: string;
  scheduled_date?: string;
  scheduled_date__gte?: string;  // Django filter: greater than or equal
  scheduled_date__lte?: string;  // Django filter: less than or equal
  scheduled_date__lt?: string;   // Django filter: less than
  scheduled_date__gt?: string;   // Django filter: greater than
  page?: number;
  page_size?: number;
  [key: string]: any;  // Allow additional Django filter parameters
}

export interface AdherenceListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: AdherenceRecord[];
}

/**
 * Adherence API Client
 */
export const adherenceAPI = {
  /**
   * Get list of adherence records with optional filters
   */
  async getAdherenceRecords(params: AdherenceListParams = {}): Promise<AdherenceListResponse> {
    // console.log('🔵 API: Fetching adherence records with params:', params);
    try {
      const response = await apiClient.get<AdherenceListResponse>('/v1/adherence/', { params });
      console.log('✅ API: Fetched adherence records:', response.data.count, 'records');
      return response.data;
    } catch (error) {
      console.error('❌ API: Failed to fetch adherence records:', error);
      throw error;
    }
  },

  /**
   * Get a single adherence record by ID
   */
  async getAdherenceRecord(id: number): Promise<AdherenceRecord> {
    // console.log('🔵 API: Fetching adherence record ID:', id);
    try {
      const response = await apiClient.get<AdherenceRecord>(`/v1/adherence/${id}/`);
      console.log('✅ API: Fetched adherence record:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ API: Failed to fetch adherence record:', error);
      throw error;
    }
  },

  /**
   * Mark an adherence record as taken
   */
  async markTaken(id: number): Promise<AdherenceRecord> {
    // console.log('🔵 API: Marking adherence record as taken:', id);
    try {
      const response = await apiClient.post<AdherenceRecord>(`/v1/adherence/${id}/mark_taken/`);
      console.log('✅ API: Marked adherence record as taken:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ API: Failed to mark adherence as taken:', error);
      throw error;
    }
  },

  /**
   * Mark an adherence record as missed with optional reason
   */
  async markMissed(id: number, reason?: string): Promise<AdherenceRecord> {
    // console.log('🔵 API: Marking adherence record as missed:', id, reason);
    try {
      const response = await apiClient.post<AdherenceRecord>(
        `/v1/adherence/${id}/mark_missed/`,
        { reason }
      );
      console.log('✅ API: Marked adherence record as missed:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ API: Failed to mark adherence as missed:', error);
      throw error;
    }
  },

  /**
   * Get overdue adherence records
   */
  async getOverdueRecords(params: AdherenceListParams = {}): Promise<AdherenceListResponse> {
    // console.log('🔵 API: Fetching overdue adherence records');
    try {
      const response = await apiClient.get<AdherenceListResponse>('/v1/adherence/overdue/', { params });
      console.log('✅ API: Fetched overdue adherence records:', response.data.count, 'records');
      return response.data;
    } catch (error) {
      console.error('❌ API: Failed to fetch overdue adherence records:', error);
      throw error;
    }
  },

  /**
   * Get adherence statistics
   */
  async getAdherenceStats(params: AdherenceListParams = {}): Promise<AdherenceStats> {
    // console.log('🔵 API: Fetching adherence statistics with params:', params);
    try {
      const response = await apiClient.get<AdherenceStats>('/v1/adherence/stats/', { params });
      console.log('✅ API: Fetched adherence stats:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ API: Failed to fetch adherence stats:', error);
      throw error;
    }
  },

  /**
   * Create a new adherence record
   */
  async createAdherenceRecord(data: Partial<AdherenceRecord>): Promise<AdherenceRecord> {
    // console.log('🔵 API: Creating adherence record:', data);
    try {
      const response = await apiClient.post<AdherenceRecord>('/v1/adherence/', data);
      console.log('✅ API: Created adherence record:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ API: Failed to create adherence record:', error);
      throw error;
    }
  },

  /**
   * Update an adherence record
   */
  async updateAdherenceRecord(id: number, data: Partial<AdherenceRecord>): Promise<AdherenceRecord> {
    // console.log('🔵 API: Updating adherence record ID:', id, 'with data:', data);
    try {
      const response = await apiClient.patch<AdherenceRecord>(`/v1/adherence/${id}/`, data);
      console.log('✅ API: Updated adherence record:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ API: Failed to update adherence record:', error);
      throw error;
    }
  },

  /**
   * Delete an adherence record
   */
  async deleteAdherenceRecord(id: number): Promise<void> {
    // console.log('🔵 API: Deleting adherence record ID:', id);
    try {
      await apiClient.delete(`/v1/adherence/${id}/`);
      console.log('✅ API: Deleted adherence record ID:', id);
    } catch (error) {
      console.error('❌ API: Failed to delete adherence record:', error);
      throw error;
    }
  },
};

export default adherenceAPI;
