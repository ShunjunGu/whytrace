# WhyTrace 演示视频终稿（约 3 分钟）

录制前：字号 ≥ 18；密钥打码；片头注明 `mock` 或 `live`。  
主命令一律用题库第 1 题。

---

**【0:00–0:18】片头**

画面：标题卡  
**WhyTrace** · Open Agent Hackathon 2026 · Track 02 *The Agent That Can Explain Why*

口播：  
「大多数 AI 答完不会告诉你为什么该信它。WhyTrace 用 Zetaris 查碎片数据，用 Meterless H-MEM 记下证据，再用信任账本把 why 摊开。」

---

**【0:18–0:40】问题**

画面：三块碎片——collisions / zones / companies，箭头断开。

口播：  
「事故表、出租车区域、公司名录不在一张表里。分析师不该手工 join，也不该相信黑盒聊天。」

切到终端，先跑：

```bash
python -m whytrace status
```

口播：点一下 `zetaris` / `meterless` 的 mode 字段，诚实说出 mock 或 live。

---

**【0:40–2:10】主演示（核心）**

```bash
python -m whytrace ask --demo 1
```

口播（跟着输出节奏）：  
1. 「代理规划了跨源查询。」  
2. 「Zetaris 拉回各区域事故密度。」  
3. 「每条发现写入 Meterless 风格记忆，带上 SQL 与样例行。」  
4. 「这是带引用的结论——请看这些 `ev-` 编号。」

停 3 秒让评委看清 citations。然后：

```bash
python -m whytrace audit --limit 12
```

口播：  
「Audit 就是信任账本：每次写入、读取，以及背后的 SQL。这就是 Track 02 要的 explain why。」

（若已切真机：插入 8–10 秒 `python3 scripts/check_zetaris.py` 或 WhyTrace `ping` 成功画面。）

（若已装 Meterless starter：插入 10 秒）

```bash
npx tsx notebook.ts ask "which zone is priority"
npx tsx notebook.ts audit <memory-id>
```

口播：「同一套记忆语义，来自 Meterless H-MEM 官方 starter。」

---

**【2:10–2:35】赞助商与代码落点**

画面：分屏或快速翻文件  
- `src/whytrace/zetaris_client.py`  
- `src/whytrace/meterless_memory.py`

口播：  
「Zetaris 是数据面；Meterless 是记忆与账本。可选 NVIDIA Nemotron 做合成，冲 DGX 实物奖。」

---

**【2:35–3:00】收束**

画面：仓库 URL、Track 02、队员名。

口播：  
「WhyTrace：问一次，拿到证据，打开账本。谢谢评委。」

淡出。

---

## 录制核对

- [ ] 总长 1–4 分钟（目标 ~3:00）
- [ ] 无 API key / `.env` 明文
- [ ] 口播至少各提一次 Zetaris、Meterless
- [ ] 出现 `ask --demo 1` 与 `audit`
- [ ] mode（mock/live）说清楚
- [ ] YouTube 可见性符合提交页要求
