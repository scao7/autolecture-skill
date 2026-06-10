---
name: autolecture-skill
version: 0.9.0
description: 把用户素材端到端做成可在 AutoLecture (https://autolecture.ai) 编译出片的项目。入口先问用户要做哪种视频,再分流到对应 workflow：纯文字稿→生成讲解; 录音/播客→转录配画面; PDF 论文→讲解(抽figure) 或 展示原件(react-pdf真页+zoom+定位高亮,借鉴 pdf2video); 实拍视频→叠加透明动效(over=) 或 录屏+头像Tella式画中画(录制产出 screen/camera 两条原始轨,画中画用模板编排可后期调); 参考视频→视觉复刻(抽帧串读动效照着写scene)。所有视觉手写 \\manimFile/\\htmlFile/\\remotionFile 源码(不走 LLM 提示词),AI 仅用于 \\image[engine=gemini]{} 生图。启动先看有没有 autolecture MCP 工具(连了 mcp.autolecture.ai/mcp 连接器)：有就 mcp 模式直接云端建项目+编译+看帧；没有就问用户用 MCP 还是只产 zip 自己上传(claude.ai 网页端走 zip)。交付两条路径：有 MCP 工具就 MCP 连接器直驱云端编译,否则打包 zip 让用户上传。目标：用户给素材 → 跑完 → out.mp4 + Studio URL。
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

## 入口:**开场先定两件事**(一次问到位,workflow 内部不再追问)

### 入口 ① · 运行模式? → 先看有没有 MCP(**workflow 跑之前必定**)

**skill 一启动,第一件事是检查你当前有没有 autolecture 的 MCP 工具** —— 连上 `mcp.autolecture.ai/mcp` 连接器后,工具列表里会出现 `create_project` / `write_file` / `edit_file` / `add_asset` / `compile` / `get_status` / `fetch_frame` 这些(前缀视客户端而定,如 `autolecture:compile`)。这是 Claude 自己就能看见的事实,不用跑脚本。

- **有 MCP 工具** → **mcp 模式**(首选)。Claude 直接用这些工具在云端建项目、写 `main.tex` + scene 文件、上传素材、编译、拉渲出的帧看效果 —— 全程不落本地 zip,一条龙做完,编译挂了能自己 `fetch_frame` 看帧调。
  **连上后先调一次 `server_info` 做版本对账**：① 返回的 `skill_version_current` 比本 SKILL.md 头部的 `version` 新 → 告诉用户「skill 有新版,跑 `npx skills add scao7/autolecture-skill` 更新(claude.ai 重传 zip)」,然后照常继续——不阻塞本次任务;② 返回的 `dsl_spec_sha` 和本地 `harness/spec/dsl.json` 对不上时,语法以 `get_dsl_spec` 拉到的 **live spec 为准**(bundled dsl.json 只是离线 fallback)。
  **起步可走模板**:`list_gallery_templates` → 看中哪个就 `get_template_card(slug)` 读填法 → `use_gallery_template(slug)` 克隆成新项目,在它基础上替换占位,比从零写快得多(模板都是编译验证过的真项目)。
- **没有 MCP 工具** → 用 `AskUserQuestion` 问用户,二选一:

  | 选项 | 走哪条 |
  |---|---|
  | **① 用 MCP(推荐)** —— Claude 直接帮你在云端建项目 + 编译 + 看效果,做完给 Studio 链接 | 引导连接器:在你的客户端(Claude.ai / Cursor / Claude Code)Settings → Connectors → Add → 粘 `https://mcp.autolecture.ai/mcp` → 浏览器点批准(OAuth)。连好后让工具刷新 / 重开对话,再启动 skill → 进 **mcp 模式** |
  | **② 给我 zip,我自己上传** —— 不连任何东西,适合 claude.ai 网页端 / 不想授权的用户 | **zip 模式**:Claude 产出项目 zip,你拖到 [autolecture.ai](https://autolecture.ai) 上传(网页自动识别 main.tex + 注册素材) |

定好模式后 **workflow 内部不再问** —— 每个 workflow 的 step 0 直接照 `mcp / zip` 分支。两种模式每个动作怎么做,对照 [`reference/runtime-modes.md`](reference/runtime-modes.md)。

### 入口 ② · 主输入是什么类型? → 选 workflow

**搞清楚用户手上有什么主输入**（看用户给的文件 + 说的话；不明确就用 AskUserQuestion 问）。然后**读对应的 workflow 文件**并照它执行：

| 用户的主输入 / 诉求 | workflow | 一句话 |
|---|---|---|
| 给一个**参考视频**要"照这个风格做"（YouTube 链接/文件/项目资产） | [`workflows/replicate-style.md`](workflows/replicate-style.md) | 抽帧串读动效 → 手写 scene 复刻视觉语言（YouTube 仅限 Claude Code 本地） |
| 只有**文字 / 一句指令 / 选题**，无录音 | [`workflows/text-to-lecture.md`](workflows/text-to-lecture.md) | **先写口播稿给用户定稿** → TTS → 按口播配画面 |
| 一段**录音 / 播客**（mp3/wav/m4a） | [`workflows/audio-upload.md`](workflows/audio-upload.md) | 转录 + 修错字 → 保留原声直接剪 或 voice clone 重合成 |
| 一份 **PDF 论文** | [`workflows/pdf-paper.md`](workflows/pdf-paper.md) | A 讲解知识(抽 figure) 或 B 展示原件(真页 + zoom + 定位高亮) |
| 一段**实拍视频** / **录屏 + 头像** | [`workflows/video.md`](workflows/video.md) | 不做 TTS,用原音频切分 → 叠加特效(毛玻璃) / 剪辑结合 / Tella 录屏画中画 |

要问就用 AskUserQuestion，选项就是上面五类：「① 我给文字 / 选题 ② 我录了音频 / 播客 ③ 我有 PDF 论文 ④ 我有实拍视频 ⑤ 我有参考视频要照着做」。

**可叠加**：主输入选一个 workflow 当主线，其它素材作配套 ——
- 音频 / 文字 + PDF figure / GitHub repo / 本地图 → 主 workflow 里按 [`reference/figure-matching.md`](reference/figure-matching.md) match 进画面。
- 音频 / 文字 + 想在画面里**展示** PDF 原件 → 叠 [`workflows/pdf-paper.md`](workflows/pdf-paper.md) 的 Flow B 镜头。
- 任意 + 实拍片段 → 那几镜用 [`workflows/video.md`](workflows/video.md) 的 `over=` 叠加 / 剪辑结合。

### 入口 ③ · 然后照常推进

模式 + 主输入定好后,就是正常视频流程 —— workflow 里依次跟用户确认:**要做什么**(选题 / 范围)、**手上的素材**(主输入 + 配套 figure / repo / 实拍)、**想要的视觉风格**(调色板二选一:editorial dark 还是 AutoLecture brand)。然后写口播稿 → 配画面 → 交付。

---

所有 workflow 最后都汇到同一个交付步骤：[`workflows/_delivery.md`](workflows/_delivery.md)。

---

## HARD BANS（所有 workflow 通用 —— 任何时候都别破）

1. **禁止用 LLM 提示词宏**：`\manim{prompt}` / `\html{prompt}` / `\remotion{prompt}` / `\show{}` 一律不准。所有视觉必须是 `\manimFile[retime=true]{path.py}` / `\htmlFile{path.html}` / `\remotionFile{path.tsx}` / `\imageFile{path.png}` / `\image[engine=gemini]{prompt}`（AI 生图允许）。理由：LLM 出代码不稳定，编译失败率高；手写源码 + 缓存命中 = 几秒出片。**`\manimFile` 必带 `[retime=true]`**（2026-05-22 起默认不再自动缩放时长，不加则动画不随音频缩放、末帧冻结）。字幕用 `\caption{}`（`\text` 已废除、`\say[mute]` 已弃用）。
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
12. **resume = 云端为唯一真相**：任何继续 / resume 任务的**第一个动作必须是 `get_snapshot`**,以云端实际文件 + `main.tex` 的 view 顺序为准。summary / journal / 记忆里的文件清单只当**线索**,逐个 `read_file` 核对真身;**别信「已全部写好」**。理由：compaction summary 会点名错文件(废弃草稿、缺镜、命名打架),凭它接手会改错那套。详见 [`reference/resume-checklist.md`](reference/resume-checklist.md)。
13. **样张先行(强制)**：任何**多镜任务先端到端做 1 个样张并签字**(建项目 → 写 1 镜 → 编译 → `fetch_frame` 看帧 → 用户说「可以」),**再批量**剩余镜。理由：样张返工成本是 1 镜,量产后返工是 N 镜;最值钱的一步。
14. **一个项目一套命名前缀 + 替换即清理孤儿**：一个项目只用一套 scene 命名前缀(如 `hd_*`),**替换旧版时顺手 `delete_file` / `move_file` 归档**,不留混版孤儿文件。`main.tex` 的 view 顺序(或 `MANIFEST.md`)是**当前正式镜次的唯一清单**。理由：多套前缀并存 = resume 时得靠考古猜「哪套正式」。
15. **`main.tex` 骨架先行**：先建**全部 view 的可编译骨架**(每 view 先放占位 `\say` + `\htmlFile`)并立刻提交,**再逐镜填**;全程保持可编译 / 有序 / 可恢复态。**`\say` 与对应画面放同一 view**(别让旁白只躺在草稿里,否则 resume 得照原文重切)。
16. **`\manimFile` 必带 `[retime=true]`;`\say` ≤400 字、默认不烧字幕**(要 `burn=on` 才烧)。理由(retime)：2026-05-22 起默认不再自动缩放时长,不加则动画不随音频缩放、末帧冻结。(此条与 ban 1 呼应,resume / 批量量产时尤其容易漏。)

---

## 两种运行模式 ── 每条 workflow 第 0 步先判定

skill 支持两种用户场景,看 Claude 当前有没有 autolecture MCP 工具:

| 模式 | 触发 | 能做 |
|---|---|---|
| **mcp**(首选) | 当前工具列表里有 autolecture MCP 工具(连了 `mcp.autolecture.ai/mcp` 连接器) | Claude 直接用 MCP 工具:云端 `create_project`、`write_file`/`edit_file` 写 tex+scene、`add_asset` 传素材、`compile`+`get_status` 编译、`fetch_frame`/`fetch_waveform` 看渲出效果、`list_scene_versions`/`pick_scene_version` 回滚到更好的历史渲染版本、`fetch_asset_frame` 看原始素材的帧(复刻参考/编排检查)、`get_captions` 拿对齐后的逐行字幕(实拍改 `{src}.transcript.txt`、覆盖场景改 `\caption{}`,都即时生效不用重渲) —— 一条龙,编译挂了自己看帧调 |
| **zip**(默认 fallback) | 没 MCP、用户也不想连(含 **claude.ai 网页端**) | **只产 zip 让用户拖** [autolecture.ai](https://autolecture.ai);Claude 查不了用户状态,改用 `AskUserQuestion` 或保守默认 |

**判定(每条 workflow 第 0 步)**:看工具列表有没有 autolecture MCP 工具 —— 有 = **mcp**,没有 = **zip**。这是 Claude 自己看得见的,不跑脚本、不看本地文件。

每当 Claude 想建项目 / 写文件 / 编译 / 查用户状态 / 看 cloud 渲出的样子 → 先按模式分支:**mcp 调 MCP 工具,zip 走本地 fallback + 打 zip**(详见 [`reference/runtime-modes.md`](reference/runtime-modes.md))。

**别默认有 MCP** —— 很多用户(尤其 claude.ai 网页端)只能走 zip。

---

## 通用建筑块（被所有 workflow 引用）

- **两种运行模式速查**（mcp / zip 每个动作怎么做）→ [`reference/runtime-modes.md`](reference/runtime-modes.md)
- **audio-first timing**（三引擎写法）→ [`reference/audio-first.md`](reference/audio-first.md)
- **引擎选择决策树**（哪种内容用 Manim / HTML / Remotion / `\image`）→ [`reference/engine-routing.md`](reference/engine-routing.md)
- **视觉调色板 + 字体栈**（全片一致）— 两套**二选一**,一个项目内只用一套:
  - [`reference/palette.md`](reference/palette.md) · **editorial dark**（深底 + 海洋蓝）,默认。适合个人 vlog / 论文讲解 / 内容是主角的 editorial 叙事。
  - [`reference/brand-style.md`](reference/brand-style.md) · **AutoLecture brand**（cream + navy + tan 渐变,跟 [autolecture.ai](https://autolecture.ai) 网站 / Studio / watermark 同一调子）。挂 AutoLecture 招牌时用——官方 demo / teaser / 教程 / 上首页 showcase / 给内测用户的功能片。
- **VideoTeX 语法速查** → [`reference/dsl-cheatsheet.md`](reference/dsl-cheatsheet.md)（在线文档 <https://autolecture.ai/docs/dsl>）
- **配套素材 anchor 匹配**（PDF figure / repo 截图 / 本地图）→ [`reference/figure-matching.md`](reference/figure-matching.md)
- **可借鉴动效技法**（写新 scene 前翻一下）→ [`reference/borrowed-techniques.md`](reference/borrowed-techniques.md)
- **交付**（MCP 直驱 / zip 上传）→ [`workflows/_delivery.md`](workflows/_delivery.md)

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
- [`workflows/_delivery.md`](workflows/_delivery.md) — 共用交付（MCP / zip）

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
- [`reference/runtime-modes.md`](reference/runtime-modes.md) — mcp / zip 两模式速查(每个动作怎么做)
- [`reference/layout-spec.md`](reference/layout-spec.md) — harness 校验的 layout 限值(canvas / safe zone / 字数上限) Claude 读这个就知道边界
- [`reference/hand-drawn-storybook.md`](reference/hand-drawn-storybook.md) — 手绘 storybook 风技法(内联 SVG 描边 draw 动画 + feTurbulence 钢笔抖动 + bob/sway 微动 + 品牌色),寓言体 / 故事化讲解可整片复用
- [`reference/compile-and-preview.md`](reference/compile-and-preview.md) — 编译 / 单镜预览 / `fetch_frame` 抽帧三件套的反直觉点(成本量级、单 view 临时覆写 main.tex、content_hash 当 scene_id、base64 落盘解码、改分辨率=全量重渲)
- [`reference/resume-checklist.md`](reference/resume-checklist.md) — resume 任务核对清单：`get_snapshot` 对齐云端真相、逐个 `read_file` 核对、清理孤儿、骨架先行

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
- [`scripts/package_zip.py`](scripts/package_zip.py) — zip 模式：校验 + 打包 zip（mcp 模式直接用 MCP 工具写文件 + 编译,不用脚本）

### 关键经验（实际跑过的 demo）
1. **不要把 70s+ 的 Manim 单 scene 当作天经地义** —— 1000+ 帧 + 40 dot + 多 FadeIn 渲染超 300s timeout；同样视觉用 Remotion DOM 模拟（CSS 粒子 + transform）<10s。
2. **修转录错字非常重要** —— 「高斯」→「高撕」、「正则项」→「政策画像」直接用会让 headline 乱码。
3. **每个 scene 独立设计 ≠ 不一致** —— 统一调色板 + 字体 + 动画语法（fade-up / pop / strike）就有一致性。
4. **HTML 是默认首选** —— 快、稳、灵活；Manim 只在数学/几何精度真重要时用；Remotion 适合大数字 / 时间轴。
5. **`\imageFile` ≠ `\image`** —— 前者是上传素材，后者是 AI 生图；可一起用（固定背景 `\imageFile`，特殊插画 `\image`）。

### 上游
- 主项目 <https://github.com/scao7/autolecture> · 远程 MCP <https://mcp.autolecture.ai/mcp> · DSL 文档 <https://autolecture.ai/docs/dsl>
