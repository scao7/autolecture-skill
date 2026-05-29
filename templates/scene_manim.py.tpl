"""Scene NN — <HEADLINE>  (~<EST_DURATION>s, audio drives actual length).

AUDIO-FIRST TIMING — load-bearing.

⚠️ The view MUST reference this file as `\\manimFile[retime=true]{...}`.
As of 2026-05-22 `\\manimFile` does NOT auto-scale by default (the compiler
no longer rewrites hand-written code unless asked). `retime=true` turns the
AST scaler back on for this scene — without it the animation renders at its
written speed and freezes on the last frame for the rest of the audio.

With `retime=true`, the AutoLecture compiler runs `fit_manim_to_target` AST
scale on the script: it sums `self.play(run_time=N)` + `self.wait(N)` across
the construct() method to get the "natural duration", then rewrites EVERY
`run_time=` kwarg and `wait()` positional arg by a constant ratio =
`target_dur / natural_dur` so the visual ends exactly when the TTS / audio
clip ends. Clamped to [0.3×, 4.0×] so a 1s audio won't fast-forward a 30s
manim into invisibility.

What this means for you when writing this file:
  ✅ Write the durations that FEEL natural for the choreography:
        self.play(FadeIn(circle), run_time=1.0)
        self.wait(2.0)
        self.play(circle.animate.scale(1.5), run_time=1.5)
     Let the AST scaler match it to audio.
  ❌ Don't pre-compute "audio is 15s, so play with run_time=2.5":
     If TTS turns out 14.3s instead of 15s, your numbers are wrong
     and the scaler does the wrong thing on top.
  ❌ Don't use `time.sleep()` or other non-Manim timing constructs —
     the scaler only sees `self.play(run_time=)` and `self.wait()`.

Class name MUST be `LectureScene` — that's the renderer's fixed entry
point (the per-view `scene=` selector was removed 2026-05-23).

Renderer time budget: target_dur × 3-8 (480p15 default). Scenes that
would render >300s are killed by the engine; if you're rendering a 90s
manim, either simplify it OR (better) re-architect the beat as Remotion
DOM particles. See reference/engine-routing.md for the threshold.
"""
from manim import (
    Scene, ThreeDScene,
    Circle, Square, Cube, Sphere, Dot, Dot3D, Line, Arrow, VGroup, MathTex, Tex, Text,
    FadeIn, FadeOut, Write, Create, Transform, TransformMatchingTex,
    PI, ORIGIN, UP, DOWN, LEFT, RIGHT, OUT, IN,
    WHITE, BLACK, BLUE, RED, GREEN, YELLOW, ORANGE, PURPLE, TEAL, GREY,
)


class LectureScene(Scene):
    def construct(self):
        # ─── Setup (title, fixed) ────────────────────────────────────
        title = Text("标题文字", font_size=42, color=WHITE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)
        self.wait(0.4)

        # ─── Main content (write NATURAL durations; scaler matches audio) ───
        circle = Circle(radius=1.5, color=BLUE, fill_color=BLUE, fill_opacity=0.3)
        self.play(FadeIn(circle), run_time=1.0)
        self.play(circle.animate.scale(1.6), run_time=1.5)
        self.wait(0.8)

        # ─── Conclusion ──────────────────────────────────────────────
        caption = Text("说明文字", font_size=28, color=YELLOW)
        caption.to_edge(DOWN, buff=0.6)
        self.play(Write(caption), run_time=0.7)
        self.wait(2.0)
