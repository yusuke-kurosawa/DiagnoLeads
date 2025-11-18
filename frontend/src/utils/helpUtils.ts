/**
 * Utility functions for help system
 */

import { PageKey } from '../types/help';

/**
 * Determines the help page key from the current pathname
 * @param pathname - Current route pathname
 * @returns Corresponding page key for help content
 */
export function getPageKeyFromPath(pathname: string): PageKey {
  // Check specific patterns first (most specific to least specific)
  if (pathname.includes('/assessments/create')) return 'assessments-create';
  if (pathname.includes('/assessments') && pathname.includes('/edit')) return 'assessments-edit';
  if (pathname.includes('/assessments')) return 'assessments';
  if (pathname.includes('/leads')) return 'leads';
  if (pathname.includes('/analytics')) return 'analytics';
  if (pathname.includes('/settings')) return 'settings';
  if (pathname.includes('/admin/masters')) return 'admin-masters';
  if (pathname.includes('/admin/audit-logs')) return 'admin-audit-logs';
  if (pathname.includes('/dashboard')) return 'dashboard';

  // Default to dashboard
  return 'dashboard';
}

/**
 * Filters text based on search query (case-insensitive)
 * @param text - Text to search in
 * @param query - Search query
 * @returns True if text contains query
 */
export function matchesSearchQuery(text: string, query: string): boolean {
  if (!query.trim()) return true;
  return text.toLowerCase().includes(query.toLowerCase());
}
