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

export interface AuditLog {
  id: string;
  tenant_id: string;
  user_id: string;
  entity_type: string;
  entity_id: string;
  action: string;
  entity_name?: string;
  old_values?: Record<string, any>;
  new_values?: Record<string, any>;
  reason?: string;
  ip_address?: string;
  user_agent?: string;
  created_at: string;
}

export interface AuditLogsListResponse {
  total: number;
  skip: number;
  limit: number;
  items: AuditLog[];
}

export const getAuditLogs = async (
  tenantId: string,
  params?: {
    entity_type?: string;
    entity_id?: string;
    action?: string;
    skip?: number;
    limit?: number;
  }
): Promise<AuditLogsListResponse> => {
  const response = await api.get('/audit-logs', {
    params: {
      tenant_id: tenantId,
      ...params,
    },
  });
  return response.data;
};

export const getEntityHistory = async (
  tenantId: string,
  entityType: string,
  entityId: string
): Promise<AuditLog[]> => {
  const response = await api.get(`/audit-logs/entity/${entityType}/${entityId}`, {
    params: {
      tenant_id: tenantId,
    },
  });
  return response.data;
};

export const getUserActivity = async (
  tenantId: string,
  userId: string,
  days?: number
): Promise<AuditLog[]> => {
  const response = await api.get(`/audit-logs/user/${userId}`, {
    params: {
      tenant_id: tenantId,
      days: days || 30,
    },
  });
  return response.data;
};
