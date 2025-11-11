/**
 * Assessment Builder Component
 * 
 * Visual builder for creating and editing assessments with:
 * - Drag & drop question reordering
 * - Question editor
 * - Real-time preview
 * - Auto-save functionality
 */

import { useState, useEffect } from 'react';
import { QuestionList } from './QuestionList';
import { QuestionEditor } from './QuestionEditor';
import { SettingsPanel } from './SettingsPanel';
import type { Assessment, AssessmentQuestion } from '../../services/assessmentService';

type Question = AssessmentQuestion;

interface AssessmentBuilderProps {
  assessment: Assessment;
  onUpdate?: (assessment: Assessment) => void;
  onSave?: (assessment: Assessment) => Promise<void>;
  onPublish?: () => Promise<void>;
  onUnpublish?: () => Promise<void>;
}

export function AssessmentBuilder({ 
  assessment, 
  onUpdate,
  onSave,
  onPublish,
  onUnpublish
}: AssessmentBuilderProps) {
  const [questions, setQuestions] = useState<Question[]>(assessment.questions || []);
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(
    questions.length > 0 ? questions[0] : null
  );
  const [isDirty, setIsDirty] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

  // Auto-save functionality (debounced)
  useEffect(() => {
    if (!isDirty || !onSave) return;

    const timeoutId = setTimeout(async () => {
      setIsSaving(true);
      try {
        await onSave({
          ...assessment,
          questions,
        });
        setLastSaved(new Date());
        setIsDirty(false);
      } catch (error) {
        console.error('Auto-save failed:', error);
      } finally {
        setIsSaving(false);
      }
    }, 3000); // 3 second debounce

    return () => clearTimeout(timeoutId);
  }, [isDirty, questions, assessment, onSave]);

  const handleQuestionsReorder = (newQuestions: Question[]) => {
    setQuestions(newQuestions);
    setIsDirty(true);
    if (onUpdate) {
      onUpdate({ ...assessment, questions: newQuestions });
    }
  };

  const handleQuestionSelect = (question: Question) => {
    setSelectedQuestion(question);
  };

  const handleQuestionChange = (updatedQuestion: Question) => {
    const newQuestions = questions.map(q =>
      q.id === updatedQuestion.id ? updatedQuestion : q
    );
    setQuestions(newQuestions);
    setSelectedQuestion(updatedQuestion);
    setIsDirty(true);
    if (onUpdate) {
      onUpdate({ ...assessment, questions: newQuestions });
    }
  };

  const handleAddQuestion = () => {
    const newQuestion: Question = {
      id: `q-${Date.now()}`,
      order: questions.length + 1,
      text: '新しい質問',
      type: 'single_choice',
      required: false,
      options: [
        { id: `opt-${Date.now()}-1`, text: '選択肢1', score: 0 },
        { id: `opt-${Date.now()}-2`, text: '選択肢2', score: 0 },
      ],
    };
    
    const newQuestions = [...questions, newQuestion];
    setQuestions(newQuestions);
    setSelectedQuestion(newQuestion);
    setIsDirty(true);
    if (onUpdate) {
      onUpdate({ ...assessment, questions: newQuestions });
    }
  };

  const handleDeleteQuestion = (questionId: string) => {
    const newQuestions = questions.filter(q => q.id !== questionId);
    setQuestions(newQuestions);
    if (selectedQuestion?.id === questionId) {
      setSelectedQuestion(newQuestions.length > 0 ? newQuestions[0] : null);
    }
    setIsDirty(true);
    if (onUpdate) {
      onUpdate({ ...assessment, questions: newQuestions });
    }
  };

  return (
    <div className="h-screen flex flex-col">
      {/* Top bar with save status */}
      <div className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">
            {assessment.title}
          </h2>
          <p className="text-sm text-gray-500">
            {questions.length} 個の質問
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          {/* Save status */}
          <div className="text-sm">
            {isSaving && (
              <span className="text-blue-600">保存中...</span>
            )}
            {!isSaving && isDirty && (
              <span className="text-yellow-600">未保存の変更</span>
            )}
            {!isSaving && !isDirty && lastSaved && (
              <span className="text-gray-500">
                最終保存: {lastSaved.toLocaleTimeString('ja-JP')}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Main builder area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Question List */}
        <div className="w-80 bg-gray-50 border-r border-gray-200 flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <button
              onClick={handleAddQuestion}
              className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              + 質問を追加
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto">
            <QuestionList
              questions={questions}
              selectedQuestion={selectedQuestion}
              onReorder={handleQuestionsReorder}
              onSelect={handleQuestionSelect}
              onDelete={handleDeleteQuestion}
            />
          </div>
        </div>

        {/* Center: Question Editor */}
        <div className="flex-1 bg-white overflow-y-auto">
          {selectedQuestion ? (
            <QuestionEditor
              question={selectedQuestion}
              onChange={handleQuestionChange}
            />
          ) : (
            <div className="flex items-center justify-center h-full text-gray-500">
              <div className="text-center">
                <p className="text-lg mb-2">質問が選択されていません</p>
                <p className="text-sm">
                  左側から質問を選択するか、新しい質問を追加してください
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Right: Settings Panel */}
        <div className="w-80 bg-gray-50 border-l border-gray-200 overflow-y-auto">
          <SettingsPanel 
            assessment={assessment} 
            onPublish={onPublish}
            onUnpublish={onUnpublish}
          />
        </div>
      </div>
    </div>
  );
}
