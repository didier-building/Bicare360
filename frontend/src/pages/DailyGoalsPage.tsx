import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import goalsAPI from '../api/goals';
import type { DailyGoal } from '../api/goals';
import GoalList from '../components/goals/GoalList';
import CreateGoalForm from '../components/goals/CreateGoalForm';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import {
  PlusIcon,
  FireIcon,
  ChartBarIcon,
  CheckCircleIcon,
  FunnelIcon,
} from '@heroicons/react/24/outline';

const FILTER_OPTIONS: Array<{ value: 'all' | 'today' | DailyGoal['category']; label: string }> = [
  { value: 'all', label: 'All Goals' },
  { value: 'today', label: "Today's Goals" },
  { value: 'exercise', label: 'Exercise' },
  { value: 'hydration', label: 'Hydration' },
  { value: 'medication', label: 'Medication' },
  { value: 'nutrition', label: 'Nutrition' },
  { value: 'sleep', label: 'Sleep' },
  { value: 'meditation', label: 'Meditation' },
  { value: 'custom', label: 'Custom' },
];

const DailyGoalsPage: React.FC = () => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [filter, setFilter] = useState<'all' | 'today' | DailyGoal['category']>('today');

  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['goal-analytics'],
    queryFn: () => goalsAPI.getAnalytics(),
    staleTime: 1000 * 60, // 1 minute
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Daily Goals</h1>
              <p className="text-sm text-gray-600 mt-1">
                Track your daily habits and build healthy streaks
              </p>
            </div>
            <button
              onClick={() => setShowCreateForm(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
            >
              <PlusIcon className="w-5 h-5" />
              <span className="font-medium">New Goal</span>
            </button>
          </div>

          {/* Analytics Cards */}
          {analyticsLoading ? (
            <div className="flex justify-center py-8">
              <LoadingSpinner />
            </div>
          ) : analytics ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Total Goals */}
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-blue-700">Total Goals</p>
                    <p className="text-3xl font-bold text-blue-900 mt-1">
                      {analytics.total_goals}
                    </p>
                  </div>
                  <ChartBarIcon className="w-10 h-10 text-blue-500 opacity-50" />
                </div>
              </div>

              {/* Today's Progress */}
              <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-green-700">Completed Today</p>
                    <p className="text-3xl font-bold text-green-900 mt-1">
                      {analytics.completed_today}/{analytics.total_goals}
                    </p>
                  </div>
                  <CheckCircleIcon className="w-10 h-10 text-green-500 opacity-50" />
                </div>
                {analytics.total_goals > 0 && (
                  <div className="mt-3">
                    <div className="flex justify-between text-xs text-green-700 mb-1">
                      <span>{analytics.completion_percentage_today.toFixed(0)}%</span>
                    </div>
                    <div className="w-full bg-green-200 rounded-full h-2">
                      <div
                        className="bg-green-600 h-2 rounded-full transition-all"
                        style={{ width: `${analytics.completion_percentage_today}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Weekly Success Rate */}
              <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4 border border-purple-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-purple-700">Weekly Success</p>
                    <p className="text-3xl font-bold text-purple-900 mt-1">
                      {analytics.weekly_completion_rate.toFixed(1)}%
                    </p>
                  </div>
                  <FireIcon className="w-10 h-10 text-purple-500 opacity-50" />
                </div>
                <p className="text-xs text-purple-600 mt-2">
                  Last 7 days average
                </p>
              </div>

              {/* Top Category */}
              <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4 border border-orange-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-orange-700">Top Category</p>
                    <p className="text-lg font-bold text-orange-900 mt-1 capitalize">
                      {analytics.most_completed_category || 'None yet'}
                    </p>
                  </div>
                  <div className="text-3xl">
                    {analytics.most_completed_category === 'exercise' && '🏃'}
                    {analytics.most_completed_category === 'hydration' && '💧'}
                    {analytics.most_completed_category === 'medication' && '💊'}
                    {analytics.most_completed_category === 'nutrition' && '🥗'}
                    {analytics.most_completed_category === 'sleep' && '😴'}
                    {analytics.most_completed_category === 'meditation' && '🧘'}
                    {analytics.most_completed_category === 'custom' && '✨'}
                    {!analytics.most_completed_category && '📊'}
                  </div>
                </div>
                <p className="text-xs text-orange-600 mt-2">
                  Most completed goals
                </p>
              </div>
            </div>
          ) : null}
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-3 overflow-x-auto">
            <FunnelIcon className="w-5 h-5 text-gray-400 flex-shrink-0" />
            {FILTER_OPTIONS.map(option => (
              <button
                key={option.value}
                onClick={() => setFilter(option.value)}
                className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                  filter === option.value
                    ? 'bg-blue-100 text-blue-700 border-2 border-blue-300'
                    : 'bg-gray-100 text-gray-700 border-2 border-transparent hover:bg-gray-200'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Goals List */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <GoalList filter={filter} showDeleteButton={true} />
      </div>

      {/* Create Goal Modal */}
      {showCreateForm && (
        <CreateGoalForm
          onClose={() => setShowCreateForm(false)}
          onSuccess={() => {
            setShowCreateForm(false);
          }}
        />
      )}

      {/* Empty State CTA */}
      {analytics && analytics.total_goals === 0 && (
        <div className="max-w-2xl mx-auto px-4 py-12 text-center">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
            <div className="text-6xl mb-4">🎯</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Start Your Journey to Better Health
            </h2>
            <p className="text-gray-600 mb-6">
              Set your first daily goal and track your progress. Build healthy habits one day at a time.
            </p>
            <button
              onClick={() => setShowCreateForm(true)}
              className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-md font-medium"
            >
              <PlusIcon className="w-5 h-5" />
              Create Your First Goal
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DailyGoalsPage;
