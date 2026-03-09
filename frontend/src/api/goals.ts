import client from './client';

export interface DailyGoal {
  id: number;
  patient: number;
  title: string;
  category: 'exercise' | 'hydration' | 'medication' | 'nutrition' | 'sleep' | 'meditation' | 'custom';
  target_value: number;
  current_value: number;
  is_completed: boolean;
  completed_at: string | null;
  is_recurring: boolean;
  recurrence_days: number[]; // 0=Monday, 6=Sunday
  reminder_time: string | null;
  created_at: string;
  updated_at: string;
}

export interface GoalProgress {
  id: number;
  goal: number;
  date: string;
  completed: boolean;
  actual_value: number;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface GoalStats {
  streak: number;
  completion_rate: number;
  total_completions: number;
  last_completed: string | null;
}

export interface GoalAnalytics {
  total_goals: number;
  completed_today: number;
  completion_percentage_today: number;
  weekly_completion_rate: number;
  most_completed_category: string | null;
}

export interface CreateGoalData {
  title: string;
  category: DailyGoal['category'];
  target_value: number;
  is_recurring?: boolean;
  recurrence_days?: number[];
  reminder_time?: string;
}

const goalsAPI = {
  // Daily Goals CRUD
  getGoals: (filters?: Record<string, any>) =>
    client.get('/v1/daily-goals/', { params: filters }).then(res => {
      const data = res.data;
      return Array.isArray(data) ? data : (data.results || []);
    }) as Promise<DailyGoal[]>,

  getTodaysGoals: () =>
    client.get('/v1/daily-goals/', { params: { today: true } }).then(res => {
      const data = res.data;
      return Array.isArray(data) ? data : (data.results || []);
    }) as Promise<DailyGoal[]>,

  getGoalsByCategory: (category: DailyGoal['category']) =>
    client.get('/v1/daily-goals/', { params: { category } }).then(res => {
      const data = res.data;
      return Array.isArray(data) ? data : (data.results || []);
    }) as Promise<DailyGoal[]>,

  getGoalById: (goalId: number) =>
    client.get(`/v1/daily-goals/${goalId}/`).then(res => res.data as DailyGoal),

  createGoal: (data: CreateGoalData) =>
    client.post('/v1/daily-goals/', data).then(res => res.data as DailyGoal),

  updateGoal: (goalId: number, data: Partial<DailyGoal>) =>
    client.patch(`/v1/daily-goals/${goalId}/`, data).then(res => res.data as DailyGoal),

  deleteGoal: (goalId: number) =>
    client.delete(`/v1/daily-goals/${goalId}/`).then(res => res.data),

  // Goal Actions
  tickGoal: (goalId: number) =>
    client.post(`/v1/daily-goals/${goalId}/tick/`).then(res => res.data as DailyGoal),

  untickGoal: (goalId: number) =>
    client.post(`/v1/daily-goals/${goalId}/untick/`).then(res => res.data as DailyGoal),

  // Goal Statistics
  getGoalStats: (goalId: number) =>
    client.get(`/v1/daily-goals/${goalId}/stats/`).then(res => res.data as GoalStats),

  getAnalytics: () =>
    client.get('/v1/daily-goals/analytics/').then(res => res.data as GoalAnalytics),
};

export default goalsAPI;
