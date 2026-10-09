/**
 * Business rules for the AX migration diagnosis.
 *
 * Values marked "要確認" are still under review by the business side
 * (see the 要確認事項 slide of the sales & marketing flow) and are kept here
 * so they can be changed without touching the evaluation logic.
 */
export interface AxMigrationConfig {
  /** MQL 条件「業種」: target industries */
  targetIndustries: readonly string[];
  /**
   * MQL 条件「システム」: migration targets.
   * VB・Access（部署単位のツールを含む）・WebPerformer を対象にする（2026-10-09 決定）。
   * その他のローコード製品（other_low_code）は当面対象外
   */
  legacySystems: readonly string[];
  /** Languages that suggest a legacy platform when the platform itself is unknown（推定でも可） */
  legacyLanguages: readonly string[];
  /**
   * MQL 条件「行動」: count completing this Web diagnosis as an action
   * (資料DL・デモ閲覧・勉強会参加 と同等に扱う。2026-10-09 決定)。
   * false にすると MQL を自動判定せず「MQL候補」として渡し、マーケが確定する
   */
  countWebDiagnosisAsMqlAction: boolean;
  /** SQL 条件③「検討時期」: timelines that count as "visible" — 要確認 */
  sqlTimelines: readonly string[];
  /** SQL 条件④「検討体制」: roles that give access to decision makers or IT */
  decisionAccessRoles: readonly string[];
  /** 相談申込への連絡期限（営業日） — 要確認 */
  consultationResponseBusinessDays: number;
}

export const AX_MIGRATION_CONFIG: AxMigrationConfig = {
  targetIndustries: ['manufacturing', 'distribution'],
  legacySystems: ['as400', 'office_computer', 'mainframe', 'vb', 'access', 'webperformer'],
  legacyLanguages: ['rpg', 'cobol', 'cl', 'vb', 'vba'],
  countWebDiagnosisAsMqlAction: true,
  sqlTimelines: ['within_1y', '1_2y'],
  decisionAccessRoles: ['executive', 'it_manager', 'it_staff'],
  consultationResponseBusinessDays: 2,
};
