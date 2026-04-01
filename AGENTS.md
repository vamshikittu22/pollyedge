# Agent Instructions

## Build Commands

### Node.js / TypeScript
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Run production build
npm run check        # TypeScript type check (strict mode)
npm run db:push      # Push Drizzle schema to database
```

### Python
```bash
# Install dependencies
pip install -r requirements.txt

# Run bot
python -m bot.pollyedge_bot

# Run API server
python api/server.py

# Wallet setup
python setup/approve_wallet.py
```

## Code Style

### TypeScript
- **Strict mode required** - no `any` types
- Use `ESNext` modules with `.ts` extensions
- Imports: Use path aliases `@/*` for client, `@shared/*` for shared
- Naming: PascalCase for components/types, camelCase for functions/variables
- Database: Use Drizzle ORM with Zod schemas in `shared/schema.ts`
- Error handling: Use try/catch with specific error types
- No semicolons (follow existing patterns)

### Python
- **Type hints required** for all functions (e.g., `-> list[dict]`, `: str`)
- Snake_case for functions/variables, PascalCase for classes
- Use `datetime.now(timezone.utc)` for timestamps
- Logging: Use module-level loggers via `logging.getLogger(name)`
- Abstract base classes for agent patterns (see `bot/agents/base_agent.py`)
- Atomic file operations: temp file + rename pattern
- Error handling: Log errors with context, continue operation

## Project Structure

```
bot/           # Python trading agents
  agents/      # Individual strategy agents (inherit BaseAgent)
  *.py         # Core modules (signal_engine, risk_manager, etc.)
client/        # React frontend (Vite + TypeScript)
server/        # Express backend
shared/        # Drizzle schemas and shared types
api/           # FastAPI standalone server
setup/         # One-time setup scripts
```

## Database

- SQLite via Drizzle ORM
- All schema changes in `shared/schema.ts`
- Run `npm run db:push` after schema updates
- Tables: bot_state, open_positions, agent_status, pending_approvals, trades

## Key Patterns

1. **Agent Architecture**: All agents inherit from `BaseAgent`, implement `scan()` method
2. **Signal Format**: `{token_id, label, side, edge, source}`
3. **Risk Management**: All trades validated through risk_manager before execution
4. **Environment**: Copy `.env.example` to `.env`, never commit secrets
5. **Async Safety**: Use threading.Lock for file operations in Python
