---
phase: 03-research-engine-polish
plan: 02
subsystem: bot-core
tags: scoring, conviction, algorithm

# Dependency graph
requires:
  - phase: 03-01-PLAN.md
    provides: signal dictionary structure with edge, source, volume fields
provides:
  - Multi-factor conviction scoring 0-100
  - analysis_breakdown field support in scoring
affects: [signal evaluation, approval workflow]

# Tech tracking
tech-stack:
  added: []
  patterns: Multi-factor weighted scoring (edge + source + confluence + volume + analysis_breakdown)

key-files:
  created: []
  modified:
    - bot/orchestrator.py

key-decisions:
  - "Used min() cap on confluence score to prevent runaway scores"
  - "Added analysis_breakdown +5 as explicit signal of structured analysis"

patterns-established:
  - "Multi-factor scoring: edge(0-40) + source(0-25) + confluence(0-15) + analysis_breakdown(+5) + volume(0-20) = 100 max"

# Metrics
duration: ~1min
completed: 2026-04-16
---

# Phase 3 Plan 2: Multi-Factor Conviction Scoring Summary

**Enhanced conviction scoring algorithm with multi-factor weights (edge, source, confluence, analysis_breakdown, volume)**

## Performance

- **Duration:** ~1 min
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- _score_signal now uses multi-factor formula with clear differentiation
- Edge score 0-40 with thresholds at 0.25/0.18/0.12/0.08
- Source reliability 0-25 with cross-agent "news+momentum" support
- Confluence capped at +15 to prevent runaway scores
- analysis_breakdown presence adds +5
- Volume 0-20 with tiered thresholds up to $1M

## Task Commits

1. **Task 1: Update _score_signal with improved multi-factor formula** - `c8ce4c0c` (feat)

## Files Modified
- `bot/orchestrator.py` - Updated _score_signal method (lines 144-188)

## Decisions Made
- Used min() cap on confluence score to prevent runaway scores
- Added news+momentum as high-value cross-agent source
- analysis_breakdown +5 boost for signals with structured analysis

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Next Phase Readiness

- Conviction scoring complete with clear differentiation
- Ready for further research engine improvements