/**
 * Analytics Service
 * 
 * API client for analytics and reporting endpoints
 */

import api from './api';

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
  async getOverview(tenantId: string): Promise<OverviewAnalytics> {
    const response = await api.get<OverviewAnalytics>(
      `/tenants/${tenantId}/analytics/overview`
    );
    return response.data;
  },

  /**
   * Get lead analytics
   */
  async getLeadAnalytics(tenantId: string): Promise<LeadAnalytics> {
    const response = await api.get<LeadAnalytics>(
      `/tenants/${tenantId}/analytics/leads`
    );
    return response.data;
  },

  /**
   * Get assessment analytics
   */
  async getAssessmentAnalytics(tenantId: string): Promise<AssessmentAnalytics> {
    const response = await api.get<AssessmentAnalytics>(
      `/tenants/${tenantId}/analytics/assessments`
    );
    return response.data;
  },

  /**
   * Get trend data
   */
  async getTrends(
    tenantId: string,
    period: '7d' | '30d' | '90d' = '30d',
    metric: 'leads' | 'assessments' = 'leads'
  ): Promise<TrendData> {
    const response = await api.get<TrendData>(
      `/tenants/${tenantId}/analytics/trends`,
      { params: { period, metric } }
    );
    return response.data;
  },
};

export default analyticsService;
