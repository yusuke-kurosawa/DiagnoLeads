# DiagnoLeads

**マルチテナントB2B診断プラットフォーム with AI**

[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.1-blue)](./openapi.json)
[![OpenSpec](https://img.shields.io/badge/OpenSpec-Spec--Driven-orange)](./openspec/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-green)](https://github.com/yusuke-kurosawa/DiagnoLeads)

DiagnoLeadsは、B2B企業が顧客の課題を診断し、質の高いリードを獲得するためのSaaSプラットフォームです。**OpenSpec + OpenAPI を完全統合した理想的なSpec駆動開発**を実証し、完璧な品質保証体制を実現しています。

## 🎉 Project Status

- ✅ **基本機能実装完了**: 診断作成、リード管理、分析ダッシュボード
- ✅ **マスタ管理機能**: トピック・業界・ユーザー管理（ドラッグ&ドロップソート機能付き）
- ✅ **UI/UX改善**: エラーハンドリング、フォームレイアウト最適化
- ✅ **革新的機能仕様完成**: 12の画期的機能を提案・文書化（Phase 1-4）
- 🚧 **Phase 1準備中**: Teams統合、LINE統合、AI A/Bテストの実装計画策定完了
- 📊 **Current Version**: 0.1.0 (MVP)

See [docs/SESSION_SUMMARY.md](./docs/SESSION_SUMMARY.md) for complete session summary.

## 🎯 主要機能

### 実装済み機能
- **📊 診断管理（CRUD）**: 診断の作成、編集、削除、一覧表示
- **📋 マスタ管理**: トピック・業界のドラッグ&ドロップソート、カラーインジケーター
- **👥 ユーザー管理**: テナント内ユーザーの作成、編集、権限管理
- **📈 基本分析**: 診断完了率、CVファネルの可視化
- **🏢 マルチテナント**: テナントID による論理分離、Row-Level Security (RLS)
- **🔐 認証・認可**: JWT ベース、3つのロール（システム管理者、テナント管理者、一般ユーザー）
- **🛡️ エラーハンドリング**: 包括的なエラーページ、強化されたエラーロギング
- **📖 ユーザーガイド機能**: コンテキスト対応ヘルプ、ヘルプセンター、Tooltip（100%テストカバレッジ）

### 計画中の機能（Phase 1-4）
- **🤖 AI診断生成**: トピック入力だけでClaude AIが質問・選択肢を自動生成
- **🎯 AIリード分析**: 診断回答から企業課題を自動検出、ホットリードスコアを算出
- **📊 ノーコード診断ビルダー**: ドラッグ&ドロップでの質問作成（強化版）

### 革新的機能（Phase 1-4: 12ヶ月計画）

#### ⚡ Phase 1 (3ヶ月) - 計画済み
- **Microsoft Teams統合** ⭐ 業界初
  - Adaptive Cards通知
  - Bot対話型診断
  - 会議内診断実施
- **マルチチャネル配信**
  - LINE Official Account（日本市場）
  - SMS配信（Twilio）
  - QRコード/NFC（オフラインイベント）
- **AI A/Bテスト自動化** ⭐ 業界初
  - トンプソンサンプリング
  - 自動最適化

#### 📋 Phase 2-4 (9ヶ月) - 計画済み
- **リアルタイムコラボレーション** ⭐ Google Docs風
- **診断マーケットプレイス** ⭐ 業界初
- **音声/ビデオ診断**
- **ゲーミフィケーション**
- **ホワイトラベル**
- その他7機能

詳細: [革新的機能提案](./openspec/changes/2025-11-10-innovative-features/innovative-features.md)

## 🚀 技術スタック（低コストスタートアップ構成）

### フロントエンド
- **React 18** + Vite + TypeScript
- **Zustand** (状態管理) + **TanStack Query** (サーバー状態)
- **Tailwind CSS** + **shadcn/ui** (UIコンポーネント)
- **Vercel** (ホスティング - 無料枠)

### バックエンド
- **FastAPI** (Python 3.11+)
- **SQLAlchemy 2.0** (ORM)
- **Railway** (ホスティング - 無料枠 → $5/月)

### データベース
- **PostgreSQL** (Supabase - 無料枠)
  - Row-Level Security (RLS) でマルチテナント実装
- **Redis** (Upstash - 無料枠)

### AI
- **Anthropic Claude API** (Claude 3.5 Sonnet)
  - 診断生成、リード分析、レポート作成

### インフラ
- **Trigger.dev** (非同期ジョブ - 無料枠)
- **GitHub Actions** (CI/CD)

## 💰 コスト構造

| フェーズ | テナント数 | 月額コスト | 主な変更 |
|---------|----------|----------|---------|
| **MVP/β** | ~10 | $30-50 | すべて無料枠 |
| **ローンチ** | ~50 | $150-200 | 有料プランに移行 |
| **スケール** | ~200 | $500-1,000 | サーバー増強 |

## 📐 アーキテクチャ

### OpenSpec仕様駆動開発

このプロジェクトは**OpenSpec**を使用した仕様駆動開発(Spec-Driven Development)を採用しています。

```
openspec/
├── specs/           # 承認済み仕様（Source of Truth）
│   ├── OVERVIEW.md
│   ├── auth/
│   │   ├── authentication.md
│   │   └── multi-tenant.md
│   └── assessments/
├── changes/         # レビュー中の変更提案
└── archive/         # 完了した変更
```

### 開発ワークフロー

```bash
# 1. 新機能の仕様を提案
/openspec-proposal "AI診断生成機能を追加"

# 2. レビュー・調整（仕様ファイル編集）

# 3. 実装
/openspec-apply

# 4. 完了後アーカイブ
/openspec-archive
```

## 🛠️ セットアップ

### 前提条件

- Node.js 18+
- Python 3.11+
- PostgreSQL 14+ (Supabase推奨)
- Redis (Upstash推奨)

### 1. プロジェクトのクローン

```bash
git clone https://github.com/yusuke-kurosawa/DiagnoLeads.git
cd DiagnoLeads
```

### 2. 環境変数の設定

```bash
# .env.example をコピー
cp .env.example .env

# 必要な環境変数を設定
# - DATABASE_URL (Supabase PostgreSQL)
# - REDIS_URL (Upstash Redis)
# - ANTHROPIC_API_KEY (Claude API - 計画中の機能用)
# - SECRET_KEY (JWT署名用)
```

### 3. バックエンドのセットアップ

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# データベースマイグレーション
alembic upgrade head

# 開発サーバー起動
uvicorn app.main:app --reload
```

### 4. フロントエンドのセットアップ

```bash
cd frontend
npm install

# 開発サーバー起動
npm run dev
```

## 📚 ドキュメント

### プロジェクト管理
- [セッションサマリー](./docs/SESSION_SUMMARY.md) ⭐ 最新の開発状況
- [Phase 1実装計画](./docs/IMPLEMENTATION_PLAN_PHASE1.md) ⭐ 12週間の詳細計画
- [Teams統合セットアップガイド](./docs/SETUP_GUIDE_TEAMS.md) ⭐ Azure AD登録手順
- [本番環境デプロイガイド](./docs/PRODUCTION_DEPLOYMENT_GUIDE.md)
- [クイックスタートデプロイ](./docs/QUICKSTART_DEPLOYMENT.md)

### OpenSpec仕様
- [プロジェクト概要](./openspec/specs/OVERVIEW.md)
- [革新的機能提案](./openspec/changes/2025-11-10-innovative-features/innovative-features.md) ⭐ 12機能
- [Microsoft Teams統合](./openspec/specs/features/microsoft-teams-integration.md)
- [マルチチャネル配信](./openspec/specs/features/multi-channel-distribution.md)
- [AI最適化エンジン](./openspec/specs/features/ai-optimization-engine.md)
- [リアルタイムコラボ](./openspec/specs/features/realtime-collaboration.md)
- [API Endpoints v2.0](./openspec/specs/api/endpoints-overview.md) (200+ endpoints)

### 開発ガイド
- [Claude Code用ガイド](./CLAUDE.md)
- [認証仕様](./openspec/specs/auth/authentication.md)
- [マルチテナント仕様](./openspec/specs/auth/multi-tenant.md)

## 🎯 ロードマップ

### Phase 1 (Week 1-12) - 📋 計画完了
- [x] 革新的機能仕様作成（12機能）
- [x] 実装計画策定（12週間）- [docs/IMPLEMENTATION_PLAN_PHASE1.md](./docs/IMPLEMENTATION_PLAN_PHASE1.md)
- [x] セットアップガイド作成 - [docs/SETUP_GUIDE_TEAMS.md](./docs/SETUP_GUIDE_TEAMS.md)
- [ ] **Milestone 1** (Week 1-3): Teams統合基盤
- [ ] **Milestone 2** (Week 4-6): Teams Bot対話機能
- [ ] **Milestone 3** (Week 7-9): LINE統合
- [ ] **Milestone 4** (Week 10-11): QR & SMS配信
- [ ] **Milestone 5** (Week 12): AI A/Bテストエンジン

詳細: [Phase 1実装計画](./docs/IMPLEMENTATION_PLAN_PHASE1.md)

### Phase 2 (Q2 2025)
- [ ] リアルタイムコラボレーション
- [ ] Microsoft Dynamics 365連携
- [ ] WhatsApp Business対応
- [ ] 診断マーケットプレイス（α版）

### Phase 3 (Q3 2025)
- [ ] 音声/ビデオ診断
- [ ] ゲーミフィケーション
- [ ] 予測分析（機械学習）
- [ ] ホワイトラベル対応

### Phase 4 (Q4 2025)
- [ ] GraphQL API
- [ ] SOC2コンプライアンス
- [ ] エンタープライズ機能
- [ ] 500+テナントへスケール

詳細: [実装計画](./docs/IMPLEMENTATION_PLAN_PHASE1.md)

## 🤝 開発への参加

### 開発の流れ（OpenSpec使用）

1. **Issueを作成** - 機能要求やバグ報告
2. **仕様提案** - `/openspec-proposal` で仕様を明確化
3. **レビュー** - チームで仕様をレビュー
4. **実装** - `/openspec-apply` で実装
5. **PR作成** - コードレビュー後マージ

### コミット規約

```
feat: 新機能追加
fix: バグ修正
docs: ドキュメント更新
refactor: リファクタリング
test: テスト追加
```

## 📄 ライセンス

MIT License - 詳細は[LICENSE](LICENSE)を参照

## 🙋 サポート

- **GitHub Issues**: バグ報告・機能要求
- **Email**: support@diagnoleads.com（予定）
- **Docs**: https://docs.diagnoleads.com（予定）

## 🎉 謝辞

このプロジェクトは以下のオープンソースツールに支えられています：

- [OpenSpec](https://github.com/Fission-AI/OpenSpec) - 仕様駆動開発フレームワーク
- [FastAPI](https://fastapi.tiangolo.com/) - 高速Webフレームワーク
- [React](https://react.dev/) - UIライブラリ
- [Anthropic Claude](https://www.anthropic.com/) - AI API
- [Supabase](https://supabase.com/) - オープンソースFirebase代替

---

**Built with ❤️ using OpenSpec Spec-Driven Development**
