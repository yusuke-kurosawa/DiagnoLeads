/**
 * TrendLineChart Component
 * 
 * Line chart for displaying trend data over time
 */

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { format, parseISO } from 'date-fns';
import { ja } from 'date-fns/locale';

interface TrendLineChartProps {
  data: Array<{ date: string; value: number }>;
  title?: string;
  color?: string;
  yAxisLabel?: string;
}

const TrendLineChart: React.FC<TrendLineChartProps> = ({
  data,
  title,
  color = '#3b82f6',
  yAxisLabel = '件数',
}) => {
  // Format data for chart
  const formattedData = data.map((item) => ({
    ...item,
    dateFormatted: format(parseISO(item.date), 'M/d', { locale: ja }),
  }));

  if (data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        {title && <h3 className="text-lg font-semibold mb-4">{title}</h3>}
        <div className="flex items-center justify-center h-64 text-gray-500">
          データがありません
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      {title && <h3 className="text-lg font-semibold mb-4">{title}</h3>}
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="dateFormatted"
            tick={{ fontSize: 12 }}
            interval="preserveStartEnd"
          />
          <YAxis label={{ value: yAxisLabel, angle: -90, position: 'insideLeft' }} />
          <Tooltip
            labelFormatter={(value) => `日付: ${value}`}
            formatter={(value: number) => [`${value} ${yAxisLabel}`, '']}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="value"
            stroke={color}
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
            name={yAxisLabel}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TrendLineChart;
