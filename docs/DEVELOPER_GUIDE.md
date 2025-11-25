# 開発者ガイド

## 目次
1. [開発環境のセットアップ](#開発環境のセットアップ)
2. [プロジェクト構造](#プロジェクト構造)
3. [コーディング規約](#コーディング規約)
4. [テストの実行](#テストの実行)
5. [デバッグ方法](#デバッグ方法)
6. [よくある問題と解決方法](#よくある問題と解決方法)

---

## 開発環境のセットアップ

### 必要なツール

- **Node.js**: 18.x以上
- **Python**: 3.11以上
- **PostgreSQL**: 14以上（または Supabase アカウント）
- **Redis**: 7.x以上（または Upstash アカウント）
- **Git**: 2.x以上

### クイックスタート

#### 1. リポジトリのクローン

```bash
git clone https://github.com/yusuke-kurosawa/DiagnoLeads.git
cd DiagnoLeads
```

#### 2. 環境変数の設定

```bash
# プロジェクトルートで .env ファイルを作成
cp .env.example .env

# 以下の環境変数を設定
nano .env
```

**必須環境変数**:
```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/diagnoleads

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-generate-with-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Anthropic Claude API (AI機能用)
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# 環境設定
ENVIRONMENT=development
DEBUG=True
```

**SECRET_KEYの生成**:
```bash
openssl rand -hex 32
```

#### 3. バックエンドのセットアップ

```bash
cd backend

# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 本番用依存関係のインストール
pip install -r requirements.txt

# 開発用依存関係のインストール（推奨）
pip install -r requirements-dev.txt

# データベースマイグレーション
alembic upgrade head

# 開発サーバーの起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**バックエンドの動作確認**:
```bash
# 別のターミナルで
curl http://localhost:8000/health
# 期待される出力: {"status":"healthy"}
```

#### 4. フロントエンドのセットアップ

```bash
cd frontend

# 依存関係のインストール
npm install

# 開発サーバーの起動
npm run dev

# ブラウザで http://localhost:5173 を開く
```

#### 5. 埋め込みウィジェットのセットアップ（オプション）

```bash
cd embed

# 依存関係のインストール
npm install

# 開発サーバーの起動（テストページ付き）
npm run dev
```

---

## プロジェクト構造

### ディレクトリ構成

```
DiagnoLeads/
├── backend/                      # FastAPIバックエンド
│   ├── app/
│   │   ├── main.py              # FastAPIアプリケーションエントリポイント
│   │   ├── api/v1/              # REST API エンドポイント
│   │   │   ├── auth.py
│   │   │   ├── assessments.py
│   │   │   ├── leads.py
│   │   │   └── ...
│   │   ├── models/              # SQLAlchemyモデル（データベーステーブル）
│   │   │   ├── tenant.py
│   │   │   ├── user.py
│   │   │   ├── assessment.py
│   │   │   └── ...
│   │   ├── schemas/             # Pydanticスキーマ（バリデーション）
│   │   │   ├── tenant.py
│   │   │   ├── user.py
│   │   │   └── ...
│   │   ├── services/            # ビジネスロジック層
│   │   │   ├── auth_service.py
│   │   │   ├── lead_service.py
│   │   │   ├── ai/
│   │   │   │   ├── ai_service.py
│   │   │   │   └── prompt_templates.py
│   │   │   └── ...
│   │   ├── core/                # コア機能・設定
│   │   │   ├── config.py        # 環境設定（重要）
│   │   │   ├── constants.py     # 定数定義
│   │   │   ├── exceptions.py    # 統一エラーハンドリング（重要）
│   │   │   ├── database.py      # データベース接続
│   │   │   ├── deps.py          # 依存性注入
│   │   │   └── middleware.py    # ミドルウェア
│   │   └── integrations/        # 外部サービス連携
│   │       ├── google_analytics/
│   │       ├── microsoft_teams/
│   │       └── ...
│   ├── tests/                   # テストスイート
│   │   ├── integration/         # 統合テスト
│   │   │   └── test_multi_tenant_isolation.py  # マルチテナント分離テスト
│   │   ├── test_auth.py
│   │   ├── test_lead.py
│   │   └── ...
│   ├── requirements.txt         # 本番用依存関係
│   ├── requirements-dev.txt     # 開発用依存関係
│   └── alembic/                 # データベースマイグレーション
│
├── frontend/                     # React + Viteフロントエンド
│   ├── src/
│   │   ├── components/          # 共通UIコンポーネント
│   │   │   ├── ui/              # shadcn/uiコンポーネント
│   │   │   ├── assessments/
│   │   │   ├── leads/
│   │   │   └── ...
│   │   ├── pages/               # ページコンポーネント
│   │   │   ├── LoginPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   └── ...
│   │   ├── services/            # APIクライアント
│   │   │   ├── api.ts
│   │   │   ├── leadService.ts
│   │   │   └── ...
│   │   ├── store/               # Zustand状態管理
│   │   │   ├── authStore.ts
│   │   │   └── ...
│   │   ├── lib/                 # ユーティリティ・ヘルパー
│   │   │   ├── apiClient.ts
│   │   │   └── errorHandler.ts
│   │   └── types/               # TypeScript型定義
│   ├── package.json
│   └── vite.config.ts
│
├── embed/                        # 埋め込みウィジェット
│   ├── src/
│   │   ├── components/
│   │   │   └── DiagnoLeadsWidget.ts
│   │   └── ...
│   └── package.json
│
├── openspec/                     # OpenSpec仕様駆動開発
│   ├── specs/                   # 承認済み仕様（Source of Truth）
│   │   ├── OVERVIEW.md
│   │   ├── auth/
│   │   ├── assessments/
│   │   └── ...
│   ├── changes/                 # 変更提案
│   └── archive/                 # 完了した変更
│
└── docs/                         # ドキュメント
    ├── SECURITY.md              # セキュリティガイドライン（重要）
    ├── REFACTORING_SUMMARY.md   # 最新のリファクタリング報告
    ├── DEVELOPER_GUIDE.md       # このドキュメント
    └── ...
```

---

## コーディング規約

### Python（バックエンド）

#### 1. コードフォーマット

**ツール**: `ruff`, `black`, `mypy`

```bash
# リント実行
ruff check .

# フォーマット
ruff format .
# または
black .

# 型チェック
mypy .
```

#### 2. 統一エラーハンドリングの使用（重要）

すべてのビジネスロジックエラーは `app.core.exceptions` を使用してください。

**悪い例**:
```python
# 一般的なExceptionを使用 - NG
def get_lead(lead_id: UUID):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise Exception("Lead not found")  # ❌
```

**良い例**:
```python
from app.core.exceptions import ResourceNotFoundError, ErrorCode

def get_lead(lead_id: UUID, tenant_id: UUID):
    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.tenant_id == tenant_id  # マルチテナント分離
    ).first()

    if not lead:
        raise ResourceNotFoundError(
            code=ErrorCode.LEAD_NOT_FOUND,
            resource_type="Lead",
            resource_id=lead_id
        )  # ✅

    return lead
```

**利用可能な例外クラス**:
- `DiagnoLeadsException` - 基底クラス
- `AuthenticationError` - 認証エラー
- `AuthorizationError` - 認可エラー（権限不足）
- `TenantError` - テナント関連エラー
- `TenantAccessDeniedError` - マルチテナント分離違反
- `ResourceNotFoundError` - リソース未発見
- `ValidationError` - バリデーションエラー
- `ExternalServiceError` - 外部サービスエラー
- `DatabaseError` - データベースエラー

詳細: [`backend/app/core/exceptions.py`](../backend/app/core/exceptions.py)

#### 3. マルチテナント分離の徹底（最重要）

**ルール**: すべてのデータベースクエリに `tenant_id` フィルタを適用

**悪い例**:
```python
# テナントフィルタなし - セキュリティリスク ❌
assessments = db.query(Assessment).all()
```

**良い例**:
```python
# 必ずテナントでフィルタリング ✅
assessments = db.query(Assessment).filter(
    Assessment.tenant_id == current_tenant.id
).all()
```

**ヘルパー関数の使用**:
```python
from app.core.deps import get_current_tenant

@router.get("/assessments")
async def get_assessments(
    current_tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    assessments = db.query(Assessment).filter(
        Assessment.tenant_id == current_tenant.id
    ).all()
    return assessments
```

詳細: [docs/SECURITY.md - マルチテナント分離](./SECURITY.md#1-マルチテナント分離最優先)

#### 4. 環境設定の使用

**ルール**: ハードコーディング禁止、必ず `settings` から読み込む

**悪い例**:
```python
# ハードコーディング ❌
ANTHROPIC_API_KEY = "sk-ant-api03-xxxxx"
```

**良い例**:
```python
from app.core.config import settings

# 環境変数から読み込み ✅
anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
```

詳細: [`backend/app/core/config.py`](../backend/app/core/config.py)

### TypeScript（フロントエンド）

#### 1. コードフォーマット

**ツール**: `ESLint`, `Prettier`

```bash
# リント実行
npm run lint

# フォーマット
npm run format

# 型チェック
npm run type-check
```

#### 2. コンポーネント設計

**原則**:
- 1コンポーネント = 1ファイル
- 200行以下を目標
- プレゼンテーション層とロジック層の分離

**例**:
```tsx
// components/leads/LeadCard.tsx
import { Lead } from '@/types/lead';

interface LeadCardProps {
  lead: Lead;
  onStatusChange: (newStatus: string) => void;
}

export const LeadCard: React.FC<LeadCardProps> = ({ lead, onStatusChange }) => {
  return (
    <div className="border rounded-lg p-4">
      <h3>{lead.name}</h3>
      <p>{lead.email}</p>
      <button onClick={() => onStatusChange('contacted')}>
        連絡済みにする
      </button>
    </div>
  );
};
```

#### 3. 状態管理

**ルール**:
- ローカルUI状態 → `useState`
- 認証状態 → `Zustand` (`authStore`)
- サーバー状態 → `TanStack Query`

**例**:
```typescript
// サーバー状態の取得
import { useQuery } from '@tanstack/react-query';
import { leadService } from '@/services/leadService';

function LeadsPage() {
  const { data: leads, isLoading, error } = useQuery({
    queryKey: ['leads'],
    queryFn: () => leadService.getLeads(),
    staleTime: 5 * 60 * 1000, // 5分
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return <LeadList leads={leads} />;
}
```

---

## テストの実行

### バックエンドテスト

#### 全テストの実行

```bash
cd backend
source venv/bin/activate

# すべてのテストを実行
pytest

# カバレッジ付きで実行
pytest --cov=app --cov-report=html

# 特定のテストファイルのみ
pytest tests/test_lead.py

# 特定のテスト関数のみ
pytest tests/test_lead.py::test_create_lead

# 統合テスト（マルチテナント分離）
pytest tests/integration/test_multi_tenant_isolation.py -v
```

#### テストの並列実行（高速化）

```bash
# pytest-xdist をインストール
pip install pytest-xdist

# 4つの並列プロセスで実行
pytest -n 4
```

#### テストカバレッジの確認

```bash
pytest --cov=app --cov-report=term-missing

# HTMLレポート生成
pytest --cov=app --cov-report=html
# htmlcov/index.html をブラウザで開く
```

### フロントエンドテスト

```bash
cd frontend

# すべてのテストを実行
npm test

# カバレッジ付きで実行
npm run test:coverage

# ウォッチモード（開発時）
npm test -- --watch

# 特定のテストファイル
npm test -- HelpStepItem.test.tsx
```

### E2Eテスト（予定）

```bash
# Playwright E2Eテスト（将来実装予定）
cd frontend
npx playwright test
```

---

## デバッグ方法

### バックエンドのデバッグ

#### 1. ロギング

```python
import structlog

logger = structlog.get_logger()

# デバッグログ
logger.debug("Lead retrieved", lead_id=lead.id, tenant_id=lead.tenant_id)

# エラーログ
logger.error("Failed to send GA4 event", error=str(e), lead_id=lead_id)
```

#### 2. IPDBでのブレークポイント

```python
# requirements-dev.txt に ipdb が含まれている
import ipdb

def process_lead(lead_id):
    lead = get_lead(lead_id)
    ipdb.set_trace()  # ブレークポイント
    # ... 処理 ...
```

#### 3. FastAPI自動ドキュメント

開発サーバー起動後、以下のURLでAPIを確認・テスト可能:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### フロントエンドのデバッグ

#### 1. React Developer Tools

Chrome/Firefox拡張機能をインストール:
- [React Developer Tools](https://react.dev/learn/react-developer-tools)

#### 2. TanStack Query Devtools

既に実装済み（開発環境のみ）:
```tsx
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// App.tsx 内で
<ReactQueryDevtools initialIsOpen={false} />
```

#### 3. コンソールログ

```typescript
// API呼び出しのログは自動的に出力される
console.log('Lead data:', lead);
```

---

## よくある問題と解決方法

### 1. データベース接続エラー

**エラー**:
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

**解決方法**:
```bash
# PostgreSQLが起動しているか確認
sudo systemctl status postgresql

# DATABASE_URLを確認
echo $DATABASE_URL

# Supabase使用の場合、URLとポート（6543）を確認
```

### 2. マイグレーションエラー

**エラー**:
```
alembic.util.exc.CommandError: Can't locate revision identified by 'xxxxx'
```

**解決方法**:
```bash
# マイグレーション履歴を確認
alembic history

# データベースをリセット（開発環境のみ）
alembic downgrade base
alembic upgrade head

# または、データベースを再作成
dropdb diagnoleads
createdb diagnoleads
alembic upgrade head
```

### 3. フロントエンドのCORS エラー

**エラー**:
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**解決方法**:
```python
# backend/app/core/config.py で ALLOWED_ORIGINS を確認
ALLOWED_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://localhost:5173",  # Viteのデフォルトポート
    "http://127.0.0.1:5173",
]
```

### 4. テスト失敗（マルチテナント分離）

**エラー**:
```
AssertionError: Cross-tenant access was not prevented
```

**解決方法**:
- すべてのクエリに `tenant_id` フィルタがあるか確認
- `get_current_tenant()` Dependencyが正しく使用されているか確認
- 詳細: [docs/SECURITY.md](./SECURITY.md)

### 5. SECRET_KEYバリデーションエラー

**エラー**:
```
ValueError: 本番環境でデフォルトのSECRET_KEYを使用しています。
```

**解決方法**:
```bash
# 新しいSECRET_KEYを生成
openssl rand -hex 32

# .env ファイルに設定
SECRET_KEY=生成されたキー
```

---

## Spectralによる仕様検証

DiagnoLeadsでは、**Spectral**を使用してOpenAPI仕様の品質を自動検証しています。

### Spectralのインストール

```bash
# グローバルインストール
npm install -g @stoplight/spectral-cli

# インストール確認
spectral --version
```

### 検証コマンド

#### 基本的な検証

```bash
cd /path/to/DiagnoLeads

# OpenAPI仕様を検証
spectral lint openapi.json
```

#### フロントエンドからの実行

```bash
cd frontend

# Spectral厳格検証（推奨）
npm run validate:openapi:strict

# Breaking Change検出
npm run openapi:diff

# 包括的検証（型チェック + OpenAPI）
npm run validate
```

### Spectralルールの概要

#### エラーレベル（マージブロック）

| ルール | 説明 | 例 |
|--------|------|-----|
| `multi-tenant-path` | すべてのパスに `/tenants/{tenant_id}/` を含む | ✅ `/api/v1/tenants/{tenant_id}/leads` |
| `operation-id-naming` | operationIdはcamelCase | ✅ `createLead` ❌ `Create_Lead` |
| `operation-id-required` | すべての操作にoperationId必須 | - |
| `response-schema-required` | 成功レスポンスにスキーマ必須 | - |
| `security-required` | すべての操作にセキュリティ要件必須 | - |
| `tag-required` | すべての操作にタグ必須 | - |

#### 警告レベル（修正推奨）

| ルール | 説明 |
|--------|------|
| `error-response-format` | ErrorResponseスキーマの使用 |
| `path-parameter-description` | パラメータ説明の記載 |
| `uuid-format` | ID系パラメータはUUIDフォーマット |
| `list-response-structure` | リストレスポンスにitemsとtotal |

### Spectralエラーの修正例

#### エラー1: Multi-tenant対応漏れ

**エラーメッセージ**:
```
multi-tenant-path: Path '/api/v1/leads' must include /tenants/{tenant_id}/
```

**修正**:
```yaml
# 修正前
/api/v1/leads:
  get:
    operationId: listLeads

# 修正後
/api/v1/tenants/{tenant_id}/leads:
  get:
    operationId: listLeads
```

#### エラー2: operationId命名規則違反

**エラーメッセージ**:
```
operation-id-naming: operationId 'Create_Lead' must be camelCase
```

**修正**:
```yaml
# 修正前
operationId: Create_Lead

# 修正後
operationId: createLead
```

#### エラー3: レスポンススキーマ欠落

**エラーメッセージ**:
```
response-schema-required: Success response (2xx) must have a schema
```

**修正**:
```yaml
# 修正前
responses:
  200:
    description: Success

# 修正後
responses:
  200:
    description: Success
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Lead'
```

### Breaking Change検出

#### oasdiffのインストール

```bash
# 方法1: npm
npm install -g oasdiff

# 方法2: Homebrew (macOS)
brew install oasdiff

# 確認
oasdiff version
```

#### Breaking Changeのチェック

```bash
cd frontend

# mainブランチとの差分を確認
npm run openapi:diff

# 手動実行
oasdiff breaking <(git show main:../openapi.json) ../openapi.json
```

#### Breaking Changeの例

**Breaking Change（マージ注意）**:
```
- エンドポイントの削除
- パスの変更
- HTTPメソッドの変更
- 必須パラメータの追加
- レスポンス型の変更（string → number等）
- Enumの値削除
```

**Non-Breaking Change（安全）**:
```
- 新しいエンドポイントの追加
- オプショナルパラメータの追加
- レスポンスフィールドの追加
- Enumの値追加
```

### CI/CDでの自動検証

PRを作成すると、以下が自動実行されます：

1. **Spectral検証** - OpenAPI仕様の品質チェック
2. **oasdiff検証** - Breaking Change検出
3. **Multi-tenant準拠チェック** - すべてのパスに`tenant_id`があるか
4. **スキーマ制約チェック** - データベース制約との整合性

詳細: [`.github/workflows/spec-validation.yml`](../.github/workflows/spec-validation.yml)

### トラブルシューティング

#### エラー: Spectral not found

```bash
# Spectral CLIをインストール
npm install -g @stoplight/spectral-cli

# パスを確認
which spectral
```

#### エラー: oasdiff not found

```bash
# oasdiffをインストール
npm install -g oasdiff
# または
brew install oasdiff
```

#### 警告が多すぎる場合

既存のOpenAPI仕様に多数の警告が出る場合は、段階的に修正してください：

1. **エラーレベルから修正** - マージブロックを解除
2. **警告レベルを修正** - 品質向上
3. **ヒントレベルを確認** - ベストプラクティス適用

詳細: [OpenAPI Validation Enhancement Proposal](../openspec/changes/openapi-validation-enhancement/proposal.md)

---

## 追加リソース

### 内部ドキュメント
- [セキュリティガイドライン](./SECURITY.md) - **必読**
- [リファクタリング報告](./REFACTORING_SUMMARY.md)
- [Claude Code用ガイド](../CLAUDE.md)

### 外部リンク
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [TanStack Query](https://tanstack.com/query/latest)
- [Pydantic](https://docs.pydantic.dev/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)

---

## 質問・サポート

開発中に問題が発生した場合:

1. **このガイドを確認** - [よくある問題と解決方法](#よくある問題と解決方法)
2. **セキュリティガイドラインを確認** - [docs/SECURITY.md](./SECURITY.md)
3. **GitHub Issueを検索** - 既存の問題がないか確認
4. **新しいIssueを作成** - 詳細な情報とともに報告

Happy Coding! 🎉
