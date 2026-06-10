# VideoTeX DSL 速查（autolecture-skill 用）

## 文档结构

```latex
\title{<title>}
\aspect{16:9}                 % 比例。默认短边 720p
% \aspect{16:9, 1080p}        % 或加分辨率：720p / 1080p / 1440p / 2k / 4k
\style{<视觉风格描述：注入 LLM 视觉引擎 system prompt>}
\voice{<TTS 音色语气描述，可选；不写则回退用 \style 的描述>}

\begin{videotex}
  \begin{view}[opts]
    ...layer 宏...
  \end{view}

  \fade[duration=0.5]{}   % 转场（可选）

  \begin{view}...\end{view}
\end{videotex}
```

## 视觉层宏（每个 view 一个）

| 宏 | 适用 | 备注 |
|---|---|---|
| `\manimFile[retime=true]{path.py}` | Manim Python 源码 | 渲染入口类固定为 `LectureScene`（把动画写进这个类；`scene=` 选择器已于 2026-05-23 移除）。**`retime=true` 必加**（2026-05-22 起 `\manimFile` 默认不再自动缩放时长——只有 `retime=true` 才把 `self.play/wait` 缩放到 `\say` 长度，否则按源码原速渲染、末帧冻结）。 |
| `\htmlFile{path.html}` | HTML 源码 | Playwright 实时录屏；独立的内联 CSS |
| `\remotionFile{path.tsx}` | Remotion React 源码 | 必须导出 `Comp` / `FPS` / `WIDTH` / `HEIGHT` / `DURATION_FRAMES` |
| `\imageFile{path.png}` | 上传的图片 | opts: `fit / position / bg / lead` |
| `\image[engine=gemini]{prompt}` | AI 生图 | Gemini，单次生成，同 prompt+style 缓存命中 |
| `\video[start=,end=]{path.mp4}` | 上传的视频片段 | `mute / loop / fit` |

**禁用**：`\manim{prompt}` / `\html{prompt}` / `\remotion{prompt}` / `\show{}` — LLM 出代码，不稳定。

## 音频层

| 宏 | 适用 |
|---|---|
| `\say{text}` | TTS 合成。opts: `voice=mine` / `speaker` / `speed` / `model` / `burn` / `as` |
| `\audio[start=N, end=N]{path.m4a}` | 剪辑原音频（不走 TTS、无自动字幕） |

## 字幕层

| 宏 | 适用 |
|---|---|
| `\caption{...}` | 纯烧字幕，**永不驱动 TTS**。opts: `position=top|bottom|hidden` / `align=auto|on|off`。给录音/实拍配字幕就用它（配 `\audio`，原声播放 + 烧字幕）。取代已废除的 `\text` 和已弃用的 `\say[mute=true]`。 |

省略时默认行为：`\say` 有 → 字幕用 `\say` 文字（需 `burn=on`）；`\audio` 单独用 → 无字幕（加 `\caption` 配字幕）。

## view-level opts

只有 2 个：`duration`（秒）+ `title`（编辑器显示名）。

## preamble-only 宏

`\title` / `\aspect` / `\style`（视觉）/ `\voice`（TTS 音色语气，与 `\style` 解耦）/ `\subtitle[size=, color=, position=top|bottom, punct=keep]{on|off|auto}`（样式只影响显示/烧录，**不触发重渲**） / `\bgm[volume=,loop=]{path}` / `\character[voice=,speed=]{name}` / `\cliplibrary{clips/day1}`（声明剪辑素材库，可重复，BibTeX 模式）。

### clip 库（剪辑素材的 BibTeX）

剪辑分块（trim）以**非破坏**方式集中写在 clip 文档里，main.tex 用 `@名字` 引用：

```latex
% main.tex 导言区（不声明则默认找 clip.tex）
\cliplibrary{clips/day1}        % 省略 .tex 自动补全，同 \bibliography

% clips/day1.tex —— 顶层只允许 \begin{segment}{name}
\begin{segment}{intro_hook}
\video[start=2, end=8]{takes/a.mp4}
\caption{开场字幕}              % 可选：随段落走的字幕
\end{segment}

% main.tex 正文 —— segment≈@entry, \video{@name}≈\cite
\begin{view}\video{@intro_hook}\end{view}
```

字幕机制（实拍默认走**素材级文稿**）：给素材写 `assets/{media}.transcript.txt`（整段校正稿）+ 已有的 `{media}.whisper.json`（`transcribe` 产物），**所有引用该素材的 view 自动按各自 [start,end] 窗口派生字幕**——tex 里零字幕内容，拖剪点字幕自动跟随，改文稿即时重对齐（免重渲）。`\caption{}` 仍可作 view 级显式覆盖：写**一整段连续文本**即可——行级拆分和时间码是派生物（对齐语音后自动按标点/约 18 字切成满屏句子），**不要**手写时间。唯一的拆分覆盖：正文里写 `\\` 强制在该处断句。整片可导出 SRT（`GET /projects/{id}/captions.srt`）。

规则：声明的库**严格**（文件缺失 / 跨库重名 segment → 报错）；clip 文档里禁止 view / 特效 / `\say`；随手剪一刀直接在 view 里写 `\video[start=, end=]{src}`（匿名内联 trim），不必进库。**agent 粗剪 = 写 clip 库；人微调 = Studio 里拖剪点 / 改字幕**——双方编辑同一份 .tex。

### `\aspect{}` 语法（重要）

- `\aspect{16:9}` — 仅比例，默认短边 **720p**（→ 1280×720）。
- `\aspect{16:9, 1080p}` — 比例+分辨率。RES 合法值：`720p` / `1080p` / `1440p` / `2k` (= 1440p) / `4k` (= 2160p)。
- 分辨率在**编译时**就生效：每个 view block 原生渲染到目标尺寸（manim/html/remotion 全部按这个 canvas 出帧）。导出按钮只决定是否烧水印，不再做分辨率切换。
- 想出 4K，就写 `\aspect{16:9, 4k}` 后重新 compile all（cache 会因为 canvas 改了而 miss → 重渲）。

## body 元素

`\begin{view}...\end{view}` / `\begin{segment}[title=,continuous=]...\end{segment}` / `\fade[duration=,color=]{}` / `\input{path.tex}`。

## 一个最小例子（手写源码模式）

```latex
\title{Hello AutoLecture}
\aspect{16:9}
\style{深色背景 #0d1117, Inter + PingFang SC, 简洁动画}

\begin{videotex}

\begin{view}[title=Hook]
  \say{今天我们来看看世界上最小的世界模型。}
  \remotionFile{scenes/scene_01_hook.tsx}
\end{view}

\begin{view}[title=Card]
  \say{15M 参数，2 个损失函数，48 倍加速。}
  \htmlFile{scenes/scene_02_card.html}
\end{view}

\end{videotex}
```

## 一个 polished 模式例子（剪辑原音频）

```latex
\title{论文解读}
\aspect{16:9}
\style{学术深度解读, 深色背景, 高对比白字, Inter + PingFang SC}

\begin{videotex}

\begin{view}[title=Hook]
  \audio[start=0.00, end=32.34]{podcast.m4a}
  \remotionFile{scenes/scene_01_hook.tsx}
\end{view}

\begin{view}[title=Card]
  \audio[start=32.34, end=66.44]{podcast.m4a}
  \htmlFile{scenes/scene_02_card.html}
\end{view}

\end{videotex}
```
