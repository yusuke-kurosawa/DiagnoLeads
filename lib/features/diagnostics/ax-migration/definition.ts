import type { DiagnosticDefinition } from '../types';

/**
 * AX migration self-diagnosis (Web セルフ診断)
 *
 * Source: AX migration sales & marketing flow (2026-10-08) and the AX migration pamphlet.
 * Target: mid-size manufacturers / distributors running legacy core systems such as AS/400.
 */
export const AX_MIGRATION_DIAGNOSTIC_KEY = 'ax-migration';

export const axMigrationDefinition: DiagnosticDefinition = {
  key: AX_MIGRATION_DIAGNOSTIC_KEY,
  version: 1,
  title: {
    ja: 'AXマイグレーション 基幹システム診断',
    en: 'AX Migration Core System Check',
  },
  description: {
    ja: '12の質問（約5分）に答えると、基幹システムの移行難易度の目安と、優先して取り組むべき課題がわかります。',
    en: 'Answer 12 questions (about 5 minutes) to see an estimate of your migration difficulty and the challenges to tackle first.',
  },
  sections: [
    {
      id: 'company',
      title: { ja: '会社について', en: 'About your company' },
      questionIds: ['industry', 'revenue'],
    },
    {
      id: 'system',
      title: { ja: '基幹システムについて', en: 'About your core system' },
      questionIds: ['system', 'languages', 'years', 'programs', 'integrations'],
    },
    {
      id: 'operation',
      title: { ja: '運用と課題について', en: 'Operations and challenges' },
      questionIds: ['maintenance', 'documents', 'challenges'],
    },
    {
      id: 'plan',
      title: { ja: '検討状況について', en: 'Your plans' },
      questionIds: ['timeline', 'role'],
    },
  ],
  questions: [
    {
      id: 'industry',
      type: 'single',
      required: true,
      label: { ja: '業種を教えてください', en: 'What is your industry?' },
      options: [
        { value: 'manufacturing', label: { ja: '製造業', en: 'Manufacturing' } },
        {
          value: 'distribution',
          label: {
            ja: '流通業（卸売・小売・物流）',
            en: 'Distribution (wholesale, retail, logistics)',
          },
        },
        { value: 'other', label: { ja: 'その他', en: 'Other' } },
      ],
    },
    {
      id: 'revenue',
      type: 'single',
      required: true,
      label: { ja: '年間売上高を教えてください', en: 'What is your annual revenue?' },
      options: [
        { value: 'lt5b', label: { ja: '50億円未満', en: 'Under JPY 5B' } },
        { value: '5b_10b', label: { ja: '50億〜100億円', en: 'JPY 5B-10B' } },
        { value: '10b_30b', label: { ja: '100億〜300億円', en: 'JPY 10B-30B' } },
        { value: '30b_100b', label: { ja: '300億〜1,000億円', en: 'JPY 30B-100B' } },
        { value: 'gte100b', label: { ja: '1,000億円以上', en: 'JPY 100B or more' } },
      ],
    },
    {
      id: 'system',
      type: 'single',
      required: true,
      label: { ja: '現在の基幹システムの基盤は？', en: 'What platform runs your core system?' },
      options: [
        { value: 'as400', label: { ja: 'AS/400（IBM i）', en: 'AS/400 (IBM i)' } },
        {
          value: 'office_computer',
          label: { ja: 'その他のオフコン', en: 'Other office computer' },
        },
        { value: 'mainframe', label: { ja: '汎用機（メインフレーム）', en: 'Mainframe' } },
        {
          value: 'package',
          label: { ja: 'パッケージ・クラウドサービス', en: 'Packaged software / cloud service' },
        },
        { value: 'unknown', label: { ja: 'わからない', en: "I don't know" } },
      ],
    },
    {
      id: 'languages',
      type: 'multiple',
      required: true,
      label: {
        ja: '主な開発言語は？（複数選択可）',
        en: 'Which languages is it built with? (select all that apply)',
      },
      exclusiveOptions: ['unknown'],
      options: [
        { value: 'rpg', label: { ja: 'RPG', en: 'RPG' } },
        { value: 'cobol', label: { ja: 'COBOL', en: 'COBOL' } },
        { value: 'cl', label: { ja: 'CL', en: 'CL' } },
        { value: 'other', label: { ja: 'Java・その他', en: 'Java / other' } },
        { value: 'unknown', label: { ja: 'わからない', en: "I don't know" } },
      ],
    },
    {
      id: 'years',
      type: 'single',
      required: true,
      label: {
        ja: '現在のシステムの利用年数は？',
        en: 'How long have you used the current system?',
      },
      options: [
        { value: 'lt10', label: { ja: '10年未満', en: 'Less than 10 years' } },
        { value: '10_20', label: { ja: '10〜20年', en: '10-20 years' } },
        { value: 'gte20', label: { ja: '20年以上', en: '20 years or more' } },
      ],
    },
    {
      id: 'programs',
      type: 'single',
      required: true,
      label: { ja: 'プログラム本数の目安は？', en: 'Roughly how many programs are there?' },
      options: [
        { value: 'lt500', label: { ja: '500本未満', en: 'Under 500' } },
        { value: '500_2000', label: { ja: '500〜2,000本', en: '500-2,000' } },
        { value: '2000_5000', label: { ja: '2,000〜5,000本', en: '2,000-5,000' } },
        { value: 'gte5000', label: { ja: '5,000本以上', en: '5,000 or more' } },
        { value: 'unknown', label: { ja: 'わからない', en: "I don't know" } },
      ],
    },
    {
      id: 'integrations',
      type: 'single',
      required: true,
      label: {
        ja: '他システムとの連携先の数は？',
        en: 'How many other systems does it integrate with?',
      },
      options: [
        { value: 'few', label: { ja: '0〜2', en: '0-2' } },
        { value: 'some', label: { ja: '3〜5', en: '3-5' } },
        { value: 'many', label: { ja: '6以上', en: '6 or more' } },
        { value: 'unknown', label: { ja: 'わからない', en: "I don't know" } },
      ],
    },
    {
      id: 'maintenance',
      type: 'single',
      required: true,
      label: { ja: 'システムを保守している体制は？', en: 'Who maintains the system?' },
      options: [
        {
          value: 'team',
          label: { ja: '社内に詳しい担当者が複数いる', en: 'Several in-house experts' },
        },
        {
          value: 'few',
          label: { ja: '社内の1〜2名に頼っている', en: 'We rely on one or two people in-house' },
        },
        {
          value: 'vendor',
          label: { ja: '外部ベンダーに頼っている', en: 'We rely on an external vendor' },
        },
        {
          value: 'none',
          label: {
            ja: '担当者がいない・退職を控えている',
            en: 'No one, or the person is about to retire',
          },
        },
      ],
    },
    {
      id: 'documents',
      type: 'single',
      required: true,
      label: { ja: '仕様書・設計書の状態は？', en: 'What state are the specifications in?' },
      options: [
        {
          value: 'updated',
          label: { ja: '最新の状態で揃っている', en: 'Complete and up to date' },
        },
        {
          value: 'partial',
          label: { ja: '一部が古い・足りない', en: 'Partly outdated or missing' },
        },
        { value: 'none', label: { ja: 'ほとんどない', en: 'Almost none' } },
      ],
    },
    {
      id: 'challenges',
      type: 'multiple',
      required: true,
      label: {
        ja: '現在感じている課題は？（複数選択可）',
        en: 'Which challenges do you face? (select all that apply)',
      },
      options: [
        {
          value: 'people',
          label: {
            ja: '扱える技術者が減り、仕様がブラックボックス化している',
            en: 'Fewer engineers can handle it; the spec is a black box',
          },
        },
        {
          value: 'cost',
          label: {
            ja: '保守・延命の費用がかさみ、新しい投資に回せない',
            en: 'Maintenance costs crowd out new investment',
          },
        },
        {
          value: 'agility',
          label: {
            ja: '取引先や市場の変化に合わせた機能追加が難しい',
            en: 'Hard to add features as customers and markets change',
          },
        },
        {
          value: 'data',
          label: {
            ja: 'データが独自形式で、経営判断にすぐ使えない',
            en: 'Data is locked in proprietary formats and not usable for decisions',
          },
        },
        {
          value: 'eos',
          label: {
            ja: 'ハードウェア・OSの保守期限が迫っている',
            en: 'Hardware or OS support is ending soon',
          },
        },
      ],
    },
    {
      id: 'timeline',
      type: 'single',
      required: true,
      label: { ja: '刷新を検討したい時期は？', en: 'When would you like to modernize?' },
      options: [
        { value: 'within_1y', label: { ja: '1年以内', en: 'Within 1 year' } },
        { value: '1_2y', label: { ja: '1〜2年以内', en: 'In 1-2 years' } },
        { value: '2_3y', label: { ja: '2〜3年以内', en: 'In 2-3 years' } },
        { value: 'undecided', label: { ja: '未定', en: 'Undecided' } },
      ],
    },
    {
      id: 'role',
      type: 'single',
      required: true,
      label: { ja: 'あなたの立場に近いものは？', en: 'Which best describes your role?' },
      options: [
        { value: 'executive', label: { ja: '経営層・決裁者', en: 'Executive / decision maker' } },
        {
          value: 'it_manager',
          label: { ja: '情報システム部門の責任者', en: 'IT department head' },
        },
        { value: 'it_staff', label: { ja: '情報システム部門の担当者', en: 'IT staff' } },
        { value: 'business', label: { ja: '業務部門', en: 'Business department' } },
        { value: 'other', label: { ja: 'その他', en: 'Other' } },
      ],
    },
  ],
};
