# 交付（所有 workflow 的最后一步）

**先判定运行模式 → 决定走哪条路径**(对应 [`reference/runtime-modes.md`](../reference/runtime-modes.md)):

看工具列表有没有 autolecture MCP 工具 —— 有 = **mcp**(路径 A),没有 = **zip**(路径 B)。

| 模式 | 交付路径 | 备注 |
|---|---|---|
| **mcp**(有 MCP 工具) | **路径 A · MCP 直驱**(首选) | Claude 用 MCP 工具云端建项目 + 写文件 + 编译 + 拿 mp4,一条龙;失败能 `fetch_frame` 看帧调 |
| **zip**(无 MCP,含网页端) | **路径 B · zip** | Claude 产出项目 zip,用户拖到 autolecture.ai 上传 |

---

## 路径 A · MCP 直驱（首选 —— 当工具列表里有 autolecture MCP 工具时）

Claude 直接用 autolecture 的 MCP 工具在云端一条龙做完。

> ⚠️ **铁律:增量持久化 —— 每写完一个 view 就立刻落到云端,绝不攒到最后一次性写。**
> 一个长项目要写十几个 scene,如果先在脑子里/本地全攒好、最后才一把 `write_file` 推上去,
> 一旦中途 **tool-use 上限用完**、断线、或某次调用失败,**全部白做**。增量写则:已写的
> view 已经在云端项目里、有效、可编译;接着干只需 `read_file("main.tex")` 看写到哪了,从后面继续。

1. **建项目 + 写骨架** —— `create_project`(或 `list_templates` 选模板)拿 project id。
   立刻 `write_file("main.tex", …)` 写一个**只有顶层宏 + 空 body 的骨架**,末尾留住 `\end{videotex}` 当锚点:
   ```
   \title{…}\aspect{…}\style{…}\voice{…}
   \begin{videotex}
   \end{videotex}
   ```
   这时云端已是一个能编译的(空)项目 —— 之后每个 view 都往这个锚点前插。

2. **逐 view 增量写(核心循环 —— 每个 view 重复)**:每做好**一个** view 就当场:
   a. `write_file("scenes/scene_NN.{html,tsx,py}", 源码)` —— 写这个 view 的场景文件。
   b. `edit_file("main.tex", old_string="\end{videotex}", new_string="<这个 view 的 \begin{view}…\end{view}>\n\end{videotex}")` —— 把这个 view **追加到锚点前**。`\end{videotex}` 唯一,可反复用;插完它还在,下个 view 继续插。
   c. 这个 view 用到素材就 `add_asset` 传上去。
   d. (推荐)`compile`(只渲这一块)+ `get_status` —— **当场渲它、当场发现错**,而不是堆到最后一起炸。
   → 每个 view 一写完就在你的平台上落地了。**中途任何中断都不丢已写的部分。**

3. **全部 view 写完 → 整片编译** —— `compile`(整项目)→ `get_status` 轮询到完成 → `get_output` 拿 mp4 + Studio URL。(单块都在 step 2d 渲过的话,这步基本全命中缓存,很快。)

4. **失败自己看帧调**(MCP 模式相对 zip 的核心价值)—— `get_status` 给结构化错(哪个 block / category / 出错源码)→ `edit_file` 改那个文件 → `fetch_frame` 拉该 view 渲出的 PNG 确认 → 只重渲改动的块(`compile` 带 only-block,其余命中缓存)。`fetch_waveform` 看音频形状。**每块最多自修 3 次**,不行带证据(出错片段 + 帧 + Studio URL)升级用户。

5. **交付** —— 回 Studio URL + 一句「怎么用」;用户可在 Studio 里继续改 / 点 ▶ Recompile。

> 工具名前缀随客户端而定(如 `autolecture:compile` / `mcp__autolecture__compile`)。参数 schema 以你实际看到的工具定义为准 —— 不确定就先 `list_projects` / `whoami` 探一下。
> **续传**:对话被打断后重连,先 `read_file("main.tex")` 看已经写了哪些 view,从 `\end{videotex}` 锚点前继续插,别从头重写。

---

## 路径 B · 打包 zip（无 MCP 时 / claude.ai 网页端）

```bash
python3 scripts/package_zip.py --work <work> --out <work>/autolecture_demo.zip
```

[`scripts/package_zip.py`](../scripts/package_zip.py) 会：
- 把 `<work>` 全部内容打到一个 zip（`main.tex` + `scenes/` + 素材）
- 校验关键文件都在（每个 `\manimFile` / `\htmlFile` / `\remotionFile` / `\imageFile` / `\audio` / `over=` / PDF 引用的文件都存在），缺了就 hard-exit
- 输出 zip 路径 + 文件清单

回复用户：zip 路径 + 「拖到 <https://autolecture.ai> 上传，会自动识别 main.tex、把素材注册好；之后在 Studio 里改代码 / 点 ▶ Recompile」。（网站 from-zip 已验证：自动加 `\begin{videotex}` 外壳、注册 assets、`staticFile()` 能拿到上传的 PDF / 图 / 视频。）

---

两条路径**都**经 AutoLecture 编译收费（skill 代码免费，任何入口的编译都收费）。
最后回复用户：交付物（Studio URL,或 zip 路径）+ 简短一句「怎么用」。
