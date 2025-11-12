/**
 * Lead Service
 * 
 * API client for lead management operations.
 * Uses auto-generated types from OpenAPI specification.
 */

import api from './api';
import type { components } from '../types/api.generated';

type LeadResponse = components['schemas']['LeadResponse'];
type LeadCreate = components['schemas']['LeadCreate'];
type LeadUpdate = components['schemas']['LeadUpdate'];
type LeadStatusUpdate = components['schemas']['LeadStatusUpdate'];
type LeadScoreUpdate = components['schemas']['LeadScoreUpdate'];

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
    const response = await api.get<LeadResponse[]>(
      `/tenants/${tenantId}/leads`,
      { params }
    );
    return response.data;
  },

  /**
   * Search leads by query
   */
  async search(tenantId: string, query: string, limit: number = 10): Promise<LeadResponse[]> {
    const response = await api.get<LeadResponse[]>(
      `/tenants/${tenantId}/leads/search`,
      { params: { q: query, limit } }
    );
    return response.data;
  },

  /**
   * Get hot leads (high score)
   */
  async getHotLeads(tenantId: string, threshold: number = 61): Promise<LeadResponse[]> {
    const response = await api.get<LeadResponse[]>(
      `/tenants/${tenantId}/leads/hot`,
      { params: { threshold } }
    );
    return response.data;
  },

  /**
   * Get lead by ID
   */
  async getById(tenantId: string, leadId: string): Promise<LeadResponse> {
    const response = await api.get<LeadResponse>(
      `/tenants/${tenantId}/leads/${leadId}`
    );
    return response.data;
  },

  /**
   * Create a new lead
   */
  async create(tenantId: string, data: LeadCreate): Promise<LeadResponse> {
    const response = await api.post<LeadResponse>(
      `/tenants/${tenantId}/leads`,
      data
    );
    return response.data;
  },

  /**
   * Update an existing lead
   */
  async update(tenantId: string, leadId: string, data: LeadUpdate): Promise<LeadResponse> {
    const response = await api.put<LeadResponse>(
      `/tenants/${tenantId}/leads/${leadId}`,
      data
    );
    return response.data;
  },

  /**
   * Update lead status
   */
  async updateStatus(
    tenantId: string,
    leadId: string,
    data: LeadStatusUpdate
  ): Promise<LeadResponse> {
    const response = await api.patch<LeadResponse>(
      `/tenants/${tenantId}/leads/${leadId}/status`,
      data
    );
    return response.data;
  },

  /**
   * Update lead score
   */
  async updateScore(
    tenantId: string,
    leadId: string,
    data: LeadScoreUpdate
  ): Promise<LeadResponse> {
    const response = await api.patch<LeadResponse>(
      `/tenants/${tenantId}/leads/${leadId}/score`,
      data
    );
    return response.data;
  },

  /**
   * Delete a lead
   */
  async delete(tenantId: string, leadId: string): Promise<void> {
    await api.delete(`/tenants/${tenantId}/leads/${leadId}`);
  },
};
