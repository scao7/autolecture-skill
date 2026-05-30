# Workflow · 简单指令 / 文字稿 → 讲解视频（音频驱动）

**入口**：用户只给**一句指令 / 一个选题 / 一段文字稿**，没有录音、没有 PDF、没有实拍。
旁白用 TTS 合成（`\say{}`），视觉全部手写源码。

> **音频驱动 + 先定稿**：这条流程没有现成音频，所以**第一件事是把口播稿写出来给用户定稿**——口播稿是整片的时间轴脊柱，定下来之后所有画面才围着它排。

> 配套素材（GitHub repo 截图 / 本地图片）是 opt-in 增量，见 [`../reference/figure-matching.md`](../reference/figure-matching.md)。用户其实给了 PDF / 录音 / 实拍 → 回路由走对应 workflow。

---

## 步骤

### 0 · 用 SKILL.md 入口已确认的运行模式 + 定 voice clone 处理

> **运行模式已在 SKILL.md 入口 ① 定下**(mcp / zip),这里不再问。

**voice clone 决策**(text-to-lecture 默认走 TTS,必须做):
- **mcp**:看 `whoami` 给的用户信息有没有 voice sample;有 → "所有 `\say[voice=mine]`";拿不到就同 zip 问用户。
- **zip**:`AskUserQuestion` 二选一:① 是,用我的克隆声(全片 `voice=mine`) ② 否 / 不清楚(默认 speaker)。

决定写进 `<work>/script.md` 的 plan 备注里。整片所有 `\say` 同一种处理。mcp / zip 两模式每个动作对照见 [`../reference/runtime-modes.md`](../reference/runtime-modes.md)。

### 1 · 准备工作目录
```bash
WORK=/tmp/autolecture_$(date +%s); mkdir -p $WORK/{scenes,figures}
```

### 2 · 写口播稿 → 交用户改 / 批准（**硬性 gate，先停一下**）
- 把用户的指令 / 选题 / 素材，写成一份**完整、分段的口播稿**（每段就是后面一个 view 的 `\say{}` 内容）。
- 写成 `<work>/script.md`，分段编号，每段下面附**一句话画面意图**（这一拍要让观众看到什么）。
- **必须把口播稿发给用户，等用户修改 / 批准后再继续。** 不要跳过这一步直接去做画面——稿子是时间轴，稿子没定，画面白做。
- 用户改了 → 更新 `script.md` 再确认一次；明确批准 → 进入下一步。

### 3 · 估算每段时长（TTS 时间）→ 切 view
- 口播稿定稿后，按字数粗估每段 TTS 时长（中文约 4–5 字/秒；英文约 2.5 词/秒）记到 beat_plan，用于规划。
- **真实时长在编译时由 TTS + audio-first 自动锁定**（`\say{}` 的实际语音长度驱动该 view，视觉用 audio-first 自适应，见 [`../reference/audio-first.md`](../reference/audio-first.md)）——所以估算只为排版，不必精确。
- 5–12 段，每段 30–90 秒；输出 `<work>/beat_plan.md`：

```markdown
| # | 估时 | 口播要点 | 视觉引擎 | 设计要点 |
|---|------|----------|----------|----------|
| 1 | ~22s | 抛出反直觉问题 | Remotion | 问题文字 typewriter + 大问号脉冲 |
| 2 | ~38s | 三大核心数字   | HTML     | 三柱卡片错位反转 |
```

### 4 · 按「口播的重点和意思」给每段配画面 + 选引擎
读 [`../reference/engine-routing.md`](../reference/engine-routing.md)。**画面要扣这一拍口播的重点和意思**，不是泛泛配图：提到数字 → 大字反转；提到流程 → 卡片渐变；提到坍塌 → 点云收缩。速记：大字/数字/打字机 → Remotion；标题/卡片/表格/流程 → HTML；3D/公式/几何 → Manim；人脸/风景 → `\image[engine=gemini]`。**默认首选 HTML**（最快最稳）。

### 5 · 手写每个 scene 的源码
骨架在 [`../templates/`](../templates/)。**严格手写，不调用 LLM 出代码**（HARD BAN #1）。统一调色板 [`../reference/palette.md`](../reference/palette.md) + 字体栈；**audio-first 铁律**见 [`../reference/audio-first.md`](../reference/audio-first.md)；每个 scene 独立设计（HARD BAN #2）、≤60s、命名 `scene_NN_label.<ext>`。

### 6 · 组装 main.tex
```latex
\title{<标题>}
\aspect{16:9}                 % 默认 720p。要 1080p 写 \aspect{16:9, 1080p}；要 4K 写 \aspect{16:9, 4k}
\style{深色背景、Inter + PingFang SC、accent #6ec1e4}

\begin{videotex}
\begin{view}[title=Scene_01_Hook]
  \say{<定稿口播这一段>}
  \remotionFile{scenes/scene_01_hook.tsx}
\end{view}
...
\end{videotex}
```

### 7 · README + 交付
用 [`../templates/README.md.tpl`](../templates/README.md.tpl) 写「怎么用」。然后 → **交付：见 [`_delivery.md`](_delivery.md)**。
