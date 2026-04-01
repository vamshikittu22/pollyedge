[FRONTEND RULES]
→ No raw fetch() in components — use TanStack Query (queryClient.ts)
→ Routing: Wouter only — never import from react-router-dom
→ Forms: react-hook-form + Zod resolver — validate on blur not submit
→ State: TanStack Query for server state — useState/useReducer for local only
→ Components in client/src/components/ui/ are Shadcn/Radix — never edit directly
→ Loading, empty, and error states required for every useQuery call
→ No any types — strict TypeScript, use shared/schema.ts types
→ Path alias: use @/ for client/src/ imports, shared/ for shared/
→ Icons: lucide-react primary, react-icons secondary — no inline SVG icons
→ Charts: recharts only — already installed, do not add chart.js or d3
→ Animation: framer-motion only — do not add additional animation libraries
→ No semicolons — follow existing file style
→ PascalCase for components and types, camelCase for functions and variables
