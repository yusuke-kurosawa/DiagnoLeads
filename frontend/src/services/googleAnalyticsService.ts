/**
 * Google Analytics Integration Service
 *
 * API client for GA4 integration endpoints
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

export interface GoogleAnalyticsIntegration {
  id: string;
  tenant_id: string;
  measurement_id: string;
  enabled: boolean;
  track_frontend: boolean;
  track_embed_widget: boolean;
  track_server_events: boolean;
  custom_dimensions?: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface GoogleAnalyticsIntegrationCreate {
  measurement_id: string;
  measurement_protocol_api_secret?: string;
  enabled: boolean;
  track_frontend: boolean;
  track_embed_widget: boolean;
  track_server_events: boolean;
  custom_dimensions?: Record<string, any>;
}

export interface GoogleAnalyticsTestResponse {
  status: 'success' | 'failed';
  message: string;
  event_name?: string;
  timestamp?: string;
  error_details?: string;
}

export interface GoogleAnalyticsPublicConfig {
  measurement_id: string;
  enabled: boolean;
  track_embed_widget: boolean;
}

/**
 * Get Google Analytics integration for a tenant
 */
export const getGoogleAnalyticsIntegration = async (
  tenantId: string
): Promise<GoogleAnalyticsIntegration> => {
  const response = await api.get(`/tenants/${tenantId}/integrations/google-analytics`);
  return response.data;
};

/**
 * Create or update Google Analytics integration
 */
export const createOrUpdateGoogleAnalyticsIntegration = async (
  tenantId: string,
  data: GoogleAnalyticsIntegrationCreate
): Promise<GoogleAnalyticsIntegration> => {
  const response = await api.put(`/tenants/${tenantId}/integrations/google-analytics`, data);
  return response.data;
};

/**
 * Delete Google Analytics integration
 */
export const deleteGoogleAnalyticsIntegration = async (
  tenantId: string
): Promise<void> => {
  await api.delete(`/tenants/${tenantId}/integrations/google-analytics`);
};

/**
 * Test Google Analytics connection
 */
export const testGoogleAnalyticsConnection = async (
  tenantId: string
): Promise<GoogleAnalyticsTestResponse> => {
  const response = await api.post(`/tenants/${tenantId}/integrations/google-analytics/test`);
  return response.data;
};

/**
 * Get public Google Analytics configuration (for embed widget)
 * No authentication required
 */
export const getPublicGoogleAnalyticsConfig = async (
  assessmentId: string
): Promise<GoogleAnalyticsPublicConfig> => {
  const response = await axios.get(
    `${API_BASE_URL}/public/assessments/${assessmentId}/google-analytics-config`
  );
  return response.data;
};

const googleAnalyticsService = {
  getGoogleAnalyticsIntegration,
  createOrUpdateGoogleAnalyticsIntegration,
  deleteGoogleAnalyticsIntegration,
  testGoogleAnalyticsConnection,
  getPublicGoogleAnalyticsConfig,
};

export default googleAnalyticsService;
