import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig, Easing } from "remotion";

// Transparent-background kinetic type test: Latin + CJK, tracking ease, hairline wipe.
export const TitleTest: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const ease = Easing.bezier(0.16, 1, 0.3, 1);
  const inP = interpolate(frame, [0, 36], [0, 1], { extrapolateRight: "clamp", easing: ease });
  const out = interpolate(frame, [durationInFrames - 18, durationInFrames], [1, 0], { extrapolateLeft: "clamp" });
  const cjk = spring({ frame: frame - 10, fps, config: { damping: 200 } });
  const line = interpolate(frame, [6, 40], [0, 1], { extrapolateRight: "clamp", easing: ease });
  const shadow = "0 2px 30px rgba(0,0,0,0.55), 0 0 2px rgba(0,0,0,0.35)"; // legibility over bright plates
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: out, textShadow: shadow }}>
      <div style={{ fontFamily: "Noto Serif CJK SC", fontWeight: 600, fontSize: 150, color: "#F3EDE2",
        opacity: cjk, transform: `translateY(${(1 - cjk) * 24}px)`, letterSpacing: 18 }}>上海</div>
      <div style={{ width: 520 * line, height: 2, background: "#C9A46A", margin: "28px 0", boxShadow: "0 0 18px rgba(0,0,0,0.5)" }} />
      <div style={{ fontFamily: "Inter", fontWeight: 300, fontSize: 40, color: "#F3EDE2",
        letterSpacing: `${0.9 - 0.5 * inP}em`, opacity: inP, textTransform: "uppercase" }}>
        Pipeline Test · Not Film Content
      </div>
    </AbsoluteFill>
  );
};
