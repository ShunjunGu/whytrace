# WhyTrace 幻灯终稿（10 页 · 可直接照做）

风格：深色底、大字、每页一个观点。截图用演示题 `--demo 1`。

---

### 1. 封面
- **WhyTrace**
- Evidence-backed answers across fragmented data
- Open Agent Hackathon 2026 · **Track 02: The Agent That Can Explain Why**
- Team: _[填写]_ · Repo: _[填写]_

### 2. 问题
- 决策卡在「数据散落 + 无法审计」
- Chatbot 会编；表格不会记、不会解释
- 评委想听的一句话：*Why should I trust this?*

### 3. 用户与任务
- 对象：运营 / 风控 / 城市数据分析师
- JTBD：一个问题 → 带引用的答案 → 可打开的账本

### 4. 演示问题（原样上屏）
> Which zones have the highest crash density and which companies operate there?

### 5. 架构（一图）
```
Analyst → WhyTrace Agent
            ├─ Zetaris (Lightning SQL / UI proxy)
            ├─ Meterless H-MEM (mine · query · ledger)
            └─ Cited answer + audit
```
赞助商方框加粗。

### 6. Zetaris
- 角色：碎片数据面
- 路径：`POST /api/proxy/sql-editor/sqls/run-query`
- 截图：一条 SQL + 返回行（或 mock 标注）

### 7. Meterless
- 角色：记忆 + Trust Ledger
- 服务名上屏：MemoryMining · Retrieval · TrustLedger
- 截图：`audit` 输出或 `notebook.ts audit`

### 8. 样例输出
- 答案段落 + `[ev-…]` 引用
- 侧栏：SQL / sample rows / confidence

### 9. 本周交付 / 下一步
- 已交付：端到端 ask → cite → audit；真机 hook；演示脚本
- 下一步：cookbook 真表、vendor 真 H-MEM、Nemotron 合成、薄 UI

### 10. 收尾
- Repo · Demo · Video
- 「Data plane: Zetaris. Why plane: Meterless.」
- 谢谢评委

---

## 导出
PDF 或 Google Slides 皆可；提交前把链接写进赛事表单与 README。
