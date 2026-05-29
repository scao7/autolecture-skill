# Workflow · 用户提供 PDF 论文 → 讲解视频

**入口**：用户给一份 PDF（通常是论文 / arxiv 链接 / .pdf 文件）。
PDF 有**两种完全不同的诉求**，先判断再动手（详见 [`../reference/pdf-showcase.md`](../reference/pdf-showcase.md)）：

| 流程 | 用户想要 | 怎么做 | PDF 出镜? |
|---|---|---|---|
| **A · 讲解知识**（默认）| "把这篇论文讲明白" | LLM 读 PDF → 口播脚本 → 抽 figure 配画面 | ✗ 只当素材源，画面是重新设计的 scene |
| **B · 展示 PDF**（本流程重点）| "在视频里**展示**这份 PDF —— 翻页 / 放大 / 高亮某句" | `react-pdf` 直接渲染真页 + zoom / scroll / 高亮 | ✓ 真页出镜 |

判定：「讲解 / 科普」→ A；「展示原件 / 翻页 / 放大原文 / 高亮这句 / 像翻杂志」→ B；含糊就问一句。**两者常混用**（A 为主，插 B 的原文高亮镜头强调关键句）。

> 旁白哪来？PDF 没有自带旁白 —— 要么 LLM 据 PDF 写口播（`\say{}` TTS），要么用户另给录音（叠加 [`audio-upload.md`](audio-upload.md)）。先确认旁白来源。

---

## 通用步骤

### 0 · 用 SKILL.md 入口已确认的 mode

> **`$mode` 已在 SKILL.md 入口 ② 定下**。

如果旁白要走 TTS(LLM 写 PDF 讲解稿),**voice clone 决策**同 audio-upload / text-to-lecture——dynamic 查 `Client().get_voice_sample()`,static 用 `AskUserQuestion` 问用户。如果旁白用用户另给的录音(叠加 audio-upload workflow),则按那条 workflow 的 step 0 处理。

详细见 [`../reference/runtime-modes.md`](../reference/runtime-modes.md)。

### 1 · 准备工作目录
```bash
WORK=/tmp/autolecture_$(date +%s); mkdir -p $WORK/{scenes,figures}
```
PDF 始终作为**项目 asset** 放进 `<work>/`（Flow B 的 scene 靠 `staticFile('paper.pdf')` 拿到它）。

---

## Flow A · 讲解知识（抽 figure 当素材）

1. LLM 读 PDF → 写口播脚本（清晰的开头/中间/结尾，5–12 段）。
2. 抽图：
   ```bash
   python3 scripts/extract_pdf_figures.py --pdf <paper.pdf> --out <work>/figures/
   # 默认 figures-only：fig-1.png .. fig-N.png + manifest（含 caption）
   # 要整页（做文字 highlight / 公式 zoom / 整页 scroll）才加 --with-pages（HARD BAN #9）
   ```
3. 按音频锚句 match 图（「图 N / Figure N / caption 关键词」→ 对应 fig）。**每张图要有 anchor 句证据**写进 `beat_plan.md`（HARD BAN #8）。
4. 抽到的图**不许裸铺**（HARD BAN #6）—— 至少包一种动态：Ken Burns（[`../templates/scene_image_zoom.tsx.tpl`](../templates/scene_image_zoom.tsx.tpl)）/ crop-reveal / annotate / side-by-side。规则见 [`../reference/figure-matching.md`](../reference/figure-matching.md)。

→ 之后就是普通的「选引擎 + 手写 scene + 组 tex」，和 [`text-to-lecture.md`](text-to-lecture.md) 步骤 3–6 一样。

---

## Flow B · 展示 PDF（react-pdf 真页，pdf2video 镜头语言）

**最终画面里出现 PDF 真页**，靠 AutoLecture Remotion bundle 内置的 `react-pdf`（pdfjs）矢量渲染 —— 任意放大不糊，**不预栅格化、不跑** `extract_pdf_figures.py`。

### 镜头语言（4 种 scene，每个 = 一拍旁白）
完整说明 + 关键参数见 [`../reference/pdf-showcase.md`](../reference/pdf-showcase.md)。

| scene 模板 | 旁白这一拍在做什么 |
|---|---|
| [`scene_pdf_overview`](../templates/scene_pdf_overview.tsx.tpl) | "这篇论文我们快速过一遍" —— 几页扇形铺开建立镜 |
| [`scene_pdf_switch`](../templates/scene_pdf_switch.tsx.tpl) | "翻到下一页 / 实验那页" —— 页 A 滑动到页 B |
| [`scene_pdf_focus`](../templates/scene_pdf_focus.tsx.tpl) | "我们看这一块" —— 推近 / 滚动到某区域 |
| [`scene_pdf_highlight`](../templates/scene_pdf_highlight.tsx.tpl) | "重点是这句话" —— 推近 + 高亮旁白正引用的那句 |

典型编排：`overview`（开场）→ `switch`（翻到目标页）→ `focus`（推到目标区域）→ `highlight`（钉死关键句）。按旁白需要挑，不必每种都用。

### 「定位」怎么对准（核心 —— 这是用户要的「渲染 + 定位」）
**绝不硬编码坐标。** 把旁白这一拍引用的短语填进模板的 `TARGET` / `FOCUS_PHRASE`，模板用 pdfjs 的 text layer 自动定位 bbox，再把 zoom 的 `transform-origin` 推到那句话：
1. `\say{}` 这一拍讲哪句 → 挑该句里**独特好匹配**的几个词（避开 "the"/"of"）填进占位符。
2. scene 里 `page.getTextContent()` 找含该短语的 text item → `viewport.convertToViewportPoint()` 换像素 bbox。
3. 高亮框画在 bbox 上，zoom 推到 bbox 中心 —— 旁白讲完时镜头刚好到位。

### 必带细节
- **PDF 当 asset 上传**；scene 里 `staticFile('paper.pdf')`。
- **audio-first**：`DURATION_FRAMES` 会被 compiler 重写成 `\say{}` 真实时长 —— 动画用 `durationInFrames` 比例，别假设固定帧数（见 [`../reference/audio-first.md`](../reference/audio-first.md)）。
- **CJK / 数学 / subset 字体**：`<Document options={{cMapUrl, cMapPacked}}>` 一律带上，否则字变空白（switch/overview 模板已内置 `PDF_OPTS`）。

### 在 main.tex 里
```latex
\begin{view}
  \say{这篇论文我们快速过一遍。}
  \remotionFile{scenes/pdf_overview.tsx}
\end{view}
\begin{view}
  \say{论文里这句话最关键 —— 基率其实非常重要。}
  \remotionFile{scenes/pdf_highlight_baserate.tsx}   % TARGET 填「基率」
\end{view}
```

### 致谢
Flow B 镜头语言（overview/switch/focus/highlight、pdfjs text-layer 定位、cMap）借鉴自 [DangJin/pdf2video](https://github.com/DangJin/pdf2video)（MIT），按 AutoLecture 的 `\remotionFile{}` + audio-first 约定重写，并把它的「只显示作者已有标注」扩展成**旁白驱动的任意文字高亮 / 定位**。

---

## README + 交付
PDF 列入包含项（Flow B 需要它作 asset）。然后 → **交付：见 [`_delivery.md`](_delivery.md)**。
