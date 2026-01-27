import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';
import type { VitalTrend } from '../../api/vitals';

interface VitalTrendsChartProps {
  vitalType: string;
  vitalTrends?: VitalTrend;
}

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

const VitalTrendsChart: React.FC<VitalTrendsChartProps> = ({ vitalType, vitalTrends }) => {
  if (!vitalTrends || !vitalTrends.readings || vitalTrends.readings.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
        <p className="text-gray-500">No data available for {getVitalTypeLabel(vitalType)}</p>
      </div>
    );
  }

  // Prepare chart data
  const chartData = vitalTrends.readings
    .sort((a, b) => new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime())
    .map(reading => ({
      date: new Date(reading.recorded_at).toLocaleDateString(),
      value: reading.value,
      secondary_value: reading.secondary_value,
      recorded_at: reading.recorded_at,
    }));

  const color = getColorForVitalType(vitalType);
  const isBP = vitalType === 'blood_pressure';

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        {getVitalTypeLabel(vitalType)} Trend
      </h3>
      <ResponsiveContainer width="100%" height={400}>
        {isBP ? (
          <LineChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="date" 
              angle={-45}
              textAnchor="end"
              height={80}
              tick={{ fontSize: 12 }}
            />
            <YAxis />
            <Tooltip 
              formatter={(value: unknown) => {
                if (typeof value === 'number') {
                  return value.toFixed(1);
                }
                return String(value);
              }}
              labelFormatter={(label) => `Date: ${label}`}
              contentStyle={{ backgroundColor: '#f3f4f6', border: '1px solid #d1d5db' }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke={color} 
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              name="Systolic"
              strokeWidth={2}
            />
            <Line 
              type="monotone" 
              dataKey="secondary_value" 
              stroke="#94a3b8" 
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              name="Diastolic"
              strokeWidth={2}
            />
          </LineChart>
        ) : (
          <AreaChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id={`gradient-${vitalType}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                <stop offset="95%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="date" 
              angle={-45}
              textAnchor="end"
              height={80}
              tick={{ fontSize: 12 }}
            />
            <YAxis />
            <Tooltip 
              formatter={(value: unknown) => {
                if (typeof value === 'number') {
                  return value.toFixed(1);
                }
                return String(value);
              }}
              labelFormatter={(label) => `Date: ${label}`}
              contentStyle={{ backgroundColor: '#f3f4f6', border: '1px solid #d1d5db' }}
            />
            <Area 
              type="monotone" 
              dataKey="value" 
              stroke={color}
              fillOpacity={1}
              fill={`url(#gradient-${vitalType})`}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          </AreaChart>
        )}
      </ResponsiveContainer>
    </div>
  );
};

export default VitalTrendsChart;
