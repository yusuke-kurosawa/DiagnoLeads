# Technology Stack - DiagnoLeads

**Version**: 1.0  
**Last Updated**: 2025-11-12  
**Status**: Published

---

## 📋 Overview

DiagnoLeads is built with a modern, cost-effective tech stack optimized for MVP/startup phase with scalability to enterprise. This document defines the technology choices and rationale.

**Design Philosophy**: 
- Low startup costs (free/cheap PaaS)
- Fast development (well-supported frameworks)
- Easy deployment (managed services)
- Scalable architecture (multi-tenant SaaS)

---

## 🏗️ Architecture Pattern

**Multi-Tenant SaaS with Shared Schema + RLS**

```
Frontend (React + Vite)
    ↓
API Gateway (FastAPI + Uvicorn)
    ↓
Application Layer (SQLAlchemy ORM)
    ↓
Database Layer (PostgreSQL + RLS)
    ↓
External Services (Anthropic Claude, Salesforce, etc.)
```

---

## 💻 Backend Stack

### Language & Framework

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| **Language** | Python | 3.11+ | Type hints, async/await, rich ecosystem |
| **Framework** | FastAPI | Latest | Async-first, automatic OpenAPI docs, fast |
| **ASGI Server** | Uvicorn | Latest | High-performance async server |
| **ORM** | SQLAlchemy | 2.0+ | Type-safe, powerful, multi-DB support |

### Key Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| `pydantic` | Latest | Request/response validation, settings |
| `alembic` | Latest | Database migrations |
| `python-jose` | Latest | JWT token creation/verification |
| `passlib` | Latest | Password hashing (bcrypt) |
| `python-multipart` | Latest | Form data parsing |
| `anthropic` | Latest | Claude API client |

### Database

| Component | Technology | Host | Tier |
|-----------|-----------|------|------|
| **DBMS** | PostgreSQL | Supabase | Free ($0-25/month) |
| **Connection Pool** | pgBouncer | Supabase | Included |
| **Backups** | Automated | Supabase | Daily |
| **Replication** | PITR | Supabase | 7 days free |

### Caching & Queues

| Component | Technology | Host | Tier |
|-----------|-----------|------|------|
| **Cache** | Redis | Upstash | Free ($0-10/month) |
| **Rate Limiting** | Redis + custom middleware | Upstash | Included |
| **Job Queue** | Trigger.dev | Trigger | Free for MVP |

### Environment

```bash
# Backend
backend/
  ├── app/
  │   ├── main.py                    # Application entry point
  │   ├── core/                      # Core utilities
  │   │   ├── config.py             # Settings management
  │   │   ├── security.py           # JWT, auth
  │   │   ├── middleware.py         # Request/response middleware
  │   │   └── deps.py               # Dependency injection
  │   ├── api/v1/                    # REST API endpoints
  │   ├── models/                    # SQLAlchemy models
  │   ├── schemas/                   # Pydantic schemas
  │   ├── services/                  # Business logic
  │   │   └── ai/                   # AI features
  │   └── integrations/              # External services
  ├── requirements.txt               # Production dependencies
  ├── requirements-dev.txt          # Development tools
  ├── Dockerfile                     # Container image
  └── tests/                         # Test suite
```

---

## 🎨 Frontend Stack

### Language & Framework

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| **Language** | TypeScript | 5.0+ | Type safety, autocomplete |
| **Framework** | React | 18+ | Component-based, large ecosystem |
| **Build Tool** | Vite | Latest | Lightning-fast dev server, build |
| **Routing** | React Router | 6+ | SPA routing, nested routes |

### State Management

| Library | Purpose | Use Case |
|---------|---------|----------|
| `zustand` | Global state | Auth, user data, settings |
| `@tanstack/react-query` | Server state | API responses, caching, sync |
| `react-hook-form` | Form state | Forms, validation |

### UI & Styling

| Library | Purpose |
|---------|---------|
| `tailwindcss` | Utility-first CSS framework |
| `shadcn/ui` | Headless component library |
| `recharts` | Data visualization (charts) |
| `date-fns` | Date formatting and manipulation |

### Development Tools

| Tool | Purpose |
|------|---------|
| `eslint` | Code linting |
| `prettier` | Code formatting |
| `vitest` | Unit testing |
| `@testing-library/react` | Component testing |

### Environment

```bash
# Frontend
frontend/
  ├── src/
  │   ├── pages/                    # Page components
  │   ├── features/                 # Feature modules
  │   ├── components/               # Reusable components
  │   ├── hooks/                    # Custom React hooks
  │   ├── services/                 # API clients
  │   ├── stores/                   # Zustand stores
  │   ├── types/                    # TypeScript types
  │   └── lib/                      # Utilities
  ├── public/                       # Static assets
  ├── vite.config.ts               # Vite configuration
  ├── tsconfig.json                # TypeScript configuration
  ├── tailwind.config.js           # Tailwind configuration
  └── package.json
```

---

## 📦 Embedded Widget Stack

### Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | TypeScript | Type safety |
| **Approach** | Web Components | Framework-agnostic |
| **Bundler** | Vite | Minimal bundle size |
| **Styling** | Shadow DOM | CSS encapsulation |

### Key Features

- Self-contained (`<diagnoleads-widget>`)
- No framework dependency
- CSS isolation via Shadow DOM
- Lazy loading support
- <50KB bundle size (gzip)

---

## 🚀 Deployment & Infrastructure

### Backend Deployment

| Service | Type | Free Tier | Cost |
|---------|------|-----------|------|
| **Railway** | Container hosting | 512MB RAM, 100GB transfer | $5-20/month |
| **Vercel (API routes)** | Serverless (alternative) | 100 requests/day | $0-20/month |
| **GitHub Actions** | CI/CD | 2000 free minutes/month | $0 |

### Frontend Deployment

| Service | Type | Cost |
|---------|------|------|
| **Vercel** | Static hosting + edge functions | $0-50/month |
| **Netlify** | Static hosting | $0-29/month |

### Production Environment

```bash
# Railway deployment
# Backend: FastAPI application
# Database: PostgreSQL (Supabase)
# Redis: Upstash (serverless)
# Domain: Custom domain ($12/year)
# SSL: Automatic (Let's Encrypt)
# Monitoring: Sentry (free tier)
```

### Environment Variables

```bash
# Backend
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=... (32+ char random string)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ANTHROPIC_API_KEY=sk-ant-...
SALESFORCE_CLIENT_ID=...
HUBSPOT_API_KEY=...
SLACK_WEBHOOK_URL=...

# Frontend
VITE_API_URL=https://api.example.com
VITE_ENVIRONMENT=production
```

---

## 🤖 AI Services

### Claude API

| Aspect | Details |
|--------|---------|
| **Provider** | Anthropic |
| **Model** | claude-3-5-sonnet-20241022 |
| **Primary Use** | Assessment generation, lead analysis |
| **Pricing** | Pay-as-you-go (~$0.003 per 1K input tokens) |
| **Monthly Cost** | $30-100 (estimated) |

### Integration

```python
from anthropic import Anthropic

client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4000,
    messages=[{"role": "user", "content": prompt}]
)
```

---

## 🔗 External Integrations

### CRM & Marketing

| Service | Purpose | Auth | Cost |
|---------|---------|------|------|
| **Salesforce** | CRM | OAuth 2.0 | $165/month+ |
| **HubSpot** | Inbound marketing | API Key | $50/month+ |
| **Slack** | Team notifications | Webhooks | Free |

### Utilities

| Service | Purpose | Integration |
|---------|---------|-------------|
| **SendGrid** | Email delivery | SMTP + API |
| **Twilio** | SMS (optional) | API |
| **Stripe** | Payments (future) | API |

---

## 📊 Cost Structure

### MVP Phase (~10 tenants)

```
Backend Hosting (Railway):        $5-10/month
Database (Supabase):              $0-10/month
Redis (Upstash):                  $0-5/month
Frontend (Vercel):                $0/month
Domain:                           $1/month
Claude API:                       $30-50/month
Monitoring (Sentry):              $0/month
─────────────────────────────────
TOTAL:                            $36-76/month
```

### Growth Phase (~50 tenants)

```
Backend Hosting:                  $15-30/month
Database:                         $25-50/month
Redis:                            $5-10/month
Frontend:                         $0-20/month
Claude API:                       $100-150/month
CRM Integrations:                 $50-200/month
─────────────────────────────────
TOTAL:                            $195-460/month
```

### Enterprise Phase (~200+ tenants)

Consider migration to:
- AWS ECS (container orchestration)
- AWS RDS (managed database)
- AWS ElastiCache (Redis)
- AWS CloudFront (CDN)
- Cost: $500-2000/month

---

## 🔒 Security Stack

| Layer | Technology | Details |
|-------|-----------|---------|
| **Transport** | TLS/SSL 1.3 | HTTPS everywhere |
| **Authentication** | JWT | 24h access + 7d refresh tokens |
| **Authorization** | RLS + Middleware | Row-Level Security in PostgreSQL |
| **Hashing** | bcrypt | Password hashing (10+ rounds) |
| **Rate Limiting** | Redis + Middleware | 5 failed attempts → 15min lockout |
| **Monitoring** | Sentry | Error tracking & alerting |

---

## 🧪 Testing Stack

### Backend

| Tool | Purpose |
|------|---------|
| `pytest` | Testing framework |
| `pytest-asyncio` | Async test support |
| `pytest-cov` | Coverage reporting |

### Frontend

| Tool | Purpose |
|------|---------|
| `vitest` | Unit testing |
| `@testing-library/react` | Component testing |
| `@testing-library/user-event` | User interaction testing |

### E2E Testing

| Tool | Purpose |
|------|---------|
| `playwright` | Cross-browser E2E testing |
| Or `cypress` | Alternative E2E testing |

---

## 📈 Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| First Contentful Paint (FCP) | <1.5s | TBD |
| Time to Interactive (TTI) | <3s | TBD |
| Lighthouse Score | >90 | TBD |
| API Response Time | <200ms (p95) | TBD |
| Database Query Time | <100ms (p95) | TBD |

---

## 🎯 Technology Selection Rationale

### Why FastAPI?

- ✅ Automatic OpenAPI documentation
- ✅ Built-in async/await support
- ✅ Type hints for request validation
- ✅ Fast (performance comparable to Node.js)
- ✅ Easy to learn for Python developers

### Why React + TypeScript?

- ✅ Large ecosystem & community
- ✅ Component-based architecture
- ✅ TypeScript for type safety
- ✅ Easy to hire developers
- ✅ Great tooling (Vite, React Router, etc.)

### Why PostgreSQL?

- ✅ ACID compliance
- ✅ Row-Level Security (RLS) native support
- ✅ JSONB for flexible data
- ✅ Full-text search capability
- ✅ Supabase hosted option

### Why Supabase + Upstash + Railway?

- ✅ Low cost for MVP
- ✅ Fully managed (no DevOps)
- ✅ Scalable to enterprise
- ✅ Easy to migrate later
- ✅ No vendor lock-in

---

## 🔄 Alternative Stacks (Not Selected)

### Backend Alternatives

| Option | Pros | Cons | Why Not |
|--------|------|------|---------|
| Django | Large ecosystem | Monolithic, slower | Overkill for API |
| Node.js + Express | JavaScript everywhere | Less type safety | Python better |
| Go | Fast, efficient | Steeper learning curve | Over-engineered |

### Frontend Alternatives

| Option | Pros | Cons | Why Not |
|--------|------|------|---------|
| Vue | Easier to learn | Smaller ecosystem | React more jobs |
| Next.js | SSR/SSG | Server-heavy | Not needed for SPA |
| Angular | Enterprise-grade | Complex, verbose | Overkill |

---

## 📚 Tech Stack Dependencies

```
DiagnoLeads
├── Backend (FastAPI + SQLAlchemy)
│   ├── Supabase (PostgreSQL + Auth)
│   ├── Upstash (Redis)
│   ├── Anthropic Claude (AI)
│   └── External APIs (Salesforce, HubSpot, Slack)
│
├── Frontend (React + Vite)
│   ├── TypeScript
│   ├── Tailwind CSS + shadcn/ui
│   └── React Query + Zustand
│
└── Infrastructure
    ├── Railway (Backend hosting)
    ├── Vercel (Frontend hosting)
    ├── GitHub Actions (CI/CD)
    └── Sentry (Error tracking)
```

---

## 🚀 Next Steps for Technology Decisions

1. ✅ **MVP Phase**: Current stack (FastAPI + React + Supabase)
2. 📅 **Growth Phase** (50+ users): Consider adding CDN, monitoring
3. 📅 **Enterprise Phase** (200+ users): Consider AWS migration

---

**Last Updated**: 2025-11-12  
**Maintained by**: Technical Lead & Architecture Team  
**Review Period**: Quarterly

---

## Related Specs

- [Architecture Overview](./architecture-overview.md)
- [API Design](../api/api-design.md)
- [Database Schema](../database/schema.md)
- [Deployment Guide](../deployment/production-deployment.md)
