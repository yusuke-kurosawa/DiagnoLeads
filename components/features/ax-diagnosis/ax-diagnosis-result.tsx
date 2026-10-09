'use client';

import { Button } from '@/components/ui/button';
import type {
  AxMigrationPublicResult,
  ChallengeType,
  Level,
} from '@/lib/features/diagnostics/ax-migration/evaluate';
import { cn } from '@/lib/utils';
import { CheckCircle2, Loader2, RotateCcw } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { useEffect, useRef, useState } from 'react';
import { trackAxEvent } from './tracking';

const LEVEL_STYLES: Record<Level, { badge: string; bar: string }> = {
  low: { badge: 'bg-emerald-100 text-emerald-800', bar: 'bg-emerald-500' },
  medium: { badge: 'bg-amber-100 text-amber-800', bar: 'bg-amber-500' },
  high: { badge: 'bg-red-100 text-red-800', bar: 'bg-red-500' },
};

const CHALLENGE_KEYS: ChallengeType[] = ['people', 'cost', 'agility', 'data'];
const STEP_KEYS = ['simple', 'survey', 'migration', 'ax'] as const;

interface AxDiagnosisResultProps {
  company: string;
  submissionId: string;
  result: AxMigrationPublicResult;
  consultationRequested: boolean;
  onRestart: () => void;
}

export function AxDiagnosisResult({
  company,
  submissionId,
  result,
  consultationRequested,
  onRestart,
}: AxDiagnosisResultProps) {
  const t = useTranslations('axDiagnosis.result');
  const [requested, setRequested] = useState(consultationRequested);
  const [sending, setSending] = useState(false);
  const [failed, setFailed] = useState(false);
  const headingRef = useRef<HTMLHeadingElement>(null);
  const acceptedRef = useRef<HTMLOutputElement>(null);

  // The submit button disappears with the form: move focus to the result heading
  useEffect(() => {
    headingRef.current?.focus();
  }, []);

  const primary = result.challenges.primary;
  const otherSelected = CHALLENGE_KEYS.filter(
    (key) => key !== primary && result.challenges.selected.includes(key)
  );

  const requestConsultation = async () => {
    setSending(true);
    setFailed(false);
    try {
      const res = await fetch('/api/diagnostics/ax-migration/consultation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ submissionId }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setRequested(true);
      requestAnimationFrame(() => acceptedRef.current?.focus());
      trackAxEvent('ax_consultation_request', { source: 'result' });
    } catch {
      setFailed(true);
    } finally {
      setSending(false);
    }
  };

  return (
    <section className="space-y-8" aria-labelledby="ax-result-heading">
      <header className="space-y-1">
        <h1
          id="ax-result-heading"
          ref={headingRef}
          tabIndex={-1}
          className="text-3xl font-bold text-gray-900 outline-none"
        >
          {t('title')}
        </h1>
        <p className="text-sm text-gray-600">{t('subtitle', { company })}</p>
      </header>

      {result.needsHearing && (
        <p className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          {t('needsHearing')}
        </p>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        <LevelCard
          label={t('difficulty')}
          level={result.difficulty.level}
          score={result.difficulty.score}
          levelLabel={t(`levels.${result.difficulty.level}`)}
          text={t(`difficultyText.${result.difficulty.level}`)}
          testId="ax-result-difficulty"
        />
        <LevelCard
          label={t('urgency')}
          level={result.urgency.level}
          score={result.urgency.score}
          levelLabel={t(`levels.${result.urgency.level}`)}
          text={t(`urgencyText.${result.urgency.level}`)}
          testId="ax-result-urgency"
        />
      </div>

      <div
        className="space-y-4 rounded-xl border border-gray-200 bg-white p-6"
        data-testid="ax-result-challenge"
      >
        {primary ? (
          <>
            <p className="text-sm font-semibold text-emerald-700">{t('primaryChallenge')}</p>
            <h2 className="text-xl font-bold text-gray-900">{t(`challenges.${primary}.title`)}</h2>
            <p className="text-gray-700">{t(`challenges.${primary}.problem`)}</p>
            <p className="flex items-start gap-2 rounded-lg bg-emerald-50 p-3 text-sm text-emerald-900">
              <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
              <span>{t(`challenges.${primary}.solution`)}</span>
            </p>
          </>
        ) : (
          <>
            <h2 className="text-xl font-bold text-gray-900">{t('noPrimaryChallenge.title')}</h2>
            <p className="text-gray-700">{t('noPrimaryChallenge.body')}</p>
          </>
        )}
        {otherSelected.length > 0 && (
          <div className="space-y-2 pt-2">
            <p className="text-xs font-medium text-gray-600">{t('selectedChallenges')}</p>
            <ul className="flex flex-wrap gap-2">
              {otherSelected.map((key) => (
                <li key={key} className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-700">
                  {t(`challenges.${key}.title`)}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="space-y-4">
        <h2 className="text-lg font-bold text-gray-900">{t('stepsTitle')}</h2>
        <ol className="grid gap-3 sm:grid-cols-4">
          {STEP_KEYS.map((key, index) => (
            <li
              key={key}
              className={cn(
                'rounded-lg border p-4',
                index === 0 ? 'border-emerald-600 bg-emerald-50' : 'border-gray-200 bg-white'
              )}
            >
              <p className="text-xs font-semibold text-gray-600">
                {t('stepLabel', { number: index + 1 })}
              </p>
              <p className="mt-1 font-semibold text-gray-900">{t(`steps.${key}.title`)}</p>
              <p className="mt-2 text-xs leading-relaxed text-gray-600">{t(`steps.${key}.body`)}</p>
            </li>
          ))}
        </ol>
      </div>

      <div className="space-y-4 rounded-xl bg-gray-900 p-6 text-white" data-testid="ax-result-cta">
        {requested ? (
          <output ref={acceptedRef} tabIndex={-1} className="flex items-start gap-3 outline-none">
            <CheckCircle2 className="mt-0.5 h-6 w-6 shrink-0 text-emerald-400" aria-hidden="true" />
            <span className="block">
              <span className="block text-lg font-semibold">{t('cta.accepted')}</span>
              <span className="block text-sm text-gray-300">{t('cta.acceptedBody')}</span>
            </span>
          </output>
        ) : (
          <>
            <h2 className="text-lg font-bold">
              {result.recommendation === 'consultation'
                ? t('cta.consultationTitle')
                : t('cta.informationTitle')}
            </h2>
            <p className="text-sm text-gray-300">{t('cta.body')}</p>
            <Button
              size="lg"
              onClick={requestConsultation}
              disabled={sending}
              className="w-full bg-emerald-500 text-gray-950 hover:bg-emerald-400 sm:w-auto"
            >
              {sending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
                  {t('cta.sending')}
                </>
              ) : (
                t('cta.button')
              )}
            </Button>
            {failed && (
              <p role="alert" className="text-sm text-red-300">
                {t('cta.failed')}
              </p>
            )}
          </>
        )}
      </div>

      <p className="text-xs leading-relaxed text-gray-600">{t('disclaimer')}</p>

      <Button variant="ghost" size="sm" onClick={onRestart}>
        <RotateCcw className="mr-2 h-4 w-4" aria-hidden="true" />
        {t('restart')}
      </Button>
    </section>
  );
}

interface LevelCardProps {
  label: string;
  level: Level;
  score: number;
  levelLabel: string;
  text: string;
  testId: string;
}

function LevelCard({ label, level, score, levelLabel, text, testId }: LevelCardProps) {
  const style = LEVEL_STYLES[level];
  return (
    <div
      className="space-y-3 rounded-xl border border-gray-200 bg-white p-5"
      data-testid={testId}
      data-level={level}
    >
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-gray-600">{label}</p>
        <span className={cn('rounded-full px-3 py-1 text-sm font-bold', style.badge)}>
          {levelLabel}
        </span>
      </div>
      {/* Decorative: the level label above carries the information */}
      <div className="h-2 w-full overflow-hidden rounded-full bg-gray-100" aria-hidden="true">
        <div className={cn('h-full rounded-full', style.bar)} style={{ width: `${score}%` }} />
      </div>
      <p className="text-sm leading-relaxed text-gray-700">{text}</p>
    </div>
  );
}
