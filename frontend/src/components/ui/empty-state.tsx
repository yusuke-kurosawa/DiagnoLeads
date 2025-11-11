/**
 * EmptyState Component
 * Based on: openspec/specs/ui-ux/usability-guidelines.md
 * 
 * Displays empty states with icon, title, description, and optional action
 */

import * as React from 'react';
import { cn } from '@/lib/utils';
import { Button, type ButtonProps } from './button';

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
    variant?: ButtonProps['variant'];
    icon?: React.ReactNode;
  };
  secondaryAction?: {
    label: string;
    onClick: () => void;
    variant?: ButtonProps['variant'];
  };
  className?: string;
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  secondaryAction,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center text-center py-12 px-4',
        className
      )}
      role="status"
      aria-live="polite"
    >
      {/* Icon */}
      {icon && (
        <div className="mb-6 text-gray-400" aria-hidden="true">
          {icon}
        </div>
      )}

      {/* Title */}
      <h3 className="text-xl font-semibold text-gray-900 mb-2">
        {title}
      </h3>

      {/* Description */}
      {description && (
        <p className="text-base text-gray-600 max-w-md mb-6">
          {description}
        </p>
      )}

      {/* Actions */}
      {(action || secondaryAction) && (
        <div className="flex flex-col sm:flex-row gap-3 mt-2">
          {action && (
            <Button
              variant={action.variant || 'primary'}
              onClick={action.onClick}
              leftIcon={action.icon}
            >
              {action.label}
            </Button>
          )}
          {secondaryAction && (
            <Button
              variant={secondaryAction.variant || 'outline'}
              onClick={secondaryAction.onClick}
            >
              {secondaryAction.label}
            </Button>
          )}
        </div>
      )}
    </div>
  );
}

/**
 * Preset variants for common empty states
 */
export function NoDataEmptyState({
  title = 'データがありません',
  description,
  action,
  icon,
}: Partial<EmptyStateProps>) {
  return (
    <EmptyState
      icon={icon}
      title={title}
      description={description}
      action={action}
    />
  );
}

export function NoResultsEmptyState({
  searchQuery,
  onClear,
}: {
  searchQuery?: string;
  onClear?: () => void;
}) {
  return (
    <EmptyState
      title="検索結果が見つかりません"
      description={
        searchQuery
          ? `"${searchQuery}" に一致する結果が見つかりませんでした。`
          : '検索条件に一致する結果が見つかりませんでした。'
      }
      action={
        onClear
          ? {
              label: '検索条件をクリア',
              onClick: onClear,
              variant: 'outline',
            }
          : undefined
      }
    />
  );
}

export function ErrorEmptyState({
  onRetry,
  errorMessage,
}: {
  onRetry: () => void;
  errorMessage?: string;
}) {
  return (
    <EmptyState
      title="データの読み込みに失敗しました"
      description={
        errorMessage ||
        '一時的なエラーが発生しました。もう一度お試しください。'
      }
      action={{
        label: '再試行',
        onClick: onRetry,
        variant: 'primary',
      }}
    />
  );
}
