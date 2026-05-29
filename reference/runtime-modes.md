# 两种运行模式 — Claude 速查表

每条 workflow 都得**显式分支**。这一页列每个动作在 **dynamic**(有 SDK auth)和 **static**(默认/zip 用户)下应该怎么做。

> **判定**:`python -m scripts.runtime_mode` → 输出 `dynamic` 或 `static`
> 也可以 `python -m scripts.runtime_mode --json` 拿到 `{mode, base_url, source, email}`。
>
> 判定规则:`AUTOLECTURE_API_KEY` env 或 `~/.config/autolecture/auth.json` 任一存在 → dynamic;都没 → static。

---

## dynamic 模式能做什么 / static 模式怎么 fallback

| 信息/动作 | DYNAMIC(有 auth) | STATIC(无 auth) |
|---|---|---|
| **用户有没有 voice clone 注册** | `client.get_voice_sample()` 一秒回 | 用 `AskUserQuestion` 问用户;不确定就按"无"处理 |
| **当前 ✦ 余额 / quota** | `client.get_balance()` / `client.get_quota()` | 跳过这步;在 README 里告诉用户 web 上自查 |
| **上传前成本预估** | `client.estimate_compile(project_id)` (dry-run,不扣 ✦) | 跳过;在 README 里写明大致 ✦ 估算 |
| **创建项目 / 上传 / 编译 / 下载 mp4** | SDK 一条龙(`upload_and_compile.py` path B) | **打包 zip** 让用户拖到 [autolecture.ai](https://autolecture.ai) 上传(path A) |
| **编译失败,Claude 自修一遍** | `debug_loop.py`:`BlockError` 结构化错 + `rerender_block` + 单块缓存命中 + Claude 看 `fetch_frame` PNG | **不可能** —— Claude 看不到 cloud 编译结果;用户在 web UI 看错。skill 在最后提示用户编译失败时怎么 debug |
| **看某个 view 真渲出来的样子** | `client.fetch_frame(content_hash, t)` 拉 PNG | **不可能** —— 必须本地 render(L3 harness 已经这么干 `\htmlFile{}`) |
| **看某个 view 的音频波形** | `client.fetch_waveform(content_hash)` PNG | **不可能** —— 用本地 `ffprobe` 拿 duration 当替代,看不到形状 |
| **增量编译(只重渲改动的 block)** | `client.compute_hashes` + `compile(only_block_hash=…)` | **不可能** —— static 每次都重新打 zip 重新让用户拖 |
| **harness check static 那 8 条** | 跑(同 static) | 跑(本地静态分析) |
| **harness L3 render**(Playwright HTML overflow/overlap) | 跑(本地 Chromium) | 跑(本地 Chromium,跟 SDK auth 无关) |
| **harness `voice_clone_consistency`** | 主动调 `/me/voice-sample` 看真有没 sample | 退化为"consistency-only"——若 .tex 里部分 `\say` 有 `voice=mine` 部分没有,警告;两边都没/都有 → 不报 |

---

## 简明规则给 Claude 用

**每条 workflow 第一步:**
```bash
mode=$(python -m scripts.runtime_mode)
# mode 是字符串 "dynamic" 或 "static"
```

**遇到需要用户状态的事**(voice clone / balance / quota):
- `mode == "dynamic"` → 调 SDK 拿到事实
- `mode == "static"` → 用 `AskUserQuestion`,或按保守默认走

**遇到需要 cloud 反馈的事**(实际编译看效果 / 看渲出 PNG):
- `mode == "dynamic"` → 调 SDK introspection
- `mode == "static"` → 用本地 harness L3 render 当替代(可以看 HTML 渲出);没本地替代品就放弃这步

**最后交付:**
- `mode == "dynamic"` → `upload_and_compile.py`(已经自动 fallback 到 `Client.login()` 走设备授权流,但只有当 cache/env 都没了才会触发,即便如此本质还是 dynamic)
- `mode == "static"` → `package_zip.py` 打 zip,告诉用户去 autolecture.ai 拖

---

## 单一真源:`harness.runtime.Mode`

代码里所有需要判定模式的地方都 import 这个:

```python
from harness.runtime import detect, auth_headers

m = detect()
if m.is_dynamic():
    # 用 m.base_url 调 SDK
    # m.email 可能可用(来自 cache)
    ...
else:
    # static fallback
    ...

# 只想一次 ad-hoc HTTP 调用、不想实例化 Client:
headers = auth_headers()   # 静态模式返回 None
if headers:
    httpx.get(f"{m.base_url}/api/v2/me/balance", headers=headers)
```

不要在别处写自己的"检测 cache 文件" / "读环境变量"逻辑——会 drift。

---

## 跟 workflows/_delivery.md 的关系

- **path A · zip** = static 模式的必选交付路径 + dynamic 模式的可选(用户想自己拖网页)
- **path B · SDK** = 只有 dynamic 模式才走得通

skill workflow 走完看 `mode`:
- static → path A 是唯一选项
- dynamic → 默认还是 path A(zip)更省事,**只有用户明确说"我让 Claude 帮我编译"才上 path B**
