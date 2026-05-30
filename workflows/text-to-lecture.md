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

### 4 · main.tex 骨架先行（**写任何视觉之前**，搭好就立刻落云端）

> 血泪教训：main.tex 拖到最后才组装 = 项目长期不是「可编译态」，中途断线 / resume 时一片散沙。**骨架要在写第一个 scene 源码之前就建好并提交。**

1. **先搭骨架**：把 step 3 切好的每一拍都建成一个 `\begin{view}…\end{view}`，view 数量 = 镜数（一个不少）。每个 view 里先放：
   - **占位 `\say{}`**：直接填**定稿口播原文切分后的那一段**（旁白从第一秒就在 view 里，不是草稿里漂着）。
   - **占位 `\htmlFile{}`**（或对应引擎文件）：指向一个**还没写的**文件名 `scenes/scene_NN_label.html`。
2. **`\say` 与画面始终同居**：`\say{}` 从一开始就和它的 `\htmlFile{}`（或 `\manimFile`/`\remotionFile`）放在**同一个 view** 里，旁白与画面绑死，永远不脱钩。后面只换文件内容、不重切旁白。
3. **立刻提交 / 写云端**：
   - **mcp 模式**：`write_file("main.tex", <完整骨架>)` —— 这时云端已是一个**所有 view 齐全、可编译**的项目（文件还没写，编译会就该块报错，但结构在）。之后逐 view 填，走 [`_delivery.md`](_delivery.md) 路径 A 的**增量循环**（每填好一个 scene 文件 → `write_file` → 当场 `compile` 那一块）。
   - **zip 模式**：把骨架写进 `<work>/main.tex`，scene 文件逐个补齐到 `<work>/scenes/`。

骨架示例（占位旁白 + 占位文件名，view 全建齐）：
```latex
\title{<标题>}
\aspect{16:9}
\style{<风格>}
\begin{videotex}
\begin{view}[title=Scene_01_Hook]
  \say{<定稿口播第 1 段原文>}
  \htmlFile{scenes/scene_01_hook.html}   % 文件待写
\end{view}
\begin{view}[title=Scene_02_...]
  \say{<定稿口播第 2 段原文>}
  \htmlFile{scenes/scene_02_....html}    % 文件待写
\end{view}
...
\end{videotex}
```

> 命名纪律：**一个项目只用一套前缀**（如全 `scene_NN_`）；替换旧版顺手 `delete_file`/归档，别让两套命名并存——resume 时「哪套正式」全靠 main.tex 的 view 顺序说了算。

### 5 · 按「口播的重点和意思」给每段配画面 + 选引擎
读 [`../reference/engine-routing.md`](../reference/engine-routing.md)。**画面要扣这一拍口播的重点和意思**，不是泛泛配图：提到数字 → 大字反转；提到流程 → 卡片渐变；提到坍塌 → 点云收缩。速记：大字/数字/打字机 → Remotion；标题/卡片/表格/流程 → HTML；3D/公式/几何 → Manim；人脸/风景 → `\image[engine=gemini]`。**默认首选 HTML**（最快最稳）。

> **引擎一致性 > 引擎多样性**：engine-routing 别误读成「必须 ≥3 种引擎，否则像 PPT」。**静态堆叠**才像 PPT；**成体系的动效手绘 SVG / HTML 不算 PPT**。要做统一风格（如全片手绘 storybook）就可以全用一种引擎，视觉一致性优先于引擎数量。手绘风见 [`../reference/hand-drawn-storybook.md`](../reference/hand-drawn-storybook.md)。

### 5b · 寓言体 / 类比讲技术 → 先批映射表（**仅当是这类选题**）

如果选题是「拿一个故事 / 寓言去类比讲技术」（如拿城镇市集讲 MCP），**画面动手前**严格按这个 gating 顺序，每一关拿到「可以」再过下一关：

| 关 | 产出 | 为什么先批它 |
|---|------|------|
| ① **映射表** | 每个技术概念 ↔ 故事元素**一一对应**的表 | 对应关系错了，后面全白做；先把「server=店铺 / tool=货架 / token=通行牌」钉死 |
| ② **故事主线** | 串起所有映射的一条叙事线（口播稿据此切 view） | 主线定了 view 顺序才定 |
| ③ **一个视觉样张** | 走下面 step 6 的样张 gating | 风格签字 |
| ④ **量产** | 填满剩余镜 | 只在前三关都「可以」之后 |

映射表示例：
```markdown
| 技术概念 | 故事元素 |
|---|---|
| MCP server   | 百巧城里的一家店铺 |
| tool         | 店里货架上的一件器物 |
| OAuth token  | 进城的通行牌 |
```

### 6 · 样张先行 gating（**强制 —— 任何多镜任务**）

> 最值钱的一步：**先只端到端做 1 个样张镜，签字，再量产剩余镜。** 全量先做完再发现风格不对 = 十几镜返工 + 一次全量编译白烧。

1. **挑一个代表镜**（角色 / 元素最全的那一拍），**只手写它一个** scene 文件，填进对应 view。
2. **渲染**：mcp 模式 `compile` 只渲这一块；zip 模式本地走样张编译。
3. **抽帧确认**：`fetch_frame` 拉这一镜的 PNG 看实际效果。三个反直觉点见 [`../reference/compile-and-preview.md`](../reference/compile-and-preview.md)（`scene_id` 传该 block 的 `content_hash`、结果落盘大 JSON、PNG base64 藏在 `inner["image"]["data"]`）。
4. **拿签字**：把样张帧发给用户（或自检）拿到明确「可以」。**没签字不准量产。**
5. 签字后 → 才进 step 7 批量手写剩余镜。

### 7 · 手写每个 scene 的源码（样张签字后才量产）
骨架在 [`../templates/`](../templates/)。**严格手写，不调用 LLM 出代码**（HARD BAN #1）。统一调色板 [`../reference/palette.md`](../reference/palette.md) + 字体栈；**audio-first 铁律**见 [`../reference/audio-first.md`](../reference/audio-first.md)；每个 scene 独立设计（HARD BAN #2）、≤60s、命名 `scene_NN_label.<ext>`（沿用 step 4 骨架里那套前缀，一套到底）。

- **手绘 storybook 风**（全片统一手绘 SVG/HTML）：技法见 [`../reference/hand-drawn-storybook.md`](../reference/hand-drawn-storybook.md)（描边 `pathLength=1` + `draw` keyframe、`feTurbulence` 钢笔抖动、bob/sway 持续微动、cream/navy/tan 品牌色）。
- **`\manimFile` 必须 `[retime=true]`**；`\say` ≤400 字、默认不烧字幕（要 `\say[burn=on]` 才烧）。
- 每填好一个 scene 文件，mcp 模式立刻 `write_file` + 当场 `compile` 那一块（增量循环，见 [`_delivery.md`](_delivery.md)），别攒到最后。

> **开发期单镜预览、最后才全量编译**：全量编译又贵又慢（每镜现合成中文 TTS + 实时录屏，十几镜首编可达数百 credits）。开发期只渲改动的那一块；全量编译前**先给用户提示成本量级**。单镜预览的具体做法（子 tex 必须是 body 片段、临时把 main.tex 覆写成单 view 文档）见 [`../reference/compile-and-preview.md`](../reference/compile-and-preview.md)。

### 8 · 全量编译 + README + 交付
样张签字、剩余镜全部填完 → 整片编译（mcp 模式单块都在 step 7 渲过的话基本全命中缓存）。用 [`../templates/README.md.tpl`](../templates/README.md.tpl) 写「怎么用」。然后 → **交付：见 [`_delivery.md`](_delivery.md)**。

> **resume / 续传**：对话被打断后重连，**第一个动作必须是 `get_snapshot`**，以云端项目实际文件 + `main.tex` 为唯一真相；summary / 记忆里的「已全部写好」只当线索，逐个 `read_file` 核对。详见 [`../reference/resume-checklist.md`](../reference/resume-checklist.md)。
