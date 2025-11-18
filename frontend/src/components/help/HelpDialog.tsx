/**
 * HelpDialog Component
 * Modal dialog for displaying contextual help content
 * Supports steps, sections, and related links
 */

import React from 'react';
import {
  Dialog,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogBody,
} from '../ui/dialog';
import { BookOpen } from 'lucide-react';
import { HelpStep, HelpSection as HelpSectionType, HelpLink } from '../../types/help';
import { HelpStepItem } from './HelpStepItem';
import { HelpSection } from './HelpSection';
import { RelatedLinks } from './RelatedLinks';

export interface HelpDialogProps {
  open: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  steps?: HelpStep[];
  sections?: HelpSectionType[];
  relatedLinks?: HelpLink[];
}

/**
 * HelpDialog displays comprehensive help content in a modal
 * Automatically organizes content into steps, sections, and links
 */
export function HelpDialog({
  open,
  onClose,
  title,
  description,
  steps = [],
  sections = [],
  relatedLinks = [],
}: HelpDialogProps) {
  const hasContent = steps.length > 0 || sections.length > 0 || relatedLinks.length > 0;

  return (
    <Dialog open={open} onClose={onClose} size="lg">
      <DialogHeader onClose={onClose}>
        <div className="flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-blue-600" aria-hidden="true" />
          <DialogTitle>{title}</DialogTitle>
        </div>
        {description && <DialogDescription>{description}</DialogDescription>}
      </DialogHeader>

      <DialogBody className="max-h-[calc(100vh-12rem)] overflow-y-auto">
        {!hasContent ? (
          <div className="text-center py-8 text-gray-500">
            <p>このページのヘルプコンテンツは準備中です。</p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Steps Section */}
            {steps.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide">
                  使い方
                </h3>
                <div className="space-y-4" role="list">
                  {steps.map((step, index) => (
                    <HelpStepItem key={index} step={step} index={index} />
                  ))}
                </div>
              </div>
            )}

            {/* Sections */}
            {sections.length > 0 && (
              <div className="space-y-6">
                {sections.map((section, index) => (
                  <HelpSection key={index} section={section} />
                ))}
              </div>
            )}

            {/* Related Links */}
            <RelatedLinks links={relatedLinks} />
          </div>
        )}
      </DialogBody>
    </Dialog>
  );
}
