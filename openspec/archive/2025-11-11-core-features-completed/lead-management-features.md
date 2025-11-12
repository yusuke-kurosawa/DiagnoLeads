# Feature Specification: Lead Management Features

**Version**: 1.0  
**Status**: Proposal  
**Last Updated**: 2025-11-11  
**Related Proposal**: [core-features-proposal.md](./core-features-proposal.md)

---

## Overview

DiagnoLeadsのリード管理機能の完全な仕様を定義します。リードの一覧表示、詳細表示、フィルタリング、ステータス管理、スコアリング、Microsoft Teams通知連携を含みます。

---

## User Stories

### US-LEAD-1: リード一覧表示
**As a** 営業担当者  
**I want to** 獲得したリードの一覧を見たい  
**So that** どのリードにフォローアップすべきか判断できる

**Acceptance Criteria:**
- [ ] リード一覧がテーブル形式で表示される
- [ ] 各リードに以下の情報が表示される: 名前、会社、スコア、ステータス、獲得日
- [ ] スコア順にソート可能
- [ ] ホットリード（スコア >= 80）がハイライト表示

### US-LEAD-2: ホットリード優先表示
**As a** 営業担当者  
**I want to** ホットリード（高スコア）を優先的に確認したい  
**So that** 最も見込みの高いリードに素早くアプローチできる

**Acceptance Criteria:**
- [ ] ホットリードフィルタ（スコア >= 80）
- [ ] ホットリードバッジ表示（🔥アイコン）
- [ ] スコア降順でデフォルトソート

### US-LEAD-3: リード詳細表示
**As a** 営業担当者  
**I want to** リードの詳細情報を確認したい  
**So that** 適切なアプローチ方法を決定できる

**Acceptance Criteria:**
- [ ] リードの基本情報（名前、会社、役職、連絡先）
- [ ] 診断結果（完了した診断、回答内容）
- [ ] スコア詳細（スコアの内訳）
- [ ] アクティビティ履歴（ステータス変更、メモ追加）
- [ ] 関連する診断への参照

### US-LEAD-4: リードフィルタリング
**As a** 営業担当者  
**I want to** リードをフィルタリング・検索したい  
**So that** 特定の条件に合うリードを素早く見つけられる

**Acceptance Criteria:**
- [ ] ステータスフィルタ（新規、コンタクト済み、商談中、成約、失注）
- [ ] スコア範囲フィルタ（例: 80-100）
- [ ] 日付範囲フィルタ（獲得日、最終アクティビティ日）
- [ ] 診断別フィルタ
- [ ] 会社名・名前の検索

### US-LEAD-5: リードステータス管理
**As a** 営業担当者  
**I want to** リードのステータスを更新したい  
**So that** 営業プロセスを管理できる

**Acceptance Criteria:**
- [ ] ステータス変更ドロップダウン
- [ ] ステータス変更履歴の記録
- [ ] ステータス変更時のメモ入力（任意）

### US-LEAD-6: リード手動作成
**As a** 営業担当者  
**I want to** 診断とは別に手動でリードを作成したい  
**So that** イベント等で獲得した名刺情報を管理できる

**Acceptance Criteria:**
- [ ] リード作成フォーム
- [ ] 必須項目: 名前、メールアドレス
- [ ] 任意項目: 会社、役職、電話番号、スコア
- [ ] 作成後、リード一覧に表示

### US-LEAD-7: Teams通知
**As a** 営業担当者  
**I want to** ホットリードが発生したらMicrosoft Teamsで通知を受けたい  
**So that** 即座にフォローアップできる

**Acceptance Criteria:**
- [ ] スコア >= 80のリード作成時に自動通知
- [ ] スコア更新で閾値を超えた時に通知
- [ ] 通知にリード詳細（名前、会社、スコア）を含む
- [ ] リード詳細ページへの直リンク

---

## Functional Requirements

### FR-LEAD-1: Lead List Page

**表示内容:**
| カラム | 説明 | ソート可否 | フィルタ可否 |
|--------|------|-----------|-------------|
| 🔥 | ホットリードアイコン | - | ✅ |
| 名前 | リード名 | ✅ | - |
| 会社 | 会社名 | ✅ | - |
| スコア | 0-100 | ✅ | ✅ |
| ステータス | 営業ステータス | ✅ | ✅ |
| 診断 | 完了した診断名 | ✅ | ✅ |
| 獲得日 | リード獲得日時 | ✅ | ✅ |
| アクション | 詳細/編集/削除 | - | - |

**フィルタリング:**
```typescript
interface LeadFilters {
  status?: LeadStatus[];          // ['new', 'contacted', ...]
  score_min?: number;             // 0-100
  score_max?: number;             // 0-100
  is_hot?: boolean;               // スコア >= 80
  assessment_id?: string;         // 診断IDでフィルタ
  created_after?: string;         // ISO 8601
  created_before?: string;        // ISO 8601
  search?: string;                // 名前・会社名の検索
}
```

**ソート:**
```typescript
interface LeadSort {
  sort_by: 'score' | 'created_at' | 'name' | 'company' | 'status';
  sort_order: 'asc' | 'desc';
}
```

**ページネーション:**
- デフォルト: 20件/ページ
- オプション: 10, 20, 50, 100件

### FR-LEAD-2: Lead Detail Page

**表示セクション:**

**1. 基本情報カード**
```
┌──────────────────────────────────────┐
│  🔥 ホットリード                     │
│  テスト太郎                          │
│  テスト株式会社 - マーケティング部長  │
│  📧 test@example.com                │
│  📞 03-1234-5678                    │
│  📊 スコア: 95/100                  │
│  📅 獲得日: 2025-11-10 14:30       │
└──────────────────────────────────────┘
```

**2. ステータス管理**
```
┌──────────────────────────────────────┐
│  現在のステータス: [新規 ▼]         │
│  担当者: [未割当 ▼]                 │
│  [ステータスを更新]                 │
└──────────────────────────────────────┘
```

**3. 診断結果**
```
┌──────────────────────────────────────┐
│  完了した診断                        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  📋 営業課題診断                    │
│     完了日: 2025-11-10 14:25       │
│     スコア: 95/100                 │
│     [詳細を見る]                    │
└──────────────────────────────────────┘
```

**4. スコア内訳**
```
┌──────────────────────────────────────┐
│  スコア内訳                          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  質問1: あなたの課題は？             │
│  回答: リード獲得が不足              │
│  配点: 20/25                        │
│  ─────────────────────────────────  │
│  質問2: 利用中のツールは？           │
│  回答: Salesforce, HubSpot          │
│  配点: 15/20                        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  合計: 95/100                       │
└──────────────────────────────────────┘
```

**5. アクティビティ履歴**
```
┌──────────────────────────────────────┐
│  アクティビティ履歴                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  ⏰ 2025-11-11 10:00               │
│  ステータス変更: 新規 → コンタクト済み │
│  by 営業太郎                        │
│  ─────────────────────────────────  │
│  ⏰ 2025-11-10 14:30               │
│  リード獲得（診断完了）              │
│  診断: 営業課題診断                  │
└──────────────────────────────────────┘
```

**6. メモ**
```
┌──────────────────────────────────────┐
│  メモ                    [+ 追加]    │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  📝 2025-11-11 10:15               │
│  電話でコンタクト。来週面談予定。    │
│  by 営業太郎                        │
└──────────────────────────────────────┘
```

### FR-LEAD-3: Lead Status Workflow

**ステータス定義:**
```typescript
enum LeadStatus {
  NEW = 'new',                  // 新規（未対応）
  CONTACTED = 'contacted',      // コンタクト済み
  QUALIFIED = 'qualified',      // 有望（商談化）
  NEGOTIATION = 'negotiation',  // 商談中
  WON = 'won',                  // 成約
  LOST = 'lost',                // 失注
}
```

**ステータス遷移ルール:**
```
新規 (new)
  ↓
コンタクト済み (contacted)
  ↓
有望 (qualified)
  ↓
商談中 (negotiation)
  ↓ ↘
成約 (won)  失注 (lost)
```

**自動ステータス更新:**
- リード獲得時: 自動的に `NEW` に設定
- スコアが80を超えた時: `QUALIFIED` に自動昇格（オプション）

### FR-LEAD-4: Lead Scoring

**スコア算出ロジック:**
```typescript
// 診断回答からスコアを算出
function calculateLeadScore(responses: Response[]): number {
  let totalScore = 0;
  let maxScore = 0;
  
  for (const response of responses) {
    const question = response.question;
    const answer = response.answer;
    
    // 回答の配点を加算
    totalScore += answer.score;
    maxScore += question.max_score;
  }
  
  // 0-100に正規化
  return Math.round((totalScore / maxScore) * 100);
}
```

**スコア更新トリガー:**
1. 診断完了時に自動算出
2. 手動スコア更新（管理者のみ）
3. 複数診断完了時は平均スコア

**ホットリード判定:**
- スコア >= 80: ホットリード（🔥アイコン表示）
- スコア >= 80で自動Teams通知

### FR-LEAD-5: Microsoft Teams Integration

**通知トリガー:**
1. **リード作成時**: スコア >= 80
2. **スコア更新時**: 閾値超え（< 80 → >= 80）

**通知内容（Adaptive Card）:**
```json
{
  "type": "AdaptiveCard",
  "body": [
    {
      "type": "TextBlock",
      "text": "🔥 ホットリード獲得！",
      "weight": "bolder",
      "size": "large"
    },
    {
      "type": "FactSet",
      "facts": [
        { "title": "名前", "value": "テスト太郎" },
        { "title": "会社", "value": "テスト株式会社" },
        { "title": "役職", "value": "マーケティング部長" },
        { "title": "スコア", "value": "95/100" },
        { "title": "診断", "value": "営業課題診断" }
      ]
    }
  ],
  "actions": [
    {
      "type": "Action.OpenUrl",
      "title": "リードを見る",
      "url": "https://app.diagnoleads.com/tenants/{tenant_id}/leads/{lead_id}"
    }
  ]
}
```

**設定:**
- テナント別Webhook URL（`tenant.settings.teams_webhook_url`）
- グローバルフォールバック（`TEAMS_WEBHOOK_URL` 環境変数）

---

## Non-Functional Requirements

### NFR-LEAD-1: Performance
- リード一覧ロード < 1秒
- フィルタリング応答 < 500ms
- ステータス更新 < 300ms
- Teams通知送信 < 2秒（非同期）

### NFR-LEAD-2: Data Privacy
- テナント間でリードデータ漏洩なし
- リードの個人情報は暗号化保存
- GDPR準拠（削除権、忘れられる権利）

### NFR-LEAD-3: Scalability
- 10,000+ リード/テナントでもパフォーマンス維持
- ページネーション必須
- インデックス最適化（tenant_id, score, created_at）

---

## API Endpoints

### List Leads
```
GET /api/v1/tenants/{tenant_id}/leads
Query Parameters:
  - status: string[] (new, contacted, qualified, ...)
  - score_min: number (0-100)
  - score_max: number (0-100)
  - is_hot: boolean
  - assessment_id: string
  - created_after: string (ISO 8601)
  - created_before: string (ISO 8601)
  - search: string
  - page: number (default: 1)
  - limit: number (default: 20)
  - sort_by: string (score, created_at, name)
  - sort_order: string (asc, desc)

Response: {
  "leads": [
    {
      "id": "uuid",
      "name": "テスト太郎",
      "email": "test@example.com",
      "company": "テスト株式会社",
      "job_title": "マーケティング部長",
      "phone": "03-1234-5678",
      "score": 95,
      "status": "new",
      "is_hot": true,
      "assessment": {
        "id": "uuid",
        "title": "営業課題診断"
      },
      "created_at": "2025-11-10T14:30:00Z",
      "last_activity_at": "2025-11-10T14:30:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 20
}
```

### Get Lead Detail
```
GET /api/v1/tenants/{tenant_id}/leads/{lead_id}

Response: {
  "id": "uuid",
  "name": "テスト太郎",
  "email": "test@example.com",
  "company": "テスト株式会社",
  "job_title": "マーケティング部長",
  "phone": "03-1234-5678",
  "score": 95,
  "status": "new",
  "assigned_to": null,
  "assessment": {
    "id": "uuid",
    "title": "営業課題診断",
    "completed_at": "2025-11-10T14:25:00Z"
  },
  "score_breakdown": [
    {
      "question": "あなたの課題は？",
      "answer": "リード獲得が不足",
      "score": 20,
      "max_score": 25
    }
  ],
  "activities": [
    {
      "id": "uuid",
      "type": "status_change",
      "from_status": "new",
      "to_status": "contacted",
      "user": { "id": "uuid", "name": "営業太郎" },
      "created_at": "2025-11-11T10:00:00Z"
    }
  ],
  "notes": [
    {
      "id": "uuid",
      "content": "電話でコンタクト。来週面談予定。",
      "user": { "id": "uuid", "name": "営業太郎" },
      "created_at": "2025-11-11T10:15:00Z"
    }
  ],
  "created_at": "2025-11-10T14:30:00Z",
  "last_activity_at": "2025-11-11T10:15:00Z"
}
```

### Create Lead (Manual)
```
POST /api/v1/tenants/{tenant_id}/leads
Body: {
  "name": "手動リード",
  "email": "manual@example.com",
  "company": "手動株式会社",
  "job_title": "部長",
  "phone": "03-5678-1234",
  "score": 70
}

Response: {
  "id": "uuid",
  "name": "手動リード",
  ...
}
```

### Update Lead Status
```
PATCH /api/v1/tenants/{tenant_id}/leads/{lead_id}/status
Body: {
  "status": "contacted",
  "note": "電話でコンタクト済み"
}

Response: {
  "id": "uuid",
  "status": "contacted",
  "last_activity_at": "2025-11-11T10:00:00Z"
}
```

### Update Lead Score
```
PATCH /api/v1/tenants/{tenant_id}/leads/{lead_id}/score
Body: {
  "score": 90
}

Response: {
  "id": "uuid",
  "score": 90,
  "is_hot": true
}
```

### Add Lead Note
```
POST /api/v1/tenants/{tenant_id}/leads/{lead_id}/notes
Body: {
  "content": "メモ内容"
}

Response: {
  "id": "uuid",
  "content": "メモ内容",
  "user": { "id": "uuid", "name": "営業太郎" },
  "created_at": "2025-11-11T10:15:00Z"
}
```

### Delete Lead
```
DELETE /api/v1/tenants/{tenant_id}/leads/{lead_id}

Response: 204 No Content
```

---

## UI/UX Design

### Lead List Page

**Layout:**
```
┌──────────────────────────────────────────────────┐
│  リード管理              [+ 手動作成] [エクスポート] │
├──────────────────────────────────────────────────┤
│ [検索] [ステータス▼] [スコア▼] [診断▼] [日付▼]  │
├──────────────────────────────────────────────────┤
│ 🔥│名前      │会社    │スコア│ステータス│獲得日  │
├──┼──────────┼────────┼──────┼──────────┼────────┤
│ 🔥│テスト太郎│テスト㈱│ 95   │新規     │11/10   │
│   │鈴木花子  │ABC㈱   │ 75   │コンタクト│11/09   │
└──────────────────────────────────────────────────┘
```

**ホットリードハイライト:**
- 背景色: `bg-orange-50`
- 境界線: `border-l-4 border-orange-500`
- アイコン: 🔥

### Lead Detail Page

**タブ構成:**
```
┌──────────────────────────────────────────┐
│  テスト太郎 (テスト株式会社)             │
│  [概要] [診断結果] [アクティビティ]      │
├──────────────────────────────────────────┤
│  (選択されたタブの内容)                  │
└──────────────────────────────────────────┘
```

---

## Component Structure

### Pages

```typescript
// frontend/src/pages/leads/LeadsPage.tsx
export function LeadsPage() {
  const { tenantId } = useParams();
  const [filters, setFilters] = useState<LeadFilters>({});
  const { data: leads, isLoading } = useLeads(tenantId, filters);
  
  return (
    <Layout>
      <LeadListHeader />
      <LeadFilters filters={filters} onChange={setFilters} />
      <LeadTable leads={leads} />
      <Pagination />
    </Layout>
  );
}

// frontend/src/pages/leads/LeadDetailPage.tsx
export function LeadDetailPage() {
  const { tenantId, leadId } = useParams();
  const { data: lead } = useLead(tenantId, leadId);
  const [activeTab, setActiveTab] = useState('overview');
  
  return (
    <Layout>
      <LeadHeader lead={lead} />
      <Tabs value={activeTab} onChange={setActiveTab}>
        <Tab value="overview">概要</Tab>
        <Tab value="assessment">診断結果</Tab>
        <Tab value="activity">アクティビティ</Tab>
      </Tabs>
      <TabContent activeTab={activeTab} lead={lead} />
    </Layout>
  );
}
```

### Components

```typescript
// frontend/src/components/leads/LeadTable.tsx
interface LeadTableProps {
  leads: Lead[];
}

export function LeadTable({ leads }: LeadTableProps) {
  return (
    <table className="w-full">
      <thead>
        <tr>
          <th></th>
          <th>名前</th>
          <th>会社</th>
          <th>スコア</th>
          <th>ステータス</th>
          <th>獲得日</th>
          <th>アクション</th>
        </tr>
      </thead>
      <tbody>
        {leads.map(lead => (
          <LeadRow key={lead.id} lead={lead} />
        ))}
      </tbody>
    </table>
  );
}

// frontend/src/components/leads/LeadRow.tsx
interface LeadRowProps {
  lead: Lead;
}

export function LeadRow({ lead }: LeadRowProps) {
  const isHot = lead.score >= 80;
  
  return (
    <tr className={isHot ? 'bg-orange-50 border-l-4 border-orange-500' : ''}>
      <td>{isHot && '🔥'}</td>
      <td>
        <Link to={`/tenants/${lead.tenant_id}/leads/${lead.id}`}>
          {lead.name}
        </Link>
      </td>
      <td>{lead.company}</td>
      <td>
        <LeadScoreBadge score={lead.score} />
      </td>
      <td>
        <LeadStatusBadge status={lead.status} />
      </td>
      <td>{formatDate(lead.created_at)}</td>
      <td>
        <LeadActionMenu lead={lead} />
      </td>
    </tr>
  );
}

// frontend/src/components/leads/LeadScoreBadge.tsx
interface LeadScoreBadgeProps {
  score: number;
}

export function LeadScoreBadge({ score }: LeadScoreBadgeProps) {
  const color = score >= 80 ? 'red' : score >= 60 ? 'yellow' : 'gray';
  
  return (
    <Badge color={color}>
      {score}
    </Badge>
  );
}

// frontend/src/components/leads/LeadFilters.tsx
interface LeadFiltersProps {
  filters: LeadFilters;
  onChange: (filters: LeadFilters) => void;
}

export function LeadFilters({ filters, onChange }: LeadFiltersProps) {
  return (
    <div className="flex gap-4">
      <MultiSelect
        label="ステータス"
        options={leadStatusOptions}
        value={filters.status}
        onChange={(status) => onChange({ ...filters, status })}
      />
      <RangeSlider
        label="スコア"
        min={0}
        max={100}
        value={[filters.score_min || 0, filters.score_max || 100]}
        onChange={([min, max]) => onChange({ ...filters, score_min: min, score_max: max })}
      />
      <Select
        label="診断"
        options={assessmentOptions}
        value={filters.assessment_id}
        onChange={(assessment_id) => onChange({ ...filters, assessment_id })}
      />
      <DateRangePicker
        label="獲得日"
        value={[filters.created_after, filters.created_before]}
        onChange={([after, before]) => onChange({ 
          ...filters, 
          created_after: after, 
          created_before: before 
        })}
      />
    </div>
  );
}
```

---

## State Management

### Lead Queries (TanStack Query)

```typescript
// frontend/src/services/leadService.ts
export function useLeads(tenantId: string, filters: LeadFilters) {
  return useQuery({
    queryKey: ['leads', tenantId, filters],
    queryFn: () => leadService.list(tenantId, filters),
  });
}

export function useLead(tenantId: string, leadId: string) {
  return useQuery({
    queryKey: ['lead', tenantId, leadId],
    queryFn: () => leadService.get(tenantId, leadId),
  });
}

export function useUpdateLeadStatus() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: leadService.updateStatus,
    onSuccess: (data) => {
      queryClient.setQueryData(['lead', data.tenant_id, data.id], data);
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
  });
}

export function useAddLeadNote() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: leadService.addNote,
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ 
        queryKey: ['lead', variables.tenantId, variables.leadId] 
      });
    },
  });
}
```

---

## Business Logic

### Lead Scoring Logic (Backend)
```python
# backend/app/services/lead_service.py
def calculate_lead_score(response: Response) -> int:
    """
    診断回答からリードスコアを算出
    """
    total_score = 0
    max_score = 0
    
    for answer in response.answers:
        question = answer.question
        option = answer.selected_option
        
        total_score += option.score
        max_score += question.max_score
    
    # 0-100に正規化
    normalized_score = round((total_score / max_score) * 100)
    
    return normalized_score

async def create_lead_from_response(
    response: Response,
    tenant_id: UUID
) -> Lead:
    """
    診断回答からリードを作成し、ホットリードの場合はTeams通知
    """
    score = calculate_lead_score(response)
    
    lead = Lead(
        tenant_id=tenant_id,
        name=response.user_info.name,
        email=response.user_info.email,
        company=response.user_info.company,
        job_title=response.user_info.job_title,
        phone=response.user_info.phone,
        score=score,
        status=LeadStatus.NEW,
        assessment_id=response.assessment_id,
    )
    
    db.add(lead)
    db.commit()
    
    # ホットリードの場合、Teams通知
    if score >= 80:
        await send_hot_lead_notification(lead, tenant)
    
    return lead
```

### Teams Notification Logic
```python
# backend/app/services/lead_service.py
async def send_hot_lead_notification(lead: Lead, tenant: Tenant):
    """
    ホットリード通知をTeamsに送信
    """
    webhook_url = (
        tenant.settings.get('teams_webhook_url') or 
        settings.TEAMS_WEBHOOK_URL
    )
    
    if not webhook_url:
        logger.warning(f"No Teams webhook configured for tenant {tenant.id}")
        return
    
    teams_client = TeamsWebhookClient(webhook_url)
    
    try:
        await teams_client.send_hot_lead_notification(
            lead_name=lead.name,
            company=lead.company,
            job_title=lead.job_title,
            score=lead.score,
            assessment_name=lead.assessment.title,
            lead_url=f"{settings.APP_URL}/tenants/{tenant.id}/leads/{lead.id}"
        )
        logger.info(f"✅ Teams notification sent for lead {lead.id}")
    except Exception as e:
        logger.error(f"⚠️  Failed to send Teams notification: {str(e)}")
```

---

## Testing Strategy

### Unit Tests

**LeadTable Component:**
- [ ] Renders lead rows correctly
- [ ] Shows hot lead icon for score >= 80
- [ ] Highlights hot leads with background color

**LeadFilters Component:**
- [ ] Applies filters correctly
- [ ] Updates URL query params
- [ ] Resets filters

**Lead Scoring Logic:**
- [ ] Calculates score correctly
- [ ] Normalizes to 0-100 range
- [ ] Handles edge cases (no answers, invalid data)

### Integration Tests

**Lead List Flow:**
1. Navigate to leads page
2. Apply status filter
3. Verify filtered results
4. Click lead → Navigate to detail page

**Lead Status Update:**
1. Open lead detail
2. Change status
3. Add note
4. Verify status updated
5. Verify activity log created

### E2E Tests

**Complete Lead Management Flow:**
1. Login
2. Navigate to leads
3. Filter by "hot leads"
4. Click first hot lead
5. View score breakdown
6. Update status to "contacted"
7. Add note
8. Verify activity log
9. Navigate back to list
10. Verify status updated in list

**Teams Notification Flow:**
1. Create lead with score 95
2. Verify Teams notification sent
3. Update lead score from 75 to 85
4. Verify Teams notification sent
5. Update lead score from 85 to 90
6. Verify NO duplicate notification

---

## Implementation Notes

### Critical Considerations

**1. Performance:**
- Large lead datasets (10,000+) require efficient indexing
- Pagination必須
- フィルタリングはバックエンドで実行（フロントエンドで全件取得しない）

**2. Data Privacy:**
- テナント分離を厳密に実施
- 個人情報の暗号化
- GDPR準拠（削除要求への対応）

**3. Teams Integration:**
- 通知失敗でもリード作成は成功させる
- 非同期処理（バックグラウンドタスク）
- リトライロジック（3回まで、指数バックオフ）

**4. Scalability:**
- PostgreSQLインデックス最適化:
  ```sql
  CREATE INDEX idx_leads_tenant_score ON leads(tenant_id, score DESC);
  CREATE INDEX idx_leads_tenant_status ON leads(tenant_id, status);
  CREATE INDEX idx_leads_tenant_created ON leads(tenant_id, created_at DESC);
  ```

---

## Related Specifications

- [System Core Features](./system-core.md)
- [Assessment Features](./assessment-features.md)
- [Microsoft Teams Integration](../../specs/features/microsoft-teams-integration.md)
- [Analytics Dashboard](../../specs/features/analytics-dashboard.md)

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-11 | 1.0 | Initial specification |

---

**Status**: ✅ Ready for Review  
**Next Steps**: Review → Approve → Implement
