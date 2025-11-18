import React, { useState } from 'react';
import {
  BookOpen,
  LayoutDashboard,
  ClipboardList,
  Users,
  BarChart3,
  Settings,
  Shield,
  Search,
  ChevronRight
} from 'lucide-react';
import { useHelpStore } from '../../store/helpStore';
import { helpContent } from '../../data/helpContent';

interface HelpCategory {
  title: string;
  icon: React.ReactNode;
  items: {
    key: string;
    title: string;
    description: string;
  }[];
}

const helpCategories: HelpCategory[] = [
  {
    title: '基本機能',
    icon: <LayoutDashboard className="w-5 h-5" />,
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
    icon: <ClipboardList className="w-5 h-5" />,
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
    icon: <Settings className="w-5 h-5" />,
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

const faqItems = [
  {
    question: 'AI診断生成機能はどのように使いますか？',
    answer: '診断作成ページで「AI診断生成」タブを選択し、トピック（例：DX診断、マーケティング診断）と業界を入力して「生成」ボタンをクリックします。Claude AIが自動的に質問、選択肢、スコアリングを生成します。',
  },
  {
    question: '診断を自社サイトに埋め込むにはどうすればよいですか？',
    answer: '診断詳細ページの「埋め込み」タブから埋め込みコードをコピーし、あなたのWebサイトのHTMLに貼り付けるだけです。WordPressやWixなどのCMSにも対応しています。',
  },
  {
    question: 'ホットリードとは何ですか？',
    answer: 'ホットリードはスコアが80点以上の見込み顧客で、購買意欲が高いと判定されたリードです。AIが診断回答から自動的に検出し、優先的にフォローアップすべきリードとしてマークします。',
  },
  {
    question: 'Salesforce/HubSpotと連携できますか？',
    answer: 'はい、設定ページの「外部連携」タブからSalesforce、HubSpot、Slackなどのサービスと連携できます。リード情報が自動的に同期され、営業活動を効率化できます。',
  },
  {
    question: '診断の完了率を上げるにはどうすればよいですか？',
    answer: '分析ダッシュボードで離脱率の高い質問を特定し、質問文を簡潔にする、選択肢を減らす、質問数を減らすなどの改善を行うことで完了率を向上できます。',
  },
  {
    question: 'チームメンバーを招待するにはどうすればよいですか？',
    answer: '設定ページの「ユーザー管理」タブから、メンバーのメールアドレスを入力して招待できます。権限（管理者/一般ユーザー）も設定可能です。',
  },
];

export function HelpCenterPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);
  const { openHelp } = useHelpStore();

  const handleHelpItemClick = (key: string) => {
    openHelp(key);
  };

  const filteredCategories = helpCategories.map(category => ({
    ...category,
    items: category.items.filter(
      item =>
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.description.toLowerCase().includes(searchQuery.toLowerCase())
    ),
  })).filter(category => category.items.length > 0);

  const filteredFaq = faqItems.filter(
    item =>
      item.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.answer.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg p-8 text-white">
        <div className="flex items-center gap-3 mb-4">
          <BookOpen className="w-8 h-8" />
          <h1 className="text-3xl font-bold">ヘルプセンター</h1>
        </div>
        <p className="text-blue-100 mb-6">
          DiagnoLeadsの使い方やよくある質問をご確認いただけます
        </p>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="ヘルプを検索..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 rounded-lg border-0 text-gray-900 placeholder-gray-500 focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Help Categories */}
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900">機能ガイド</h2>
        {filteredCategories.map((category, categoryIndex) => (
          <div key={categoryIndex} className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <div className="text-blue-600">{category.icon}</div>
              <h3 className="text-lg font-semibold text-gray-900">
                {category.title}
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {category.items.map((item) => (
                <button
                  key={item.key}
                  onClick={() => handleHelpItemClick(item.key)}
                  className="flex items-center justify-between p-4 bg-gray-50 hover:bg-blue-50 border border-gray-200 hover:border-blue-300 rounded-lg transition-colors text-left group"
                >
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 group-hover:text-blue-600 mb-1">
                      {item.title}
                    </h4>
                    <p className="text-sm text-gray-600">{item.description}</p>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-blue-600 ml-2" />
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* FAQ Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          よくある質問（FAQ）
        </h2>

        <div className="space-y-3">
          {filteredFaq.map((item, index) => (
            <div
              key={index}
              className="border border-gray-200 rounded-lg overflow-hidden"
            >
              <button
                onClick={() => setExpandedFaq(expandedFaq === index ? null : index)}
                className="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 transition-colors text-left"
              >
                <span className="font-medium text-gray-900">{item.question}</span>
                <ChevronRight
                  className={`w-5 h-5 text-gray-400 transition-transform ${
                    expandedFaq === index ? 'rotate-90' : ''
                  }`}
                />
              </button>
              {expandedFaq === index && (
                <div className="p-4 bg-white border-t border-gray-200">
                  <p className="text-gray-600 leading-relaxed">{item.answer}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Contact Support */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          問題が解決しませんか？
        </h3>
        <p className="text-gray-600 mb-4">
          サポートチームがお手伝いします。お気軽にお問い合わせください。
        </p>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          サポートに問い合わせる
        </button>
      </div>
    </div>
  );
}
