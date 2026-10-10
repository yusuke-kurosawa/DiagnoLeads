import { unknownTechnicalQuestions } from '@/lib/features/diagnostics/ax-migration/technical';
import { accessAnswers, as400Answers } from '@/test/fixtures/ax-migration';
import { describe, expect, it } from 'vitest';

describe('unknownTechnicalQuestions', () => {
  it('lists the technical questions answered "I don\'t know", in question order', () => {
    const ids = unknownTechnicalQuestions({
      ...as400Answers,
      source_docs: 'unknown',
      maintenance: 'unknown',
      as400_languages: ['unknown'],
    }).map((q) => q.id);
    expect(ids).toEqual(['maintenance', 'as400_languages', 'source_docs']);
  });

  it('ignores the respondent, their plans and the optional follow-ups', () => {
    expect(
      unknownTechnicalQuestions({ ...as400Answers, timeline: 'undecided', gaiji: 'unknown' })
    ).toEqual([]);
  });

  it('does not count "I don\'t know" picked together with what is known', () => {
    expect(
      unknownTechnicalQuestions({ ...accessAnswers, access_features: ['vba', 'unknown'] })
    ).toEqual([]);
    const ids = unknownTechnicalQuestions({
      ...accessAnswers,
      access_features: ['unknown'],
    }).map((q) => q.id);
    expect(ids).toEqual(['access_features']);
  });
});
