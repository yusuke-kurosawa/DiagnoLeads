import { AlertCircle, X } from 'lucide-react';

interface AlertErrorProps {
  message: string;
  onClose?: () => void;
}

export function AlertError({ message, onClose }: AlertErrorProps) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start justify-between">
      <div className="flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
        <p className="text-sm text-red-800">{message}</p>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="text-red-400 hover:text-red-600 transition-colors"
          aria-label="閉じる"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}
