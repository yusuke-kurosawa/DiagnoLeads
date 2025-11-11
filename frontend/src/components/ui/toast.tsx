/**
 * Toast Component - Modern notification system
 * Based on: openspec/specs/ui-ux/component-library.md
 */

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';
import { X, CheckCircle, XCircle, AlertCircle, Info } from 'lucide-react';

const toastVariants = cva(
  'pointer-events-auto flex w-full max-w-md items-start gap-3 rounded-lg border p-4 shadow-lg backdrop-blur-sm',
  {
    variants: {
      variant: {
        default: 'bg-white border-gray-200 text-gray-900',
        success: 'bg-success-50 border-success-200 text-success-900',
        error: 'bg-error-50 border-error-200 text-error-900',
        warning: 'bg-warning-50 border-warning-200 text-warning-900',
        info: 'bg-info-50 border-info-200 text-info-900',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

const iconMap = {
  default: Info,
  success: CheckCircle,
  error: XCircle,
  warning: AlertCircle,
  info: Info,
};

const iconColorMap = {
  default: 'text-gray-500',
  success: 'text-success-600',
  error: 'text-error-600',
  warning: 'text-warning-600',
  info: 'text-info-600',
};

export interface ToastProps extends VariantProps<typeof toastVariants> {
  id: string;
  title?: string;
  description?: string;
  action?: React.ReactNode;
  onClose?: () => void;
  duration?: number;
}

export function Toast({
  variant = 'default',
  title,
  description,
  action,
  onClose,
  duration = 5000,
}: ToastProps) {
  const [progress, setProgress] = React.useState(100);
  const Icon = iconMap[variant || 'default'];
  const iconColor = iconColorMap[variant || 'default'];

  React.useEffect(() => {
    if (duration === Infinity) return;

    const interval = setInterval(() => {
      setProgress((prev) => {
        const next = prev - (100 / duration) * 50;
        return next <= 0 ? 0 : next;
      });
    }, 50);

    const timeout = setTimeout(() => {
      onClose?.();
    }, duration);

    return () => {
      clearInterval(interval);
      clearTimeout(timeout);
    };
  }, [duration, onClose]);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -50, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      className={cn(toastVariants({ variant }), 'relative overflow-hidden')}
    >
      {/* Icon */}
      <Icon className={cn('w-5 h-5 flex-shrink-0 mt-0.5', iconColor)} />

      {/* Content */}
      <div className="flex-1 space-y-1">
        {title && (
          <div className="font-semibold text-sm leading-none">{title}</div>
        )}
        {description && (
          <div className="text-sm opacity-90">{description}</div>
        )}
        {action && <div className="mt-2">{action}</div>}
      </div>

      {/* Close Button */}
      {onClose && (
        <button
          onClick={onClose}
          className="flex-shrink-0 rounded-lg p-1 hover:bg-black/5 transition-colors"
          aria-label="Close"
        >
          <X className="w-4 h-4" />
        </button>
      )}

      {/* Progress Bar */}
      {duration !== Infinity && (
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/10">
          <motion.div
            className="h-full bg-current opacity-50"
            initial={{ width: '100%' }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.05, ease: 'linear' }}
          />
        </div>
      )}
    </motion.div>
  );
}

export interface ToastContainerProps {
  position?: 'top-right' | 'top-center' | 'top-left' | 'bottom-right' | 'bottom-center' | 'bottom-left';
  children: React.ReactNode;
}

const positionClasses = {
  'top-right': 'top-4 right-4',
  'top-center': 'top-4 left-1/2 -translate-x-1/2',
  'top-left': 'top-4 left-4',
  'bottom-right': 'bottom-4 right-4',
  'bottom-center': 'bottom-4 left-1/2 -translate-x-1/2',
  'bottom-left': 'bottom-4 left-4',
};

export function ToastContainer({ position = 'top-right', children }: ToastContainerProps) {
  return (
    <div
      className={cn(
        'fixed z-notification pointer-events-none flex flex-col gap-2 w-full max-w-md',
        positionClasses[position]
      )}
    >
      <AnimatePresence mode="popLayout">
        {children}
      </AnimatePresence>
    </div>
  );
}
