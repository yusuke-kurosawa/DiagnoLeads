import type {
  AnswerValidationIssue,
  AnswerValidationResult,
  DiagnosticAnswers,
  DiagnosticDefinition,
  DiagnosticQuestion,
  DiagnosticSection,
} from './types';

/**
 * Sections shown for the given answers, in order.
 * A condition may only refer to a question in an earlier section, so one pass is enough.
 */
export function shownSections(
  definition: DiagnosticDefinition,
  answers: Record<string, unknown>
): DiagnosticSection[] {
  const shown: DiagnosticSection[] = [];
  const applicable = new Set<string>();
  for (const section of definition.sections) {
    const condition = section.showWhen;
    if (condition) {
      const value = answers[condition.questionId];
      const met =
        applicable.has(condition.questionId) &&
        typeof value === 'string' &&
        condition.anyOf.includes(value);
      if (!met) continue;
    }
    shown.push(section);
    for (const id of section.questionIds) applicable.add(id);
  }
  return shown;
}

/** Questions that apply to the given answers (each once, in the order they are shown) */
export function applicableQuestions(
  definition: DiagnosticDefinition,
  answers: Record<string, unknown>
): DiagnosticQuestion[] {
  const byId = new Map(definition.questions.map((q) => [q.id, q]));
  const ids = new Set(shownSections(definition, answers).flatMap((s) => s.questionIds));
  return [...ids].flatMap((id) => byId.get(id) ?? []);
}

/** Drop answers to questions that no longer apply (e.g. after switching the migration path) */
export function pruneAnswers(
  definition: DiagnosticDefinition,
  answers: DiagnosticAnswers
): DiagnosticAnswers {
  const ids = new Set(applicableQuestions(definition, answers).map((q) => q.id));
  return Object.fromEntries(Object.entries(answers).filter(([id]) => ids.has(id)));
}

/**
 * Validate raw answers against a definition.
 * Unknown questions and options are rejected so that stored answers always match the definition.
 * Only questions in shown sections apply: they are required as defined, and answers to the
 * others are rejected (the client drops them when the respondent switches paths).
 */
export function validateAnswers(
  definition: DiagnosticDefinition,
  raw: Record<string, unknown>
): AnswerValidationResult {
  const issues: AnswerValidationIssue[] = [];
  const candidates: DiagnosticAnswers = {};
  const known = new Set(definition.questions.map((q) => q.id));

  for (const questionId of Object.keys(raw)) {
    if (!known.has(questionId)) issues.push({ questionId, code: 'unknown_question' });
  }

  const empty = new Set<string>();
  for (const question of definition.questions) {
    const value = raw[question.id];
    const allowed = new Set(question.options.map((o) => o.value));
    const isEmpty =
      value === undefined ||
      value === null ||
      value === '' ||
      (Array.isArray(value) && value.length === 0);

    if (isEmpty) {
      empty.add(question.id);
      continue;
    }

    if (question.type === 'single') {
      if (typeof value !== 'string') {
        issues.push({ questionId: question.id, code: 'invalid_type' });
      } else if (!allowed.has(value)) {
        issues.push({ questionId: question.id, code: 'invalid_option' });
      } else {
        candidates[question.id] = value;
      }
      continue;
    }

    if (!Array.isArray(value) || value.some((v) => typeof v !== 'string')) {
      issues.push({ questionId: question.id, code: 'invalid_type' });
      continue;
    }
    const selected = [...new Set(value as string[])];
    if (selected.some((v) => !allowed.has(v))) {
      issues.push({ questionId: question.id, code: 'invalid_option' });
      continue;
    }
    const exclusive = question.exclusiveOptions ?? [];
    if (selected.length > 1 && selected.some((v) => exclusive.includes(v))) {
      issues.push({ questionId: question.id, code: 'exclusive_conflict' });
      continue;
    }
    candidates[question.id] = selected;
  }

  // Applicability depends on the (valid) answers to the questions that select a path
  const applicable = new Set(applicableQuestions(definition, candidates).map((q) => q.id));
  const answers: DiagnosticAnswers = {};
  for (const question of definition.questions) {
    if (!applicable.has(question.id)) {
      if (question.id in candidates)
        issues.push({ questionId: question.id, code: 'not_applicable' });
      continue;
    }
    if (empty.has(question.id)) {
      if (question.required) issues.push({ questionId: question.id, code: 'required' });
      continue;
    }
    if (question.id in candidates) answers[question.id] = candidates[question.id];
  }

  return issues.length > 0 ? { success: false, issues } : { success: true, answers };
}

/** Read a single-choice answer */
export function single(answers: DiagnosticAnswers, questionId: string): string | undefined {
  const value = answers[questionId];
  return typeof value === 'string' ? value : undefined;
}

/** Read a multiple-choice answer (always an array) */
export function multiple(answers: DiagnosticAnswers, questionId: string): string[] {
  const value = answers[questionId];
  return Array.isArray(value) ? value : [];
}

/** Clamp a number into 0..100 and round it */
export function toPercent(value: number, max: number): number {
  if (max <= 0) return 0;
  return Math.max(0, Math.min(100, Math.round((value / max) * 100)));
}
