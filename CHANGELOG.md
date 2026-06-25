# Changelog

版本协商机制：skill 安装后是分发出去的拷贝，不会自动更新。mcp 模式下
agent 连上 `mcp.autolecture.ai/mcp` 后调 `server_info`，把返回的
`skill_version_current` 和 SKILL.md frontmatter 里的 `version` 对比 —
落后就提醒用户 `npx skills add scao7/autolecture-skill`（claude.ai 重传 zip）。
语法真相以 MCP 的 `get_dsl_spec` 为准；bundled `harness/spec/dsl.json`
只是 zip/离线模式的 fallback。

## 0.13.0 — 2026-06-25 — JSON-canonical authoring (state ops)

- **BREAKING: the project is now authored as a list of JSON shots via MCP state
  ops, not VideoTeX text.** The server fully migrated the MCP surface to
  JSON-canonical (`SKILL_VERSION_CURRENT` 0.13.0). The legacy VideoTeX tools are
  RETIRED and no longer in the tool list: `commit_files`, `edit_file`, the `.tex`
  `write_file`/`read_file`, `list_directory`/`search_files`/`move_file`/`delete_file`,
  `generate_full_from_storyboard`, `render_scene`, and the blocks-debug set
  (`fetch_frame`/`fetch_waveform`/`fetch_asset_frame`/`list_scene_versions`/
  `pick_scene_version`/`get_captions`/`get_snapshot`), plus `list_templates`.
- **New authoring surface:** `get_state` · `set_project` · `upsert_shot` ·
  `update_shot` · `remove_shot` · `reorder_shots` · per-shot `write_file` (scene
  CODE only, refuses `.tex`) · `render_shot` (per-shot still/clip). `compile` /
  `get_status` / `get_output` / `add_asset` / `transcribe` / `get_dsl_spec` stay.
- SKILL.md gains an authoritative **AUTHORING MODEL — v0.13** section that governs
  the file + the `workflows/` playbooks: any legacy "write `storyboard.tex` /
  `commit_files` / `fetch_frame`" instruction translates to the equivalent state
  op. Hand-written Manim/HTML/Remotion scene code + the audio-driven spine are
  unchanged; only the project-structure surface moved from `.tex` to JSON shots.
- Follow-up: the `workflows/` and `reference/` playbooks still carry VideoTeX
  phrasing in places — governed by the AUTHORING MODEL section for now; a full
  per-file rewrite is the next pass.

## 0.12.1 — 2026-06-22

- **MCP authoring now defaults to atomic `commit_files` for a complete view.**
  When a view changes both the active root tex and an external scene file, agents
  should land them in one SourceRevision via `commit_files`, then compile that
  block. `write_file` / `edit_file` remain for standalone single-file edits.
  This prevents resume/compile from seeing a root that references missing source,
  or a source file that has not been connected to the root yet.

## 0.12.0 — 2026-06-21

- **Cross-shot continuity is now named-anchor based: `[id=]` / `[ref=]`.**
  Give a shot a stable anchor (`\begin{view}[id=bars]`) and have later shots
  cite it (`[ref=bars]`); the compiler feeds the anchor's code into each
  citer's codegen so the sequence reuses the same composition (variable names,
  object count, colors, coordinates) and only changes what the description
  changes. This is what makes a multi-shot scene look coherent instead of like
  unrelated clips, and it now propagates into the FULL render (not just the
  storyboard still). The retired positional forms `ref=prev` / `ref=#N` are
  errors. Emit `[id=]`/`[ref=]` whenever consecutive shots share a scene.

## 0.11.0 — 2026-06-17

- **English-first.** Translated the whole skill to English for the US Claude Code
  marketplace — SKILL.md (incl. the `description` frontmatter that shows in the
  listing), all `reference/`, `workflows/`, and `genre-skills/`. Instructions are
  English-PRIMARY; output still follows the user's topic language. Intentional
  Chinese example VALUES are kept (Whisper-typo tables, `\say` example narrations
  for Chinese-topic demos, platform names like Bilibili/Douyin).

## 0.10.1 — 2026-06-17

- **商城 playbook 同步开放/封闭分层**(`reference/marketplace.md`):
  `list_gallery_templates`/搜索**只列官方(curated)题材**;用户发布的社区模版
  `official=false`+`unlisted`,**只能按确切 slug 加载**,不进模糊浏览列表。
  用户报具体社区模版名时别模糊匹配——按确切 slug 直接 `get_template_card`/
  `use_gallery_template`(两者解析任意 id)。
- **dsl.json drift fix**:`\image` / `\imageFile` 补上 `style` opt(从后端 spec.py regen)。

## 0.10.0 — 2026-06-13

- 入口加 **freestyle / 模版商城分叉**(入口 ②):定好运行模式后先问用户「自由创作」
  还是「去模版商城找专用模版」。自由创作 = 现有 workflows 按主输入分流(独立可用,
  不依赖商城);模版商城 = 服务端按题材(genre)交付的专用创作指令卡,经 MCP 按需拉取。
- 新增 [`reference/marketplace.md`](reference/marketplace.md):商城路径 playbook
  ——列题材 → 选模版 → `get_template_card` 拉创作指令卡 → `use_gallery_template`
  克隆起始项目 → 按卡 recipe 接管。仅 mcp 模式(zip 回退 freestyle);含 entitlement
  鉴权与 `publish_template` 自建模版说明。
- **跨 agent 设计**:商城内容全部住服务端、经 MCP 交付,不做本地安装 skill,所以
  Claude / Codex 等任何连了 `mcp.autolecture.ai/mcp` 的 agent 都能消费同一批模版。
  marketplace.md 用 agent 中立措辞写,作为后续多 agent 打包的抽象缝。
- 新增 [`genre-skills/fable-science.md`](genre-skills/fable-science.md):第一张
  **题材 recipe 卡**(寓言科普)——把抽象/技术概念讲成手绘 storybook 寓言。服务端
  模版卡 `demos/cards/fable_paper.md` 引用它作配套 recipe;后续题材卡照此格式扩。

## 0.9.1 — 2026-06-10

- HARD BAN 17: 禁止「全写完再编译」—— 每写一个 view 当场增量编译验证;
  配套上下文卫生(不复述 scene 代码 / edit_file 改文件 / fetch_frame 限 1-2 帧)。
  起因: claude.ai 长视频会话批量写完再编,上下文爆掉 "conversation too long",
  已写内容全未验证。MCP 工具描述(compile/write_file/fetch_frame)同步烧入此纪律,
  没装 skill 的纯 MCP 会话也能看到。

## 0.9.0 — 2026-06-10

- 版本协商：SKILL.md frontmatter 加 `version:`；mcp 模式启动先调 `server_info` 对账
- 模板起步路径：`list_gallery_templates` → `get_template_card` → `use_gallery_template`
- 视觉复刻 workflow（`workflows/replicate-style.md`）：参考视频抽帧串读动效 → 手写 scene 复刻
- 录屏双轨编排：screen_cam 录制产出 screen/camera 两条原始轨，画中画用模板编排可后期调
- 素材级文稿字幕约定（`{media}.transcript.txt`）+ `\subtitle` 样式 opts
- 剪辑库（`\cliplibrary` + `\video{@name}`，BibTeX 模式）
- knowledge-only 收敛：移除本地渲染探针与 SDK 残留，skill 只做知识 + 编排

## 0.x（更早）

见 git log — 2026-05-20 由 autolecture-demo 更名而来；2026-05-30 SDK 退役、
MCP 成为唯一编程路径；2026-06-09 收敛为 mcp / zip 两种交付模式。
