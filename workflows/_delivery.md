# 交付（所有 workflow 的最后一步）

**先判定运行模式 → 决定走哪条路径**(对应 [`reference/runtime-modes.md`](../reference/runtime-modes.md)):

```bash
mode=$(python -m scripts.runtime_mode)
```

| `mode` | 默认路径 | 备注 |
|---|---|---|
| **static**(默认/绝大多数用户) | **路径 A · zip** | 唯一选项 |
| **dynamic**(用户登录过 OAuth / 有 key) | **路径 A · zip**(默认)or 路径 B(用户明确要"让 Claude 帮我编译") | 没特别要求就给 zip,省事更稳 |

路径 A 永远可走;路径 B 只在 dynamic 才走得通。

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

## 路径 B · SDK 一键上传 + 编译 + 下载 mp4

> Path B 现在**无需用户手动贴 API key** —— 首次运行如果没缓存凭证,脚本会**自动跑 OAuth 设备授权流**(RFC 8628):打印一个 `/connect?code=XXXX-YYYY` 链接,用户在已登录的浏览器里点一下 [批准],脚本继续。Key 落盘 `~/.config/autolecture/auth.json`(chmod 600),之后所有 `Client()` 与脚本自动用。

```bash
python3 scripts/upload_and_compile.py <work>
```
[`scripts/upload_and_compile.py`](../scripts/upload_and_compile.py):
- **SDK 缺失** → 用 `require_pip` 打印 "fail-loud" 安装框(`pip install autolecture`),退出码 2。
- **认证缺失**(无 `AUTOLECTURE_API_KEY` env 且无 cache) → 自动跑 `Client.login()`:打印 `/connect?code=…` URL,等用户点批准,拿 key 写 cache,继续 upload+compile。
- **认证有**(env 或 cache 任一) → 静默继续。
- 然后:读主 tex → 建项目 → 上传 assets → PUT tex → 触发 compile + 轮询 → 下载 `out.mp4` → 打印 Studio URL(记下它打印的 project id)。配额超限显示需要的 ✦ + 余额。可选 `--no-compile` / `--base-url` / `--poll-interval` / `--name`。

也可以让用户**先手动登录一次**,之后所有脚本完全静默用 cache:
```bash
autolecture login                                       # 默认连 prod
autolecture login --base-url http://localhost:8001      # 或 dev 沙箱
autolecture whoami                                      # 看缓存的身份
autolecture logout                                      # 清本机 cache(server 那边的 key 不撤销)
```

撤销已授权设备:web 上 `https://autolecture.ai/account → Connected devices`,每个客户端 mint 的 key 可单独 revoke。

**编译失败 → 进调试环（这是 Path B 相对 zip 的核心价值：云端帮你 SEE + 调）：**

```bash
python3 scripts/debug_loop.py run --project-id <pid> --workdir <work>
# 读它打印的每个失败 block 的结构化证据（category / 出错文件:行 + 代码片段 / .debug/*.png 帧）
# 按 NEXT 提示动作：
#   code_error      → 改 <work> 里那个 .py/.tsx/.html，然后 rerender
#   render_timeout  → 调小该 view 的 duration= 或拆成两个 view，再 rerender main.tex
#   engine_capability → 换引擎（manimFile↔htmlFile↔remotionFile）
#   missing_asset / quota / toolchain → 升级给用户（别自己重试）
python3 scripts/debug_loop.py rerender --project-id <pid> --workdir <work> --file scenes/scene_03.tsx
```

[`scripts/debug_loop.py`](../scripts/debug_loop.py) 用 SDK 的结构化错误（`CompileFailedError.block_errors`：code/category/actions/failing_source/hint）+ 多模态帧（`fetch_frame`）。失败隔离到 block：rerender 只重渲染你改的那个 block，其它都命中缓存。**每个 block 最多自己修 3 次**，还不行就带着证据（出错片段 + 帧 + Studio URL）升级给用户——绝不丢一个裸失败。transient 的 provider 错误脚本会自动重试。退出码：0 成功 / 2 待 Claude 修 / 3 升级用户。

---

两条路径**都**经 AutoLecture 编译收费（skill 代码免费，任何入口的编译都收费）。
最后回复用户：交付物路径（zip 或 `out.mp4` + Studio URL）+ 简短一句「怎么用」。
