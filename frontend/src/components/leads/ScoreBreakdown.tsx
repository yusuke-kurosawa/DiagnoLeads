/**
 * Score Breakdown Component
 * 
 * Visualizes how the lead score was calculated with:
 * - Component scores (engagement, profile, behavior)
 * - Visual progress bars
 * - Total score calculation
 */

import React from 'react';
import { TrendingUpIcon, UserIcon, ActivityIcon, CheckCircleIcon } from 'lucide-react';

interface ScoreComponent {
  name: string;
  score: number;
  maxScore: number;
  description: string;
  icon: React.ReactNode;
}

interface ScoreBreakdownProps {
  totalScore: number;
  components?: ScoreComponent[];
}

export function ScoreBreakdown({ totalScore, components }: ScoreBreakdownProps) {
  // Default breakdown if not provided
  const defaultComponents: ScoreComponent[] = [
    {
      name: 'プロフィール完成度',
      score: Math.round(totalScore * 0.3),
      maxScore: 30,
      description: '企業情報、役職、連絡先の充実度',
      icon: <UserIcon className="w-5 h-5" />,
    },
    {
      name: 'エンゲージメント',
      score: Math.round(totalScore * 0.4),
      maxScore: 40,
      description: '診断回答の質と完了率',
      icon: <ActivityIcon className="w-5 h-5" />,
    },
    {
      name: '購買意欲',
      score: Math.round(totalScore * 0.3),
      maxScore: 30,
      description: '課題の深刻度と緊急度',
      icon: <TrendingUpIcon className="w-5 h-5" />,
    },
  ];

  const scoreComponents = components || defaultComponents;
  const isHot = totalScore >= 80;

  const getScoreColor = (score: number, maxScore: number): string => {
    const percentage = (score / maxScore) * 100;
    if (percentage >= 80) return 'bg-red-500';
    if (percentage >= 60) return 'bg-yellow-500';
    return 'bg-gray-400';
  };

  const getScoreBadgeColor = (score: number): string => {
    if (score >= 80) return 'bg-red-100 text-red-800 border-red-200';
    if (score >= 60) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-gray-100 text-gray-600 border-gray-200';
  };

  return (
    <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">スコア内訳</h3>
        <div className={`flex items-center gap-2 px-3 py-1 rounded-full border ${getScoreBadgeColor(totalScore)}`}>
          {isHot && <span>🔥</span>}
          <span className="text-2xl font-bold">{totalScore}</span>
          <span className="text-sm">/100</span>
        </div>
      </div>

      {/* Total Score Visualization */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">総合スコア</span>
          <span className="text-sm text-gray-600">{totalScore}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className={`h-3 rounded-full transition-all duration-500 ${
              totalScore >= 80
                ? 'bg-gradient-to-r from-red-500 to-red-600'
                : totalScore >= 60
                ? 'bg-gradient-to-r from-yellow-500 to-yellow-600'
                : 'bg-gradient-to-r from-gray-400 to-gray-500'
            }`}
            style={{ width: `${totalScore}%` }}
          />
        </div>
        {isHot && (
          <div className="mt-2 flex items-center gap-2 text-sm text-red-600 font-medium">
            <CheckCircleIcon className="w-4 h-4" />
            <span>ホットリード - 優先的にフォローアップ推奨</span>
          </div>
        )}
      </div>

      {/* Component Breakdown */}
      <div className="space-y-4">
        <h4 className="text-sm font-semibold text-gray-700 mb-3">スコア構成要素</h4>
        {scoreComponents.map((component, index) => (
          <div key={index} className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-start gap-3 mb-3">
              <div className="text-gray-600">{component.icon}</div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-gray-900">{component.name}</span>
                  <span className="text-sm font-semibold text-gray-900">
                    {component.score}/{component.maxScore}
                  </span>
                </div>
                <p className="text-xs text-gray-600 mb-2">{component.description}</p>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${getScoreColor(
                      component.score,
                      component.maxScore
                    )}`}
                    style={{ width: `${(component.score / component.maxScore) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Score Interpretation */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <h4 className="text-sm font-semibold text-gray-700 mb-2">スコア評価</h4>
        <div className="space-y-2 text-sm">
          {totalScore >= 80 && (
            <div className="flex items-start gap-2 text-red-700">
              <span className="font-medium">🔥 ホットリード:</span>
              <span>即座にコンタクトを取り、デモや商談の提案を行いましょう。</span>
            </div>
          )}
          {totalScore >= 60 && totalScore < 80 && (
            <div className="flex items-start gap-2 text-yellow-700">
              <span className="font-medium">⚡ ウォームリード:</span>
              <span>関心が高いため、追加情報の提供やフォローアップメールを送りましょう。</span>
            </div>
          )}
          {totalScore < 60 && (
            <div className="flex items-start gap-2 text-gray-700">
              <span className="font-medium">📧 コールドリード:</span>
              <span>ナーチャリングキャンペーンに追加し、定期的な情報提供を続けましょう。</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
