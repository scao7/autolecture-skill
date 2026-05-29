# 视觉调色板 + 字体 · editorial dark(autolecture-skill 默认)

> 这是**默认**的 editorial dark 调色板,适合**内容是主角**的 vlog / 论文讲解 / 个人叙事——深底、克制、冷调。
>
> 如果项目要**挂 AutoLecture 招牌**(官方 demo / teaser / 教程 / 上首页 showcase),改用 [`brand-style.md`](brand-style.md) ——浅 cream + navy + tan 渐变,与 [autolecture.ai](https://autolecture.ai) 网站、Studio、watermark 同一调子。**一个项目内只用一套,别混。**

## 调色板

```
bg:        #0d1117   /* 深底，所有 scene 默认背景 */
fg:        #ffffff   /* 主文字 */
accent:    #6ec1e4   /* 主品牌色 - 海洋蓝 */
highlight: #f4d35e   /* 重点强调 - 暖黄 */
warn:      #ee6c4d   /* 警告 / 红线 - 珊瑚红 */
mint:      #4ec9b0   /* 次要强调 - 薄荷 */
dim:       #5a6273   /* 弱化文字 */
sub:       #aab1c0   /* 副文本 / 注释 */
border:    #2a2f3a   /* 卡片边框 */
panel:     #1a2030   /* 卡片底色 */
```

## 字体栈

```
font-family: 'Inter', system-ui, -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
```

数学公式专用：
```
font-family: 'Latin Modern Math', 'Cambria Math', 'STIX Two Math', serif;
```

毛笔/书法（"大道至简" 这类）：
```
font-family: '楷体', 'KaiTi', 'STKaiti', 'Songti SC', serif;
```

## 文字层级

| 类型 | 大小 | 字重 | 字距 |
|---|---|---|---|
| 大标题 (hook) | 96-124px | 800-900 | -2 |
| 副标题 | 38-56px | 700 | -0.5 |
| 段落标题 | 24-32px | 700 | 0 |
| 正文 | 16-22px | 400-500 | 0.3 |
| 元信息 (kicker) | 12-14px | 600 | 4-6 |

## 动画语法（一致性关键）

| 动作 | CSS / Remotion |
|---|---|
| fade-up（出现） | `opacity: 0 → 1, transform: translateY(20px → 0)` |
| pop（弹出） | `opacity: 0 → 1, transform: scale(0.85 → 1)` |
| typewriter | 按 frame 切片显示字符 |
| strike-through | `::after` 伪元素 width: 0% → 100% |
| underline draw | 同上但横向 |
| 数字滚动 | 按 frame 切换显示数字（Remotion） |

时序：开头 200ms 出 kicker，400ms 出标题，600ms 起内容错位出现。

## Remotion 标准导出

```tsx
export const FPS = 30;
export const WIDTH = 1280;
export const HEIGHT = 720;
export const DURATION_FRAMES = N * FPS;   // N 秒
```

Compiler 在渲染时按音频时长覆盖 `DURATION_FRAMES`（通过 Comp.tsx 的 `n_replaced` 路径），所以这个值给个合理 default 即可。

## HTML scene 模板风格

- `body { background: #0d1117; }`
- 居中 stage：`display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 50px;`
- 入场动画统一用 `@keyframes` + `animation-delay` 错位
- 用 ` <style>` 内联，**不依赖外部 CSS / 网络字体**
- viewBox 16:9 默认（1280×720），9:16 时改 stage 宽高
