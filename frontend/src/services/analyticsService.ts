/**
 * Analytics Service
 * 
 * API client for analytics and reporting endpoints
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

/**
 * Get authentication token from localStorage
 */
const getAuthToken = (): string | null => {
  return localStorage.getItem('token');
};

/**
 * Build headers with authentication
 */
const getHeaders = (): HeadersInit => {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  };
};

export interface OverviewAnalytics {
  tenant_id: string;
  period: string;
  leads: LeadAnalytics;
  assessments: AssessmentAnalytics;
  generated_at: string;
}

export interface LeadAnalytics {
  total: number;
  new: number;
  contacted: number;
  qualified: number;
  converted: number;
  disqualified: number;
  hot_leads: number;
  warm_leads: number;
  cold_leads: number;
  average_score: number;
  conversion_rate: number;
}

export interface AssessmentAnalytics {
  total: number;
  published: number;
  draft: number;
  archived: number;
  ai_generated: number;
  manual_created: number;
  hybrid: number;
}

export interface TrendDataPoint {
  date: string;
  value: number;
}

export interface TrendData {
  period: string;
  metric: string;
  data_points: TrendDataPoint[];
  summary: {
    total: number;
    average_per_day: number;
  };
}

const analyticsService = {
  /**
   * Get overview analytics
   */
  getOverview: async (tenantId: string): Promise<OverviewAnalytics> => {
    const response = await fetch(
      `${API_BASE}/tenants/${tenantId}/analytics/overview`,
      {
        method: 'GET',
        headers: getHeaders(),
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch overview analytics: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Get lead analytics
   */
  getLeadAnalytics: async (tenantId: string): Promise<LeadAnalytics> => {
    const response = await fetch(
      `${API_BASE}/tenants/${tenantId}/analytics/leads`,
      {
        method: 'GET',
        headers: getHeaders(),
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch lead analytics: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Get assessment analytics
   */
  getAssessmentAnalytics: async (tenantId: string): Promise<AssessmentAnalytics> => {
    const response = await fetch(
      `${API_BASE}/tenants/${tenantId}/analytics/assessments`,
      {
        method: 'GET',
        headers: getHeaders(),
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch assessment analytics: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Get trend data
   */
  getTrends: async (
    tenantId: string,
    period: '7d' | '30d' | '90d' = '30d',
    metric: 'leads' | 'assessments' = 'leads'
  ): Promise<TrendData> => {
    const url = new URL(`${API_BASE}/tenants/${tenantId}/analytics/trends`);
    url.searchParams.append('period', period);
    url.searchParams.append('metric', metric);

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch trends: ${response.statusText}`);
    }

    return response.json();
  },
};

export default analyticsService;
