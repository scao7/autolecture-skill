// Scene NN — TRANSPARENT OVERLAY for 实拍结合 (live-action + motion graphics)
// (~<EST_DURATION>s, but the FOOTAGE drives actual length — see below)
//
// Use this when the user wants animated graphics ON TOP OF real video
// footage (lower-thirds, callouts, arrows, labels, score bugs). Wire it
// in main.tex with the `over=` opt:
//
//   \begin{view}
//     \remotionFile[over=clip.mp4]{scene_overlay.tsx}   % clip.mp4 in assets/
//     \say{你的旁白……}                                  % MIXED on top of footage audio
//   \end{view}
//
// The backend alpha-renders this scene (transparent background), then
// composites it OVER assets/clip.mp4. The footage is the SPINE: its
// duration sets the clip length and this overlay is rendered to match.
// Footage audio + your \say narration are MIXED additively (not replaced).
// Levels: \remotionFile[over=clip.mp4, over_volume=0.4]{...} ducks the
// footage; \say[volume=1.2]{...} lifts the narration.
//
// ── TWO HARD RULES FOR OVERLAYS ──────────────────────────────────────
// 1. NEVER set an opaque backgroundColor on the root AbsoluteFill. The
//    background MUST stay transparent or it hides the footage. Only the
//    graphic ELEMENTS get backgrounds. (This is the #1 overlay mistake.)
// 2. Keep WIDTH/HEIGHT at the footage's resolution. The compiler also
//    forces --width/--height to the project \aspect{}, so just match the
//    footage aspect ratio here (16:9 default below).
//
// AUDIO-FIRST TIMING (same as every scene): express animation timings as
// fractions of `dur` (live duration), never hardcoded frames — the
// compiler overrides DURATION_FRAMES to the footage length at render time.
import React from 'react';
import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
  interpolate, spring,
} from 'remotion';

export const FPS = 30;
export const WIDTH = 1280;
export const HEIGHT = 720;
// Author estimate; compiler overrides to the FOOTAGE length at render time.
export const DURATION_FRAMES = 10 * FPS;

const C = {
  fg: '#ffffff',
  accent: '#6ec1e4',
  card: 'rgba(20, 24, 33, 0.82)',   // semi-opaque so text stays legible over busy footage
  bar: '#ee6c4d',
};

export const Comp: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames: dur } = useVideoConfig();

  // Lower-third slides up + fades in over the first 12% of the clip,
  // then slides back out over the last 12% so it doesn't linger.
  const IN_END  = dur * 0.12;
  const OUT_BEG = dur * 0.88;

  const enter = spring({ frame, fps, config: { damping: 16 }, durationInFrames: IN_END });
  const exit  = interpolate(frame, [OUT_BEG, dur], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const y       = interpolate(enter, [0, 1], [60, 0]) + interpolate(exit, [0, 1], [0, 60]);
  const opacity = Math.min(interpolate(enter, [0, 1], [0, 1]), 1 - exit);

  return (
    // ⛔ NO backgroundColor here — transparent root lets footage through.
    <AbsoluteFill style={{ fontFamily: 'Inter, system-ui, "PingFang SC", sans-serif' }}>
      {/* Lower-third card, bottom-left. Only the card has a background. */}
      <div
        style={{
          position: 'absolute',
          left: 64,
          bottom: 72,
          transform: `translateY(${y}px)`,
          opacity,
          display: 'flex',
          alignItems: 'stretch',
          borderRadius: 12,
          overflow: 'hidden',
          boxShadow: '0 10px 40px rgba(0,0,0,0.45)',
        }}
      >
        <div style={{ width: 8, background: C.bar }} />
        <div style={{ background: C.card, color: C.fg, padding: '16px 26px' }}>
          <div style={{ fontSize: 30, fontWeight: 800, letterSpacing: -0.5 }}>
            主标题 <span style={{ color: C.accent }}>关键词</span>
          </div>
          <div style={{ fontSize: 17, color: '#aab1c0', marginTop: 4 }}>
            副标题 / 说明文字
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
