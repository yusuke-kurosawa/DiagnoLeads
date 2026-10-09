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
    const countDiagnosis = { ...AX_MIGRATION_CONFIG, countWebDiagnosisAsMqlAction: true };

    it('hands a manufacturer on AS/400 to marketing as an MQL candidate by default', () => {
      const result = evaluateAxMigration(typicalAs400);
      expect(result.mql).toEqual({
        qualified: false,
        candidate: true,
        criteria: { industry: true, system: true, action: false },
      });
    });

    it('qualifies automatically only when the diagnosis counts as an action (config)', () => {
      expect(evaluateAxMigration(typicalAs400, countDiagnosis).mql.qualified).toBe(true);
      expect(
        evaluateAxMigration(answer({ industry: 'distribution', system: 'mainframe' }), countDiagnosis)
          .mql.qualified
      ).toBe(true);
    });

    it('does not make other industries a candidate', () => {
      const result = evaluateAxMigration(answer({ industry: 'other' }), countDiagnosis);
      expect(result.mql.candidate).toBe(false);
      expect(result.mql.qualified).toBe(false);
    });

    it('does not make packaged / cloud systems a candidate', () => {
      const result = evaluateAxMigration(answer({ system: 'package', languages: ['other'] }));
      expect(result.mql.criteria.system).toBe(false);
    });

    it('estimates a legacy system from RPG / COBOL when the platform is unknown（推定でも可）', () => {
      const result = evaluateAxMigration(answer({ system: 'unknown', languages: ['cobol'] }));
      expect(result.mql.criteria.system).toBe(true);
      expect(result.targetSystem).toBe('other_legacy');
    });
  });

  describe('client-server / EUC and low-code targets', () => {
    it('treats VB / Access client-server systems as migration targets', () => {
      const result = evaluateAxMigration(answer({ system: 'client_server', languages: ['vb', 'vba'] }));
      expect(result.targetSystem).toBe('client_server');
      expect(result.mql.candidate).toBe(true);
    });

    it('treats Notes / FileMaker style low-code platforms as migration targets', () => {
      const result = evaluateAxMigration(answer({ system: 'low_code', languages: ['other'] }));
      expect(result.targetSystem).toBe('low_code');
      expect(result.mql.candidate).toBe(true);
    });

    it('estimates client-server from VB / VBA when the platform is unknown', () => {
      expect(evaluateAxMigration(answer({ system: 'unknown', languages: ['vba'] })).targetSystem).toBe(
        'client_server'
      );
    });

    it('can exclude them from the MQL target via config', () => {
      const result = evaluateAxMigration(answer({ system: 'client_server', languages: ['vb'] }), {
        ...AX_MIGRATION_CONFIG,
        legacySystems: ['as400', 'office_computer', 'mainframe'],
        legacyLanguages: ['rpg', 'cobol', 'cl'],
      });
      expect(result.mql.candidate).toBe(false);
    });
  });

  describe('no challenges / many unknowns', () => {
    it('has no primary challenge and no problem awareness for "no particular challenges"', () => {
      const result = evaluateAxMigration(answer({ challenges: ['none'], maintenance: 'team' }));
      expect(result.challenges.primary).toBeNull();
      expect(result.sqlSignals.problemAware).toBe(false);
    });

    it('rejects "no particular challenges" combined with a challenge', () => {
      expect(
        validateAnswers(axMigrationDefinition, answer({ challenges: ['none', 'cost'] })).success
      ).toBe(false);
    });

    it('flags a hearing when three or more system answers are "I don\'t know"', () => {
      const result = evaluateAxMigration(
        answer({ system: 'unknown', languages: ['unknown'], programs: 'unknown', documents: 'unknown' })
      );
      expect(result.needsHearing).toBe(true);
      expect(evaluateAxMigration(typicalAs400).needsHearing).toBe(false);
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

    it('recommends a consultation to MQL candidates and information otherwise', () => {
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
      expect(Object.keys(publicResult).sort()).toEqual([
        'challenges',
        'difficulty',
        'needsHearing',
        'recommendation',
        'urgency',
      ]);
    });
  });
});
