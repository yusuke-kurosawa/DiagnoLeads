# DiagnoLeads v2 - Complete Architecture Specification

**Document Version**: 1.0
**Last Updated**: 2025-11-23
**Status**: Approved for Implementation

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Strategic Context](#strategic-context)
3. [Complete Technology Stack](#complete-technology-stack)
4. [Architecture Decisions](#architecture-decisions)
5. [Project Structure](#project-structure)
6. [Development Environment](#development-environment)
7. [Spec-Driven Development Workflow](#spec-driven-development-workflow)
8. [Migration Strategy](#migration-strategy)
9. [Cost Analysis](#cost-analysis)
10. [Setup Instructions](#setup-instructions)

---

## Executive Summary

DiagnoLeads v2 represents a complete architectural redesign to support the platform's goal of becoming **診断プラットフォームのデファクト** (the default diagnostic platform). The new architecture transitions from a separated Vite + React Router + FastAPI stack to a unified **Next.js 15 full-stack architecture** optimized for:

- 🚀 **Performance**: Bun + Turbopack for 7x faster development
- 💰 **Cost Efficiency**: Eliminates separate backend server ($30-40/month savings)
- 🔒 **Type Safety**: End-to-end TypeScript with tRPC
- 📊 **Scalability**: Edge-ready with Vercel + Drizzle ORM
- 🎯 **Developer Experience**: Spec-driven development with OpenAPI integration

---

## Strategic Context

### Business Goals

DiagnoLeads aims to be embedded in product landing pages across B2B companies, requiring:

1. **High Performance**: Sub-300ms page loads for embedded widgets
2. **SEO Excellence**: Server-side rendering for public diagnostic pages
3. **Multi-tenant Isolation**: Row-level security for enterprise clients
4. **AI-Powered Features**: Claude API for diagnostic generation and lead analysis
5. **Global Reach**: Edge deployment in Tokyo region with global CDN

### Why Complete Redesign?

**Current Issues**:
- Separate frontend/backend increases hosting costs
- Python FastAPI requires dedicated server
- Client-side rendering hurts SEO
- Type safety breaks at API boundaries
- Complex deployment pipeline

**New Approach Benefits**:
- Single Next.js deployment on Vercel
- Server Components + Client Components for optimal performance
- Full type safety with tRPC
- Automatic API documentation with OpenAPI
- Edge-ready architecture

---

## Complete Technology Stack

### Core Framework

| Category | Technology | Version | Rationale |
|----------|-----------|---------|-----------|
| **Framework** | Next.js | 15.1.5 | Latest stable, App Router, Server Components, PPR |
| **Runtime** | Node.js (Production) | 20 LTS | Vercel-managed, no manual setup required |
| **Runtime** | Bun (Development) | 1.1.38 | 7x faster installs, 2.3x faster dev server |
| **Language** | TypeScript | 5.7+ | Type safety, better DX |
| **Package Manager** | Bun | 1.1.38 | Fastest package manager, native TypeScript support |
| **Version Manager** | mise | Latest | Multi-language version management |
| **Bundler** | Turbopack | Built-in | Next.js 15 default, 700x faster than Webpack |

### Frontend Stack

| Category | Technology | Version | Rationale |
|----------|-----------|---------|-----------|
| **Styling** | Tailwind CSS | 4.0 | Oxide Engine (Rust-based, 10x faster) |
| **UI Components** | shadcn/ui | v2 | React Aria integration, accessible, customizable |
| **Icons** | Lucide React | Latest | Consistent icon system |
| **Forms** | React Hook Form | 7.54+ | Best performance, Zod integration |
| **Validation** | Zod | 3.24+ | Type-safe validation, OpenAPI generation |
| **State (Client)** | Zustand | 5.0+ | Minimal client state (auth, UI) |
| **State (Server)** | TanStack Query | 5.62+ | Server state caching, mutations |
| **State (URL)** | nuqs | 2.8+ | Type-safe URL parameters |
| **Data Grid** | TanStack Table | 8.21+ | Headless table with sorting/filtering |
| **Visualization** | Tremor | 3.19+ | Dashboard charts and analytics |
| **Notifications** | Sonner | 1.7+ | Beautiful toast notifications |
| **Internationalization** | next-intl | 3.27+ | i18n with App Router support |

### Backend Stack

| Category | Technology | Version | Rationale |
|----------|-----------|---------|-----------|
| **API (Internal)** | tRPC | 11.0+ | End-to-end type safety, no code generation |
| **API (External)** | REST API Routes | Next.js | Webhooks, public API, third-party integrations |
| **Mutations** | Server Actions | Next.js | Form submissions, optimistic updates |
| **Database** | PostgreSQL | 16+ | Supabase managed, Tokyo region |
| **ORM** | Drizzle ORM | 0.38+ | 10x faster than Prisma, edge-compatible |
| **Schema Migration** | Drizzle Kit | Latest | Type-safe migrations |
| **Vector Search** | pgvector | Latest | AI embeddings for semantic search |
| **Full-Text Search** | pg_search | Latest | Japanese text search support |
| **Authentication** | BetterAuth | 0.9+ | Multi-tenant orgs, RBAC, database sessions |
| **Authorization** | CASL | 6.8+ | Attribute-based access control |
| **Job Queue** | Trigger.dev | v3 | Managed jobs, Vercel integration |
| **Email** | Resend | 4.0+ | Transactional email delivery |
| **Email Templates** | React Email | 3.0+ | React components for emails |

### AI & Analytics

| Category | Technology | Version | Rationale |
|----------|-----------|---------|-----------|
| **AI SDK** | Vercel AI SDK | 4.0+ | Streaming, Claude integration |
| **AI Provider** | Anthropic Claude | 3.5 Sonnet | Diagnostic generation, lead analysis |
| **Embeddings** | OpenAI Embeddings | text-embedding-3-small | Vector search, semantic matching |
| **Analytics** | Vercel Analytics | Latest | Web analytics, Core Web Vitals |
| **Error Tracking** | Sentry | Latest | Error monitoring, performance tracking |
| **Logging** | Axiom | Latest | Structured logging, serverless-friendly |
| **Session Replay** | Highlight.io | Latest | (Optional) User session debugging |

### Development Tools

| Category | Technology | Version | Rationale |
|----------|-----------|---------|-----------|
| **Linter/Formatter** | Biome | 1.9+ | 100x faster than ESLint+Prettier |
| **Git Hooks** | lefthook | 1.10+ | Parallel execution, Go-based, fastest |
| **Commit Convention** | commitlint | 19.7+ | Conventional Commits enforcement |
| **Type Checking** | TypeScript | 5.7+ | Strict mode, path aliases |
| **Testing (Unit)** | Vitest | 4.0+ | 7.5x faster than Jest, Vite-powered |
| **Testing (E2E)** | Playwright | 1.51+ | Cross-browser, most stable |
| **Testing (Component)** | Testing Library | Latest | User-centric component tests |
| **Visual Regression** | Percy | Latest | (Optional) Screenshot comparison |
| **API Testing** | openapi-typescript | Latest | Contract testing with OpenAPI |

### Spec-Driven Development

| Category | Technology | Version | Rationale |
|----------|-----------|---------|-----------|
| **Spec Format** | OpenSpec | Latest | Feature proposal workflow |
| **API Spec** | OpenAPI | 3.1 | REST API documentation |
| **Schema Conversion** | zod-to-openapi | Latest | Zod → OpenAPI schemas |
| **tRPC to REST** | trpc-openapi | Latest | Automatic REST API from tRPC |
| **Type Generation** | openapi-typescript | 7.4+ | OpenAPI → TypeScript types |
| **API Documentation** | Scalar | v2 | Modern OpenAPI documentation UI |

### Infrastructure & Hosting

| Category | Technology | Cost | Rationale |
|----------|-----------|------|-----------|
| **Hosting** | Vercel Pro | $20/month | Tokyo edge, automatic scaling |
| **Database** | Supabase Pro | $25/month | PostgreSQL, Row-Level Security |
| **Job Queue** | Trigger.dev Free | $0 | 100k credits/month |
| **Email** | Resend Free | $0 | 3k emails/month |
| **Error Tracking** | Sentry Free | $0 | 5k events/month |
| **Analytics** | Vercel Analytics | Included | No additional cost |
| **AI API** | Anthropic Claude | ~$30-100/month | Pay-as-you-go |
| **Domain** | Custom | ~$12/year | diagnoleads.com |
| **Total (MVP)** | - | **$45-115/month** | vs $75-155 with FastAPI |

### Development Environment

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Container** | Docker Compose | Local PostgreSQL, Redis, Mailhog, PgAdmin |
| **IDE** | VS Code | Recommended with Biome extension |
| **Database GUI** | PgAdmin 4 | Database management (localhost:5050) |
| **Email Testing** | Mailhog | Email preview (localhost:8025) |
| **Cache** | Redis | Local caching for development |

---

## Architecture Decisions

### ADR-001: Next.js 15 Full-Stack Architecture

**Status**: ✅ Approved
**Date**: 2025-11-23

**Context**:
- Current architecture splits frontend (Vite + React Router) and backend (FastAPI Python)
- Separate deployments increase complexity and cost
- Type safety breaks at API boundaries
- SEO requirements for public diagnostic pages

**Decision**:
Adopt Next.js 15 full-stack architecture, eliminating FastAPI backend.

**Consequences**:
- ✅ Single deployment reduces costs by $30-40/month
- ✅ Full type safety with tRPC
- ✅ Server Components improve performance
- ✅ Better SEO with SSR/SSG
- ⚠️ Requires migrating Python AI code to TypeScript
- ⚠️ Team needs to learn Next.js App Router

**Alternatives Considered**:
- Keep FastAPI: Rejected due to cost and complexity
- Remix: Rejected due to smaller ecosystem
- SvelteKit: Rejected due to less mature ecosystem

---

### ADR-002: Drizzle ORM over Prisma

**Status**: ✅ Approved
**Date**: 2025-11-23

**Context**:
- Need ORM for PostgreSQL with multi-tenant support
- Prisma is popular but has performance concerns
- Edge deployment planned for future

**Decision**:
Use Drizzle ORM instead of Prisma.

**Rationale**:
- **Performance**: 10x faster queries (no Prisma Client overhead)
- **Edge Compatibility**: Works on Vercel Edge without Accelerator ($29/month)
- **Bundle Size**: 10KB vs 1MB+ (critical for serverless)
- **SQL-First**: Better for complex multi-tenant queries
- **Type Safety**: TypeScript-first, better DX

**Consequences**:
- ✅ Better performance in serverless
- ✅ No additional costs for edge deployment
- ✅ Smaller bundle sizes
- ⚠️ Smaller community than Prisma
- ⚠️ Less mature admin UI tools

**Cost Savings**: $29/month (Prisma Accelerate not needed)

---

### ADR-003: BetterAuth over Lucia Auth

**Status**: ✅ Approved
**Date**: 2025-11-23

**Context**:
- Multi-tenant SaaS requires organization/team management
- Need RBAC for admin/user roles
- Database sessions for security

**Decision**:
Use BetterAuth instead of Lucia Auth.

**Rationale**:
- **Built-in Multi-Tenant**: Organization/team support out-of-box
- **RBAC**: Role-based access control included
- **Modern**: Active development, better DX
- **Database Sessions**: More secure than JWT-only
- **Social Auth**: Built-in providers (Google, GitHub, etc.)

**Consequences**:
- ✅ No need to build custom organization logic
- ✅ Better security with database sessions
- ⚠️ Beta status (0.9.x) but production-ready
- ⚠️ Less documentation than Lucia

**Trade-offs**:
- Lucia is more mature (v3) but lacks multi-tenant features
- BetterAuth is beta but has critical features we need

---

### ADR-004: Bun as Package Manager

**Status**: ✅ Approved
**Date**: 2025-11-23

**Context**:
- npm is slow for large projects
- pnpm saves disk space but still slower than Bun
- Development speed is critical

**Decision**:
Use Bun for development, Vercel uses Node.js in production automatically.

**Benchmarks**:
- **Install Speed**: Bun 7x faster than npm, 3x faster than pnpm
- **Dev Server**: Bun 2.3x faster startup than npm
- **Disk Space**: Similar to pnpm (content-addressable storage)
- **Compatibility**: 99%+ npm package compatibility

**Consequences**:
- ✅ Much faster CI/CD pipelines
- ✅ Better developer experience
- ✅ Native TypeScript support
- ✅ No production risk (Vercel uses Node.js)
- ⚠️ Team needs to install Bun locally

**Vercel Production**: Automatically uses Node.js (managed), no manual Node.js setup needed.

---

### ADR-005: Vitest over Jest

**Status**: ✅ Approved
**Date**: 2025-11-23

**Context**:
- Next.js 15 recommends Vitest for App Router testing
- Jest is slower and requires complex configuration
- Need fast feedback loop

**Decision**:
Use Vitest for unit/integration tests, Playwright for E2E.

**Benchmarks**:
- **Speed**: Vitest 5-10x faster than Jest (Vite-powered)
- **Watch Mode**: Instant hot-reload vs Jest's full re-run
- **ESM Support**: Native vs Jest's experimental mode
- **Next.js Compatibility**: Built-in support in Next.js 15

**Consequences**:
- ✅ Much faster test execution
- ✅ Better Next.js App Router support
- ✅ Simpler configuration
- ⚠️ Smaller ecosystem than Jest
- ⚠️ Team needs to learn Vitest API (similar to Jest)

**Rejected**: Buntest (too immature, missing features)

---

### ADR-006: lefthook for Git Hooks

**Status**: ✅ Approved
**Date**: 2025-11-23

**Context**:
- Need to enforce code quality before commits
- husky is slow and has npm-only installation issues
- Want parallel execution for speed

**Decision**:
Use lefthook + commitlint + Biome for Git hooks.

**Rationale**:
- **Performance**: Go-based, executes in milliseconds
- **Parallel Execution**: Runs linting, tests, typecheck concurrently
- **No npm Dependency**: Single binary, works with any package manager
- **Better DX**: Simpler configuration than husky

**Consequences**:
- ✅ Faster pre-commit hooks (parallel execution)
- ✅ Works with Bun, npm, pnpm without issues
- ✅ Easier to maintain
- ⚠️ Team needs to install lefthook locally

**Benchmark**: lefthook pre-commit runs in ~2-3 seconds vs husky ~8-10 seconds.

---

### ADR-007: Trigger.dev over BullMQ

**Status**: ✅ Approved
**Date**: 2025-11-23

**Context**:
- Need job queue for async tasks (email, integrations, reports)
- BullMQ requires Redis hosting and management
- Serverless-friendly solution preferred

**Decision**:
Use Trigger.dev v3 for job queue.

**Rationale**:
- **Managed Infrastructure**: No Redis to maintain
- **Vercel Integration**: Works seamlessly with Next.js
- **Free Tier**: 100k credits/month (sufficient for MVP)
- **Better DX**: Web UI for monitoring jobs
- **Type Safety**: TypeScript-first API

**Consequences**:
- ✅ No Redis hosting costs ($10-15/month saved)
- ✅ Better developer experience
- ✅ Automatic retries and monitoring
- ⚠️ Vendor lock-in to Trigger.dev
- ⚠️ Cold starts for infrequent jobs

**Cost Savings**: $10-15/month (no Redis hosting needed)

---

### ADR-008: Spec-Driven Development with OpenAPI

**Status**: ✅ Approved
**Date**: 2025-11-23

**Context**:
- Current DiagnoLeads uses OpenSpec workflow successfully
- Need to maintain spec-driven approach in v2
- Want automatic API documentation

**Decision**:
Integrate OpenSpec + Zod + tRPC + OpenAPI workflow.

**Workflow**:
1. **Proposal**: Write feature spec in `openspec/changes/`
2. **Schema Definition**: Define Zod schemas in `lib/validation/`
3. **Auto-Generation**: Scripts generate OpenAPI specs from Zod
4. **tRPC Implementation**: Implement tRPC routers with Zod validation
5. **REST API**: trpc-openapi generates REST endpoints automatically
6. **Documentation**: Scalar UI displays interactive API docs
7. **Type Safety**: openapi-typescript generates types for external consumers

**Consequences**:
- ✅ Single source of truth (Zod schemas)
- ✅ Automatic API documentation
- ✅ Type-safe internal (tRPC) and external (REST) APIs
- ✅ Contract testing with OpenAPI validation
- ⚠️ Initial setup complexity
- ⚠️ Team needs to learn workflow

---

### ADR-009: New Repository (diagnoleads-v2)

**Status**: ✅ Approved
**Date**: 2025-11-23

**Context**:
- Architecture is completely different from current DiagnoLeads
- Migration will take several months
- Need to maintain current version during development

**Decision**:
Create new `diagnoleads-v2` repository instead of forking.

**Rationale**:
- **Clean Start**: No legacy code or configuration
- **Parallel Development**: Current version stays operational
- **Clear Separation**: Different tech stack, different structure
- **Incremental Migration**: Can migrate features gradually

**Consequences**:
- ✅ Clean Git history
- ✅ No confusion with old codebase
- ✅ Easier onboarding for new developers
- ⚠️ Need to manually port business logic
- ⚠️ Duplicate documentation initially

**Migration Strategy**: Feature-by-feature migration, not big-bang rewrite.

---

### ADR-010: Tailwind CSS 4.0 + shadcn/ui v2

**Status**: ✅ Approved
**Date**: 2025-11-23

**Context**:
- Need consistent, accessible UI components
- Want fast development without CSS-in-JS runtime
- Tailwind CSS 4.0 released with major performance improvements

**Decision**:
Use Tailwind CSS 4.0 (Oxide Engine) + shadcn/ui v2 with React Aria Components.

**Rationale**:
- **Performance**: Oxide Engine is 10x faster (Rust-based)
- **Accessibility**: shadcn/ui v2 uses React Aria Components
- **Customization**: Copy-paste components, full control
- **No Runtime**: Zero-cost at runtime vs CSS-in-JS
- **Ecosystem**: Largest component library ecosystem

**Consequences**:
- ✅ Fast build times with Oxide Engine
- ✅ Accessible components out-of-box
- ✅ Easy customization
- ⚠️ Tailwind CSS 4.0 is in beta (stable expected Q1 2025)
- ⚠️ Large HTML files with utility classes

**Alternatives Rejected**:
- **Panda CSS**: Zero-runtime but smaller ecosystem
- **StyleX**: Meta-backed but less mature

---

## Project Structure

### Complete File Structure

```
diagnoleads-v2/
├── .claude/                                   # Claude Code configuration
│   └── commands/
│       ├── openspec-proposal.md               # Feature proposal command
│       ├── openspec-apply.md                  # Apply spec command
│       └── openspec-archive.md                # Archive completed specs
│
├── .github/
│   └── workflows/
│       ├── ci.yml                             # CI pipeline (test, lint, build)
│       ├── deploy.yml                         # Deploy to Vercel
│       └── openapi.yml                        # Generate OpenAPI on spec changes
│
├── openspec/                                  # OpenSpec workflow
│   ├── specs/                                 # Approved specifications
│   │   ├── OVERVIEW.md
│   │   ├── auth/
│   │   │   ├── authentication.md
│   │   │   └── multi-tenant.md
│   │   ├── assessments/
│   │   │   ├── ai-generation.md
│   │   │   └── embedding.md
│   │   ├── leads/
│   │   │   ├── scoring.md
│   │   │   └── analysis.md
│   │   └── integrations/
│   │       ├── salesforce.md
│   │       └── hubspot.md
│   ├── changes/                               # Pending changes
│   │   └── 2025-11-23-feature-name/
│   │       ├── spec.md
│   │       └── diagrams/
│   └── archive/                               # Completed changes
│       └── 2025-11-20-ai-generation/
│
├── openapi/                                   # OpenAPI specifications
│   ├── specs/                                 # Hand-written specs
│   │   ├── openapi.yaml                       # Main OpenAPI spec
│   │   ├── schemas/                           # Schema definitions
│   │   │   ├── auth.yaml
│   │   │   ├── leads.yaml
│   │   │   └── assessments.yaml
│   │   └── paths/                             # API endpoints
│   │       ├── auth.yaml
│   │       ├── leads.yaml
│   │       └── assessments.yaml
│   └── generated/                             # Auto-generated from Zod
│       ├── openapi.json                       # Generated OpenAPI
│       └── client.ts                          # Generated TypeScript client
│
├── app/                                       # Next.js App Router
│   ├── (auth)/                                # Auth layout group
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── register/
│   │   │   └── page.tsx
│   │   └── layout.tsx
│   ├── (marketing)/                           # Marketing layout group
│   │   ├── page.tsx                           # Landing page
│   │   ├── pricing/
│   │   │   └── page.tsx
│   │   ├── assessments/
│   │   │   └── [slug]/
│   │   │       └── page.tsx                   # Public assessment (SEO)
│   │   └── layout.tsx
│   ├── (app)/                                 # App layout group (dashboard)
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   ├── leads/
│   │   │   ├── page.tsx
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx
│   │   │   └── create/
│   │   │       └── page.tsx
│   │   ├── assessments/
│   │   │   ├── page.tsx
│   │   │   ├── [id]/
│   │   │   │   ├── page.tsx
│   │   │   │   └── edit/
│   │   │   │       └── page.tsx
│   │   │   └── create/
│   │   │       └── page.tsx
│   │   ├── analytics/
│   │   │   └── page.tsx
│   │   ├── settings/
│   │   │   ├── page.tsx
│   │   │   ├── organization/
│   │   │   │   └── page.tsx
│   │   │   └── integrations/
│   │   │       └── page.tsx
│   │   └── layout.tsx
│   ├── api/                                   # REST API routes
│   │   ├── trpc/
│   │   │   └── [trpc]/
│   │   │       └── route.ts                   # tRPC adapter
│   │   ├── openapi/
│   │   │   └── route.ts                       # OpenAPI JSON endpoint
│   │   ├── webhooks/
│   │   │   ├── salesforce/
│   │   │   │   └── route.ts
│   │   │   └── stripe/
│   │   │       └── route.ts
│   │   └── embed/
│   │       └── [assessmentId]/
│   │           └── route.ts                   # Widget data endpoint
│   ├── actions/                               # Server Actions
│   │   ├── auth.ts
│   │   ├── leads.ts
│   │   ├── assessments.ts
│   │   └── integrations.ts
│   ├── layout.tsx                             # Root layout
│   ├── page.tsx                               # Root page (redirect)
│   ├── error.tsx                              # Error boundary
│   ├── not-found.tsx                          # 404 page
│   └── globals.css                            # Global styles
│
├── components/                                # React components
│   ├── ui/                                    # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── select.tsx
│   │   ├── dialog.tsx
│   │   ├── table.tsx
│   │   └── ...
│   └── features/                              # Feature components
│       ├── auth/
│       │   ├── LoginForm.tsx
│       │   └── RegisterForm.tsx
│       ├── leads/
│       │   ├── LeadList.tsx
│       │   ├── LeadFilters.tsx
│       │   ├── LeadCard.tsx
│       │   └── LeadScoreChart.tsx
│       ├── assessments/
│       │   ├── AssessmentBuilder.tsx
│       │   ├── QuestionEditor.tsx
│       │   └── AssessmentPreview.tsx
│       ├── analytics/
│       │   ├── DashboardStats.tsx
│       │   ├── ConversionFunnel.tsx
│       │   └── LeadScoreDistribution.tsx
│       └── embed/
│           ├── EmbedWidget.tsx
│           └── EmbedPreview.tsx
│
├── lib/                                       # Shared utilities
│   ├── db/                                    # Database
│   │   ├── index.ts                           # Drizzle client
│   │   ├── schema.ts                          # Database schema
│   │   └── migrations/                        # Migration files
│   │       ├── 0001_create_tenants.sql
│   │       ├── 0002_create_users.sql
│   │       └── ...
│   ├── validation/                            # Zod schemas (source of truth)
│   │   ├── auth.ts
│   │   ├── leads.ts
│   │   ├── assessments.ts
│   │   └── common.ts
│   ├── auth/                                  # Authentication
│   │   ├── config.ts                          # BetterAuth config
│   │   ├── permissions.ts                     # CASL rules
│   │   └── middleware.ts
│   ├── ai/                                    # AI utilities
│   │   ├── claude.ts                          # Claude API client
│   │   ├── embeddings.ts                      # OpenAI embeddings
│   │   └── prompts/
│   │       ├── assessment-generation.ts
│   │       └── lead-analysis.ts
│   ├── integrations/                          # External integrations
│   │   ├── salesforce.ts
│   │   ├── hubspot.ts
│   │   └── slack.ts
│   ├── email/                                 # Email
│   │   ├── client.ts                          # Resend client
│   │   └── templates/                         # React Email templates
│   │       ├── welcome.tsx
│   │       └── lead-notification.tsx
│   ├── types/                                 # TypeScript types
│   │   ├── api.generated.ts                   # Generated from OpenAPI
│   │   ├── database.ts                        # Database types
│   │   └── models.ts                          # Business models
│   └── utils/                                 # Utility functions
│       ├── cn.ts                              # Class name merger
│       ├── date.ts                            # Date utilities
│       ├── format.ts                          # Formatters
│       └── constants.ts                       # Constants
│
├── server/                                    # tRPC server
│   ├── routers/                               # tRPC routers
│   │   ├── auth.ts
│   │   ├── leads.ts
│   │   ├── assessments.ts
│   │   ├── analytics.ts
│   │   └── integrations.ts
│   ├── context.ts                             # tRPC context
│   ├── trpc.ts                                # tRPC setup
│   └── index.ts                               # Root router
│
├── test/                                      # Tests
│   ├── unit/                                  # Vitest unit tests
│   │   ├── lib/
│   │   │   ├── validation.test.ts
│   │   │   └── utils.test.ts
│   │   └── server/
│   │       ├── routers/
│   │       │   ├── auth.test.ts
│   │       │   ├── leads.test.ts
│   │       │   └── assessments.test.ts
│   │       └── context.test.ts
│   ├── integration/                           # Integration tests
│   │   ├── api/
│   │   │   ├── auth.test.ts
│   │   │   └── leads.test.ts
│   │   └── db/
│   │       ├── multi-tenant.test.ts
│   │       └── migrations.test.ts
│   ├── e2e/                                   # Playwright E2E tests
│   │   ├── auth.spec.ts
│   │   ├── leads.spec.ts
│   │   ├── assessments.spec.ts
│   │   └── analytics.spec.ts
│   ├── fixtures/                              # Test fixtures
│   │   ├── users.ts
│   │   ├── leads.ts
│   │   └── assessments.ts
│   └── helpers/                               # Test helpers
│       ├── setup.ts
│       └── db.ts
│
├── scripts/                                   # Build/deploy scripts
│   ├── generate-openapi.ts                    # Generate OpenAPI from Zod
│   ├── generate-types.ts                      # Generate TypeScript types
│   ├── db-seed.ts                             # Seed database
│   └── db-reset.ts                            # Reset database
│
├── public/                                    # Static files
│   ├── images/
│   ├── fonts/
│   └── embed/
│       └── widget.js                          # Embed widget script
│
├── docs/                                      # Documentation
│   ├── architecture/
│   │   ├── decisions/                         # ADRs
│   │   │   ├── 001-nextjs-fullstack.md
│   │   │   ├── 002-drizzle-orm.md
│   │   │   └── ...
│   │   ├── diagrams/
│   │   └── overview.md
│   ├── api/
│   │   └── README.md                          # API documentation
│   ├── guides/
│   │   ├── getting-started.md
│   │   ├── spec-driven-development.md
│   │   └── deployment.md
│   └── contributing/
│       ├── code-style.md
│       └── git-workflow.md
│
├── .cursorrules                               # Cursor IDE rules
├── .env.example                               # Environment variables template
├── .env.local                                 # Local environment (gitignored)
├── .gitignore                                 # Git ignore rules
├── .lefthook.yml                              # Git hooks configuration
├── .mise.toml                                 # mise version manager config
├── biome.json                                 # Biome linter/formatter config
├── commitlint.config.js                       # Commitlint configuration
├── docker-compose.yml                         # Local development environment
├── drizzle.config.ts                          # Drizzle ORM configuration
├── next.config.js                             # Next.js configuration
├── package.json                               # Dependencies
├── playwright.config.ts                       # Playwright configuration
├── postcss.config.js                          # PostCSS configuration
├── tailwind.config.ts                         # Tailwind CSS configuration
├── tsconfig.json                              # TypeScript configuration
├── vitest.config.ts                           # Vitest configuration
└── README.md                                  # Project README
```

### Key Directory Purposes

| Directory | Purpose | Key Concepts |
|-----------|---------|--------------|
| `app/` | Next.js App Router pages and layouts | Route groups, Server Components, Layouts |
| `components/ui/` | shadcn/ui components | Accessible, customizable, copy-paste |
| `components/features/` | Feature-specific components | Business logic components |
| `lib/validation/` | **Source of Truth** Zod schemas | Single schema definition for validation + types + OpenAPI |
| `lib/db/` | Database schema and migrations | Drizzle ORM, multi-tenant RLS |
| `server/` | tRPC routers and configuration | Type-safe internal APIs |
| `app/api/` | REST API routes | External integrations, webhooks, public API |
| `app/actions/` | Server Actions | Form mutations, optimistic updates |
| `openspec/` | Spec-driven development | Feature proposals, approved specs, archives |
| `openapi/` | OpenAPI specifications | Auto-generated and hand-written specs |
| `test/` | All tests | unit (Vitest), integration (Vitest), e2e (Playwright) |

---

## Development Environment

### Local Development Setup

#### Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: diagnoleads-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: diagnoleads_dev
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: diagnoleads-pgadmin
    restart: unless-stopped
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@diagnoleads.local
      PGADMIN_DEFAULT_PASSWORD: admin
      PGADMIN_LISTEN_PORT: 80
    ports:
      - "5050:80"
    volumes:
      - pgadmin_data:/var/lib/pgadmin
    depends_on:
      - postgres

  redis:
    image: redis:7-alpine
    container_name: diagnoleads-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  mailhog:
    image: mailhog/mailhog:latest
    container_name: diagnoleads-mailhog
    restart: unless-stopped
    ports:
      - "1025:1025"  # SMTP
      - "8025:8025"  # Web UI
    logging:
      driver: none  # Disable logging (optional)

volumes:
  postgres_data:
    driver: local
  pgadmin_data:
    driver: local
  redis_data:
    driver: local
```

#### mise Configuration

```toml
# .mise.toml
[tools]
bun = "1.1.38"
node = "20.11.0"
lefthook = "1.10.1"

[env]
NODE_ENV = "development"
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/diagnoleads_dev"
REDIS_URL = "redis://localhost:6379"
SMTP_HOST = "localhost"
SMTP_PORT = "1025"
```

#### lefthook Configuration

```yaml
# .lefthook.yml
pre-commit:
  parallel: true
  commands:
    biome:
      glob: "*.{ts,tsx,js,jsx,json}"
      run: biome check --write {staged_files}
      stage_fixed: true
    typecheck:
      run: bun --bun tsc --noEmit
    test:
      glob: "*.{ts,tsx}"
      run: bun test --run {staged_files}

commit-msg:
  commands:
    commitlint:
      run: bunx commitlint --edit {1}

pre-push:
  parallel: true
  commands:
    test:
      run: bun test --run
    e2e:
      run: bunx playwright test
    build:
      run: bun run build
```

#### commitlint Configuration

```js
// commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'scope-enum': [
      2,
      'always',
      [
        'auth',      // 認証関連
        'leads',     // リード管理
        'assessments', // 診断コンテンツ
        'analytics', // 分析・レポート
        'ai',        // AI機能（生成、分析）
        'db',        // データベース、マイグレーション
        'api',       // API（tRPC, REST）
        'ui',        // UIコンポーネント
        'embed',     // 埋め込みウィジェット
        'integrations', // 外部連携（Salesforce, HubSpot）
        'email',     // メール送信
        'jobs',      // ジョブキュー（Trigger.dev）
        'i18n',      // 国際化
        'seo',       // SEO関連
        'ci',        // CI/CD
        'deps',      // 依存関係
        'config',    // 設定ファイル
        'docs',      // ドキュメント
        'test',      // テスト
      ],
    ],
    'type-enum': [
      2,
      'always',
      [
        'feat',     // 新機能
        'fix',      // バグ修正
        'docs',     // ドキュメント
        'style',    // コードスタイル（フォーマット）
        'refactor', // リファクタリング
        'perf',     // パフォーマンス改善
        'test',     // テスト追加・修正
        'chore',    // ビルド、ツール設定
        'ci',       // CI/CD
        'revert',   // コミットの取り消し
      ],
    ],
    'subject-case': [0],
  },
};
```

#### Biome Configuration

```json
// biome.json
{
  "$schema": "https://biomejs.dev/schemas/1.9.0/schema.json",
  "organizeImports": {
    "enabled": true
  },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "complexity": {
        "noForEach": "off"
      },
      "style": {
        "useImportType": "error",
        "useExportType": "error"
      },
      "suspicious": {
        "noExplicitAny": "warn"
      }
    }
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "single",
      "trailingComma": "es5",
      "semicolons": "always"
    }
  },
  "files": {
    "ignore": [
      "node_modules",
      ".next",
      "dist",
      "build",
      "coverage",
      "*.generated.ts"
    ]
  }
}
```

### VS Code Configuration

```json
// .vscode/settings.json
{
  "editor.defaultFormatter": "biomejs.biome",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "quickfix.biome": "explicit",
    "source.organizeImports.biome": "explicit"
  },
  "[typescript]": {
    "editor.defaultFormatter": "biomejs.biome"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "biomejs.biome"
  },
  "[json]": {
    "editor.defaultFormatter": "biomejs.biome"
  },
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true
}
```

```json
// .vscode/extensions.json
{
  "recommendations": [
    "biomejs.biome",
    "bradlc.vscode-tailwindcss",
    "dbaeumer.vscode-eslint",
    "prisma.prisma",
    "ms-playwright.playwright",
    "formulahendry.auto-rename-tag"
  ]
}
```

---

## Spec-Driven Development Workflow

### Overview

DiagnoLeads v2 uses a **Zod-first spec-driven workflow** where Zod schemas serve as the single source of truth for:

1. Runtime validation
2. TypeScript type inference
3. OpenAPI schema generation
4. tRPC procedure definitions
5. REST API documentation

### Workflow Steps

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Feature Proposal (OpenSpec)                              │
│    /openspec-proposal "Add lead scoring feature"            │
│    → Creates: openspec/changes/2025-11-23-lead-scoring/    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Define Zod Schemas (Single Source of Truth)             │
│    lib/validation/leads.ts                                  │
│                                                              │
│    export const leadCreateSchema = z.object({               │
│      name: z.string().min(1),                               │
│      email: z.string().email(),                             │
│      score: z.number().min(0).max(100),                     │
│    });                                                       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Generate OpenAPI Spec (Automatic)                        │
│    bun run generate:openapi                                 │
│    → Converts Zod → OpenAPI via zod-to-openapi             │
│    → Outputs: openapi/generated/openapi.json                │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Implement tRPC Router                                    │
│    server/routers/leads.ts                                  │
│                                                              │
│    export const leadsRouter = router({                      │
│      create: protectedProcedure                             │
│        .input(leadCreateSchema)                             │
│        .mutation(async ({ input, ctx }) => {                │
│          return await ctx.db.insert(leads).values(input);   │
│        }),                                                   │
│    });                                                       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Auto-Generate REST API (via trpc-openapi)               │
│    app/api/openapi/route.ts                                 │
│                                                              │
│    POST /api/leads → calls leadsRouter.create               │
│    (Automatic conversion from tRPC to REST)                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. Generate TypeScript Types (for External Consumers)      │
│    bun run generate:types                                   │
│    → Converts OpenAPI → TypeScript via openapi-typescript  │
│    → Outputs: lib/types/api.generated.ts                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. API Documentation (Scalar UI)                            │
│    https://app.diagnoleads.com/api/docs                     │
│    → Interactive API documentation from OpenAPI spec        │
│    → Try-it-out feature for testing                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 8. Archive Completed Spec                                   │
│    /openspec-archive                                        │
│    → Moves spec to openspec/archive/                        │
└─────────────────────────────────────────────────────────────┘
```

### Example: Lead Scoring Feature

#### Step 1: OpenSpec Proposal

```markdown
<!-- openspec/changes/2025-11-23-lead-scoring/spec.md -->
# Lead Scoring Feature

## Overview
Automatically score leads based on diagnostic responses.

## Requirements
1. Calculate score (0-100) from question answers
2. Classify as Hot (80+), Warm (50-79), Cold (<50)
3. Store score history for trend analysis

## API Changes
- POST /api/leads/calculate-score
- GET /api/leads/{id}/score-history
```

#### Step 2: Define Zod Schema

```typescript
// lib/validation/leads.ts
import { z } from 'zod';
import { createInsertSchema, createSelectSchema } from 'drizzle-zod';
import { leads } from '@/lib/db/schema';

// Base schemas from Drizzle
export const leadInsertSchema = createInsertSchema(leads);
export const leadSelectSchema = createSelectSchema(leads);

// Custom schemas for API
export const leadCreateSchema = z.object({
  name: z.string().min(1, 'Name is required').max(255),
  email: z.string().email('Invalid email'),
  company: z.string().optional(),
  phone: z.string().optional(),
  assessmentId: z.string().uuid(),
  responses: z.array(z.object({
    questionId: z.string().uuid(),
    optionId: z.string().uuid(),
    points: z.number(),
  })),
});

export const leadScoreCalculateSchema = z.object({
  responses: z.array(z.object({
    questionId: z.string().uuid(),
    optionId: z.string().uuid(),
    points: z.number().min(0).max(100),
  })),
  weights: z.record(z.string(), z.number()).optional(),
});

export const leadScoreResultSchema = z.object({
  score: z.number().min(0).max(100),
  classification: z.enum(['hot', 'warm', 'cold']),
  breakdown: z.array(z.object({
    questionId: z.string().uuid(),
    points: z.number(),
    weight: z.number(),
  })),
});

// TypeScript types inferred from Zod
export type LeadCreate = z.infer<typeof leadCreateSchema>;
export type LeadScoreCalculate = z.infer<typeof leadScoreCalculateSchema>;
export type LeadScoreResult = z.infer<typeof leadScoreResultSchema>;
```

#### Step 3: Generate OpenAPI

```typescript
// scripts/generate-openapi.ts
import { extendZodWithOpenApi } from '@asteasolutions/zod-to-openapi';
import { z } from 'zod';
import {
  leadCreateSchema,
  leadScoreCalculateSchema,
  leadScoreResultSchema,
} from '@/lib/validation/leads';

extendZodWithOpenApi(z);

// Register schemas
registry.register('LeadCreate', leadCreateSchema.openapi({
  description: 'Lead creation payload',
}));

registry.register('LeadScoreCalculate', leadScoreCalculateSchema.openapi({
  description: 'Lead score calculation input',
}));

registry.register('LeadScoreResult', leadScoreResultSchema.openapi({
  description: 'Lead score calculation result',
}));

// Generate OpenAPI spec
const openApiSpec = registry.generateOpenApiSpec({
  openapi: '3.1.0',
  info: {
    title: 'DiagnoLeads API',
    version: '1.0.0',
  },
});

// Write to file
await Bun.write('openapi/generated/openapi.json', JSON.stringify(openApiSpec, null, 2));
```

#### Step 4: Implement tRPC Router

```typescript
// server/routers/leads.ts
import { z } from 'zod';
import { router, protectedProcedure } from '../trpc';
import {
  leadCreateSchema,
  leadScoreCalculateSchema,
  leadScoreResultSchema,
} from '@/lib/validation/leads';
import { leads, scoreHistory } from '@/lib/db/schema';
import { eq } from 'drizzle-orm';

export const leadsRouter = router({
  create: protectedProcedure
    .meta({ openapi: { method: 'POST', path: '/leads' } })
    .input(leadCreateSchema)
    .output(leadSelectSchema)
    .mutation(async ({ input, ctx }) => {
      // Multi-tenant check
      if (ctx.user.tenantId !== input.tenantId) {
        throw new TRPCError({ code: 'FORBIDDEN' });
      }

      // Calculate score
      const score = calculateScore(input.responses);

      // Insert lead
      const [lead] = await ctx.db.insert(leads).values({
        ...input,
        score,
        classification: classifyScore(score),
        tenantId: ctx.user.tenantId,
        createdBy: ctx.user.id,
      }).returning();

      return lead;
    }),

  calculateScore: protectedProcedure
    .meta({ openapi: { method: 'POST', path: '/leads/calculate-score' } })
    .input(leadScoreCalculateSchema)
    .output(leadScoreResultSchema)
    .mutation(async ({ input }) => {
      const breakdown = input.responses.map((r) => ({
        questionId: r.questionId,
        points: r.points,
        weight: input.weights?.[r.questionId] ?? 1,
      }));

      const totalPoints = breakdown.reduce((sum, b) => sum + (b.points * b.weight), 0);
      const maxPoints = breakdown.reduce((sum, b) => sum + (100 * b.weight), 0);
      const score = Math.round((totalPoints / maxPoints) * 100);

      return {
        score,
        classification: classifyScore(score),
        breakdown,
      };
    }),

  getScoreHistory: protectedProcedure
    .meta({ openapi: { method: 'GET', path: '/leads/{id}/score-history' } })
    .input(z.object({ leadId: z.string().uuid() }))
    .output(z.array(scoreHistorySelectSchema))
    .query(async ({ input, ctx }) => {
      // Multi-tenant check
      const lead = await ctx.db.query.leads.findFirst({
        where: eq(leads.id, input.leadId),
      });

      if (!lead || lead.tenantId !== ctx.user.tenantId) {
        throw new TRPCError({ code: 'NOT_FOUND' });
      }

      return ctx.db.query.scoreHistory.findMany({
        where: eq(scoreHistory.leadId, input.leadId),
        orderBy: (sh, { desc }) => [desc(sh.createdAt)],
      });
    }),
});

function calculateScore(responses: Array<{ points: number }>): number {
  const total = responses.reduce((sum, r) => sum + r.points, 0);
  const max = responses.length * 100;
  return Math.round((total / max) * 100);
}

function classifyScore(score: number): 'hot' | 'warm' | 'cold' {
  if (score >= 80) return 'hot';
  if (score >= 50) return 'warm';
  return 'cold';
}
```

#### Step 5: REST API Auto-Generated

```typescript
// app/api/trpc/[trpc]/route.ts
import { createOpenApiNextHandler } from 'trpc-openapi';
import { appRouter } from '@/server';

const handler = createOpenApiNextHandler({
  router: appRouter,
  createContext: () => ({}),
});

export { handler as GET, handler as POST };
```

**Auto-generated REST endpoints:**
- `POST /api/leads` → `leadsRouter.create`
- `POST /api/leads/calculate-score` → `leadsRouter.calculateScore`
- `GET /api/leads/{id}/score-history` → `leadsRouter.getScoreHistory`

#### Step 6: Generate TypeScript Types

```bash
bun run generate:types
```

```typescript
// lib/types/api.generated.ts (auto-generated)
export interface LeadCreate {
  name: string;
  email: string;
  company?: string;
  phone?: string;
  assessmentId: string;
  responses: Array<{
    questionId: string;
    optionId: string;
    points: number;
  }>;
}

export interface LeadScoreResult {
  score: number;
  classification: 'hot' | 'warm' | 'cold';
  breakdown: Array<{
    questionId: string;
    points: number;
    weight: number;
  }>;
}
```

#### Step 7: API Documentation

Scalar UI automatically displays:
- **Endpoint**: `POST /api/leads/calculate-score`
- **Request Body**: JSON schema from `leadScoreCalculateSchema`
- **Response**: JSON schema from `leadScoreResultSchema`
- **Try It Out**: Interactive form to test API

Access at: `https://app.diagnoleads.com/api/docs`

### Benefits of This Workflow

1. **Single Source of Truth**: Zod schemas define everything
2. **No Manual Sync**: OpenAPI and types auto-generated
3. **Type Safety**: End-to-end from DB → API → Client
4. **Contract Testing**: Validate API responses against OpenAPI
5. **Documentation**: Always up-to-date from schemas
6. **Internal + External APIs**: tRPC for internal, REST for external

---

## Migration Strategy

### Phased Migration Approach

#### Phase 1: Foundation (Month 1)
**Goal**: Set up new repository with core infrastructure

- ✅ Create `diagnoleads-v2` repository
- ✅ Initialize Next.js 15 project with Bun
- ✅ Set up Docker Compose development environment
- ✅ Configure Drizzle ORM + PostgreSQL
- ✅ Implement BetterAuth authentication
- ✅ Set up CI/CD with GitHub Actions
- ✅ Configure Biome + lefthook + commitlint
- ✅ Deploy initial Vercel project

**Deliverable**: Working Next.js app with auth, no business logic yet

#### Phase 2: Core Features (Month 2-3)
**Goal**: Migrate critical features

- ✅ Migrate database schema from SQLAlchemy to Drizzle
- ✅ Implement tRPC routers for core entities:
  - Tenants
  - Users
  - Assessments
  - Questions
  - Leads
- ✅ Build admin dashboard UI
- ✅ Implement multi-tenant row-level security
- ✅ Set up OpenSpec + OpenAPI workflow
- ✅ Write unit + integration tests (70% coverage)

**Deliverable**: Feature parity with current DiagnoLeads admin

#### Phase 3: AI Features (Month 4)
**Goal**: Migrate AI functionality to TypeScript

- ✅ Port assessment generation to Vercel AI SDK
- ✅ Port lead analysis to Vercel AI SDK
- ✅ Implement vector embeddings with pgvector
- ✅ Set up Trigger.dev for async jobs
- ✅ Migrate email templates to React Email + Resend

**Deliverable**: Full AI feature parity

#### Phase 4: Public Pages (Month 5)
**Goal**: Build SEO-optimized public pages

- ✅ Implement marketing landing page
- ✅ Build public assessment pages with SSR/SSG
- ✅ Create embed widget (Web Components)
- ✅ Optimize for Core Web Vitals
- ✅ Implement structured data for SEO

**Deliverable**: Production-ready public site

#### Phase 5: Integrations (Month 6)
**Goal**: Migrate external integrations

- ✅ Salesforce integration
- ✅ HubSpot integration
- ✅ Slack notifications
- ✅ Webhook system
- ✅ Public API endpoints

**Deliverable**: Full integration parity

#### Phase 6: Analytics & Polish (Month 7)
**Goal**: Add analytics and final touches

- ✅ Analytics dashboard with Tremor
- ✅ Real-time updates with Supabase Realtime
- ✅ Advanced filtering with TanStack Table
- ✅ Performance optimization
- ✅ E2E test coverage (Playwright)
- ✅ Documentation completion

**Deliverable**: Production-ready v2

#### Phase 7: Migration & Cutover (Month 8)
**Goal**: Migrate production data and switch

- ✅ Data migration scripts (SQL → SQL)
- ✅ Parallel run (v1 + v2)
- ✅ User acceptance testing
- ✅ Gradual cutover (feature flags)
- ✅ Decommission v1

**Deliverable**: Full migration complete

### Data Migration Strategy

```sql
-- Example migration script structure
-- scripts/migrate-data.sql

-- 1. Migrate tenants (no changes needed)
INSERT INTO diagnoleads_v2.tenants
SELECT * FROM diagnoleads_v1.tenants;

-- 2. Migrate users (map to BetterAuth schema)
INSERT INTO diagnoleads_v2.users (id, email, name, tenant_id, created_at)
SELECT id, email, full_name, tenant_id, created_at
FROM diagnoleads_v1.users;

-- 3. Migrate assessments
INSERT INTO diagnoleads_v2.assessments
SELECT * FROM diagnoleads_v1.assessments;

-- 4. Migrate questions (preserve relationships)
INSERT INTO diagnoleads_v2.questions
SELECT * FROM diagnoleads_v1.questions;

-- 5. Migrate leads (recalculate scores if needed)
INSERT INTO diagnoleads_v2.leads
SELECT
  id,
  tenant_id,
  name,
  email,
  company,
  score,
  CASE
    WHEN score >= 80 THEN 'hot'
    WHEN score >= 50 THEN 'warm'
    ELSE 'cold'
  END as classification,
  created_at
FROM diagnoleads_v1.leads;
```

### Risk Mitigation

1. **Parallel Run**: Keep v1 running during v2 development
2. **Feature Flags**: Gradual rollout of v2 features
3. **Data Sync**: Daily sync from v1 to v2 during migration
4. **Rollback Plan**: Keep v1 deployable for 3 months
5. **Monitoring**: Enhanced error tracking during cutover

---

## Cost Analysis

### Current Architecture (v1) Costs

| Service | Plan | Monthly Cost |
|---------|------|--------------|
| Vercel (Frontend) | Pro | $20 |
| Railway (FastAPI Backend) | Starter | $5-20 |
| Supabase (Database) | Pro | $25 |
| Upstash (Redis) | Free | $0 |
| Anthropic Claude API | Usage | $30-100 |
| Trigger.dev | Free | $0 |
| Resend | Free | $0 |
| Sentry | Free | $0 |
| **Total** | | **$80-165/month** |

### New Architecture (v2) Costs

| Service | Plan | Monthly Cost | Savings |
|---------|------|--------------|---------|
| Vercel (Full-Stack) | Pro | $20 | - |
| ~~Railway (Backend)~~ | ~~Eliminated~~ | $0 | **+$5-20** |
| Supabase (Database) | Pro | $25 | - |
| ~~Upstash (Redis)~~ | ~~Not needed~~ | $0 | **+$0** (was free) |
| ~~Prisma Accelerate~~ | ~~Not needed~~ | $0 | **+$29** (Drizzle instead) |
| Anthropic Claude API | Usage | $30-100 | - |
| Trigger.dev | Free | $0 | - |
| Resend | Free | $0 | - |
| Sentry | Free | $0 | - |
| **Total** | | **$75-145/month** | **$5-49/month savings** |

### Scalability Costs

#### At 100 Tenants

| Service | v1 Cost | v2 Cost | Savings |
|---------|---------|---------|---------|
| Compute | $50-80 | $20-40 | $30-40 |
| Database | $25 | $25 | $0 |
| Edge Functions | $10 | $0 (included) | $10 |
| AI API | $100-200 | $100-200 | $0 |
| **Total** | $185-315 | $145-265 | **$40-50** |

#### At 500 Tenants

| Service | v1 Cost | v2 Cost | Savings |
|---------|---------|---------|---------|
| Compute | $200-300 | $100-150 | $100-150 |
| Database | $100 | $100 | $0 |
| Edge Functions | $50 | $0 (included) | $50 |
| AI API | $500-800 | $500-800 | $0 |
| **Total** | $850-1250 | $700-1050 | **$150-200** |

### Development Cost Savings

- **Faster Development**: Bun 7x faster installs = **1-2 hours/week saved**
- **Less Debugging**: Type safety reduces bugs by ~30% = **3-5 hours/week saved**
- **Simpler Deployment**: Single app vs 2 apps = **2-3 hours/month saved**
- **Estimated Developer Time Savings**: **20-30 hours/month** ($2,000-3,000/month at $100/hour)

---

## Setup Instructions

### Prerequisites

1. **Install mise**:
   ```bash
   curl https://mise.run | sh
   echo 'eval "$(mise activate bash)"' >> ~/.bashrc
   source ~/.bashrc
   ```

2. **Install tools via mise**:
   ```bash
   cd diagnoleads-v2
   mise install
   # Installs: Bun 1.1.38, Node.js 20.11.0, lefthook 1.10.1
   ```

3. **Install Docker Desktop**:
   - Download from https://www.docker.com/products/docker-desktop

### Initial Setup

```bash
# 1. Clone repository
git clone https://github.com/your-org/diagnoleads-v2.git
cd diagnoleads-v2

# 2. Install dependencies
bun install

# 3. Copy environment variables
cp .env.example .env.local

# 4. Start development services
docker-compose up -d

# 5. Run database migrations
bun run db:migrate

# 6. Seed database (optional)
bun run db:seed

# 7. Install Git hooks
bun run prepare

# 8. Start development server
bun run dev
```

### Environment Variables

```bash
# .env.local

# Database (Supabase)
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/diagnoleads_dev"
DIRECT_URL="postgresql://postgres:postgres@localhost:5432/diagnoleads_dev"

# BetterAuth
BETTER_AUTH_SECRET="your-secret-key-here-generate-with-openssl"
BETTER_AUTH_URL="http://localhost:3000"

# Anthropic Claude
ANTHROPIC_API_KEY="sk-ant-xxx"

# Resend (Email)
RESEND_API_KEY="re_xxx"

# Trigger.dev
TRIGGER_API_KEY="tr_dev_xxx"
TRIGGER_API_URL="https://api.trigger.dev"

# Optional: Analytics
NEXT_PUBLIC_SENTRY_DSN="https://xxx@sentry.io/xxx"
AXIOM_TOKEN="xaat-xxx"

# Development
NODE_ENV="development"
NEXT_PUBLIC_APP_URL="http://localhost:3000"
```

### Verification

```bash
# Check all services running
docker-compose ps

# Should see:
# - diagnoleads-postgres (5432)
# - diagnoleads-pgadmin (5050)
# - diagnoleads-redis (6379)
# - diagnoleads-mailhog (8025)

# Access services:
# - App: http://localhost:3000
# - PgAdmin: http://localhost:5050 (admin@diagnoleads.local / admin)
# - Mailhog: http://localhost:8025

# Run tests
bun test                 # Unit tests
bun test:e2e             # E2E tests

# Check code quality
bun run check            # Biome lint + format
bun run typecheck        # TypeScript check
```

### Deployment

```bash
# 1. Connect to Vercel
bunx vercel link

# 2. Configure environment variables on Vercel
# (same as .env.local but with production values)

# 3. Deploy
bunx vercel --prod

# 4. Run database migrations on production
# (via Vercel dashboard or CLI)
```

---

## Summary

DiagnoLeads v2 represents a complete architectural modernization:

### Key Improvements

1. **Performance**: Bun + Turbopack = 7x faster development
2. **Cost Efficiency**: $5-49/month savings by eliminating FastAPI backend
3. **Type Safety**: End-to-end TypeScript with tRPC
4. **Developer Experience**: Spec-driven development with automatic API generation
5. **Scalability**: Edge-ready architecture with Vercel + Drizzle
6. **SEO Excellence**: Server Components for public pages
7. **Modern Stack**: Latest versions of all technologies (2025)

### Migration Timeline

- **Total Duration**: 8 months
- **MVP Ready**: Month 3
- **Feature Parity**: Month 6
- **Production Cutover**: Month 8

### Next Steps

1. ✅ Review this architecture document
2. ✅ Create `diagnoleads-v2` repository
3. ✅ Begin Phase 1: Foundation setup
4. ✅ Weekly architecture review meetings
5. ✅ Assign team members to migration tasks

---

**Document Status**: ✅ Ready for Implementation
**Approval Required**: Product Team, Engineering Team
**Questions**: Contact Architecture Team

---

**Last Updated**: 2025-11-23
**Version**: 1.0
**Authors**: Claude (AI Assistant), DiagnoLeads Team
