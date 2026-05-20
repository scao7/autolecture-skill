# PDF 视频化 — 两种流程

用户给一个 PDF（通常是论文），有**两种**完全不同的诉求。先判断是哪一种，再选工具。

| 流程 | 用户想要 | 怎么做 | 视觉素材 |
|---|---|---|---|
| **A · 讲解知识** | "把这篇论文讲明白" | LLM 读 PDF → 重写成口播脚本 → 抽 figure 配画面 | `extract_pdf_figures.py` 抽出的 figure crop + 手写 scene |
| **B · 展示 PDF** | "在视频里展示这篇 PDF，翻页 / 放大 / 高亮某句话" | 直接在画面里渲染 PDF 真页，zoom / scroll / highlight | `react-pdf` 渲染真页（不预栅格化）|

判定规则：
- "帮我把这篇论文做成讲解 / 科普" → **A**（默认）
- "在视频里**展示**这篇 PDF" / "翻页" / "放大原文某段" / "高亮这句话" / "像翻杂志一样" → **B**
- 含糊 → 问一句："你想让我**讲解里面的知识**（配动画），还是想**在视频里展示这份 PDF 原件**（翻页+放大+高亮）？"

两种可以混用：A 为主，中间插一两个 B 的"原文高亮"镜头强调关键句。

---

## Flow A · 讲解知识（已有流程）

不变。见 [`figure-matching.md`](figure-matching.md)：抽 figure → 按音频锚句 match → Ken Burns / annotate。PDF 只是**素材来源**，最终画面是重新设计的 scene，不出现 PDF 原件。

---

## Flow B · 展示 PDF（react-pdf，新）

最终画面里**出现 PDF 真页**。靠 AutoLecture Remotion bundle 里的 `react-pdf`（pdfjs）直接渲染——矢量清晰，任意放大不糊，无需预先栅格化成 PNG。

### 前提
- PDF 作为**项目 asset 上传**（和音频/图一样）。scene 里 `staticFile('paper.pdf')` 就能拿到（AutoLecture 编译时把项目 assets/ 挂成 bundle 的 public/）。
- 不需要跑 `extract_pdf_figures.py`——react-pdf 直接读原 PDF。

### 模板
| 模板 | 效果 | 关键参数 |
|---|---|---|
| [`scene_pdf_highlight.tsx.tpl`](../templates/scene_pdf_highlight.tsx.tpl) | 显示某页 + zoom 推近 + **高亮旁白正在讲的那句话** | `TARGET`（旁白引用的短语）、`ZOOM_END` |
| [`scene_pdf_focus.tsx.tpl`](../templates/scene_pdf_focus.tsx.tpl) | 显示某页 + 聚焦/滚动到某区域（无高亮框）| `FOCUS_PHRASE` 或 `FOCUS_FX/FY`、`SCROLL` |

### 高亮怎么对准（核心）
**不要硬编码坐标。** 模板用 pdfjs 的 text layer 自动定位：
1. `\say{}` 里旁白这一拍在讲哪句话 → 把那句话（或其中一个独特短语）填进 `TARGET`。
2. scene 里 `page.getTextContent()` 找到包含 `TARGET` 的 text item，取 `transform` → `viewport.convertToViewportPoint()` 换成像素 bbox。
3. 高亮框画在那个 bbox 上；zoom 的 `transform-origin` 设成 bbox 中心 → 镜头自动推到那句话。

短语选择建议：挑该行里**独特、好匹配**的几个词（避免 "the"/"of" 这种到处都是的词）。高亮粒度是**整行/整个 text span**（pdfjs 按 span 给文字）——视觉上"高亮这一句"已经够干净；要精确到词需要按字符比例估算，proportional 字体下不准，默认别做。

### audio-first
两个模板的 `DURATION_FRAMES` 都会被 compiler 重写成对应 `\say{}` 的真实时长——zoom 永远在旁白讲完时刚好推到位。所以写动画时用"自然时长比例"（`interpolate(frame, [0, durationInFrames-1], ...)`），别假设固定帧数。

### 在 main.tex 里
```latex
\begin{view}
  \say{论文里这句话最关键 —— 基率其实非常重要。}
  \remotionFile{scenes/pdf_highlight_baserate.tsx}
\end{view}
```
（scene 文件就是填好占位符的 `scene_pdf_highlight.tsx.tpl`。）

### 成本
react-pdf scene 是手写 `\remotionFile{}` → 命中缓存 → 重编译几乎 0 成本（和其它 `\manimFile`/`\htmlFile` 一样）。比 `\remotion{prompt}` LLM 生成便宜得多。

---

## 致谢
Flow B 的 scene 语法（focus zoom / scroll / 高亮）借鉴自
[DangJin/pdf2video](https://github.com/DangJin/pdf2video)（MIT）——pdfjs
worker 配置、`delayRender`/`continueRender` 异步加载、focus/scroll 动效
都参考了它。我们的实现是按 AutoLecture 的 `\remotionFile{}` + audio-first
约定重写的，并把 pdf2video 的"只显示作者已有标注"扩展成**旁白驱动的任意文字高亮**。
