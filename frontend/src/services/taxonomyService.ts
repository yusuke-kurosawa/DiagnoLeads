import axios from 'axios';
import type { Topic, Industry } from '../types/taxonomy';

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

export const getTopics = async (tenantId: string): Promise<Topic[]> => {
  const response = await api.get(`/tenants/${tenantId}/topics`);
  return response.data;
};

export const getTopic = async (tenantId: string, topicId: string): Promise<Topic> => {
  const response = await api.get(`/tenants/${tenantId}/topics/${topicId}`);
  return response.data;
};

export const createTopic = async (
  tenantId: string,
  data: {
    name: string;
    description?: string;
    color?: string;
    icon?: string;
  }
): Promise<Topic> => {
  const response = await api.post(`/tenants/${tenantId}/topics`, data);
  return response.data;
};

export const updateTopic = async (
  tenantId: string,
  topicId: string,
  data: Partial<Topic>
): Promise<Topic> => {
  const response = await api.put(`/tenants/${tenantId}/topics/${topicId}`, data);
  return response.data;
};

export const deleteTopic = async (tenantId: string, topicId: string): Promise<void> => {
  await api.delete(`/tenants/${tenantId}/topics/${topicId}`);
};

export const getIndustries = async (tenantId: string): Promise<Industry[]> => {
  const response = await api.get(`/tenants/${tenantId}/industries`);
  return response.data;
};

export const getIndustry = async (tenantId: string, industryId: string): Promise<Industry> => {
  const response = await api.get(`/tenants/${tenantId}/industries/${industryId}`);
  return response.data;
};

export const createIndustry = async (
  tenantId: string,
  data: {
    name: string;
    description?: string;
    color?: string;
    icon?: string;
  }
): Promise<Industry> => {
  const response = await api.post(`/tenants/${tenantId}/industries`, data);
  return response.data;
};

export const updateIndustry = async (
  tenantId: string,
  industryId: string,
  data: Partial<Industry>
): Promise<Industry> => {
  const response = await api.put(`/tenants/${tenantId}/industries/${industryId}`, data);
  return response.data;
};

export const deleteIndustry = async (tenantId: string, industryId: string): Promise<void> => {
  await api.delete(`/tenants/${tenantId}/industries/${industryId}`);
};
