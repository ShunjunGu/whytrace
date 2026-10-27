# WhyTrace — 提交核对清单（自检版）

截止：**2026-10-27 23:45 UTC** = 上海 **2026-10-28 07:45**。建议 **10/28 06:00 前** Submit。

图例：✅ 仓库侧已完成 · ⬜ 仍需你（用户）完成 · 🔶 有 key 后可很快完成

---

## ✅ 已完成（Bot / 仓库侧）

- [x] 选题：**Track 02** + 项目名 **WhyTrace**
- [x] 代码骨架：`src/whytrace/`（默认 `USE_MOCK=1`）
- [x] Zetaris client：mock + live UI-proxy 路径与错误提示
- [x] Meterless H-MEM 形状记忆 + `audit` 账本（Python mock）
- [x] 演示题库：`python -m whytrace demos` / `ask --demo 1`
- [x] 文档：README · ARCHITECTURE · INTEGRATION_NOTES · DEMO_SCRIPT · SLIDES_OUTLINE
- [x] `USER_NEXT_STEPS.md`（中文倒排）· `PROJECT_BLURB.md`（英文可粘贴）
- [x] 幻灯：`slides/whytrace-deck.html` + `.md`
- [x] `.env.example` · `.gitignore` · `LICENSE`
- [x] 测试：`tests/test_whytrace.py` **6/6 绿**（2026-10-26 复跑）
- [x] 本地 mock：`ask --demo 1` + `audit` 通过

## ⬜ 仍需你完成（注册 / 账号 / 提交）

- [ ] 用**自己的邮箱**在 https://hackathon.genai.works/event/open-agent-hackathon-2026 **注册**
- [ ] **建队**（可单人 1–5）
- [ ] 平台上选赛道 **Track 02**
- [ ] 按活动指引申请 **Zetaris** 实例 / 账号
- [ ] Zetaris UI：建 **API Token** + 抄数字 **Org ID** → 写入你本机 `.env`（勿提交 git）
- [ ] （推荐）`npx degit meterless/meterless/templates/agentathon-starter meterless-hmem` + `npm run setup`
- [ ] 新建**公开 GitHub** 并推送本仓库（排除 `.env`）
- [ ] 按 `DEMO_SCRIPT.md` **录视频**并上传（YouTube 等）
- [ ] 用 `slides/whytrace-deck.html` **导出 PDF** 或上传到网盘/Slides
- [ ] 把 `PROJECT_BLURB.md` 粘进平台项目说明，填 Repo / Video / Slides 链接
- [ ] 平台 **Submit** + 截确认页（建议 10/28 06:00 前）

## 🔶 有 key 后的短路径（非阻塞录屏，但加分）

- [ ] `.env`：`USE_MOCK=0` + proxy 三项（BASE_URL / ORG_ID / API_KEY）
- [ ] `python -m whytrace ping` 成功
- [ ] 真表名对齐后 `ask --demo 1` live 成功
- [ ] 视频中出现 Meterless `notebook.ts ask/audit` 或 Runtime（可选）
- [ ] （可选）Cursor / NVIDIA Nemotron 在 blurb 中如实勾选

## 官方 starter 命令（备用）

```bash
git clone https://github.com/zetaris/getting-started.git
npx degit meterless/meterless/templates/agentathon-starter meterless-hmem
npx degit meterless/meterless/engines/hmem my-hmem
```

## 代理禁区（再次确认）

- 不代注册、不代提交、不代建 Token、不把密钥写入仓库
