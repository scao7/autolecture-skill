# Workflow · 用户录音上传 → 视频（音频驱动）

**入口**：用户给一段**音频**（mp3/wav/m4a）。**音频驱动**：人声是时间轴脊柱。
先转录 + 修错字 + 判断要不要重构讲稿，这决定音频是「保留原声直接剪」还是「voice clone 重合成」。

---

## 步骤

### 0 · 用 SKILL.md 入口已确认的 mode + 定 voice clone 处理

> **`$mode` 已在 SKILL.md 入口 ② 定下**——dynamic 还是 static 这里不再问。继续往下,DYNAMIC / STATIC 分两条路。

**voice clone 处理决策**(这条 workflow 特有,决定后面 `\say` 写不写 `voice=mine`):

- **DYNAMIC**:`python -c "from autolecture import Client; print(Client().get_voice_sample())"` → `filename` 字段存在 = 有 sample → plan 写"所有 `\say` 带 `voice=mine`";否则用默认 speaker。
- **STATIC**:`AskUserQuestion` 三选一:① 是,用我的克隆声(全片 `voice=mine`) ② 否 / 不清楚(默认 speaker) ③ 我要保留原声不做 TTS(走 `\audio[start,end]{}` + `\caption{}` 路径,不用 `\say` TTS)。

决策写进 `<work>/beat_plan.md`,**整片所有 `\say` 用同一种处理,不能 mix**。每个动作的 dynamic/static fallback 全表见 [`../reference/runtime-modes.md`](../reference/runtime-modes.md)。

### 1 · 准备 + 转录
```bash
WORK=/tmp/autolecture_$(date +%s); mkdir -p $WORK/{scenes,figures}
python3 scripts/transcribe.py --audio <user.m4a> --out <work>/<user>.m4a.whisper.json
```
[`scripts/transcribe.py`](../scripts/transcribe.py) 用 `whisper.base` 加词级时间戳，落 sidecar JSON。

### 2 · 修转录错字（HARD BAN #3）
读 [`../reference/typo-fixes.md`](../reference/typo-fixes.md)（「高撕」→「高斯」、「政策画像」→「正则项」）+ 本次新发现的，逐句过一遍，修正映射记到 `<work>/transcript_corrections.md`。**原音频不动**，错字只影响视觉文字 / 重构稿。

### 3 · 分析：纯净口播 还是 随口录的想法？→ 决定是否重构
- **纯净口播**（成品播客 / 有意识录的连贯旁白）→ 大概率**不重构**，保留原声。
- **随口录的想法**（跑题、卡顿、重复、想到哪说到哪）→ 大概率**需要重构**讲稿。
- 含糊就用 AskUserQuestion 问用户：「保留你的原声直接剪辑，还是让我把内容重新组织、用你的声音（voice clone）重讲一遍？」

---

## 路线 A · 不重构（保留原声，直接剪）

音频保持原状，按内容自然分段，用 `\audio[start=,end=]{}` 剪辑原音频，给每段配画面。

1. 在 transcript 里搜每段**锚句**（开头特征字），用 [`scripts/find_beats.py`](../scripts/find_beats.py) 定位 start 时间戳；相邻锚句之间 = 一个 view 的 `[start, end]`。**不重组叙事**，按音频自然顺序切。
2. 组装：
   ```latex
   \begin{view}
     \audio[start=32.34, end=37.48]{<user>.m4a}   % 原声片段
     \htmlFile{scenes/scene_02.html}               % 配的画面
   \end{view}
   ```

## 路线 B · 重构（voice clone + TTS 重讲）

把内容重新组织成清晰叙事，用**用户自己的声音克隆**重新合成（不是默认 TTS 嗓音），再按 TTS 时长切分写画面。

1. **重写讲稿**：基于修正后的 transcript 重组叙事（清晰开头/中间/结尾，删冗余、补连接句）。
2. **voice clone**：让用户在 <https://autolecture.ai/account> 注册声音样本（把这段录音当样本），之后 `\say[voice=mine]{...}` 就用克隆的嗓音合成。在交付说明里写明这一步（没注册样本会回落到默认嗓音）。
3. **按 TTS 时长切分写画面**：每段重写后的稿子 = 一个 view 的 `\say[voice=mine]{}`；真实时长在编译时由 TTS + audio-first 锁定（见 [`../reference/audio-first.md`](../reference/audio-first.md)），估算只为排版。
   ```latex
   \begin{view}
     \say[voice=mine]{<重写后的这一段>}
     \remotionFile{scenes/scene_02.tsx}
   \end{view}
   ```

---

## 配套素材（两条路线都适用，如果有）
用户同时给了 PDF / repo / 图 → 按 [`../reference/figure-matching.md`](../reference/figure-matching.md) match 进画面，每张图**必须有 anchor 句证据**写进 `beat_plan.md`（HARD BAN #8）。想在画面里**展示 PDF 原件** → 叠 [`pdf-paper.md`](pdf-paper.md) 的 Flow B 镜头。

## 选引擎 + 手写 scene
读 [`../reference/engine-routing.md`](../reference/engine-routing.md)；画面扣每段口播的重点和意思。统一调色板 [`../reference/palette.md`](../reference/palette.md)，每个 scene 独立设计、≤60s、命名 `scene_NN_label.<ext>`。

## README + 交付
`<audio>.m4a` + `.whisper.json` 列入包含项（路线 A 字幕对齐要用）。然后 → **交付：见 [`_delivery.md`](_delivery.md)**。
