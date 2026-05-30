# 两种运行模式 — Claude 速查表

每条 workflow 都得**显式分支**。这一页列每个动作在 **mcp**(有 MCP 工具)和 **zip**(默认 / 网页端)下应该怎么做。

> **判定**:看 Claude 当前工具列表里有没有 autolecture MCP 工具(`create_project` / `write_file` / `compile` / `fetch_frame`…)。
> - **有** → `mcp` 模式(直接用工具一条龙)。
> - **没有** → `zip` 模式(产 zip 让用户上传)。
>
> 这是 Claude 自己看得见的事实,**不跑脚本、不看本地文件、不看 auth**。没 MCP 工具时想引导用户连接器,见 SKILL.md 入口①。

---

## 每个动作两种模式怎么做

| 信息/动作 | MCP(有 MCP 工具) | ZIP(无,含网页端) |
|---|---|---|
| **建项目 / 写文件 / 传素材 / 编译 / 拿 mp4** | MCP 工具一条龙:`create_project` → `write_file`/`edit_file` → `add_asset` → `compile`+`get_status` → `get_output` | **打包 zip** 让用户拖到 [autolecture.ai](https://autolecture.ai) |
| **编译失败,Claude 自修一遍** | `get_status` 结构化错 → `edit_file` 改 → `fetch_frame` 看帧 → `compile` 单块重渲(其余命中缓存) | **不可能** —— 用户在 web 看错;skill 最后提示怎么 debug |
| **看某 view 真渲出来的样子** | `fetch_frame(hash, t)` PNG | **不可能** —— 本地 render 当替代(L3 harness 渲 `\htmlFile{}`) |
| **看某 view 的音频波形** | `fetch_waveform(hash)` PNG | **不可能** —— 本地 `ffprobe` 拿 duration 替代 |
| **增量编译(只重渲改动块)** | `compile` 带 only-block | **不可能** —— 每次重打 zip |
| **voice clone 注册 / ✦ 余额 / quota** | 看 `whoami` 给的信息;拿不到就同 zip 问用户 | `AskUserQuestion` 或保守默认;README 让用户 web 自查 |
| **上传前成本预估** | 一般无 dry-run 工具 → 跳过;README 写估算 | 跳过;README 写估算 |
| **harness check / L3 render**(本地静态分析 + Chromium) | 跑(跟模式无关) | 跑 |
| **harness `voice_clone_consistency`** | 有 `whoami` 等工具就核;没有退化为 consistency-only | consistency-only:部分 `\say` 有 `voice=mine` 部分没 → 警告 |

---

## 简明规则给 Claude 用

**每条 workflow 第 0 步:** 看工具列表有没有 autolecture MCP 工具 → 有 = **mcp**,没有 = **zip**。

**遇到需要用户状态的事**(voice clone / balance / quota):
- **mcp** → 看 `whoami` 等工具给的;拿不到就同 zip 问用户
- **zip** → `AskUserQuestion` 或保守默认

**遇到需要 cloud 反馈的事**(实际编译看效果 / 看渲出 PNG):
- **mcp** → `compile` + `get_status` + `fetch_frame` 工具
- **zip** → 本地 harness L3 render 当替代(看 HTML 渲出);没替代就放弃这步

**最后交付:**
- **mcp** → MCP 工具一条龙(_delivery.md 路径 A),交 Studio URL
- **zip** → `package_zip.py` 打 zip,告诉用户去 autolecture.ai 拖(路径 B)

---

## 跟 workflows/_delivery.md 的关系

- **路径 A · MCP 直驱** = mcp 模式的交付路径(首选)
- **路径 B · zip** = zip 模式的交付路径(无 MCP / 网页端唯一选项)

skill workflow 走完按模式:
- mcp → 路径 A(MCP 工具一条龙,交 Studio URL)
- zip → 路径 B 是唯一选项
