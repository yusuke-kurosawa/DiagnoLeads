/**
 * Code-defined diagnostics
 *
 * A diagnostic is defined in TypeScript (questions, options and scoring rules)
 * and evaluated on the server only. Clients receive a public view without scores.
 */

export type DiagnosticLocale = 'ja' | 'en';

export type LocalizedText = Record<DiagnosticLocale, string>;

export interface DiagnosticOption {
  value: string;
  label: LocalizedText;
}

export interface DiagnosticQuestion {
  id: string;
  type: 'single' | 'multiple';
  label: LocalizedText;
  description?: LocalizedText;
  required: boolean;
  options: DiagnosticOption[];
  /** Options that cannot be combined with others in a multiple-choice question */
  exclusiveOptions?: string[];
}

export interface DiagnosticSection {
  id: string;
  title: LocalizedText;
  questionIds: string[];
}

export interface DiagnosticDefinition {
  key: string;
  /** Increment when questions or scoring change so stored results stay interpretable */
  version: number;
  title: LocalizedText;
  description: LocalizedText;
  sections: DiagnosticSection[];
  questions: DiagnosticQuestion[];
}

/** Normalized answers: single → string, multiple → string[] */
export type DiagnosticAnswers = Record<string, string | string[]>;

export interface AnswerValidationIssue {
  questionId: string;
  code: 'required' | 'invalid_option' | 'invalid_type' | 'exclusive_conflict' | 'unknown_question';
}

export type AnswerValidationResult =
  | { success: true; answers: DiagnosticAnswers }
  | { success: false; issues: AnswerValidationIssue[] };
