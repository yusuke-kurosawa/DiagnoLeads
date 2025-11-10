/**
 * MetricCard Component
 * 
 * Displays a single metric with label and optional comparison
 */

import React from 'react';

interface MetricCardProps {
  label: string;
  value: number | string;
  unit?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  className?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  unit = '',
  trend,
  trendValue,
  className = '',
}) => {
  const getTrendColor = () => {
    if (!trend) return '';
    switch (trend) {
      case 'up':
        return 'text-green-600';
      case 'down':
        return 'text-red-600';
      case 'neutral':
        return 'text-gray-600';
      default:
        return '';
    }
  };

  const getTrendIcon = () => {
    if (!trend) return null;
    switch (trend) {
      case 'up':
        return '↑';
      case 'down':
        return '↓';
      case 'neutral':
        return '→';
      default:
        return null;
    }
  };

  return (
    <div
      className={`bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow ${className}`}
    >
      <div className="text-sm font-medium text-gray-600 mb-2">{label}</div>
      <div className="flex items-end justify-between">
        <div className="text-3xl font-bold text-gray-900">
          {value}
          {unit && <span className="text-xl text-gray-600 ml-1">{unit}</span>}
        </div>
        {trend && trendValue && (
          <div className={`flex items-center text-sm font-medium ${getTrendColor()}`}>
            <span className="mr-1">{getTrendIcon()}</span>
            <span>{trendValue}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default MetricCard;
