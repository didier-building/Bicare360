import React, { useState } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import type { Alert } from '../api/nursing';
import { nursingAPI } from '../api/nursing';
import toast from 'react-hot-toast';
import { formatDistanceToNow, format } from 'date-fns';

interface AlertDetailModalProps {
  alert: Alert;
  isOpen: boolean;
  onClose: () => void;
  onUpdate: () => void;
}

const AlertDetailModal: React.FC<AlertDetailModalProps> = ({ alert, isOpen, onClose, onUpdate }) => {
  const [notes, setNotes] = useState(alert.resolution_notes || '');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-300';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low': return 'bg-green-100 text-green-800 border-green-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'new': return 'bg-blue-100 text-blue-800';
      case 'assigned': return 'bg-purple-100 text-purple-800';
      case 'in_progress': return 'bg-yellow-100 text-yellow-800';
      case 'resolved': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleAcknowledge = async () => {
    setIsSubmitting(true);
    try {
      await nursingAPI.acknowledgeAlert(alert.id);
      toast.success('Alert acknowledged');
      onUpdate();
      onClose();
    } catch (err) {
      console.error('Failed to acknowledge:', err);
      toast.error('Failed to acknowledge alert');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAssignToSelf = async () => {
    setIsSubmitting(true);
    try {
      await nursingAPI.assignAlertToSelf(alert.id);
      toast.success('Alert assigned to you');
      onUpdate();
      onClose();
    } catch (err) {
      console.error('Failed to assign:', err);
      toast.error('Failed to assign alert');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSaveNotes = async () => {
    setIsSubmitting(true);
    try {
      await nursingAPI.addNotes(alert.id, notes);
      toast.success('Notes saved');
      onUpdate();
    } catch (err) {
      console.error('Failed to save notes:', err);
      toast.error('Failed to save notes');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResolve = async () => {
    setIsSubmitting(true);
    try {
      await nursingAPI.resolveAlert(alert.id, notes);
      toast.success('Alert resolved');
      onUpdate();
      onClose();
    } catch (err) {
      console.error('Failed to resolve:', err);
      toast.error('Failed to resolve alert');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity" 
        onClick={onClose}
      ></div>

      {/* Modal Container */}
      <div className="fixed inset-0 z-50 overflow-y-auto">
        <div className="flex min-h-full items-center justify-center p-4">
          <div className="relative bg-white rounded-lg shadow-xl w-full max-w-2xl" onClick={(e) => e.stopPropagation()}>
            {/* Header */}
            <div className="bg-gray-50 px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">
                Alert Details
              </h3>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

          {/* Content */}
          <div className="px-6 py-4 space-y-6">
            {/* Status badges */}
            <div className="flex items-center gap-3">
              <div className={`px-3 py-1 rounded-full text-xs font-semibold border ${getSeverityColor(alert.severity)}`}>
                {alert.severity.toUpperCase()}
              </div>
              <div className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(alert.status)}`}>
                {alert.status.replace('_', ' ').toUpperCase()}
              </div>
            </div>

            {/* Alert Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Alert Type</label>
              <p className="text-lg font-semibold text-gray-900">{alert.title || alert.alert_type}</p>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <p className="text-gray-900">{alert.description}</p>
            </div>

            {/* Patient Info */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-blue-900 mb-2">Patient Information</h4>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="text-blue-700 font-medium">Name:</span>
                  <p className="text-blue-900">{alert.patient.first_name} {alert.patient.last_name}</p>
                </div>
                <div>
                  <span className="text-blue-700 font-medium">MRN:</span>
                  <p className="text-blue-900">{alert.patient.medical_record_number}</p>
                </div>
              </div>
            </div>

            {/* Timeline */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Timeline</label>
              <div className="space-y-2 text-sm text-gray-600">
                <div className="flex items-center gap-2">
                  <span className="w-24 font-medium">Created:</span>
                  <span>{format(new Date(alert.created_at), 'PPp')} ({formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })})</span>
                </div>
                {alert.acknowledged_at && (
                  <div className="flex items-center gap-2">
                    <span className="w-24 font-medium">Acknowledged:</span>
                    <span>{format(new Date(alert.acknowledged_at), 'PPp')} ({formatDistanceToNow(new Date(alert.acknowledged_at), { addSuffix: true })})</span>
                  </div>
                )}
                {alert.resolved_at && (
                  <div className="flex items-center gap-2">
                    <span className="w-24 font-medium">Resolved:</span>
                    <span>{format(new Date(alert.resolved_at), 'PPp')} ({formatDistanceToNow(new Date(alert.resolved_at), { addSuffix: true })})</span>
                  </div>
                )}
              </div>
            </div>

            {/* Assigned Nurse */}
            {alert.assigned_nurse && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Assigned Nurse</label>
                <p className="text-gray-900">
                  {alert.assigned_nurse.user.first_name} {alert.assigned_nurse.user.last_name}
                </p>
              </div>
            )}

            {/* Notes */}
            {alert.status !== 'resolved' && (
              <div>
                <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-2">
                  Notes
                </label>
                <textarea
                  id="notes"
                  rows={4}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Add notes about this alert..."
                  disabled={isSubmitting}
                />
                {notes !== alert.resolution_notes && (
                  <button
                    onClick={handleSaveNotes}
                    disabled={isSubmitting}
                    className="mt-2 px-4 py-2 bg-gray-600 text-white rounded-lg text-sm font-medium hover:bg-gray-700 disabled:bg-gray-400 transition-colors"
                  >
                    {isSubmitting ? 'Saving...' : 'Save Notes'}
                  </button>
                )}
              </div>
            )}

            {alert.status === 'resolved' && alert.resolution_notes && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Resolution Notes</label>
                <p className="text-gray-900 bg-gray-50 p-3 rounded-lg">{alert.resolution_notes}</p>
              </div>
            )}
          </div>

          {/* Footer Actions */}
          <div className="bg-gray-50 px-6 py-4 border-t border-gray-200 flex flex-wrap gap-3 justify-end">
            {alert.status === 'new' && (
              <>
                <button
                  onClick={handleAcknowledge}
                  disabled={isSubmitting}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm font-medium hover:bg-blue-600 disabled:bg-gray-400 transition-colors"
                >
                  {isSubmitting ? 'Processing...' : 'Acknowledge'}
                </button>
                {!alert.assigned_nurse && (
                  <button
                    onClick={handleAssignToSelf}
                    disabled={isSubmitting}
                    className="px-4 py-2 bg-purple-500 text-white rounded-lg text-sm font-medium hover:bg-purple-600 disabled:bg-gray-400 transition-colors"
                  >
                    {isSubmitting ? 'Processing...' : 'Assign to Me'}
                  </button>
                )}
              </>
            )}
            {(alert.status === 'assigned' || alert.status === 'in_progress') && (
              <button
                onClick={handleResolve}
                disabled={isSubmitting}
                className="px-4 py-2 bg-green-500 text-white rounded-lg text-sm font-medium hover:bg-green-600 disabled:bg-gray-400 transition-colors"
              >
                {isSubmitting ? 'Processing...' : 'Mark as Resolved'}
              </button>
            )}
            <button
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg text-sm font-medium hover:bg-gray-300 disabled:bg-gray-100 transition-colors"
            >
              Close
            </button>
          </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AlertDetailModal;
