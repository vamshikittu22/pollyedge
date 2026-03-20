# Stack Research

**Domain:** Trading research + human-in-the-loop approval workflow
**Researched:** 2026-03-19
**Confidence:** MEDIUM-HIGH

> Rationale: FastAPI/Pydantic/Next.js ecosystem is verified via current docs and multiple 2026 sources. Polymarket-specific libraries (py-clob-client) verified via pm.wiki and agentbets.ai (March 2026). PostgreSQL, Redis, Docker patterns are standard and verified. uv is verified via Astral docs. TanStack Query/Recharts are verified via multiple 2026 sources. Some library minor versions have LOW confidence (pinned to ~major.minor in practice is the right call).

## Recommended Stack

### Core Backend

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **FastAPI** | ~0.115 | Async REST API + WebSocket | De facto standard for Python APIs in 2026. Auto OpenAPI docs, native Pydantic V2 integration, first-class async. Powers production trading bots at scale. Multiple 2026 articles confirm it as the standard over Flask. [Source: FastAPI release notes, auth0.com/blog/fastapi-best-practices, dev.to/apaksh/building-production-ready-apis-with-fastapi-in-2026] |
| **Pydantic V2** | ~2.10 | Data validation and settings | Rust-powered core, 5-50x faster than v1. Native to FastAPI. Annotated types enable reusable field constraints. SecretStr for API keys. model_validate_json for performance. [Source: devtoolbox.dedyn.io, FastAPI official migration guide, towardsdatascience.com] |
| **SQLAlchemy 2.0** | ~2.0 | Async ORM | Native async support. async_sessionmaker, AsyncSession, create_async_engine. Replaces sync patterns entirely. Production standard for FastAPI + PostgreSQL. [Source: oneuptime.com/blog/post/2026-01-27-sqlalchemy-fastapi] |
| **asyncpg** | ~0.30 | Async PostgreSQL driver | Required for async SQLAlchemy 2.0 with PostgreSQL. Sub-millisecond connection pooling. [Source: oneuptime.com/blog/post/2026-02-02-fastapi-async-database] |
| **uv** | latest | Python package and environment manager | 10-100x faster than pip. Single binary. Replaces pip, pip-tools, virtualenv, Poetry. Native pyproject.toml and lockfile. Astral (Ruff) backed. [Source: astral.sh/docs/uv, medium.com/@gayathrisaranathan/uv-should-be-preferred-2026] |
| **Uvicorn** | ~0.30 | ASGI server | Standard ASGI server for FastAPI. --workers N for multiprocess. UvicornWorker for Gunicorn. [Source: FastAPI production guide] |

**Confidence: HIGH** for FastAPI + Pydantic + SQLAlchemy + asyncpg (verified via multiple 2026 sources and official docs). **MEDIUM** for uv (newer entrant, momentum is strong, official Astral docs confirm compatibility).

### Database

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **SQLite** | (built-in) | Dev database | Zero config. File-based. Fine for single-instance bot + dashboard. Swap to PostgreSQL when scaling. [Source: fastapi.tiangolo.com/tutorial/sql-databases] |
| **PostgreSQL** | ~17 | Production database | Robust, async-capable, excellent with asyncpg. TimescaleDB extension available for time-series if needed later. |
| **Alembic** | ~1.15 | DB migrations | Standard for SQLAlchemy migrations. Keeps schema in version control. |

**Confidence: HIGH** for PostgreSQL (industry standard). **MEDIUM** for Alembic (standard but has rough edges with async SQLAlchemy 2.0 -- verify latest docs).

### Scheduling and Background Tasks

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **APScheduler** | ~3.10 | In-process scheduler | No broker required. BackgroundScheduler runs inside the FastAPI process or a sidecar. Sufficient for periodic market scans (every 1-5 min). Simpler than Celery or Temporal. [Source: calmops.com/programming/python/task-scheduling-apscheduler-celery] |
| **Celery + Redis** | ~5.4 / ~7 | Distributed task queue | Only needed if scaling to multiple workers or needing distributed retry semantics. Overkill for MVP. [Source: calmops.com, alibabacloud.com/product-insights/celery-beat-explained] |
| **Temporal** | ~1.35 | Durable execution | Excellent for complex multi-step workflows (scan, research, score, wait-for-approval, execute). But adds operational complexity (Temporal server, UI). Defer until workflow logic is proven. [Source: temporal.io/blog/how-to-convert-your-job-scheduling-system-to-temporal-schedules, dasroot.net/posts/2026/02/orchestrating-ai-tasks-celery-temporal] |

**Confidence: HIGH** for APScheduler (simple, verified). **MEDIUM** for Temporal (powerful but over-engineering for Phase 1).

### Caching and Real-time

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Redis** | ~7 | Caching + pub/sub | Sub-millisecond reads. Cache market data, signals. Pub/sub for WebSocket broadcast. redis.asyncio for async FastAPI. [Source: oneuptime.com/blog/post/2026-01-21-redis-fastapi-integration] |
| **redis-py** | ~5.2 | Python Redis client | Native async via redis.asyncio. Connection pooling built-in. |

**Confidence: HIGH** for Redis (industry standard, verified via multiple 2026 sources).

### Data Sources (Polymarket + Crypto + Stocks)

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **py-clob-client** | latest | Polymarket CLOB API | Official Python SDK. Handles auth (EIP-712 signed messages), order placement, order book, positions. Well-documented in 2026 guides. [Source: agentbets.ai/guides/polymarket-api-guide, pm.wiki/learn/polymarket-api (March 2026)] |
| **ccxt** | ~4.0 | Multi-exchange crypto API | Unified interface across Binance, Kraken, Coinbase, etc. Handles rate limiting, authentication, order book normalization. Standard for crypto bots. [Source: Multiple trading bot articles 2026] |
| **yfinance** | ~0.2 | Stock/crypto price data | Free. No API key needed for basic use. Covers Yahoo Finance data. Good for initial stock/crypto signals. [Source: dev.to/kotaro987/building-a-trading-bot-in-python-from-idea-to-live, github.com/HassanJawadKhan/Smart-Trading-Bot] |
| **Tavily AI** or **DuckDuckGo** | -- | News signal research | Tavily: AI-optimized search API. DuckDuckGo: free, no API key. Used by trading agent articles for event-driven signals. [Source: medium.com/@xppert9/how-to-build-an-autonomous-trading-agent-with-python-in-2026] |

**Confidence: MEDIUM-HIGH** for py-clob-client and ccxt (well-documented 2026). **MEDIUM** for yfinance (reliable but unofficial/frequent API changes). **LOW** for news APIs (Tavily has API costs, DuckDuckGo reliability varies).

### Frontend Dashboard

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Next.js** | 15 or 16 | React framework | App Router, Server Components, API routes. SSR for initial dashboard load. [Source: adminlte.io/blog/nextjs-admin-dashboards-shadcn, 2026] |
| **TypeScript** | ~5.8 | Type safety | Required. Catches errors at build time. Matches Python backend type intent. |
| **shadcn/ui** | latest | UI component library | Copy-paste components (not npm dependency). Built on Radix primitives + Tailwind. Full code ownership. Accessible by default. Dominant 2026 pattern for dashboards. [Source: dev.to/codedthemes/shadcnui-cheat-sheet-2026, differ.blog/p/30-best-shadcn-components-for-2026] |
| **Tailwind CSS** | ~4.0 | CSS framework | v4 uses @theme directive, CSS-first config (no tailwind.config.js). Oxide engine. Compatible with shadcn/ui. [Source: medium.com/@shahzaibnawaz/next-js-16-roadmap-day-4-30] |
| **TanStack Query** | ~5.83 | Server state management | Handles polling, caching, deduping, background refetch. Critical for real-time dashboard updates. Replaces Redux for server data. [Source: dev.to/krish_kakadiya_5f0eaf6342/react-server-components-tanstack-query-2026, codewithseb.com/blog/tanstack-ecosystem-complete-guide-2026] |
| **Recharts** | ~3.0 | Charts | Popular React charting library. Composable, declarative. Good for analytics dashboards. For candlestick/trading charts consider TradingView Lightweight Charts alongside. [Source: recharts.org] |
| **TanStack Table** | ~8 | Headless table | Build any table UI (sortable, filterable, paginated). Headless -- no styles imposed. Works great with shadcn/ui Table. [Source: tanstack.com/table] |
| **Framer Motion** | ~11 | Animations | Standard for React animations in 2026. AnimatePresence for page transitions, motion.div for micro-interactions. Works with shadcn/ui. |

**Confidence: HIGH** for Next.js, TypeScript, shadcn/ui, TanStack Query (widely validated 2026). **MEDIUM-HIGH** for Tailwind v4 (newer, momentum is strong). **MEDIUM** for Recharts (most popular but can lag on financial chart features -- consider lightweight-charts for candlesticks).

### Infrastructure and DevOps

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Docker** | latest | Containerization | Package FastAPI backend + Next.js dashboard into containers. docker-compose for local dev. [Source: dev.to/propfirmkey/docker-containerization-for-trading-bots-best-practices-1gd6] |
| **pytest** | ~8 | Python testing | Standard. pytest-asyncio for async tests. httpx.AsyncClient for FastAPI test client. |
| **Ruff** | latest | Python linting + formatting | 100-1000x faster than flake8/isort/black. Single tool replaces all four. From Astral (uv team). |

**Confidence: HIGH** for Docker (standard containerization). **HIGH** for pytest. **HIGH** for Ruff (Astral toolchain, replacing black/isort/flake8).

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **pydantic-settings** | ~2.7 | Typed settings from env | Preferred over raw os.getenv. Integrates with Pydantic BaseModel. |
| **structlog** | latest | Structured logging | JSON logs. Required for production monitoring. Better than stdlib logging. |
| **httpx** | ~0.28 | HTTP client | For calling external APIs (news, data feeds). Async. Drop-in for requests replacement. |
| **python-jose** | latest | JWT handling | If adding auth to dashboard. |
| **passlib + bcrypt** | latest | Password hashing | If dashboard has user accounts. |
| **ta** | latest | Technical analysis | 50+ technical indicators. Pandas-based. Alternative to TA-Lib (no C compilation needed). |
| **numpy / pandas** | latest | Data manipulation | For signal computation, historical analysis. |
| **tenacity** | latest | Retry logic | Decorator-based retry with exponential backoff. For resilient API calls. |
| **python-dotenv** | latest | Env variable loading | For .env files in dev. Use pydantic-settings in production. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| **Ruff** | Linting + formatting + import sorting | ruff check . and ruff format . Replaces black, isort, flake8. |
| **uv** | Package + environment management | uv sync, uv run, uv add. Faster than npm/pip. Single binary. |
| **Next.js ESLint** | JS/TS linting | Included via create-next-app. Add eslint-config-next. |
| **Turso** or **Litestream** | SQLite replication (optional) | If sticking with SQLite but wanting replication. Not needed for MVP. |

## Human-in-the-Loop Approval Pattern

The core workflow pattern for the approval queue:

    Bot scan cycle -> Write pending_opportunities to DB -> Dashboard polls GET /opportunities?status=pending
        -> Human POST /opportunities/{id}/approve or /reject
        -> Bot picks up approved on next scan cycle -> Executes trade

**Database-backed queue** is the right choice for MVP:
- Simple to reason about
- No additional infrastructure (unlike Kafka, Temporal)
- Dashboard can poll or use SSE/WebSocket for live updates
- Full audit trail in one place
- Easy to add fields (conviction_score, rejection_reason, notes)

**When to upgrade:** If the workflow becomes complex (multi-step approvals, escalation paths, conditional execution), consider Temporal or a dedicated workflow engine. But for bot vets, human approves, bot executes -- database is sufficient.

**Confidence: HIGH** for database-backed queue pattern (widely validated in 2026 HiTL articles and production trading systems).

## Installation

```bash
# Backend (uv)
uv init --app --name pollyedge-backend
cd pollyedge-backend
uv add fastapi pydantic pydantic-settings sqlalchemy asyncpg alembic
uv add redis apscheduler httpx python-dotenv structlog
uv add py-clob-client ccxt yfinance ta tenacity
uv add pytest pytest-asyncio httpx ruff

# Frontend (Next.js)
npx create-next-app@latest pollyedge-dashboard --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
cd pollyedge-dashboard
npx shadcn@latest init
npx shadcn@latest add button card table badge
npm install @tanstack/react-query @tanstack/react-table recharts framer-motion zod
npm install -D @types/node @types/react @types/react-dom typescript
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| FastAPI | Flask | Flask is sync-only by default. FastAPI has native Pydantic V2, auto docs, async first. Flask is legacy for new projects in 2026. |
| FastAPI | Django Ninja | Ninja is solid but smaller ecosystem. FastAPI dominates 2026 trading bot space. |
| FastAPI | Starlette | FastAPI builds on Starlette and adds Pydantic, docs, validation. |
| SQLAlchemy 2.0 | SQLModel | SQLModel is great for simple cases, but SQLAlchemy 2.0 gives more control for complex trading schemas. |
| PostgreSQL | MySQL | PostgreSQL has better JSON support, array types. Better for time-series if needed later. |
| PostgreSQL | MongoDB | MongoDB lacks ACID guarantees needed for trade audit trails. PostgreSQL + JSONB is the right hybrid. |
| APScheduler | Celery + Redis | Celery requires Redis/RabbitMQ, more ops overhead. APScheduler is sufficient for single-instance periodic scans. |
| APScheduler | Temporal | Temporal is excellent for durable execution. Overkill for Phase 1. |
| Next.js | React + Vite | Next.js gives SSR, API routes, routing out of the box. |
| shadcn/ui | MUI | MUI ships pre-styled opaque components. shadcn/ui gives code ownership and Tailwind consistency. shadcn/ui is the 2026 preferred pattern. |
| shadcn/ui | Ant Design | Ant Design is heavy and jQuery-era design language. |
| Recharts | Lightweight Charts | TradingView Lightweight Charts is excellent for candlestick/price charts. Recharts is better for analytics. Use both. |
| TanStack Query | SWR | TanStack Query has better ecosystem and maintenance as of 2026. |
| uv | Poetry | uv is 10-100x faster and from the active Astral team. Poetry is stable but slower. |
| uv | pip + requirements.txt | No lockfile, slow installs. uv is the 2026 standard for new projects. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **Pydantic V1** | End-of-life. No Python 3.14 support. Migration path from v1 is well-documented. | Pydantic V2 (~2.10) |
| **SQLAlchemy 1.x sync patterns** | 2.0 has complete async rewrite. Mixing sync/async creates hard-to-debug deadlocks. | SQLAlchemy 2.0 async |
| **TA-Lib** | Requires C compilation. Proprietary license. | ta library (pure Python, no compilation) |
| **Celery Beat as primary scheduler** | Requires Redis or RabbitMQ. Operational complexity for MVP. | APScheduler (in-process, no broker) |
| **MongoDB for trade data** | No ACID transactions. Trade records need atomicity. | PostgreSQL |
| **WebSocket-only dashboard** | WebSockets add complexity. REST polling with TanStack Query is simpler and sufficient for 1-5 min scan cycles. | REST polling + optional SSE for push |
| **Django** | Heavy ORM, sync-first, opinionated structure. Overkill for a trading research API. | FastAPI |
| **Flask-RESTX or Flask** | Sync. Requires asyncpg wrappers, manual docs. FastAPI is the clear winner for 2026. | FastAPI |
| **JavaScript** | No type safety across frontend/backend boundary. | TypeScript |
| **CSS-in-JS (styled-components, emotion)** | Runtime overhead. Conflicts with Tailwind. | Tailwind CSS v4 |
| **Redux for server state** | Redux is for client state. TanStack Query is purpose-built for server state. | TanStack Query |
| **pip** | Slow. No lockfile. No environment management. | uv |
| **requirements.txt** | No dependency resolution. Drift causes works on my machine. | uv + uv.lock |
| **Polymarket unofficial scraping** | Breaks TOS. Unreliable. API is official and well-documented. | py-clob-client (official SDK) |
| **NewsAPI free tier** | Heavy rate limits. Not suitable for automated polling. | Tavily (AI search) or DuckDuckGo |

## Stack Patterns by Variant

**If Polymarket-only (Phase 1 MVP):**
- py-clob-client for all market data and execution
- Skip ccxt and yfinance
- Reduces complexity significantly

**If adding crypto (Phase 2):**
- Add ccxt for Binance/Kraken
- Unified signal schema across Polymarket + exchanges
- Keep Polymarket as the conviction filter since it aggregates event outcomes

**If adding stocks (Phase 3):**
- Add yfinance for price/financial data
- Consider a premium data source (Polygon.io, Alpaca) for reliable stock data
- yfinance is unreliable for production stock trading

**If scaling to multiple users:**
- Add PostgreSQL (from SQLite)
- Add Celery + Redis for distributed task queue
- Consider Temporal for approval workflow durability
- Add authentication (NextAuth.js or Clerk)

## Version Compatibility

| Package | Notes |
|---------|-------|
| FastAPI ~0.115 | Requires Pydantic V2. Dropped Pydantic V1 support as of 0.126. Use bump-pydantic tool to migrate. |
| Pydantic V2 ~2.10 | Compatible with Python 3.9+. Use Annotated[int, Field(gt=0)] pattern for reusable constraints. |
| SQLAlchemy 2.0.x | asyncpg driver for PostgreSQL. aiosqlite for SQLite. Never mix sync and async sessions. |
| Next.js 15 / 16 | React 18+ required. App Router. Server Components for initial data load. |
| React 18+ | Required for Server Components support. |
| Tailwind CSS ~4.0 | CSS-first config (@theme in CSS). Not compatible with tailwind.config.js v3 patterns. Read Tailwind v4 migration guide. |
| shadcn/ui | Works with both Tailwind v3 and v4. Components are copy-pasted, not npm-installed. |
| TanStack Query ~5.x | v5 has breaking changes from v4. Ensure tutorials/docs match v5 API. |
| Python 3.10+ | FastAPI and SQLAlchemy 2.0 require 3.10+. Use 3.12 for production. |

## Sources

- [FastAPI Official Docs](https://fastapi.tiangolo.com/) -- Current version, Pydantic V2 migration, production patterns
- [FastAPI Release Notes](https://fastapi.tiangolo.com/release-notes/) -- Version history, Pydantic compatibility
- [pm.wiki Polymarket API Guide (March 2026)](https://pm.wiki/learn/polymarket-api) -- CLOB, Gamma, Data API
- [agentbets.ai Polymarket Bot Quickstart (2026)](https://agentbets.ai/guides/polymarket-bot-quickstart/) -- py_clob_client SDK, architecture patterns
- [Auth0 FastAPI Best Practices](https://auth0.com/blog/fastapi-best-practices/) -- Production patterns
- [Dev.to: Production FastAPI APIs 2026](https://dev.to/apaksh/building-production-ready-apis-with-fastapi-in-2026-the-complete-playbook-5hlb) -- Project structure, testing, deployment
- [OneUptime: SQLAlchemy 2.0 + FastAPI Async](https://oneuptime.com/blog/post/2026-01-27-sqlalchemy-fastapi) -- Async patterns
- [Dev.to: shadcn/ui Cheat Sheet 2026](https://dev.to/codedthemes/shadcnui-cheat-sheet-2026) -- Component patterns
- [TanStack Ecosystem 2026 Guide](https://codewithseb.com/blog/tanstack-ecosystem-complete-guide-2026) -- Query, Table, Router
- [Astral uv + FastAPI Docs](https://docs.astral.sh/uv/guides/integration/fastapi/) -- uv project setup
- [Dev.to: Docker Trading Bot Best Practices 2026](https://dev.to/propfirmkey/docker-containerization-for-trading-bots-best-practices-1gd6) -- Containerization
- [medium.com: Autonomous Trading Agent Polymarket 2026](https://medium.com/@xppert9/how-to-build-an-autonomous-trading-agent-with-python-in-2026-0b8e97ba4546) -- Architecture, AI integration
- [Dev.to: Trading Bot Architecture Deep Dive 2026](https://dev.to/eqhoids/how-i-built-a-crypto-trading-bot-architecture-deep-dive-1405) -- Binance WebSocket, indicators
- [Paper-Trader-Bot-with-Alpaca (GitHub)](https://github.com/FelipeGarciaCosta/Paper-Trader-Bot-with-Alpaca) -- FastAPI + React + TypeScript stack reference
- [Dev.to: Human-in-the-Loop React](https://dev.to/rifzankhan/stop-your-ai-agents-from-doing-stupid-things-i-open-sourced-a-react-ui-for-human-in-the-loop-5eek) -- HITL approval card patterns
- [StackAI: Human-in-the-Loop Design](https://www.stack-ai.com/insights/human-in-the-loop-ai-agents-how-to-design-approval-workflows-for-safe-and-scalable-automation) -- HITL workflow patterns

---
*Stack research for: High-conviction trading command center (Pollyedge)*
*Researched: 2026-03-19*
