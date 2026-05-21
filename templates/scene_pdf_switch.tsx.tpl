// {{SCENE_TITLE}} — PDF showcase (Flow B): turn the page. Show PAGE_FROM,
// then slide/cross-fade to PAGE_TO at the narration's transition beat —
// the "翻页 / 接下来看下一页" feel. Borrowed from pdf2video's SwitchScene,
// rewritten audio-first for AutoLecture's \remotionFile{} convention.
//
// Use when the narration moves from one page to another ("讲完方法,我们翻到
// 实验那一页"). For "zoom into a region of ONE page" use scene_pdf_focus;
// for "highlight one sentence" use scene_pdf_highlight.
//
// HOW TO ADAPT:
//   PDF_FILE   — uploaded pdf, relative to assets/ (e.g. 'paper.pdf')
//   PAGE_FROM  — page showing at the start (1-indexed)
//   PAGE_TO    — page to turn to
//   PAGE_W     — px width pages rasterize at (e.g. 1000; bump for sharpness)
//   DIR        — 'left' | 'up'  (slide direction; 'left' = next page)
//   TURN_AT    — 0..1 fraction of the clip where the turn happens (e.g. 0.5)
//
// Audio-first: DURATION_FRAMES is overwritten to the \say{} length, so the
// turn lands at TURN_AT × (narration length). Drive all timing off
// durationInFrames — never hardcode absolute frames.
import {
  AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig,
  staticFile, Easing,
} from 'remotion';
import {Document, Page, pdfjs} from 'react-pdf';

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs', import.meta.url,
).toString();

// cMap config lets pdfjs render embedded / CJK fonts correctly (papers
// with Chinese, math glyphs, or subset fonts otherwise show blanks).
const PDF_OPTS = {
  cMapUrl: 'https://unpkg.com/pdfjs-dist@4.4.168/cmaps/',
  cMapPacked: true,
};

export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;
export const DURATION_FRAMES = 150;          // overwritten to audio length

const PDF_FILE  = '{{PDF_FILE}}';
const PAGE_FROM = {{PAGE_FROM}};
const PAGE_TO   = {{PAGE_TO}};
const PAGE_W    = {{PAGE_W}};                 // e.g. 1000
const DIR       = '{{DIR}}';                  // 'left' | 'up'
const TURN_AT   = {{TURN_AT}};                // 0..1, e.g. 0.5

export const Comp: React.FC = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();

  // Turn happens over a 0.5s window centered on TURN_AT × clip.
  const mid = (durationInFrames - 1) * TURN_AT;
  const half = FPS * 0.28;
  const t = interpolate(frame, [mid - half, mid + half], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });

  // Gentle Ken-Burns on whichever page is on screen so it never freezes.
  const breathe = interpolate(frame, [0, durationInFrames - 1], [1.0, 1.04]);

  const axis = DIR === 'up' ? 'translateY' : 'translateX';
  const fromOff = `${axis}(${interpolate(t, [0, 1], [0, -8])}%)`;
  const toOff   = `${axis}(${interpolate(t, [0, 1], [8, 0])}%)`;

  const pageStyle: React.CSSProperties = {
    position: 'absolute', transformOrigin: 'center center',
  };

  return (
    <AbsoluteFill style={{backgroundColor: '#0d1117', justifyContent: 'center', alignItems: 'center'}}>
      <div style={{position: 'relative', transform: `scale(${breathe})`}}>
        <div style={{...pageStyle, opacity: 1 - t, transform: fromOff}}>
          <Document file={staticFile(PDF_FILE)} options={PDF_OPTS} loading={null}>
            <Page pageNumber={PAGE_FROM} width={PAGE_W} renderTextLayer={false} renderAnnotationLayer={false} />
          </Document>
        </div>
        <div style={{...pageStyle, opacity: t, transform: toOff}}>
          <Document file={staticFile(PDF_FILE)} options={PDF_OPTS} loading={null}>
            <Page pageNumber={PAGE_TO} width={PAGE_W} renderTextLayer={false} renderAnnotationLayer={false} />
          </Document>
        </div>
      </div>
    </AbsoluteFill>
  );
};
