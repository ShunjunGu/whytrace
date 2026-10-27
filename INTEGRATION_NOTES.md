# 拿到 Key 后 30 分钟切真机（WhyTrace）

目标：从 `USE_MOCK=1` 切到 **Zetaris 真查询 +（可选）Meterless 真 H-MEM**，并跑通 `python -m whytrace ask --demo 1`。

前提：你已在 GenAI.Works 注册、拿到 Zetaris 实例 URL / 账号（浏览器侧并行完成）。**本仓库不会替你注册或伪造 key。**

---

## 0–5 分钟 · 准备仓库与官方 starter

```bash
# WhyTrace
cd /workspace/paid-ops/open-agent-2026
cp -n .env.example .env
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python -m whytrace status   # 应显示 zetaris.mode=mock

# Zetaris 官方 helpers（强烈建议并行 clone，用来对照/preflight）
git clone https://github.com/zetaris/getting-started.git ../zetaris-getting-started

# Meterless H-MEM starter（提交前建议换成真引擎）
npx degit meterless/meterless/templates/agentathon-starter ../meterless-hmem
cd ../meterless-hmem && npm install && npm run setup
# setup = degit engines/hmem/reference → vendor/hmem
npx tsx notebook.ts seed
npx tsx notebook.ts ask "what did we decide about storage"
```

公开 URL：

| 资源 | URL |
|---|---|
| 赛事页 | https://hackathon.genai.works/event/open-agent-hackathon-2026 |
| Zetaris getting-started | https://github.com/zetaris/getting-started |
| Zetaris client setup | https://zetaris.github.io/getting-started/docs/connections/client-setup.html |
| Meterless monorepo | https://github.com/Meterless/Meterless |
| Agentathon starter | https://github.com/Meterless/Meterless/tree/main/templates/agentathon-starter |
| H-MEM engine | https://github.com/Meterless/Meterless/tree/main/engines/hmem |
| Meterless engines 页 | https://meterless.ai/engines.html |

---

## 5–15 分钟 · Zetaris：建 Key 并写入 `.env`

在 **Zetaris Web UI**（活动发给你的实例，不是随便猜的 localhost）：

1. 登录。
2. **Management → API Tokens** → `+` 创建 → **只显示一次**，立刻粘贴到本地。
3. **Management → Organisation** → 复制 **数字** ID（不是名字 / slug）。

编辑 WhyTrace `.env`：

```dotenv
USE_MOCK=0
ZETARIS_CHANNEL=proxy
ZETARIS_BASE_URL=https://YOUR-HACKATHON-UI-ORIGIN
ZETARIS_ORG_ID=123
ZETARIS_API_KEY=paste-once-here
ZETARIS_QUERY_LIMIT=50
```

规则（与官方 `scripts/zetaris_api.py` 一致）：

- `ZETARIS_BASE_URL` = **UI 源站**，无 path（例 `https://foo.example.com`），**不是** `/api/v1.0`。
- `ZETARIS_ORG_ID` 必须是纯数字。
- 优先 API Key；若没有 key，可暂用 `ZETARIS_USERNAME` + `ZETARIS_PASSWORD`（proxy 会打 `/api/auth/login`）。

同步一份到 `../zetaris-getting-started/.env.local`（官方脚本读这个文件名），然后：

```bash
cd ../zetaris-getting-started
python3 scripts/check_zetaris.py
# 期望: Zetaris connection OK. Visible Lightning databases: N
python3 scripts/query_zetaris.py "SELECT 1"
```

WhyTrace 等价检查：

```bash
cd /workspace/paid-ops/open-agent-2026
PYTHONPATH=src python -m whytrace ping
# zetaris.ok == true
```

### 真实 HTTP（proxy，WhyTrace 默认 live channel）

```http
GET  {ZETARIS_BASE_URL}/api/proxy/lightning-database/databases
POST {ZETARIS_BASE_URL}/api/proxy/sql-editor/sqls/run-query
Authorization: Bearer {ZETARIS_API_KEY}
X-Org-ID: {ZETARIS_ORG_ID}
X-Request-ID: {uuid4}

{"sql":"SELECT 1","limit":50}
```

对应代码：`src/whytrace/zetaris_client.py` → `_proxy_run_sql` / `_proxy_list_databases`。

### 常见错误 → 怎么修

| 现象 | 处理 |
|---|---|
| `live-unconfigured` / missing Org ID | `.env` 里 `ZETARIS_ORG_ID` 必须是数字 |
| HTTP 401/403 | 重新建 API Token；确认 Bearer 未带引号/空格 |
| HTTP 400 | Org ID 错或非数字；换新 `X-Request-ID`（客户端每次自动生成） |
| HTTP 404 on proxy path | `ZETARIS_BASE_URL` 写成了 API base；改成 UI origin |
| Cannot reach host | VPN / 错误 URL / 实例未开 |
| 空 rows | 表未注册：用 getting-started `onboard.py` / cookbook；先 mock 演练视频 |

表名在真机上可能与 mock 不同。拿到 `SHOW LIGHTNING DATABASES` 结果后，改 `agent.py` / SQL 模板里的 qualified name，或先用官方 `company_dns` / collisions cookbook。

可选：`ZETARIS_CHANNEL=direct` + `ZETARIS_REST_URL=…/api/v1.0`（旧 OpenSqlQuery）。**不确定时用 proxy。**

---

## 15–25 分钟 · Meterless：真 H-MEM（推荐）或 Runtime

### A. H-MEM starter（零云端 key，评委爱看 engine usage）

```bash
npx degit meterless/meterless/templates/agentathon-starter meterless-hmem
cd meterless-hmem
npm install
npm run setup          # 必做：vendor/ 被 gitignore，不 setup 就没有引擎
npx tsx notebook.ts seed
npx tsx notebook.ts remember "Midtown Center is our priority safety zone"
npx tsx notebook.ts ask "which zone is priority"
npx tsx notebook.ts audit mem-1   # 用 seed/remember 打印出的真实 id
```

真实调用（`notebook.ts`）：

```ts
const mined = await hmem.mine("chat_message", text);
const record = hmem.add({ content: text, type: "general", source: "notebook:manual" });
const result = hmem.query(question, { threshold: 0.1 });
const history = hmem.ledger.history(memoryId);
const preview = hmem.sleep.preview();
```

WhyTrace 当前默认 `METERLESS_BRIDGE=mock`（Python 账本）。切真机演示策略（30 分钟够用）：

1. **视频里先跑 WhyTrace mock/live Zetaris ask**，展示 citations；
2. **再切到 `meterless-hmem` 终端**，对同一结论 `remember` / `ask` / `audit`，口头说明 “Meterless TrustLedgerService”；
3. 若有余力，把 findings JSON 管道进 `notebook.ts remember`（一行 shell 即可）。

引擎-only：

```bash
npx degit meterless/meterless/engines/hmem my-hmem
cd my-hmem/reference && npm install && npm test
HMEM_IMPL=$PWD/index.ts npx tsx ../conformance/runner.ts   # 路径以仓库为准
```

### B. Meterless Runtime（可选，给 synthesizer）

```dotenv
SYNTHESIS_PROVIDER=meterless
METERLESS_RUNTIME_URL=http://127.0.0.1:8088/v1
METERLESS_RUNTIME_TOKEN=   # 来自 runtime <stateDir>/proxy-token；禁止用占位 rt-local
METERLESS_APP_ID=whytrace
```

```http
POST http://127.0.0.1:8088/v1/chat/completions
Authorization: Bearer <token>
meterless-app: whytrace
meterless-scope: user

{"model":"meterless/auto","messages":[{"role":"user","content":"..."}]}
```

没有 Runtime 时保持 `SYNTHESIS_PROVIDER=mock`——答案仍带 citations，足够 Track 02 叙事。

---

## 25–30 分钟 · 验收与录屏命令

```bash
cd /workspace/paid-ops/open-agent-2026
source .venv/bin/activate
export PYTHONPATH=src

python -m whytrace ping          # zetaris.ok true
python -m whytrace demos         # 看题库
python -m whytrace ask --demo 1  # 主演示题
python -m whytrace audit --limit 20
```

通过标准：

- [ ] `ping` 成功（或诚实保留 mock 并在口播说明，同时展示 live `query_zetaris.py`）
- [ ] `ask --demo 1` 打出带 `[ev-…]` 的答案
- [ ] `audit` 能看到 write/read 与 SQL provenance
- [ ] 另开终端能跑 Meterless `notebook.ts ask/audit`
- [ ] `.env` 未进 git

失败时：**不要用假 key 盲打真实 API**。改回 `USE_MOCK=1`，先用 mock 录完整视频，再插 10 秒真机 `SELECT 1` / `check_zetaris` 镜头。

---

## 接口对照（实现者）

| WhyTrace | Zetaris 真机 | Meterless 真机 |
|---|---|---|
| `ZetarisClient.ping` | `GET …/lightning-database/databases` | — |
| `execute_sql` / density / zones / companies | `POST …/sql-editor/sqls/run-query` | — |
| `MeterlessMemory.remember/mine_finding` | — | `hmem.mine` / `hmem.add` |
| `retrieve` | — | `hmem.query` |
| `audit` | — | `hmem.ledger.history` |
| `synthesizer` meterless | — | Runtime `/v1/chat/completions` |

错误类：`ZetarisError`（含修复提示）→ `whytrace ask` 打印并 exit 2；`whytrace ping` 失败 exit 2。
