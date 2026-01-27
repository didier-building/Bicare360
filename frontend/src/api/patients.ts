import client from './client';

export interface Address {
  id: number;
  province: string;
  district: string;
  sector: string;
  cell: string;
  village: string;
  latitude?: number;
  longitude?: number;
  street_address?: string;
  landmarks?: string;
  created_at: string;
  updated_at: string;
}

export interface EmergencyContact {
  id: number;
  full_name: string;
  relationship: string;
  phone_number: string;
  alt_phone_number?: string;
  is_primary: boolean;
  created_at: string;
  updated_at: string;
}

export interface PatientList {
  id: number;
  full_name: string;
  national_id: string;
  phone_number: string;
  age: number;
  gender: string;
  is_active: boolean;
  enrolled_date: string;
}

export interface PatientDetail extends PatientList {
  first_name: string;
  last_name: string;
  first_name_kinyarwanda?: string;
  last_name_kinyarwanda?: string;
  date_of_birth: string;
  email?: string;
  blood_type?: string;
  alt_phone_number?: string;
  enrolled_by_username: string;
  prefers_sms: boolean;
  prefers_whatsapp: boolean;
  language_preference: string;
  address?: Address;
  emergency_contacts?: EmergencyContact[];
  updated_at: string;
}

export interface PatientResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

export interface SearchPatient extends PatientList {
  first_name: string;
  last_name: string;
  email?: string;
  date_of_birth?: string;
  blood_type?: string;
}

const BASE_URL = '/v1/patients';

export const patientsAPI = {
  /**
   * Advanced patient search with full-text search and filtering
   */
  searchPatients: async (params?: {
    q?: string;
    is_active?: boolean | string;
    gender?: string;
    blood_type?: string;
    enrolled_after?: string;
    enrolled_before?: string;
    sort?: string;
    order?: 'asc' | 'desc';
    limit?: number;
  }): Promise<SearchPatient[]> => {
    try {
      const response = await client.get(`${BASE_URL}/search/`, { params });
      return response.data;
    } catch (error) {
      console.error('Failed to search patients:', error);
      throw error;
    }
  },

  /**
   * Get list of patients with filtering and search
   */
  getPatients: async (params?: {
    search?: string;
    is_active?: boolean;
    gender?: string;
    ordering?: string;
    limit?: number;
    offset?: number;
  }): Promise<PatientResponse<PatientList>> => {
    try {
      const response = await client.get(`${BASE_URL}/`, { params });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch patients:', error);
      throw error;
    }
  },

  /**
   * Get patient details by ID
   */
  getPatient: async (id: number): Promise<PatientDetail> => {
    const response = await client.get(`${BASE_URL}/${id}/`);
    return response.data;
  },

  /**
   * Update patient information
   */
  updatePatient: async (
    id: number,
    data: Partial<PatientDetail>
  ): Promise<PatientDetail> => {
    const response = await client.patch(`${BASE_URL}/${id}/`, data);
    return response.data;
  },

  /**
   * Add notes to patient (if there's a notes endpoint)
   */
  addPatientNotes: async (
    id: number,
    notes: string
  ): Promise<PatientDetail> => {
    const response = await client.patch(`${BASE_URL}/${id}/`, {
      notes,
    });
    return response.data;
  },
};

export default patientsAPI;
