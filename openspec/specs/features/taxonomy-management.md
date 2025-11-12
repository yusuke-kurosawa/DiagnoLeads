# テナント別タクソノミー管理（トピック・業界管理）

## 概要

マルチテナント対応のタクソノミー（分類体系）管理機能。各テナントが独立した「トピック」と「業界」のマスターデータを管理でき、診断作成時にドロップダウン選択して使用できます。これにより、データ一貫性が向上し、各テナントのビジネス分類に対応できます。

**ビジネス価値:**
- 📊 各テナントが独自の分類体系を構築可能
- 🎯 診断のカテゴリ分けが統一される
- 📈 タクソノミー準拠率を分析できる
- 🔒 テナント間でのデータ混在を防止

**対象ユーザー:**
- テナント管理者：分類の作成・編集・削除
- 診断作成者：診断作成時に分類を選択

---

## 1. 機能要件

### 1.1 トピック管理

#### トピックの属性
| 属性 | 型 | 説明 | 必須 |
|------|-----|------|------|
| `id` | UUID | トピック一意識別子 | ✅ |
| `tenant_id` | UUID | テナント ID（外部キー） | ✅ |
| `name` | String(100) | トピック名（例：マーケティング） | ✅ |
| `description` | String(500) | トピックの説明 | ❌ |
| `color` | String(7) | 管理画面表示用カラーコード（#RRGGBB） | ❌ |
| `icon` | String(50) | アイコン識別子（lucide-react） | ❌ |
| `sort_order` | Integer | 表示順序（昇順） | ❌ (デフォルト: 999) |
| `is_active` | Boolean | 有効/無効フラグ | ❌ (デフォルト: true) |
| `created_at` | DateTime | 作成日時 | ✅ |
| `updated_at` | DateTime | 更新日時 | ✅ |
| `created_by` | UUID | 作成者 ID | ✅ |

#### トピック CRUD 操作

**C - 作成 (POST /api/v1/tenants/{tenant_id}/topics)**
```json
{
  "name": "マーケティング",
  "description": "マーケティング戦略・施策に関する診断",
  "color": "#3B82F6",
  "icon": "target"
}
```

**R - 読取 (GET /api/v1/tenants/{tenant_id}/topics)**
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "マーケティング",
      "description": "...",
      "color": "#3B82F6",
      "icon": "target",
      "sort_order": 1,
      "is_active": true
    }
  ],
  "total": 5
}
```

**U - 更新 (PUT /api/v1/tenants/{tenant_id}/topics/{topic_id})**
```json
{
  "name": "マーケティング戦略",
  "sort_order": 2
}
```

**D - 削除 (DELETE /api/v1/tenants/{tenant_id}/topics/{topic_id})**
- 削除対象トピックが診断で使用されている場合：エラー（409 Conflict）
- またはソフトデリート（is_active = false）に変更

### 1.2 業界（Industry）管理

トピックと同じ構造：

| 属性 | 型 | 説明 |
|------|-----|------|
| `id` | UUID | 業界 ID |
| `tenant_id` | UUID | テナント ID |
| `name` | String(100) | 業界名（例：テクノロジー） |
| `description` | String(500) | 業界の説明 |
| `color` | String(7) | カラーコード |
| `icon` | String(50) | アイコン |
| `sort_order` | Integer | 表示順序 |
| `is_active` | Boolean | 有効フラグ |
| `created_at` | DateTime | 作成日時 |
| `updated_at` | DateTime | 更新日時 |
| `created_by` | UUID | 作成者 ID |

#### 業界 API エンドポイント
```
POST   /api/v1/tenants/{tenant_id}/industries
GET    /api/v1/tenants/{tenant_id}/industries
PUT    /api/v1/tenants/{tenant_id}/industries/{industry_id}
DELETE /api/v1/tenants/{tenant_id}/industries/{industry_id}
```

### 1.3 デフォルト分類

**新規テナント作成時に自動生成するデフォルトトピック：**
```
1. マーケティング
2. 営業
3. カスタマーサービス
4. HR / 人材育成
5. IT / 技術
```

**新規テナント作成時に自動生成するデフォルト業界：**
```
1. テクノロジー
2. 金融・銀行
3. 製造・工業
4. 小売・流通
5. ヘルスケア
6. 教育
7. 不動産
8. その他
```

---

## 2. UI/UX 要件

### 2.1 診断作成フォーム

**トピック・業界フィールドをドロップダウンに変更：**

```tsx
// Before: テキスト入力
<input type="text" placeholder="e.g., Marketing Strategy" />

// After: ドロップダウン選択
<select>
  <option value="">トピックを選択してください</option>
  <option value={topic_id}>マーケティング</option>
  <option value={topic_id}>営業</option>
</select>
```

**UI ガイドラインに追加：**
- セクション 6.7: ドロップダウン/セレクトコンポーネント
- データソース：REST API から動的に読み込み
- キャッシング戦略：TanStack Query でキャッシュ

### 2.2 テナント設定ページ（新規）

**ルート:** `/tenants/{tenant_id}/settings/taxonomy`

**ページ構成：**
```
┌─────────────────────────────────┐
│ タクソノミー管理                 │
│ トピックと業界を一元管理します   │
└─────────────────────────────────┘

【タブ】
├─ トピック
└─ 業界

【トピックタブ内容】
┌─────────────────────────────────┐
│ + 新規トピック作成              │
├─────────────────────────────────┤
│ 名前          | 説明    | アクション │
├─────────────────────────────────┤
│ マーケティング | ...   | 編集 削除  │
│ 営業           | ...   | 編集 削除  │
│ ...            | ...   | 編集 削除  │
└─────────────────────────────────┘
```

**ダイアログ（新規/編集）:**
```
【トピックを作成】

名前*: [テキスト入力]
説明:  [複数行テキスト]
色:    [カラーピッカー]
アイコン: [アイコン選択]

[キャンセル] [保存]
```

### 2.3 診断一覧ページの拡張

**各診断カードにトピック・業界バッジを表示：**
```
┌──────────────────────────┐
│ 診断タイトル             │
│                          │
│ [マーケティング] [技術]   │
│ 2025年11月12日          │
└──────────────────────────┘
```

---

## 3. 技術要件

### 3.1 バックエンド

#### 新規モデル（SQLAlchemy）

**Topic モデル:**
```python
class Topic(Base):
    __tablename__ = "topics"
    
    id: UUID = Column(UUID, primary_key=True, default=uuid4)
    tenant_id: UUID = Column(UUID, ForeignKey("tenants.id"), nullable=False)
    name: str = Column(String(100), nullable=False)
    description: Optional[str] = Column(String(500))
    color: Optional[str] = Column(String(7))  # #RRGGBB
    icon: Optional[str] = Column(String(50))
    sort_order: int = Column(Integer, default=999)
    is_active: bool = Column(Boolean, default=True)
    created_at: DateTime = Column(DateTime, default=datetime.utcnow)
    updated_at: DateTime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by: UUID = Column(UUID, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant")
    assessments = relationship("Assessment", back_populates="topic")
```

**Industry モデル:**
Topic と同じ構造

**Assessment モデルの更新:**
```python
class Assessment(Base):
    # 既存フィールド...
    
    topic_id: Optional[UUID] = Column(UUID, ForeignKey("topics.id"))
    industry_id: Optional[UUID] = Column(UUID, ForeignKey("industries.id"))
    
    # Relationships
    topic = relationship("Topic", back_populates="assessments")
    industry = relationship("Industry", back_populates="assessments")
```

#### 新規 API エンドポイント

**File: `backend/app/api/v1/topics.py`**
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

router = APIRouter(prefix="/topics", tags=["Topics"])

@router.post("", response_model=TopicResponse)
async def create_topic(
    tenant_id: UUID,
    topic: TopicCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new topic for tenant"""
    
@router.get("", response_model=List[TopicResponse])
async def list_topics(
    tenant_id: UUID,
    is_active: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all topics for tenant"""
    
@router.put("/{topic_id}", response_model=TopicResponse)
async def update_topic(
    tenant_id: UUID,
    topic_id: UUID,
    topic: TopicUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update topic"""
    
@router.delete("/{topic_id}")
async def delete_topic(
    tenant_id: UUID,
    topic_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete or soft-delete topic"""
```

**File: `backend/app/api/v1/industries.py`**
Topic と同じ構造

#### Pydantic Schemas

```python
# backend/app/schemas/topic.py

class TopicBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    sort_order: int = 999

class TopicCreate(TopicBase):
    pass

class TopicUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None

class TopicResponse(TopicBase):
    id: UUID
    tenant_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: UUID
```

#### マイグレーション

**Alembic migration file:**
- `versions/xxx_add_topics_and_industries_tables.py`
- Topics テーブル作成
- Industries テーブル作成
- Assessment に topic_id, industry_id カラム追加

### 3.2 フロントエンド

#### 新規 Service（assessmentTaxonomyService）

```typescript
// src/services/taxonomyService.ts

export const taxonomyService = {
  // Topics
  async getTopics(tenantId: string): Promise<Topic[]> {
    const response = await api.get(`/tenants/${tenantId}/topics`);
    return response.data;
  },

  async createTopic(tenantId: string, data: TopicCreate): Promise<Topic> {
    const response = await api.post(`/tenants/${tenantId}/topics`, data);
    return response.data;
  },

  async updateTopic(tenantId: string, topicId: string, data: TopicUpdate): Promise<Topic> {
    const response = await api.put(`/tenants/${tenantId}/topics/${topicId}`, data);
    return response.data;
  },

  async deleteTopic(tenantId: string, topicId: string): Promise<void> {
    await api.delete(`/tenants/${tenantId}/topics/${topicId}`);
  },

  // Industries
  async getIndustries(tenantId: string): Promise<Industry[]> {
    const response = await api.get(`/tenants/${tenantId}/industries`);
    return response.data;
  },
  // ... similar CRUD for industries
};
```

#### コンポーネント更新

**AssessmentForm.tsx:**
```tsx
// useQuery で動的にトピック・業界を読み込み
const { data: topics } = useQuery({
  queryKey: ['topics', tenantId],
  queryFn: () => taxonomyService.getTopics(tenantId),
});

const { data: industries } = useQuery({
  queryKey: ['industries', tenantId],
  queryFn: () => taxonomyService.getIndustries(tenantId),
});

// セレクト要素に追加
<select {...register('topic_id')}>
  <option value="">トピックを選択</option>
  {topics?.map(topic => (
    <option key={topic.id} value={topic.id}>{topic.name}</option>
  ))}
</select>
```

#### 新規設定ページ

**`src/pages/settings/TaxonomyPage.tsx`**
- トピック・業界の管理インターフェース
- タブ切り替え（トピック/業界）
- 一覧表示、新規作成、編集、削除

### 3.3 データベース

#### マイグレーション SQL

```sql
CREATE TABLE topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    color VARCHAR(7),
    icon VARCHAR(50),
    sort_order INTEGER DEFAULT 999,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL REFERENCES users(id),
    UNIQUE(tenant_id, name)
);

CREATE TABLE industries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    color VARCHAR(7),
    icon VARCHAR(50),
    sort_order INTEGER DEFAULT 999,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL REFERENCES users(id),
    UNIQUE(tenant_id, name)
);

ALTER TABLE assessments 
ADD COLUMN topic_id UUID REFERENCES topics(id),
ADD COLUMN industry_id UUID REFERENCES industries(id);
```

---

## 4. セキュリティ要件

- ✅ テナント ID による行レベルセキュリティ（RLS）
- ✅ タクソノミーの所有者確認（tenant_id マッチング）
- ✅ 認証が必要（JWT）
- ✅ 削除時の診断関連チェック（外部キー制約）

---

## 5. テスト要件

### 単体テスト
- Topic CRUD 操作
- Industry CRUD 操作
- デフォルト分類の自動生成
- テナント間のデータ分離

### 統合テスト
- 診断作成フローでのトピック・業界選択
- 削除時の依存関係チェック

### E2E テスト
- 設定画面でのトピック・業界管理
- 診断作成フォームでの選択と保存

---

## 6. 実装段階

### Phase 1: バックエンド基盤（優先度: HIGH）
- [ ] モデル定義（Topic, Industry）
- [ ] マイグレーション
- [ ] API エンドポイント実装
- [ ] デフォルト分類の自動生成ロジック

### Phase 2: フロントエンド統合（優先度: HIGH）
- [ ] 診断作成フォームをドロップダウン化
- [ ] TaxonomyService 実装
- [ ] キャッシング戦略（TanStack Query）

### Phase 3: 管理画面（優先度: MEDIUM）
- [ ] 設定ページの構築
- [ ] タクソノミー管理 UI

### Phase 4: 拡張・最適化（優先度: LOW）
- [ ] トピック・業界のバッチ操作
- [ ] エクスポート機能
- [ ] 分析レポート

---

## 7. API ドキュメント

### エラーハンドリング

| ステータスコード | 説明 |
|------------------|------|
| 201 | 作成成功 |
| 200 | 取得・更新成功 |
| 204 | 削除成功 |
| 400 | バリデーション エラー |
| 401 | 認証エラー |
| 403 | 権限なし |
| 404 | リソース not found |
| 409 | 削除対象がまだ使用中（診断に参照） |

---

## 8. UI ガイドライン更新

**UI_GUIDELINES.md に追加するセクション:**

### 6.7 ドロップダウン・セレクトコンポーネント

```tsx
<select className="block text-left text-sm font-medium text-gray-700 mb-2 w-full px-3 py-2 border border-gray-300 rounded-md">
  <option value="">-- 選択してください --</option>
  <option value="value1">オプション1</option>
  <option value="value2">オプション2</option>
</select>
```

**データ取得パターン:**
- 初期ロード時に TanStack Query で API から取得
- キャッシュキー: `['topics', tenantId]`
- 更新時は `queryClient.invalidateQueries()` で無効化

---

## 9. 完了基準

- ✅ Topic・Industry テーブルが作成され、診断と連携
- ✅ 診断作成フォームのトピック・業界がドロップダウン化
- ✅ テナント設定ページでタクソノミーを管理可能
- ✅ デフォルト分類が新規テナント作成時に自動生成
- ✅ すべてのテストが成功
- ✅ テナント間のデータ分離が確保

---

## 参考：デフォルト分類データ

### デフォルトトピック
```json
[
  { "name": "マーケティング", "description": "マーケティング戦略・施策", "color": "#3B82F6", "icon": "target" },
  { "name": "営業", "description": "営業プロセス・営業スキル", "color": "#10B981", "icon": "briefcase" },
  { "name": "カスタマーサービス", "description": "顧客対応・サポート", "color": "#F59E0B", "icon": "headphones" },
  { "name": "HR / 人材育成", "description": "採用・育成・組織", "color": "#8B5CF6", "icon": "users" },
  { "name": "IT / 技術", "description": "IT スキル・技術力", "color": "#06B6D4", "icon": "cpu" }
]
```

### デフォルト業界
```json
[
  { "name": "テクノロジー", "color": "#06B6D4", "icon": "cpu" },
  { "name": "金融・銀行", "color": "#059669", "icon": "banknote" },
  { "name": "製造・工業", "color": "#DC2626", "icon": "factory" },
  { "name": "小売・流通", "color": "#F59E0B", "icon": "shopping-cart" },
  { "name": "ヘルスケア", "color": "#EC4899", "icon": "heart" },
  { "name": "教育", "color": "#3B82F6", "icon": "book-open" },
  { "name": "不動産", "color": "#8B5CF6", "icon": "building" },
  { "name": "その他", "color": "#6B7280", "icon": "more-horizontal" }
]
```
