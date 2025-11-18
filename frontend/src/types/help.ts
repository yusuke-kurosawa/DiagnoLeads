/**
 * Help system type definitions
 */

import { ReactNode } from 'react';
import { type LucideIcon } from 'lucide-react';

/**
 * Individual step in a help guide
 */
export interface HelpStep {
  title: string;
  description: string;
  image?: string;
}

/**
 * Section within help content
 */
export interface HelpSection {
  title: string;
  content: string | ReactNode;
}

/**
 * Related link for additional resources
 */
export interface HelpLink {
  title: string;
  url: string;
}

/**
 * Complete help content for a page
 */
export interface PageHelp {
  title: string;
  description: string;
  steps?: HelpStep[];
  sections?: HelpSection[];
  relatedLinks?: HelpLink[];
}

/**
 * Help content map keyed by page identifier
 */
export type HelpContentMap = Record<string, PageHelp>;

/**
 * Help category for organization
 */
export interface HelpCategory {
  title: string;
  icon: LucideIcon;
  items: HelpCategoryItem[];
}

/**
 * Individual item within a help category
 */
export interface HelpCategoryItem {
  key: string;
  title: string;
  description: string;
}

/**
 * FAQ item
 */
export interface FAQItem {
  question: string;
  answer: string;
}

/**
 * Page keys for help content
 */
export type PageKey =
  | 'dashboard'
  | 'assessments'
  | 'assessments-create'
  | 'assessments-edit'
  | 'leads'
  | 'analytics'
  | 'settings'
  | 'admin-masters'
  | 'admin-audit-logs';
