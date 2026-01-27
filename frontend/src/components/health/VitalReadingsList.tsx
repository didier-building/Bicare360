import React, { useState } from 'react';
import type { VitalReading } from '../../api/vitals';
import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';

interface VitalReadingsListProps {
  vitals: VitalReading[];
  patientId: number;
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
    blood_pressure: 'text-red-600',
    heart_rate: 'text-orange-600',
    temperature: 'text-amber-600',
    weight: 'text-purple-600',
    oxygen_saturation: 'text-cyan-600',
    respiratory_rate: 'text-indigo-600',
    blood_glucose: 'text-pink-600',
  };
  return colors[vitalType] || 'text-blue-600';
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

const VitalReadingsList: React.FC<VitalReadingsListProps> = ({ vitals }) => {
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [sortField, setSortField] = useState<'date' | 'type'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const sortedVitals = [...vitals].sort((a, b) => {
    let compareValue = 0;

    if (sortField === 'date') {
      compareValue = new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime();
    } else if (sortField === 'type') {
      compareValue = a.reading_type.localeCompare(b.reading_type);
    }

    return sortOrder === 'asc' ? compareValue : -compareValue;
  });

  if (vitals.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
        <p className="text-gray-500">No vital readings recorded yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
          <select
            value={sortField}
            onChange={(e) => setSortField(e.target.value as 'date' | 'type')}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
          >
            <option value="date">Date</option>
            <option value="type">Vital Type</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Order</label>
          <button
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white hover:bg-gray-50"
          >
            {sortOrder === 'desc' ? 'Newest First' : 'Oldest First'}
          </button>
        </div>
        <div className="flex-1 text-right text-sm text-gray-600">
          {vitals.length} readings
        </div>
      </div>

      {/* List */}
      <div className="space-y-2">
        {sortedVitals.map(vital => (
          <div
            key={vital.id}
            className="bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
          >
            <button
              onClick={() => setExpandedId(expandedId === vital.id ? null : vital.id)}
              className="w-full p-4 flex items-center justify-between text-left"
            >
              <div className="flex-1 flex items-center gap-4">
                <div>
                  <h4 className={`font-semibold ${getColorForVitalType(vital.reading_type)}`}>
                    {getVitalTypeLabel(vital.reading_type)}
                  </h4>
                  <p className="text-sm text-gray-500 mt-1">
                    {new Date(vital.recorded_at).toLocaleDateString()} at {' '}
                    {new Date(vital.recorded_at).toLocaleTimeString([], { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-6">
                <div className="text-right">
                  <p className="text-2xl font-bold text-gray-900">
                    {vital.value.toFixed(1)}
                  </p>
                  {vital.secondary_value !== null && vital.secondary_value !== undefined && (
                    <p className="text-sm text-gray-600">
                      / {vital.secondary_value.toFixed(1)}
                    </p>
                  )}
                  <p className="text-xs text-gray-500 mt-1">{getVitalUnit(vital.reading_type)}</p>
                </div>

                {expandedId === vital.id ? (
                  <ChevronUpIcon className="w-5 h-5 text-gray-400" />
                ) : (
                  <ChevronDownIcon className="w-5 h-5 text-gray-400" />
                )}
              </div>
            </button>

            {/* Expanded Details */}
            {expandedId === vital.id && (
              <div className="border-t border-gray-200 p-4 bg-gray-50">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Reading Type</p>
                    <p className="font-semibold text-gray-900">
                      {getVitalTypeLabel(vital.reading_type)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Value</p>
                    <p className="font-semibold text-gray-900">
                      {vital.value.toFixed(1)} {getVitalUnit(vital.reading_type)}
                    </p>
                  </div>
                  {vital.secondary_value !== null && vital.secondary_value !== undefined && (
                    <div>
                      <p className="text-sm text-gray-600">Secondary Value</p>
                      <p className="font-semibold text-gray-900">
                        {vital.secondary_value.toFixed(1)}
                      </p>
                    </div>
                  )}
                  <div>
                    <p className="text-sm text-gray-600">Recorded At</p>
                    <p className="font-semibold text-gray-900">
                      {new Date(vital.recorded_at).toLocaleString()}
                    </p>
                  </div>
                  {vital.notes && (
                    <div className="md:col-span-2">
                      <p className="text-sm text-gray-600 mb-1">Notes</p>
                      <p className="font-semibold text-gray-900 bg-white p-2 rounded border border-gray-200">
                        {vital.notes}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default VitalReadingsList;
