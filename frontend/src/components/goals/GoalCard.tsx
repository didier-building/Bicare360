import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import goalsAPI from '../../api/goals';
import type { DailyGoal, GoalStats } from '../../api/goals';
import {
  CheckCircleIcon,
  FireIcon,
  ChartBarIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckCircleSolid } from '@heroicons/react/24/solid';

interface GoalCardProps {
  goal: DailyGoal;
  onDelete?: (id: number) => void;
}

const CATEGORY_COLORS: Record<DailyGoal['category'], string> = {
  exercise: 'bg-blue-100 text-blue-800 border-blue-300',
  hydration: 'bg-cyan-100 text-cyan-800 border-cyan-300',
  medication: 'bg-purple-100 text-purple-800 border-purple-300',
  nutrition: 'bg-green-100 text-green-800 border-green-300',
  sleep: 'bg-indigo-100 text-indigo-800 border-indigo-300',
  meditation: 'bg-pink-100 text-pink-800 border-pink-300',
  custom: 'bg-gray-100 text-gray-800 border-gray-300',
};

const CATEGORY_LABELS: Record<DailyGoal['category'], string> = {
  exercise: 'Exercise',
  hydration: 'Hydration',
  medication: 'Medication',
  nutrition: 'Nutrition',
  sleep: 'Sleep',
  meditation: 'Meditation',
  custom: 'Custom',
};

const WEEKDAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

const GoalCard: React.FC<GoalCardProps> = ({ goal, onDelete }) => {
  const queryClient = useQueryClient();
  const [showStats, setShowStats] = useState(false);
  const [stats, setStats] = useState<GoalStats | null>(null);
  const [loadingStats, setLoadingStats] = useState(false);

  const tickMutation = useMutation({
    mutationFn: () => goalsAPI.tickGoal(goal.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['daily-goals'] });
      queryClient.invalidateQueries({ queryKey: ['goal-analytics'] });
    },
  });

  const untickMutation = useMutation({
    mutationFn: () => goalsAPI.untickGoal(goal.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['daily-goals'] });
      queryClient.invalidateQueries({ queryKey: ['goal-analytics'] });
    },
  });

  const handleTickToggle = () => {
    if (goal.is_completed) {
      untickMutation.mutate();
    } else {
      tickMutation.mutate();
    }
  };

  const handleShowStats = async () => {
    if (!showStats) {
      setLoadingStats(true);
      try {
        const statsData = await goalsAPI.getGoalStats(goal.id);
        setStats(statsData);
        setShowStats(true);
      } catch (error) {
        console.error('Failed to load stats:', error);
      } finally {
        setLoadingStats(false);
      }
    } else {
      setShowStats(false);
    }
  };

  const progressPercentage = goal.target_value > 0
    ? Math.min(100, (goal.current_value / goal.target_value) * 100)
    : 0;

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow p-4">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className={`px-2 py-1 text-xs font-medium rounded-full border ${CATEGORY_COLORS[goal.category]}`}>
              {CATEGORY_LABELS[goal.category]}
            </span>
            {goal.is_recurring && (
              <span className="text-xs text-gray-500">
                {goal.recurrence_days.length === 7 ? 'Daily' : 'Recurring'}
              </span>
            )}
          </div>
          <h3 className="text-lg font-semibold text-gray-900">{goal.title}</h3>
          {goal.target_value > 0 && (
            <p className="text-sm text-gray-600">
              Target: {goal.target_value} {goal.category === 'exercise' ? 'steps' : 'units'}
            </p>
          )}
        </div>
        
        {/* Completion Button */}
        <button
          onClick={handleTickToggle}
          disabled={tickMutation.isPending || untickMutation.isPending}
          className={`p-2 rounded-full transition-all ${
            goal.is_completed
              ? 'bg-green-100 hover:bg-green-200 text-green-600'
              : 'bg-gray-100 hover:bg-gray-200 text-gray-400'
          } disabled:opacity-50`}
          title={goal.is_completed ? 'Mark incomplete' : 'Mark complete'}
        >
          {goal.is_completed ? (
            <CheckCircleSolid className="w-8 h-8" />
          ) : (
            <CheckCircleIcon className="w-8 h-8" />
          )}
        </button>
      </div>

      {/* Progress Bar */}
      {goal.target_value > 0 && (
        <div className="mb-3">
          <div className="flex justify-between text-xs text-gray-600 mb-1">
            <span>{goal.current_value}</span>
            <span>{goal.target_value}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${
                goal.is_completed ? 'bg-green-500' : 'bg-blue-500'
              }`}
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>
      )}

      {/* Recurrence Days */}
      {goal.is_recurring && goal.recurrence_days.length > 0 && goal.recurrence_days.length < 7 && (
        <div className="flex gap-1 mb-3">
          {WEEKDAY_LABELS.map((day, index) => (
            <span
              key={index}
              className={`text-xs px-2 py-1 rounded ${
                goal.recurrence_days.includes(index)
                  ? 'bg-blue-100 text-blue-700 font-medium'
                  : 'bg-gray-100 text-gray-400'
              }`}
            >
              {day}
            </span>
          ))}
        </div>
      )}

      {/* Stats Toggle */}
      {showStats && stats && (
        <div className="bg-gray-50 rounded-lg p-3 mb-3 grid grid-cols-2 gap-3">
          <div className="flex items-center gap-2">
            <FireIcon className="w-5 h-5 text-orange-500" />
            <div>
              <p className="text-xs text-gray-600">Streak</p>
              <p className="text-lg font-bold text-gray-900">{stats.streak} days</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <ChartBarIcon className="w-5 h-5 text-blue-500" />
            <div>
              <p className="text-xs text-gray-600">Completion</p>
              <p className="text-lg font-bold text-gray-900">{stats.completion_rate.toFixed(1)}%</p>
            </div>
          </div>
          <div className="col-span-2">
            <p className="text-xs text-gray-600">Total Completions</p>
            <p className="text-sm font-semibold text-gray-900">{stats.total_completions} times</p>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2">
        <button
          onClick={handleShowStats}
          disabled={loadingStats}
          className="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-blue-700 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors disabled:opacity-50"
        >
          <ChartBarIcon className="w-4 h-4" />
          {loadingStats ? 'Loading...' : showStats ? 'Hide Stats' : 'Show Stats'}
        </button>
        {onDelete && (
          <button
            onClick={() => onDelete(goal.id)}
            className="px-3 py-2 text-sm font-medium text-red-700 bg-red-50 rounded-md hover:bg-red-100 transition-colors"
            title="Delete goal"
          >
            <TrashIcon className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Completion Time */}
      {goal.is_completed && goal.completed_at && (
        <p className="text-xs text-gray-500 mt-2">
          Completed {new Date(goal.completed_at).toLocaleTimeString()}
        </p>
      )}
    </div>
  );
};

export default GoalCard;
