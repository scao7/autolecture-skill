# 编译 / 预览 / 抽帧 — 坑速查

开发期不要全量编译。这一页固化「单镜预览 / fetch_frame 解码 / 编译成本 / 缓存失效」四个坑。
违反的后果：烧一堆 credits、抽帧抽不出来、改个分辨率全片重渲。

> 适用：**mcp** 模式（有 `get_snapshot` / `compile` / `fetch_frame` 工具）。zip 模式没这些工具，跳过。

---

## 1. 单镜预览 — 没有原生入口，靠覆写 main.tex

AutoLecture **没有**「只编译第 N 镜」的入口。开发期想单看某一镜，唯一办法是
**临时把 main.tex 覆写成一个只含那一个 view 的文档**，编译，看完再恢复。

⚠️ 子 tex（`\input{}` 进来的片段）**必须是 body 片段**：
- 不能带 preamble（`\title` / `\aspect` / `\style` / `\voice`）。
- 不能带 `\begin{videotex}` / `\end{videotex}`。
- 里头就是裸的 `\begin{view}...\end{view}`。

所以不能直接编译一个子 tex，得套一层完整文档。步骤：

1. **先备份**真正的 main.tex（`get_snapshot` 先存一份内容，或本地留副本）。
2. **覆写 main.tex** 成一个单 view 文档（preamble 照抄原片，body 只留目标镜）：
   ```latex
   \title{preview}
   \aspect{16:9}                 % 跟正式片一致，别在这里改分辨率(见第 4 节)
   \style{...原片同款...}
   \voice{...原片同款...}

   \begin{videotex}
   \begin{view}[title=scene_07]
     \say{这一镜的旁白原文照抄}
     \htmlFile{scenes/hd_07.html}
   \end{view}
   \end{videotex}
   ```
   用 `write_file` / `edit_file` 写回 main.tex。
3. `compile` → `get_status` 等完 → `fetch_frame` 看帧（见第 2 节）。
4. **看完立刻把 main.tex 恢复**成备份的全片版本。别把单镜文档留在云端当正式片
   （resume 时会把它误当真相——见 SKILL.md「真相在云端」铁律）。

> 迭代多镜时：每改一镜，覆写 → 编 → 抽帧 → 恢复，循环。比全量编译省 90%+ credits。

---

## 2. fetch_frame — 三个反直觉点，照做

`fetch_frame` 抽某一镜某一时刻的 PNG。三个坑全都会让你抽空：

### (a) scene_id 传的是 `content_hash`，不是 view 的 title

`fetch_frame` 的 scene_id 参数要传**那个 block 的 `content_hash`**，
从 `get_snapshot` 的 `blocks[].content_hash` 取。**不是** view 的 `title`，
**不是** 序号，**不是** 文件名。

```python
snap = get_snapshot(project_id)        # MCP 工具
block = snap["blocks"][6]              # 第 7 镜（0-based）
scene_id = block["content_hash"]       # ← 传这个
# fetch_frame(scene_id=scene_id, t=1.5)
```

### (b) 返回是超大 JSON，被落盘到 `/mnt/user-data/tool_results/...json`

PNG 是 base64 塞在 JSON 里的，体积很大，工具结果不会内联回对话，而是
**落盘**到 `/mnt/user-data/tool_results/<某哈希>.json`。你拿到的是这个**文件路径**。

### (c) base64 在 `inner["image"]["data"]`，得自己解码成 .png

落盘的 JSON 结构是套了两层的。外层是个 list，第 0 个 element 的 `text` 字段
是一个 **JSON 字符串**，再 `json.loads` 一次才到 `inner`，PNG base64 在
`inner["image"]["data"]`。解码：

```python
import json, base64, pathlib

results_json = "/mnt/user-data/tool_results/<那个文件>.json"   # fetch_frame 返回的路径
outer = json.loads(pathlib.Path(results_json).read_text())
inner = json.loads(outer[0]["text"])          # 注意：再 loads 一层
png_b64 = inner["image"]["data"]              # base64 字符串
pathlib.Path("/tmp/frame.png").write_bytes(base64.b64decode(png_b64))
# 然后 Read /tmp/frame.png 看图
```

解出来 Read 那张 .png 就能肉眼检查这一镜渲成什么样。

---

## 3. 编译成本量级 — 编前必须提示

全量编译又贵又慢：**每镜现合成中文 TTS + 1080p 实时录屏**，成本随旁白长度、
分辨率上升。参考量级：

| 规模 | 首次全量编译成本 |
|---|---|
| 17 镜（每镜 TTS + 1080p 录屏） | ≈ **375 credits** |

**单镜** ≈ 全量 / 镜数，量级小得多 → 所以开发期单镜迭代。

规则：
1. **开发期只用单镜预览**（第 1 节）迭代视觉 / 时序。
2. **只在最后做一次全量编译**出片。
3. **每次全量 compile 前，先跟用户提示成本量级**（按镜数 × 旁白长度 × 分辨率估），
   别闷头烧 credits。

---

## 4. 缓存随 canvas 失效 — 别在迭代中途改分辨率

`\aspect{}` 的分辨率在**编译期逐 block 生效**：每个 view block 原生渲染到目标尺寸
（manim / html / remotion 都按这个 canvas 出帧）。

所以**改分辨率 = 改了 canvas = 所有 block 的 content_hash 变 = 全量 cache miss = 全片重渲**。
没有「只把分辨率切一下、复用旧帧」这种事。

规则：
- 分辨率（`\aspect{16:9, 1080p}` 里的 `1080p`）**一开始就定死**，迭代期别动。
- 单镜预览（第 1 节）里的 `\aspect` 也保持跟正式片一致——在预览文档里改分辨率，
  既污染缓存、预览又跟成片不一致。
- 真要出 4K，等内容定稿后再把 `\aspect{16:9, 4k}` 改上去做**那一次**全量 compile，
  接受全片重渲的成本。
