# Changelog

版本协商机制：skill 安装后是分发出去的拷贝，不会自动更新。mcp 模式下
agent 连上 `mcp.autolecture.ai/mcp` 后调 `server_info`，把返回的
`skill_version_current` 和 SKILL.md frontmatter 里的 `version` 对比 —
落后就提醒用户 `npx skills add scao7/autolecture-skill`（claude.ai 重传 zip）。
语法真相以 MCP 的 `get_dsl_spec` 为准；bundled `harness/spec/dsl.json`
只是 zip/离线模式的 fallback。

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
