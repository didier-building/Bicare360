import client from './client';

export interface Alert {
  id: number;
  patient: {
    id: number;
    first_name: string;
    last_name: string;
    medical_record_number: string;
  };
  alert_type: string;
  title?: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'new' | 'assigned' | 'in_progress' | 'resolved';
  assigned_nurse?: {
    id: number;
    user: {
      id: number;
      username: string;
      first_name: string;
      last_name: string;
    };
    phone_number?: string;
    license_number?: string;
  };
  description: string;
  created_at: string;
  acknowledged_at?: string | null;
  resolved_at?: string | null;
  resolution_notes?: string;
  is_overdue?: boolean;
  sla_deadline?: string;
}

export interface AlertListParams {
  status?: string;
  severity?: string;
  assigned_to_me?: boolean;
  ordering?: string;
  page?: number;
  page_size?: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const nursingAPI = {
  // Get alerts list
  getAlerts: async (params?: AlertListParams): Promise<PaginatedResponse<Alert>> => {
    const response = await client.get<PaginatedResponse<Alert>>('/v1/nursing/alerts/', { params });
    return response.data;
  },

  // Get single alert
  getAlert: async (id: number): Promise<Alert> => {
    const response = await client.get<Alert>(`/v1/nursing/alerts/${id}/`);
    return response.data;
  },

  // Acknowledge alert
  acknowledgeAlert: async (id: number): Promise<Alert> => {
    const response = await client.post<Alert>(`/v1/nursing/alerts/${id}/acknowledge/`);
    return response.data;
  },

  // Assign alert to self
  assignAlertToSelf: async (id: number): Promise<Alert> => {
    const response = await client.post<Alert>(`/v1/nursing/alerts/${id}/assign/`);
    return response.data;
  },

  // Resolve alert
  resolveAlert: async (id: number, notes?: string): Promise<Alert> => {
    const response = await client.post<Alert>(`/v1/nursing/alerts/${id}/resolve/`, { notes });
    return response.data;
  },

  // Add notes to alert
  addNotes: async (id: number, notes: string): Promise<Alert> => {
    const response = await client.patch<Alert>(`/v1/nursing/alerts/${id}/`, { notes });
    return response.data;
  },
};
