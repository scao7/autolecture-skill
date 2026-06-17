# Common Chinese Whisper Mis-transcriptions

Whisper transcribing Chinese (especially mixed Cantonese/Mandarin, or with background noise) produces a lot of homophone errors. **The audio itself is fine; the transcription is wrong.** On-screen text must use the corrected version.

## Class 1: terminology / English transliterations (high frequency)

| Whisper output | Should be |
|---|---|
| LydowWM / 雷威艷 / 雷威 M | LeWM |
| LoccasMyers | Lucas Maes |
| 央勒坑 / 央勒康 | Yann LeCun |
| J-POP | JEPA |
| LinusProbes | Linear Probes |
| SuppriseEvaluation / Surprise eval | Surprise Evaluation |
| AIRosBIC | Anomaly Signal / 异常警报 |
| LadenSpaceyS | Latent Space |

## Class 2: generic homophone errors

| Whisper | Should be | Context |
|---|---|---|
| 玻璃 | 剥离 | 把…剥离 |
| 寒暑 | 函数 | 损失函数 |
| 粗套 | 粗糙 | 粗糙的环境 |
| 貪查 / 攤他 / 攤它 / 撞她 / 谈她 | 坍塌 | 表示坍塌 |
| 死舉 | 死局 | 全局最优死局 |
| 死科 | 死磕 | 死磕每个像素 |
| 高撕 | 高斯 | 高斯分布 |
| 高撕分布 / 高撕包落面 / 高撕约数 | 高斯分布 / 高斯包络面 / 高斯约束 | |
| 政策畫像 / 政策画像 | 正则项 | SIGReg 正则项 |
| 排斥立場 | 排斥力场 | |
| 應射 / 应射 | 映射 | |
| 順意 | 语义 | 语义信息 |
| 短/長數相量 | 常数向量 | |
| 凡相量 / 烦相量 | 反向量 | 辅助/反向量 |
| 复养笨 / 副养笨 | 负样本 | |
| 集型超参数 | 极限超参数 | |
| 危壓縮 / 危压缩 | 维度压缩 | |
| 嚴刻 / 严刻 | 严苛 | |
| 算立 / 算利 | 算力 | |
| 動折 / 动折 | 动辄 | |
| 信息平緊 / 信息平景 | 信息瓶颈 | |
| 油票 | 邮票 | 邮票大小的纸条 |
| 進靠廠 / 进靠厂 | 进考场 | |
| 必無選擇 / 必无选择 | 别无选择 | |
| 自規回 | 自回归 | 自回归过程 |
| 推延 / 滾動推延 | 推演 / 滚动推演 | rollout |
| 跌開 | 解码 | 解码回像素 |
| 觀彩板 | 棺材板 | 牛顿的棺材板 |
| L2 距離 物差 | L2 距离 误差 | |
| 物差信号 | 误差信号 | |
| 融陷出 | 涌现出 | |
| 弱能 | 动能 / 跃能 | |
| 凡事 | 范式 | |
| 大道之間 | 大道至简 | |
| 集合與動力學 | 几何与动力学 | |
| 動場 | 动力学 | |
| 貪縮 | 坍缩 | |
| 堆氣 | 堆砌 | 算力堆砌 |
| 拆解 | 拆解 ✓ | don't "correct" this one |

## Class 3: numbers / units

| Whisper | Should be |
|---|---|
| 15000 萬 | 1500 万 (= 15M) — Whisper often mishears "千万" |
| 千億 | 千亿 |

## Workflow

1. Read the full transcript once.
2. Find the sentences that "don't read right."
3. Verify homophone candidates by pinyin (pinyin shū / shù → 数 / 暑 / 述 etc.).
4. Record each replacement in `<work>/transcript_corrections.md`, one per line: `wrong → right`.
5. All downstream headlines / on-screen text / captions use the corrected version.
6. **In `\audio` mode the original audio is unchanged**; in TTS mode (`\say`) you must feed the corrected text to TTS.
