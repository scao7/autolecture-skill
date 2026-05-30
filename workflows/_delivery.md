# 交付（所有 workflow 的最后一步）

**先判定运行模式 → 决定走哪条路径**(对应 [`reference/runtime-modes.md`](../reference/runtime-modes.md)):

看工具列表有没有 autolecture MCP 工具 —— 有 = **mcp**(路径 A),没有 = **zip**(路径 B)。

| 模式 | 交付路径 | 备注 |
|---|---|---|
| **mcp**(有 MCP 工具) | **路径 A · MCP 直驱**(首选) | Claude 用 MCP 工具云端建项目 + 写文件 + 编译 + 拿 mp4,一条龙;失败能 `fetch_frame` 看帧调 |
| **zip**(无 MCP,含网页端) | **路径 B · zip** | Claude 产出项目 zip,用户拖到 autolecture.ai 上传 |

---

## 路径 A · MCP 直驱（首选 —— 当工具列表里有 autolecture MCP 工具时）

Claude 直接用 autolecture 的 MCP 工具,在云端一条龙做完。本地 `<work>` 还是照常先把 `main.tex` + `scenes/` + 素材写好(workflow 该做的都做),然后推到云端项目:

1. **建项目** —— `create_project`(或 `list_templates` 选个模板再建),记下 project id。
2. **写文件** —— `write_file` 把 `main.tex` 和每个 `scenes/*.{tsx,html,py}` 写进项目(路径沿用本地 `<work>` 结构);改动用 `edit_file`。
3. **传素材** —— `add_asset` 上传录音 / PDF / 实拍 / 本地图。
4. **编译** —— `compile`(或单 scene `render_scene`)触发,`get_status` 轮询到完成,`get_output` 拿 mp4 + Studio URL。
5. **失败自己看帧调**(MCP 模式相对 zip 的核心价值)—— `get_status` 给结构化错(哪个 block / category / 出错源码)→ `edit_file` 改那个文件 → `fetch_frame` 拉该 view 渲出的 PNG 确认 → 只重渲改动的块(`compile` 带 only-block,其余命中缓存)。`fetch_waveform` 看音频形状。**每块最多自修 3 次**,不行带证据(出错片段 + 帧 + Studio URL)升级用户。
6. **交付** —— 回 Studio URL + 一句「怎么用」;用户可在 Studio 里继续改 / 点 ▶ Recompile。

> 工具名前缀随客户端而定(如 `autolecture:compile` / `mcp__autolecture__compile`)。参数 schema 以你实际看到的工具定义为准 —— 不确定就先 `list_projects` / `whoami` 探一下。

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
