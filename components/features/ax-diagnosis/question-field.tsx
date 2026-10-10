'use client';

import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import type { DiagnosticLocale, DiagnosticQuestion } from '@/lib/features/diagnostics/types';
import { cn } from '@/lib/utils';
import { AlertCircle } from 'lucide-react';
import { useTranslations } from 'next-intl';

export const CHECKBOX_CLASS =
  'border-gray-500 focus-visible:ring-ax-teal-dark data-[state=checked]:border-ax-teal-dark data-[state=checked]:bg-ax-teal-dark';

interface QuestionFieldProps {
  question: DiagnosticQuestion;
  locale: DiagnosticLocale;
  value: string | string[] | undefined;
  error?: string;
  onSingle: (value: string) => void;
  onToggle: (value: string, checked: boolean) => void;
}

export function QuestionField({
  question,
  locale,
  value,
  error,
  onSingle,
  onToggle,
}: QuestionFieldProps) {
  const t = useTranslations('axDiagnosis');
  const legendId = `q-${question.id}`;
  const exclusive = question.exclusiveOptions ?? [];
  const optionClass = (selected: boolean) =>
    cn(
      'flex min-h-12 cursor-pointer items-start gap-3 rounded-xl border-2 p-3 text-sm transition-colors has-[:focus-visible]:ring-3 has-[:focus-visible]:ring-ax-teal-dark has-[:focus-visible]:ring-offset-2',
      selected
        ? 'border-ax-teal-dark bg-ax-teal/5 text-ax-ink'
        : 'border-gray-200 bg-white text-gray-800 hover:border-gray-300'
    );
  // The hint is a description of the option, not part of its name
  const optionText = (option: DiagnosticQuestion['options'][number], id: string) => (
    <span>
      <span className="block font-medium">{option.label[locale]}</span>
      {option.hint && (
        <span
          id={`${id}-hint`}
          aria-hidden="true"
          className="mt-0.5 block text-xs leading-relaxed text-gray-600"
        >
          {option.hint[locale]}
        </span>
      )}
    </span>
  );
  const hintId = (option: DiagnosticQuestion['options'][number], id: string) =>
    option.hint ? `${id}-hint` : undefined;
  // Name the options that clear the others, as they are written on screen
  const exclusiveLabels = question.options
    .filter((option) => exclusive.includes(option.value))
    .map((option) => t('quoted', { label: option.label[locale] }))
    .join(t('listJoiner'));

  return (
    <fieldset
      className={cn('space-y-3', error && 'rounded-2xl border-2 border-red-600 p-3')}
      // The error is part of the group name (legend) only, so it is read once
      aria-describedby={
        [
          question.description ? `${legendId}-description` : '',
          question.type === 'multiple' ? `${legendId}-hint` : '',
        ]
          .filter(Boolean)
          .join(' ') || undefined
      }
    >
      <legend id={legendId} className="mb-1 font-bold leading-relaxed">
        {question.label[locale]}
        {!question.required && (
          <span className="ml-2 inline-block rounded bg-gray-100 px-1.5 py-0.5 align-middle text-xs font-bold text-gray-600">
            {t('optional')}
          </span>
        )}
        {error && <span className="sr-only">{error}</span>}
      </legend>
      {question.description && (
        <p id={`${legendId}-description`} className="text-sm leading-relaxed text-gray-600">
          {question.description[locale]}
        </p>
      )}
      {question.type === 'multiple' && (
        <p id={`${legendId}-hint`} className="text-xs text-gray-600">
          {exclusive.length > 0
            ? t('multipleHintExclusive', { options: exclusiveLabels })
            : t('multipleHint')}
        </p>
      )}

      {question.type === 'single' ? (
        <RadioGroup
          value={typeof value === 'string' ? value : ''}
          onValueChange={onSingle}
          required={question.required}
          className="grid gap-2 sm:grid-cols-2"
        >
          {question.options.map((option) => {
            const id = `${question.id}-${option.value}`;
            return (
              <Label
                key={option.value}
                htmlFor={id}
                className={optionClass(value === option.value)}
              >
                <RadioGroupItem
                  id={id}
                  value={option.value}
                  aria-describedby={hintId(option, id)}
                  className="mt-0.5 border-gray-500 text-ax-teal-dark"
                />
                {optionText(option, id)}
              </Label>
            );
          })}
        </RadioGroup>
      ) : (
        <div className="grid gap-2 sm:grid-cols-2">
          {question.options.map((option) => {
            const id = `${question.id}-${option.value}`;
            const checked = Array.isArray(value) && value.includes(option.value);
            return (
              <Label key={option.value} htmlFor={id} className={optionClass(checked)}>
                <Checkbox
                  id={id}
                  checked={checked}
                  onCheckedChange={(state) => onToggle(option.value, state === true)}
                  aria-describedby={hintId(option, id)}
                  className={cn('mt-0.5', CHECKBOX_CLASS)}
                />
                {optionText(option, id)}
              </Label>
            );
          })}
        </div>
      )}

      {error && (
        <p
          id={`${legendId}-error`}
          className="flex items-center gap-1.5 text-sm font-bold text-red-700"
        >
          <AlertCircle className="h-4 w-4 shrink-0" aria-hidden="true" />
          {error}
        </p>
      )}
    </fieldset>
  );
}
