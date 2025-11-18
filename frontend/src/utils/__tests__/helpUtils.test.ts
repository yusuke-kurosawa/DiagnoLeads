/**
 * Unit tests for helpUtils
 */

import { describe, it, expect } from 'vitest';
import { getPageKeyFromPath, matchesSearchQuery } from '../helpUtils';

describe('helpUtils', () => {
  describe('getPageKeyFromPath', () => {
    it('should return "assessments-create" for create assessment path', () => {
      expect(getPageKeyFromPath('/tenants/123/assessments/create')).toBe('assessments-create');
    });

    it('should return "assessments-edit" for edit assessment path', () => {
      expect(getPageKeyFromPath('/tenants/123/assessments/456/edit')).toBe('assessments-edit');
    });

    it('should return "assessments" for assessments list path', () => {
      expect(getPageKeyFromPath('/tenants/123/assessments')).toBe('assessments');
    });

    it('should return "leads" for leads path', () => {
      expect(getPageKeyFromPath('/tenants/123/leads')).toBe('leads');
    });

    it('should return "analytics" for analytics path', () => {
      expect(getPageKeyFromPath('/tenants/123/analytics')).toBe('analytics');
    });

    it('should return "settings" for settings path', () => {
      expect(getPageKeyFromPath('/tenants/123/settings')).toBe('settings');
    });

    it('should return "admin-masters" for masters admin path', () => {
      expect(getPageKeyFromPath('/tenants/123/admin/masters')).toBe('admin-masters');
    });

    it('should return "admin-audit-logs" for audit logs path', () => {
      expect(getPageKeyFromPath('/tenants/123/admin/audit-logs')).toBe('admin-audit-logs');
    });

    it('should return "dashboard" for dashboard path', () => {
      expect(getPageKeyFromPath('/dashboard')).toBe('dashboard');
    });

    it('should return "dashboard" for unknown paths', () => {
      expect(getPageKeyFromPath('/unknown-path')).toBe('dashboard');
    });

    it('should prioritize more specific paths (create over general)', () => {
      expect(getPageKeyFromPath('/tenants/123/assessments/create')).toBe('assessments-create');
      expect(getPageKeyFromPath('/tenants/123/assessments/456')).toBe('assessments');
    });
  });

  describe('matchesSearchQuery', () => {
    it('should return true for empty query', () => {
      expect(matchesSearchQuery('any text', '')).toBe(true);
      expect(matchesSearchQuery('any text', '   ')).toBe(true);
    });

    it('should match case-insensitively', () => {
      expect(matchesSearchQuery('Hello World', 'hello')).toBe(true);
      expect(matchesSearchQuery('Hello World', 'WORLD')).toBe(true);
      expect(matchesSearchQuery('Hello World', 'HeLLo WoRLd')).toBe(true);
    });

    it('should return true for partial matches', () => {
      expect(matchesSearchQuery('Dashboard Overview', 'dash')).toBe(true);
      expect(matchesSearchQuery('Dashboard Overview', 'view')).toBe(true);
    });

    it('should return false for non-matching queries', () => {
      expect(matchesSearchQuery('Dashboard', 'analytics')).toBe(false);
      expect(matchesSearchQuery('Hello', 'goodbye')).toBe(false);
    });

    it('should handle Japanese text', () => {
      expect(matchesSearchQuery('ダッシュボード', 'ダッシュ')).toBe(true);
      expect(matchesSearchQuery('診断管理', '診断')).toBe(true);
      expect(matchesSearchQuery('リード管理', 'リード')).toBe(true);
    });

    it('should handle special characters', () => {
      expect(matchesSearchQuery('test@example.com', '@example')).toBe(true);
      expect(matchesSearchQuery('path/to/file', 'path/to')).toBe(true);
    });
  });
});
