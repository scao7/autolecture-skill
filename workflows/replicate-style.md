# 视觉复刻 — 看着参考视频"抄"动效与排版

输入：一个参考视频（YouTube 链接 / 本地文件 / 项目内资产）+ 你自己的内容。
输出：用参考视频的视觉语言（动效/排版/配色/节奏）呈现你的内容。

> ⚠️ **运行边界**：YouTube 拉取（yt-dlp）只在 **Claude Code 本地模式**做——
> 服务端代下载违反 YouTube ToS，永远不要把它做成平台功能或建议用户走 zip/云端。
> 参考视频若已是项目资产，则云端 MCP 模式也能走（用 `fetch_asset_frame` 看帧）。
> 复刻"风格"用于自己的内容；逐镜复刻他人完整作品的边界由用户自己把握。

## 流程

1. **取材**（按来源分流）
   - YouTube（仅本地）：`yt-dlp -f "bv*[height<=1080]" -o /tmp/ref.mp4 <url>`
   - 项目资产：跳过下载，后续抽帧用 MCP `fetch_asset_frame(project_id, rel_path, t)`

2. **抽帧串看动效**——动效要连续帧才能读，单帧只能读排版：
   - 先粗扫定位动效节点：`ffmpeg -i /tmp/ref.mp4 -vf "fps=1,scale=320:-2,tile=10x6" /tmp/ref_contact.png`（接触印相，一图概览全片）
   - 对每个目标动效抽 1 秒 8 帧的帧串：`ffmpeg -ss <t> -i /tmp/ref.mp4 -t 1 -vf "fps=8,scale=480:-2,tile=8x1" /tmp/fx_<name>.png`
   - 逐串判读并**写下结论**：入场方式（位移/缩放/淡入/遮罩揭示）、缓动感（spring 回弹 / ease-out 急停 / linear）、stagger 间隔、停留时长、出场方式

3. **提炼风格 token**：配色（吸 3-5 个主色 hex）、字体气质（衬线/黑体/等宽、字重）、圆角/描边/阴影语言、安全区习惯。写进项目 `\style{}` 与场景常量。

4. **手写 scene 复刻**：从 [`templates/`](../templates/) 选最近的骨架，把第 2 步的结论翻译成代码参数（remotion: `spring({damping})`/`interpolate+Easing`；html: CSS animation/SMIL）。已沉淀的反推配方在 [`reference/borrowed-techniques.md`](../reference/borrowed-techniques.md)——新反推出的好配方应回写到那里。

5. **对照迭代**：编译 → `fetch_frame`（渲染块）与参考帧串**并排**比对 → 调参数重渲。常见差距按序排查：缓动类型 → 时长 → stagger → 字号/字距。

## 预期管理（要先告诉用户）

文字/MG 动效（标题、信息卡、图表、转场）可达"神似"；缓动与时长是观感级近似；
3D/粒子/实拍合成只能仿意境；不做像素级逐帧一致。
