# DiagnoLeads - Project Overview

## Vision

DiagnoLeadsは、B2B企業向けのマルチテナント診断サービスプラットフォームです。複数の事業者（テナント）が独立した環境で診断コンテンツを作成・運用し、Webサイトに埋め込んで見込み顧客を獲得できます。

## Core Features

### 1. ノーコード診断作成
ドラッグ&ドロップで質問・回答選択肢を設定、スコアリングロジックを構築できる診断ビルダーを提供。

### 2. AI活用機能
- **診断自動生成**: トピックを入力するだけでClaude AIが質問・選択肢・スコアリングを自動生成
- **リード分析**: 診断回答から企業の課題を自動検出し、ホットリードスコアを算出
- **パーソナライズレポート**: 企業ごとに最適化された診断結果レポートを生成

### 3. 柔軟な埋め込み
JavaScript一行でクライアントサイトに診断機能を実装可能。

### 4. リード管理
診断結果と連動した見込み顧客情報の自動収集、スコアリング、ホットリード検出。

### 5. 分析ダッシュボード
診断完了率、離脱ポイント、コンバージョンファネルをリアルタイム可視化。

### 6. 外部連携
Salesforce、HubSpot、Slack等のMAツール・CRMと自動同期。

## Technical Architecture

### Frontend
- **Framework**: React 18 + Vite
- **Language**: TypeScript
- **State Management**: Zustand + TanStack Query
- **UI**: Tailwind CSS + shadcn/ui
- **Hosting**: Vercel

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **ORM**: SQLAlchemy 2.0
- **Hosting**: Railway

### Database
- **Primary**: PostgreSQL (Supabase)
- **Cache**: Redis (Upstash)
- **Strategy**: Shared Schema with Row-Level Security

### AI Services
- **Provider**: Anthropic Claude API
- **Models**: Claude 3.5 Sonnet
- **Use Cases**: Assessment generation, lead analysis, report generation

### Background Jobs
- **Framework**: Trigger.dev
- **Use Cases**: External integrations, analytics aggregation

## Multi-Tenant Architecture

### Data Isolation Strategy
- **Approach**: Shared Database, Shared Schema with tenant_id column
- **Security**: PostgreSQL Row-Level Security (RLS)
- **Middleware**: Automatic tenant filtering on all queries

### Authentication
- **Method**: JWT-based authentication
- **Provider**: Supabase Auth
- **Roles**: System Admin, Tenant Admin, User

## Development Approach

### Spec-Driven Development with OpenSpec
このプロジェクトはOpenSpecを使用した仕様駆動開発を採用しています。

**Workflow:**
1. **Proposal**: `/openspec-proposal` で新機能の仕様を提案
2. **Review**: チームで仕様をレビュー・調整
3. **Implementation**: `/openspec-apply` で仕様に基づき実装
4. **Archive**: `/openspec-archive` で完了した変更をアーカイブ

**Benefits:**
- 明確な仕様定義により手戻りを削減
- 実装と仕様の乖離を防止
- 自動的にドキュメント化

## Cost Structure (Startup Phase)

### Phase 1: MVP/Beta (~10 tenants)
- **Monthly Cost**: $30-50
- **Primary Cost**: Claude API usage
- **Infrastructure**: Free tiers (Vercel, Railway, Supabase, Upstash)

### Phase 2: Launch (~50 tenants)
- **Monthly Cost**: $150-200
- **Revenue Projection**: ¥1,500,000/month (¥30,000/tenant)

### Phase 3: Scale (~200 tenants)
- **Monthly Cost**: $500-1,000
- **Revenue Projection**: ¥5,000,000/month

## Success Metrics

### Technical KPIs
- API response time < 200ms (p95)
- Assessment generation success rate > 95%
- Uptime > 99.5%

### Business KPIs
- Monthly Active Tenants
- Assessments created per tenant
- Lead conversion rate
- Customer retention rate

## Security & Compliance

### Data Protection
- Row-Level Security (RLS) enforcement
- Encrypted data at rest and in transit
- Regular security audits

### Compliance
- GDPR-compliant data handling
- ISO 27001 準拠予定
- プライバシーポリシー整備

## Roadmap

### Q1 2025
- ✅ Project setup with OpenSpec
- ⏳ MVP development (auth, multi-tenant, assessment builder)
- ⏳ AI integration (Claude API)
- ⏳ Beta launch

### Q2 2025
- Lead management features
- Analytics dashboard
- External integrations (Salesforce, HubSpot)
- Official launch

### Q3 2025
- Advanced AI features
- Custom branding
- White-label options
- Mobile app (optional)

### Q4 2025
- Enterprise features
- Advanced analytics
- Custom integrations
- Scale to 200+ tenants

## Feature Specs (Index)

### UI/UX Specifications
- **Design System**: [./ui-ux/design-system.md](./ui-ux/design-system.md) - Colors, typography, spacing, shadows
- **Component Library**: [./ui-ux/component-library.md](./ui-ux/component-library.md) - Reusable UI components
- **Usability Guidelines**: [./ui-ux/usability-guidelines.md](./ui-ux/usability-guidelines.md) - Accessibility & best practices
- **Interaction Patterns**: [./ui-ux/interaction-patterns.md](./ui-ux/interaction-patterns.md) - Animations & micro-interactions

### Core Features
- AI Support: [./features/ai-support.md](./features/ai-support.md)
- Embed Widget: [./features/embed-widget.md](./features/embed-widget.md)
- Lead Management: [./features/lead-management.md](./features/lead-management.md)
- Analytics Dashboard: [./features/analytics-dashboard.md](./features/analytics-dashboard.md)
- Publishing & Versioning: [./features/publishing-and-versioning.md](./features/publishing-and-versioning.md)
- Integrations (Base): [./features/integrations.md](./features/integrations.md)

### Innovative Features (Phase 1-4)
- **Microsoft Teams Integration**: [./features/microsoft-teams-integration.md](./features/microsoft-teams-integration.md) ⚡ Priority: Critical
- **Multi-Channel Distribution**: [./features/multi-channel-distribution.md](./features/multi-channel-distribution.md) (LINE, SMS, Email, QR, NFC)
- **AI Optimization Engine**: [./features/ai-optimization-engine.md](./features/ai-optimization-engine.md) (A/B Testing, Copywriting, Predictions)
- **Real-time Collaboration**: [./features/realtime-collaboration.md](./features/realtime-collaboration.md) (Google Docs風)
- Assessment Marketplace (Coming Soon)
- Gamification Engine (Coming Soon)
- Video & Voice Assessments (Coming Soon)
- Assessment Funnel Chains (Coming Soon)
- White-Label Solutions (Coming Soon)

### API Reference
- **Endpoints Overview**: [./api/endpoints-overview.md](./api/endpoints-overview.md) - Complete API documentation v2.0

### Change Proposals
- **Innovative Features Proposal**: [../changes/2025-11-10-innovative-features/innovative-features.md](../changes/2025-11-10-innovative-features/innovative-features.md) - 12の革新的機能提案
