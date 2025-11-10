# DiagnoLeads - プロジェクトコンテキスト

このファイルは、Factory DroidがDiagnoLeadsプロジェクトで作業する際の重要なコンテキスト情報を提供します。

## プロジェクト概要

**DiagnoLeads**は、B2B企業が顧客の課題を診断し、質の高いリードを獲得するためのマルチテナントSaaSプラットフォームです。AI（Claude）を活用した診断自動生成、リード分析、パーソナライズレポート生成により、マーケティング活動を効率化します。

### ビジネス価値
- **診断コンテンツ作成の自動化**: AIが質問・選択肢・スコアリングを自動生成
- **リード品質の向上**: 診断回答から企業課題を自動検出、ホットリードを優先化
- **マーケティングROI向上**: 見込み顧客獲得コストを削減
- **マルチテナント**: 複数企業が独立環境で運用可能

## アーキテクチャの重要ポイント

### 1. マルチテナント設計（最重要）

**すべてのコードでテナント分離を必ず実装すること**

#### データベースアクセスルール
```python
# ❌ 絶対にやってはいけない - テナントフィルタなし
assessments = db.query(Assessment).all()

# ✅ 必ずテナントでフィルタリング
assessments = db.query(Assessment).filter(
    Assessment.tenant_id == current_tenant.id
).all()
```

#### APIエンドポイント設計
```python
# ✅ テナントスコープを含むパス
@router.get("/api/v1/tenants/{tenant_id}/assessments")
async def list_assessments(
    tenant_id: UUID,
    current_user: User = Depends(get_current_user)
):
    # テナントIDの検証
    if current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403)
    
    # テナントフィルタ付きクエリ
    return await assessment_service.list_by_tenant(tenant_id)
```

#### テスト時のチェックポイント
- [ ] 異なるテナントのデータが混在しないか
- [ ] テナントAのユーザーがテナントBのデータにアクセスできないか
- [ ] マイグレーション後にテナントデータが正しく分離されているか

### 2. OpenSpec仕様駆動開発

DiagnoLeadsはOpenSpecを使用した仕様駆動開発を採用しています。

#### ワークフロー
1. **仕様提案**: 新機能や変更の仕様を `openspec/changes/` に作成
2. **レビュー**: チームで仕様をレビュー・調整
3. **承認**: レビュー完了後、`openspec/specs/` に移動（Source of Truth）
4. **実装**: 承認された仕様に基づいて実装
5. **アーカイブ**: 完了した変更を `openspec/archive/` に移動

#### 仕様ファイルの場所
- `openspec/specs/` - 承認済み仕様（実装の基準）
- `openspec/changes/` - レビュー中の変更提案
- `openspec/archive/` - 完了した変更

**重要**: 実装前に必ず関連する仕様ファイルを確認すること

### 3. AI機能の統合

#### Anthropic Claude API使用パターン

```python
from anthropic import Anthropic

class AssessmentGenerator:
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def generate(self, topic: str, industry: str, tenant_id: UUID) -> dict:
        """
        診断コンテンツを自動生成
        
        注意:
        - プロンプトにテナント固有の情報を含めない
        - 生成結果には必ずtenant_idを付与
        - コスト管理のためトークン数を監視
        """
        prompt = self._build_prompt(topic, industry)
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = self._parse_response(response)
        result["tenant_id"] = tenant_id  # 必須
        
        return result
```

#### AI機能のテストポイント
- [ ] APIキーが環境変数から読み込まれているか
- [ ] エラーハンドリング（レート制限、タイムアウト）
- [ ] トークン使用量の監視
- [ ] 生成結果の検証

### 4. セキュリティ要件

#### 必須チェック項目
- [ ] **認証**: すべての保護されたエンドポイントでJWT検証
- [ ] **認可**: ユーザーがアクセス権限を持つリソースかチェック
- [ ] **入力検証**: すべてのユーザー入力をサニタイズ
- [ ] **SQLインジェクション対策**: ORMのパラメータ化クエリを使用
- [ ] **XSS対策**: フロントエンドでHTMLエスケープ
- [ ] **CSRF対策**: トークン検証
- [ ] **機密情報管理**: .envファイルで管理、.gitignoreに追加

#### 機密情報の取り扱い
```python
# ❌ 絶対にやってはいけない
DATABASE_URL = "postgresql://user:password@localhost/db"

# ✅ 環境変数から読み込む
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    anthropic_api_key: str
    secret_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## 技術スタック詳細

### バックエンド (FastAPI)

**ディレクトリ構造**
```
backend/
├── app/
│   ├── main.py                    # アプリケーションエントリーポイント
│   ├── api/v1/                    # REST APIエンドポイント
│   │   ├── assessments.py
│   │   ├── leads.py
│   │   └── auth.py
│   ├── models/                    # SQLAlchemyモデル
│   │   ├── tenant.py
│   │   ├── assessment.py
│   │   └── lead.py
│   ├── services/                  # ビジネスロジック層
│   │   ├── assessment_service.py
│   │   ├── lead_service.py
│   │   └── ai/
│   │       ├── assessment_generator.py
│   │       └── lead_analyzer.py
│   ├── core/                      # コア機能
│   │   ├── config.py
│   │   ├── security.py
│   │   └── multi_tenant.py
│   └── integrations/              # 外部サービス連携
│       ├── salesforce.py
│       └── hubspot.py
├── tests/
└── requirements.txt
```

**開発コマンド**
```bash
cd backend

# 仮想環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt

# データベースマイグレーション
alembic upgrade head

# 開発サーバー起動
uvicorn app.main:app --reload

# テスト実行
pytest tests/ -v --cov=app

# コード品質チェック
ruff check .
ruff format .
mypy .
```

### フロントエンド (React + Vite)

**ディレクトリ構造**
```
frontend/
├── src/
│   ├── features/                  # 機能ベースの構造
│   │   ├── assessments/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── stores/
│   │   │   └── types.ts
│   │   ├── leads/
│   │   └── analytics/
│   ├── components/                # 共通UIコンポーネント
│   │   ├── ui/                    # shadcn/ui
│   │   └── layout/
│   ├── stores/                    # Zustand状態管理
│   ├── lib/                       # ユーティリティ
│   │   ├── api.ts
│   │   └── utils.ts
│   └── App.tsx
└── package.json
```

**開発コマンド**
```bash
cd frontend

# 依存関係インストール
npm install

# 開発サーバー起動
npm run dev

# ビルド
npm run build

# テスト実行
npm test

# コード品質チェック
npm run lint
npm run type-check
```

## データモデル

### 主要エンティティ

#### Tenant（テナント）
```python
class Tenant(Base):
    __tablename__ = "tenants"
    
    id: UUID = Column(UUID(as_uuid=True), primary_key=True)
    name: str
    domain: str  # カスタムドメイン
    plan: str  # free, starter, professional, enterprise
    settings: dict  # JSON設定
    created_at: datetime
    updated_at: datetime
```

#### Assessment（診断）
```python
class Assessment(Base):
    __tablename__ = "assessments"
    
    id: UUID
    tenant_id: UUID  # 必須: マルチテナント分離
    title: str
    description: str
    status: str  # draft, published, archived
    questions: List[Question]  # リレーション
    scoring_logic: dict  # スコアリングルール
    created_by: UUID  # ユーザーID
    created_at: datetime
    updated_at: datetime
```

#### Question（質問）
```python
class Question(Base):
    __tablename__ = "questions"
    
    id: UUID
    assessment_id: UUID
    tenant_id: UUID  # 必須
    text: str
    type: str  # single_choice, multiple_choice, scale
    options: List[dict]  # 選択肢
    weights: dict  # スコアウェイト
    order: int
```

#### Lead（リード）
```python
class Lead(Base):
    __tablename__ = "leads"
    
    id: UUID
    tenant_id: UUID  # 必須
    assessment_id: UUID
    email: str
    company: str
    score: float  # 診断スコア
    hot_score: float  # ホットリードスコア（AI分析）
    responses: dict  # 回答データ
    analysis: dict  # AI分析結果
    created_at: datetime
```

## 外部サービス連携

### Supabase
- **用途**: PostgreSQL データベース + 認証
- **設定**: `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`

### Upstash Redis
- **用途**: キャッシュ、セッション管理
- **設定**: `REDIS_URL`

### Anthropic Claude
- **用途**: AI診断生成、リード分析
- **設定**: `ANTHROPIC_API_KEY`
- **モデル**: claude-3-5-sonnet-20241022

### Trigger.dev（オプション）
- **用途**: 非同期ジョブ処理
- **設定**: `TRIGGER_API_KEY`, `TRIGGER_API_URL`

### Salesforce/HubSpot（オプション）
- **用途**: CRM連携
- **設定**: 各種認証情報

## 開発ワークフロー

### 1. 新機能開発

```bash
# 1. 仕様を確認
cat openspec/specs/{feature}/specification.md

# 2. ブランチ作成
git checkout -b feature/feature-name

# 3. バックエンド実装
cd backend
# モデル作成 → マイグレーション → サービス → API

# 4. フロントエンド実装
cd frontend
# コンポーネント → 状態管理 → API統合

# 5. テスト
cd backend && pytest
cd frontend && npm test

# 6. コミット
git add .
git commit -m "feat: Add feature-name"

# 7. プッシュ＆PR
git push origin feature/feature-name
gh pr create
```

### 2. バグ修正

```bash
# 1. Issue確認
gh issue view {issue-number}

# 2. ブランチ作成
git checkout -b fix/bug-name

# 3. 修正実装

# 4. テスト追加（再発防止）
# tests/ に失敗ケースを追加

# 5. コミット
git commit -m "fix: Fix bug-name"

# 6. プッシュ＆PR
gh pr create
```

## トラブルシューティング

### マルチテナントデータ漏洩が疑われる場合

```python
# データベース検証クエリ
# 各テーブルのtenant_id分布を確認
SELECT tenant_id, COUNT(*) 
FROM assessments 
GROUP BY tenant_id;

# 孤立データの確認（tenant_idがNULL）
SELECT * FROM assessments WHERE tenant_id IS NULL;
```

### AI API エラー

```python
# レート制限エラー
# → Trigger.devで非同期化、リトライロジック実装

# タイムアウト
# → max_tokensを調整、プロンプトを簡潔化

# コスト超過
# → トークン使用量を監視、キャッシュ活用
```

### データベースマイグレーションエラー

```bash
# マイグレーション履歴確認
alembic history

# 現在のバージョン
alembic current

# ロールバック
alembic downgrade -1

# マイグレーション再実行
alembic upgrade head
```

## 参考リソース

- [OpenSpec GitHub](https://github.com/Fission-AI/OpenSpec)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Supabase Multi-Tenancy Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [React Query Documentation](https://tanstack.com/query/latest)

## チーム連絡先

- **プロジェクトリード**: yusuke-kurosawa
- **Repository**: https://github.com/yusuke-kurosawa/DiagnoLeads
- **Issue Tracker**: GitHub Issues
