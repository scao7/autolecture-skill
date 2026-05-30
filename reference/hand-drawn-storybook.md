# Hand-drawn storybook — 手绘 storybook 视觉技法 recipe

这是一份**可直接照做**的 `\htmlFile{}` 技法,内联 SVG 做出「手绘绘本」质感:
钢笔描边逐条画出来、颜料随后淌进去、整张图带轻微抖动 + 持续微动。
2026-05-30 在「百巧城 / MCP 寓言」17 个场景里验证过 17 次,固化成 reference,
**别让下次重新发明**。

> 适用:寓言体讲技术 / 概念拟人化 / 任何想要「温暖、手作、非 PPT」的成片风格。
> 全片用同一套手绘 HTML/SVG 不算 PPT——**成体系的动效手绘是一种引擎**,
> 静态堆叠才像 PPT。视觉一致性 > 引擎数量(见 [`engine-routing.md`](engine-routing.md))。

---

## 五个零件(缺一不可的就前三个)

| 零件 | 作用 | 关键属性 |
|---|---|---|
| 1. 内联 SVG | 画面主体,不依赖外部资源 | `<svg viewBox>` 直接写进 HTML |
| 2. 描边 draw | 线条「被画出来」 | `pathLength=1` + `stroke-dasharray/offset` + `@keyframes draw` |
| 3. 填充 flood | 颜料在线条之后淌进去 | `.f { opacity: 0→1 }`,`animation-delay` ≥ 描边时长 |
| 4. 钢笔抖动 | 手作质感(线条不是尺子画的) | `feTurbulence` + `feDisplacementMap` 套外层 `<g>` |
| 5. 持续微动 | 长音频不冻结 | `bob` / `sway` / `spin` 循环 |

前三个是骨架,第 4 个给「手绘味」,第 5 个是 audio-first 的硬要求(见下「入场预算」)。

---

## 1. 描边 draw —— 线条被画出来

核心:给每条 `<path>` 设 `pathLength="1"`,这样无论真实路径多长,
`stroke-dasharray` / `stroke-dashoffset` 都按归一化的 `1` 来算,一个 `@keyframes` 通吃所有线。

```css
.s {
  fill: none;
  stroke: #234976;
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-dasharray: 1;        /* 配合 pathLength=1 */
  stroke-dashoffset: 1;       /* 初始全部「未画」 */
  animation: draw 1s ease forwards;
}
@keyframes draw {
  to { stroke-dashoffset: 0; }  /* 画完 */
}
```

```html
<path class="s" pathLength="1" d="M40 80 C 80 20, 160 20, 200 80" />
```

**多条线错峰 stagger**(像真人一笔一笔画,不是同时冒出来):

```css
.s:nth-child(1) { animation-delay: 0s;   }
.s:nth-child(2) { animation-delay: 0.15s; }
.s:nth-child(3) { animation-delay: 0.30s; }
```

约束:

- 单条 `draw` ~1s 足够;别超过 1.5s(见入场预算)。
- stagger 步进 0.1–0.2s;太密看不出笔触,太疏会拖过预算。
- `pathLength="1"` 写在 SVG 元素上(attribute),不是 CSS。

---

## 2. 填充 flood —— 颜料在线条之后淌进去

填充层独立于描边层,默认透明,描边画完后才 `opacity: 0→1` 淌进来。

```css
.f {
  opacity: 0;
  animation: flood 0.5s ease forwards;
  animation-delay: 1s;        /* ≥ 描边总时长,确保「先画线、后上色」 */
}
@keyframes flood {
  to { opacity: 1; }
}
```

```html
<!-- 填充层在前(底),描边层在后(盖在上面) -->
<path class="f" d="M40 80 C 80 20, 160 20, 200 80 Z" fill="#d9b47b" />
<path class="s" pathLength="1" d="M40 80 C 80 20, 160 20, 200 80" />
```

要点:

- `animation-delay` 至少等于「描边最后一条画完」的时刻,否则颜料早于线条出现,穿帮。
- 想要「水彩淌开」感:`flood` 时长稍长(0.5–0.8s)+ 轻微 `transform: scale(0.96→1)`。
- 一个区域一个 `.f`;不同区域可再叠各自的小 delay 做层次。

---

## 3. 钢笔抖动 —— feTurbulence + feDisplacementMap

把分形噪声当位移图,套在最外层 `<g>` 上,整张图的边缘就有「手抖、墨水洇」的不规则,
告别尺规般的死板。

```html
<svg viewBox="0 0 400 300">
  <defs>
    <filter id="rough">
      <feTurbulence type="fractalNoise" baseFrequency="0.02"
                    numOctaves="2" seed="7" result="noise" />
      <feDisplacementMap in="SourceGraphic" in2="noise"
                         scale="5" />   <!-- scale 4–6 是甜区 -->
    </filter>
  </defs>
  <g filter="url(#rough)">
    <!-- 所有 .s / .f path 放这里 -->
  </g>
</svg>
```

调参:

| 参数 | 取值 | 说明 |
|---|---|---|
| `scale` | **4–6** | 抖动幅度;>8 线条会断裂、糊掉 |
| `baseFrequency` | 0.01–0.03 | 越大越「毛」;太大像噪点 |
| `numOctaves` | 1–2 | 2 够用,更多只是变慢 |
| `seed` | 任意整数 | 换 seed = 换一种抖法,每个场景给不同 seed 避免雷同 |

注意:filter 套在**外层 `<g>`**(整组一起抖),不要逐 path 套(各抖各的会错位)。

---

## 4. 持续微动 —— bob / sway / spin

入场画完后,留至少一个**循环**微动,让长音频下画面有呼吸感(audio-first 硬要求)。

```css
/* 上下浮动 —— 角色、漂浮物 */
@keyframes bob  { 0%,100% { transform: translateY(0);    } 50% { transform: translateY(-6px); } }
/* 左右轻摆 —— 旗帜、树、招牌 */
@keyframes sway { 0%,100% { transform: rotate(-2deg);     } 50% { transform: rotate(2deg);     } }
/* 缓慢旋转 —— 齿轮、星、光环 */
@keyframes spin { to      { transform: rotate(360deg);    } }

.bob  { animation: bob  3s ease-in-out infinite; }
.sway { animation: sway 4s ease-in-out infinite; transform-origin: top center; }
.spin { animation: spin 12s linear infinite;     transform-origin: center;     }
```

- 周期给 3–12s,慢即高级;`infinite` 保证不冻结。
- `sway` / `spin` 记得设 `transform-origin`(摆动支点 / 旋转中心)。
- 微动施加在 SVG 元素或包裹 `<g>` 上,与 draw/flood 不冲突(不同属性轴)。

---

## 5. 品牌色 + 标题/字幕

手绘 storybook 用 [`brand-style.md`](brand-style.md) 的浅色 cream 调子:

```
cream  #fefcf6   /* 背景 / 纸面 */
navy   #234976   /* 描边 stroke / 主文字 */
tan    #d9b47b   /* 填充 / 暖色块 */
```

**标题 / 字幕用 HTML overlay**,不画进 SVG(SVG 留给插画):
绝对定位一层 `<div>`,文字配 `rise` 入场。

```css
body { background: #fefcf6; }
.title {
  position: absolute; left: 0; right: 0; bottom: 8%;
  text-align: center; color: #234976;
  font-family: 'KaiTi','STKaiti','Songti SC',serif;  /* 手作感衬线/楷体 */
  font-size: 44px; font-weight: 700;
  opacity: 0; animation: rise 0.6s ease forwards; animation-delay: 1.1s;
}
@keyframes rise { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
```

字幕沿用 audio-first 规则:旁白走 `\say`(默认不烧字幕,要 `burn=on` 才烧);
标题这类「画面文字」才用 overlay。

---

## 入场预算(audio-first 铁律)

时长由 `\say` 驱动,**HTML scene 不知道音频多长**——compiler 不改你的 CSS keyframes,
Playwright 录满 `target_duration` 秒,入场动画跑完之后就是 frozen frame。
所以(见 [`audio-first.md`](audio-first.md)):

1. **入场动画(画线 draw + 淌色 flood)≤ 约 1.5s 全部画完。**
   - 描边 ~1s(含 stagger),填充 `delay 1s` + ~0.5s,卡在 1.5s 内收尾。
2. 1.5s 之后**只留** `bob` / `sway` / `spin` 一类**循环**微动。
3. **禁止**排长队 sequential delays(`delay: 0s; 3s; 6s; 9s`)——音频若只有 5s,
   后面的元素永远不出现。

**自检一句**:打开 scene,问自己「第 2 秒之后画面还有没有在动?动的是不是只有
`infinite` 的 bob/sway/spin?入场是不是 1.5s 内就画完了?」三个都「是」才算合规。

---

## 最小可跑骨架(复制即用)

一个完整的手绘 scene:cream 纸面 + 一个 tan 太阳(描边→填充→旋转)+ navy 标题 overlay。

```html
<!doctype html>
<html><head><meta charset="utf-8"><style>
  html,body { margin:0; height:100%; }
  body {
    background:#fefcf6;
    display:flex; align-items:center; justify-content:center;
    font-family:'KaiTi','STKaiti','Songti SC',serif;
  }
  .stage { position:relative; width:1280px; height:720px;
           display:flex; align-items:center; justify-content:center; }

  /* 描边 */
  .s { fill:none; stroke:#234976; stroke-width:4;
       stroke-linecap:round; stroke-linejoin:round;
       stroke-dasharray:1; stroke-dashoffset:1;
       animation:draw 1s ease forwards; }
  .s:nth-of-type(2){ animation-delay:.15s; }
  @keyframes draw { to { stroke-dashoffset:0; } }

  /* 填充(线画完之后) */
  .f { opacity:0; animation:flood .5s ease forwards; animation-delay:1s; }
  @keyframes flood { to { opacity:1; } }

  /* 持续微动 */
  .spin { transform-origin:center; animation:spin 14s linear infinite; }
  @keyframes spin { to { transform:rotate(360deg); } }

  /* 标题 overlay + rise */
  .title { position:absolute; bottom:8%; width:100%; text-align:center;
           color:#234976; font-size:44px; font-weight:700;
           opacity:0; animation:rise .6s ease forwards; animation-delay:1.1s; }
  @keyframes rise { from{opacity:0;transform:translateY(20px);} to{opacity:1;transform:translateY(0);} }
</style></head>
<body>
  <div class="stage">
    <svg viewBox="0 0 400 400" width="320" height="320">
      <defs>
        <filter id="rough">
          <feTurbulence type="fractalNoise" baseFrequency="0.02"
                        numOctaves="2" seed="7" result="n"/>
          <feDisplacementMap in="SourceGraphic" in2="n" scale="5"/>
        </filter>
      </defs>
      <!-- 抖动套外层 g + 持续旋转 -->
      <g filter="url(#rough)" class="spin">
        <!-- 填充层在底 -->
        <circle class="f" cx="200" cy="200" r="70" fill="#d9b47b"/>
        <!-- 描边层在上:圆 + 一道光芒 -->
        <circle class="s" pathLength="1" cx="200" cy="200" r="70"/>
        <path   class="s" pathLength="1" d="M200 90 V40 M200 360 V310
                 M90 200 H40 M360 200 H310"/>
      </g>
    </svg>
    <div class="title">百巧城的太阳</div>
  </div>
</body></html>
```

跑这个 scene:描边 ~1.15s 画完 → 1s 起填充淌入 → 1.1s 标题 rise →
之后太阳一直 `spin`。符合「入场 ≤1.5s,之后只剩循环微动」。

---

## 量产 checklist(17 镜验证过)

1. **先做 1 个样张镜** → 编译 → `fetch_frame` 抽帧 → 签字「可以」→ 才量产剩余镜
   (最值钱的一步,见主 workflow 的样张纪律)。
2. 全片**一套命名前缀**(如 `hd_01..hd_17`),换版顺手 `delete_file` 归档旧的。
3. 每个 scene 给不同 `seed`,抖法不雷同。
4. 品牌色三件套不跑偏:cream / navy / tan。
5. 每个 scene 过一遍上面那句「入场预算自检」。
