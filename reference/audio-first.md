# Audio-first timing — 三引擎写法对照

**核心原则**：音频长度是 ground truth。视觉适配音频，绝不反过来。
compiler 编译时已经知道 audio 时长（target_dur），三个引擎各自的适配方式不同。
这是所有 workflow 共用的铁律（HARD BAN #10），写任何 scene 前先读这页。

违反的后果：scene 会出现「动画提前结束 + 后段冻结」或「动画跑得比音频快 → 看不清」。

---

## `\manimFile{}` — compiler 自动 AST scale

AutoLecture 后端对 `\manimFile` 用户源码跑 `fit_manim_to_target`：扫 `construct()`
里所有 `self.play(run_time=N)` + `self.wait(N)`，求和得 natural_dur，然后把每个
`run_time=` 和 `wait()` 按 `target_dur / natural_dur` 倍率统一重写（clamp 在 [0.3×, 4.0×]）。

**写法**：写「自然时长」让 scaler 接管：
```python
self.play(FadeIn(circle), run_time=1.0)
self.wait(2.0)
self.play(circle.animate.scale(1.6), run_time=1.5)
```
**禁止**：
- 预估「音频 15s 所以 run_time=2.5」——TTS 实际 14.3s 时整片都错。
- 用 `time.sleep()` 或其它非 Manim 计时——scaler 看不到。

---

## `\remotionFile{}` — `useVideoConfig().durationInFrames` 相对时间

compiler 只 override 顶部导出的 `DURATION_FRAMES` 常量，**不改组件 body**。所以
组件里写死 `interpolate(frame, [0, 30], ...)` 会在 1s 处结束，剩下时间冻结。

**写法**：用 `useVideoConfig().durationInFrames` 算 phase 边界：
```tsx
const { durationInFrames: dur } = useVideoConfig();
const kickerOp = interpolate(frame, [0, dur * 0.10], [0, 1], { extrapolateRight: 'clamp' });
const titleOp  = interpolate(frame, [dur * 0.10, dur * 0.20], [0, 1], { extrapolateRight: 'clamp' });
const accentOp = interpolate(frame, [dur * 0.85, dur], [0, 1], { extrapolateLeft: 'clamp' });
```
**禁止**：硬编码绝对帧号（`[0, 30]`, `[60, 90]`）。

---

## `\htmlFile{}` — 短入场 + 持续微动态

compiler **不改 CSS keyframes**。Playwright 录制 `target_duration` 秒整页面；
CSS 动画结束之后就是 frozen frame。

**写法**：
1. **入场动画在 1.0–1.5s 内全部结束**（用错位 `animation-delay`：0.2s / 0.4s / 0.6s）。
2. **保留至少一个 element 持续微动态**（缓慢 pulse / 横向 scan / drift）—— 长音频时
   画面有「呼吸感」，不会变成静止图。
3. **禁止排长队的 sequential delays**（`delay: 0s; 4s; 8s; 12s`）—— 如果 audio 实际
   5s，后面的 element 永远不显示。

`templates/scene_html.html.tpl` 的 `.accent-pulse` + `.underline-scan` 是默认的
「呼吸 + sheen」骨架。
