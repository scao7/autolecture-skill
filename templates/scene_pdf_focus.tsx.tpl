// {{SCENE_TITLE}} — PDF showcase (Flow B): show a PDF page and slowly
// focus (zoom + optional vertical scroll) toward a region. No highlight
// box — use this when the narration is "let's look at this page / this
// part of the figure" rather than "this exact sentence."
//
// Focal point can be given two ways (pick one):
//   1. FOCUS_PHRASE non-empty → focus centers on that phrase (text layer)
//   2. FOCUS_PHRASE = ''      → focus on FOCUS_FX / FOCUS_FY fractional
//                               coords (0..1 of page width/height)
//
// Scroll: if SCROLL = true, the page also translates vertically from
// top toward the focal point — good for "scroll down to the methods
// section" feel on a tall page.
//
// Requires react-pdf in AutoLecture's bundle. PDF must be a project
// asset (staticFile resolves it via the staged public/ dir).
//
// HOW TO ADAPT:
//   PDF_FILE / PAGE_NUM / PAGE_W   — as in scene_pdf_highlight
//   FOCUS_PHRASE                   — '' or a phrase to center on
//   FOCUS_FX / FOCUS_FY            — fallback focal point (fractions)
//   ZOOM_END                       — final scale (1.3–2.0)
//   SCROLL                         — true|false
//
// Audio-first: DURATION_FRAMES overwritten to the \say{} length.
import {useState, useCallback} from 'react';
import {
  AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig,
  delayRender, continueRender, staticFile, Easing,
} from 'remotion';
import {Document, Page, pdfjs} from 'react-pdf';

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs', import.meta.url,
).toString();

export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;
export const DURATION_FRAMES = 150;          // overwritten to audio length

const PDF_FILE     = '{{PDF_FILE}}';
const PAGE_NUM     = {{PAGE_NUM}};
const PAGE_W       = {{PAGE_W}};             // e.g. 1100
const FOCUS_PHRASE = '{{FOCUS_PHRASE}}';     // '' → use FOCUS_FX/FY
const FOCUS_FX     = {{FOCUS_FX}};           // 0..1 (page width fraction)
const FOCUS_FY     = {{FOCUS_FY}};           // 0..1 (page height fraction)
const ZOOM_END     = {{ZOOM_END}};           // e.g. 1.6
const SCROLL       = {{SCROLL}};             // true|false

export const Comp: React.FC = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const [handle] = useState(() => delayRender('locate focal point'));
  const [focus, setFocus] = useState<{x: number; y: number} | null>(null);
  const [pageH, setPageH] = useState(PAGE_W * 1.3);

  const onLoadSuccess = useCallback(async (pdf: any) => {
    try {
      const page = await pdf.getPage(PAGE_NUM);
      const base = page.getViewport({scale: 1});
      const scale = PAGE_W / base.width;
      const vp = page.getViewport({scale});
      setPageH(vp.height);

      if (FOCUS_PHRASE) {
        const tc = await page.getTextContent();
        const needle = FOCUS_PHRASE.toLowerCase();
        for (const it of tc.items as any[]) {
          const s = (it.str || '').toLowerCase();
          if (s.trim() && (s.includes(needle) || s.includes(needle.split(' ')[0]))) {
            const [, , , , e, f] = it.transform;
            const [px, py] = vp.convertToViewportPoint(e, f);
            setFocus({x: px, y: py});
            break;
          }
        }
      }
      if (!FOCUS_PHRASE) {
        setFocus({x: PAGE_W * FOCUS_FX, y: vp.height * FOCUS_FY});
      }
    } finally {
      continueRender(handle);
    }
  }, [handle]);

  const p = interpolate(frame, [0, durationInFrames - 1], [0, 1], {
    extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic),
  });
  const scale = interpolate(p, [0, 1], [1.0, ZOOM_END]);

  const fx = focus ? focus.x : PAGE_W / 2;
  const fy = focus ? focus.y : pageH / 2;

  // Optional scroll: start focused near the top, drift to the focal y.
  const startY = SCROLL ? pageH * 0.18 : fy;
  const curY = interpolate(p, [0, 1], [startY, fy]);

  return (
    <AbsoluteFill style={{backgroundColor: '#0d1117', justifyContent: 'center', alignItems: 'center'}}>
      <div style={{transform: `scale(${scale})`, transformOrigin: `${fx}px ${curY}px`, position: 'relative'}}>
        <Document file={staticFile(PDF_FILE)} loading={null} onLoadSuccess={onLoadSuccess}>
          <Page pageNumber={PAGE_NUM} width={PAGE_W} renderTextLayer={false} renderAnnotationLayer={false} />
        </Document>
      </div>
    </AbsoluteFill>
  );
};
