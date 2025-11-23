/**
 * Error Log Service
 *
 * Retrieves error logs from the backend for monitoring and analytics.
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface ErrorLog {
  id: string;
  tenant_id?: string;
  user_id?: string;
  error_type: string;
  error_code?: string;
  severity: string;
  error_message: string;
  stack_trace?: string;
  endpoint?: string;
  method?: string;
  status_code?: number;
  duration_ms?: number;
  environment: string;
  ip_address?: string;
  user_agent?: string;
  correlation_id?: string;
  created_at: string;
}

export interface ErrorLogsListResponse {
  total: number;
  skip: number;
  limit: number;
  items: ErrorLog[];
}

export interface ErrorSummary {
  total_errors: number;
  errors_by_type: Record<string, number>;
  errors_by_severity: Record<string, number>;
  errors_by_environment: Record<string, number>;
  critical_errors: number;
}

export interface ErrorTrend {
  interval: string;
  data_points: Array<{
    date: string;
    count: number;
  }>;
}

export interface ErrorAnalytics {
  summary: ErrorSummary;
  trend: ErrorTrend;
  frequent_errors: Array<{
    error_type: string;
    error_message: string;
    count: number;
    last_occurrence: string;
  }>;
}

/**
 * Get error logs with filters
 */
export const getErrorLogs = async (params?: {
  error_type?: string;
  severity?: string;
  environment?: string;
  endpoint?: string;
  start_date?: string;
  end_date?: string;
  correlation_id?: string;
  skip?: number;
  limit?: number;
}): Promise<ErrorLogsListResponse> => {
  const response = await api.get('/error-logs', { params });
  return response.data;
};

/**
 * Get error summary statistics
 */
export const getErrorSummary = async (): Promise<ErrorSummary> => {
  const response = await api.get('/error-logs/summary');
  return response.data;
};

/**
 * Get error trend data
 */
export const getErrorTrend = async (params?: {
  interval?: 'hour' | 'day';
  days?: number;
}): Promise<ErrorTrend> => {
  const response = await api.get('/error-logs/trend', { params });
  return response.data;
};

/**
 * Get comprehensive error analytics
 */
export const getErrorAnalytics = async (): Promise<ErrorAnalytics> => {
  const response = await api.get('/error-logs/analytics');
  return response.data;
};

/**
 * Get errors by correlation ID
 */
export const getErrorsByCorrelation = async (
  correlationId: string
): Promise<ErrorLog[]> => {
  const response = await api.get(`/error-logs/correlation/${correlationId}`);
  return response.data;
};

/**
 * Get error details by ID
 */
export const getErrorDetails = async (errorId: string): Promise<ErrorLog> => {
  const response = await api.get(`/error-logs/${errorId}`);
  return response.data;
};
