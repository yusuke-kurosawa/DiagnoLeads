/**
 * Question List Component
 * 
 * Displays a draggable list of questions with:
 * - Drag & drop reordering
 * - Question type icons
 * - Selection highlighting
 * - Delete actions
 */

import React from 'react';
import { 
  GripVerticalIcon, 
  Trash2Icon, 
  CheckSquareIcon, 
  CheckCircle2Icon,
  TypeIcon,
  SlidersIcon
} from 'lucide-react';

interface Question {
  id: string;
  order: number;
  text: string;
  type: 'single_choice' | 'multiple_choice' | 'text' | 'slider';
  required: boolean;
  options?: QuestionOption[];
}

interface QuestionOption {
  id: string;
  text: string;
  score: number;
}

interface QuestionListProps {
  questions: Question[];
  selectedQuestion: Question | null;
  onReorder: (questions: Question[]) => void;
  onSelect: (question: Question) => void;
  onDelete: (questionId: string) => void;
}

const getQuestionTypeIcon = (type: Question['type']) => {
  switch (type) {
    case 'single_choice':
      return CheckCircle2Icon;
    case 'multiple_choice':
      return CheckSquareIcon;
    case 'text':
      return TypeIcon;
    case 'slider':
      return SlidersIcon;
    default:
      return CheckCircle2Icon;
  }
};

const getQuestionTypeLabel = (type: Question['type']) => {
  switch (type) {
    case 'single_choice':
      return '単一選択';
    case 'multiple_choice':
      return '複数選択';
    case 'text':
      return '自由記述';
    case 'slider':
      return 'スライダー';
    default:
      return '不明';
  }
};

export function QuestionList({
  questions,
  selectedQuestion,
  onReorder,
  onSelect,
  onDelete,
}: QuestionListProps) {
  const [draggedIndex, setDraggedIndex] = React.useState<number | null>(null);

  const handleDragStart = (e: React.DragEvent, index: number) => {
    setDraggedIndex(index);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === index) return;

    const newQuestions = [...questions];
    const draggedQuestion = newQuestions[draggedIndex];
    newQuestions.splice(draggedIndex, 1);
    newQuestions.splice(index, 0, draggedQuestion);

    // Update order numbers
    const reorderedQuestions = newQuestions.map((q, i) => ({
      ...q,
      order: i + 1,
    }));

    setDraggedIndex(index);
    onReorder(reorderedQuestions);
  };

  const handleDragEnd = () => {
    setDraggedIndex(null);
  };

  const handleDelete = (e: React.MouseEvent, questionId: string) => {
    e.stopPropagation();
    if (window.confirm('この質問を削除しますか？')) {
      onDelete(questionId);
    }
  };

  return (
    <div className="space-y-2 p-4">
      {questions.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p className="text-sm">質問がありません</p>
          <p className="text-xs mt-1">「質問を追加」ボタンをクリックしてください</p>
        </div>
      ) : (
        questions.map((question, index) => {
          const Icon = getQuestionTypeIcon(question.type);
          const isSelected = selectedQuestion?.id === question.id;

          return (
            <div
              key={question.id}
              draggable
              onDragStart={(e) => handleDragStart(e, index)}
              onDragOver={(e) => handleDragOver(e, index)}
              onDragEnd={handleDragEnd}
              onClick={() => onSelect(question)}
              className={`
                group relative bg-white border rounded-lg p-3 cursor-pointer
                transition-all duration-200
                ${isSelected 
                  ? 'border-blue-500 shadow-md ring-2 ring-blue-200' 
                  : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
                }
                ${draggedIndex === index ? 'opacity-50' : ''}
              `}
            >
              {/* Drag handle */}
              <div className="absolute left-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
                <GripVerticalIcon className="w-4 h-4 text-gray-400" />
              </div>

              {/* Question number */}
              <div className="flex items-start gap-3 pl-4">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center text-xs font-semibold text-gray-700">
                  {index + 1}
                </div>

                <div className="flex-1 min-w-0">
                  {/* Question text */}
                  <p className="text-sm font-medium text-gray-900 truncate mb-1">
                    {question.text}
                  </p>

                  {/* Question type badge */}
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1 text-xs text-gray-500">
                      <Icon className="w-3 h-3" />
                      <span>{getQuestionTypeLabel(question.type)}</span>
                    </div>

                    {question.required && (
                      <span className="text-xs text-red-500">必須</span>
                    )}

                    {question.options && (
                      <span className="text-xs text-gray-400">
                        {question.options.length}個の選択肢
                      </span>
                    )}
                  </div>
                </div>

                {/* Delete button */}
                <button
                  onClick={(e) => handleDelete(e, question.id)}
                  className="flex-shrink-0 opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-600 transition-all"
                  title="削除"
                >
                  <Trash2Icon className="w-4 h-4" />
                </button>
              </div>
            </div>
          );
        })
      )}
    </div>
  );
}
