# WhyTrace — Evidence-Backed Answers Across Fragmented Data

**Open Agent Hackathon 2026 · Track 02: The Agent That Can Explain Why**

> Ask a complex question across messy, split datasets. Get an answer with SQL citations, then inspect the Meterless H-MEM trust ledger that shows *why* each claim is trusted.

- Event: https://hackathon.genai.works/event/open-agent-hackathon-2026
- Deadline: **2026-10-27 23:45 UTC** (Asia/Shanghai **2026-10-28 07:45**)
- Hard requirement: every submission must integrate **Zetaris** and **Meterless**
- Optional: Cursor; NVIDIA Nemotron for Best-use-of-Nemotron (DGX Spark)

This package is a **no-login scaffold**: mock mode runs locally without API keys. Real keys go in `.env` only after you create them yourself.

---

## For the human submitter

- Chinese next steps (deadline countdown): [`USER_NEXT_STEPS.md`](./USER_NEXT_STEPS.md)
- English blurb to paste on GenAI.Works: [`PROJECT_BLURB.md`](./PROJECT_BLURB.md)
- Slides (HTML → Print to PDF): [`slides/whytrace-deck.html`](./slides/whytrace-deck.html)

## One-line value

WhyTrace turns fragmented Lightning SQL sources (via Zetaris) into auditable, evidence-backed recommendations, with every finding stored and explained through Meterless H-MEM.

## User story

As an ops / risk analyst, I ask:

> “Which NYC taxi zones show the highest nearby crash density, and which companies appear tied to those zones?”

WhyTrace:

1. Plans SQL against fragmented tables (collisions, zones, company directory).
2. Runs queries through the **Zetaris** client (or local mock tables).
3. Mines each finding into **Meterless H-MEM** with source provenance (SQL + row refs).
4. Returns an answer with citations, plus `audit` so a human can see the trust ledger.

## CLI cheat sheet

```bash
export PYTHONPATH=src
python -m whytrace status
python -m whytrace ping
python -m whytrace demos
python -m whytrace ask --demo 1          # primary video question
python -m whytrace ask "your question"
python -m whytrace audit --limit 20
python -m whytrace audit --memory ev-........
python -m whytrace remember "Prefer borough rollups when joins are sparse."
```

Live switch (after real keys): set `USE_MOCK=0`, fill Zetaris proxy env, follow **INTEGRATION_NOTES.md** (30-minute path). Default stays mock.

Tests (mock only):

```bash
PYTHONPATH=src python -m unittest tests.test_whytrace -v
```

## Quick start (mock — no keys)

```bash
cd /workspace/paid-ops/open-agent-2026
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # leave USE_MOCK=1

python -m whytrace ask "Which zones have the highest crash density and which companies operate there?"
python -m whytrace audit
python -m whytrace remember "Prefer borough-level rollups when zone joins are sparse."
```

Expected: a printed answer with `[ev-…]` citation ids, then a ledger of memory writes/reads.

## Sponsor integration (judges look here)

| Sponsor | Role in WhyTrace | Where in code |
|---|---|---|
| **Zetaris** | Fragmented data plane: Open SQL query / Lightning databases | `src/whytrace/zetaris_client.py` |
| **Meterless** | H-MEM memory + trust ledger for “why / evidence” | `src/whytrace/meterless_memory.py` |
| Cursor (optional) | Build/debug agent loop | human workflow |
| NVIDIA Nemotron (optional) | Synthesis model for DGX prize track | `SYNTHESIS_PROVIDER=nemotron` in `.env` |

### Zetaris — minimal real call (after you have keys)

```python
# Headers: Authorization: Bearer <ZETARIS_API_KEY>
#          X-Org-ID: <ZETARIS_ORG_ID>
#          X-Request-ID: <uuid4>
# Body (OpenSqlQuery style):
{"select": "SELECT * FROM NY_VEHICLE_COLLISIONS.crash", "pageLimit": 20}
```

Docs / starters:

- Getting started: https://zetaris.github.io/getting-started/
- Client setup (REST + API key): https://zetaris.github.io/getting-started/docs/connections/client-setup.html
- Scripts HOWTO: https://zetaris.github.io/getting-started/scripts/HOWTO.html
- Knowledge base REST: https://kbase.zetaris.com/knowledge/rest-api
- Hackathon getting-started repo (LinkedIn / Zetaris): search `zetaris/getting-started` on GitHub

**API key application (you must do this):**

1. Register on the GenAI.Works hackathon page and complete Zetaris access / Data Day onboarding as provided in the event workspace.
2. Sign in to the Zetaris UI → **Management → API Tokens** → create key → save once as `ZETARIS_API_KEY`.
3. **Management → Organisation** → copy numeric ID → `ZETARIS_ORG_ID`.
4. Set `ZETARIS_REST_URL` to the supplied API base ending in `/api/v1.0` (local default `http://localhost:8888/api/v1.0`).

### Meterless — minimal integration

Option A — **H-MEM engine** (recommended for Track 02; zero cloud keys for memory):

```bash
npx degit meterless/meterless/templates/agentathon-starter meterless-hmem
cd meterless-hmem && npm install && npm run setup
```

Wire WhyTrace findings into `remember` / retrieval / `audit` (TrustLedgerService). Spec: https://github.com/Meterless/Meterless/tree/main/engines/hmem

Option B — **Meterless Runtime** as OpenAI-compatible LLM (optional synthesis):

```http
POST http://127.0.0.1:8088/v1/chat/completions
Authorization: Bearer <token from runtime stateDir/proxy-token>
meterless-app: whytrace
{"model":"meterless/auto","messages":[{"role":"user","content":"..."}]}
```

Docs: https://meterless.ai/engines.html · Repo: https://github.com/Meterless/Meterless · Hackathon guide: https://github.com/Meterless/Meterless/blob/main/docs/community/hackathon-guide.md

This repo ships a **faithful Python mock** of mine / store / retrieve / ledger so the demo runs without Node. Swap `meterless_memory.py` for the real reference when you vendor H-MEM.

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md).

## Demo & slides

- Video script (1–4 min): [DEMO_SCRIPT.md](./DEMO_SCRIPT.md)
- Slide outline: [SLIDES_OUTLINE.md](./SLIDES_OUTLINE.md)
- Submission checklist: [CHECKLIST.md](./CHECKLIST.md)

## Tech stack

- Python 3.10+
- `httpx` for Zetaris REST
- Local JSON mock datasets under `data/`
- Optional: Meterless Runtime / Anthropic / NVIDIA Nemotron for answer synthesis

## License

MIT (add `LICENSE` before public GitHub push). Do not commit `.env` or API keys.

## Status

Scaffold only — **not registered, not submitted, no real API keys present.**  
`USE_MOCK=1` by default.
