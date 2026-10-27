# WhyTrace — Slide Deck (Markdown export)

> Open in any Markdown→PDF tool, or use `whytrace-deck.html` in a browser (Print → Save as PDF).

---

## 1. Title

# WhyTrace
Evidence-backed answers across fragmented data

Open Agent Hackathon 2026  
**Track 02 — The Agent That Can Explain Why**

**Team:** Gu Shunjun / WhyTrace (solo)  
**Repo:** https://github.com/ShunjunGu/whytrace

---

## 2. The problem

- Facts live in **disconnected** tables and APIs
- Chatbots **invent**; spreadsheets **don’t explain**
- Stakeholders ask: **“Why should I trust this?”**

---

## 3. Who it’s for

**Ops / risk / city-data analysts**

Job-to-be-done: one question → cited answer → inspectable ledger

---

## 4. Demo question

> Which zones have the highest crash density  
> and which companies operate there?

---

## 5. Architecture

```
Analyst → WhyTrace Agent
            ├─ Zetaris (Lightning SQL / UI proxy)
            ├─ Meterless H-MEM (mine · query · ledger)
            └─ Cited answer + audit
```

---

## 6. Zetaris (required)

- **Role:** fragmented data plane
- **Call:** `POST /api/proxy/sql-editor/sqls/run-query`
- Auth: Bearer API key · `X-Org-ID` · `X-Request-ID`

---

## 7. Meterless (required)

- **Role:** memory + trust ledger (*the why*)
- Services: MemoryMining · Retrieval · **TrustLedger**
- Starter: `npx degit meterless/meterless/templates/agentathon-starter …`

---

## 8. Sample output

- Answer with `[ev-…]` citations
- Provenance: SQL + sample rows + confidence
- `python -m whytrace audit` → append-only history

---

## 9. Built this sprint / next

**Done:** end-to-end ask → cite → audit · live-ready client hooks (default mock) · docs · demo script  

**Next:** live cookbooks · vendor real H-MEM · optional Nemotron · thin UI

**Tooling:** Cursor (optional) · NVIDIA Nemotron (optional / DGX prize)

---

## 10. Closing

**Data plane: Zetaris. Why plane: Meterless.**

**Team:** Gu Shunjun / WhyTrace  
**Repo:** https://github.com/ShunjunGu/whytrace  
**Demo video:** https://github.com/ShunjunGu/whytrace/releases/download/demo-video/whytrace-demo.mp4  
**Contact:** gushunjun72@gmail.com

Thank you, judges.
