import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface Assessment {
  id: string;
  tenant_id: string;
  title: string;
  description?: string;
  status: 'draft' | 'published' | 'archived';
  topic?: string;
  industry?: string;
  ai_generated: 'manual' | 'ai' | 'hybrid';
  scoring_logic: Record<string, unknown>;
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
  scoring_logic?: Record<string, any>;
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

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
};

export const assessmentService = {
  async list(tenantId: string, params?: { skip?: number; limit?: number; status?: string }) {
    const response = await axios.get<Assessment[]>(
      `${API_BASE_URL}/tenants/${tenantId}/assessments`,
      {
        headers: getAuthHeaders(),
        params,
      }
    );
    return response.data;
  },

  async get(tenantId: string, assessmentId: string) {
    const response = await axios.get<Assessment>(
      `${API_BASE_URL}/tenants/${tenantId}/assessments/${assessmentId}`,
      {
        headers: getAuthHeaders(),
      }
    );
    return response.data;
  },

  async create(tenantId: string, data: CreateAssessmentData) {
    const response = await axios.post<Assessment>(
      `${API_BASE_URL}/tenants/${tenantId}/assessments`,
      data,
      {
        headers: getAuthHeaders(),
      }
    );
    return response.data;
  },

  async update(tenantId: string, assessmentId: string, data: UpdateAssessmentData) {
    const response = await axios.put<Assessment>(
      `${API_BASE_URL}/tenants/${tenantId}/assessments/${assessmentId}`,
      data,
      {
        headers: getAuthHeaders(),
      }
    );
    return response.data;
  },

  async delete(tenantId: string, assessmentId: string) {
    await axios.delete(
      `${API_BASE_URL}/tenants/${tenantId}/assessments/${assessmentId}`,
      {
        headers: getAuthHeaders(),
      }
    );
  },

  async search(tenantId: string, query: string, limit = 10) {
    const response = await axios.get<Assessment[]>(
      `${API_BASE_URL}/tenants/${tenantId}/assessments/search`,
      {
        headers: getAuthHeaders(),
        params: { q: query, limit },
      }
    );
    return response.data;
  },
};
