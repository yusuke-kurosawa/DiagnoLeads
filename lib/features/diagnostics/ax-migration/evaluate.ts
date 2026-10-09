import type { TargetSystem } from '@/lib/features/leads/types/pipeline';
import { multiple, single, toPercent } from '../engine';
import type { DiagnosticAnswers } from '../types';
import { AX_MIGRATION_CONFIG, type AxMigrationConfig } from './config';
import { axMigrationDefinition } from './definition';

export type Level = 'low' | 'medium' | 'high';
export type ChallengeType = 'people' | 'cost' | 'agility' | 'data';

export interface AxMigrationResult {
  diagnosticVersion: number;
  /** 移行難易度の目安 */
  difficulty: { score: number; level: Level };
  /** 刷新の緊急度 */
  urgency: { score: number; level: Level };
  /**
   * ヒト／カネ／モノ／情報 — the primary one drives the result message.
   * For hypothesis H1 use the raw `selected` answers, not `primary` (ties favour people).
   * `primary` is null when the respondent sees no particular challenge.
   */
  challenges: {
    primary: ChallengeType | null;
    selected: string[];
    scores: Record<ChallengeType, number>;
  };
  /** Lead score stored on leads.score (0-100) */
  leadScore: number;
  targetSystem: TargetSystem | null;
  /**
   * MQL: all three criteria must be met. While the Web diagnosis does not count as an
   * action (config), `qualified` stays false and `candidate` (industry × system) is handed
   * to marketing, who confirm the MQL.
   */
  mql: {
    qualified: boolean;
    candidate: boolean;
    criteria: { industry: boolean; system: boolean; action: boolean };
  };
  /** Hints for sales. SQL is decided by sales after the hearing: ①② required + ③ or ④ */
  sqlSignals: {
    candidate: boolean;
    systemKnown: boolean;
    problemAware: boolean;
    timelineVisible: boolean;
    decisionAccess: boolean;
  };
  /** Many "I don't know" answers: the estimate is weak and needs a hearing */
  needsHearing: boolean;
  /** Next step suggested to the respondent */
  recommendation: 'consultation' | 'information';
}

const DIFFICULTY_POINTS = {
  system: {
    as400: 20,
    office_computer: 25,
    mainframe: 30,
    client_server: 15,
    low_code: 20,
    package: 10,
    unknown: 20,
  },
  languages: { rpg: 10, cobol: 10, cl: 5, vb: 8, vba: 8, other: 5, unknown: 10 },
  programs: { lt500: 5, '500_2000': 15, '2000_5000': 25, gte5000: 30, unknown: 20 },
  integrations: { few: 3, some: 9, many: 15, unknown: 9 },
  documents: { updated: 0, partial: 8, none: 15, unknown: 10 },
  years: { lt10: 0, '10_20': 3, gte20: 5 },
} as const;
const LANGUAGE_POINTS_CAP = 20;
const DIFFICULTY_MAX = 30 + LANGUAGE_POINTS_CAP + 30 + 15 + 15 + 5;

const URGENCY_POINTS = {
  maintenance: { team: 0, vendor: 15, few: 25, none: 35 },
  eos: 25,
  years: { lt10: 0, '10_20': 8, gte20: 15 },
  timeline: { within_1y: 25, '1_2y': 15, '2_3y': 5, beyond_3y: 0, undecided: 0 },
} as const;
const URGENCY_MAX = 35 + 25 + 15 + 25;

const LEAD_SCORE_POINTS = {
  revenue: { lt5b: 5, '5b_10b': 10, '10b_30b': 15, '30b_100b': 10, gte100b: 5 },
  timeline: { within_1y: 20, '1_2y': 15, '2_3y': 8, beyond_3y: 2, undecided: 3 },
  role: { executive: 10, it_manager: 10, it_staff: 6, business: 4, other: 2 },
} as const;

const CHALLENGE_ORDER: ChallengeType[] = ['people', 'cost', 'agility', 'data'];
/** Number of "I don't know" answers on the system questions that triggers needsHearing */
const NEEDS_HEARING_UNKNOWNS = 3;

function points<T extends Record<string, number>>(table: T, value: string | undefined): number {
  return value !== undefined && value in table ? table[value as keyof T] : 0;
}

function toLevel(score: number, mediumFrom: number, highFrom: number): Level {
  if (score >= highFrom) return 'high';
  if (score >= mediumFrom) return 'medium';
  return 'low';
}

function deriveTargetSystem(system: string | undefined, languages: string[]): TargetSystem | null {
  if (system === 'as400') return 'as400';
  if (system === 'office_computer' || system === 'mainframe') return 'other_legacy';
  if (system === 'client_server') return 'client_server';
  if (system === 'low_code') return 'low_code';
  if (system === 'package') return 'other';
  // Platform unknown: estimate from languages (RPG / CL run on IBM i, VB / VBA on Windows)
  if (languages.includes('rpg') || languages.includes('cl')) return 'as400';
  if (languages.includes('cobol')) return 'other_legacy';
  if (languages.includes('vb') || languages.includes('vba')) return 'client_server';
  return null;
}

/**
 * Evaluate validated answers. Pure function: no I/O, deterministic.
 */
export function evaluateAxMigration(
  answers: DiagnosticAnswers,
  config: AxMigrationConfig = AX_MIGRATION_CONFIG
): AxMigrationResult {
  const industry = single(answers, 'industry');
  const system = single(answers, 'system');
  const languages = multiple(answers, 'languages');
  const years = single(answers, 'years');
  const programs = single(answers, 'programs');
  const integrations = single(answers, 'integrations');
  const maintenance = single(answers, 'maintenance');
  const documents = single(answers, 'documents');
  const challenges = multiple(answers, 'challenges');
  const timeline = single(answers, 'timeline');
  const role = single(answers, 'role');

  // 移行難易度の目安
  const languagePoints = Math.min(
    LANGUAGE_POINTS_CAP,
    languages.reduce((sum, lang) => sum + points(DIFFICULTY_POINTS.languages, lang), 0)
  );
  const difficultyRaw =
    points(DIFFICULTY_POINTS.system, system) +
    languagePoints +
    points(DIFFICULTY_POINTS.programs, programs) +
    points(DIFFICULTY_POINTS.integrations, integrations) +
    points(DIFFICULTY_POINTS.documents, documents) +
    points(DIFFICULTY_POINTS.years, years);
  const difficultyScore = toPercent(difficultyRaw, DIFFICULTY_MAX);

  // 緊急度
  const urgencyRaw =
    points(URGENCY_POINTS.maintenance, maintenance) +
    (challenges.includes('eos') ? URGENCY_POINTS.eos : 0) +
    points(URGENCY_POINTS.years, years) +
    points(URGENCY_POINTS.timeline, timeline);
  const urgencyScore = toPercent(urgencyRaw, URGENCY_MAX);

  // 主な課題（ヒト／カネ／モノ／情報）
  const challengeScores: Record<ChallengeType, number> = {
    people:
      (challenges.includes('people') ? 3 : 0) +
      (maintenance === 'few' || maintenance === 'none' ? 2 : 0),
    cost:
      (challenges.includes('cost') ? 3 : 0) +
      (challenges.includes('eos') ? 1 : 0) +
      (maintenance === 'vendor' ? 1 : 0),
    agility: challenges.includes('agility') ? 3 : 0,
    data: challenges.includes('data') ? 3 : 0,
  };
  const best = CHALLENGE_ORDER.reduce((top, type) =>
    challengeScores[type] > challengeScores[top] ? type : top
  );
  // "No particular challenges" with nothing else pointing at one: no primary challenge
  const primary = challengeScores[best] > 0 ? best : null;

  // MQL（3条件すべて）
  const legacyEstimated =
    system === 'unknown' && languages.some((lang) => config.legacyLanguages.includes(lang));
  const mqlCriteria = {
    industry: industry !== undefined && config.targetIndustries.includes(industry),
    system: (system !== undefined && config.legacySystems.includes(system)) || legacyEstimated,
    action: config.countWebDiagnosisAsMqlAction,
  };
  const mqlCandidate = mqlCriteria.industry && mqlCriteria.system;
  const mqlQualified = mqlCandidate && mqlCriteria.action;

  // SQL の手がかり（①②必須＋③④のいずれか）
  const systemKnown =
    system !== undefined &&
    system !== 'unknown' &&
    languages.length > 0 &&
    !languages.includes('unknown') &&
    programs !== undefined &&
    programs !== 'unknown';
  const problemAware = challenges.some((c) => c === 'people' || c === 'cost' || c === 'eos');
  const timelineVisible = timeline !== undefined && config.sqlTimelines.includes(timeline);
  const decisionAccess = role !== undefined && config.decisionAccessRoles.includes(role);

  // Lead score (fit + intent)
  const systemFit = mqlCriteria.system ? (legacyEstimated ? 15 : 20) : system === 'unknown' ? 8 : 3;
  const leadScore = Math.min(
    100,
    (mqlCriteria.industry ? 20 : 5) +
      points(LEAD_SCORE_POINTS.revenue, single(answers, 'revenue')) +
      systemFit +
      Math.round(urgencyScore * 0.15) +
      points(LEAD_SCORE_POINTS.timeline, timeline) +
      points(LEAD_SCORE_POINTS.role, role)
  );

  const unknownAnswers = [
    system === 'unknown',
    languages.includes('unknown'),
    programs === 'unknown',
    integrations === 'unknown',
    documents === 'unknown',
  ].filter(Boolean).length;

  const difficultyLevel = toLevel(difficultyScore, 40, 70);
  const urgencyLevel = toLevel(urgencyScore, 30, 60);

  return {
    diagnosticVersion: axMigrationDefinition.version,
    difficulty: { score: difficultyScore, level: difficultyLevel },
    urgency: { score: urgencyScore, level: urgencyLevel },
    challenges: { primary, selected: challenges, scores: challengeScores },
    leadScore,
    targetSystem: deriveTargetSystem(system, languages),
    mql: { qualified: mqlQualified, candidate: mqlCandidate, criteria: mqlCriteria },
    sqlSignals: {
      candidate: systemKnown && problemAware && (timelineVisible || decisionAccess),
      systemKnown,
      problemAware,
      timelineVisible,
      decisionAccess,
    },
    needsHearing: unknownAnswers >= NEEDS_HEARING_UNKNOWNS,
    recommendation:
      mqlCandidate || difficultyLevel === 'high' || urgencyLevel === 'high'
        ? 'consultation'
        : 'information',
  };
}

/** Part of the result shown to the respondent (no lead score or MQL/SQL judgement) */
export type AxMigrationPublicResult = Pick<
  AxMigrationResult,
  'difficulty' | 'urgency' | 'challenges' | 'needsHearing' | 'recommendation'
>;

export function toPublicResult(result: AxMigrationResult): AxMigrationPublicResult {
  return {
    difficulty: result.difficulty,
    urgency: result.urgency,
    challenges: result.challenges,
    needsHearing: result.needsHearing,
    recommendation: result.recommendation,
  };
}
