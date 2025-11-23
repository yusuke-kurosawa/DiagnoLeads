/**
 * AI Usage Service
 *
 * Retrieves AI usage logs and statistics for billing and cost analysis.
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

export interface AIUsageLog {
  id: string;
  tenant_id: string;
  user_id?: string;
  operation: string;
  model: string;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  cost_usd: number;
  assessment_id?: string;
  lead_id?: string;
  duration_ms?: number;
  success: string;
  created_at: string;
}

export interface AIUsageSummary {
  total_requests: number;
  total_tokens: number;
  total_cost_usd: number;
  operations: Record<string, {
    count: number;
    tokens: number;
    cost_usd: number;
  }>;
  success_rate: number;
}

export interface AIUsageTrend {
  data_points: Array<{
    date: string;
    requests: number;
    tokens: number;
    cost_usd: number;
  }>;
}

/**
 * Get AI usage logs for a tenant (Note: API endpoint TBD)
 */
export const getAIUsageLogs = async (
  tenantId: string,
  params?: {
    operation?: string;
    start_date?: string;
    end_date?: string;
    skip?: number;
    limit?: number;
  }
): Promise<{
  total: number;
  skip: number;
  limit: number;
  items: AIUsageLog[];
}> => {
  const response = await api.get(`/tenants/${tenantId}/ai-usage`, { params });
  return response.data;
};

/**
 * Get AI usage summary for a tenant (Note: API endpoint TBD)
 */
export const getAIUsageSummary = async (
  tenantId: string,
  params?: {
    start_date?: string;
    end_date?: string;
  }
): Promise<AIUsageSummary> => {
  const response = await api.get(`/tenants/${tenantId}/ai-usage/summary`, { params });
  return response.data;
};

/**
 * Get AI usage trend data (Note: API endpoint TBD)
 */
export const getAIUsageTrend = async (
  tenantId: string,
  params?: {
    interval?: 'day' | 'week' | 'month';
    days?: number;
  }
): Promise<AIUsageTrend> => {
  const response = await api.get(`/tenants/${tenantId}/ai-usage/trend`, { params });
  return response.data;
};
