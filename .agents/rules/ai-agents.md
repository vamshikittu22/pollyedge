[AI AGENT RULES]
→ All agents inherit from bot/agents/baseagent.py — never duplicate scan/signal logic
→ Orchestrator (orchestrator.py) coordinates agents — never places trades directly
→ Signal flow: agent.scan() → signalengine.py → riskmanager.py → approvalgate.py → trade
→ Risk manager gates every trade — no agent bypasses riskmanager.py
→ Approval gate: REQUIRE_APPROVAL=true sends to Telegram before execution
→ Each agent is responsible for ONE signal type only — no crossover logic
→ Agent parallelism: Python threading in orchestrator — never asyncio in bot code
→ load_dotenv must be first in every agent file — checked via AST before commit
→ Agent signals must include: label, side, size, edge, source, score, market_prob, model_prob
→ Min edge threshold: 8% — any signal below this is filtered before risk manager sees it
→ Never hardcode API keys — all via os.getenv after load_dotenv
→ Log every signal: found, rejected (with reason), and executed to logs/pollyedge.log
