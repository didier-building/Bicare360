import React from 'react';
import type { VitalAlerts } from '../../api/vitals';
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';

interface VitalAlertsPanelProps {
  alerts?: VitalAlerts;
}

const getAlertSeverity = (reason: string): 'critical' | 'warning' | 'info' => {
  if (reason.includes('High') || reason.includes('Low')) {
    return 'warning';
  }
  if (reason.includes('fever') || reason.includes('saturation')) {
    return 'critical';
  }
  return 'info';
};

const getAlertColor = (severity: 'critical' | 'warning' | 'info'): string => {
  switch (severity) {
    case 'critical':
      return 'bg-red-50 border-red-200';
    case 'warning':
      return 'bg-yellow-50 border-yellow-200';
    case 'info':
      return 'bg-blue-50 border-blue-200';
  }
};

const getAlertBadgeColor = (severity: 'critical' | 'warning' | 'info'): string => {
  switch (severity) {
    case 'critical':
      return 'bg-red-100 text-red-800';
    case 'warning':
      return 'bg-yellow-100 text-yellow-800';
    case 'info':
      return 'bg-blue-100 text-blue-800';
  }
};

const VitalAlertsPanel: React.FC<VitalAlertsPanelProps> = ({ alerts }) => {
  if (!alerts || alerts.abnormal_readings.length === 0) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-8 text-center">
        <ExclamationTriangleIcon className="w-12 h-12 text-green-300 mx-auto mb-4" />
        <p className="text-green-800 font-semibold">All vital readings are normal</p>
        <p className="text-green-700 text-sm mt-1">No alerts detected</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">
          Abnormal Readings
        </h3>
        <span className="bg-red-100 text-red-800 text-sm font-semibold px-3 py-1 rounded-full">
          {alerts.total_abnormal} Alert{alerts.total_abnormal !== 1 ? 's' : ''}
        </span>
      </div>

      <div className="space-y-3">
        {alerts.abnormal_readings.map((reading, index) => {
          const severity = getAlertSeverity(reading.alert_reason);
          return (
            <div
              key={`${reading.id}-${index}`}
              className={`p-4 rounded-lg border-2 ${getAlertColor(severity)}`}
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                  <ExclamationTriangleIcon className="w-6 h-6 text-red-600" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h4 className="font-semibold text-gray-900">
                      {getVitalTypeLabel(reading.reading_type)}
                    </h4>
                    <span className={`text-xs font-semibold px-2 py-1 rounded-full ${getAlertBadgeColor(severity)}`}>
                      {reading.alert_reason}
                    </span>
                  </div>

                  <p className="text-sm text-gray-600 mb-2">
                    Reading: <span className="font-semibold text-gray-900">{reading.value}</span>
                    {reading.secondary_value && (
                      <span className="ml-2">
                        / <span className="font-semibold text-gray-900">{reading.secondary_value}</span>
                      </span>
                    )}
                    {' '}<span className="text-gray-500">{reading.unit}</span>
                  </p>

                  <p className="text-xs text-gray-500">
                    {new Date(reading.recorded_at).toLocaleDateString()} at {' '}
                    {new Date(reading.recorded_at).toLocaleTimeString([], { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </p>

                  {reading.notes && (
                    <p className="text-sm text-gray-700 mt-2 pt-2 border-t border-current/20">
                      {reading.notes}
                    </p>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
        <p className="text-sm text-blue-800">
          <span className="font-semibold">Note:</span> These alerts indicate readings outside normal ranges. 
          Please consult with a healthcare provider if you have concerns.
        </p>
      </div>
    </div>
  );
};

const getVitalTypeLabel = (vitalType: string): string => {
  const labels: Record<string, string> = {
    blood_pressure: 'Blood Pressure',
    heart_rate: 'Heart Rate',
    temperature: 'Temperature',
    weight: 'Weight',
    oxygen_saturation: 'O2 Saturation',
    respiratory_rate: 'Respiratory Rate',
    blood_glucose: 'Blood Glucose',
  };
  return labels[vitalType] || vitalType;
};

export default VitalAlertsPanel;
