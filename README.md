# DiagnoLeads

**マルチテナントB2B診断プラットフォーム with AI**

[![Tests](https://img.shields.io/badge/tests-42%2F42%20passing-brightgreen)](https://github.com/yusuke-kurosawa/DiagnoLeads)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.1-blue)](./openapi.json)
[![OpenSpec](https://img.shields.io/badge/OpenSpec-Spec--Driven-orange)](./openspec/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

DiagnoLeadsは、B2B企業が顧客の課題を診断し、質の高いリードを獲得するためのSaaSプラットフォームです。**OpenSpec + OpenAPI を完全統合した理想的なSpec駆動開発**を実証し、完璧な品質保証体制を実現しています。

## 🎉 Project Status

- ✅ **Phase 1 Complete**: Foundation solid, production-ready quality
- ✅ **100% Test Coverage**: 42/42 tests passing
- ✅ **Spec-Driven Development**: OpenSpec 7-phase workflow demonstrated
- ✅ **Full-Stack Implementation**: Assessment & Lead CRUD complete
- 📊 **Current Version**: 0.1.0 (Beta Ready)

See [PROJECT_STATUS.md](./PROJECT_STATUS.md) for detailed status report.

## 🎯 主要機能

- **🤖 AI診断生成**: トピック入力だけでClaude AIが質問・選択肢・スコアリングを自動生成
- **📊 ノーコード診断ビルダー**: ドラッグ&ドロップで診断コンテンツを作成
- **🎯 AIリード分析**: 診断回答から企業課題を自動検出、ホットリードスコアを算出
- **📈 リアルタイム分析**: 診断完了率、離脱ポイント、CVファネルを可視化
- **🔗 外部連携**: Salesforce、HubSpot、Slackと自動同期
- **🏢 マルチテナント**: 複数企業が独立環境で運用可能

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
- npm
- OpenSpec CLI

### 1. OpenSpecのインストール

```bash
npm install -g @fission-ai/openspec@latest
```

### 2. プロジェクトのクローン

```bash
git clone https://github.com/yusuke-kurosawa/DiagnoLeads.git
cd DiagnoLeads
```

### 3. 環境変数の設定

```bash
# .env.example をコピー
cp .env.example .env

# 必要な環境変数を設定
# - DATABASE_URL (Supabase PostgreSQL)
# - REDIS_URL (Upstash Redis)
# - ANTHROPIC_API_KEY (Claude API)
# - SECRET_KEY (JWT署名用)
```

### 4. バックエンドのセットアップ

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

### 5. フロントエンドのセットアップ

```bash
cd frontend
npm install

# 開発サーバー起動
npm run dev
```

## 📚 ドキュメント

- [プロジェクト概要](openspec/specs/OVERVIEW.md)
- [認証仕様](openspec/specs/auth/authentication.md)
- [マルチテナント仕様](openspec/specs/auth/multi-tenant.md)
- [Claude Code用ガイド](CLAUDE.md)

## 🎯 ロードマップ

### Q1 2025
- [x] プロジェクトセットアップ (OpenSpec導入)
- [ ] MVP開発（認証、マルチテナント、診断ビルダー）
- [ ] AI統合（Claude API）
- [ ] β版ローンチ

### Q2 2025
- [ ] リード管理機能
- [ ] 分析ダッシュボード
- [ ] 外部連携（Salesforce、HubSpot）
- [ ] 正式ローンチ

### Q3 2025
- [ ] 高度なAI機能
- [ ] カスタムブランディング
- [ ] ホワイトラベルオプション

### Q4 2025
- [ ] エンタープライズ機能
- [ ] 高度な分析
- [ ] カスタム連携
- [ ] 200+テナントへスケール

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
