# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

**DiagnoLeads**は、B2B企業向けのマルチテナント診断サービスプラットフォームです。複数の事業者（テナント）が独立した環境で診断コンテンツを作成・運用し、Webサイトに埋め込んで見込み顧客を獲得できます。

### 主要機能
- **🤖 AI診断生成**: Claude APIでトピック入力だけで質問・選択肢・スコアリングを自動生成
- **📊 ノーコード診断ビルダー**: ドラッグ&ドロップで質問・回答選択肢を設定
- **🎯 AIリード分析**: 診断回答から企業課題を自動検出、ホットリードスコアを算出
- **📈 リアルタイム分析**: 診断完了率、離脱ポイント、CVファネルを可視化
- **🔗 外部連携**: Salesforce、HubSpot、Slackと自動同期
- **🏢 マルチテナント**: 複数企業が独立環境で運用可能

## アーキテクチャ

### OpenSpec仕様駆動開発

このプロジェクトは**OpenSpec**を使用した仕様駆動開発を採用しています。

**ワークフロー:**
1. `/openspec-proposal` - 新機能の仕様を提案
2. レビュー・調整（仕様ファイル編集）
3. `/openspec-apply` - 仕様に基づき実装
4. `/openspec-archive` - 完了した変更をアーカイブ

**仕様ファイルの場所:**
- `openspec/specs/` - 承認済み仕様（Source of Truth）
- `openspec/changes/` - レビュー中の変更提案
- `openspec/archive/` - 完了した変更

### 高レベル構造

```
DiagnoLeads/
├── openspec/                          # OpenSpec仕様管理
│   ├── specs/                         # 承認済み仕様（Source of Truth）
│   │   ├── OVERVIEW.md
│   │   ├── auth/
│   │   │   ├── authentication.md
│   │   │   └── multi-tenant.md
│   │   ├── assessments/
│   │   ├── leads/
│   │   └── integrations/
│   ├── changes/                       # 変更提案
│   └── archive/                       # 完了した変更
│
├── backend/                           # FastAPIバックエンド
│   ├── app/
│   │   ├── main.py
│   │   ├── api/v1/                    # REST API エンドポイント
│   │   ├── models/                    # SQLAlchemyモデル
│   │   ├── services/                  # ビジネスロジック層
│   │   │   └── ai/                    # AI機能（診断生成、リード分析）
│   │   ├── integrations/              # 外部サービス連携
│   │   └── core/                      # マルチテナント、認証
│   ├── tests/
│   └── requirements.txt
│
├── frontend/                          # React + Vite
│   ├── src/
│   │   ├── features/                  # 機能ベースの構造
│   │   │   ├── assessments/
│   │   │   ├── leads/
│   │   │   └── analytics/
│   │   ├── components/                # 共通UIコンポーネント
│   │   ├── stores/                    # Zustand状態管理
│   │   └── lib/                       # ユーティリティ、API
│   └── package.json
│
├── embed/                             # 埋め込みウィジェット
│   └── ...
│
└── docs/                              # ドキュメント
```

### マルチテナントアーキテクチャ

**テナント分離戦略**:
- データベースレベル: テナントIDによる論理分離（Shared Schema with Tenant ID）
- 各テーブルに`tenant_id`カラムを持ち、すべてのクエリでテナントフィルタリング
- Row-Level Security (RLS) を活用してデータ漏洩を防止

**認証・認可**:
- JWT（JSON Web Token）ベースの認証
- テナント管理者、一般ユーザー、システム管理者の3つのロール
- テナントスコープの権限管理

### データモデルの主要エンティティ

1. **Tenant（テナント）**: 事業者情報、契約プラン、設定
2. **Assessment（診断）**: 診断コンテンツ、質問、スコアリングロジック
3. **Question（質問）**: 質問文、回答選択肢、分岐ロジック
4. **Response（回答）**: ユーザーの診断回答データ
5. **Lead（リード）**: 獲得した見込み顧客情報、スコア
6. **Integration（連携）**: 外部サービス連携設定、認証情報

### 埋め込みウィジェットの動作

1. クライアントサイトに埋め込みスクリプトを配置
2. ウィジェットがテナントIDを元にDiagnoLeadsサーバーから診断データを取得
3. ユーザーが質問に回答
4. 回答データをリアルタイムで送信、スコアリング
5. 結果表示 + リード情報収集フォーム表示
6. 収集したリード情報をテナントのダッシュボードに即座に反映

## 技術スタック（低コストスタートアップ構成）

### バックエンド
- **言語**: Python 3.11+
- **フレームワーク**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **データベース**: PostgreSQL (Supabase無料枠)
- **キャッシュ**: Redis (Upstash無料枠)
- **認証**: Supabase Auth + JWT
- **非同期ジョブ**: Trigger.dev (無料枠)
- **ホスティング**: Railway (無料枠 → $5/月)

### フロントエンド
- **言語**: TypeScript
- **フレームワーク**: React 19 + Vite
- **状態管理**: Zustand (軽量) + TanStack Query (サーバー状態)
- **ルーティング**: React Router 7
- **URL状態管理**: nuqs（型安全な検索パラメータ管理）
- **UIライブラリ**: Tailwind CSS + shadcn/ui
- **フォーム**: React Hook Form + Zod
- **データ可視化**: Recharts
- **ホスティング**: Vercel (無料枠)

### AI機能
- **プロバイダー**: Anthropic Claude API
- **モデル**: Claude 3.5 Sonnet
- **用途**: 診断生成、リード分析、レポート作成
- **コスト**: 従量課金（月$30-100想定）

### 埋め込みウィジェット
- **言語**: TypeScript
- **アプローチ**: Web Components（フレームワーク非依存）
- **バンドル**: Vite（最小サイズ化）
- **スタイル**: Shadow DOM

### インフラ
- **CI/CD**: GitHub Actions
- **監視**: Sentry (無料枠) + Vercel Analytics
- **ドメイン**: カスタムドメイン

### コスト構造
- **MVP/β版（~10テナント）**: 月$30-50（ほぼAI API費用のみ）
- **正式ローンチ（~50テナント）**: 月$150-200
- **スケールアップ（~200テナント）**: 月$500-1,000
- **エンタープライズ（500+テナント）**: AWS移行検討

## 開発コマンド

### バックエンド開発

```bash
# 仮想環境のセットアップ
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 開発用ツール

# データベースマイグレーション
alembic upgrade head  # SQLAlchemyの場合
python manage.py migrate  # Djangoの場合

# 開発サーバー起動
uvicorn main:app --reload  # FastAPI
python manage.py runserver  # Django

# テスト実行
pytest tests/  # すべてのテスト
pytest tests/test_assessments.py  # 特定のテスト
pytest -v --cov=.  # カバレッジ付き

# リンター・フォーマッター
ruff check .  # リント
ruff format .  # フォーマット
mypy .  # 型チェック
```

### フロントエンド開発

```bash
cd frontend

# 依存関係のインストール
npm install

# 開発サーバー起動
npm run dev

# ビルド
npm run build

# テスト実行
npm test  # すべてのテスト
npm test -- AssessmentBuilder.test.tsx  # 特定のテスト
npm run test:coverage  # カバレッジ付き

# リンター・フォーマッター
npm run lint  # ESLint
npm run format  # Prettier
npm run type-check  # TypeScriptの型チェック
```

### 埋め込みウィジェット開発

```bash
cd embed

# 依存関係のインストール
npm install

# 開発サーバー（テストページ付き）
npm run dev

# ビルド（本番用最小化）
npm run build

# テスト実行
npm test
```

### OpenSpec開発ワークフロー

```bash
# 新機能の仕様を提案（Claude Codeで使用）
/openspec-proposal "AI診断生成機能を追加"

# 生成された仕様ファイルをレビュー・編集
# openspec/changes/YYYY-MM-DD-feature-name/

# 仕様に基づいて実装
/openspec-apply

# 実装完了後、変更をアーカイブ
/openspec-archive

# 仕様ファイルの確認
cat openspec/specs/assessments/ai-generation.md
```

## 重要な開発規約

### コーディングスタイルと品質基準

#### Python コーディング規約
**必須**: PEP8準拠 + プロジェクト固有ルール

```python
# ✅ 正しいimport順序
# 1. 標準ライブラリ
import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from uuid import UUID, uuid4

# 2. サードパーティライブラリ
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

# 3. ローカルアプリケーション
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import AuthService
```

#### 日時処理の統一規約
**必須**: すべてのdatetime処理でtimezone-awareを使用

```python
from datetime import datetime, timedelta, timezone

# ❌ 絶対に使用禁止
datetime.utcnow()  # offset-naive datetime

# ✅ 必ずこちらを使用
datetime.now(timezone.utc)  # timezone-aware datetime
```

**理由**:
- PostgreSQL `DateTime(timezone=True)` との互換性
- タイムゾーンバグの防止
- 国際化対応

#### 型ヒントの使用
**推奨**: すべての関数で型ヒントを使用

```python
# ✅ 良い例
def create_lead(
    db: Session,
    data: LeadCreate,
    tenant_id: UUID,
    created_by: UUID
) -> Lead:
    """リードを作成"""
    lead = Lead(**data.model_dump(), tenant_id=tenant_id, created_by=created_by)
    db.add(lead)
    db.commit()
    return lead
```

#### Docstring規約
**推奨**: Googleスタイルのdocstring

```python
def calculate_lead_score(answers: List[Answer], weights: dict) -> int:
    """リードスコアを計算する

    Args:
        answers: 診断の回答リスト
        weights: 質問ごとの重み付け辞書

    Returns:
        int: 計算されたスコア（0-100）

    Raises:
        ValueError: answersが空の場合

    Example:
        >>> answers = [Answer(points=10), Answer(points=20)]
        >>> score = calculate_lead_score(answers, {"q1": 1.5})
        >>> print(score)
        45
    """
    if not answers:
        raise ValueError("Answers cannot be empty")

    # 実装
```

### マルチテナントデータアクセス

すべてのデータベースクエリでテナントフィルタリングを**必ず**適用してください。

**悪い例**:
```python
# テナントフィルタなし - セキュリティリスク
assessments = db.query(Assessment).all()
```

**良い例**:
```python
# 必ずテナントでフィルタリング
assessments = db.query(Assessment).filter(
    Assessment.tenant_id == current_tenant.id
).all()
```

**ベストプラクティス**: サービスクラスで自動テナントフィルタリング

```python
class AssessmentService:
    """アセスメントサービス（テナント分離保証）"""

    def __init__(self, db: Session):
        self.db = db

    def list_by_tenant(self, tenant_id: UUID) -> List[Assessment]:
        """テナントのアセスメント一覧を取得

        IMPORTANT: 必ずtenant_idでフィルタリング
        """
        return self.db.query(Assessment).filter(
            Assessment.tenant_id == tenant_id
        ).all()
```

### APIエンドポイント設計

**必須**: RESTful設計原則とテナント分離

```python
# ✅ 正しいエンドポイント設計
@router.get("/tenants/{tenant_id}/assessments")
async def list_assessments(
    tenant_id: UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """アセスメント一覧取得

    - tenant_idをパスに含める（必須）
    - 認証チェック（current_user）
    - テナント権限チェック
    - ページネーション対応
    """
    # テナント権限検証
    if current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    service = AssessmentService(db)
    return service.list_by_tenant(tenant_id, skip=skip, limit=limit)
```

**設計原則**:
- テナント固有リソース: `/api/v1/tenants/{tenant_id}/resource`
- 認証必須エンドポイント: `Depends(get_current_user)`
- ページネーション: `skip`と`limit`パラメータ
- フィルタリング: クエリパラメータで提供
- ソート: `order_by`パラメータ

### エラーハンドリング

**必須**: 一貫したエラーレスポンス

```python
from fastapi import HTTPException, status

# ✅ 良い例 - 適切なHTTPステータスコード
@router.get("/tenants/{tenant_id}/leads/{lead_id}")
async def get_lead(tenant_id: UUID, lead_id: UUID, ...):
    lead = service.get_by_id(lead_id, tenant_id)

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    return lead

# ✅ 権限エラー
if current_user.tenant_id != tenant_id:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access forbidden"
    )

# ✅ バリデーションエラー
if not data.email:
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Email is required"
    )
```

**HTTPステータスコード使用ガイド**:
- `200 OK`: 成功（GET, PUT）
- `201 Created`: 作成成功（POST）
- `204 No Content`: 削除成功（DELETE）
- `400 Bad Request`: 不正なリクエスト
- `401 Unauthorized`: 認証が必要
- `403 Forbidden`: 権限不足
- `404 Not Found`: リソースが存在しない
- `422 Unprocessable Entity`: バリデーションエラー
- `500 Internal Server Error`: サーバーエラー

### ロギングとモニタリング

**推奨**: 構造化ロギング

```python
import structlog

logger = structlog.get_logger()

# ✅ 良い例 - 構造化ログ
logger.info(
    "lead_created",
    tenant_id=str(tenant_id),
    lead_id=str(lead.id),
    score=lead.score,
    user_id=str(current_user.id)
)

# ✅ エラーログ
try:
    result = await ai_service.generate_assessment(...)
except Exception as e:
    logger.error(
        "ai_generation_failed",
        tenant_id=str(tenant_id),
        error=str(e),
        exc_info=True
    )
    raise
```

### 埋め込みウィジェットの考慮事項

- **名前空間の衝突回避**: すべてのグローバル変数・関数に `DiagnoLeads_` プレフィックス
- **CSSの分離**: Shadow DOM またはプレフィックス付きクラス名を使用
- **パフォーマンス**: バンドルサイズを50KB以下に抑える（gzip圧縮前）
- **クロスドメイン対応**: CORS設定を適切に行う

### AI機能の実装

**診断生成サービス例:**
```python
# backend/app/services/ai/assessment_generator.py
from anthropic import Anthropic

class AssessmentGenerator:
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def generate(self, topic: str, industry: str) -> dict:
        prompt = f"トピック:{topic}、業界:{industry}の診断を生成してください"
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        return parse_response(response)
```

### 外部連携の実装

- Trigger.devで非同期実行
- リトライロジックを実装（最大3回、指数バックオフ）
- 認証情報はSupabase Secrets Manager または環境変数で管理
- レート制限を考慮したAPI呼び出し

### セキュリティ

- すべてのユーザー入力をサニタイズ
- SQLインジェクション対策: ORMのパラメータ化クエリを使用
- XSS対策: フロントエンドでのHTMLエスケープ
- CSRF対策: トークン検証
- 機密情報（API鍵、DB認証情報）は `.env` ファイルで管理し、`.gitignore` に追加

## テストの方針

### バックエンド
- **単体テスト**: サービス層のビジネスロジック
- **統合テスト**: API エンドポイント（テナント分離の検証を含む）
- **E2Eテスト**: 診断作成から埋め込み、リード獲得までのフロー

### フロントエンド
- **単体テスト**: コンポーネント、状態管理、ユーティリティ関数
- **統合テスト**: ページ単位の動作
- **E2Eテスト**: Playwright / Cypress によるユーザーフロー検証

### カバレッジ目標
- バックエンド: 80%以上
- フロントエンド: 70%以上
- クリティカルパス（認証、テナント分離、スコアリング）: 100%

### テスト実装のベストプラクティス

#### 1. Importの整理
**必須**: すべてのimportはファイル先頭に配置（PEP8準拠）

```python
# ❌ 悪い例 - 関数内import
def test_something():
    from uuid import uuid4
    user_id = uuid4()

# ✅ 良い例 - ファイル先頭import
from uuid import uuid4

def test_something():
    user_id = uuid4()
```

#### 2. Timezone-Aware Datetimeの使用
**必須**: すべてのdatetime操作でtimezone-awareを使用（PostgreSQL `DateTime(timezone=True)` 対応）

```python
# ❌ 悪い例 - offset-naive datetime
from datetime import datetime, timedelta
expiry = datetime.utcnow() + timedelta(hours=1)

# ✅ 良い例 - timezone-aware datetime
from datetime import datetime, timedelta, timezone
expiry = datetime.now(timezone.utc) + timedelta(hours=1)
```

**理由**: Userモデルなどで `DateTime(timezone=True)` を使用しているため、offset-naiveとの比較でエラーが発生

#### 3. SQLAlchemyモデルとリレーションシップ
**必須**: リレーションシップは個別にモデルを作成してリンク

```python
# ❌ 悪い例 - optionsを直接dictで設定
question = Question(
    text="Question text",
    options=[{"text": "Option 1", "points": 10}]  # これは動かない
)

# ✅ 良い例 - QuestionOptionモデルを個別に作成
question = Question(text="Question text", order=1)
db_session.add(question)
db_session.commit()

option1 = QuestionOption(
    question_id=question.id,
    text="Option 1",
    points=10,
    order=1
)
db_session.add(option1)
db_session.commit()
```

#### 4. Mock/Patchの正しい使用
**必須**: 実際のimportパスでpatchを適用

```python
# ❌ 悪い例 - サービスモジュールのアトリビュートをpatch
@patch("app.services.report_export_service.Workbook")

# ✅ 良い例 - 実際のライブラリをpatch
@patch("openpyxl.Workbook")
@patch("reportlab.platypus.SimpleDocTemplate")
```

#### 5. UUID検証のテスト
**必須**: トークンテストでは有効なUUID文字列を使用

```python
# ❌ 悪い例 - 文字列をそのまま使用
data = {"sub": "user-123", "tenant_id": "tenant-456"}

# ✅ 良い例 - 有効なUUID
from uuid import uuid4
user_id = str(uuid4())
tenant_id = str(uuid4())
data = {"sub": user_id, "tenant_id": tenant_id}
```

#### 6. Fixtureの命名と使用
**推奨**: 標準的なfixture名を使用

```python
# conftest.pyで定義されているfixture
- db_session: 同期DBセッション
- test_user: テストユーザー
- test_tenant: テストテナント
- client: FastAPI TestClient

# ❌ 悪い例 - 存在しないfixture
def test_something(async_db_session):  # 定義されていない

# ✅ 良い例 - 存在するfixture
def test_something(db_session):
```

#### 7. テスト構造
**推奨**: テストクラスで論理的にグループ化

```python
class TestUserService:
    """UserServiceのテスト"""

    def test_create_user(self, db_session):
        """ユーザー作成のテスト"""
        pass

    def test_update_user(self, db_session):
        """ユーザー更新のテスト"""
        pass

class TestUserServicePasswordHashing:
    """パスワードハッシュ機能のテスト"""

    def test_hash_password(self):
        """パスワードハッシュ化のテスト"""
        pass
```

#### 8. APIエンドポイントテスト
**必須**: 正しいエンドポイントパスを使用

```python
# ❌ 悪い例 - 古いパス構造
response = client.get("/api/v1/leads")

# ✅ 良い例 - テナントIDを含む正しいパス
response = client.get(f"/api/v1/tenants/{tenant_id}/leads")
```

#### 9. テストカバレッジの優先順位

1. **最優先**: マルチテナント分離の検証
   - クロステナントアクセスの防止
   - 権限チェック (403 Forbidden)

2. **高優先**: ビジネスロジック
   - スコアリング計算
   - リード分類（Hot/Warm/Cold）
   - AI生成ロジック

3. **中優先**: CRUDオペレーション
   - 作成・更新・削除の基本動作
   - バリデーション

4. **通常**: エッジケース
   - 空データの処理
   - 不正な入力の処理
   - エラーハンドリング

#### 10. テストデータの管理

```python
# ✅ 良い例 - 明示的なテストデータ
def test_lead_scoring(db_session, test_tenant, test_user):
    lead = Lead(
        tenant_id=test_tenant.id,
        created_by=test_user.id,
        name="Test Lead",
        email="test@example.com",
        score=85,
        status="qualified"
    )
    db_session.add(lead)
    db_session.commit()

    # テストロジック
```

## データベーススキーマ管理

- マイグレーションファイルは必ずバージョン管理
- 本番環境へのマイグレーション前に必ずバックアップ
- Down migration（ロールバック）も実装
- テナントデータが混在しないようマイグレーション時に検証

## ブランチ戦略

- `main`: 本番環境
- `develop`: 開発環境
- `feature/*`: 機能開発
- `fix/*`: バグ修正
- `release/*`: リリース準備

プルリクエストには以下を含める:
- 変更内容の説明
- テストケースの追加
- 関連するIssue番号

## 環境変数

以下の環境変数を `.env` ファイルで設定してください（`.env.example` を参照）:

```bash
# Supabase (Database + Auth)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres

# Upstash Redis
REDIS_URL=https://your-redis.upstash.io

# Anthropic Claude API
ANTHROPIC_API_KEY=sk-ant-xxx

# JWT
SECRET_KEY=your-secret-key-here-generate-with-openssl
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Trigger.dev
TRIGGER_API_KEY=tr_dev_xxx
TRIGGER_API_URL=https://api.trigger.dev

# External Integrations (Optional)
SALESFORCE_CLIENT_ID=
SALESFORCE_CLIENT_SECRET=
HUBSPOT_API_KEY=
SLACK_WEBHOOK_URL=

# Environment
ENVIRONMENT=development  # development, staging, production
DEBUG=True
```

## 参考リソース

### OpenSpec & 仕様駆動開発
- [OpenSpec GitHub](https://github.com/Fission-AI/OpenSpec)
- [OpenSpec公式サイト](https://openspec.dev/)

### 技術ドキュメント
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.com/docs)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [PostgreSQL Multi-Tenancy](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [TanStack Query](https://tanstack.com/query/latest)
- [nuqs - Type-safe search params](https://nuqs.dev/) - URL検索パラメータの型安全な管理（[導入ガイド](docs/frontend/NUQS_GUIDE.md)）
- [shadcn/ui](https://ui.shadcn.com/)

### セキュリティ
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [JWT Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)

### PaaS プロバイダー
- [Vercel](https://vercel.com/docs)
- [Railway](https://docs.railway.app/)
- [Upstash](https://docs.upstash.com/)
- [Trigger.dev](https://trigger.dev/docs)
