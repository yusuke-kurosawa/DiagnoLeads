/**
 * Alert Dialog Component - Simple alert dialogs
 * Based on: openspec/specs/ui-ux/component-library.md
 */
import {
  Dialog,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogBody,
  DialogFooter,
} from './dialog';
import { Button } from './button';
import { CheckCircle, XCircle, AlertTriangle, Info } from 'lucide-react';

export interface AlertDialogProps {
  open: boolean;
  onClose: () => void;
  variant?: 'success' | 'error' | 'warning' | 'info';
  title: string;
  description?: string;
  confirmText?: string;
}

const variantConfig = {
  success: {
    icon: CheckCircle,
    iconColor: 'text-success-600',
    iconBg: 'bg-success-100',
  },
  error: {
    icon: XCircle,
    iconColor: 'text-error-600',
    iconBg: 'bg-error-100',
  },
  warning: {
    icon: AlertTriangle,
    iconColor: 'text-warning-600',
    iconBg: 'bg-warning-100',
  },
  info: {
    icon: Info,
    iconColor: 'text-info-600',
    iconBg: 'bg-info-100',
  },
};

export function AlertDialog({
  open,
  onClose,
  variant = 'info',
  title,
  description,
  confirmText = 'OK',
}: AlertDialogProps) {
  const config = variantConfig[variant];
  const Icon = config.icon;

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
          variant="primary"
          onClick={onClose}
          fullWidth
        >
          {confirmText}
        </Button>
      </DialogFooter>
    </Dialog>
  );
}
