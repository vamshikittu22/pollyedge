[API RULES]
→ Express routes: consistent response shape { success, data, error }
→ FastAPI routes: pydantic models for request/response validation
→ All routes must have input validation before any business logic
→ HTTP status codes: 200 OK, 201 Created, 400 Bad input, 401 Unauth, 500 Server error
→ Never expose raw SQLite errors or Python tracebacks in API responses
→ All list endpoints must be paginated: { data[], total, page, limit }
→ Bot state reads: server/storage.ts reads from SQLite — never from JSON files directly
→ Python API (api/server.py): load_dotenv at top before any os.getenv usage
→ Express server: TypeScript strict mode, no any types
→ Session auth via Passport.js — never roll custom auth logic
→ Rate limit public endpoints — bot-facing endpoints are internal only
