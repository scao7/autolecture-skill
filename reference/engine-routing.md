# 引擎选择决策树

每个 beat 必须挑一个视觉引擎。下面是按内容类型的路由表。

## 快速决策

```
beat 内容是什么？
├── 数学公式 / 几何 / 3D 点云 / 函数图像 / 物理模拟
│   → Manim (.py)
├── 大数字反转 / 时间轴动画 / 多阶段过渡 / 文字打字机
│   → Remotion (.tsx)
├── 论文标题 / 卡片 / 对比布局 / 流程图 / 表格 / 概念图
│   → HTML (.html)
├── 真人照片 / 上传插画
│   → \imageFile{path}
└── AI 风格插画（水彩 / 卡通 / 概念图）
    → \image[engine=gemini]{prompt}
```

## 详细规则

### Manim（数学/几何）

**用**：
- 3D 点云、向量场、矩阵变换
- 数学公式 morph（`TransformMatchingTex`）
- 几何证明（拆分正方形、画切线）
- 函数图像、参数曲线
- 重力/物理模拟（小球落地）

**避免**：
- 文字密集场景（Manim 渲文字慢且丑）
- 复杂动画 + 大量元素（容易超 300s timeout）
- 简单卡片布局（HTML 写起来简单 100 倍）

**渲染时长粗算**：480p15 默认 → 渲染时长 ≈ scene 时长 × 3-8 倍。**70 秒以上的 Manim scene 必须拆**，或者改用 Remotion DOM。

**标准头**：
```python
from manim import Scene, ThreeDScene, Circle, ... 
from manim import PI, ORIGIN, UP, DOWN, RIGHT, LEFT, WHITE, BLUE, RED, YELLOW, GREEN

class LectureScene(Scene):  # or ThreeDScene
    def construct(self):
        # ...
        self.play(FadeIn(...), run_time=1.0)
        self.wait(2.0)
```

### Remotion（精细动画）

**用**：
- 大数字 reveal（"48×" 反转）
- 文字打字机 / blur → sharp
- 多阶段过渡（多个 `interpolate` + `spring`）
- L2 距离折线 + 标记尖峰
- 计数器（6 → 5 → 4 → 1）
- 撕胶带 / 拼图等抽象时间轴动画
- 大量粒子 DOM 模拟（替代 Manim 3D 点云的轻量化方案）

**避免**：
- 静态卡片（HTML 更短）
- 数学严谨度要求（用 Manim）

**必须导出**：
```tsx
export const FPS = 30;
export const WIDTH = 1280;
export const HEIGHT = 720;
export const DURATION_FRAMES = N * FPS;
export const Comp: React.FC = () => { ... };
```

### HTML（卡片/布局/文字）

**用**：
- 论文标题卡（title + authors + arxiv）
- 三柱对比、four-card grid
- 流程图、时间线
- 公式卡（带颜色注释）
- 引言 / 总结 / 致谢
- 简单 SVG 图标

**避免**：
- 复杂时间轴（要求精确 frame-level 控制时用 Remotion）
- 真 3D（用 Manim）

**标准头**：
```html
<!DOCTYPE html>
<html lang="zh"><head><meta charset="UTF-8"><title>...</title>
<style>
  html, body { margin: 0; padding: 0; width: 100%; height: 100%;
               background: #0d1117; overflow: hidden;
               font-family: 'Inter', system-ui, 'PingFang SC', sans-serif;
               color: #fff; }
  .stage { width: 100vw; height: 100vh; display: flex; flex-direction: column;
           align-items: center; justify-content: center; padding: 50px;
           box-sizing: border-box; }
  @keyframes in { to { opacity: 1; transform: translate(0); } }
</style></head>
<body>
<div class="stage">
  ...
</div>
</body></html>
```

### `\imageFile`（上传素材）

**用**：
- 有具体的真人照片、文档截图、产品图
- 用户预先准备好的插画

**注意**：
- 文件放 assets/figures/ 下
- 用 `[fit=contain]` 避免裁切

### `\image`（AI 生图，Gemini）

**用**：
- 需要原创插画但不想找设计师 / 自己画
- 风格统一（搭配 `\style{}` 用）
- 一次性概念图（"一个想 idea 的女孩"、"卡通鸭子在水边"）

**避免**：
- 含具体文字（AI 出文字常错）
- 需要数据准确性（图表）

**调用方式**：
```latex
\image[engine=gemini, aspect=16:9]{a thoughtful person at a desk, soft watercolor}
```

## 一致性原则

**视觉一致性优先于引擎数量。** "像 PPT" 的真正病因是**静态堆叠** —— 一屏屏不动的卡片硬切，而不是 "只用了一种引擎"。

- **静态堆叠才像 PPT**：没有入场动效、没有持续微动作、镜与镜之间生切。
- **成体系的动效手绘 SVG/HTML 不算 PPT**：描边 `draw`、填充淡入、`feTurbulence` 钢笔抖动、`bob/sway/spin` 微动作连成一套语言，整片就是一部会动的绘本，不是幻灯片。

所以：为了统一风格（比如全程手绘 storybook），**主动收敛到单一引擎是合理且鼓励的**。别为了凑 "≥3 种引擎" 而牺牲视觉一致性。具体技法见 [`hand-drawn-storybook.md`](hand-drawn-storybook.md)。

下面这张分布表只是 **混合讲解片** 的默认起点，不是硬指标 —— 风格统一的项目（手绘绘本、纯 Manim 数学课）可以并且应该偏离它：

| 引擎 | 占比 |
|---|---|
| HTML | 50-60% (主力，便宜稳) |
| Remotion | 25-35% (大数字、时间轴、抽象动画) |
| Manim | 5-15% (只在数学/3D 真的需要时) |
| `\image` AI | 0-5% (人物/插画) |
| `\imageFile` | 0-10% (具体素材) |
