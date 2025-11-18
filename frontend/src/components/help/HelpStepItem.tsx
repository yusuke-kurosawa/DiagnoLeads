/**
 * HelpStepItem Component
 * Displays a single step in help guide
 */

import { type HelpStep } from '../../types/help';

interface HelpStepItemProps {
  step: HelpStep;
  index: number;
}

export function HelpStepItem({ step, index }: HelpStepItemProps) {
  return (
    <div
      className="flex gap-4 p-4 bg-gray-50 rounded-lg border border-gray-200"
      role="listitem"
    >
      <div className="flex-shrink-0">
        <div
          className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold text-sm"
          aria-label={`Step ${index + 1}`}
        >
          {index + 1}
        </div>
      </div>
      <div className="flex-1">
        <h4 className="font-medium text-gray-900 mb-1">{step.title}</h4>
        <p className="text-sm text-gray-600">{step.description}</p>
        {step.image && (
          <img
            src={step.image}
            alt={step.title}
            className="mt-3 rounded border border-gray-200 w-full"
            loading="lazy"
          />
        )}
      </div>
    </div>
  );
}
