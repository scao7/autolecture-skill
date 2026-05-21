// {{SCENE_TITLE}} — PDF showcase (Flow B): fan a few real PDF pages out
// like a hand of cards, for an opening "这篇论文我们快速过一遍" overview
// shot. Borrowed from pdf2video's Stack/Fan scenes, rewritten audio-first.
//
// Use as the FIRST pdf beat (establish the document), then cut to
// scene_pdf_switch / scene_pdf_focus / scene_pdf_highlight for the detail.
//
// HOW TO ADAPT:
//   PDF_FILE — uploaded pdf, relative to assets/ (e.g. 'paper.pdf')
//   PAGES    — array of page numbers to fan out, e.g. [1, 2, 3, 4]
//   PAGE_W   — px width each page rasterizes at (e.g. 520 for thumbnails)
//   SPREAD   — fan angle in degrees between adjacent cards (e.g. 9)
//
// Audio-first: cards stagger-in over the first ~40% of the narration, then
// hold with a slow breathe. All timing is relative to durationInFrames.
import {
  AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig,
  staticFile,
} from 'remotion';
import {Document, Page, pdfjs} from 'react-pdf';

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs', import.meta.url,
).toString();

const PDF_OPTS = {
  cMapUrl: 'https://unpkg.com/pdfjs-dist@4.4.168/cmaps/',
  cMapPacked: true,
};

export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;
export const DURATION_FRAMES = 150;          // overwritten to audio length

const PDF_FILE = '{{PDF_FILE}}';
const PAGES    = {{PAGES}};                   // e.g. [1, 2, 3, 4]
const PAGE_W   = {{PAGE_W}};                  // e.g. 520
const SPREAD   = {{SPREAD}};                  // degrees, e.g. 9

export const Comp: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const n = PAGES.length;
  const mid = (n - 1) / 2;
  const breathe = interpolate(frame, [0, durationInFrames - 1], [1.0, 1.03]);

  return (
    <AbsoluteFill style={{backgroundColor: '#0d1117', justifyContent: 'center', alignItems: 'center'}}>
      <div style={{position: 'relative', transform: `scale(${breathe})`, width: PAGE_W, height: PAGE_W * 1.3}}>
        {PAGES.map((pg: number, i: number) => {
          // Stagger each card in over the first ~40% of the clip.
          const start = (durationInFrames * 0.4) * (i / Math.max(1, n));
          const enter = spring({frame: frame - start, fps, config: {damping: 18, mass: 0.6}});
          const angle = (i - mid) * SPREAD;
          const dx = (i - mid) * (PAGE_W * 0.42);
          return (
            <div key={pg} style={{
              position: 'absolute', left: 0, top: 0,
              transformOrigin: 'bottom center',
              transform: `translateX(${dx * enter}px) rotate(${angle * enter}deg) translateY(${(1 - enter) * 80}px)`,
              opacity: enter,
              boxShadow: '0 18px 50px rgba(0,0,0,0.55)',
              borderRadius: 6, overflow: 'hidden',
              border: '1px solid rgba(110,193,228,0.25)',
            }}>
              <Document file={staticFile(PDF_FILE)} options={PDF_OPTS} loading={null}>
                <Page pageNumber={pg} width={PAGE_W} renderTextLayer={false} renderAnnotationLayer={false} />
              </Document>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
