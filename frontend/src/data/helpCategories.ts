/**
 * Help center categories and FAQ items
 */

import {
  LayoutDashboard,
  ClipboardList,
  Settings,
} from 'lucide-react';
import { type HelpCategory, type FAQItem } from '../types/help';

/**
 * Help categories organized by feature area
 */
export const helpCategories: HelpCategory[] = [
  {
    title: '基本機能',
    icon: LayoutDashboard,
    items: [
      {
        key: 'dashboard',
        title: 'ダッシュボード',
        description: '主要な指標とアクティビティの確認',
      },
      {
        key: 'assessments',
        title: '診断管理',
        description: '診断の作成、編集、公開',
      },
      {
        key: 'leads',
        title: 'リード管理',
        description: '見込み顧客の管理とフォローアップ',
      },
      {
        key: 'analytics',
        title: '分析ダッシュボード',
        description: 'パフォーマンスの詳細分析',
      },
    ],
  },
  {
    title: '診断機能',
    icon: ClipboardList,
    items: [
      {
        key: 'assessments-create',
        title: '診断作成',
        description: '新しい診断を作成する方法',
      },
      {
        key: 'assessments-edit',
        title: '診断編集',
        description: '既存の診断を編集する方法',
      },
    ],
  },
  {
    title: '設定と管理',
    icon: Settings,
    items: [
      {
        key: 'settings',
        title: '設定',
        description: 'テナント設定と外部連携',
      },
      {
        key: 'admin-masters',
        title: 'マスターデータ管理',
        description: 'システム全体のマスターデータ',
      },
      {
        key: 'admin-audit-logs',
        title: '監査ログ',
        description: 'システム操作の記録と確認',
      },
    ],
  },
];

/**
 * Frequently Asked Questions
 */
export const faqItems: FAQItem[] = [
  {
    question: 'AI診断生成機能はどのように使いますか？',
    answer:
      '診断作成ページで「AI診断生成」タブを選択し、トピック（例：DX診断、マーケティング診断）と業界を入力して「生成」ボタンをクリックします。Claude AIが自動的に質問、選択肢、スコアリングを生成します。',
  },
  {
    question: '診断を自社サイトに埋め込むにはどうすればよいですか？',
    answer:
      '診断詳細ページの「埋め込み」タブから埋め込みコードをコピーし、あなたのWebサイトのHTMLに貼り付けるだけです。WordPressやWixなどのCMSにも対応しています。',
  },
  {
    question: 'ホットリードとは何ですか？',
    answer:
      'ホットリードはスコアが80点以上の見込み顧客で、購買意欲が高いと判定されたリードです。AIが診断回答から自動的に検出し、優先的にフォローアップすべきリードとしてマークします。',
  },
  {
    question: 'Salesforce/HubSpotと連携できますか？',
    answer:
      'はい、設定ページの「外部連携」タブからSalesforce、HubSpot、Slackなどのサービスと連携できます。リード情報が自動的に同期され、営業活動を効率化できます。',
  },
  {
    question: '診断の完了率を上げるにはどうすればよいですか？',
    answer:
      '分析ダッシュボードで離脱率の高い質問を特定し、質問文を簡潔にする、選択肢を減らす、質問数を減らすなどの改善を行うことで完了率を向上できます。',
  },
  {
    question: 'チームメンバーを招待するにはどうすればよいですか？',
    answer:
      '設定ページの「ユーザー管理」タブから、メンバーのメールアドレスを入力して招待できます。権限（管理者/一般ユーザー）も設定可能です。',
  },
];
