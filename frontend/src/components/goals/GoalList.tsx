import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import goalsAPI from '../../api/goals';
import type { DailyGoal } from '../../api/goals';
import GoalCard from './GoalCard';
import LoadingSpinner from '../ui/LoadingSpinner';
import { ExclamationCircleIcon } from '@heroicons/react/24/outline';

interface GoalListProps {
  filter?: 'all' | 'today' | DailyGoal['category'];
  showDeleteButton?: boolean;
}

const GoalList: React.FC<GoalListProps> = ({ filter = 'all', showDeleteButton = true }) => {
  const queryClient = useQueryClient();

  const { data: goals, isLoading, error } = useQuery({
    queryKey: ['daily-goals', filter],
    queryFn: async () => {
      if (filter === 'today') {
        return goalsAPI.getTodaysGoals();
      } else if (filter === 'all') {
        return goalsAPI.getGoals();
      } else {
        return goalsAPI.getGoalsByCategory(filter);
      }
    },
    staleTime: 1000 * 60, // 1 minute
  });

  const deleteMutation = useMutation({
    mutationFn: (goalId: number) => goalsAPI.deleteGoal(goalId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['daily-goals'] });
      queryClient.invalidateQueries({ queryKey: ['goal-analytics'] });
    },
  });

  const handleDelete = (goalId: number) => {
    if (window.confirm('Are you sure you want to delete this goal?')) {
      deleteMutation.mutate(goalId);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
        <ExclamationCircleIcon className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
        <div>
          <h3 className="text-sm font-medium text-red-800">Failed to load goals</h3>
          <p className="text-sm text-red-700 mt-1">
            {error instanceof Error ? error.message : 'An error occurred'}
          </p>
        </div>
      </div>
    );
  }

  if (!goals || goals.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
          <ExclamationCircleIcon className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-1">No goals yet</h3>
        <p className="text-sm text-gray-600">
          {filter === 'today'
            ? "You don't have any goals scheduled for today."
            : 'Create your first daily goal to get started!'}
        </p>
      </div>
    );
  }

  // Separate completed and incomplete goals
  const incompleteGoals = goals.filter(g => !g.is_completed);
  const completedGoals = goals.filter(g => g.is_completed);

  return (
    <div className="space-y-6">
      {/* Incomplete Goals */}
      {incompleteGoals.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-3">
            Active Goals ({incompleteGoals.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {incompleteGoals.map(goal => (
              <GoalCard
                key={goal.id}
                goal={goal}
                onDelete={showDeleteButton ? handleDelete : undefined}
              />
            ))}
          </div>
        </div>
      )}

      {/* Completed Goals */}
      {completedGoals.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-3">
            Completed ({completedGoals.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 opacity-75">
            {completedGoals.map(goal => (
              <GoalCard
                key={goal.id}
                goal={goal}
                onDelete={showDeleteButton ? handleDelete : undefined}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default GoalList;
