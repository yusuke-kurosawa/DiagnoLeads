import { AX_MIGRATION_CONFIG } from '@/lib/features/diagnostics/ax-migration/config';
import { axMigrationDefinition } from '@/lib/features/diagnostics/ax-migration/definition';
import {
  evaluateAxMigration,
  toPublicResult,
} from '@/lib/features/diagnostics/ax-migration/evaluate';
import { validateAnswers } from '@/lib/features/diagnostics/engine';
import type { DiagnosticAnswers } from '@/lib/features/diagnostics/types';
import { describe, expect, it } from 'vitest';

/** Typical target: mid-size manufacturer on AS/400 with key-person risk */
const typicalAs400: DiagnosticAnswers = {
  industry: 'manufacturing',
  revenue: '10b_30b',
  system: 'as400',
  languages: ['rpg', 'cl'],
  years: 'gte20',
  programs: '500_2000',
  integrations: 'some',
  maintenance: 'few',
  documents: 'partial',
  challenges: ['people', 'cost'],
  timeline: '1_2y',
  role: 'it_manager',
};

const answer = (overrides: Partial<DiagnosticAnswers>): DiagnosticAnswers => ({
  ...typicalAs400,
  ...overrides,
});

describe('axMigrationDefinition', () => {
  it('places every question in exactly one section', () => {
    const sectionIds = axMigrationDefinition.sections.flatMap((s) => s.questionIds);
    const questionIds = axMigrationDefinition.questions.map((q) => q.id);
    expect([...sectionIds].sort()).toEqual([...questionIds].sort());
    expect(new Set(sectionIds).size).toBe(sectionIds.length);
  });

  it('has 12 questions with ja and en labels', () => {
    expect(axMigrationDefinition.questions).toHaveLength(12);
    for (const question of axMigrationDefinition.questions) {
      expect(question.label.ja).not.toBe('');
      expect(question.label.en).not.toBe('');
      for (const option of question.options) {
        expect(option.label.ja).not.toBe('');
        expect(option.label.en).not.toBe('');
      }
    }
  });

  it('accepts the typical answers', () => {
    expect(validateAnswers(axMigrationDefinition, typicalAs400).success).toBe(true);
  });
});

describe('evaluateAxMigration', () => {
  describe('MQL (業種 × システム × 行動)', () => {
    it('qualifies a manufacturer on AS/400', () => {
      const result = evaluateAxMigration(typicalAs400);
      expect(result.mql).toEqual({
        qualified: true,
        criteria: { industry: true, system: true, action: true },
      });
    });

    it('qualifies a distributor on a mainframe', () => {
      const result = evaluateAxMigration(answer({ industry: 'distribution', system: 'mainframe' }));
      expect(result.mql.qualified).toBe(true);
    });

    it('does not qualify other industries', () => {
      const result = evaluateAxMigration(answer({ industry: 'other' }));
      expect(result.mql.qualified).toBe(false);
      expect(result.mql.criteria.industry).toBe(false);
    });

    it('does not qualify packaged / cloud systems', () => {
      const result = evaluateAxMigration(answer({ system: 'package', languages: ['other'] }));
      expect(result.mql.criteria.system).toBe(false);
    });

    it('estimates a legacy system from RPG / COBOL when the platform is unknown（推定でも可）', () => {
      const result = evaluateAxMigration(answer({ system: 'unknown', languages: ['cobol'] }));
      expect(result.mql.criteria.system).toBe(true);
      expect(result.targetSystem).toBe('other_legacy');
    });

    it('does not count the diagnosis as an action when the config says so', () => {
      const result = evaluateAxMigration(typicalAs400, {
        ...AX_MIGRATION_CONFIG,
        countWebDiagnosisAsMqlAction: false,
      });
      expect(result.mql.qualified).toBe(false);
      expect(result.mql.criteria.action).toBe(false);
    });
  });

  describe('SQL signals (①②必須＋③④のいずれか)', () => {
    it('marks a candidate when system and problem are known and timeline is visible', () => {
      const { sqlSignals } = evaluateAxMigration(answer({ role: 'business' }));
      expect(sqlSignals).toMatchObject({
        systemKnown: true,
        problemAware: true,
        timelineVisible: true,
        decisionAccess: false,
        candidate: true,
      });
    });

    it('marks a candidate through decision access when the timeline is undecided', () => {
      const { sqlSignals } = evaluateAxMigration(answer({ timeline: 'undecided', role: 'executive' }));
      expect(sqlSignals.timelineVisible).toBe(false);
      expect(sqlSignals.candidate).toBe(true);
    });

    it('requires the system to be known', () => {
      const { sqlSignals } = evaluateAxMigration(answer({ programs: 'unknown' }));
      expect(sqlSignals.systemKnown).toBe(false);
      expect(sqlSignals.candidate).toBe(false);
    });

    it('requires awareness of people / cost / end-of-support problems', () => {
      const { sqlSignals } = evaluateAxMigration(answer({ challenges: ['agility', 'data'] }));
      expect(sqlSignals.problemAware).toBe(false);
      expect(sqlSignals.candidate).toBe(false);
    });

    it('is not a candidate with neither timeline nor decision access', () => {
      const { sqlSignals } = evaluateAxMigration(answer({ timeline: 'undecided', role: 'business' }));
      expect(sqlSignals.candidate).toBe(false);
    });
  });

  describe('difficulty（移行難易度の目安）', () => {
    it('is medium for the typical AS/400 case', () => {
      const { difficulty } = evaluateAxMigration(typicalAs400);
      expect(difficulty.level).toBe('medium');
      expect(difficulty.score).toBe(63); // (20+15+15+9+8+5) / 115
    });

    it('is high for a large mainframe system without documents', () => {
      const { difficulty } = evaluateAxMigration(
        answer({
          system: 'mainframe',
          languages: ['cobol'],
          programs: 'gte5000',
          integrations: 'many',
          documents: 'none',
        })
      );
      expect(difficulty.level).toBe('high');
    });

    it('is low for a small packaged system', () => {
      const { difficulty } = evaluateAxMigration(
        answer({
          system: 'package',
          languages: ['other'],
          years: 'lt10',
          programs: 'lt500',
          integrations: 'few',
          documents: 'updated',
        })
      );
      expect(difficulty.level).toBe('low');
    });

    it('caps language points so selecting many languages does not dominate', () => {
      const few = evaluateAxMigration(answer({ languages: ['rpg', 'cobol'] }));
      const many = evaluateAxMigration(answer({ languages: ['rpg', 'cobol', 'cl', 'other'] }));
      expect(many.difficulty.score).toBe(few.difficulty.score);
    });
  });

  describe('urgency（緊急度）', () => {
    it('is high when the only maintainer is leaving and support is ending', () => {
      const { urgency } = evaluateAxMigration(
        answer({ maintenance: 'none', challenges: ['eos'], timeline: 'within_1y' })
      );
      expect(urgency.level).toBe('high');
      expect(urgency.score).toBe(100);
    });

    it('is low with an in-house team, a young system and no plan', () => {
      const { urgency } = evaluateAxMigration(
        answer({ maintenance: 'team', years: 'lt10', timeline: 'undecided', challenges: ['data'] })
      );
      expect(urgency.level).toBe('low');
      expect(urgency.score).toBe(0);
    });
  });

  describe('primary challenge（ヒト／カネ／モノ／情報）', () => {
    it('prefers people when key-person risk backs it up', () => {
      expect(evaluateAxMigration(typicalAs400).challenges.primary).toBe('people');
    });

    it('picks cost when the vendor dependency and end of support back it up', () => {
      const result = evaluateAxMigration(
        answer({ maintenance: 'vendor', challenges: ['people', 'cost', 'eos'] })
      );
      expect(result.challenges.scores).toMatchObject({ people: 3, cost: 5 });
      expect(result.challenges.primary).toBe('cost');
    });

    it('breaks ties in the order people, cost, agility, data', () => {
      const result = evaluateAxMigration(
        answer({ maintenance: 'team', challenges: ['data', 'agility'] })
      );
      expect(result.challenges.primary).toBe('agility');
    });
  });

  describe('lead score and recommendation', () => {
    it('stays within 0-100', () => {
      const best = evaluateAxMigration(
        answer({ maintenance: 'none', challenges: ['eos', 'people'], timeline: 'within_1y', role: 'executive' })
      );
      const worst = evaluateAxMigration(
        answer({
          industry: 'other',
          revenue: 'lt5b',
          system: 'package',
          languages: ['other'],
          maintenance: 'team',
          years: 'lt10',
          challenges: ['data'],
          timeline: 'undecided',
          role: 'other',
        })
      );
      expect(best.leadScore).toBeLessThanOrEqual(100);
      expect(best.leadScore).toBeGreaterThan(80);
      expect(worst.leadScore).toBeGreaterThanOrEqual(0);
      expect(worst.leadScore).toBeLessThan(30);
    });

    it('recommends a consultation to MQLs and information otherwise', () => {
      expect(evaluateAxMigration(typicalAs400).recommendation).toBe('consultation');
      const info = evaluateAxMigration(
        answer({
          industry: 'other',
          system: 'package',
          languages: ['other'],
          maintenance: 'team',
          challenges: ['data'],
          timeline: 'undecided',
        })
      );
      expect(info.recommendation).toBe('information');
    });

    it('hides sales-only fields from the public result', () => {
      const publicResult = toPublicResult(evaluateAxMigration(typicalAs400));
      expect(publicResult).not.toHaveProperty('leadScore');
      expect(publicResult).not.toHaveProperty('mql');
      expect(publicResult).not.toHaveProperty('sqlSignals');
    });
  });
});
