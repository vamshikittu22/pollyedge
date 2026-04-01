[TESTING RULES]
→ Reproduce the failure before writing the fix — write test first
→ One assertion per test — name describes exact behavior being tested
→ Use AAA pattern: Arrange → Act → Assert, separated by blank lines
→ Never mock bot/db.py internals — mock the SQLite connection instead
→ Test file mirrors source: bot/logger.py → tests/test_logger.py
→ Python tests: pytest, fixtures for SQLite in-memory DB (not real data/pollyedge.db)
→ TypeScript tests: vitest (already in vite ecosystem)
→ Risk rules are high-priority tests: 3% cap, 10% daily loss cap, 3 positions, 8% edge
→ Always test DRYRUN=true behavior separately from live behavior
→ Test Telegram approval timeout: 120s auto-reject behavior
→ No test should modify data/pollyedge.db — use in-memory SQLite for all tests
