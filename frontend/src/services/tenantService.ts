import axios from 'axios';
import type { Tenant } from '../types/tenant';

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

export const getTenants = async (): Promise<Tenant[]> => {
  const response = await api.get('/tenants');
  return response.data;
};

export const getTenant = async (id: string): Promise<Tenant> => {
  const response = await api.get(`/tenants/${id}`);
  return response.data;
};

export const createTenant = async (data: {
  name: string;
  slug: string;
  plan: string;
}): Promise<Tenant> => {
  const response = await api.post('/tenants', data);
  return response.data;
};

export const updateTenant = async (
  id: string,
  data: Partial<Tenant>
): Promise<Tenant> => {
  const response = await api.put(`/tenants/${id}`, data);
  return response.data;
};

export const deleteTenant = async (id: string): Promise<void> => {
  await api.delete(`/tenants/${id}`);
};
