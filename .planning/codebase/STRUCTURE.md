# Codebase Structure

**Analysis Date:** 2026-03-19

## Directory Layout

```
pollyedge/
├── api/                   # Python FastAPI server (alternative API)
├── bot/                   # Python trading bot
│   ├── agents/            # Signal generation agents
│   ├── __init__.py
│   ├── approval_gate.py   # Telegram approval flow
│   ├── logger.py          # Trade logging utilities
│   ├── notifier.py        # Telegram notifications
│   ├── orchestrator.py    # Multi-agent coordination
│   ├── pollyedge_bot.py    # Bot entry point
│   ├── risk_manager.py    # Position sizing & risk rules
│   └── signal_engine.py    # Signal processing
├── client/                # React frontend
│   ├── src/               # Source code
│   │   ├── components/    # React components
│   │   │   └── ui/        # Radix UI primitives
│   │   ├── hooks/         # Custom React hooks
│   │   ├── lib/           # Utilities (queryClient, utils)
│   │   ├── pages/         # Page components
│   │   ├── App.tsx        # Root component
│   │   ├── main.tsx       # Entry point
│   │   └── index.css      # Global styles + Tailwind
│   ├── index.html
│   └── package.json
├── server/                # Node.js Express API server
│   ├── index.ts           # Server entry point
│   ├── routes.ts          # API route handlers
│   ├── storage.ts          # File-based state management
│   └── vite.ts            # Vite dev server setup
├── shared/                # Shared TypeScript code
│   └── schema.ts          # Zod schemas
├── setup/                 # Python setup scripts
├── script/                # Build scripts
├── logs/                  # Runtime logs (generated)
├── .env.example           # Environment template
├── package.json           # Node.js dependencies
├── requirements.txt       # Python dependencies
├── tsconfig.json          # TypeScript config
├── vite.config.ts         # Vite bundler config
├── tailwind.config.ts     # Tailwind CSS config
├── drizzle.config.ts      # Drizzle ORM config
└── postcss.config.js      # PostCSS config
```

## Directory Purposes

**`client/src/`:**
- Purpose: React dashboard frontend
- Contains: TSX components, hooks, pages, styles
- Key files: `App.tsx`, `pages/dashboard.tsx`

**`client/src/components/`:**
- Purpose: Dashboard UI components
- Contains: Feature components (`BalanceCard.tsx`, `TradesTable.tsx`) and UI primitives (`ui/`)
- Key files: `BalanceCard.tsx`, `BotStatusCard.tsx`, `PnLChart.tsx`, `AgentSwarmPanel.tsx`, `ApprovalQueue.tsx`

**`client/src/components/ui/`:**
- Purpose: Shadcn/ui component library
- Contains: 40+ Radix UI-based primitives

**`server/`:**
- Purpose: Express API server + Vite integration
- Contains: Route handlers, storage layer, static file serving
- Key files: `index.ts`, `routes.ts`, `storage.ts`

**`bot/`:**
- Purpose: Python trading bot
- Contains: Orchestrator, agents, risk management, approval flow
- Key files: `orchestrator.py`, `risk_manager.py`, `approval_gate.py`

**`bot/agents/`:**
- Purpose: Individual signal-generating agents
- Contains: `base_agent.py`, `earnings_agent.py`, `news_agent.py`, `momentum_agent.py`, `arb_agent.py`, `crypto_agent.py`

**`shared/`:**
- Purpose: TypeScript schemas shared between client and server
- Contains: Zod schemas with TypeScript type inference

**`api/`:**
- Purpose: Alternative Python FastAPI server
- Contains: `server.py` with FastAPI endpoints

## Key File Locations

**Entry Points:**
- `client/src/main.tsx` - React app entry
- `server/index.ts` - Express server entry
- `bot/pollyedge_bot.py` - Trading bot entry

**Configuration:**
- `.env.example` - Environment variables template
- `package.json` - Node dependencies and scripts
- `requirements.txt` - Python dependencies
- `tsconfig.json` - TypeScript configuration
- `vite.config.ts` - Vite bundler configuration
- `tailwind.config.ts` - Tailwind CSS theming

**Shared Code:**
- `shared/schema.ts` - Zod schemas and TypeScript types

**Core Logic:**
- `server/routes.ts` - API route handlers
- `server/storage.ts` - State management
- `bot/orchestrator.py` - Agent coordination
- `bot/risk_manager.py` - Risk controls

## Naming Conventions

**Files:**
- React components: PascalCase (`Dashboard.tsx`, `BalanceCard.tsx`)
- UI components: PascalCase (`Button.tsx`, `Card.tsx`)
- TypeScript modules: camelCase (`queryClient.ts`, `utils.ts`)
- Python modules: snake_case (`risk_manager.py`, `approval_gate.py`)
- Python classes: PascalCase (`RiskManager`, `BaseAgent`)

**Directories:**
- All directories: kebab-case or snake_case
- `client/src/components/ui/` - UI primitives in subdirectory
- `bot/agents/` - Agent modules in subdirectory

## Where to Add New Code

**New Dashboard Component:**
- Implementation: `client/src/components/NewComponent.tsx`
- Tests: Not detected (no test directory structure)
- Style: Use Tailwind CSS classes, import UI primitives from `@/components/ui/`

**New API Endpoint:**
- Implementation: `server/routes.ts` (add new `app.METHOD` handler)
- Reads/Writes: State via `storage.ts` methods

**New Trading Agent:**
- Implementation: `bot/agents/new_agent.py` (extend `BaseAgent`)
- Register: Add to agents list in `bot/orchestrator.py`

**New Python Utility:**
- Implementation: `bot/utils.py` or appropriate module
- Import pattern: `from bot.utils import ...`

**Shared Type Definition:**
- Implementation: `shared/schema.ts`
- Pattern: Add Zod schema and export TypeScript type

**New Frontend Hook:**
- Implementation: `client/src/hooks/useNewHook.ts`
- Pattern: Follow existing hooks pattern (`use-mobile.tsx`, `use-toast.ts`)

## Special Directories

**`client/src/components/ui/`:**
- Purpose: Shadcn/ui component primitives
- Generated: Components are copied from shadcn/ui
- Committed: Yes

**`logs/`:**
- Purpose: Runtime logs from Python bot
- Generated: Created at runtime by `pollyedge_bot.py`
- Committed: No (in `.gitignore`)

**`node_modules/`:**
- Purpose: Node.js dependencies
- Generated: By npm install
- Committed: No

---

*Structure analysis: 2026-03-19*
