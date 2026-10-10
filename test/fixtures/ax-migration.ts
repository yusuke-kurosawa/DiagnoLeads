/**
 * Typical answers for each path of the AX migration diagnosis (v2), shared by the tests
 */
import type { DiagnosticAnswers } from '@/lib/features/diagnostics/types';

const business = {
  challenges: ['people', 'cost'],
  timeline: '1_2y',
  industry: 'manufacturing',
  role: 'it_manager',
};

/** Mid-size manufacturer on AS/400 that depends on one or two people */
export const as400Answers: DiagnosticAnswers = {
  platform: 'as400',
  maintenance: 'few',
  support_end: '1_3y',
  integrations: 'some',
  as400_programs: '500_1999',
  as400_languages: ['rpg4'],
  source_docs: 'no_docs',
  ...business,
};

/** Distributor on ACOS-4 whose hardware support is about to end */
export const acosAnswers: DiagnosticAnswers = {
  platform: 'acos',
  acos_series: 'acos4',
  maintenance: 'vendor',
  support_end: 'within_1y',
  acos_programs: '3000_9999',
  acos_languages: ['cobol_only'],
  source_docs: 'complete',
  ...business,
  industry: 'distribution',
};

/** Department Access tools whose author has left, still on Office 2016 / 2019 */
export const accessAnswers: DiagnosticAnswers = {
  platform: 'access',
  access_maintainer: 'nobody',
  access_version: ['v2016_2019'],
  access_tools: '2_5',
  access_screens_forms: '20_50',
  access_features: ['vba', 'excel'],
  access_challenges: ['people', 'stability'],
  timeline: '1_2y',
  industry: 'manufacturing',
  role: 'business_manager',
};

/** Visual Basic client-server system */
export const otherAnswers: DiagnosticAnswers = {
  platform: 'other',
  other_system: 'vb',
  maintenance: 'team',
  support_end: 'beyond_3y',
  other_programs: '300_999',
  integrations: 'few',
  source_docs: 'complete',
  ...business,
};

export const answersByPlatform = {
  as400: as400Answers,
  acos: acosAnswers,
  access: accessAnswers,
  other: otherAnswers,
} as const;
