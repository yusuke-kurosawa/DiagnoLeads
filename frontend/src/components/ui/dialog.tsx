/**
 * Dialog/Modal Component - Modern dialog system
 * Based on: openspec/specs/ui-ux/component-library.md
 */

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';
import { X } from 'lucide-react';

const dialogVariants = cva(
  'relative bg-white rounded-lg shadow-2xl',
  {
    variants: {
      size: {
        sm: 'max-w-md',
        md: 'max-w-lg',
        lg: 'max-w-2xl',
        xl: 'max-w-4xl',
        full: 'max-w-full mx-4 h-[calc(100vh-2rem)]',
      },
    },
    defaultVariants: {
      size: 'md',
    },
  }
);

export interface DialogProps extends VariantProps<typeof dialogVariants> {
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
  closeOnOverlayClick?: boolean;
  closeOnEsc?: boolean;
  className?: string;
}

export function Dialog({
  open,
  onClose,
  children,
  size,
  closeOnOverlayClick = true,
  closeOnEsc = true,
  className,
}: DialogProps) {
  React.useEffect(() => {
    if (!closeOnEsc) return;

    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (open) {
      document.addEventListener('keydown', handleEsc);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEsc);
      document.body.style.overflow = 'unset';
    };
  }, [open, onClose, closeOnEsc]);

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-modal-backdrop bg-black/50 backdrop-blur-sm"
            onClick={closeOnOverlayClick ? onClose : undefined}
          />

          {/* Dialog Container */}
          <div className="fixed inset-0 z-modal flex items-center justify-center p-4 pointer-events-none">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ duration: 0.2 }}
              className={cn(
                dialogVariants({ size }),
                'pointer-events-auto w-full',
                className
              )}
              onClick={(e) => e.stopPropagation()}
            >
              {children}
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}

export interface DialogHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children?: React.ReactNode;
  onClose?: () => void;
  showCloseButton?: boolean;
}

export function DialogHeader({
  children,
  onClose,
  showCloseButton = true,
  className,
  ...props
}: DialogHeaderProps) {
  return (
    <div
      className={cn(
        'flex items-start justify-between p-6 border-b border-gray-200',
        className
      )}
      {...props}
    >
      <div className="flex-1">{children}</div>
      {showCloseButton && onClose && (
        <button
          onClick={onClose}
          className="ml-4 rounded-lg p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
          aria-label="Close"
        >
          <X className="w-5 h-5" />
        </button>
      )}
    </div>
  );
}

export function DialogTitle({
  className,
  ...props
}: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h2
      className={cn('text-xl font-semibold text-gray-900', className)}
      {...props}
    />
  );
}

export function DialogDescription({
  className,
  ...props
}: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p
      className={cn('text-sm text-gray-600 mt-1', className)}
      {...props}
    />
  );
}

export function DialogBody({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn('p-6', className)}
      {...props}
    />
  );
}

export function DialogFooter({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'flex items-center justify-end gap-3 p-6 border-t border-gray-200',
        className
      )}
      {...props}
    />
  );
}
