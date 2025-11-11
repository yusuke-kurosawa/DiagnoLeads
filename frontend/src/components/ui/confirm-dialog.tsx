/**
 * Confirm Dialog Component - Confirmation dialogs
 * Based on: openspec/specs/ui-ux/component-library.md
 */

import * as React from 'react';
import {
  Dialog,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogBody,
  DialogFooter,
} from './dialog';
import { Button } from './button';
import { AlertTriangle, HelpCircle, Info } from 'lucide-react';

export interface ConfirmDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void | Promise<void>;
  title: string;
  description?: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'default' | 'destructive' | 'warning';
  loading?: boolean;
}

const variantConfig = {
  default: {
    icon: HelpCircle,
    iconColor: 'text-primary-600',
    iconBg: 'bg-primary-100',
    confirmVariant: 'primary' as const,
  },
  destructive: {
    icon: AlertTriangle,
    iconColor: 'text-error-600',
    iconBg: 'bg-error-100',
    confirmVariant: 'destructive' as const,
  },
  warning: {
    icon: Info,
    iconColor: 'text-warning-600',
    iconBg: 'bg-warning-100',
    confirmVariant: 'primary' as const,
  },
};

export function ConfirmDialog({
  open,
  onClose,
  onConfirm,
  title,
  description,
  confirmText = '確認',
  cancelText = 'キャンセル',
  variant = 'default',
  loading = false,
}: ConfirmDialogProps) {
  const [isConfirming, setIsConfirming] = React.useState(false);
  const config = variantConfig[variant];
  const Icon = config.icon;

  const handleConfirm = async () => {
    setIsConfirming(true);
    try {
      await onConfirm();
      onClose();
    } catch (error) {
      console.error('Confirmation failed:', error);
    } finally {
      setIsConfirming(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} size="sm">
      <DialogHeader onClose={onClose} showCloseButton={false} />
      
      <DialogBody>
        <div className="flex gap-4">
          <div className={`flex-shrink-0 w-12 h-12 rounded-full ${config.iconBg} flex items-center justify-center`}>
            <Icon className={`w-6 h-6 ${config.iconColor}`} />
          </div>
          
          <div className="flex-1">
            <DialogTitle>{title}</DialogTitle>
            {description && (
              <DialogDescription className="mt-2">
                {description}
              </DialogDescription>
            )}
          </div>
        </div>
      </DialogBody>

      <DialogFooter>
        <Button
          variant="outline"
          onClick={onClose}
          disabled={isConfirming || loading}
        >
          {cancelText}
        </Button>
        <Button
          variant={config.confirmVariant}
          onClick={handleConfirm}
          loading={isConfirming || loading}
        >
          {confirmText}
        </Button>
      </DialogFooter>
    </Dialog>
  );
}
