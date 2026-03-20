/**
 * Appointments API Client
 * Handles all appointment scheduling endpoints
 */
import apiClient from './client';

export interface Appointment {
  id: number;
  patient: number;
  patient_name?: string;
  hospital: number;
  hospital_name?: string;
  discharge_summary?: number | null;
  prescription?: number | null;
  appointment_datetime: string;
  appointment_type: 'follow_up' | 'medication_review' | 'consultation' | 'emergency' | 'routine_checkup';
  status: 'scheduled' | 'confirmed' | 'completed' | 'cancelled' | 'no_show' | 'rescheduled';
  location_type: 'hospital' | 'home_visit' | 'telemedicine';
  provider_name?: string;
  department?: string;
  reason?: string;
  notes?: string;
  duration_minutes?: number;
  reminder_sent?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface AppointmentListParams {
  status?: string;
  appointment_type?: string;
  patient?: number;
  hospital?: number;
  location_type?: string;
  search?: string;
  ordering?: string;
  limit?: number;
  offset?: number;
}

export interface AppointmentListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Appointment[];
}

export interface AppointmentCreateData {
  patient: number;
  hospital: number;
  discharge_summary?: number | null;
  prescription?: number | null;
  appointment_datetime: string;
  appointment_type: string;
  location_type: string;
  provider_name?: string;
  department?: string;
  reason?: string;
  notes?: string;
  duration_minutes?: number;
}

const appointmentsAPI = {
  /**
   * Get list of appointments with optional filters
   */
  async getAppointments(params?: AppointmentListParams): Promise<AppointmentListResponse> {
    // console.log('🔵 Fetching appointments:', params);
    try {
      const response = await apiClient.get<AppointmentListResponse>('/v1/appointments/', { params });
      console.log('✅ Appointments fetched:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Error fetching appointments:', error);
      throw error;
    }
  },

  /**
   * Get a single appointment by ID
   */
  async getAppointment(id: number): Promise<Appointment> {
    // console.log('🔵 Fetching appointment:', id);
    try {
      const response = await apiClient.get<Appointment>(`/v1/appointments/${id}/`);
      console.log('✅ Appointment fetched:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Error fetching appointment:', error);
      throw error;
    }
  },

  /**
   * Get upcoming appointments (future, not cancelled/completed)
   */
  async getUpcomingAppointments(params?: AppointmentListParams): Promise<AppointmentListResponse> {
    // console.log('🔵 Fetching upcoming appointments');
    try {
      const response = await apiClient.get<AppointmentListResponse>('/v1/appointments/upcoming/', { params });
      console.log('✅ Upcoming appointments fetched:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Error fetching upcoming appointments:', error);
      throw error;
    }
  },

  /**
   * Create a new appointment
   */
  async createAppointment(data: AppointmentCreateData): Promise<Appointment> {
    // console.log('🔵 Creating appointment:', data);
    try {
      const response = await apiClient.post<Appointment>('/v1/appointments/', data);
      console.log('✅ Appointment created:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Error creating appointment:', error);
      throw error;
    }
  },

  /**
   * Update an existing appointment
   */
  async updateAppointment(id: number, data: Partial<AppointmentCreateData>): Promise<Appointment> {
    // console.log('🔵 Updating appointment:', id, data);
    try {
      const response = await apiClient.patch<Appointment>(`/v1/appointments/${id}/`, data);
      console.log('✅ Appointment updated:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Error updating appointment:', error);
      throw error;
    }
  },

  /**
   * Delete an appointment
   */
  async deleteAppointment(id: number): Promise<void> {
    // console.log('🔵 Deleting appointment:', id);
    try {
      await apiClient.delete(`/v1/appointments/${id}/`);
      console.log('✅ Appointment deleted');
    } catch (error) {
      console.error('❌ Error deleting appointment:', error);
      throw error;
    }
  },

  /**
   * Confirm an appointment
   */
  async confirmAppointment(id: number): Promise<Appointment> {
    // console.log('🔵 Confirming appointment:', id);
    try {
      const response = await apiClient.post<Appointment>(`/v1/appointments/${id}/confirm/`);
      console.log('✅ Appointment confirmed:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Error confirming appointment:', error);
      throw error;
    }
  },

  /**
   * Cancel an appointment
   */
  async cancelAppointment(id: number): Promise<Appointment> {
    // console.log('🔵 Cancelling appointment:', id);
    try {
      const response = await apiClient.post<Appointment>(`/v1/appointments/${id}/cancel/`);
      console.log('✅ Appointment cancelled:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Error cancelling appointment:', error);
      throw error;
    }
  },

  /**
   * Mark appointment as completed
   */
  async completeAppointment(id: number): Promise<Appointment> {
    // console.log('🔵 Completing appointment:', id);
    try {
      const response = await apiClient.post<Appointment>(`/v1/appointments/${id}/complete/`);
      console.log('✅ Appointment completed:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Error completing appointment:', error);
      throw error;
    }
  },
};

export default appointmentsAPI;
