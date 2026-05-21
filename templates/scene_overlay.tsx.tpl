// Scene NN — TRANSPARENT OVERLAY for 实拍结合 (live-action + motion graphics)
// (~<EST_DURATION>s, but the FOOTAGE drives actual length — see below)
//
// Use this when the user wants animated graphics ON TOP OF real video
// footage (lower-thirds, callouts, arrows, labels, score bugs). Put the
// footage as a `\video` BASE layer and this scene as an `over=true` overlay
// in the SAME view:
//
//   \begin{view}
//     \video[start=0, end=8.5]{clip.mp4}            % footage base + its audio = spine
//     \remotionFile[over=true]{scene_overlay.tsx}   % this transparent overlay
//   \end{view}
//
// `over=true` is a RENDER HINT: the backend renders THIS scene to a
// transparent alpha webm and the MANIFEST stacks it over the \video base —
// the engine never touches the footage. The footage is the SPINE: the
// \video clip's duration (audio-first on its own audio) sets the view
// length. Add a \say / \bgm to layer extra audio (mixed additively;
// balance with \say[volume=] / \bgm[volume=]). `\video[mute=on]` drops the
// footage's own audio.
//
// ── THREE HARD RULES FOR OVERLAYS ────────────────────────────────────
// 1. NEVER set an opaque backgroundColor on the root AbsoluteFill. The
//    background MUST stay transparent or the alpha webm hides the footage.
//    Only the graphic ELEMENTS get backgrounds. (#1 overlay mistake.)
// 2. Keep WIDTH/HEIGHT at the footage's resolution. The compiler also
//    forces --width/--height to the project \aspect{}, so just match the
//    footage aspect ratio here (16:9 default below).
// 3. FROSTED-GLASS look: panels are TRANSLUCENT glass (low-alpha fill +
//    light border + top sheen) so the footage reads through them. The
//    overlay is rendered standalone to a transparent webm (the footage is
//    NOT in this render — the manifest composites them), so
//    `backdrop-filter: blur()` has nothing to blur here; don't rely on it.
//    Translucency (alpha 0.30–0.50) is what sells the glass.
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
  glass: 'rgba(18, 22, 31, 0.42)',         // frosted-glass fill — translucent so footage reads through
  glassBorder: 'rgba(255, 255, 255, 0.16)', // light hairline = the "glass edge"
  sheen: 'linear-gradient(180deg, rgba(255,255,255,0.12), rgba(255,255,255,0) 38%)',
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
        {/* Frosted-glass panel: translucent fill + hairline border + top
            sheen. backgroundImage paints the sheen over the glass fill. */}
        <div style={{
          background: C.glass,
          backgroundImage: C.sheen,
          border: `1px solid ${C.glassBorder}`,
          borderLeft: 'none',
          color: C.fg,
          padding: '16px 26px',
        }}>
          <div style={{ fontSize: 30, fontWeight: 800, letterSpacing: -0.5, textShadow: '0 2px 12px rgba(0,0,0,0.5)' }}>
            主标题 <span style={{ color: C.accent }}>关键词</span>
          </div>
          <div style={{ fontSize: 17, color: '#cdd4de', marginTop: 4, textShadow: '0 1px 8px rgba(0,0,0,0.5)' }}>
            副标题 / 说明文字
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
