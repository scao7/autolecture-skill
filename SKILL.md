---
name: autolecture-skill
description: 用户给一段口播音频 / 已录好的播客 / 或纯文字脚本（可选附加 PDF 论文 / GitHub repo），端到端生成一个可在 AutoLecture (https://autolecture.ai) 编译出片的项目。交付两条路径任选：打包 zip 让用户自己上传网站改代码，或用 `autolecture` Python SDK 一键上传 + 编译 + 下载 mp4。所有视觉用 \\manimFile / \\htmlFile / \\remotionFile 手写源码（**不走 LLM 提示词**），AI 仅用于 \\image[engine=gemini]{} 生图。PDF 可「讲解知识」(抽 figure) 或「展示原件」(react-pdf 真页 + zoom + 文字高亮)。目标：用户提供素材 → 跑完 → out.mp4 + Studio URL。
---

# autolecture-skill

把"一段随手录的乱口播 / 一段成品播客 / 一段文字稿"变成可立即在 AutoLecture 里点 ▶ Recompile 出片的项目包。

## 何时触发

- 用户说"做个 autolecture demo"、"我录了段口播，做成视频"、"我有篇文字稿，做成解说"、"剪我这段播客配画面"、"把我这篇论文做成讲解视频"、"我 GitHub 上有个项目，帮我做个介绍片"
- 用户提供以下任一**主输入**：
  - 一段音频文件（mp3/wav/m4a），内容是随口录的（可能跑题、卡顿、错字）
  - 一段已经精修过的音频（podcast 成品、有意识录的口播）
  - 一段文字（演讲稿、博客文章、项目介绍）
- 可选**配套素材输入**（自动 match 到对应音频段 → 出现在画面上）：
  - **PDF 论文**：抽出每页 + 单独图表（pdftoppm），按音频提到的图号 / 概念 match
  - **GitHub repo**（URL 或本地路径）：扫描 `*.png/*.jpg/*.svg/*.gif` + README 截图，按文件名 / 上下文 match
  - **本地图片文件夹**：用户已经手动整理好的素材，直接按文件名 match
- 用户的目标是<strong>立刻能编译出片</strong>，而不是花一周打磨

## 三种输入模式

| 模式 | 输入 | 音频处理 | 叙事处理 | 输出风格 |
|---|---|---|---|---|
| **rough** | 随口录的乱音频 | Whisper 转录 → 修错字 → LLM 重组叙事 → **TTS 重新合成**（`\say{}`） | 重写顺序、补充连接句、删冗余 | 干净播客感 |
| **polished** | 成品播客/精修音频 | Whisper 转录用于定位 + 字幕，**音频保持原状**（`\audio[start=,end=]{}` 剪辑） | 不改顺序，按内容自然分段 | 保留原声 |
| **text** | 纯文字稿 | 无 → 直接 `\say{}` TTS 合成 | 按段落切 view | 旁白讲述 |

判定规则：
- 用户明说"用我自己的声音/原音"→ **polished**
- 用户提供的音频是一气呵成的旁白稿（>10 分钟、连贯）→ 默认 **polished**，但向用户确认一次
- 用户提供的是头脑风暴、卡顿、重复的录音 → **rough**
- 用户只给文字 → **text**
- 含糊不清 → AskUserQuestion 让用户在 rough / polished 中选

## PDF 有两种流程 — 先判断再动手

用户给 PDF（通常是论文），**先分清诉求**（详见 [`reference/pdf-showcase.md`](reference/pdf-showcase.md)）：

| 流程 | 用户想要 | 怎么做 |
|---|---|---|
| **A · 讲解知识**（默认）| "把这篇论文讲明白" | LLM 读 PDF → 口播脚本 → 抽 figure 配画面（下方"配套素材"流程）|
| **B · 展示 PDF** | "在视频里**展示**这份 PDF，翻页 / 放大 / 高亮某句话" | `react-pdf` 直接渲染真页 + zoom + 文字高亮，用 [`scene_pdf_highlight`](templates/scene_pdf_highlight.tsx.tpl) / [`scene_pdf_focus`](templates/scene_pdf_focus.tsx.tpl) 模板 |

判定："讲解/科普" → A；"展示原件 / 翻页 / 放大原文 / 高亮这句话 / 像翻杂志" → B；含糊就问一句。两者可混用（A 为主，插 B 的原文高亮镜头）。

**Flow B 要点**：PDF 当项目 asset 上传，scene 里 `staticFile('paper.pdf')`，**不跑** `extract_pdf_figures.py`。高亮**不要硬编码坐标** — 把旁白这一拍引用的短语填进模板的 `TARGET`，模板用 pdfjs text layer 自动定位 bbox + 把 zoom 推到那句话。需要 AutoLecture bundle 里的 react-pdf（已内置）。

下面的"配套素材"流程是 **Flow A** 用的（抽 figure 当素材，最终画面是重新设计的 scene，PDF 原件不出镜）。

## 配套素材（Flow A）：PDF figure / GitHub repo / 本地图片

主输入是音频/文字（始终需要）。**配套素材是 opt-in 增量**：用户给了 → 自动 match → 出现在画面上；没给 → 跳过这一步，按基础 mode 出 demo。

| 配套类型 | 抽取 | match 策略 | 视觉表达 |
|---|---|---|---|
| **PDF 论文** | `scripts/extract_pdf_figures.py`：**默认 figures-only** — pdftoppm 临时栅格化 + pdfplumber 检测 figure bbox + Pillow 裁切 → `fig-1.png .. fig-N.png` + manifest（含 caption）。整页栅格仅 `--with-pages` 才输出 | "图 N / Figure N / caption 关键词" → 对应 fig；引用一段文字 / 公式 → 需要 `--with-pages` 拿整页 + highlight rect | figure zoom-in / annotate overlay / side-by-side；text-highlight 用整页 + masked region |
| **GitHub repo** | `scripts/clone_github_assets.py`：sparse-clone → 扫 `*.png/.jpg/.svg/.gif` + `README*` 引用 | 音频里搜 repo 名 / 模块名 / 截图标题；README anchor 段落 → 对应截图 | 截图 zoom-in + annotate / 代码 diff 卡片 |
| **本地图片夹** | 直接读 | 按文件名 keyword 匹配 transcript（"intro.png" 匹配 "我们先看 intro" 这种段落） | 同 PDF |

判定规则：
- 用户说"我有论文 / paper / arxiv 链接 / .pdf 文件"→ 走 PDF 流程
- 用户说"我有个 GitHub repo / 我开源的项目"→ 走 repo 流程
- 用户传图片附件 → 走本地图片流程
- 用户没提到任何素材 → 跳过 match 步骤，按基础 mode 出片

## 视觉效果（图表特化）

抽到图表后**不要**单纯铺图。每张图至少包装一种动态：

| 效果 | 实现 | 何时用 |
|---|---|---|
| **Zoom-in (Ken Burns)** | Remotion `scale(1 → 1.15)` + `translate` 移焦点 | 静态截图 / 论文图 |
| **Crop + reveal** | HTML 先显示完整图缩略，cross-fade 到放大版的某一部分 | 论文图里只想强调一个区域 |
| **Annotate overlay** | Remotion 在图上方画箭头 / 红框 + 文字标签（绝对定位） | 教程类讲解，需要"看这里" |
| **Side-by-side** | HTML grid + 两张图入场动画错位 | A/B 对比、before/after |
| **Page scroll** | Remotion 整页 PDF 截图 + `translateY` 慢滚 | 给观众"翻一翻"的感觉 |

模板：[`templates/scene_image_zoom.tsx.tpl`](templates/scene_image_zoom.tsx.tpl) 是 Ken Burns 默认骨架；剩下的按需手写。

## 实拍结合（footage + 动效叠加）

用户给一段**真实拍摄的视频**（口播、操作录屏、产品镜头），想在上面加动效字幕 / 下三分图 / 箭头标注 → 用 Remotion 的 `over=` opt。后端把 scene **透明渲染**（alpha），再 ffmpeg 合成到实拍片段**上面**；实拍是主轴，它的时长决定这一镜的长度。

```latex
\begin{view}
  \remotionFile[over=clip.mp4]{scene_overlay.tsx}   % clip.mp4 在 assets/
  \say{这一拍的旁白……}                              % 与实拍原声「叠加」播放，不替换
\end{view}
```

- **音频是叠加模式**：实拍原声 + `\say` 旁白 + `\bgm` 一起 mix（不是替换）。调音量：`over_volume=0.4`（压低实拍原声给旁白让路）、`\say[volume=1.2]`、`\bgm[volume=0.3]`。
- **模板** [`templates/scene_overlay.tsx.tpl`](templates/scene_overlay.tsx.tpl)。两条铁律：① 根 `AbsoluteFill` **绝不能设不透明 backgroundColor**（否则盖住实拍）；② 只给图形元素本身上背景。
- 实拍片段当普通 asset 上传到 `assets/`；`over=` 的值是相对 `assets/` 的路径。

## HARD BANS

1. **禁止用 LLM 提示词宏**：`\manim{prompt}` / `\html{prompt}` / `\remotion{prompt}` / `\show{}` 一律不准。所有视觉必须是 `\manimFile{path.py}` / `\htmlFile{path.html}` / `\remotionFile{path.tsx}` / `\imageFile{path.png}` / `\image[engine=gemini]{prompt}`（AI 生图允许）。
   - 理由：LLM 出代码不稳定，编译失败率高、用户调试痛苦。手写源码 + 缓存命中 = 编译几秒钟搞定。
2. **禁止 96-card-template 偷懒**：每个 scene 的视觉<strong>必须</strong>根据该 view 的内容定制设计。不能用同一个模板填不同文字。比如提到坍塌 → 画 3D 点云收缩；提到流程 → Remotion 卡片渐变；提到数字 → 大字反转。
3. **禁止漏修转录错字**：中文 Whisper 转录有大量同音字错误，必须建立<strong>修正映射表</strong>后再用于 headline。常见错字见 [`reference/typo-fixes.md`](reference/typo-fixes.md)。**音频内容不动**，错字只影响视觉文字。
4. **禁止 silent fallback — 质量优先**：依赖缺失、抽取失败、视觉素材损坏 → **立即报错给用户**，不输出降级产物。例如 `extract_pdf_figures.py` 缺 pdfplumber 就 hard-exit，不会偷偷只出 page-level。`autolecture_no_silent_fallback` 是这个 skill 的生命线。
5. **禁止给 `examples/` 提交 AI 生成的样例**（按 `autolecture_few_shot_human_curated` 规则）。
6. **禁止裸铺图**：从 PDF / repo 抽出来的图必须包装至少一种动态效果（zoom / crop / annotate / side-by-side / scroll）。静态贴图 = 偷懒。
7. **禁止从 repo 拉超过 50MB 素材**：`clone_github_assets.py` 用 sparse-checkout 只拉图片；超过阈值的图自动跳过 + 警告用户。
8. **图表 match 必须有锚句证据**：每张抽到的图标记到哪个 view 时，要在 `beat_plan.md` 里写明 transcript 中触发匹配的原句（防止凭感觉乱塞图）。
9. **禁止默认抽 PDF 整页栅格**：`extract_pdf_figures.py` 默认 figures-only — 你只对图片感兴趣。**只有显式做「文字 highlight」（quote 一段、zoom 一条公式、整页 scroll）才用 `--with-pages` opt-in。**
10. **音频时长驱动视觉**：写源码时**绝不**反向假设视觉时长决定 scene 时长。三个引擎各自的 audio-first 写法见下节，违反规则的 scene 会出现"动画提前结束 + 后段冻结"或"动画跑得比音频快 → 看不清"。

## 音频优先（audio-first timing）— 三引擎写法对照

**核心原则**：音频长度是 ground truth。视觉适配音频，绝不反过来。compiler 编译时已经知道 audio 时长（target_dur），三个引擎各自的适配方式不同：

### `\manimFile{}` — compiler 自动 AST scale

AutoLecture 后端对 `\manimFile` 用户源码跑 `fit_manim_to_target`：扫 `construct()` 里所有 `self.play(run_time=N)` + `self.wait(N)`，求和得 natural_dur，然后把每个 `run_time=` 和 `wait()` 按 `target_dur / natural_dur` 倍率统一重写（clamp 在 [0.3×, 4.0×]）。

**写法**：写「自然时长」让 scaler 接管：
```python
self.play(FadeIn(circle), run_time=1.0)
self.wait(2.0)
self.play(circle.animate.scale(1.6), run_time=1.5)
```
**禁止**：
- 预估"音频 15s 所以 run_time=2.5"——TTS 实际 14.3s 时整片都错。
- 用 `time.sleep()` 或其它非 Manim 计时——scaler 看不到。

### `\remotionFile{}` — `useVideoConfig().durationInFrames` 相对时间

compiler 只 override 顶部导出的 `DURATION_FRAMES` 常量，**不改组件 body**。所以组件里写死 `interpolate(frame, [0, 30], ...)` 会在 1s 处结束，剩下时间冻结。

**写法**：用 `useVideoConfig().durationInFrames` 算 phase 边界：
```tsx
const { durationInFrames: dur } = useVideoConfig();
const kickerOp = interpolate(frame, [0, dur * 0.10], [0, 1], { extrapolateRight: 'clamp' });
const titleOp = interpolate(frame, [dur * 0.10, dur * 0.20], [0, 1], { extrapolateRight: 'clamp' });
const accentOp = interpolate(frame, [dur * 0.85, dur], [0, 1], { extrapolateLeft: 'clamp' });
```
**禁止**：硬编码绝对帧号（`[0, 30]`, `[60, 90]`）。

### `\htmlFile{}` — 短入场 + 持续微动态

compiler **不改 CSS keyframes**。Playwright 录制 `target_duration` 秒整页面；CSS 动画结束之后就是 frozen frame。

**写法**：
1. **入场动画在 1.0-1.5s 内全部结束**（用错位 `animation-delay`：0.2s / 0.4s / 0.6s 这种）。
2. **保留至少一个 element 持续微动态**（缓慢 pulse / 横向 scan / drift）— 长音频时画面有"呼吸感"，不会变成静止图。
3. **禁止排长队的 sequential delays**（`delay: 0s; 4s; 8s; 12s`）——如果 audio 实际 5s，后面的 element 永远不显示。

`scene_html.html.tpl` 的 `.accent-pulse` + `.underline-scan` 是默认的「呼吸 + sheen」骨架。

## 端到端流程

### 步骤 1 · 准备工作目录
```bash
WORK=/tmp/autolecture_$(date +%s)
mkdir -p $WORK/{scenes,figures}
```

最终产出物结构：
```
<work>/
  paper_walkthrough.tex            # 主 tex（或随项目重命名）
  1500_.m4a                        # 原音频（rough/polished 模式）
  1500_.m4a.whisper.json           # Whisper sidecar（rough/polished 模式）
  scenes/
    scene_01_hook.tsx              # Remotion 源码
    scene_02_punch.html            # HTML 源码
    scene_03_collapse.py           # Manim 源码
    ...
  figures/
    cover.png                      # （可选）AI 生图 / 上传素材
  README.md                        # 给用户的"怎么用"说明
```

### 步骤 2 · 获取脚本文字（按模式分支）

**rough / polished 模式**：
```bash
python3 scripts/transcribe.py --audio <user.m4a> --out <work>/<user>.m4a.whisper.json
```
读 [`scripts/transcribe.py`](scripts/transcribe.py) — 用 `whisper.base` 模型加词级时间戳，落 sidecar JSON。

**text 模式**：用户给的文字直接当脚本，跳过转录。

### 步骤 3 · 修转录错字（rough / polished 模式才需要）

读 [`reference/typo-fixes.md`](reference/typo-fixes.md) 拿到常见错字映射（"高撕"→"高斯"，"政策画像"→"正则项"，"答辩"→"答辩" 等），加上**针对本次内容**新发现的：
1. 把转录文字逐句过一遍
2. 凡是看着不通的句子 → 同音字检查（用拼音输入法验证）
3. 把修正映射记到 `<work>/transcript_corrections.md`
4. 后续 headline / 字幕 / 注释一律用修正后版本；**原音频不动**

### 步骤 3.5 · 抽取配套素材（如果有）

读 [`reference/figure-matching.md`](reference/figure-matching.md) — 完整 anchor 规则。

**PDF 论文**：
```bash
python3 scripts/extract_pdf_figures.py --pdf <paper.pdf> --out <work>/figures/
# 出 page-01.png .. page-NN.png (整页 144 DPI) + (best-effort) fig-N.png 单图
```

**GitHub repo**：
```bash
python3 scripts/clone_github_assets.py --repo <url-or-path> --out <work>/figures/ --max-mb 50
# sparse-clone 拉 *.png/.jpg/.svg/.gif + README 截图引用列表写入 <work>/figures/.manifest.json
```

**本地图片夹**：直接 `cp -r` 进 `<work>/figures/`。

### 步骤 3.6 · 把素材 match 到 beat（如果有）

在 transcript 里搜每张图的 anchor 句（图号 / 模块名 / 截图标题 / README 段落）。**每张图至少需要一个 anchor 句证据**写到 `beat_plan.md`，比如：

| 图 | match 到 beat | anchor 证据 |
|---|---|---|
| `fig-3.png` | beat 7 (collapse 段) | "如图 3 所示，所有向量都坍塌到同一个点" |
| `figures/screenshot.png` | beat 12 (UI 介绍段) | "我们打开 settings 页面就能看到" |

没找到 anchor 的图 → 留着不用（**禁止凭感觉塞图**）。

### 步骤 4 · 设计叙事节拍

#### rough / text 模式：
- 让 LLM（或自己）重新组织叙事 — 一个清晰的开头/中间/结尾
- 切成 5-12 个叙事段，每段 30-90 秒
- 每段一句话写清楚"画面应该出现什么"
- 列出对应的 view duration 估计

#### polished 模式：
- 在 Whisper transcript 里搜<strong>锚句</strong>（每段开头特征明显的几个字）
- 用 [`scripts/find_beats.py`](scripts/find_beats.py) 的算法定位每个锚句的 start 时间戳
- 相邻锚句之间 = 一个 view 的 `[start=, end=]` 窗口
- 不重组叙事，按音频自然顺序切

输出：`<work>/beat_plan.md` 形如：
```markdown
| # | 时长 | 内容 | 视觉引擎 | 配套素材 (可选) | 设计要点 |
|---|------|------|----------|-----------------|----------|
| 1 | 0-25s   | 抛出反直觉问题 | Remotion | —                          | 问题文字 typewriter 浮现 + 大问号脉冲 |
| 2 | 25-60s  | 论文标题       | Remotion | figures/page-01.png        | 整页淡入 + 标题区域 zoom-in |
| 3 | 60-90s  | 三大核心数字   | HTML     | —                          | 三柱卡片错位反转 |
| 7 | 180-210s| 表示坍塌       | Manim    | figures/fig-3.png (overlay)| 3D 点云收缩 + 论文图 ken-burns 切换 |
...
```

### 步骤 5 · 为每个 beat 选引擎

读 [`reference/engine-routing.md`](reference/engine-routing.md)。简要规则：

| Beat 内容 | 引擎 |
|----|----|
| 大字 / 数字反转 / 文字打字机 / 抽象动画 | **Remotion** (`.tsx`) |
| 论文标题 / 卡片对比 / 表格 / 流程图 / 引言 | **HTML** (`.html`) |
| 3D 点云 / 数学公式动画 / 几何变换 / 函数图像 | **Manim** (`.py`) |
| **PDF 整页 / repo 截图 + zoom-in / annotate** | **Remotion** ([`templates/scene_image_zoom.tsx.tpl`](templates/scene_image_zoom.tsx.tpl)) — `<Img src='figures/...'>` + interpolated `transform: scale + translate` |
| **多张图 side-by-side / before-after** | **HTML** — `grid-template-columns` 把多张 figure 错位入场 |
| 真人照片 / 上传插画（无动效） | **`\imageFile`** |
| 需要 AI 出原创插画（水彩、卡通、概念图） | **`\image[engine=gemini]`** |

判定原则：
- 优先 HTML（最快、最稳，3-5 秒渲完）
- 涉及数学/3D/几何精度 → Manim
- 需要逐帧精细控制 / 复杂时间轴 → Remotion
- 实在没法靠代码画的（人脸、风景）→ `\image` AI 生图

### 步骤 6 · 手写每个 scene 的源码

参考 [`templates/`](templates/) 里的骨架。每个 scene 独立一个文件，**严格手写**（不调用 LLM 生成代码）。重点：

- **视觉一致性**：全片用同一调色板 [`reference/palette.md`](reference/palette.md)（深底 #0d1117、accent #6ec1e4、warn #ee6c4d、highlight #f4d35e、dim #aab1c0）；同一字体栈（Inter + PingFang SC）
- **Remotion 必须导出**：`Comp` / `FPS` / `WIDTH` / `HEIGHT` / `DURATION_FRAMES` — 看 [`templates/scene_remotion.tsx.tpl`](templates/scene_remotion.tsx.tpl)
- **Manim 类名必须叫 `LectureScene`**（除非显式 `scene=` opt 改），定义 `construct(self)` 方法
- **HTML 不需要外部 CSS** — 用 `<style>` 内联，独立文件
- **每个 scene 时长 ≤ 60 秒**；如果某个 beat > 60s，拆成两个相关 scene 而不是一个超长 scene
- **Manim 复杂场景必须粗算渲染时长** —— 1500 帧 / 40 个 dot / FadeIn 全部 = >300s 渲染会超时。复杂的改用 Remotion DOM 模拟

### 步骤 7 · 组装 paper_walkthrough.tex（或任意项目主 tex）

参考 [`templates/main.tex.tpl`](templates/main.tex.tpl)。模板：

```latex
\title{<项目标题>}
\aspect{16:9}
\style{<风格描述：深色背景、Inter + PingFang SC、accent #6ec1e4 等>}

\begin{videotex}

\begin{view}[title=Scene_01_Hook]
  % rough/text 模式 —— TTS
  \say{<这一段的旁白文字>}
  \remotionFile{scenes/scene_01_hook.tsx}
\end{view}

\begin{view}[title=Scene_02_Card]
  % polished 模式 —— 剪辑原音频
  \audio[start=32.34, end=37.48]{<user_audio>.m4a}
  \htmlFile{scenes/scene_02_card.html}
\end{view}

...

\end{videotex}
```

### 步骤 8 · 写 README

[`templates/README.md.tpl`](templates/README.md.tpl) 是给用户的"怎么用"说明：

```markdown
# AutoLecture 项目包

## 怎么用

1. 上 https://autolecture.ai 新建项目（空白）
2. 把这个目录里所有文件拖进 assets/（也可以直接用 zip 上传功能）
3. 把 `<project>.tex` 内容粘进 main.tex（或者直接 `\input{<project>.tex}`）
4. 点 ▶ Recompile all

## 包含

- `<project>.tex` —— 主脚本
- `scenes/` —— N 个手写的视觉源码（Manim Python / HTML / Remotion TSX）
- `<audio>.m4a` —— 原音频（如果用 polished 模式）
- `<audio>.m4a.whisper.json` —— Whisper 转录（供字幕对齐用）
- `transcript_corrections.md` —— 转录错字修正表（如果有）
- `beat_plan.md` —— 叙事结构 + 引擎路由记录（参考用）

## 设计思路

每个 view 一个独立场景源码，遵循一致的调色板（#0d1117 / #6ec1e4 / #f4d35e / #ee6c4d / #aab1c0）和字体栈（Inter + PingFang SC）。
```

### 步骤 9 · 交付 — 两种路径,让用户选

工作目录做好后,有**两条平等的交付路径**。先问用户(或按线索判断)要哪条:

| 路径 | 适合 | 怎么交付 |
|---|---|---|
| **A · zip 上传**(步骤 9A)| 用户想**自己在网站上改代码** / 偏好网页操作 / agent 没有网络或 API key(如大陆用 Codex)| `package_zip.py` 打个 zip → 用户拖到 <https://autolecture.ai> 上传 → 在 Studio 里自己编辑 + 编译 |
| **B · API 直传**(步骤 9B)| 用户想让 **AI 实时改代码**(在 Claude/Codex 里继续迭代)| `upload_and_compile.py` 走 SDK,一键上传 + 编译 + 下载 mp4 |

判定:用户说"给我个 zip 我自己传 / 我想在网站改" → A;"你直接帮我传上去 / 边跑边调" → B;含糊就**两个都给**(先打 zip,再问要不要顺便 API 直传)。两条路径**都**经 AutoLecture 编译收费(skill 代码免费,任何入口的编译都收费)。

#### 步骤 9A · 打包 zip(用户自己上传)

```bash
python3 scripts/package_zip.py --work <work> --out <work>/autolecture_demo.zip
```

[`scripts/package_zip.py`](scripts/package_zip.py) 会:
- 把 `<work>` 全部内容打到一个 zip(`main.tex` + `scenes/` + 素材)
- 校验关键文件都在(每个 `\manimFile` / `\htmlFile` / `\remotionFile` / `\imageFile` / `\audio` 引用的文件都存在),缺了就 hard-exit
- 输出 zip 路径 + 文件清单

回复用户:zip 路径 + "拖到 autolecture.ai 上传,会自动识别 main.tex、把素材注册好;之后在 Studio 里改代码 / 点 Recompile"。(网站 from-zip 已验证:自动加 `\begin{videotex}` 外壳、注册 assets、`staticFile()` 能拿到上传的 PDF/图。)

#### 步骤 9B · SDK 一键上传 + 编译 + 下载 mp4

前提:

1. 已经 `pip install autolecture`(SDK 仓库:<https://github.com/scao7/autolecture-python>)
2. 已经在 <https://autolecture.ai/account> → 🔑 API Keys 生成 key,并 `export AUTOLECTURE_API_KEY=al_live_...`

执行:

```bash
python3 scripts/upload_and_compile.py <work>
```

[`scripts/upload_and_compile.py`](scripts/upload_and_compile.py) 会:

1. 读取 `<work>` 里的主 tex(优先级 `main.tex` > `index.tex` > `paper_walkthrough.tex` > 第一个根目录 .tex)
2. 在 AutoLecture 创建新项目(项目名 = workdir basename,可用 `--name` 覆盖)
3. 把其余每个文件作为 asset 上传(保留相对路径,`scenes/v1.py` 上传后还是 `scenes/v1.py`)
4. PUT 主 tex 内容到 `/api/v2/.../tex` endpoint(主 tex 是源码不是 asset)
5. 触发 compile,每 2 秒轮询并打印 `[done/total] status now: block#N`
6. 编译成功后流式下载 final mp4 到 `<work>/out.mp4`
7. 打印 Studio URL `https://autolecture.ai/studio?id=...` 让用户在网页里看 / 调

排错:
- 编译失败 → 脚本退出码 1 + stderr 打印 error_log tail。在 Studio 里逐 block 查问题。
- 配额超限(`InsufficientCreditsError` / `RateLimitError`)→ stderr 显示需要的 ✦ + 当前余额。
- 没装 SDK → 提示 `pip install autolecture`。

可选参数:
- `--no-compile` — 只上传,不编译(用户想先在 Studio 里手动调整)
- `--base-url https://dev.autolecture.ai` — 走 dev 后端
- `--poll-interval 5.0` — 拉长轮询周期(省 API 调用,慢点知道进度)

最后回复用户:`out.mp4` 路径 + Studio URL + 简短的"项目在线上了"。

## 关键经验(来自实际跑过的 demo)

1. **不要把 70s+ 的 Manim 单 scene 当作天经地义** — Manim 1000+ 帧 + 40 个 dot + 多个 FadeIn 渲染时间会超 300s 默认 timeout。同样的视觉用 Remotion DOM 模拟（CSS 粒子 + transform），渲染时间 <10s。
2. **修转录错字非常重要** — Whisper 把"高斯分布"转成"高撕分布"、"正则项"转成"政策画像"，直接用会让 headline 变成乱码。
3. **每个 scene 独立设计 ≠ 不一致** — 用统一调色板 + 字体 + 动画语法（fade-up / pop / strike）就有视觉一致性。
4. **HTML 是默认首选** — 渲染快、稳、灵活。Manim 只在数学/几何精度真的重要的时候用。
5. **Remotion 适合大数字 / 时间轴动画** — 比如 "48× 加速" 反转、L2 距离尖峰图、6→1 计数器。
6. **scene 文件命名**：`scene_NN_label.<ext>`，按时间顺序编号，便于阅读。
7. **`\imageFile` ≠ `\image`** — `\imageFile` 是上传素材（mirror manimFile）；`\image` 是 AI 生图。两个一起用：固定背景用 `\imageFile`，特殊插画用 `\image`。

## 参考资料

- [`reference/dsl-cheatsheet.md`](reference/dsl-cheatsheet.md) — VideoTeX 语法速查
- [`reference/typo-fixes.md`](reference/typo-fixes.md) — 中文 Whisper 常见错字
- [`reference/palette.md`](reference/palette.md) — 视觉调色板
- [`reference/engine-routing.md`](reference/engine-routing.md) — 引擎选择决策树
- [`reference/figure-matching.md`](reference/figure-matching.md) — PDF / repo 图素材的 anchor 匹配规则
- [`reference/borrowed-techniques.md`](reference/borrowed-techniques.md) — 6 个可借鉴的动效模板(无限滚动 / 旋转盘 / 爆炸组装 / 聚光灯 / 打字机 / 程序波动),写新 scene 前先翻一下。归纳自 vibe-motion/skills,只学技法,不抄代码
- [`reference/pdf-showcase.md`](reference/pdf-showcase.md) — PDF 两种流程(讲解知识 vs 展示原件)+ react-pdf 文字高亮怎么对准
- [`templates/`](templates/) — Remotion / HTML / Manim 骨架 + scene_image_zoom Ken Burns 模板
- [`templates/scene_pdf_highlight.tsx.tpl`](templates/scene_pdf_highlight.tsx.tpl) — Flow B:渲染 PDF 真页 + zoom + 旁白驱动文字高亮(react-pdf)
- [`templates/scene_pdf_focus.tsx.tpl`](templates/scene_pdf_focus.tsx.tpl) — Flow B:PDF 真页聚焦/滚动到某区域(react-pdf)
- [`templates/scene_overlay.tsx.tpl`](templates/scene_overlay.tsx.tpl) — 实拍结合:透明动效叠加到实拍视频(`\remotionFile[over=clip.mp4]{...}`,音频叠加)
- [`scripts/transcribe.py`](scripts/transcribe.py) — Whisper 词级转录
- [`scripts/find_beats.py`](scripts/find_beats.py) — anchor-phrase 定位时间戳
- [`scripts/extract_pdf_figures.py`](scripts/extract_pdf_figures.py) — PDF 页 + 图抽取（pdftoppm + pdfplumber）
- [`scripts/clone_github_assets.py`](scripts/clone_github_assets.py) — repo 图片 sparse-clone + manifest
- [`scripts/package_zip.py`](scripts/package_zip.py) — 路径 A:校验 + 打包成 zip,用户自己上传到网站改代码
- [`scripts/upload_and_compile.py`](scripts/upload_and_compile.py) — 路径 B:用 `autolecture` SDK 一键上传+编译+下载 mp4(AI 实时迭代)
- AutoLecture 主项目:<https://github.com/scao7/autolecture>
- AutoLecture Python SDK:<https://github.com/scao7/autolecture-python>
- VideoTeX 在线文档:<https://autolecture.ai/docs/dsl>
