'use client';

import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ProgressBar } from '@/components/ui/progress-bar';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { axMigrationDefinition } from '@/lib/features/diagnostics/ax-migration/definition';
import type { AxMigrationPublicResult } from '@/lib/features/diagnostics/ax-migration/evaluate';
import type {
  DiagnosticAnswers,
  DiagnosticLocale,
  DiagnosticQuestion,
} from '@/lib/features/diagnostics/types';
import { cn } from '@/lib/utils';
import { ChevronLeft, ChevronRight, Clock, Gauge, Loader2, Target } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { useEffect, useRef, useState } from 'react';
import { AxDiagnosisResult } from './ax-diagnosis-result';
import { trackAxEvent } from './tracking';

const definition = axMigrationDefinition;
const CONTACT_STEP = definition.sections.length;

interface ContactState {
  company: string;
  name: string;
  email: string;
  phone: string;
  department: string;
}

interface SubmissionResponse {
  submissionId: string;
  consultationRequested: boolean;
  result: AxMigrationPublicResult;
}

interface AxDiagnosisFlowProps {
  locale: DiagnosticLocale;
  privacyPolicyUrl?: string;
}

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/** Match the checkbox accent to the radio buttons (brand green of the AX pamphlet) */
const CHECKBOX_CLASS =
  'border-gray-500 focus-visible:ring-emerald-600 data-[state=checked]:border-emerald-600 data-[state=checked]:bg-emerald-600';

/** Read UTM / referral parameters once on the landing page */
function readTracking(): Record<string, string> {
  if (typeof window === 'undefined') return {};
  const params = new URLSearchParams(window.location.search);
  const pick = (key: string) => params.get(key)?.slice(0, 200) || undefined;
  const tracking: Record<string, string | undefined> = {
    utmSource: pick('utm_source'),
    utmMedium: pick('utm_medium'),
    utmCampaign: pick('utm_campaign'),
    utmContent: pick('utm_content'),
    utmTerm: pick('utm_term'),
    ref: params.get('ref')?.slice(0, 100) || undefined,
    referrer: document.referrer ? document.referrer.slice(0, 500) : undefined,
    landingPath: window.location.pathname.slice(0, 500),
  };
  return Object.fromEntries(
    Object.entries(tracking).filter((entry): entry is [string, string] => Boolean(entry[1]))
  );
}

export function AxDiagnosisFlow({ locale, privacyPolicyUrl }: AxDiagnosisFlowProps) {
  const t = useTranslations('axDiagnosis');
  const [stage, setStage] = useState<'intro' | 'questions' | 'result'>('intro');
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<DiagnosticAnswers>({});
  const [contact, setContact] = useState<ContactState>({
    company: '',
    name: '',
    email: '',
    phone: '',
    department: '',
  });
  const [consultation, setConsultation] = useState(false);
  const [consent, setConsent] = useState(false);
  const [honeypot, setHoneypot] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [response, setResponse] = useState<SubmissionResponse | null>(null);
  const tracking = useRef<Record<string, string>>({});
  const topRef = useRef<HTMLDivElement>(null);
  const stepHeadingRef = useRef<HTMLHeadingElement>(null);

  // Move focus to the step heading on every step change so keyboard and screen reader
  // users start at the new questions instead of the bottom of the page
  // biome-ignore lint/correctness/useExhaustiveDependencies: `step` is the trigger (refocus on every step)
  useEffect(() => {
    if (stage === 'questions') stepHeadingRef.current?.focus();
  }, [stage, step]);

  // Warn before leaving the page (e.g. the browser back button) with unsent answers
  useEffect(() => {
    if (stage !== 'questions' || Object.keys(answers).length === 0) return;
    const warn = (event: BeforeUnloadEvent) => {
      event.preventDefault();
      event.returnValue = '';
    };
    window.addEventListener('beforeunload', warn);
    return () => window.removeEventListener('beforeunload', warn);
  }, [stage, answers]);

  useEffect(() => {
    tracking.current = readTracking();
  }, []);

  const scrollToTop = () => topRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });

  /** Bring the first invalid field into view and focus it */
  const focusFirstError = (elementId: string) => {
    requestAnimationFrame(() => {
      const element = document.getElementById(elementId);
      if (!element) return;
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      const target =
        element instanceof HTMLInputElement || element instanceof HTMLButtonElement
          ? element
          : element.closest('fieldset')?.querySelector<HTMLElement>('button, input');
      target?.focus({ preventScroll: true });
    });
  };

  const questionById = (id: string) =>
    definition.questions.find((q) => q.id === id) as DiagnosticQuestion;

  const setSingle = (questionId: string, value: string) => {
    setAnswers((prev) => ({ ...prev, [questionId]: value }));
    setErrors((prev) => ({ ...prev, [questionId]: '' }));
  };

  const toggleMultiple = (question: DiagnosticQuestion, value: string, checked: boolean) => {
    setAnswers((prev) => {
      const current = Array.isArray(prev[question.id]) ? (prev[question.id] as string[]) : [];
      const exclusive = question.exclusiveOptions ?? [];
      let next: string[];
      if (!checked) {
        next = current.filter((v) => v !== value);
      } else if (exclusive.includes(value)) {
        next = [value];
      } else {
        next = [...current.filter((v) => !exclusive.includes(v)), value];
      }
      return { ...prev, [question.id]: next };
    });
    setErrors((prev) => ({ ...prev, [question.id]: '' }));
  };

  const validateSection = (sectionIndex: number): boolean => {
    const section = definition.sections[sectionIndex];
    const nextErrors: Record<string, string> = {};
    for (const id of section.questionIds) {
      const question = questionById(id);
      const value = answers[id];
      const empty = value === undefined || (Array.isArray(value) && value.length === 0);
      if (question.required && empty) nextErrors[id] = t('errors.required');
    }
    setErrors(nextErrors);
    const first = section.questionIds.find((id) => nextErrors[id]);
    if (first) focusFirstError(`q-${first}`);
    return first === undefined;
  };

  const validateContact = (): boolean => {
    const nextErrors: Record<string, string> = {};
    if (!contact.company.trim()) nextErrors.company = t('errors.contactRequired');
    if (!contact.name.trim()) nextErrors.name = t('errors.contactRequired');
    if (!contact.email.trim()) nextErrors.email = t('errors.contactRequired');
    else if (!EMAIL_PATTERN.test(contact.email.trim())) nextErrors.email = t('errors.email');
    if (!consent) nextErrors.consent = t('errors.consent');
    setErrors(nextErrors);
    const first = ['company', 'name', 'email', 'consent'].find((key) => nextErrors[key]);
    if (first) focusFirstError(first === 'consent' ? 'consent' : `contact-${first}`);
    return first === undefined;
  };

  const start = () => {
    setStage('questions');
    setStep(0);
    trackAxEvent('ax_diagnosis_start');
    scrollToTop();
  };

  const goNext = () => {
    if (!validateSection(step)) return;
    setStep((s) => s + 1);
    scrollToTop();
  };

  const goBack = () => {
    setErrors({});
    if (step === 0) {
      setStage('intro');
    } else {
      setStep((s) => s - 1);
    }
    scrollToTop();
  };

  const submit = async () => {
    if (!validateContact()) return;
    setSubmitting(true);
    setSubmitError(null);
    try {
      const res = await fetch('/api/diagnostics/ax-migration', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          answers,
          contact: {
            company: contact.company.trim(),
            name: contact.name.trim(),
            email: contact.email.trim(),
            phone: contact.phone.trim() || undefined,
            department: contact.department.trim() || undefined,
          },
          privacyConsent: consent,
          consultationRequested: consultation,
          tracking: tracking.current,
          locale,
          website: honeypot || undefined,
        }),
      });

      if (res.status === 429) {
        setSubmitError(t('errors.rateLimited'));
        return;
      }
      const json = await res.json().catch(() => null);
      if (!res.ok || !json) {
        // Jump back to the first section with an invalid answer, if any
        const issues: { questionId: string }[] = json?.issues ?? [];
        const sectionIndex = definition.sections.findIndex((section) =>
          issues.some((issue) => section.questionIds.includes(issue.questionId))
        );
        if (sectionIndex >= 0) {
          setStep(sectionIndex);
          setErrors(
            Object.fromEntries(issues.map((issue) => [issue.questionId, t('errors.required')]))
          );
          scrollToTop();
        }
        setSubmitError(t('errors.submit'));
        return;
      }

      setResponse(json as SubmissionResponse);
      setStage('result');
      trackAxEvent('ax_diagnosis_complete', {
        difficulty: json.result.difficulty.level,
        urgency: json.result.urgency.level,
        primary_challenge: json.result.challenges.primary,
        consultation_requested: consultation,
      });
      if (consultation) trackAxEvent('ax_consultation_request', { source: 'form' });
      scrollToTop();
    } catch {
      setSubmitError(t('errors.submit'));
    } finally {
      setSubmitting(false);
    }
  };

  const restart = () => {
    setAnswers({});
    setResponse(null);
    setConsultation(false);
    setConsent(false);
    setErrors({});
    setSubmitError(null);
    setStage('intro');
    setStep(0);
    scrollToTop();
  };

  return (
    <div ref={topRef} className="mx-auto w-full max-w-3xl px-4 py-10 sm:py-14">
      {stage === 'intro' && (
        <section className="space-y-8" aria-labelledby="ax-intro-heading">
          <div className="space-y-4">
            <p className="text-sm font-semibold tracking-wide text-emerald-700">
              {t('intro.eyebrow')}
            </p>
            <h1
              id="ax-intro-heading"
              className="text-3xl font-bold leading-tight text-gray-900 sm:text-4xl"
            >
              {t('intro.headline')}
            </h1>
            <p className="text-lg text-gray-600">{t('intro.lead')}</p>
          </div>

          <ul className="grid gap-3 sm:grid-cols-3">
            {[
              { icon: Clock, text: t('intro.points.time') },
              { icon: Gauge, text: t('intro.points.difficulty') },
              { icon: Target, text: t('intro.points.challenge') },
            ].map(({ icon: Icon, text }) => (
              <li
                key={text}
                className="flex items-center gap-3 rounded-lg border border-gray-200 bg-white p-4"
              >
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-emerald-50 text-emerald-700">
                  <Icon className="h-5 w-5" aria-hidden="true" />
                </span>
                <span className="text-sm font-medium text-gray-800">{text}</span>
              </li>
            ))}
          </ul>

          <div className="space-y-3">
            <Button
              size="lg"
              onClick={start}
              className="w-full bg-emerald-700 hover:bg-emerald-800 sm:w-auto"
            >
              {t('intro.start')}
              <ChevronRight className="ml-1 h-4 w-4" aria-hidden="true" />
            </Button>
            <p className="text-xs text-gray-500">{t('intro.note')}</p>
          </div>
        </section>
      )}

      {stage === 'questions' && (
        <section className="space-y-8" aria-labelledby="ax-step-heading">
          <div className="space-y-2">
            <div className="flex items-center justify-between gap-3 text-sm text-gray-600">
              <span aria-live="polite">
                {t('progress', { current: step + 1, total: CONTACT_STEP + 1 })}
              </span>
              <h2
                id="ax-step-heading"
                ref={stepHeadingRef}
                tabIndex={-1}
                className="text-base font-semibold text-gray-900 outline-none"
              >
                {step < CONTACT_STEP ? definition.sections[step].title[locale] : t('contactStep')}
              </h2>
            </div>
            <ProgressBar
              value={((step + 1) / (CONTACT_STEP + 1)) * 100}
              color="emerald"
              className="h-2"
            />
          </div>

          {step < CONTACT_STEP ? (
            <div className="space-y-8">
              {definition.sections[step].questionIds.map((id) => {
                const question = questionById(id);
                return (
                  <QuestionField
                    key={id}
                    question={question}
                    locale={locale}
                    value={answers[id]}
                    error={errors[id]}
                    requiredLabel={t('required')}
                    multipleHint={t('multipleHint')}
                    onSingle={(value) => setSingle(id, value)}
                    onToggle={(value, checked) => toggleMultiple(question, value, checked)}
                  />
                );
              })}
            </div>
          ) : (
            <ContactFields
              contact={contact}
              errors={errors}
              consultation={consultation}
              consent={consent}
              honeypot={honeypot}
              privacyPolicyUrl={privacyPolicyUrl}
              onContact={(field, value) => {
                setContact((prev) => ({ ...prev, [field]: value }));
                setErrors((prev) => ({ ...prev, [field]: '' }));
              }}
              onConsultation={setConsultation}
              onConsent={(value) => {
                setConsent(value);
                setErrors((prev) => ({ ...prev, consent: '' }));
              }}
              onHoneypot={setHoneypot}
            />
          )}

          {submitError && (
            <p role="alert" className="rounded-md bg-red-50 p-3 text-sm text-red-700">
              {submitError}
            </p>
          )}

          <div className="flex items-center justify-between gap-3">
            <Button key="back" variant="outline" onClick={goBack} disabled={submitting}>
              <ChevronLeft className="mr-1 h-4 w-4" aria-hidden="true" />
              {t('back')}
            </Button>
            {step < CONTACT_STEP ? (
              <Button key="next" onClick={goNext} className="bg-emerald-700 hover:bg-emerald-800">
                {t('next')}
                <ChevronRight className="ml-1 h-4 w-4" aria-hidden="true" />
              </Button>
            ) : (
              <Button
                key="submit"
                onClick={submit}
                disabled={submitting}
                className="bg-emerald-700 hover:bg-emerald-800"
              >
                {submitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
                    {t('submitting')}
                  </>
                ) : (
                  t('submit')
                )}
              </Button>
            )}
          </div>
        </section>
      )}

      {stage === 'result' && response && (
        <AxDiagnosisResult
          company={contact.company.trim()}
          submissionId={response.submissionId}
          result={response.result}
          consultationRequested={response.consultationRequested}
          onRestart={restart}
        />
      )}

      <p className="mt-12 text-center text-xs text-gray-500">{t('operator')}</p>
    </div>
  );
}

interface QuestionFieldProps {
  question: DiagnosticQuestion;
  locale: DiagnosticLocale;
  value: string | string[] | undefined;
  error?: string;
  requiredLabel: string;
  multipleHint: string;
  onSingle: (value: string) => void;
  onToggle: (value: string, checked: boolean) => void;
}

function QuestionField({
  question,
  locale,
  value,
  error,
  requiredLabel,
  multipleHint,
  onSingle,
  onToggle,
}: QuestionFieldProps) {
  const legendId = `q-${question.id}`;
  const optionClass = (selected: boolean) =>
    cn(
      'flex cursor-pointer items-start gap-3 rounded-lg border p-3 text-sm transition-colors',
      selected
        ? 'border-emerald-600 bg-emerald-50 text-gray-900'
        : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400 hover:bg-gray-50'
    );

  return (
    <fieldset
      className="space-y-3"
      aria-describedby={
        [question.type === 'multiple' ? `${legendId}-hint` : '', error ? `${legendId}-error` : '']
          .filter(Boolean)
          .join(' ') || undefined
      }
    >
      <legend id={legendId} className="mb-1 text-base font-semibold text-gray-900">
        {question.label[locale]}
        {question.required && (
          <span className="ml-2 rounded bg-gray-100 px-1.5 py-0.5 text-xs font-normal text-gray-600">
            {requiredLabel}
          </span>
        )}
      </legend>
      {question.type === 'multiple' && (
        <p id={`${legendId}-hint`} className="text-xs text-gray-600">
          {multipleHint}
        </p>
      )}

      {question.type === 'single' ? (
        <RadioGroup
          value={typeof value === 'string' ? value : ''}
          onValueChange={onSingle}
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
                <RadioGroupItem id={id} value={option.value} className="mt-0.5 border-gray-500" />
                <span>{option.label[locale]}</span>
              </Label>
            );
          })}
        </RadioGroup>
      ) : (
        <div className="grid gap-2">
          {question.options.map((option) => {
            const id = `${question.id}-${option.value}`;
            const checked = Array.isArray(value) && value.includes(option.value);
            return (
              <Label key={option.value} htmlFor={id} className={optionClass(checked)}>
                <Checkbox
                  id={id}
                  checked={checked}
                  onCheckedChange={(state) => onToggle(option.value, state === true)}
                  className={cn('mt-0.5', CHECKBOX_CLASS)}
                />
                <span>{option.label[locale]}</span>
              </Label>
            );
          })}
        </div>
      )}

      {error && (
        <p id={`${legendId}-error`} className="text-sm text-red-600">
          {error}
        </p>
      )}
    </fieldset>
  );
}

interface ContactFieldsProps {
  contact: ContactState;
  errors: Record<string, string>;
  consultation: boolean;
  consent: boolean;
  honeypot: string;
  privacyPolicyUrl?: string;
  onContact: (field: keyof ContactState, value: string) => void;
  onConsultation: (value: boolean) => void;
  onConsent: (value: boolean) => void;
  onHoneypot: (value: string) => void;
}

function ContactFields({
  contact,
  errors,
  consultation,
  consent,
  honeypot,
  privacyPolicyUrl,
  onContact,
  onConsultation,
  onConsent,
  onHoneypot,
}: ContactFieldsProps) {
  const t = useTranslations('axDiagnosis');
  const fields: {
    key: keyof ContactState;
    type: string;
    required: boolean;
    autoComplete: string;
  }[] = [
    { key: 'company', type: 'text', required: true, autoComplete: 'organization' },
    { key: 'name', type: 'text', required: true, autoComplete: 'name' },
    { key: 'email', type: 'email', required: true, autoComplete: 'email' },
    { key: 'phone', type: 'tel', required: false, autoComplete: 'tel' },
    { key: 'department', type: 'text', required: false, autoComplete: 'organization-title' },
  ];

  return (
    <div className="space-y-6">
      <p className="text-sm text-gray-600">{t('contact.description')}</p>

      <div className="grid gap-4 sm:grid-cols-2">
        {fields.map(({ key, type, required, autoComplete }) => (
          <div key={key} className={cn('space-y-1.5', key === 'email' && 'sm:col-span-2')}>
            <Label htmlFor={`contact-${key}`} className="text-sm font-medium text-gray-800">
              {t(`contact.${key}`)}
              <span className="ml-2 text-xs font-normal text-gray-500">
                {required ? t('required') : t('optional')}
              </span>
            </Label>
            <Input
              id={`contact-${key}`}
              type={type}
              autoComplete={autoComplete}
              value={contact[key]}
              onChange={(e) => onContact(key, e.target.value)}
              aria-invalid={Boolean(errors[key])}
              aria-required={required}
              aria-describedby={errors[key] ? `contact-${key}-error` : undefined}
              className={cn(errors[key] && 'border-red-500')}
            />
            {errors[key] && (
              <p id={`contact-${key}-error`} className="text-sm text-red-600">
                {errors[key]}
              </p>
            )}
          </div>
        ))}
      </div>

      {/* Honeypot: hidden from people, filled by bots */}
      <div aria-hidden="true" className="absolute -left-[9999px] h-0 w-0 overflow-hidden">
        <label htmlFor="contact-website">Website</label>
        <input
          id="contact-website"
          tabIndex={-1}
          autoComplete="off"
          value={honeypot}
          onChange={(e) => onHoneypot(e.target.value)}
        />
      </div>

      <div className="space-y-3 rounded-lg border border-emerald-200 bg-emerald-50/60 p-4">
        <Label htmlFor="consultation" className="flex cursor-pointer items-start gap-3">
          <Checkbox
            id="consultation"
            checked={consultation}
            onCheckedChange={(state) => onConsultation(state === true)}
            className={cn('mt-0.5', CHECKBOX_CLASS)}
          />
          <span>
            <span className="block text-sm font-medium text-gray-900">
              {t('contact.consultation')}
            </span>
            <span className="block text-xs text-gray-600">{t('contact.consultationHint')}</span>
          </span>
        </Label>
      </div>

      <div className="space-y-2">
        <p className="text-xs text-gray-500">
          {t('contact.consentNotice')}
          {privacyPolicyUrl && (
            <>
              {' '}
              <a
                href={privacyPolicyUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-emerald-700 underline"
              >
                {t('contact.privacyPolicy')}
              </a>
            </>
          )}
        </p>
        <Label htmlFor="consent" className="flex cursor-pointer items-center gap-3">
          <Checkbox
            id="consent"
            checked={consent}
            onCheckedChange={(state) => onConsent(state === true)}
            aria-invalid={Boolean(errors.consent)}
            aria-describedby={errors.consent ? 'consent-error' : undefined}
            className={CHECKBOX_CLASS}
          />
          <span className="text-sm text-gray-800">{t('contact.consent')}</span>
        </Label>
        {errors.consent && (
          <p id="consent-error" className="text-sm text-red-600">
            {errors.consent}
          </p>
        )}
      </div>
    </div>
  );
}
