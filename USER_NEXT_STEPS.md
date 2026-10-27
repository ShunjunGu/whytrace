# 你这边要做的事（WhyTrace · Open Agent Hackathon 2026）

Bot 电脑你暂时打不开，**请用自己的邮箱在 GenAI.Works 注册**。  
本仓库已在 `/workspace/paid-ops/open-agent-2026/` 备好可提交骨架（mock 全绿）。下面按**上海时间截止 2026-10-28 07:45**倒排。

赛事页：https://hackathon.genai.works/event/open-agent-hackathon-2026

---

## 倒排时间表（建议）

| 时段（上海） | 你要完成的事 |
|---|---|
| **现在 → 10/26 晚** | ① 邮箱注册 ② 建队（可单人）③ **选 Track 02** ④ 跟活动指引申请 **Zetaris** 准入/账号 |
| **10/27 上午** | ⑤ Zetaris：UI 建 API Token + 抄数字 Org ID；填本机 `.env`，`USE_MOCK=0` 后跑 `ping` / `ask --demo 1` |
| **10/27 下午** | ⑥ Meterless：`npx degit …/agentathon-starter` + `npm run setup`；视频里能展示 `ask`/`audit` |
| **10/27 晚** | ⑦ 公开 GitHub（推本仓库）⑧ 按 `DEMO_SCRIPT.md` 录 2–4 分钟视频 ⑨ 用 `slides/` 导出 PDF/上传 |
| **10/28 05:00 前** | ⑩ 平台表单全部填完并 **Submit**；截确认页。**最迟不要拖过 07:45** |

缓冲：Submit 至少提前 **60 分钟**（建议 10/28 06:00 前完成）。

---

## 逐步清单

### 1. 注册与组队
1. 打开赛事页 → Register（用你的邮箱）。
2. 创建 Team（单人也可以，队伍人数 1–5）。
3. **赛道选：Track 02 — The Agent That Can Explain Why**（不要选 Wildcard，除非你有「赛前已有项目」要扩展）。

### 2. 申请赞助商访问
**Zetaris**
- 按活动工作区 / Data Day / Discord 指引开通实例。
- 登录 UI → **Management → API Tokens** 建 key（只显示一次）。
- **Management → Organisation** 抄**数字** ID。
- 文档：https://zetaris.github.io/getting-started/docs/connections/client-setup.html  
- 官方 helpers：`git clone https://github.com/zetaris/getting-started.git`

**Meterless**
```bash
npx degit meterless/meterless/templates/agentathon-starter meterless-hmem
cd meterless-hmem && npm install && npm run setup
npx tsx notebook.ts seed
npx tsx notebook.ts ask "what did we decide about storage"
```
- 仓库：https://github.com/Meterless/Meterless  
- 无云端 key 也能跑 H-MEM；Runtime 可选。

### 3. 填本机 `.env`（密钥只放你电脑）
从仓库复制 `.env.example` → `.env`：

```dotenv
USE_MOCK=0
ZETARIS_CHANNEL=proxy
ZETARIS_BASE_URL=https://你的UI源站   # 不要带 /api 路径
ZETARIS_ORG_ID=数字
ZETARIS_API_KEY=粘贴一次
```

然后在仓库根目录：

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src
python -m whytrace ping
python -m whytrace ask --demo 1
python -m whytrace audit
```

拿不到 key 或 ping 失败时：保持 `USE_MOCK=1` 仍可录完整演示，口播说明 mock，并尽量插 10 秒官方 `check_zetaris.py` 成功画面。细节见 `INTEGRATION_NOTES.md`。

### 4. 公开 GitHub
1. 新建公开仓库（例如 `whytrace`）。
2. 推送本目录内容（**不要**提交 `.env` / `.venv` / `.whytrace`）。
3. README 已写赞助商集成说明；确认 LICENSE 在仓内。

### 5. 录视频
- 照 `DEMO_SCRIPT.md`（约 3 分钟）。
- 必跑：`python -m whytrace ask --demo 1` → `python -m whytrace audit`。
- 口播点名 **Zetaris** 与 **Meterless**；字号大；无密钥入镜。
- 上传 YouTube（公开或提交页允许的可见性），复制链接。

### 6. 幻灯
- 源稿：`slides/whytrace-deck.md` 与 `slides/whytrace-deck.html`（浏览器打开 HTML → 打印/另存 PDF，或按页截图）。
- 也可按 `SLIDES_OUTLINE.md` 丢进 Google Slides / Canva。

### 7. 平台提交
粘贴 `PROJECT_BLURB.md` 到项目说明。  
附上：Repo URL、Demo/视频、幻灯链接、Track 02。  
点 Submit → **截确认页保存**。

---

## 我们已替你做好的（无需重复）

- Track 02 选题与 WhyTrace 代码骨架（mock 可跑）
- README / ARCHITECTURE / INTEGRATION_NOTES / DEMO_SCRIPT / CHECKLIST
- 英文项目说明 `PROJECT_BLURB.md`
- 幻灯大纲 HTML+MD（`slides/`）
- 单元测试 6/6 通过

## 我们不会替你做的

- GenAI.Works 注册 / 建队 / 选赛道  
- 申请或填写 API key  
- 在你账号下建 GitHub、传 YouTube、点 Submit  

卡住时把报错原文（打码密钥）发回来即可继续改代码。
