/**
 * Settings Panel Component
 * 
 * Right sidebar for assessment-level settings:
 * - Publish/unpublish
 * - Status management
 * - Embed code
 * - Preview link
 */

import React from 'react';
import { 
  EyeIcon, 
  CodeIcon, 
  ShareIcon, 
  SettingsIcon,
  CheckCircle2Icon,
  XCircleIcon
} from 'lucide-react';

interface Assessment {
  id: string;
  title: string;
  description?: string;
  status: 'draft' | 'published' | 'unpublished';
  questions: any[];
}

interface SettingsPanelProps {
  assessment: Assessment;
  onPublish?: () => void;
  onUnpublish?: () => void;
}

export function SettingsPanel({ 
  assessment, 
  onPublish, 
  onUnpublish 
}: SettingsPanelProps) {
  const isPublished = assessment.status === 'published';
  const isDraft = assessment.status === 'draft';

  const handleCopyEmbedCode = () => {
    const embedCode = `<script src="https://app.diagnoleads.com/embed.js"></script>
<div data-diagnoleads-assessment="${assessment.id}"></div>`;
    
    navigator.clipboard.writeText(embedCode);
    alert('埋め込みコードをコピーしました');
  };

  const handleCopyPublicUrl = () => {
    const url = `https://app.diagnoleads.com/a/${assessment.id}`;
    navigator.clipboard.writeText(url);
    alert('公開URLをコピーしました');
  };

  const canPublish = assessment.questions.length > 0;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-4">
        <div className="flex items-center gap-2 mb-2">
          <SettingsIcon className="w-5 h-5 text-gray-700" />
          <h3 className="text-lg font-semibold text-gray-900">設定</h3>
        </div>
        <p className="text-sm text-gray-500">
          診断の公開設定と共有オプション
        </p>
      </div>

      {/* Status */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          ステータス
        </label>
        <div className="flex items-center gap-2">
          {isPublished && (
            <div className="flex items-center gap-2 text-green-600">
              <CheckCircle2Icon className="w-5 h-5" />
              <span className="font-medium">公開中</span>
            </div>
          )}
          {isDraft && (
            <div className="flex items-center gap-2 text-yellow-600">
              <XCircleIcon className="w-5 h-5" />
              <span className="font-medium">下書き</span>
            </div>
          )}
          {assessment.status === 'unpublished' && (
            <div className="flex items-center gap-2 text-gray-600">
              <XCircleIcon className="w-5 h-5" />
              <span className="font-medium">非公開</span>
            </div>
          )}
        </div>
      </div>

      {/* Publish/Unpublish Actions */}
      <div className="space-y-3">
        {!isPublished && (
          <button
            onClick={onPublish}
            disabled={!canPublish}
            className={`
              w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg
              font-medium transition-colors
              ${canPublish
                ? 'bg-green-600 text-white hover:bg-green-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }
            `}
          >
            <CheckCircle2Icon className="w-4 h-4" />
            公開する
          </button>
        )}

        {isPublished && (
          <button
            onClick={onUnpublish}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 font-medium transition-colors"
          >
            <XCircleIcon className="w-4 h-4" />
            非公開にする
          </button>
        )}

        {!canPublish && (
          <p className="text-xs text-red-600">
            ⚠️ 最低1つの質問が必要です
          </p>
        )}
      </div>

      {/* Preview */}
      {isPublished && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            プレビュー
          </label>
          <button
            onClick={() => window.open(`/preview/${assessment.id}`, '_blank')}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <EyeIcon className="w-4 h-4" />
            プレビューを開く
          </button>
        </div>
      )}

      {/* Public URL */}
      {isPublished && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            公開URL
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={`https://app.diagnoleads.com/a/${assessment.id}`}
              readOnly
              className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg bg-gray-50"
            />
            <button
              onClick={handleCopyPublicUrl}
              className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              title="コピー"
            >
              <ShareIcon className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Embed Code */}
      {isPublished && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            埋め込みコード
          </label>
          <button
            onClick={handleCopyEmbedCode}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <CodeIcon className="w-4 h-4" />
            埋め込みコードをコピー
          </button>
          <p className="text-xs text-gray-500 mt-2">
            このコードをWebサイトに貼り付けてください
          </p>
        </div>
      )}

      {/* Statistics */}
      <div className="border-t border-gray-200 pt-4">
        <h4 className="text-sm font-medium text-gray-700 mb-3">統計情報</h4>
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">質問数</span>
            <span className="font-medium">{assessment.questions.length}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">回答数</span>
            <span className="font-medium">0</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">完了率</span>
            <span className="font-medium">-</span>
          </div>
        </div>
      </div>

      {/* Help */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="text-sm font-medium text-blue-900 mb-2">💡 ヒント</h4>
        <ul className="text-xs text-blue-800 space-y-1">
          <li>• 質問は左側で並び替えできます</li>
          <li>• スコアで自動的にホットリード判定</li>
          <li>• 公開後も編集可能です</li>
        </ul>
      </div>
    </div>
  );
}
