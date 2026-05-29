// Scene NN — BRAND lower-third (TRANSPARENT OVERLAY for `over=true`, brand-style)
// (~<EST_DURATION>s; the FOOTAGE drives actual length — audio-first)
//
// Use this when the project is in AutoLecture BRAND style (cream/navy/tan
// from <reference/brand-style.md>) — e.g. official demos, teasers,
// tutorials, anything carrying the AutoLecture name. For editorial /
// personal vlogs in the dark palette, use `scene_overlay.tsx.tpl` instead.
//
// Same composition pattern as the dark overlay: footage is the BASE
// (\video[start,end]{clip.mp4}), this scene is rendered to a TRANSPARENT
// alpha webm by `over=true` and stacked over the footage by the manifest.
//
//   \begin{view}
//     \video[start=0, end=8]{clip.mp4}
//     \remotionFile[over=true]{scenes/scene_NN_brand_lower_third.tsx}
//   \end{view}
//
// ── THREE HARD RULES (same as dark overlay) ──────────────────────────
// 1. NEVER put an opaque `backgroundColor` on the root AbsoluteFill — it
//    becomes the alpha webm background and hides the footage. Only the
//    card itself gets a fill.
// 2. WIDTH/HEIGHT match the project aspect (compiler also forces them).
//    9:16 → 720×1280; 16:9 → 1280×720.
// 3. BRAND glass = a TRANSLUCENT PAPER panel (rgba 0.86) + hairline
//    navy-tinted border + a tan top sheen. This is the **brand**
//    counterpart to dark's frosted glass. Don't ship the dark glass
//    (low-alpha black) on a brand project — it looks dirty on cream
//    footage.
//
// AUDIO-FIRST: express timings as fractions of `dur` from
// useVideoConfig() — the compiler overrides DURATION_FRAMES to the
// footage length at render time.
import React from 'react';
import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
  interpolate, spring,
} from 'remotion';

export const FPS = 30;
export const WIDTH = 1280;     // change to 720 for 9:16
export const HEIGHT = 720;     // change to 1280 for 9:16
export const DURATION_FRAMES = 8 * FPS;

// Brand palette mirrors styles.css :root in the website (cream/navy/tan).
// See ../reference/brand-style.md for the source-of-truth tokens.
const C = {
  cream:  '#f4e5bd',
  tan:    '#d9b47b',
  navy:   '#234976',
  navyD:  '#1a3554',
  paper:  'rgba(255, 255, 255, 0.86)',          // translucent paper — the brand "glass"
  border: 'rgba(35, 73, 118, 0.18)',            // navy-tinted hairline
  sheen:  'linear-gradient(180deg, rgba(217,180,123,0.22), rgba(217,180,123,0) 44%)', // tan top sheen
  shadow: '0 12px 36px rgba(35, 73, 118, 0.22)',
  ink1:   '#4a6585',
};

export const Comp: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames: dur } = useVideoConfig();

  const IN_END  = dur * 0.12;
  const OUT_BEG = dur * 0.88;

  const enter = spring({ frame, fps, config: { damping: 17 }, durationInFrames: IN_END });
  const exit  = interpolate(frame, [OUT_BEG, dur], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const y       = interpolate(enter, [0, 1], [60, 0]) + interpolate(exit, [0, 1], [0, 60]);
  const opacity = Math.min(interpolate(enter, [0, 1], [0, 1]), 1 - exit);

  return (
    // ⛔ NO backgroundColor on the root — transparent so footage reads through.
    <AbsoluteFill style={{ fontFamily: 'Inter, "Noto Sans SC", system-ui, "PingFang SC", sans-serif' }}>
      {/* Lower-third card, bottom-left. Only the card has a fill. */}
      <div
        style={{
          position: 'absolute',
          left: 56,
          bottom: 68,
          transform: `translateY(${y}px)`,
          opacity,
          display: 'flex',
          alignItems: 'stretch',
          borderRadius: 14,
          overflow: 'hidden',
          boxShadow: C.shadow,
        }}
      >
        {/* Tan accent bar — the brand's warm side */}
        <div style={{ width: 8, background: C.tan }} />
        {/* Paper panel: translucent white + navy hairline + tan sheen on top */}
        <div style={{
          background: C.paper,
          backgroundImage: C.sheen,
          border: `1px solid ${C.border}`,
          borderLeft: 'none',
          color: C.navy,
          padding: '16px 26px',
        }}>
          <div style={{
            fontSize: 14, fontWeight: 700, letterSpacing: 5,
            color: C.tan, textTransform: 'uppercase',
          }}>
            kicker
          </div>
          <div style={{
            fontSize: 30, fontWeight: 900, letterSpacing: -0.5, marginTop: 4,
            color: C.navy,
          }}>
            主标题 <span style={{
              backgroundImage: 'linear-gradient(135deg, #234976 0%, #d9b47b 100%)',
              WebkitBackgroundClip: 'text', backgroundClip: 'text',
              color: 'transparent', fontWeight: 900,
            }}>关键词</span>
          </div>
          <div style={{ fontSize: 16, color: C.ink1, marginTop: 4 }}>
            副标题 / 说明
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
