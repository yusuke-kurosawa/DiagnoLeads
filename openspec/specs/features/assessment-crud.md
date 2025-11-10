# Feature: Assessment CRUD

**Status**: ✅ Implemented  
**Created**: 2025-01-10  
**Last Updated**: 2025-01-10

## Overview

診断アセスメントを作成・管理する機能。テナントごとに独立した診断コンテンツを管理し、リードに対して診断を実施できる。

## User Stories

- **テナント管理者として**、診断アセスメントを作成したい、so that リードの課題を評価できる
- **マーケティング担当者として**、アセスメントを公開・非公開できるようにしたい、so that 適切なタイミングでリリースできる
- **営業担当者として**、AI生成されたアセスメントを使いたい、so that 効率的にコンテンツを作成できる

## Requirements

### Functional Requirements

#### 1. Assessment管理
- ✅ アセスメントの作成
- ✅ アセスメントの一覧表示
- ✅ アセスメントの詳細表示
- ✅ アセスメントの編集
- ✅ アセスメントの削除
- ✅ アセスメントの検索（タイトル）

#### 2. ステータス管理
- ✅ `draft` - 下書き（作成中）
- ✅ `published` - 公開済み
- ✅ `archived` - アーカイブ済み

#### 3. AI生成対応
- ✅ `manual` - 手動作成
- ✅ `ai` - AI生成
- ✅ `hybrid` - AI + 手動編集

#### 4. マルチテナント対応
- ✅ テナントごとに完全分離
- ✅ テナント間のデータアクセス禁止
- ✅ CASCADE DELETE（テナント削除時）

### Non-Functional Requirements

- **パフォーマンス**: 一覧取得は100ms以内
- **セキュリティ**: すべてのクエリでtenant_idフィルタリング
- **可用性**: 99.9%以上
- **スケーラビリティ**: 1テナントあたり10,000アセスメントまで対応

## Data Model

### Assessment Entity

```python
class Assessment(Base):
    """Assessment model with tenant association"""
    
    __tablename__ = "assessments"
    
    # Primary Key
    id: UUID                    # 一意識別子
    
    # Foreign Keys
    tenant_id: UUID             # テナントID（必須、CASCADE DELETE）
    created_by: UUID            # 作成者ユーザーID
    updated_by: UUID | None     # 更新者ユーザーID
    
    # Core Fields
    title: str                  # タイトル（最大255文字）
    description: str | None     # 説明文
    status: str                 # ステータス (draft/published/archived)
    
    # AI Generation
    topic: str | None           # トピック（AI生成用）
    industry: str | None        # 業界（AI生成用）
    ai_generated: str           # 生成方法 (manual/ai/hybrid)
    
    # Scoring
    scoring_logic: JSON         # スコアリングロジック
    
    # Timestamps
    created_at: DateTime        # 作成日時
    updated_at: DateTime        # 更新日時
    
    # Indexes
    Index('idx_assessments_tenant_status', tenant_id, status)
    Index('idx_assessments_created_by', created_by)
```

### Validation Rules

- `title`: 必須、1-255文字
- `status`: `draft` | `published` | `archived`
- `ai_generated`: `manual` | `ai` | `hybrid`
- `tenant_id`: 必須、存在するテナント
- `created_by`: 必須、存在するユーザー
- `scoring_logic`: JSON形式、デフォルト `{}`

## API Design (概要)

詳細なAPI仕様は[openapi.json](../../openapi.json)を参照。

### Endpoints

```
GET    /api/v1/tenants/{tenant_id}/assessments
GET    /api/v1/tenants/{tenant_id}/assessments/search?q={query}
GET    /api/v1/tenants/{tenant_id}/assessments/{assessment_id}
POST   /api/v1/tenants/{tenant_id}/assessments
PUT    /api/v1/tenants/{tenant_id}/assessments/{assessment_id}
DELETE /api/v1/tenants/{tenant_id}/assessments/{assessment_id}
```

### Security

すべてのエンドポイントで：
- ✅ JWT認証必須
- ✅ ユーザーのtenant_idとパスのtenant_idの一致を検証
- ✅ 不一致の場合は403 Forbidden
- ✅ 存在しないリソースは404 Not Found

## UI/UX Design

### Components

#### 1. AssessmentList
- カード形式の一覧表示
- ステータスバッジ（色分け）
- AI生成アイコン表示
- 作成日時表示
- 検索機能
- "Create Assessment"ボタン

#### 2. AssessmentForm (create/edit共通)
- タイトル入力（必須）
- 説明文入力（任意）
- ステータス選択
- トピック入力
- 業界入力
- 生成タイプ選択
- バリデーションエラー表示
- Cancel/Save ボタン

#### 3. AssessmentDetailPage
- タイトル表示
- ステータスバッジ
- 説明文
- メタデータ（トピック、業界、生成タイプ）
- 作成・更新日時
- Edit/Delete ボタン
- Back to list リンク

### User Flow

```
[AssessmentList]
    ↓ "Create Assessment"
[CreateAssessmentPage]
    ↓ フォーム入力
    ↓ "Save"
[AssessmentDetailPage] ← 新規作成完了
    ↓ "Edit"
[EditAssessmentPage]
    ↓ 編集
    ↓ "Save"
[AssessmentDetailPage] ← 更新完了
```

## Business Logic

### 1. アセスメント作成
1. ユーザー認証確認
2. テナント権限確認
3. バリデーション実行
4. `tenant_id`と`created_by`を自動設定
5. データベースに保存
6. 201 Createdで応答

### 2. アセスメント一覧
1. ユーザー認証確認
2. テナント権限確認
3. `tenant_id`でフィルタリング
4. オプション: `status`でフィルタリング
5. ページネーション適用
6. 作成日時の降順でソート
7. 200 OKで応答

### 3. アセスメント検索
1. ユーザー認証確認
2. テナント権限確認
3. `tenant_id`と`title`（部分一致）でフィルタリング
4. 最大10件まで返却
5. 200 OKで応答

### 4. アセスメント更新
1. ユーザー認証確認
2. テナント権限確認
3. リソースの存在確認（404 Not Found）
4. バリデーション実行
5. `updated_by`を現在ユーザーに設定
6. 更新実行
7. 200 OKで応答

### 5. アセスメント削除
1. ユーザー認証確認
2. テナント権限確認
3. リソースの存在確認（404 Not Found）
4. 削除実行
5. 204 No Contentで応答

### Multi-Tenant Security Logic

**すべての操作で以下を実行:**

```python
# 1. ユーザーのテナントIDを取得
current_user_tenant_id = current_user.tenant_id

# 2. パスのテナントIDと比較
if current_user_tenant_id != path_tenant_id:
    raise HTTPException(status_code=403, detail="Access forbidden")

# 3. データベースクエリに必ずtenant_idを含める
query = query.filter(Assessment.tenant_id == tenant_id)
```

## Testing Strategy

### Unit Tests (Backend)
- ✅ `test_list_assessments_empty` - 空リスト
- ✅ `test_create_assessment` - 作成
- ✅ `test_get_assessment` - 取得
- ✅ `test_list_assessments` - 一覧
- ✅ `test_update_assessment` - 更新
- ✅ `test_delete_assessment` - 削除
- ✅ `test_search_assessments` - 検索
- ✅ `test_cross_tenant_access_denied` - **クロステナントアクセス拒否（重要）**
- ✅ `test_get_nonexistent_assessment` - 404エラー
- ✅ `test_unauthorized_access` - 未認証エラー

### Integration Tests
- マルチテナント分離の検証
- CASCADE DELETEの動作確認
- トランザクション整合性

### Frontend Tests
- コンポーネントのレンダリング
- フォームバリデーション
- API呼び出し（モック）

## Implementation Status

### Backend ✅
- ✅ Models: `backend/app/models/assessment.py`
- ✅ Schemas: `backend/app/schemas/assessment.py`
- ✅ Service: `backend/app/services/assessment_service.py`
- ✅ API: `backend/app/api/v1/assessments.py`
- ✅ Dependencies: `backend/app/core/deps.py`
- ✅ Tests: `backend/tests/test_assessment.py` (10/10 passing)
- ✅ Migration: `backend/alembic/versions/d724f366bbf2_add_assessment_model.py`

### Frontend ✅
- ✅ Types: `frontend/src/types/api.generated.ts` (自動生成)
- ✅ Service: `frontend/src/services/assessmentService.ts`
- ✅ Components:
  - ✅ `AssessmentList.tsx`
  - ✅ `AssessmentForm.tsx`
- ✅ Pages:
  - ✅ `AssessmentsPage.tsx`
  - ✅ `CreateAssessmentPage.tsx`
  - ✅ `EditAssessmentPage.tsx`
  - ✅ `AssessmentDetailPage.tsx`

### API Specification ✅
- ✅ OpenAPI: `openapi.json` (自動生成)
- ✅ Endpoints: 6個
- ✅ Schemas: AssessmentCreate, AssessmentUpdate, AssessmentResponse

## Related Specs

- [Multi-Tenant Architecture](../architecture/multi-tenant.md)
- [API Overview](../api/endpoints-overview.md)
- [Lead Management](./lead-management.md) (予定)

## Implementation Notes

### 注意点

1. **テナント分離は絶対**: すべてのクエリで`tenant_id`フィルタリング必須
2. **CASCADE DELETE**: テナント削除時にアセスメントも自動削除
3. **インデックス**: `(tenant_id, status)`の複合インデックスでパフォーマンス最適化
4. **JSON フィールド**: `scoring_logic`はJSON型、デフォルト値は`{}`

### 将来の拡張

- [ ] アセスメント質問の管理
- [ ] アセスメント回答の記録
- [ ] スコアリングロジックの実行
- [ ] AI自動生成機能（Claude API統合）
- [ ] アセスメントのテンプレート機能
- [ ] バージョン管理機能

## Change History

- 2025-01-10: Initial implementation (v0.1.0)
  - CRUD機能実装
  - マルチテナント対応
  - フロントエンドUI実装
  - 全テストパス（19/19）

---

**実装完了日**: 2025-01-10  
**テスト結果**: 19/19 PASSED ✅  
**本番環境**: 未デプロイ
