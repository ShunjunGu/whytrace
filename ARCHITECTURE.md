# WhyTrace Architecture

## Track fit

**Track 02 — The Agent That Can Explain Why**

> Build agents that investigate complex questions across multiple data sources, connect findings, and produce evidence-backed answers or recommendations.

WhyTrace maps 1:1:

| Track need | Component |
|---|---|
| Multiple data sources | Zetaris Lightning SQL over fragmented tables (collisions / zones / companies) |
| Investigate & connect | Planner → multi-query → join-in-agent |
| Evidence-backed answer | Citations `[ev-id]` tied to SQL + sample rows |
| Explain why | Meterless H-MEM trust ledger (`audit`) |

## High-level diagram

```
┌─────────────┐     question      ┌──────────────────┐
│  Analyst    │ ───────────────▶  │  WhyTrace Agent  │
│  (CLI/UI)   │ ◀───────────────  │  (orchestrator)  │
└─────────────┘   answer+cites    └────────┬─────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    ▼                      ▼                      ▼
           ┌────────────────┐    ┌──────────────────┐   ┌─────────────────┐
           │ Zetaris Client │    │ Meterless H-MEM  │   │ Synthesizer     │
           │ REST / mock    │    │ mine/store/audit │   │ mock | runtime  │
           └────────┬───────┘    └────────▲─────────┘   └────────▲────────┘
                    │                     │                      │
                    ▼                     │                      │
           ┌────────────────┐             │                      │
           │ Lightning DBs  │── findings ─┘                      │
           │ or data/*.json │──────── evidence block ────────────┘
           └────────────────┘
```

## Data flow (one ask)

1. **Parse** user question → intent tags (`crash_density`, `company_link`, …).
2. **Plan** 1–N read-only SQL templates (or mock equivalents).
3. **Query Zetaris** (`OpenSqlQuery`-style POST) with Bearer + `X-Org-ID` + `X-Request-ID`; paginate via `queryToken` if needed; close query.
4. **Mine findings** into Meterless H-MEM: each finding = claim text + provenance (sql, table, row ids) + confidence.
5. **Retrieve** related prior memories (cross-run context).
6. **Synthesize** answer that cites memory/evidence ids; label mock vs live model.
7. **Ledger** every write/read for `audit` (append-only).

## Module map

| Path | Responsibility |
|---|---|
| `src/whytrace/main.py` | CLI: `ask` / `audit` / `remember` / `status` |
| `src/whytrace/agent.py` | Orchestration loop |
| `src/whytrace/zetaris_client.py` | REST client + mock backend |
| `src/whytrace/meterless_memory.py` | H-MEM-shaped store + ledger |
| `src/whytrace/synthesizer.py` | Answer assembly (mock / OpenAI-compat) |
| `src/whytrace/mock_data.py` | Load `data/*.json` |
| `data/` | Fragmented demo sources |

## Why not Track 01 / 03 / Wildcard

- **Track 01** (Fragmented Intelligence): also natural for Zetaris, but weaker “explain why” story for Meterless trust ledger.
- **Track 03** (Reasoning Architecture): needs a more novel decision architecture than a 20h MVP.
- **Wildcard**: requires extending a *prior* project; we start greenfield.

## Failure & honesty policy

- Surface Zetaris / Meterless errors in the demo UI/CLI (no silent empty answers).
- Mark `mode=mock` vs `mode=live` in every response header line.
- Never log API keys or put them in the repo.

## Stretch (post-MVP)

- Vendor real Meterless `engines/hmem` via `npx degit` and drop the Python mock.
- Register `company_dns` / cookbook sources on a live Zetaris instance.
- Route synthesis to NVIDIA Nemotron for the in-kind DGX prize.
- Tiny Gradio/Streamlit front-end for the video.
