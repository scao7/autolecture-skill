# Workflow · 用户提供视频 → 视频（用原视频音频，不做 TTS）

**入口**：用户给一段**实拍视频**（口播 talking-head、操作录屏、产品镜头）。
大概率用户想**用原始视频**，所以**不做 TTS** —— 直接拿视频自带的音频当 ground truth。

> 仍然是**音频驱动**：视频里的人声是时间轴的脊柱，画面（保留实拍 / 切到我们的素材 / 叠加动效）都围着它排。

> ⚠️ **剪辑全用 .tex 表达,绝不预剪素材**（HARD BAN #11）。原始视频**整个**当 asset，
> 选段用 `\video[start=, end=]{原片}` / `\audio[start=, end=]{原片}`（编译器从原片取窗口,
> 原片不动）、拼接用 view 顺序、转场用 `\fade`。**不要**在外面 ffmpeg 切片/拼接/变速再丢进来 ——
> 那会把剪辑烧死在文件里、绕过 .tex（P1 LaTeX 唯一真相 / 预览即导出）。

---

## 步骤

### 0 · 检测运行模式
```bash
mode=$(python -m scripts.runtime_mode)   # → "dynamic" 或 "static"
```
- **dynamic** → 可调 SDK 预估编译成本、SDK 一条龙交付
- **static** → 只产 zip 让用户拖 [autolecture.ai](https://autolecture.ai)

详见 [`../reference/runtime-modes.md`](../reference/runtime-modes.md)。

**这条 workflow 不做 TTS**(用原片音频),所以**不需要查 voice clone 状态**——`voice=mine` 跟这条 workflow 无关。

⚠️ **资产大小注意**:原片 ≥ 100MB(几乎所有 1080p+ 视频)→ 都得**转码代理片**(720p H.264 < 100MB)才能通过 zip / SDK 上传。详见 [HARD BAN #11 例外条款](../SKILL.md) 与 [`large-media-upload-constraint` memory note]。

### 1 · 准备工作目录 + 分析音频
```bash
WORK=/tmp/autolecture_$(date +%s); mkdir -p $WORK/{scenes,figures}
# 视频当 asset 放进 <work>/，如 clip.mp4
python3 scripts/transcribe.py --audio <clip.mp4> --out <work>/clip.mp4.whisper.json
```
转录**视频自带音频**（用于定位 + 字幕 + 切分），修转录错字（[`../reference/typo-fixes.md`](../reference/typo-fixes.md)）。**不重写、不重合成**——音频保持原状。

### 2 · 按音频拆分 beat
用 [`scripts/find_beats.py`](../scripts/find_beats.py) 在 transcript 里搜锚句，得到每段的 `[start, end]`。相邻锚句之间 = 一镜。输出 `<work>/beat_plan.md`。

### 3 · 问用户：叠加特效 还是 剪辑结合？
这是视频流程的关键分叉，用 AskUserQuestion 问（或按线索判断）：

| 模式 | 用户想要 | 怎么排 |
|---|---|---|
| **A · 叠加（overlay）** | "在我这段视频**上面**加字幕条 / 数据卡 / 箭头" | 每镜 `\video{clip}` + `\remotionFile[over=true]{}`，**半透明毛玻璃**动效叠在实拍上 |
| **B · 剪辑结合（intercut）** | "把我的口播和讲解画面**剪在一起**" | 音频为主轴：该露脸时放 talking-head，该讲概念时切到我们写的素材 scene |
| **C · Tella 录屏 + 画中画** | 有**两段素材**（录屏 + 头像），要那种"头像从全屏缩进角落、录屏接管"的丝滑切 | 一个 view 里一个 `\remotionFile{}` scene 同时载入两段，`interpolate` 做全屏↔小窗 morph |

---

## 模式 A · 叠加特效（frosted-glass overlay）

同一个 view 里放两层视觉：**实拍底**（`\video`，自带原声 = 脊柱）+ **透明动效覆盖层**（`\remotionFile[over=true]`）。Remotion 把动效渲成**透明 alpha 素材**，由 **manifest 叠**在实拍上 —— 引擎只产素材，叠加编排全在 VideoTeX/manifest（预览即导出）。

```latex
\begin{view}
  \video[start=0, end=8.5]{clip.mp4}                  % 实拍底 + 自带原声 = 脊柱
  \remotionFile[over=true]{scenes/overlay_01.tsx}      % 透明动效覆盖层
  % 可选：额外叠加配音/背景乐（音频叠加,不替换原声）
  % \say[volume=1.2]{补充说明……}
\end{view}
```

- 模板 [`../templates/scene_overlay.tsx.tpl`](../templates/scene_overlay.tsx.tpl)。**半透明毛玻璃**：面板用低透明度填充（alpha 0.30–0.50）+ 浅色描边 + 顶部 sheen，让实拍透过来。
- **机制**：`over=true` 只是个**渲染提示** —— 让 Remotion 渲成透明 webm（alpha）。**引擎完全不碰实拍**；把 alpha 叠到 `\video` 上是 manifest 的事。这一镜时长由 `\video`（自带音频）决定（audio-first）；想去原声用 `\video[mute=on]`。
- 两条铁律：① 覆盖层根 `AbsoluteFill` 绝不设不透明 `backgroundColor`（否则盖住实拍）；② 只给图形元素本身上背景。
- 音频叠加：实拍原声 + `\say` + `\bgm` 一起 mix（用各自 `volume=` 调比例）。`over=true` 对 `\remotion` 和 `\remotionFile` 都有效。

## 模式 B · 剪辑结合（intercut，音频驱动）

用户的口播音频是**连续主轴**，画面在「露脸」和「我们的素材」之间切。哪一拍露脸、哪一拍上素材由音频内容决定（讲到需要可视化的概念 → 切素材；个人观点 / 镜头感强的段落 → 露脸）。

- **露脸镜**：直接放实拍片段（含原声）：
  ```latex
  \begin{view}
    \video[start=0, end=8.5]{clip.mp4}     % talking-head，原声跟随
  \end{view}
  ```
- **素材镜**：切到我们手写的 scene，**底下铺这一段的原声**（从同一视频音频里剪那一段）：
  ```latex
  \begin{view}
    \audio[start=8.5, end=15.2]{clip.mp4}  % 用户这一段的人声
    \htmlFile{scenes/scene_concept.html}    % 我们写的讲解画面
  \end{view}
  ```
- 两种镜交替排满整条音频时间轴，`start/end` 首尾相接（不留缝、不重叠）。素材镜的画面 audio-first（跟 `\audio` 时长，见 [`../reference/audio-first.md`](../reference/audio-first.md)）。
- 选引擎 / 手写 scene 同 [`text-to-lecture.md`](text-to-lecture.md) 步骤 3–4，统一调色板 [`../reference/palette.md`](../reference/palette.md)。

## 模式 C · Tella 录屏 + 头像画中画（全屏↔小窗 morph）

用户有**两段素材**（一段录屏 + 一段对着摄像头的口播），想要那种很丝滑的
Tella 效果：开场头像铺满全屏自我介绍，然后**缩进角落变成小窗**、录屏接管画面。

关键认知：**这个「缩小」是一镜之内的 morph，必须放在同一个 `view` 里**。一个
`\remotionFile{}` scene 同时载入两段视频，用 `interpolate` 把头像的 scale /
位置 / 圆角随时间插值。这**不是** `over=` 叠加（叠加层是独立透明渲染、引擎碰不到
实拍）—— 这一镜里 scene 自己把两段合成。manifest 只在 **view 边界**做切 / 淡，
所以跨两个 view 做不出这种 morph。

```latex
\begin{view}
  \remotionFile{scenes/screencast_01.tsx}   % 同时载入 screen.mp4 + webcam.mp4
  \audio{webcam.mp4}                          % 人声 = 脊柱 + 决定这一镜时长
\end{view}
```

- 模板 [`../templates/scene_screencast_pip.tsx.tpl`](../templates/scene_screencast_pip.tsx.tpl)。两段都 `staticFile()` 直接载入、scene 里都 `muted`（scene 只出画面、不带音频）。
- **音频**：人声来自 `\audio{webcam.mp4}`（同一头像文件当音轨脊柱）；它也定这一镜时长，编译器据此覆盖 `DURATION_FRAMES`，所以模板里用 `dur` 的分数表达的 morph 时间点会自动对齐。录屏自带系统音（点击声 / demo 声）也想要的话，再加一条 `\audio[...]{screen.mp4}`（叠加 mix，不替换）。
- 模板参数：`PIP_SCALE`（小窗占比 0.22–0.30）、`PIP_CORNER`（br/bl/tr/tl）、`MORPH_START/END`（0..1，缩小动作发生在片段的哪一段）。要反向（结尾再放大回全屏脸）/ 加标题条 / 录屏 punch-in 放大，模板里搜 `VARIANT` 注释。

---

## README + 交付
视频片段列入包含项。然后 → **交付：见 [`_delivery.md`](_delivery.md)**。
