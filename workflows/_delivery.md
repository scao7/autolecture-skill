# 交付（所有 workflow 的最后一步）

**默认：打包 zip 让用户自己上传。** 先看用户有没有我们的 API key
（`AUTOLECTURE_API_KEY`）：

- **没有**（绝大多数情况）→ 走**路径 A · zip**（下方）。这是当前的默认交付方式。
- **有** → 可以走路径 B（SDK 直传）；但这条路径还在随 API 完善，**没特别要求就还是给 zip**。

---

## 路径 A · 打包 zip（默认）

```bash
python3 scripts/package_zip.py --work <work> --out <work>/autolecture_demo.zip
```

[`scripts/package_zip.py`](../scripts/package_zip.py) 会：
- 把 `<work>` 全部内容打到一个 zip（`main.tex` + `scenes/` + 素材）
- 校验关键文件都在（每个 `\manimFile` / `\htmlFile` / `\remotionFile` / `\imageFile` / `\audio` / `over=` / PDF 引用的文件都存在），缺了就 hard-exit
- 输出 zip 路径 + 文件清单

回复用户：zip 路径 + 「拖到 <https://autolecture.ai> 上传，会自动识别 main.tex、把素材注册好；之后在 Studio 里改代码 / 点 ▶ Recompile」。（网站 from-zip 已验证：自动加 `\begin{videotex}` 外壳、注册 assets、`staticFile()` 能拿到上传的 PDF / 图 / 视频。）

---

## 路径 B · SDK 一键上传 + 编译 + 下载 mp4（用户已有 API key 时；流程待完善）

> 当前阶段以 zip 为主；此路径随 API 持续完善。仅当用户**已有 API key 且明确想让 AI 边跑边调**时用。

前提：
1. `pip install autolecture`（SDK：<https://github.com/scao7/autolecture-python>）
2. 在 <https://autolecture.ai/account> → 🔑 API Keys 生成 key，`export AUTOLECTURE_API_KEY=al_live_...`

```bash
python3 scripts/upload_and_compile.py <work>
```
[`scripts/upload_and_compile.py`](../scripts/upload_and_compile.py)：读主 tex → 建项目 → 上传 assets → PUT tex → 触发 compile + 轮询 → 下载 `out.mp4` → 打印 Studio URL。排错：编译失败退出码 1 + error_log tail；配额超限显示需要的 ✦ + 余额；没装 SDK 提示 `pip install autolecture`。可选 `--no-compile` / `--base-url` / `--poll-interval`。

---

两条路径**都**经 AutoLecture 编译收费（skill 代码免费，任何入口的编译都收费）。
最后回复用户：交付物路径（zip 或 `out.mp4` + Studio URL）+ 简短一句「怎么用」。
