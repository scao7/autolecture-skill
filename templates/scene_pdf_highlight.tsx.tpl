// {{SCENE_TITLE}} — PDF showcase (Flow B): render a real PDF page,
// zoom toward a target phrase, and highlight the line(s) containing it.
//
// Used as a \remotionFile{} scene in AutoLecture. The phrase is what
// the narration (\say{}) is talking about at this beat — the highlight
// + zoom land on exactly those words via the pdfjs text layer, NO
// hardcoded coordinates.
//
// Requires react-pdf in AutoLecture's Remotion bundle (shipped). The
// PDF must be uploaded as a project asset; staticFile() resolves it
// because AutoLecture stages the project's assets/ as the bundle's
// public/ at render time.
//
// HOW TO ADAPT (Claude fills these in per beat):
//   PDF_FILE      — the uploaded pdf, relative to assets/ (e.g. 'paper.pdf')
//   PAGE_NUM      — which page (1-indexed)
//   TARGET        — the phrase the narration references (drives box + zoom)
//   ZOOM_END      — final zoom scale (1.0 = no zoom; 1.4–1.8 typical)
//   PAGE_W        — px width the page rasterizes at; bump for sharper zoom
//
// Audio-first: DURATION_FRAMES below is overwritten by the compiler to
// match the \say{} length, so the zoom always ends exactly when the
// narration does.
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
export const DURATION_FRAMES = 120;          // overwritten to audio length

const PDF_FILE = '{{PDF_FILE}}';             // e.g. 'paper.pdf'
const PAGE_NUM = {{PAGE_NUM}};               // e.g. 1
const TARGET   = '{{TARGET}}';               // phrase the narration references
const ZOOM_END = {{ZOOM_END}};               // e.g. 1.6
const PAGE_W   = {{PAGE_W}};                 // e.g. 1100

type Box = {x: number; y: number; w: number; h: number};

export const Comp: React.FC = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const [handle] = useState(() => delayRender('locate target text'));
  const [box, setBox] = useState<Box | null>(null);
  const [pageH, setPageH] = useState(0);

  const onLoadSuccess = useCallback(async (pdf: any) => {
    try {
      const page = await pdf.getPage(PAGE_NUM);
      const base = page.getViewport({scale: 1});
      const scale = PAGE_W / base.width;
      const vp = page.getViewport({scale});
      setPageH(vp.height);

      const tc = await page.getTextContent();
      const needle = TARGET.toLowerCase();
      // Collect every text item that overlaps the phrase (handles a
      // phrase split across spans / wrapped to the next line).
      const hits: Box[] = [];
      for (const it of tc.items as any[]) {
        const s = (it.str || '').toLowerCase();
        if (!s.trim()) continue;
        if (s.includes(needle) || needle.includes(s) || s.includes(needle.split(' ')[0])) {
          const [a, , , , e, f] = it.transform;
          const [px, py] = vp.convertToViewportPoint(e, f);
          const w = (it.width || 0) * scale;
          const h = (it.height || a) * scale;
          hits.push({x: px, y: py - h, w, h});
        }
      }
      if (hits.length) {
        // Union the hit boxes into one highlight rect.
        const x = Math.min(...hits.map(b => b.x));
        const y = Math.min(...hits.map(b => b.y));
        const r = Math.max(...hits.map(b => b.x + b.w));
        const bot = Math.max(...hits.map(b => b.y + b.h));
        setBox({x, y, w: r - x, h: bot - y});
      }
    } finally {
      continueRender(handle);
    }
  }, [handle]);

  const p = interpolate(frame, [0, durationInFrames - 1], [0, 1], {
    extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic),
  });
  const scale = interpolate(p, [0, 1], [1.0, ZOOM_END]);
  const hl = interpolate(frame, [Math.round(FPS * 0.7), Math.round(FPS * 1.2)], [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  // Zoom origin = highlight center (fall back to page center pre-load).
  const ox = box ? box.x + box.w / 2 : PAGE_W / 2;
  const oy = box ? box.y + box.h / 2 : (pageH || PAGE_W * 1.3) / 2;

  return (
    <AbsoluteFill style={{backgroundColor: '#0d1117', justifyContent: 'center', alignItems: 'center'}}>
      <div style={{transform: `scale(${scale})`, transformOrigin: `${ox}px ${oy}px`, position: 'relative'}}>
        <Document file={staticFile(PDF_FILE)} loading={null} onLoadSuccess={onLoadSuccess}>
          <Page pageNumber={PAGE_NUM} width={PAGE_W} renderTextLayer={false} renderAnnotationLayer={false} />
        </Document>
        {box && (
          <div style={{
            position: 'absolute',
            left: box.x - 4, top: box.y - 2,
            width: box.w + 8, height: box.h + 4,
            background: 'rgba(244, 211, 94, 0.30)',
            border: '2px solid #f4d35e',
            borderRadius: 4,
            opacity: hl,
          }}/>
        )}
      </div>
    </AbsoluteFill>
  );
};
