/**
 * Diagnostics engine: sections shown only for some answers (migration paths)
 */
import {
  applicableQuestions,
  pruneAnswers,
  shownSections,
  validateAnswers,
} from '@/lib/features/diagnostics/engine';
import type { DiagnosticDefinition, DiagnosticQuestion } from '@/lib/features/diagnostics/types';
import { describe, expect, it } from 'vitest';

const choice = (id: string, values: string[], required = true): DiagnosticQuestion => ({
  id,
  type: 'single',
  required,
  label: { ja: id, en: id },
  options: values.map((value) => ({ value, label: { ja: value, en: value } })),
});

const definition: DiagnosticDefinition = {
  key: 'paths',
  version: 1,
  title: { ja: 't', en: 't' },
  description: { ja: 'd', en: 'd' },
  sections: [
    { id: 'start', title: { ja: 's', en: 's' }, questionIds: ['path'] },
    {
      id: 'a',
      title: { ja: 'a', en: 'a' },
      questionIds: ['a_only', 'shared', 'a_detail'],
      showWhen: { questionId: 'path', anyOf: ['a'] },
    },
    {
      id: 'b',
      title: { ja: 'b', en: 'b' },
      questionIds: ['b_only', 'shared'],
      showWhen: { questionId: 'path', anyOf: ['b'] },
    },
    { id: 'end', title: { ja: 'e', en: 'e' }, questionIds: ['timeline'] },
  ],
  questions: [
    choice('path', ['a', 'b', 'c']),
    choice('a_only', ['x', 'y']),
    choice('b_only', ['x', 'y']),
    choice('shared', ['x', 'y']),
    { ...choice('a_detail', ['x', 'y'], false), detail: true },
    choice('timeline', ['soon', 'later']),
  ],
};

describe('shownSections / applicableQuestions', () => {
  it('shows only the always-on sections before a path is chosen', () => {
    expect(shownSections(definition, {}).map((s) => s.id)).toEqual(['start', 'end']);
  });

  it('adds the section for the chosen path', () => {
    expect(shownSections(definition, { path: 'b' }).map((s) => s.id)).toEqual([
      'start',
      'b',
      'end',
    ]);
  });

  it('lists a question shared by two paths once', () => {
    expect(applicableQuestions(definition, { path: 'a' }).map((q) => q.id)).toEqual([
      'path',
      'a_only',
      'shared',
      'a_detail',
      'timeline',
    ]);
  });

  it('ignores a value the condition does not list', () => {
    expect(shownSections(definition, { path: 'c' }).map((s) => s.id)).toEqual(['start', 'end']);
  });
});

describe('validateAnswers with paths', () => {
  it('requires the questions of the chosen path only', () => {
    const result = validateAnswers(definition, { path: 'a', timeline: 'soon' });
    expect(result.success).toBe(false);
    if (result.success) return;
    expect(result.issues).toEqual([
      { questionId: 'a_only', code: 'required' },
      { questionId: 'shared', code: 'required' },
    ]);
  });

  it('accepts a complete path without its optional detail', () => {
    const result = validateAnswers(definition, {
      path: 'b',
      b_only: 'x',
      shared: 'y',
      timeline: 'later',
    });
    expect(result).toEqual({
      success: true,
      answers: { path: 'b', b_only: 'x', shared: 'y', timeline: 'later' },
    });
  });

  it('rejects answers to questions of another path', () => {
    const result = validateAnswers(definition, {
      path: 'b',
      b_only: 'x',
      shared: 'y',
      a_only: 'x',
      timeline: 'soon',
    });
    expect(result.success).toBe(false);
    if (result.success) return;
    expect(result.issues).toEqual([{ questionId: 'a_only', code: 'not_applicable' }]);
  });

  it('does not open a path for an invalid path answer', () => {
    const result = validateAnswers(definition, { path: 'z', a_only: 'x', timeline: 'soon' });
    expect(result.success).toBe(false);
    if (result.success) return;
    expect(result.issues).toEqual([
      { questionId: 'path', code: 'invalid_option' },
      { questionId: 'a_only', code: 'not_applicable' },
    ]);
  });

  it('keeps optional detail answers on the chosen path', () => {
    const result = validateAnswers(definition, {
      path: 'a',
      a_only: 'x',
      shared: 'x',
      a_detail: 'y',
      timeline: 'soon',
    });
    expect(result.success).toBe(true);
    if (!result.success) return;
    expect(result.answers.a_detail).toBe('y');
  });
});

describe('pruneAnswers', () => {
  it('drops answers left over from a previously chosen path and keeps shared ones', () => {
    expect(
      pruneAnswers(definition, {
        path: 'b',
        a_only: 'x',
        a_detail: 'y',
        shared: 'x',
        b_only: 'y',
        timeline: 'soon',
      })
    ).toEqual({ path: 'b', shared: 'x', b_only: 'y', timeline: 'soon' });
  });
});
