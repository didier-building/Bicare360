import React, { useState } from 'react';
import type { HealthGoal } from '../../api/vitals';
import { CheckCircleIcon } from '@heroicons/react/24/outline';
import vitalsAPI from '../../api/vitals';
import { useMutation, useQueryClient } from '@tanstack/react-query';

interface HealthGoalsPanelProps {
  goals: HealthGoal[];
  patientId: number;
}

const getStatusColor = (status: string): string => {
  switch (status) {
    case 'active':
      return 'bg-blue-50 border-blue-200 text-blue-800';
    case 'achieved':
      return 'bg-green-50 border-green-200 text-green-800';
    case 'abandoned':
      return 'bg-red-50 border-red-200 text-red-800';
    default:
      return 'bg-gray-50 border-gray-200 text-gray-800';
  }
};

const getStatusBadgeColor = (status: string): string => {
  switch (status) {
    case 'active':
      return 'bg-blue-100 text-blue-800';
    case 'achieved':
      return 'bg-green-100 text-green-800';
    case 'abandoned':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const HealthGoalsPanel: React.FC<HealthGoalsPanelProps> = ({ goals, patientId }) => {
  const queryClient = useQueryClient();
  const [editingId, setEditingId] = useState<number | null>(null);

  const updateGoalMutation = useMutation({
    mutationFn: (data: { goalId: number; status: string }) =>
      vitalsAPI.updateGoal(patientId, data.goalId, { status: data.status as any }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['health-goals'] });
      setEditingId(null);
    },
  });

  const handleStatusChange = (goalId: number, newStatus: string) => {
    updateGoalMutation.mutate({ goalId, status: newStatus });
  };

  const activeGoals = goals.filter(g => g.status === 'active');
  const achievedGoals = goals.filter(g => g.status === 'achieved');
  const abandonedGoals = goals.filter(g => g.status === 'abandoned');

  return (
    <div className="space-y-6">
      {/* Active Goals */}
      {activeGoals.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-blue-900">Active Goals ({activeGoals.length})</h3>
          <div className="space-y-2">
            {activeGoals.map(goal => (
              <GoalCard
                key={goal.id}
                goal={goal}
                onStatusChange={handleStatusChange}
                isEditing={editingId === goal.id}
                setEditing={setEditingId}
              />
            ))}
          </div>
        </div>
      )}

      {/* Achieved Goals */}
      {achievedGoals.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-green-900">Achieved Goals ({achievedGoals.length})</h3>
          <div className="space-y-2">
            {achievedGoals.map(goal => (
              <GoalCard
                key={goal.id}
                goal={goal}
                onStatusChange={handleStatusChange}
                isEditing={editingId === goal.id}
                setEditing={setEditingId}
              />
            ))}
          </div>
        </div>
      )}

      {/* Abandoned Goals */}
      {abandonedGoals.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-red-900">Abandoned Goals ({abandonedGoals.length})</h3>
          <div className="space-y-2">
            {abandonedGoals.map(goal => (
              <GoalCard
                key={goal.id}
                goal={goal}
                onStatusChange={handleStatusChange}
                isEditing={editingId === goal.id}
                setEditing={setEditingId}
              />
            ))}
          </div>
        </div>
      )}

      {goals.length === 0 && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
          <CheckCircleIcon className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">No health goals set yet</p>
        </div>
      )}
    </div>
  );
};

interface GoalCardProps {
  goal: HealthGoal;
  onStatusChange: (goalId: number, status: string) => void;
  isEditing: boolean;
  setEditing: (id: number | null) => void;
}

const GoalCard: React.FC<GoalCardProps> = ({ goal, onStatusChange, isEditing, setEditing }) => {
  const daysRemaining = goal.target_date
    ? Math.ceil(
        (new Date(goal.target_date).getTime() - new Date().getTime()) /
        (1000 * 60 * 60 * 24)
      )
    : null;

  return (
    <div className={`p-4 rounded-lg border-2 ${getStatusColor(goal.status)}`}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h4 className="font-semibold text-gray-900">{goal.goal_name}</h4>
            <span className={`text-xs font-semibold px-2 py-1 rounded-full ${getStatusBadgeColor(goal.status)}`}>
              {goal.status.charAt(0).toUpperCase() + goal.status.slice(1)}
            </span>
          </div>

          <p className="text-sm text-gray-600 mb-3">
            {goal.vital_type} • Target: {goal.target_value} {goal.unit}
          </p>

          {daysRemaining !== null && goal.status === 'active' && (
            <p className={`text-sm font-medium ${daysRemaining > 0 ? 'text-blue-600' : 'text-red-600'}`}>
              {daysRemaining > 0
                ? `${daysRemaining} days remaining`
                : 'Target date passed'}
            </p>
          )}

          {goal.notes && (
            <p className="text-sm text-gray-700 mt-2 pt-2 border-t border-current/20">
              {goal.notes}
            </p>
          )}
        </div>

        {isEditing ? (
          <div className="flex gap-2 pt-2">
            <select
              value={goal.status}
              onChange={(e) => onStatusChange(goal.id, e.target.value)}
              className="px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500"
            >
              <option value="active">Active</option>
              <option value="achieved">Achieved</option>
              <option value="abandoned">Abandoned</option>
            </select>
            <button
              onClick={() => setEditing(null)}
              className="px-2 py-1 text-sm bg-gray-500 text-white rounded hover:bg-gray-600"
            >
              Close
            </button>
          </div>
        ) : (
          goal.status === 'active' && (
            <button
              onClick={() => setEditing(goal.id)}
              className="px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700"
            >
              Update Status
            </button>
          )
        )}
      </div>
    </div>
  );
};

export default HealthGoalsPanel;
