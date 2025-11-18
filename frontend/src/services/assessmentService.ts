import api from './api';

export interface AssessmentQuestion {
  id: string;
  order: number;
  text: string;
  type: 'single_choice' | 'multiple_choice' | 'text' | 'slider';
  required: boolean;
  options?: Array<{
    id: string;
    text: string;
    score: number;
  }>;
  max_score?: number;
}

export interface Assessment {
  id: string;
  tenant_id: string;
  title: string;
  description?: string;
  status: 'draft' | 'published' | 'archived' | 'unpublished';
  topic?: string;
  industry?: string;
  ai_generated: 'manual' | 'ai' | 'hybrid';
  scoring_logic: Record<string, unknown>;
  questions?: AssessmentQuestion[];
  qr_code_url?: string;
  created_by: string;
  updated_by?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateAssessmentData {
  title: string;
  description?: string;
  status?: string;
  topic?: string;
  industry?: string;
  ai_generated?: string;
  scoring_logic?: Record<string, unknown>;
}

export interface UpdateAssessmentData {
  title?: string;
  description?: string;
  status?: string;
  topic?: string;
  industry?: string;
  ai_generated?: string;
  scoring_logic?: Record<string, unknown>;
}



export const assessmentService = {
  async list(tenantId: string, params?: { skip?: number; limit?: number; status?: string }) {
    const response = await api.get<Assessment[]>(
      `/tenants/${tenantId}/assessments`,
      { params }
    );
    return response.data;
  },

  async get(tenantId: string, assessmentId: string) {
    const response = await api.get<Assessment>(
      `/tenants/${tenantId}/assessments/${assessmentId}`
    );
    return response.data;
  },

  async create(tenantId: string, data: CreateAssessmentData) {
    const response = await api.post<Assessment>(
      `/tenants/${tenantId}/assessments`,
      data
    );
    return response.data;
  },

  async update(tenantId: string, assessmentId: string, data: UpdateAssessmentData) {
    const response = await api.put<Assessment>(
      `/tenants/${tenantId}/assessments/${assessmentId}`,
      data
    );
    return response.data;
  },

  async delete(tenantId: string, assessmentId: string) {
    await api.delete(`/tenants/${tenantId}/assessments/${assessmentId}`);
  },

  async search(tenantId: string, query: string, limit = 10) {
    const response = await api.get<Assessment[]>(
      `/tenants/${tenantId}/assessments/search`,
      { params: { q: query, limit } }
    );
    return response.data;
  },

  async publish(tenantId: string, assessmentId: string) {
    const response = await api.post<Assessment>(
      `/tenants/${tenantId}/assessments/${assessmentId}/publish`,
      {}
    );
    return response.data;
  },

  async unpublish(tenantId: string, assessmentId: string) {
    const response = await api.post<Assessment>(
      `/tenants/${tenantId}/assessments/${assessmentId}/unpublish`,
      {}
    );
    return response.data;
  },
};
