# Technology Stack

**Analysis Date:** 2026-03-19

## Languages

**Primary:**
- TypeScript 5.6.3 - Frontend (React) and backend (Express)
- Python 3.x - Trading bot

**Secondary:**
- JavaScript (JSX) - React components (minority)

## Runtime

**Environment:**
- Node.js 20.x (from `@types/node` 20.19.27)
- Python 3.x with dotenv

**Package Manager:**
- npm (via package.json)
- Lockfile: `package-lock.json` (present)

## Frameworks

**Frontend:**
- React 18.3.1 - UI library
- Vite 7.3.0 - Build tool and dev server
- Tailwind CSS 3.4.17 - Styling
- Wouter 3.3.5 - Routing (hash-based)

**Backend (API):**
- Express 5.0.1 - HTTP server
- TypeScript via tsx for development

**Python Bot:**
- FastAPI 0.110.0+ - Alternative API server
- Standard library threading for agent parallelism

**UI Components:**
- Radix UI primitives (multiple packages)
- Shadcn/ui components (copied into `client/src/components/ui/`)

**Build/Dev:**
- Vite 7.3.0 - Frontend bundler
- tsx 4.20.5 - TypeScript execution
- esbuild 0.25.0 - Underlying bundler

## Key Dependencies

**React Ecosystem:**
- `@tanstack/react-query` 5.60.5 - Server state management
- `react-hook-form` 7.55.0 - Form handling
- `@hookform/resolvers` 3.10.0 - Form validation resolvers
- `zod` 3.24.2 - Schema validation
- `framer-motion` 11.13.1 - Animations
- `recharts` 2.15.4 - Charts

**UI Primitives:**
- `@radix-ui/react-*` (20+ packages) - Unstyled component primitives
- `class-variance-authority` 0.7.1 - Component variants
- `clsx` 2.1.1 - Conditional classes
- `tailwind-merge` 2.6.0 - Tailwind class merging
- `lucide-react` 0.453.0 - Icons
- `react-icons` 5.4.0 - Additional icons

**Data Visualization:**
- `embla-carousel-react` 8.6.0 - Carousel
- `react-resizable-panels` 2.1.7 - Resizable layouts

**Trading (Python):**
- `web3` 6.0.0+ - Blockchain interaction
- `py-clob-client` 0.24.0+ - Polymarket CLOB API client
- `requests` 2.31.0+ - HTTP requests
- `python-dotenv` 1.0.0+ - Environment variables

**Database:**
- `drizzle-orm` 0.39.3 - SQL ORM
- `pg` 8.16.3 - PostgreSQL driver
- `connect-pg-simple` 10.0.0 - Session store

**Session/Auth:**
- `express-session` 1.18.1 - Session management
- `passport` 0.7.0 - Authentication
- `passport-local` 1.0.0 - Username/password strategy
- `memorystore` 1.6.7 - In-memory session store

**Real-time:**
- `ws` 8.18.0 - WebSocket support

**Dev Tools:**
- `drizzle-kit` 0.31.8 - Database migrations
- `typescript` 5.6.3 - Type checking
- `@vitejs/plugin-react` 4.7.0 - React plugin for Vite

## Configuration

**Environment:**
- `.env` file (not committed) with environment variables
- Template: `.env.example`
- Key configs: `PORT`, `DRY_RUN`, `STARTING_BALANCE`, Telegram tokens

**Build:**
- `tsconfig.json` - TypeScript configuration with path aliases
- `vite.config.ts` - Vite configuration with React plugin and path aliases
- `tailwind.config.ts` - Tailwind with dark mode and custom theme
- `postcss.config.js` - PostCSS with Tailwind

## Platform Requirements

**Development:**
- Node.js 20.x
- Python 3.x with pip
- npm for package management

**Production:**
- Node.js for API server (Express)
- Python 3.x for trading bot (separate process)
- PostgreSQL (via `pg` driver)

---

*Stack analysis: 2026-03-19*
