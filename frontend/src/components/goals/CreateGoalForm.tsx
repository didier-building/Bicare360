import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import goalsAPI from '../../api/goals';
import type { CreateGoalData, DailyGoal } from '../../api/goals';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface CreateGoalFormProps {
  onClose: () => void;
  onSuccess?: () => void;
}

const CATEGORIES: Array<{ value: DailyGoal['category']; label: string; icon: string }> = [
  { value: 'exercise', label: 'Exercise', icon: '🏃' },
  { value: 'hydration', label: 'Hydration', icon: '💧' },
  { value: 'medication', label: 'Medication', icon: '💊' },
  { value: 'nutrition', label: 'Nutrition', icon: '🥗' },
  { value: 'sleep', label: 'Sleep', icon: '😴' },
  { value: 'meditation', label: 'Meditation', icon: '🧘' },
  { value: 'custom', label: 'Custom', icon: '✨' },
];

const WEEKDAYS = [
  { value: 0, label: 'Mon' },
  { value: 1, label: 'Tue' },
  { value: 2, label: 'Wed' },
  { value: 3, label: 'Thu' },
  { value: 4, label: 'Fri' },
  { value: 5, label: 'Sat' },
  { value: 6, label: 'Sun' },
];

const CreateGoalForm: React.FC<CreateGoalFormProps> = ({ onClose, onSuccess }) => {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState<CreateGoalData>({
    title: '',
    category: 'exercise',
    target_value: 0,
    is_recurring: false,
    recurrence_days: [],
    reminder_time: '',
  });

  const createMutation = useMutation({
    mutationFn: (data: CreateGoalData) => goalsAPI.createGoal(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['daily-goals'] });
      queryClient.invalidateQueries({ queryKey: ['goal-analytics'] });
      onSuccess?.();
      onClose();
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate
    if (!formData.title.trim()) {
      alert('Please enter a goal title');
      return;
    }
    
    if (formData.target_value < 0) {
      alert('Target value must be positive');
      return;
    }

    if (formData.is_recurring && formData.recurrence_days!.length === 0) {
      alert('Please select at least one day for recurring goals');
      return;
    }

    createMutation.mutate(formData);
  };

  const handleWeekdayToggle = (day: number) => {
    const currentDays = formData.recurrence_days || [];
    const newDays = currentDays.includes(day)
      ? currentDays.filter(d => d !== day)
      : [...currentDays, day].sort();
    
    setFormData({ ...formData, recurrence_days: newDays });
  };

  const selectAllDays = () => {
    setFormData({ ...formData, recurrence_days: [0, 1, 2, 3, 4, 5, 6] });
  };

  const clearAllDays = () => {
    setFormData({ ...formData, recurrence_days: [] });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">Create Daily Goal</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <XMarkIcon className="w-6 h-6 text-gray-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Title */}
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
              Goal Title *
            </label>
            <input
              type="text"
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="e.g., Walk 10,000 steps"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          {/* Category */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Category *
            </label>
            <div className="grid grid-cols-3 sm:grid-cols-4 gap-3">
              {CATEGORIES.map(cat => (
                <button
                  key={cat.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, category: cat.value })}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    formData.category === cat.value
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-2xl mb-1">{cat.icon}</div>
                  <div className="text-xs font-medium text-gray-700">{cat.label}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Target Value */}
          <div>
            <label htmlFor="target_value" className="block text-sm font-medium text-gray-700 mb-2">
              Target Value
            </label>
            <input
              type="number"
              id="target_value"
              value={formData.target_value}
              onChange={(e) => setFormData({ ...formData, target_value: parseInt(e.target.value) || 0 })}
              min="0"
              placeholder="e.g., 10000"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">
              {formData.category === 'exercise' && 'Steps, minutes, or distance'}
              {formData.category === 'hydration' && 'Glasses or liters of water'}
              {formData.category === 'medication' && 'Number of doses'}
              {formData.category === 'nutrition' && 'Servings or calories'}
              {formData.category === 'sleep' && 'Hours of sleep'}
              {formData.category === 'meditation' && 'Minutes of meditation'}
              {formData.category === 'custom' && 'Any numeric target'}
            </p>
          </div>

          {/* Recurring */}
          <div>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.is_recurring}
                onChange={(e) => setFormData({ ...formData, is_recurring: e.target.checked })}
                className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-gray-700">Recurring Goal</span>
            </label>
            <p className="text-xs text-gray-500 mt-1">
              Goal repeats on selected days of the week
            </p>
          </div>

          {/* Recurrence Days */}
          {formData.is_recurring && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-700">
                  Repeat On *
                </label>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={selectAllDays}
                    className="text-xs text-blue-600 hover:text-blue-700 font-medium"
                  >
                    All
                  </button>
                  <button
                    type="button"
                    onClick={clearAllDays}
                    className="text-xs text-gray-600 hover:text-gray-700 font-medium"
                  >
                    None
                  </button>
                </div>
              </div>
              <div className="flex gap-2">
                {WEEKDAYS.map(day => (
                  <button
                    key={day.value}
                    type="button"
                    onClick={() => handleWeekdayToggle(day.value)}
                    className={`flex-1 py-2 px-1 text-sm font-medium rounded-lg border-2 transition-all ${
                      formData.recurrence_days?.includes(day.value)
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 text-gray-600 hover:border-gray-300'
                    }`}
                  >
                    {day.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Reminder Time */}
          <div>
            <label htmlFor="reminder_time" className="block text-sm font-medium text-gray-700 mb-2">
              Reminder Time (Optional)
            </label>
            <input
              type="time"
              id="reminder_time"
              value={formData.reminder_time}
              onChange={(e) => setFormData({ ...formData, reminder_time: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">
              Receive a daily reminder at this time
            </p>
          </div>

          {/* Error Message */}
          {createMutation.isError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-800">
                Failed to create goal. Please try again.
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createMutation.isPending ? 'Creating...' : 'Create Goal'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateGoalForm;
