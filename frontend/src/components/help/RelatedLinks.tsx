/**
 * RelatedLinks Component
 * Displays related help links
 */

import { ExternalLink } from 'lucide-react';
import { type HelpLink } from '../../types/help';

interface RelatedLinksProps {
  links: HelpLink[];
}

export function RelatedLinks({ links }: RelatedLinksProps) {
  if (links.length === 0) return null;

  return (
    <div className="space-y-2 pt-4 border-t border-gray-200">
      <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide">
        関連リンク
      </h3>
      <nav aria-label="Related links">
        <ul className="space-y-2">
          {links.map((link, index) => (
            <li key={index}>
              <a
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800 hover:underline focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
              >
                <ExternalLink className="w-4 h-4" aria-hidden="true" />
                <span>{link.title}</span>
              </a>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
}
