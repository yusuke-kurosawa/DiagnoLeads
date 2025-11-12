# Feature Specification: Assessment Features

**Version**: 1.0  
**Status**: Proposal  
**Last Updated**: 2025-11-11  
**Related Proposal**: [core-features-proposal.md](./core-features-proposal.md)

---

## Overview

DiagnoLeadsの診断機能の完全な仕様を定義します。診断の作成、編集、公開、ビルダーUI、バージョン管理を含みます。

---

## User Stories

### US-ASSESS-1: 診断一覧表示
**As a** テナント管理者  
**I want to** 自分のテナントの診断一覧を見たい  
**So that** 既存の診断を管理できる

**Acceptance Criteria:**
- [ ] 診断一覧がテーブル形式で表示される
- [ ] 各診断に以下の情報が表示される: タイトル、ステータス、作成日、更新日、完了数
- [ ] 「新規作成」ボタンが表示される
- [ ] 検索・フィルタリング機能がある

### US-ASSESS-2: 診断作成
**As a** テナント管理者  
**I want to** 新しい診断を作成したい  
**So that** 顧客にアセスメントを提供できる

**Acceptance Criteria:**
- [ ] 「新規作成」ボタンで作成ページに遷移
- [ ] 基本情報フォーム（タイトル、説明、カテゴリ）
- [ ] 質問追加機能
- [ ] 回答選択肢追加機能
- [ ] 下書き保存機能
- [ ] 公開/非公開切り替え

### US-ASSESS-3: 診断ビルダー
**As a** テナント管理者  
**I want to** ビジュアルエディタで診断を構築したい  
**So that** コーディング不要で複雑な診断を作成できる

**Acceptance Criteria:**
- [ ] ドラッグ&ドロップで質問を並び替え
- [ ] 質問タイプの選択（単一選択、複数選択、自由記述）
- [ ] 条件分岐の設定
- [ ] スコアリングルールの設定
- [ ] プレビュー機能

### US-ASSESS-4: 診断編集
**As a** テナント管理者  
**I want to** 既存の診断を編集したい  
**So that** 内容を改善・更新できる

**Acceptance Criteria:**
- [ ] 一覧から診断を選択して編集ページに遷移
- [ ] 既存の情報が入力された状態で表示
- [ ] 変更を保存できる
- [ ] 変更を破棄できる（確認ダイアログ）

### US-ASSESS-5: 診断公開管理
**As a** テナント管理者  
**I want to** 診断の公開/非公開を管理したい  
**So that** 準備が整ったものだけを公開できる

**Acceptance Criteria:**
- [ ] 公開/非公開ステータスの切り替え
- [ ] 公開前のバリデーション（必須項目チェック）
- [ ] 公開URLの表示・コピー
- [ ] 埋め込みコードの生成

---

## Functional Requirements

### FR-ASSESS-1: Assessment List Page

**表示内容:**
| カラム | 説明 | ソート可否 |
|--------|------|----------|
| タイトル | 診断名 | ✅ |
| ステータス | 下書き/公開中/非公開 | ✅ |
| 完了数 | 診断完了回数 | ✅ |
| 作成日 | 作成日時 | ✅ |
| 更新日 | 最終更新日時 | ✅ |
| アクション | 編集/削除/複製/公開切替 | - |

**フィルタリング:**
- ステータスフィルタ（すべて、公開中、下書き、非公開）
- カテゴリフィルタ
- 日付範囲フィルタ

**検索:**
- タイトル・説明文の全文検索
- リアルタイム検索（300msデバウンス）

**ページネーション:**
- デフォルト: 20件/ページ
- オプション: 10, 20, 50, 100件

### FR-ASSESS-2: Assessment Creation Flow

**Step 1: 基本情報**
- タイトル (必須, max 200文字)
- 説明 (任意, max 1000文字)
- カテゴリ (選択, 例: マーケティング、営業、技術)
- タグ (任意, 複数選択)

**Step 2: 質問作成**
- 質問追加ボタン
- 質問タイプ選択:
  - 単一選択（ラジオボタン）
  - 複数選択（チェックボックス）
  - 自由記述（テキストエリア）
  - スライダー（1-10）
- 質問文入力
- 回答選択肢追加（単一/複数選択の場合）
- 必須/任意設定

**Step 3: スコアリング設定**
- 各回答にスコアを設定
- スコアリングロジック:
  - 合計点方式
  - カテゴリ別評価
  - カスタムロジック（将来実装）

**Step 4: 結果ページ設定**
- 結果タイトルテンプレート
- 結果説明テンプレート
- スコア範囲別メッセージ
- リード情報収集フォーム設定

**Step 5: 確認・保存**
- プレビュー表示
- 下書き保存 or 公開

### FR-ASSESS-3: Assessment Builder UI

**左サイドバー: 質問リスト**
- 質問一覧（ドラッグ可能）
- 「質問を追加」ボタン
- 質問の展開/折りたたみ

**中央エリア: エディタ**
- 選択中の質問の編集フォーム
- リアルタイムプレビュー

**右サイドバー: 設定**
- 診断全体の設定
- 公開設定
- 埋め込み設定

**ドラッグ&ドロップ機能:**
```typescript
// 質問の並び替え
onDragEnd = (result) => {
  const newQuestions = reorder(
    questions,
    result.source.index,
    result.destination.index
  );
  setQuestions(newQuestions);
};
```

### FR-ASSESS-4: Assessment Status Management

**ステータス遷移:**
```
下書き (draft)
   ↓ (公開)
公開中 (published)
   ↓ (非公開化)
非公開 (unpublished)
   ↓ (再公開)
公開中 (published)
```

**公開前チェック:**
- [ ] 最低1つの質問が存在
- [ ] すべての質問に回答選択肢がある（自由記述を除く）
- [ ] タイトルが設定されている
- [ ] スコアリングルールが設定されている

---

## Non-Functional Requirements

### NFR-ASSESS-1: Performance
- 診断一覧ロード < 1秒
- ビルダーUI操作レスポンス < 100ms
- ドラッグ&ドロップスムーズ (60fps)
- オートセーブ: 3秒おき

### NFR-ASSESS-2: Data Validation
- フロントエンド: Zodバリデーション
- バックエンド: Pydanticバリデーション
- リアルタイムエラー表示

### NFR-ASSESS-3: Accessibility
- キーボード操作のみで診断作成可能
- スクリーンリーダー対応
- ARIA属性適用

---

## API Endpoints

### List Assessments
```
GET /api/v1/tenants/{tenant_id}/assessments
Query Parameters:
  - status: string (draft, published, unpublished)
  - category: string
  - search: string
  - page: number (default: 1)
  - limit: number (default: 20)
  - sort_by: string (created_at, updated_at, title)
  - sort_order: string (asc, desc)

Response: {
  "assessments": [
    {
      "id": "uuid",
      "title": "診断タイトル",
      "description": "説明",
      "status": "published",
      "category": "marketing",
      "completion_count": 150,
      "created_at": "2025-11-11T10:00:00Z",
      "updated_at": "2025-11-11T12:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "limit": 20
}
```

### Get Assessment Detail
```
GET /api/v1/tenants/{tenant_id}/assessments/{assessment_id}

Response: {
  "id": "uuid",
  "title": "診断タイトル",
  "description": "説明",
  "status": "published",
  "category": "marketing",
  "questions": [
    {
      "id": "uuid",
      "order": 1,
      "text": "質問文",
      "type": "single_choice",
      "required": true,
      "options": [
        {
          "id": "uuid",
          "text": "選択肢1",
          "score": 10
        }
      ]
    }
  ],
  "scoring_rules": {...},
  "result_template": {...}
}
```

### Create Assessment
```
POST /api/v1/tenants/{tenant_id}/assessments
Body: {
  "title": "診断タイトル",
  "description": "説明",
  "category": "marketing",
  "status": "draft"
}

Response: {
  "id": "uuid",
  "title": "診断タイトル",
  ...
}
```

### Update Assessment
```
PUT /api/v1/tenants/{tenant_id}/assessments/{assessment_id}
Body: {
  "title": "更新後タイトル",
  ...
}

Response: {
  "id": "uuid",
  "title": "更新後タイトル",
  ...
}
```

### Publish Assessment
```
POST /api/v1/tenants/{tenant_id}/assessments/{assessment_id}/publish

Response: {
  "id": "uuid",
  "status": "published",
  "published_url": "https://diagnoleads.com/a/{short_id}"
}
```

### Unpublish Assessment
```
POST /api/v1/tenants/{tenant_id}/assessments/{assessment_id}/unpublish

Response: {
  "id": "uuid",
  "status": "unpublished"
}
```

### Delete Assessment
```
DELETE /api/v1/tenants/{tenant_id}/assessments/{assessment_id}

Response: 204 No Content
```

---

## UI/UX Design

### Assessment List Page

**Layout:**
```
┌─────────────────────────────────────────────────┐
│  診断管理                    [+ 新規作成]        │
├─────────────────────────────────────────────────┤
│ [検索]  [ステータス▼] [カテゴリ▼]              │
├─────────────────────────────────────────────────┤
│ タイトル     │ ステータス │ 完了数 │ 更新日     │
├──────────────┼───────────┼────────┼─────────────┤
│ 営業課題診断 │ 🟢 公開中 │  150  │ 2025-11-10 │
│ IT診断       │ 📝 下書き │   0   │ 2025-11-09 │
└─────────────────────────────────────────────────┘
```

### Assessment Builder Page

**Layout:**
```
┌────┬──────────────────────┬────┐
│質問│                      │設定│
│一覧│   エディタエリア      │    │
│    │                      │    │
│Q1  │  質問文: [テキスト]  │公開│
│Q2  │  タイプ: [選択▼]     │状態│
│Q3  │  選択肢:            │    │
│    │  □ 選択肢1 (10点)   │埋込│
│[+] │  □ 選択肢2 (20点)   │    │
│    │                      │    │
└────┴──────────────────────┴────┘
```

### Question Types UI

**単一選択:**
```
質問: あなたの課題は何ですか？
○ リード獲得が不足 (10点)
○ 商談化率が低い (20点)
○ 営業効率が悪い (15点)
```

**複数選択:**
```
質問: 利用中のツールを選択してください（複数選択可）
☑ Salesforce (5点)
☐ HubSpot (5点)
☑ Marketo (5点)
```

**自由記述:**
```
質問: その他の課題があれば記入してください
[テキストエリア]
```

**スライダー:**
```
質問: 現在の満足度は？
1 ━━━●━━━━ 10
```

---

## Component Structure

### Pages

```typescript
// frontend/src/pages/assessments/AssessmentsPage.tsx
export function AssessmentsPage() {
  const { tenantId } = useParams();
  const { data: assessments, isLoading } = useAssessments(tenantId);
  
  return (
    <Layout>
      <AssessmentListHeader />
      <AssessmentFilters />
      <AssessmentTable assessments={assessments} />
      <Pagination />
    </Layout>
  );
}

// frontend/src/pages/assessments/CreateAssessmentPage.tsx
export function CreateAssessmentPage() {
  const { tenantId } = useParams();
  const navigate = useNavigate();
  const createMutation = useCreateAssessment();
  
  const handleSubmit = async (data: AssessmentFormData) => {
    await createMutation.mutateAsync(data);
    navigate(`/tenants/${tenantId}/assessments`);
  };
  
  return (
    <Layout>
      <AssessmentForm onSubmit={handleSubmit} />
    </Layout>
  );
}

// frontend/src/pages/assessments/EditAssessmentPage.tsx
export function EditAssessmentPage() {
  const { tenantId, assessmentId } = useParams();
  const { data: assessment } = useAssessment(tenantId, assessmentId);
  
  return (
    <Layout>
      <AssessmentBuilder assessment={assessment} />
    </Layout>
  );
}
```

### Components

```typescript
// frontend/src/components/assessments/AssessmentBuilder.tsx
interface AssessmentBuilderProps {
  assessment: Assessment;
}

export function AssessmentBuilder({ assessment }: AssessmentBuilderProps) {
  const [questions, setQuestions] = useState(assessment.questions);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  
  return (
    <div className="grid grid-cols-[250px,1fr,300px]">
      <QuestionList
        questions={questions}
        onReorder={setQuestions}
        onSelect={setSelectedQuestion}
      />
      <QuestionEditor
        question={selectedQuestion}
        onChange={handleQuestionChange}
      />
      <SettingsPanel assessment={assessment} />
    </div>
  );
}

// frontend/src/components/assessments/QuestionEditor.tsx
interface QuestionEditorProps {
  question: Question | null;
  onChange: (question: Question) => void;
}

export function QuestionEditor({ question, onChange }: QuestionEditorProps) {
  if (!question) {
    return <EmptyState message="質問を選択してください" />;
  }
  
  return (
    <div className="p-6">
      <Input
        label="質問文"
        value={question.text}
        onChange={(e) => onChange({ ...question, text: e.target.value })}
      />
      <Select
        label="質問タイプ"
        value={question.type}
        onChange={(value) => onChange({ ...question, type: value })}
        options={[
          { label: '単一選択', value: 'single_choice' },
          { label: '複数選択', value: 'multiple_choice' },
          { label: '自由記述', value: 'text' },
          { label: 'スライダー', value: 'slider' },
        ]}
      />
      {question.type === 'single_choice' && (
        <OptionsEditor
          options={question.options}
          onChange={(options) => onChange({ ...question, options })}
        />
      )}
    </div>
  );
}
```

---

## State Management

### Assessment Store (Zustand + TanStack Query)

```typescript
// frontend/src/services/assessmentService.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export function useAssessments(tenantId: string) {
  return useQuery({
    queryKey: ['assessments', tenantId],
    queryFn: () => assessmentService.list(tenantId),
  });
}

export function useAssessment(tenantId: string, assessmentId: string) {
  return useQuery({
    queryKey: ['assessment', tenantId, assessmentId],
    queryFn: () => assessmentService.get(tenantId, assessmentId),
  });
}

export function useCreateAssessment() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: assessmentService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessments'] });
    },
  });
}

export function useUpdateAssessment() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: assessmentService.update,
    onSuccess: (data) => {
      queryClient.setQueryData(['assessment', data.tenant_id, data.id], data);
    },
  });
}

export function usePublishAssessment() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: assessmentService.publish,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessments'] });
    },
  });
}
```

---

## Business Logic

### Auto-save Logic
```typescript
// Debounced auto-save every 3 seconds
const debouncedSave = useDebouncedCallback(
  (assessment: Assessment) => {
    updateAssessmentMutation.mutate(assessment);
  },
  3000
);

useEffect(() => {
  if (isDirty) {
    debouncedSave(assessment);
  }
}, [assessment, isDirty]);
```

### Validation Logic
```typescript
// Zod schema
const assessmentSchema = z.object({
  title: z.string().min(1).max(200),
  description: z.string().max(1000).optional(),
  category: z.string().min(1),
  questions: z.array(z.object({
    text: z.string().min(1),
    type: z.enum(['single_choice', 'multiple_choice', 'text', 'slider']),
    required: z.boolean(),
    options: z.array(z.object({
      text: z.string().min(1),
      score: z.number(),
    })).min(2).when('type', {
      is: (val: string) => ['single_choice', 'multiple_choice'].includes(val),
      then: (schema) => schema,
      otherwise: (schema) => schema.optional(),
    }),
  })).min(1),
});

// Validation function
function validateAssessment(assessment: Assessment): ValidationResult {
  try {
    assessmentSchema.parse(assessment);
    return { valid: true, errors: [] };
  } catch (error) {
    return { valid: false, errors: error.errors };
  }
}
```

---

## Testing Strategy

### Unit Tests

**AssessmentBuilder Component:**
- [ ] Renders question list
- [ ] Adds new question
- [ ] Deletes question
- [ ] Reorders questions via drag and drop
- [ ] Updates question on edit

**QuestionEditor Component:**
- [ ] Renders different question types
- [ ] Validates input
- [ ] Shows error messages

**Auto-save Hook:**
- [ ] Debounces correctly
- [ ] Saves after 3 seconds of inactivity
- [ ] Cancels save on unmount

### Integration Tests

**Assessment Creation Flow:**
1. Click "新規作成"
2. Fill in form
3. Add questions
4. Save as draft
5. Verify assessment appears in list

**Assessment Publishing:**
1. Edit assessment
2. Click "公開"
3. Verify validation
4. Confirm publish
5. Verify status changed to "published"

### E2E Tests

**Complete Assessment Creation:**
1. Login
2. Navigate to assessments
3. Create new assessment
4. Add 3 questions
5. Configure scoring
6. Publish
7. Verify public URL works

---

## Implementation Notes

### Critical Considerations

**1. Performance:**
- Large assessments (>50 questions) require virtualization
- Debounced auto-save to avoid excessive API calls
- Optimistic updates for better UX

**2. Data Consistency:**
- Conflict resolution for concurrent edits (future: use WebSocket)
- Version history tracking
- Audit log for changes

**3. User Experience:**
- Clear save indicators
- Unsaved changes warning on navigation
- Keyboard shortcuts (Ctrl+S to save, etc.)

**4. Multi-Tenant:**
- すべてのAPIコールにtenantId含める
- テナント間でデータ漏洩がないことを検証

---

## Related Specifications

- [System Core Features](./system-core.md)
- [Lead Management Features](./lead-management-features.md)
- [AI Support](../../specs/features/ai-support.md)
- [Embed Widget](../../specs/features/embed-widget.md)

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-11 | 1.0 | Initial specification |

---

**Status**: ✅ Ready for Review  
**Next Steps**: Review → Approve → Implement
