# Coding Conventions

**Analysis Date:** 2026-03-19

## Naming Patterns

**Files:**
- React/TypeScript: PascalCase for components (`Dashboard.tsx`), camelCase for utilities (`queryClient.ts`)
- Python: snake_case for modules (`risk_manager.py`), PascalCase for classes (`RiskManager`)
- Config files: kebab-case or snake_case

**Functions:**
- TypeScript: camelCase (`getBotState`, `updateConfig`)
- Python: snake_case (`get_live_balance`, `record_trade_open`)

**Variables:**
- TypeScript: camelCase (`currentBalance`, `pendingApprovals`)
- Python: snake_case (`current_balance`, `pending_approvals`)
- Constants: SCREAMING_SNAKE_CASE in Python, camelCase in TypeScript

**Types:**
- TypeScript interfaces/schemas: PascalCase (`BotStatus`, `Trade`)
- Zod schemas: camelCase variable (`botStatusSchema`)

## Code Style

**Formatting:**
- Tool: Prettier (implicit via Tailwind, but not explicitly configured)
- Key settings: Not detected (no `.prettierrc` file)

**Linting:**
- Tool: ESLint (implied by package structure)
- Key rules: Not explicitly configured

**TypeScript:**
- Strict mode enabled in `tsconfig.json`
- No explicit ESLint config file detected

## Import Organization

**Order (TypeScript):**
1. React/core imports (`react`, `react-dom`)
2. Third-party libraries (`@tanstack/react-query`, `wouter`)
3. UI component imports (`@/components/ui/*`)
4. Local component imports (`@/components/*`)
5. Shared imports (`@shared/*`)
6. Utility imports (`@/lib/*`)

**Example from `client/src/pages/dashboard.tsx`:**
```typescript
import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import type { BotStatus } from "@shared/schema";
import { BalanceCard } from "@/components/BalanceCard";
// ...
```

**Path Aliases:**
- `@/*` → `./client/src/*`
- `@shared/*` → `./shared/*`
- `@assets/*` → `./attached_assets`

**Python imports:**
```python
# Standard library
import os, sys, logging, signal
from datetime import datetime

# Third-party
from dotenv import load_dotenv
import requests

# Local
from bot.agents.base_agent import BaseAgent
from bot.risk_manager import RiskManager
```

## Error Handling

**Patterns:**

**TypeScript/Express:**
```typescript
// Route error handling
app.use((err: any, _req: Request, res: Response, next: NextFunction) => {
  const status = err.status || err.statusCode || 500;
  const message = err.message || "Internal Server Error";
  return res.status(status).json({ message });
});

// Try-catch with fallbacks
try {
  if (fs.existsSync(FILE)) {
    const raw = fs.readFileSync(FILE, "utf-8");
    return JSON.parse(raw);
  }
} catch {
  return defaultValue;
}
```

**Python:**
```python
# Try-except with pass (silent fail)
try:
    # operation
except Exception:
    pass

# Fail-safe returns
except Exception as e:
    log.error(f"Error: {e}")
    return False  # or return None, empty list, etc.
```

## Logging

**Framework:** Console logging

**Python:**
```python
import logging

log = logging.getLogger("ModuleName")
log.info(f"Starting with {count} items")
log.error(f"Failed: {e}")
```

**TypeScript:**
```typescript
// Simple console
console.log(`${formattedTime} [${source}] ${message}`);
```

## Comments

**When to Comment:**
- Module docstrings at top of files
- Class docstrings explaining purpose
- Inline comments for non-obvious logic (e.g., "// Bug 3 fix:")

**JSDoc/TSDoc:**
- Not heavily used
- TypeScript types via inference from Zod schemas

**Python Docstrings:**
- Used in `bot/` modules
- Format: Triple-quoted strings with descriptions
```python
def request_approval(self, signal: dict, size: float) -> bool:
    """
    Send trade proposal to Telegram with inline APPROVE/REJECT buttons.
    Block until user responds or timeout.
    Returns True if approved, False if rejected/timeout.
    """
```

## Function Design

**Size:** Functions kept reasonably small with single responsibility

**Parameters:**
- TypeScript: Typed parameters, destructuring for options
- Python: Type hints used, default values common

**Return Values:**
- TypeScript: Explicit return types preferred
- Python: Type hints for methods, None as default empty return

## Module Design

**Exports:**
- TypeScript: Named exports preferred
```typescript
export function registerRoutes(...) { ... }
export const storage = new MemStorage();
```

- Python: Direct class/function definition (no `__all__` detected)

**Barrel Files:**
- Not used (components imported directly from source)

---

*Convention analysis: 2026-03-19*
