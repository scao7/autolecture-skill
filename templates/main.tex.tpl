% {{PROJECT_TITLE}} —— autolecture-skill 生成
% Mode: {{MODE}}        (rough / polished / text)
% Source audio: {{AUDIO_FILE}}    (omit for text mode)
% Generated scenes: {{N_SCENES}}

\title{{{PROJECT_TITLE}}}
\aspect{16:9}                  % 比例。默认短边 720p。要 1080p / 4K 写 \aspect{16:9, 1080p} / \aspect{16:9, 4k}
\style{{{STYLE_DESCRIPTION}}}          % 视觉风格（喂 LLM 视觉引擎）
% \voice{沉稳男中音, 慢节奏, 偏学术}    % 可选：TTS 音色语气（与 \style 解耦；不写则回退用 \style）

\begin{videotex}

% ──────────────── Example: text / rough mode (TTS) ────────────────
\begin{view}[title=Scene_01_Hook]
  \say{这里是这一段的旁白文字，TTS 会朗读。}
  \remotionFile{scenes/scene_01_hook.tsx}
\end{view}

% ──────────────── Example: polished mode (clip 原音频) ────────────
\begin{view}[title=Scene_02_Card]
  \audio[start=32.34, end=66.44]{{{AUDIO_FILE}}}
  \htmlFile{scenes/scene_02_card.html}
\end{view}

% ──────────────── Example: Manim 数学 ─────────────────────────────
% retime=true 让 compiler 把动画时长缩放到这一拍的音频长度（audio-first）。
% 不加 retime 则按源码原速渲染、末帧冻结 —— skill 的 \manimFile 一律加 retime=true。
\begin{view}[title=Scene_03_Math]
  \audio[start=66.44, end=87.40]{{{AUDIO_FILE}}}
  \manimFile[retime=true]{scenes/scene_03_math.py}
\end{view}

% ──────────────── Example: AI image ───────────────────────────────
\begin{view}[title=Scene_04_Illustration]
  \say{这一段用 AI 生图配画面。}
  \image[engine=gemini]{a thoughtful person looking up at the sky,
                         hand-drawn watercolor with warm pastel palette}
\end{view}

% ──────────────── Example: 上传的图片 ──────────────────────────────
\begin{view}[title=Scene_05_Photo]
  \say{这是从相机里导入的照片。}
  \imageFile[fit=contain]{figures/photo_01.jpg}
\end{view}

\end{videotex}
