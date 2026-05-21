// {{SCENE_TITLE}} — Tella-style screencast: webcam full-screen → corner PIP
// morph, screen recording behind it. ONE self-contained view.
//
// ── WHY THIS IS ONE VIEW (not over=) ─────────────────────────────────────
// The signature Tella move — webcam fills the frame while you introduce a
// topic, then SHRINKS into a rounded corner thumbnail as the screen
// recording takes over — is a MORPH that happens MID-SHOT. It must live
// inside a SINGLE \begin{view}: one \remotionFile{} scene that loads BOTH
// clips and interpolates the webcam's scale/position over time. The
// manifest only does cut/fade at view BOUNDARIES, so a cross-view split
// can't morph. This is also why it is NOT an over=true overlay: an overlay
// renders standalone-transparent and the engine never sees the footage —
// here the scene deliberately composites both clips itself.
//
//   \begin{view}
//     \remotionFile{scenes/screencast_01.tsx}   % loads screen + webcam
//     \audio{webcam.mp4}                          % voice + audio-first length
//   \end{view}
//
// AUDIO: both clips are `muted` INSIDE this scene (a scene produces VISUALS
// only; it never carries audio). The voice comes from \audio{webcam.mp4} —
// the same webcam file, used as the audio spine. That \audio also sets the
// view length, and the compiler overwrites DURATION_FRAMES to match it, so
// the morph timings below (fractions of `dur`) stay in sync automatically.
// (If the screen recording has system audio you also want — clicks, a demo's
// sound — add \audio[...]{screen.mp4} too; \audio layers mix additively.)
//
// ── HOW TO ADAPT ─────────────────────────────────────────────────────────
//   SCREEN_FILE  — uploaded screen recording, relative to assets (e.g. 'screen.mp4')
//   WEBCAM_FILE  — uploaded webcam recording (e.g. 'webcam.mp4')
//   PIP_SCALE    — webcam thumbnail size as a fraction of frame (0.22–0.30)
//   PIP_CORNER   — 'br' | 'bl' | 'tr' | 'tl'  (which corner the PIP docks)
//   PIP_MARGIN   — px gap from the frame edge
//   MORPH_START  — 0..1 fraction of the clip where the shrink begins
//   MORPH_END    — 0..1 fraction where the webcam has fully docked
//   BG           — letterbox / gap color
// Common variants (search "VARIANT" below):
//   • Reverse (end on a face cam full-screen): swap the interpolate ranges
//     so p goes 1→0 near the end, or add a second morph back to full.
//   • Title bar during the intro: drop in a <div> gated on (1 - p).
//   • Screen "punch-in" zoom on a detail: animate screenScale past 1.0.
import {
  AbsoluteFill, OffthreadVideo, staticFile, interpolate,
  useCurrentFrame, useVideoConfig, Easing,
} from 'remotion';

export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;
export const DURATION_FRAMES = 300;   // overwritten to \audio length at render

const SCREEN_FILE = '{{SCREEN_FILE}}';   // e.g. 'screen.mp4'
const WEBCAM_FILE = '{{WEBCAM_FILE}}';   // e.g. 'webcam.mp4'
const PIP_SCALE   = {{PIP_SCALE}};       // e.g. 0.26
const PIP_CORNER  = '{{PIP_CORNER}}';    // 'br' | 'bl' | 'tr' | 'tl'
const PIP_MARGIN  = {{PIP_MARGIN}};      // e.g. 48
const MORPH_START = {{MORPH_START}};     // e.g. 0.18
const MORPH_END   = {{MORPH_END}};       // e.g. 0.32
const BG          = '{{BG}}';            // e.g. '#0d1117'

export const Comp: React.FC = () => {
  const f = useCurrentFrame();
  const { durationInFrames: d, width: W, height: H } = useVideoConfig();

  // p: 0 = webcam full-screen, 1 = webcam fully docked as corner PIP.
  // Driven off `d` (live duration) so the morph lands at the same FRACTION
  // of the shot no matter how long the narration runs.
  const p = interpolate(f, [d * MORPH_START, d * MORPH_END], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });

  // Webcam: full frame → PIP_SCALE thumbnail in the chosen corner.
  const camScale  = interpolate(p, [0, 1], [1, PIP_SCALE]);
  const camRadius = interpolate(p, [0, 1], [0, 18]);
  const pipW = W * PIP_SCALE, pipH = H * PIP_SCALE;
  // Travel from center (0,0) to the corner. translate happens BEFORE scale
  // in the transform string, so offsets are in full-frame px to the point
  // where the SCALED thumbnail's center should sit.
  const dxFull = (W / 2) - pipW / 2 - PIP_MARGIN;   // center → right edge
  const dyFull = (H / 2) - pipH / 2 - PIP_MARGIN;   // center → bottom edge
  const signX = PIP_CORNER === 'br' || PIP_CORNER === 'tr' ? 1 : -1;
  const signY = PIP_CORNER === 'br' || PIP_CORNER === 'bl' ? 1 : -1;
  const camTX = interpolate(p, [0, 1], [0, signX * dxFull]);
  const camTY = interpolate(p, [0, 1], [0, signY * dyFull]);

  // Screen recording fades up + settles from a slight overscale as the
  // webcam clears out of the way.
  const screenOp    = interpolate(p, [0, 1], [0, 1]);
  const screenScale = interpolate(p, [0, 1], [1.04, 1]);

  return (
    <AbsoluteFill style={{ backgroundColor: BG }}>
      {/* Screen recording — the base, revealed as the webcam docks. */}
      <AbsoluteFill style={{ opacity: screenOp }}>
        <OffthreadVideo
          src={staticFile(SCREEN_FILE)}
          muted
          style={{ width: '100%', height: '100%', objectFit: 'cover',
                   transform: `scale(${screenScale})` }}
        />
      </AbsoluteFill>

      {/* Webcam — starts full-frame, morphs into the corner thumbnail. */}
      <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
        <div style={{
          width: '100%', height: '100%',
          transform: `translate(${camTX}px, ${camTY}px) scale(${camScale})`,
          borderRadius: camRadius, overflow: 'hidden',
          // shadow only once it reads as a floating thumbnail
          boxShadow: p > 0.5 ? '0 12px 40px rgba(0,0,0,0.45)' : 'none',
        }}>
          <OffthreadVideo
            src={staticFile(WEBCAM_FILE)}
            muted
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
