# WhyTrace — Project Description (paste into GenAI.Works)

**Track:** 02 — The Agent That Can Explain Why  
**One-liner:** Ask a complex question across fragmented datasets; get an evidence-backed answer with citations and an inspectable trust ledger.

## Problem

Operational decisions stall when facts live in disconnected tables (e.g. crashes, zones, company directories). Chatbots invent; spreadsheets do not remember or explain *why* a recommendation is trustworthy.

## Solution

**WhyTrace** is an investigation agent that:

1. Plans read-only SQL across fragmented sources.
2. Runs queries through **Zetaris** (Lightning SQL via the official UI-proxy client: `POST /api/proxy/sql-editor/sqls/run-query` with Bearer API key, `X-Org-ID`, `X-Request-ID`).
3. Mines each finding into a **Meterless H-MEM**-shaped memory store with provenance (SQL + sample rows + confidence).
4. Returns a cited answer and exposes an append-only **trust ledger** (`audit`) so a human can see every write/read — the *why*.

Primary demo question:

> Which zones have the highest crash density and which companies operate there?

## Sponsor technology

| Sponsor | Role |
|---|---|
| **Zetaris** (required) | Data plane — query fragmented Lightning / cookbook sources |
| **Meterless** (required) | Why plane — H-MEM mine / retrieve / TrustLedger (`audit`); optional Meterless Runtime for OpenAI-compatible synthesis |
| **Cursor** (optional) | Used to scaffold, debug, and document the agent loop |
| **NVIDIA Nemotron** (optional stretch) | Alternate synthesis provider for the Best-use-of-Nemotron / DGX Spark in-kind prize |

Local rehearsal runs with `USE_MOCK=1` (bundled JSON tables + Python H-MEM mock). Live mode uses env-configured Zetaris credentials; Meterless can be swapped to the official starter:

`npx degit meterless/meterless/templates/agentathon-starter meterless-hmem`

## How to run

```bash
pip install -r requirements.txt
export PYTHONPATH=src
python -m whytrace ask --demo 1
python -m whytrace audit
```

See `README.md`, `ARCHITECTURE.md`, and `INTEGRATION_NOTES.md` in the repository.

## What judges should look for

- Alignment with Track 02: investigate → connect findings → evidence-backed recommendation.
- Explicit, non-fake sponsor usage callouts for **Zetaris** and **Meterless**.
- Demo clarity: citations (`ev-…`) plus ledger audit in under three minutes.

## Team / links

- Repository: _[paste public GitHub URL]_
- Demo video: _[paste YouTube URL]_
- Slides: _[paste PDF / Slides URL]_
- Contact: _[email]_
