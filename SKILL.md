---
name: autolecture-skill
description: 把用户素材端到端做成可在 AutoLecture (https://autolecture.ai) 编译出片的项目。入口先问用户要做哪种视频,再分流到对应 workflow：纯文字稿→生成讲解; 录音/播客→转录配画面; PDF 论文→讲解(抽figure) 或 展示原件(react-pdf真页+zoom+定位高亮,借鉴 pdf2video); 实拍视频→叠加透明动效(over=) 或 录屏+头像Tella式画中画。所有视觉手写 \\manimFile/\\htmlFile/\\remotionFile 源码(不走 LLM 提示词),AI 仅用于 \\image[engine=gemini]{} 生图。交付两条路径：打包 zip 让用户上传, 或用 autolecture Python SDK 一键上传+编译+下载 mp4。目标：用户给素材 → 跑完 → out.mp4 + Studio URL。
---

# autolecture-skill

把用户的素材变成可立即在 AutoLecture 里点 ▶ Recompile 出片的项目包。
这个 SKILL.md 是**路由入口** —— 先判断用户要做哪种视频，再打开对应的
[`workflows/`](workflows/) playbook 执行。

## 核心：一切都是音频驱动

和别的 skill 不一样 —— **AutoLecture 项目永远是音频驱动**：旁白 / 人声是整片的
时间轴脊柱，画面只是配合音频的节奏与含义出现，绝不反过来。无论入口是哪种：
- **简单指令 / 文字** → 先写口播稿**给用户定稿** → TTS → 按每段口播的时间和含义配画面。
- **录音** → 转录 + 修错字 → 判断「保留原声直接剪」还是「voice clone 重合成」→ 按音频切分配画面。
- **视频** → **不做 TTS**，直接用视频自带音频分析、切分 → 叠加特效 或 剪辑结合。

所以每条 workflow 的第一步都是「确定音频时间轴」，第二步才是「给每段配画面」。

## 何时触发

用户说「做个 autolecture 视频 / demo」「我录了段口播做成视频」「我有篇稿子 / 论文 / 项目想做讲解」「剪我这段播客配画面」「在我这段实拍上加点动效」，或直接丢来音频 / 文字 / PDF / 视频文件。

---

## 入口：先确定走哪个 workflow

**第一步永远是搞清楚用户手上有什么主输入**（看用户给的文件 + 说的话；不明确就用 AskUserQuestion 问）。然后**读对应的 workflow 文件**并照它执行：

| 用户的主输入 / 诉求 | workflow | 一句话 |
|---|---|---|
| 只有**文字 / 一句指令 / 选题**，无录音 | [`workflows/text-to-lecture.md`](workflows/text-to-lecture.md) | **先写口播稿给用户定稿** → TTS → 按口播配画面 |
| 一段**录音 / 播客**（mp3/wav/m4a） | [`workflows/audio-upload.md`](workflows/audio-upload.md) | 转录 + 修错字 → 保留原声直接剪 或 voice clone 重合成 |
| 一份 **PDF 论文** | [`workflows/pdf-paper.md`](workflows/pdf-paper.md) | A 讲解知识(抽 figure) 或 B 展示原件(真页 + zoom + 定位高亮) |
| 一段**实拍视频** / **录屏 + 头像** | [`workflows/video.md`](workflows/video.md) | 不做 TTS,用原音频切分 → 叠加特效(毛玻璃) / 剪辑结合 / Tella 录屏画中画 |

要问就用 AskUserQuestion，选项就是上面四类：「① 我给文字 / 选题 ② 我录了音频 / 播客 ③ 我有 PDF 论文 ④ 我有实拍视频」。

**可叠加**：主输入选一个 workflow 当主线，其它素材作配套 ——
- 音频 / 文字 + PDF figure / GitHub repo / 本地图 → 主 workflow 里按 [`reference/figure-matching.md`](reference/figure-matching.md) match 进画面。
- 音频 / 文字 + 想在画面里**展示** PDF 原件 → 叠 [`workflows/pdf-paper.md`](workflows/pdf-paper.md) 的 Flow B 镜头。
- 任意 + 实拍片段 → 那几镜用 [`workflows/video.md`](workflows/video.md) 的 `over=` 叠加 / 剪辑结合。

所有 workflow 最后都汇到同一个交付步骤：[`workflows/_delivery.md`](workflows/_delivery.md)。

---

## HARD BANS（所有 workflow 通用 —— 任何时候都别破）

1. **禁止用 LLM 提示词宏**：`\manim{prompt}` / `\html{prompt}` / `\remotion{prompt}` / `\show{}` 一律不准。所有视觉必须是 `\manimFile{path.py}` / `\htmlFile{path.html}` / `\remotionFile{path.tsx}` / `\imageFile{path.png}` / `\image[engine=gemini]{prompt}`（AI 生图允许）。理由：LLM 出代码不稳定，编译失败率高；手写源码 + 缓存命中 = 几秒出片。
2. **禁止模板偷懒**：每个 scene 的视觉**必须**按该 view 内容定制设计，不能同一模板填不同文字。
3. **禁止漏修转录错字**：中文 Whisper 大量同音字错误，必须先建[修正映射表](reference/typo-fixes.md)再用于 headline。**音频内容不动**，错字只影响视觉文字。
4. **禁止 silent fallback —— 质量优先**：依赖缺失 / 抽取失败 / 素材损坏 → **立即报错给用户**，不输出降级产物。`autolecture_no_silent_fallback` 是这个 skill 的生命线。
5. **禁止给 `examples/` 提交 AI 生成的样例**（`autolecture_few_shot_human_curated` 规则）。
6. **禁止裸铺图**：从 PDF / repo 抽出的图必须包装至少一种动态（zoom / crop / annotate / side-by-side / scroll）。
7. **禁止从 repo 拉超过 50MB 素材**：`clone_github_assets.py` sparse-checkout 只拉图片，超阈值跳过 + 警告。
8. **图素材 match 必须有锚句证据**：每张图标到哪个 view，要在 `beat_plan.md` 写明 transcript 里触发匹配的原句（防凭感觉塞图）。
9. **禁止默认抽 PDF 整页栅格**：`extract_pdf_figures.py` 默认 figures-only；只有显式做「文字 highlight / 公式 zoom / 整页 scroll」才用 `--with-pages`。
10. **音频时长驱动视觉**：绝不反向假设视觉时长决定 scene 时长。三引擎 audio-first 写法见 [`reference/audio-first.md`](reference/audio-first.md) —— 写任何 scene 前必读。
11. **禁止预剪 / 预拼素材 —— 剪辑全用 .tex 表达**：**绝不**在外面用 ffmpeg / 剪辑软件把原始素材切片、拼接、重排、变速、加转场后再丢进项目。素材**原片整个**作 asset，所有剪辑都用 VideoTeX 声明：
    - **选段 / 切镜** → `\video[start=, end=]{原片.mp4}` / `\audio[start=, end=]{原片.mp4}`（编译器从原片取那个时间窗,原片不动）。
    - **排序 / 拼接** → view 的先后顺序（manifest 按序 concat）。
    - **转场** → `\fade` / view 边界，不要把转场烧进素材。

    理由：P1 **LaTeX 是唯一真相**、P2 **没有 GUI 漂移** —— 剪辑是 .tex 里**可改、可预览、非破坏性**的字符（预览即导出）。预剪素材 = 把剪辑决策烧死在文件里、绕过 .tex，违反整套架构。（唯一例外:原片实在过大时可先粗剪到一个工作区间当 asset,但**精剪仍写在 .tex 里**。）

---

## 通用建筑块（被所有 workflow 引用）

- **audio-first timing**（三引擎写法）→ [`reference/audio-first.md`](reference/audio-first.md)
- **引擎选择决策树**（哪种内容用 Manim / HTML / Remotion / `\image`）→ [`reference/engine-routing.md`](reference/engine-routing.md)
- **视觉调色板 + 字体栈**（全片一致）— 两套**二选一**,一个项目内只用一套:
  - [`reference/palette.md`](reference/palette.md) · **editorial dark**（深底 + 海洋蓝）,默认。适合个人 vlog / 论文讲解 / 内容是主角的 editorial 叙事。
  - [`reference/brand-style.md`](reference/brand-style.md) · **AutoLecture brand**（cream + navy + tan 渐变,跟 [autolecture.ai](https://autolecture.ai) 网站 / Studio / watermark 同一调子）。挂 AutoLecture 招牌时用——官方 demo / teaser / 教程 / 上首页 showcase / 给内测用户的功能片。
- **VideoTeX 语法速查** → [`reference/dsl-cheatsheet.md`](reference/dsl-cheatsheet.md)（在线文档 <https://autolecture.ai/docs/dsl>）
- **配套素材 anchor 匹配**（PDF figure / repo 截图 / 本地图）→ [`reference/figure-matching.md`](reference/figure-matching.md)
- **可借鉴动效技法**（写新 scene 前翻一下）→ [`reference/borrowed-techniques.md`](reference/borrowed-techniques.md)
- **交付**（zip 上传 / SDK 直传）→ [`workflows/_delivery.md`](workflows/_delivery.md)

工作目录与产出物结构（所有 workflow 共用）：
```
<work>/
  main.tex                     # 主 tex（可随项目重命名）
  <audio>.m4a(.whisper.json)   # 录音模式
  paper.pdf                    # PDF 模式（作 asset）
  clip.mp4                     # 实拍模式（作 asset）
  scenes/  scene_NN_label.{tsx,html,py}   # 手写视觉源码
  figures/                     # 抽出的 figure / AI 生图 / 上传素材
  beat_plan.md                 # 叙事结构 + 引擎路由 + anchor 证据
  transcript_corrections.md    # 转录错字修正表（录音模式）
  README.md                    # 给用户的「怎么用」
```

---

## 参考资料

### workflows/（按主输入分流）
- [`workflows/text-to-lecture.md`](workflows/text-to-lecture.md) — 纯文字 → 生成讲解
- [`workflows/audio-upload.md`](workflows/audio-upload.md) — 录音 / 播客（rough / polished）
- [`workflows/pdf-paper.md`](workflows/pdf-paper.md) — PDF 论文（A 讲解 / B 展示原件）
- [`workflows/video.md`](workflows/video.md) — 实拍视频（叠加毛玻璃特效 / 剪辑结合，不做 TTS）
- [`workflows/_delivery.md`](workflows/_delivery.md) — 共用交付（zip / SDK）

### reference/
- [`reference/audio-first.md`](reference/audio-first.md) — 三引擎 audio-first 写法（铁律）
- [`reference/engine-routing.md`](reference/engine-routing.md) — 引擎选择决策树
- [`reference/palette.md`](reference/palette.md) — editorial dark 调色板（#0d1117 / #6ec1e4 / #f4d35e / #ee6c4d / #aab1c0）
- [`reference/brand-style.md`](reference/brand-style.md) — AutoLecture brand-light 调色板（cream #fefcf6 / navy #234976 / tan #d9b47b 渐变,镜像 styles.css）
- [`reference/dsl-cheatsheet.md`](reference/dsl-cheatsheet.md) — VideoTeX 语法速查
- [`reference/figure-matching.md`](reference/figure-matching.md) — 配套素材 anchor 匹配
- [`reference/pdf-showcase.md`](reference/pdf-showcase.md) — PDF 两种流程 + 4 种 react-pdf 镜头
- [`reference/typo-fixes.md`](reference/typo-fixes.md) — 中文 Whisper 常见错字
- [`reference/borrowed-techniques.md`](reference/borrowed-techniques.md) — 6 个可借鉴动效技法

### templates/
- [`templates/main.tex.tpl`](templates/main.tex.tpl) · [`templates/README.md.tpl`](templates/README.md.tpl)
- [`templates/scene_remotion.tsx.tpl`](templates/scene_remotion.tsx.tpl) · [`templates/scene_html.html.tpl`](templates/scene_html.html.tpl) · [`templates/scene_manim.py.tpl`](templates/scene_manim.py.tpl)
- [`templates/scene_image_zoom.tsx.tpl`](templates/scene_image_zoom.tsx.tpl) — figure Ken Burns
- [`templates/scene_overlay.tsx.tpl`](templates/scene_overlay.tsx.tpl) — 实拍结合透明叠加(editorial dark · 黑玻璃)
- [`templates/scene_brand_lower_third.tsx.tpl`](templates/scene_brand_lower_third.tsx.tpl) — 实拍结合透明叠加(AutoLecture brand · paper 玻璃 + navy→tan 渐变)
- [`templates/scene_screencast_pip.tsx.tpl`](templates/scene_screencast_pip.tsx.tpl) — Tella 录屏 + 头像全屏↔小窗 morph
- PDF 真页镜头（Flow B）：[`scene_pdf_overview`](templates/scene_pdf_overview.tsx.tpl) · [`scene_pdf_switch`](templates/scene_pdf_switch.tsx.tpl) · [`scene_pdf_focus`](templates/scene_pdf_focus.tsx.tpl) · [`scene_pdf_highlight`](templates/scene_pdf_highlight.tsx.tpl)

### scripts/
- [`scripts/transcribe.py`](scripts/transcribe.py) — Whisper 词级转录
- [`scripts/find_beats.py`](scripts/find_beats.py) — anchor-phrase 定位时间戳
- [`scripts/extract_pdf_figures.py`](scripts/extract_pdf_figures.py) — PDF figure 抽取（默认 figures-only）
- [`scripts/clone_github_assets.py`](scripts/clone_github_assets.py) — repo 图片 sparse-clone
- [`scripts/package_zip.py`](scripts/package_zip.py) — 交付 A：校验 + 打包 zip
- [`scripts/upload_and_compile.py`](scripts/upload_and_compile.py) — 交付 B：SDK 一键上传 + 编译 + 下载 mp4

### 关键经验（实际跑过的 demo）
1. **不要把 70s+ 的 Manim 单 scene 当作天经地义** —— 1000+ 帧 + 40 dot + 多 FadeIn 渲染超 300s timeout；同样视觉用 Remotion DOM 模拟（CSS 粒子 + transform）<10s。
2. **修转录错字非常重要** —— 「高斯」→「高撕」、「正则项」→「政策画像」直接用会让 headline 乱码。
3. **每个 scene 独立设计 ≠ 不一致** —— 统一调色板 + 字体 + 动画语法（fade-up / pop / strike）就有一致性。
4. **HTML 是默认首选** —— 快、稳、灵活；Manim 只在数学/几何精度真重要时用；Remotion 适合大数字 / 时间轴。
5. **`\imageFile` ≠ `\image`** —— 前者是上传素材，后者是 AI 生图；可一起用（固定背景 `\imageFile`，特殊插画 `\image`）。

### 上游
- 主项目 <https://github.com/scao7/autolecture> · SDK <https://github.com/scao7/autolecture-python> · DSL 文档 <https://autolecture.ai/docs/dsl>
