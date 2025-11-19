/**
 * HelpSection Component
 * Displays a section of help content
 */

import { type HelpSection as HelpSectionType } from '../../types/help';

interface HelpSectionProps {
  section: HelpSectionType;
}

export function HelpSection({ section }: HelpSectionProps) {
  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide">
        {section.title}
      </h3>
      {typeof section.content === 'string' ? (
        <p className="text-sm text-gray-600 leading-relaxed">{section.content}</p>
      ) : (
        <div className="text-sm text-gray-600">{section.content}</div>
      )}
    </div>
  );
}
