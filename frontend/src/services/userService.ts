import axios from 'axios';
import type { UserAdmin } from '../types/user';

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

export const getUsers = async (tenantId?: string): Promise<UserAdmin[]> => {
  const params = tenantId ? { tenant_id: tenantId } : {};
  const response = await api.get('/users', { params });
  return response.data;
};

export const getUser = async (id: string): Promise<UserAdmin> => {
  const response = await api.get(`/users/${id}`);
  return response.data;
};

export const createUser = async (data: {
  tenant_id: string;
  email: string;
  password: string;
  name: string;
  role: string;
}): Promise<UserAdmin> => {
  const response = await api.post('/users', data);
  return response.data;
};

export const updateUser = async (
  id: string,
  data: Partial<UserAdmin>
): Promise<UserAdmin> => {
  const response = await api.put(`/users/${id}`, data);
  return response.data;
};

export const deleteUser = async (id: string): Promise<void> => {
  await api.delete(`/users/${id}`);
};
