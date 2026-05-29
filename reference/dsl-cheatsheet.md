# VideoTeX DSL 速查（autolecture-skill 用）

## 文档结构

```latex
\title{<title>}
\aspect{16:9}     % or 9:16 / 1:1
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

`\title` / `\aspect` / `\style`（视觉）/ `\voice`（TTS 音色语气，与 `\style` 解耦）/ `\subtitle{on|off|auto}` / `\bgm[volume=,loop=]{path}` / `\character[voice=,speed=]{name}`。

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
