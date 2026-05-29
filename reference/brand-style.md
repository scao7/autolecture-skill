# Brand Style — AutoLecture 品牌一致视觉(浅色 cream + navy + tan 渐变)

> **何时用这个,何时用 [`palette.md`](palette.md):**
> - **brand-style.md(本文)** = 内容要"挂 AutoLecture 招牌"——官方 demo / teaser / 教程 / 上首页的 showcase / 给内测用户看的功能片。视觉跟 [autolecture.ai](https://autolecture.ai) 网站、Studio、watermark 同一调子,**品牌一致**。
> - [`palette.md`](palette.md)(editorial dark)= **内容本身是主角**的 vlog / 论文讲解 / 个人叙事——深底 + 海洋蓝那套,通用编辑器风格,不绑品牌。
>
> **一个项目内只用一套,别混。**两套基色对调(cream vs #0d1117)、文字色相反,混着用会很跳。
>
> ⚠️ **强提示:不确定时也别两套都拿,问用户或默认 editorial dark。**brand-style 是**用 AutoLecture 名义对外**时的统一外观,误用比不用更糟(看上去山寨自己)。

---

## Source of truth

色值与 token 抄自 **`Auto_Lecture/frontend/src/styles.css`**(`:root` 块,2026-05 时点);如果将来网站改主题,先改那个文件,再同步本文。Logo 取自 `backend/static/watermark/autolecture-logo.png`(840×216)。

---

## Palette(逐字镜像 styles.css 的 `--brand-*` / `--bg-*` / `--fg-*`)

### Brand 主色(取自小鸭/小鸡 logo)
```
brand-cream:     #f4e5bd   /* chick body — 大面积品牌色 */
brand-tan:       #d9b47b   /* outline / "ginger" — 描边与暖部 */
brand-navy:      #234976   /* wordmark / 主 CTA — 也是默认正文 */
brand-navy-deep: #1a3554   /* hover / pressed navy */
brand-cheek:     #7a1f1f   /* 极少用,仅强强调,一个点的量 */
```

### 表面(由外到内逐层加奶油色,**不要黑底**)
```
bg-0: #fefcf6   /* 页面外层 — 最浅 cream */
bg-1: #ffffff   /* 主面板 / 卡片 */
bg-2: #f6efde   /* 次面板 / hover */
bg-3: #ece4d0   /* popover / pressed */
```

### 文字(navy 阶梯,**不要白字**)
```
fg-0: #234976   /* 主文字 = 品牌 navy,与 wordmark 同色 */
fg-1: #4a6585   /* 副文字 */
fg-muted: #82929f
fg-dim:   #aab3bf
```

### 边框 / 链接 / 语义色
```
border:        rgba(35,73,118,0.14)   /* navy 调透明,落 cream 上不刺眼 */
border-soft:   rgba(35,73,118,0.07)
border-strong: rgba(35,73,118,0.30)

link:    #234976           /* 与 accent 同色,内联链接不抢 CTA */
accent:  #234976           /* 实心 navy CTA */
accent-bg: rgba(35,73,118,0.10)

good: #2d8a3e   warn: #b58a1a   err: #c72d24
purple: #5e3aa0
```

### 品牌渐变(hero / AI engine pill / 强调点)
```
accent-grad:      linear-gradient(135deg, #234976 0%, #d9b47b 100%);
accent-grad-soft: linear-gradient(135deg, #23497615 0%, #d9b47b22 100%);
```
navy → tan 的暖向渐变,是**唯一的渐变样式**;别造别的(`linear-gradient(orange→red)` 之类不要)。

---

## 字体栈

```
sans: "Inter", "Noto Sans SC", -apple-system, BlinkMacSystemFont,
      "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
      sans-serif;
mono: ui-monospace, "SF Mono", Consolas, "Roboto Mono", monospace;
```

跟 [`palette.md`](palette.md) 一致(Inter 主、Noto Sans SC 处理中文),**唯一差别**是回落顺序里加了 Noto Sans SC——网站用它兜底,我们也跟上。

---

## 文字层级(brand 模式下的覆盖)

| 类型 | 大小 | 字重 | 颜色 |
|---|---|---|---|
| Hero 大标题 | 88–120px | 800–900 | `accent-grad` 渐变文字(`background-clip: text`) |
| 段落标题 | 24–32px | 700 | `fg-0` (#234976) |
| 正文 | 16–22px | 400–500 | `fg-1` (#4a6585) |
| 元信息 kicker | 12–14px | 600,letter-spacing 4–6 | `brand-tan` (#d9b47b) |
| 数字 / 大数据点 | 64–96px | 800 | `brand-navy` 主、`brand-tan` 次,**不要珊瑚红** |

---

## CSS 雏形(HTML scene 用,品牌版)

```html
<style>
  html, body {
    margin: 0; background: #fefcf6;   /* cream base */
    color: #234976;                   /* navy text */
    font-family: 'Inter', 'Noto Sans SC', system-ui, 'PingFang SC', sans-serif;
  }
  .stage { display: flex; flex-direction: column; align-items: center;
           justify-content: center; height: 100vh; padding: 56px; }
  .kicker { color: #d9b47b; font-size: 14px; font-weight: 700;
            letter-spacing: 6px; text-transform: uppercase; }
  h1 { font-size: 80px; font-weight: 900; letter-spacing: -2px;
       background: linear-gradient(135deg, #234976 0%, #d9b47b 100%);
       -webkit-background-clip: text; background-clip: text; color: transparent; }
  .card { background: #ffffff;
          border: 1px solid rgba(35,73,118,0.14);
          border-radius: 14px; padding: 28px 24px;
          box-shadow: 0 8px 24px rgba(35,73,118,0.06); }
  .num.navy { color: #234976; }   .num.tan { color: #d9b47b; }
  .pill { display: inline-block; padding: 4px 12px; border-radius: 999px;
          background: rgba(35,73,118,0.10); color: #1a3554;
          font-size: 13px; font-weight: 700; }
</style>
```

## Remotion 雏形(品牌 lower-third)

完整模板见 [`../templates/scene_brand_lower_third.tsx.tpl`](../templates/scene_brand_lower_third.tsx.tpl)。核心是:
```tsx
const C = {
  cream:  '#f4e5bd',
  tan:    '#d9b47b',
  navy:   '#234976',
  navyD:  '#1a3554',
  paper:  '#ffffff',
  ink1:   '#4a6585',
  border: 'rgba(35,73,118,0.14)',
  grad:   'linear-gradient(135deg, #234976 0%, #d9b47b 100%)',
};
```

---

## 透明叠加(`over=true`)在 brand 模式下的注意

跟 dark 一样的**铁律**:覆盖层 `AbsoluteFill` 仍然**不能**有任何不透明 `backgroundColor`——只有卡片元素能上底色。区别只在卡片本身:dark 用半透明黑玻璃,**brand 用半透明 cream/paper**:
```tsx
background: 'rgba(255,255,255,0.86)',     // paper 半透明(原色透出来时偏暖)
border: '1px solid rgba(35,73,118,0.16)',
boxShadow: '0 10px 30px rgba(35,73,118,0.18)',
color: '#234976',                          // navy 文字
```
比 dark 玻璃透得更"克制"——cream 项目里覆盖层不应过暗,否则像是脏掉。

---

## Mascot:小鸭/小鸡 🐥

logo 资源 `Auto_Lecture/backend/static/watermark/autolecture-logo.png`(840×216),可作 `\imageFile{logos/autolecture-logo.png}` 拉进项目当 watermark / outro 卡。

emoji 替代:**🐥**(小鸡,黄色对应 cream)优于🦆(鸭,蓝灰偏冷)——除非内容真的是鸭子(像那次养鸭 vlog,主题决定一切)。

参见 memory: `brand_mascot_duck.md` —— AutoLecture-specific mascot rules,**不要套用到其它 skill / 个人项目**。

---

## `\style{}` 推荐串(直接抄进 main.tex preamble)

```latex
\style{AutoLecture brand-light; cream 表面 #fefcf6→#ffffff→#f6efde 三层叠,navy #234976 主文字与 CTA,brand 渐变 navy→tan #d9b47b 用于 hero/AI engine pill;Inter + Noto Sans SC + PingFang SC fallback;克制动效,fade-up + 小幅 pop,渐变文字 background-clip;实拍叠加用半透明 paper 玻璃(rgba 0.86),不要深玻璃}
```

editorial 版仍在 [`palette.md`](palette.md) 的 `\style{}` 例子里,选一个。

---

## Do / Don't

| ✅ Do | ❌ Don't |
|---|---|
| cream 底 + navy 文字,渐变只走 navy→tan | 不要把 dark 套(#0d1117 + 海洋蓝 #6ec1e4)和 cream 套混用 |
| 用 `accent-grad` 渐变做 hero 大字 | 不要造彩虹渐变 / 三色渐变 / 黄到红等不在品牌内的 |
| 警告 / 错误用 `warn #b58a1a` 或 `err #c72d24`(都偏暖,跟 cream 协调) | 不要用 dark 套的珊瑚红 `#ee6c4d`——颜色刺眼且不在品牌色 |
| `\imageFile{logos/autolecture-logo.png}` 当 outro / corner mark | 不要随便造一个新 logo / 改 logo 配色 |
| 文字层级落到 navy 阶 `fg-0/fg-1/muted/dim` | 不要用纯黑 `#000` 文字——和 navy 不协调,看起来像没设计 |

---

## 整片基调对比(供决策时一眼对照)

| | brand-style(本文) | [`palette.md`](palette.md) editorial |
|---|---|---|
| 底色 | cream `#fefcf6` / paper `#ffffff` | 深底 `#0d1117` |
| 文字 | navy `#234976` 阶梯 | 白色阶梯 |
| 主色 / CTA | brand navy `#234976` | 海洋蓝 `#6ec1e4` |
| 暖部 / 强调 | brand tan `#d9b47b` / cream | 暖黄 `#f4d35e` |
| 警告 | warn `#b58a1a` / err `#c72d24` | 珊瑚红 `#ee6c4d` |
| 渐变 | navy → tan(品牌专用) | 不强求渐变 |
| 适用 | 官方品宣 / 教程 / 上首页 / SaaS 内置 demo | 个人 vlog / 论文讲解 / editorial 叙事 |
| 心理基调 | 暖、信任、产品感 | 冷、专注、内容感 |
