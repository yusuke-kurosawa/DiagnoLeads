import { CheckCircle2, X } from 'lucide-react';

interface AlertSuccessProps {
  message: string;
  onClose?: () => void;
}

export function AlertSuccess({ message, onClose }: AlertSuccessProps) {
  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start justify-between">
      <div className="flex items-start gap-3">
        <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
        <p className="text-sm text-green-800">{message}</p>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="text-green-400 hover:text-green-600 transition-colors"
          aria-label="閉じる"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}
