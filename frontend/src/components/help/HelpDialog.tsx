import React from 'react';
import {
  Dialog,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogBody,
} from '../ui/dialog';
import { BookOpen, ExternalLink } from 'lucide-react';
import { HelpStep, HelpSection, HelpLink } from '../../types/help';

export interface HelpDialogProps {
  open: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  steps?: HelpStep[];
  sections?: HelpSection[];
  relatedLinks?: HelpLink[];
}

export function HelpDialog({
  open,
  onClose,
  title,
  description,
  steps,
  sections,
  relatedLinks,
}: HelpDialogProps) {
  return (
    <Dialog open={open} onClose={onClose} size="lg">
      <DialogHeader onClose={onClose}>
        <div className="flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-blue-600" />
          <DialogTitle>{title}</DialogTitle>
        </div>
        {description && <DialogDescription>{description}</DialogDescription>}
      </DialogHeader>

      <DialogBody className="max-h-[calc(100vh-12rem)] overflow-y-auto">
        <div className="space-y-6">
          {/* Steps Section */}
          {steps && steps.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide">
                使い方
              </h3>
              <div className="space-y-4">
                {steps.map((step, index) => (
                  <div
                    key={index}
                    className="flex gap-4 p-4 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold text-sm">
                        {index + 1}
                      </div>
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 mb-1">
                        {step.title}
                      </h4>
                      <p className="text-sm text-gray-600">{step.description}</p>
                      {step.image && (
                        <img
                          src={step.image}
                          alt={step.title}
                          className="mt-3 rounded border border-gray-200 w-full"
                        />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Sections */}
          {sections && sections.length > 0 && (
            <div className="space-y-6">
              {sections.map((section, index) => (
                <div key={index} className="space-y-2">
                  <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide">
                    {section.title}
                  </h3>
                  {typeof section.content === 'string' ? (
                    <p className="text-sm text-gray-600 leading-relaxed">
                      {section.content}
                    </p>
                  ) : (
                    <div className="text-sm text-gray-600">{section.content}</div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Related Links */}
          {relatedLinks && relatedLinks.length > 0 && (
            <div className="space-y-2 pt-4 border-t border-gray-200">
              <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide">
                関連リンク
              </h3>
              <div className="space-y-2">
                {relatedLinks.map((link, index) => (
                  <a
                    key={index}
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800 hover:underline"
                  >
                    <ExternalLink className="w-4 h-4" />
                    {link.title}
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      </DialogBody>
    </Dialog>
  );
}
