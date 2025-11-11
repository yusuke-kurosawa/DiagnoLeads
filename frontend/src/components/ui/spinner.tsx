/**
 * Spinner Component
 * Based on: openspec/specs/ui-ux/usability-guidelines.md
 * 
 * Loading indicator for short-duration operations
 */

import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const spinnerVariants = cva(
  'inline-block animate-spin rounded-full border-solid border-current border-r-transparent',
  {
    variants: {
      size: {
        xs: 'h-3 w-3 border-2',
        sm: 'h-4 w-4 border-2',
        md: 'h-6 w-6 border-2',
        lg: 'h-8 w-8 border-3',
        xl: 'h-12 w-12 border-4',
      },
      variant: {
        default: 'text-gray-500',
        primary: 'text-primary-600',
        white: 'text-white',
        success: 'text-success-600',
        warning: 'text-warning-600',
        error: 'text-error-600',
      },
    },
    defaultVariants: {
      size: 'md',
      variant: 'default',
    },
  }
);

export interface SpinnerProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof spinnerVariants> {
  label?: string;
}

function Spinner({ 
  className, 
  size, 
  variant, 
  label = '読み込み中...',
  ...props 
}: SpinnerProps) {
  return (
    <div
      role="status"
      className={cn('inline-flex items-center justify-center', className)}
      aria-label={label}
      {...props}
    >
      <div className={cn(spinnerVariants({ size, variant }))} />
      <span className="sr-only">{label}</span>
    </div>
  );
}

/**
 * Full page spinner overlay
 */
function PageSpinner({ label = '読み込み中...' }: { label?: string }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/80 backdrop-blur-sm">
      <div className="text-center">
        <Spinner size="xl" variant="primary" label={label} />
        <p className="mt-4 text-sm text-gray-600">{label}</p>
      </div>
    </div>
  );
}

/**
 * Centered spinner for sections
 */
function SectionSpinner({ label = '読み込み中...' }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <Spinner size="lg" variant="primary" label={label} />
      <p className="mt-3 text-sm text-gray-600">{label}</p>
    </div>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export { Spinner, PageSpinner, SectionSpinner, spinnerVariants };
