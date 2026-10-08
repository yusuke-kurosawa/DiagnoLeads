import type {
  AnswerValidationIssue,
  AnswerValidationResult,
  DiagnosticAnswers,
  DiagnosticDefinition,
} from './types';

/**
 * Validate raw answers against a definition.
 * Unknown questions and options are rejected so that stored answers always match the definition.
 */
export function validateAnswers(
  definition: DiagnosticDefinition,
  raw: Record<string, unknown>
): AnswerValidationResult {
  const issues: AnswerValidationIssue[] = [];
  const answers: DiagnosticAnswers = {};
  const known = new Set(definition.questions.map((q) => q.id));

  for (const questionId of Object.keys(raw)) {
    if (!known.has(questionId)) issues.push({ questionId, code: 'unknown_question' });
  }

  for (const question of definition.questions) {
    const value = raw[question.id];
    const allowed = new Set(question.options.map((o) => o.value));
    const isEmpty =
      value === undefined ||
      value === null ||
      value === '' ||
      (Array.isArray(value) && value.length === 0);

    if (isEmpty) {
      if (question.required) issues.push({ questionId: question.id, code: 'required' });
      continue;
    }

    if (question.type === 'single') {
      if (typeof value !== 'string') {
        issues.push({ questionId: question.id, code: 'invalid_type' });
      } else if (!allowed.has(value)) {
        issues.push({ questionId: question.id, code: 'invalid_option' });
      } else {
        answers[question.id] = value;
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
    answers[question.id] = selected;
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
