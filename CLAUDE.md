# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

**DiagnoLeads**は、B2B企業向けのマルチテナント診断サービスプラットフォームです。複数の事業者（テナント）が独立した環境で診断コンテンツを作成・運用し、Webサイトに埋め込んで見込み顧客を獲得できます。

### 主要機能
- **ノーコード診断作成**: ドラッグ&ドロップで質問・回答選択肢を設定、スコアリングロジックを構築
- **柔軟な埋め込み**: JavaScript一行でクライアントサイトに診断機能を実装
- **リード管理**: 診断結果と連動した見込み顧客情報の自動収集、スコアリング、ホットリード検出
- **分析ダッシュボード**: 診断完了率、離脱ポイント、コンバージョンファネルをリアルタイム可視化
- **外部連携**: Salesforce、HubSpot、Slack等のMAツール・CRMと自動同期

## アーキテクチャ

### 高レベル構造

```
DiagnoLeads/
├── backend/          # バックエンドAPI（FastAPI/Django）
│   ├── api/          # REST API エンドポイント
│   ├── models/       # データモデル（テナント、診断、リード等）
│   ├── services/     # ビジネスロジック層
│   ├── integrations/ # 外部サービス連携（Salesforce、HubSpot等）
│   └── core/         # マルチテナント管理、認証・認可
├── frontend/         # 管理画面（React/Vue.js）
│   ├── components/   # UIコンポーネント
│   ├── pages/        # ページ（ダッシュボード、診断作成等）
│   ├── stores/       # 状態管理
│   └── services/     # API呼び出し
├── embed/            # 埋め込みウィジェット（Vanilla JS/WebComponents）
│   ├── widget/       # 診断ウィジェット本体
│   ├── loader/       # ローダースクリプト
│   └── styles/       # カスタマイズ可能なスタイル
├── database/         # データベーススキーマ・マイグレーション
└── docs/             # ドキュメント
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

## 技術スタック（推奨）

### バックエンド
- **言語**: Python 3.11+
- **フレームワーク**: FastAPI または Django REST Framework
- **データベース**: PostgreSQL（マルチテナント対応、JSON型サポート）
- **ORM**: SQLAlchemy / Django ORM
- **認証**: python-jose（JWT）、OAuth2
- **タスクキュー**: Celery + Redis（外部連携の非同期処理）
- **キャッシュ**: Redis

### フロントエンド（管理画面）
- **言語**: TypeScript
- **フレームワーク**: React 18+ / Vue 3+
- **ルーティング**: React Router / Vue Router
- **状態管理**: Redux Toolkit / Pinia
- **UIライブラリ**: Tailwind CSS, shadcn/ui
- **フォーム**: React Hook Form / VeeValidate
- **データ可視化**: Chart.js, Recharts

### 埋め込みウィジェット
- **言語**: TypeScript
- **アプローチ**: Web Components または Vanilla JS（フレームワーク非依存）
- **バンドル**: Rollup / Vite（最小サイズ化）
- **スタイル**: Shadow DOM によるカプセル化

### インフラ
- **コンテナ**: Docker, Docker Compose
- **オーケストレーション**: Kubernetes（本番環境）
- **CI/CD**: GitHub Actions
- **監視**: Prometheus + Grafana
- **ログ**: ELK Stack / CloudWatch

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

### Docker環境

```bash
# すべてのサービスを起動（バックエンド、フロントエンド、DB、Redis）
docker-compose up -d

# ログ確認
docker-compose logs -f backend

# データベースマイグレーション（コンテナ内で実行）
docker-compose exec backend alembic upgrade head

# テスト実行（コンテナ内）
docker-compose exec backend pytest

# すべてのサービスを停止・削除
docker-compose down -v
```

## 重要な開発規約

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

ミドルウェアまたはデコレーターで自動的にテナントスコープを適用することを推奨します。

### APIエンドポイント設計

- テナント固有のリソースは `/api/v1/tenants/{tenant_id}/assessments` のようなパスを使用
- 認証が必要なエンドポイントには必ずJWT検証を実装
- ページネーション、フィルタリング、ソートをサポート

### 埋め込みウィジェットの考慮事項

- **名前空間の衝突回避**: すべてのグローバル変数・関数に `DiagnoLeads_` プレフィックス
- **CSSの分離**: Shadow DOM またはプレフィックス付きクラス名を使用
- **パフォーマンス**: バンドルサイズを50KB以下に抑える（gzip圧縮前）
- **クロスドメイン対応**: CORS設定を適切に行う

### 外部連携の実装

- Celeryタスクとして非同期実行
- リトライロジックを実装（最大3回、指数バックオフ）
- 認証情報は環境変数または暗号化して保存
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
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/diagnoleads

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External Integrations
SALESFORCE_CLIENT_ID=
SALESFORCE_CLIENT_SECRET=
HUBSPOT_API_KEY=
SLACK_WEBHOOK_URL=

# Environment
ENVIRONMENT=development  # development, staging, production
DEBUG=True
```

## 参考リソース

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Multi-Tenancy](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Web Components Best Practices](https://web.dev/custom-elements-best-practices/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/) - セキュリティベストプラクティス
