import React from 'react';
import type { VitalSummary, VitalReading } from '../../api/vitals';
import { HeartIcon } from '@heroicons/react/24/outline';

interface HealthSummaryCardProps {
  vitals?: VitalSummary;
}

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

const getColorForVitalType = (vitalType: string): string => {
  const colors: Record<string, string> = {
    blood_pressure: '#ef4444',
    heart_rate: '#f97316',
    temperature: '#f59e0b',
    weight: '#8b5cf6',
    oxygen_saturation: '#06b6d4',
    respiratory_rate: '#6366f1',
    blood_glucose: '#ec4899',
  };
  return colors[vitalType] || '#3b82f6';
};

const getVitalUnit = (vitalType: string): string => {
  const units: Record<string, string> = {
    blood_pressure: 'mmHg',
    heart_rate: 'bpm',
    temperature: '°C',
    weight: 'kg',
    oxygen_saturation: '%',
    respiratory_rate: 'breaths/min',
    blood_glucose: 'mg/dL',
  };
  return units[vitalType] || '';
};

const HealthSummaryCard: React.FC<HealthSummaryCardProps> = ({ vitals = {} }) => {
  const vitalEntries = Object.entries(vitals) as [string, VitalReading][];

  if (vitalEntries.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
        <HeartIcon className="w-12 h-12 text-gray-300 mx-auto mb-4" />
        <p className="text-gray-500">No vital readings recorded yet</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Latest Vital Readings</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {vitalEntries.map(([_key, vital]) => (
          <div
            key={vital.id}
            className="p-4 rounded-lg border-2 transition-all hover:shadow-md"
            style={{
              borderColor: getColorForVitalType(vital.reading_type),
              backgroundColor: `${getColorForVitalType(vital.reading_type)}10`,
            }}
          >
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-semibold text-gray-900">
                {getVitalTypeLabel(vital.reading_type)}
              </h4>
              <span
                className="text-xs font-semibold px-2.5 py-1 rounded-full text-white"
                style={{ backgroundColor: getColorForVitalType(vital.reading_type) }}
              >
                {getVitalUnit(vital.reading_type)}
              </span>
            </div>

            <div className="space-y-2">
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-gray-900">
                  {vital.value.toFixed(1)}
                </span>
                {vital.secondary_value !== null && vital.secondary_value !== undefined && (
                  <span className="text-lg text-gray-600">
                    / {vital.secondary_value.toFixed(1)}
                  </span>
                )}
              </div>

              <p className="text-xs text-gray-500">
                {new Date(vital.recorded_at).toLocaleDateString()} at {' '}
                {new Date(vital.recorded_at).toLocaleTimeString([], { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })}
              </p>

              {vital.notes && (
                <p className="text-sm text-gray-700 pt-2 border-t border-gray-200">
                  {vital.notes}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default HealthSummaryCard;
