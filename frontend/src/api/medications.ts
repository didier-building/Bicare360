import client from './client';

export interface Medication {
  id: number;
  name: string;
  generic_name: string;
  brand_name?: string;
  dosage_form: string;
  strength: string;
  unit: string;
  requires_prescription: boolean;
  side_effects?: string;
  contraindications?: string;
  storage_instructions?: string;
  is_active: boolean;
  created_at: string;
}

export interface Prescription {
  id: number;
  patient: number;
  patient_name?: string;
  medication: number;
  medication_name?: string;
  dosage: string;
  frequency: string;
  route: string;
  start_date: string;
  end_date?: string;
  duration_days?: number;
  quantity_prescribed: number;
  refills_allowed: number;
  instructions?: string;
  is_active: boolean;
  prescribed_by?: string;
  created_at: string;
}

export interface MedicationAdherence {
  id: number;
  prescription: number;
  date: string;
  taken: boolean;
  taken_at?: string;
  missed_reason?: string;
  notes?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const medicationsAPI = {
  // Medications
  getMedications: async (params?: {
    search?: string;
    dosage_form?: string;
    requires_prescription?: boolean;
    is_active?: boolean;
  }): Promise<PaginatedResponse<Medication>> => {
    console.log('🔵 API Call: GET /v1/medications/', params);
    const response = await client.get<PaginatedResponse<Medication>>('/v1/medications/', { params });
    console.log('✅ API Response: GET /v1/medications/', response.data);
    return response.data;
  },

  getMedication: async (id: number): Promise<Medication> => {
    console.log(`🔵 API Call: GET /v1/medications/${id}/`);
    const response = await client.get<Medication>(`/v1/medications/${id}/`);
    console.log(`✅ API Response: GET /v1/medications/${id}/`, response.data);
    return response.data;
  },

  getActiveMedications: async (): Promise<Medication[]> => {
    console.log('🔵 API Call: GET /v1/medications/active/');
    const response = await client.get<Medication[]>('/v1/medications/active/');
    console.log('✅ API Response: GET /v1/medications/active/', response.data);
    return response.data;
  },

  createMedication: async (data: Partial<Medication>): Promise<Medication> => {
    console.log('🔵 API Call: POST /v1/medications/', data);
    const response = await client.post<Medication>('/v1/medications/', data);
    console.log('✅ API Response: POST /v1/medications/', response.data);
    return response.data;
  },

  updateMedication: async (id: number, data: Partial<Medication>): Promise<Medication> => {
    console.log(`🔵 API Call: PATCH /v1/medications/${id}/`, data);
    const response = await client.patch<Medication>(`/v1/medications/${id}/`, data);
    console.log(`✅ API Response: PATCH /v1/medications/${id}/`, response.data);
    return response.data;
  },

  // Prescriptions
  getPrescriptions: async (params?: {
    patient?: number;
    medication?: number;
    is_active?: boolean;
  }): Promise<PaginatedResponse<Prescription>> => {
    console.log('🔵 API Call: GET /v1/prescriptions/', params);
    const response = await client.get<PaginatedResponse<Prescription>>('/v1/prescriptions/', { params });
    console.log('✅ API Response: GET /v1/prescriptions/', response.data);
    return response.data;
  },

  getPrescription: async (id: number): Promise<Prescription> => {
    console.log(`🔵 API Call: GET /v1/prescriptions/${id}/`);
    const response = await client.get<Prescription>(`/v1/prescriptions/${id}/`);
    console.log(`✅ API Response: GET /v1/prescriptions/${id}/`, response.data);
    return response.data;
  },

  getCurrentPrescriptions: async (): Promise<PaginatedResponse<Prescription>> => {
    console.log('🔵 API Call: GET /v1/prescriptions/current/');
    const response = await client.get<PaginatedResponse<Prescription>>('/v1/prescriptions/current/');
    console.log('✅ API Response: GET /v1/prescriptions/current/', response.data);
    return response.data;
  },

  createPrescription: async (data: Partial<Prescription>): Promise<Prescription> => {
    console.log('🔵 API Call: POST /v1/prescriptions/', data);
    const response = await client.post<Prescription>('/v1/prescriptions/', data);
    console.log('✅ API Response: POST /v1/prescriptions/', response.data);
    return response.data;
  },

  updatePrescription: async (id: number, data: Partial<Prescription>): Promise<Prescription> => {
    console.log(`🔵 API Call: PATCH /v1/prescriptions/${id}/`, data);
    const response = await client.patch<Prescription>(`/v1/prescriptions/${id}/`, data);
    console.log(`✅ API Response: PATCH /v1/prescriptions/${id}/`, response.data);
    return response.data;
  },

  deactivatePrescription: async (id: number): Promise<Prescription> => {
    console.log(`🔵 API Call: POST /v1/prescriptions/${id}/deactivate/`);
    const response = await client.post<Prescription>(`/v1/prescriptions/${id}/deactivate/`);
    console.log(`✅ API Response: POST /v1/prescriptions/${id}/deactivate/`, response.data);
    return response.data;
  },

  // Adherence
  getAdherence: async (prescriptionId: number): Promise<MedicationAdherence[]> => {
    console.log(`🔵 API Call: GET /v1/prescriptions/${prescriptionId}/adherence/`);
    const response = await client.get<MedicationAdherence[]>(`/v1/prescriptions/${prescriptionId}/adherence/`);
    console.log(`✅ API Response: GET /v1/prescriptions/${prescriptionId}/adherence/`, response.data);
    return response.data;
  },

  recordAdherence: async (data: Partial<MedicationAdherence>): Promise<MedicationAdherence> => {
    console.log('🔵 API Call: POST /v1/medication-adherence/', data);
    const response = await client.post<MedicationAdherence>('/v1/medication-adherence/', data);
    console.log('✅ API Response: POST /v1/medication-adherence/', response.data);
    return response.data;
  },
};
