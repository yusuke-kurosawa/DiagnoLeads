/**
 * Lead Service
 * 
 * API client for lead management operations.
 * Uses auto-generated types from OpenAPI specification.
 */

import type { components } from '../types/api.generated';

type LeadResponse = components['schemas']['LeadResponse'];
type LeadCreate = components['schemas']['LeadCreate'];
type LeadUpdate = components['schemas']['LeadUpdate'];
type LeadStatusUpdate = components['schemas']['LeadStatusUpdate'];
type LeadScoreUpdate = components['schemas']['LeadScoreUpdate'];

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

/**
 * Lead Service API
 */
export const leadService = {
  /**
   * List all leads for a tenant
   */
  async list(
    tenantId: string,
    params?: {
      skip?: number;
      limit?: number;
      status?: string;
      min_score?: number;
      max_score?: number;
      assigned_to?: string;
    }
  ): Promise<LeadResponse[]> {
    const queryParams = new URLSearchParams();
    if (params?.skip !== undefined) queryParams.append('skip', params.skip.toString());
    if (params?.limit !== undefined) queryParams.append('limit', params.limit.toString());
    if (params?.status) queryParams.append('status', params.status);
    if (params?.min_score !== undefined) queryParams.append('min_score', params.min_score.toString());
    if (params?.max_score !== undefined) queryParams.append('max_score', params.max_score.toString());
    if (params?.assigned_to) queryParams.append('assigned_to', params.assigned_to);

    const url = `${API_BASE}/tenants/${tenantId}/leads?${queryParams}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch leads: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Search leads by query
   */
  async search(tenantId: string, query: string, limit: number = 10): Promise<LeadResponse[]> {
    const queryParams = new URLSearchParams({ q: query, limit: limit.toString() });
    const url = `${API_BASE}/tenants/${tenantId}/leads/search?${queryParams}`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to search leads: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Get hot leads (high score)
   */
  async getHotLeads(tenantId: string, threshold: number = 61): Promise<LeadResponse[]> {
    const queryParams = new URLSearchParams({ threshold: threshold.toString() });
    const url = `${API_BASE}/tenants/${tenantId}/leads/hot?${queryParams}`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch hot leads: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Get lead by ID
   */
  async getById(tenantId: string, leadId: string): Promise<LeadResponse> {
    const url = `${API_BASE}/tenants/${tenantId}/leads/${leadId}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: getHeaders(),
    });

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Lead not found');
      }
      throw new Error(`Failed to fetch lead: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Create a new lead
   */
  async create(tenantId: string, data: LeadCreate): Promise<LeadResponse> {
    const url = `${API_BASE}/tenants/${tenantId}/leads`;
    const response = await fetch(url, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create lead');
    }

    return response.json();
  },

  /**
   * Update an existing lead
   */
  async update(tenantId: string, leadId: string, data: LeadUpdate): Promise<LeadResponse> {
    const url = `${API_BASE}/tenants/${tenantId}/leads/${leadId}`;
    const response = await fetch(url, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update lead');
    }

    return response.json();
  },

  /**
   * Update lead status
   */
  async updateStatus(
    tenantId: string,
    leadId: string,
    data: LeadStatusUpdate
  ): Promise<LeadResponse> {
    const url = `${API_BASE}/tenants/${tenantId}/leads/${leadId}/status`;
    const response = await fetch(url, {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update lead status');
    }

    return response.json();
  },

  /**
   * Update lead score
   */
  async updateScore(
    tenantId: string,
    leadId: string,
    data: LeadScoreUpdate
  ): Promise<LeadResponse> {
    const url = `${API_BASE}/tenants/${tenantId}/leads/${leadId}/score`;
    const response = await fetch(url, {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update lead score');
    }

    return response.json();
  },

  /**
   * Delete a lead
   */
  async delete(tenantId: string, leadId: string): Promise<void> {
    const url = `${API_BASE}/tenants/${tenantId}/leads/${leadId}`;
    const response = await fetch(url, {
      method: 'DELETE',
      headers: getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to delete lead: ${response.statusText}`);
    }
  },
};
