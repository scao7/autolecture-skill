# 模版商城路径（marketplace）

用户在入口选了「② 去模版商城找专用模版」时走这条。商城里每个**题材**
（genre）是一份服务端的**专用创作指令包**（agent card）——选中一个题材/模版后，
它就接管这条片子怎么做：用哪些引擎、节奏、aspect、结构、配音风格。

> **设计意图（跨 agent）**：商城内容**全部住在服务端**，经 autolecture MCP
> 工具按需拉取，不是本地安装的 skill。所以任何能连 `mcp.autolecture.ai/mcp`
> 的 agent（Claude / Codex / …）都能直接消费同一批模版，零安装、即点即用。
> 这条 playbook 的逻辑只依赖 MCP 工具名，不依赖某个客户端的专有能力。

---

## 前置：商城只在 mcp 模式可用

商城是服务端 gallery，**必须有 autolecture MCP 工具**才能浏览/克隆。

- **mcp 模式** → 照下面走。
- **zip 模式**（claude.ai 网页端 / 没连接器）→ 商城用不了。告诉用户：要么
  连上 `mcp.autolecture.ai/mcp` 连接器再来，要么走**自由创作**（freestyle，
  见 SKILL.md 入口 ② 的 freestyle 分支，不依赖商城）。

---

## 流程（最多两问，简单易用）

### 1 · 列出题材 → 让用户选

调 `list_gallery_templates`，返回的列表里每项带 `genre`（题材）、`slug`、
`title`、`description`、`engines`、`duration_sec`、`has_agent_card`。

- **按 `genre` 分组展示**给用户（如：科普讲解 / AI 短剧 / 数学公式 / 产品介绍 /
  数据可视化 / 口播带货…）。列表是 slim 的，**不含创作指令正文**——正文按需拉，
  省 context。
- 用 `AskUserQuestion`（Claude）或等价的选项呈现让用户先选**题材**，再在题材下选
  **具体模版（slug）**。题材内只有一个模版就直接定。

### 2 · 拉选中那张卡的创作指令包

对用户选的 `slug` 调 `get_template_card(slug)`（或 `get_template_skill(slug)`，
若服务端已提供）——返回该模版的**专用创作指令**（markdown）：干什么用、哪些
scene/asset 是待替换占位、哪些旋钮要调、引擎/节奏/结构/配音风格、1~2 个示例 view。

- **只拉选中的这一张**，别把所有卡正文都拉进来（token 控住）。
- 读完这份卡，**后续就按它的 recipe 创作**，它是这条片子的权威指引。

### 3 · 克隆起始项目

调 `use_gallery_template(slug)`——把模版的 `main.tex` + scene 文件 + 素材整体
克隆成用户名下一个新项目，返回 `project_id` + `studio_url`。这些模版都是
**编译验证过的真项目**，在它基础上替换占位比从零写快得多。

### 4 · 按卡接管创作

之后就是正常的 audio-first 创作回路，但**遵循卡里的 recipe**（引擎选择、节奏、
结构、配音风格都照它）：

- 替换占位 scene / 素材为用户的真实内容（HARD BAN 2：每个 scene 按内容定制设计，
  不许同模板填不同字）。
- **每替换/新增一个 view 当场 `compile` + 看 `block_errors` + 修**（HARD BAN 17，
  增量编译）；关键视觉用 `fetch_frame` 抽 1~2 帧验证。
- 多镜任务先做 1 个样张签字再批量（HARD BAN 13）。
- 交付走 [`../workflows/_delivery.md`](../workflows/_delivery.md)。

---

## 门槛 / 鉴权（entitlement）

模版可能带 `entitlement`（免费 / Pro / 一次性解锁）。若 `get_template_card` /
`use_gallery_template` 因权限被服务端拦截（返回鉴权类错误），**如实把升级/解锁
提示转达用户**，别降级硬塞——服务端是唯一裁决方。

---

## 和自由创作的关系

- 商城路径 = 选好题材，照专用 recipe 走，省去从零定方案。
- 自由创作（freestyle）= 没有合适题材、或想完全自定义时走，按主输入类型
  分流到 `workflows/`，不依赖商城。
- 两条都汇到同一个交付步骤 [`../workflows/_delivery.md`](../workflows/_delivery.md)。

> **发布自己的模版**：用户做完一个满意的项目，可以把它固化成一个新的题材模版
> 发布到商城（agent 从成品反推创作指令草稿 → 用户审核填题材/价格 → 服务端
> 校验编译 → 上架）。见 `publish_template`（服务端提供该工具时启用）。
