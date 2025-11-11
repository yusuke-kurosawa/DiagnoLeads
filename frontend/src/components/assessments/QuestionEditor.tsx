/**
 * Question Editor Component
 * 
 * Form for editing question details:
 * - Question text
 * - Question type
 * - Options (for choice types)
 * - Scoring
 * - Required flag
 */

import { useState, useEffect } from 'react';
import { PlusIcon, Trash2Icon } from 'lucide-react';

interface Question {
  id: string;
  order: number;
  text: string;
  type: 'single_choice' | 'multiple_choice' | 'text' | 'slider';
  required: boolean;
  options?: QuestionOption[];
  max_score?: number;
}

interface QuestionOption {
  id: string;
  text: string;
  score: number;
}

interface QuestionEditorProps {
  question: Question;
  onChange: (question: Question) => void;
}

export function QuestionEditor({ question, onChange }: QuestionEditorProps) {
  const [localQuestion, setLocalQuestion] = useState<Question>(question);

  // Update local state when question prop changes
  useEffect(() => {
    setLocalQuestion(question);
  }, [question.id]); // Only update when question ID changes

  const handleChange = (updates: Partial<Question>) => {
    const updated = { ...localQuestion, ...updates };
    setLocalQuestion(updated);
    onChange(updated);
  };

  const handleOptionChange = (optionId: string, updates: Partial<QuestionOption>) => {
    const updatedOptions = localQuestion.options?.map(opt =>
      opt.id === optionId ? { ...opt, ...updates } : opt
    );
    handleChange({ options: updatedOptions });
  };

  const handleAddOption = () => {
    const newOption: QuestionOption = {
      id: `opt-${Date.now()}`,
      text: `選択肢${(localQuestion.options?.length || 0) + 1}`,
      score: 0,
    };
    handleChange({ options: [...(localQuestion.options || []), newOption] });
  };

  const handleDeleteOption = (optionId: string) => {
    const updatedOptions = localQuestion.options?.filter(opt => opt.id !== optionId);
    handleChange({ options: updatedOptions });
  };

  const handleTypeChange = (newType: Question['type']) => {
    const updates: Partial<Question> = { type: newType };
    
    // Add default options for choice types
    if ((newType === 'single_choice' || newType === 'multiple_choice') && !localQuestion.options) {
      updates.options = [
        { id: `opt-${Date.now()}-1`, text: '選択肢1', score: 10 },
        { id: `opt-${Date.now()}-2`, text: '選択肢2', score: 20 },
      ];
    }
    
    // Remove options for non-choice types
    if (newType === 'text' || newType === 'slider') {
      updates.options = undefined;
    }
    
    handleChange(updates);
  };

  const showOptions = localQuestion.type === 'single_choice' || localQuestion.type === 'multiple_choice';

  return (
    <div className="p-6 space-y-6">
      <div className="border-b border-gray-200 pb-4">
        <h3 className="text-lg font-semibold text-gray-900">質問の編集</h3>
        <p className="text-sm text-gray-500 mt-1">
          質問文、タイプ、選択肢を設定してください
        </p>
      </div>

      {/* Question Text */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          質問文 <span className="text-red-500">*</span>
        </label>
        <textarea
          value={localQuestion.text}
          onChange={(e) => handleChange({ text: e.target.value })}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="質問文を入力してください"
        />
      </div>

      {/* Question Type */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          質問タイプ
        </label>
        <select
          value={localQuestion.type}
          onChange={(e) => handleTypeChange(e.target.value as Question['type'])}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="single_choice">単一選択（ラジオボタン）</option>
          <option value="multiple_choice">複数選択（チェックボックス）</option>
          <option value="text">自由記述（テキストエリア）</option>
          <option value="slider">スライダー（1-10）</option>
        </select>
      </div>

      {/* Required Flag */}
      <div className="flex items-center">
        <input
          type="checkbox"
          id="required"
          checked={localQuestion.required}
          onChange={(e) => handleChange({ required: e.target.checked })}
          className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
        />
        <label htmlFor="required" className="ml-2 text-sm text-gray-700">
          必須項目にする
        </label>
      </div>

      {/* Options (for choice types) */}
      {showOptions && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="block text-sm font-medium text-gray-700">
              選択肢とスコア
            </label>
            <button
              onClick={handleAddOption}
              className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700"
            >
              <PlusIcon className="w-4 h-4" />
              追加
            </button>
          </div>

          <div className="space-y-3">
            {localQuestion.options?.map((option, index) => (
              <div key={option.id} className="flex items-start gap-3">
                {/* Option number */}
                <div className="flex-shrink-0 w-6 h-9 flex items-center justify-center text-xs font-semibold text-gray-500">
                  {index + 1}
                </div>

                {/* Option text */}
                <input
                  type="text"
                  value={option.text}
                  onChange={(e) => handleOptionChange(option.id, { text: e.target.value })}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="選択肢のテキスト"
                />

                {/* Score */}
                <div className="flex-shrink-0 w-24">
                  <input
                    type="number"
                    value={option.score}
                    onChange={(e) => handleOptionChange(option.id, { score: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-right"
                    placeholder="点数"
                  />
                </div>

                {/* Delete button */}
                <button
                  onClick={() => handleDeleteOption(option.id)}
                  className="flex-shrink-0 text-gray-400 hover:text-red-600 transition-colors p-2"
                  disabled={localQuestion.options && localQuestion.options.length <= 2}
                  title="削除"
                >
                  <Trash2Icon className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>

          <p className="text-xs text-gray-500 mt-2">
            最低2つの選択肢が必要です。各選択肢にスコアを設定できます。
          </p>
        </div>
      )}

      {/* Slider settings */}
      {localQuestion.type === 'slider' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            最大スコア
          </label>
          <input
            type="number"
            value={localQuestion.max_score || 10}
            onChange={(e) => handleChange({ max_score: parseInt(e.target.value) || 10 })}
            className="w-32 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            min="1"
            max="100"
          />
          <p className="text-xs text-gray-500 mt-1">
            スライダーの最大値（1-100）
          </p>
        </div>
      )}

      {/* Preview */}
      <div className="border-t border-gray-200 pt-4">
        <h4 className="text-sm font-medium text-gray-700 mb-3">プレビュー</h4>
        <div className="bg-gray-50 p-4 rounded-lg">
          <p className="text-sm font-medium text-gray-900 mb-3">
            {localQuestion.text}
            {localQuestion.required && <span className="text-red-500 ml-1">*</span>}
          </p>

          {localQuestion.type === 'single_choice' && (
            <div className="space-y-2">
              {localQuestion.options?.map((option) => (
                <label key={option.id} className="flex items-center gap-2 text-sm">
                  <input type="radio" name="preview" className="w-4 h-4" disabled />
                  <span>{option.text}</span>
                  <span className="text-xs text-gray-500">({option.score}点)</span>
                </label>
              ))}
            </div>
          )}

          {localQuestion.type === 'multiple_choice' && (
            <div className="space-y-2">
              {localQuestion.options?.map((option) => (
                <label key={option.id} className="flex items-center gap-2 text-sm">
                  <input type="checkbox" className="w-4 h-4" disabled />
                  <span>{option.text}</span>
                  <span className="text-xs text-gray-500">({option.score}点)</span>
                </label>
              ))}
            </div>
          )}

          {localQuestion.type === 'text' && (
            <textarea
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              rows={3}
              placeholder="回答を入力してください"
              disabled
            />
          )}

          {localQuestion.type === 'slider' && (
            <div>
              <input
                type="range"
                min="1"
                max={localQuestion.max_score || 10}
                className="w-full"
                disabled
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>1</span>
                <span>{localQuestion.max_score || 10}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
