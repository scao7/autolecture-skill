# Workflow · 用户提供视频 → 视频（用原视频音频，不做 TTS）

**入口**：用户给一段**实拍视频**（口播 talking-head、操作录屏、产品镜头）。
大概率用户想**用原始视频**，所以**不做 TTS** —— 直接拿视频自带的音频当 ground truth。

> 仍然是**音频驱动**：视频里的人声是时间轴的脊柱，画面（保留实拍 / 切到我们的素材 / 叠加动效）都围着它排。

---

## 步骤

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
| **A · 叠加（overlay）** | "在我这段视频**上面**加字幕条 / 数据卡 / 箭头" | 每镜 `\remotionFile[over=clip.mp4]{}`，**半透明毛玻璃**动效叠在实拍上 |
| **B · 剪辑结合（intercut）** | "把我的口播和讲解画面**剪在一起**" | 音频为主轴：该露脸时放 talking-head，该讲概念时切到我们写的素材 scene |

---

## 模式 A · 叠加特效（frosted-glass overlay）

实拍是主轴，动效**透明渲染**后由后端 ffmpeg 合成到实拍**上面**；实拍时长决定这一镜长度。

```latex
\begin{view}
  \remotionFile[over=clip.mp4, over_volume=1.0]{scenes/overlay_lower_third.tsx}
  % 可选：另配旁白叠加（不替换原声）
  % \say[volume=1.2]{补充说明……}
\end{view}
```

- 模板 [`../templates/scene_overlay.tsx.tpl`](../templates/scene_overlay.tsx.tpl)。**半透明毛玻璃**：面板用低透明度填充（alpha 0.30–0.50）+ 浅色描边 + 顶部 sheen，让实拍透过来。
- **机制**：`over=` 把实拍当作**这一镜 Remotion 合成里的实时 `<OffthreadVideo>` 背景**，scene 在它上面画透明动效 —— 一次渲染，不是 ffmpeg 后合成。所以普通 CSS 叠在真实视频上都有效，连 `backdrop-filter: blur()` 都能真的模糊背后的实拍（如果想要）。**这里不需要 blur** —— 半透明面板本身就够「毛玻璃」质感了。
- 两条铁律：① 根 `AbsoluteFill` 绝不设不透明 `backgroundColor`（否则盖住实拍）；② 只给图形元素本身上背景。
- 音频叠加：原声 + `\say` + `\bgm` 一起 mix（`over_volume=` / `\say[volume=]` / `\bgm[volume=]` 调比例）。

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

---

## README + 交付
视频片段列入包含项。然后 → **交付：见 [`_delivery.md`](_delivery.md)**。
