import React from "react";
import {
  AbsoluteFill,
  Img,
  Sequence,
  staticFile,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const SERIF = "Georgia, 'Times New Roman', serif";
const SANS = "Inter, system-ui, -apple-system, sans-serif";

// Duración de la ESCENA actual. Dentro de un <Sequence>, useVideoConfig()
// devuelve la duración de la composición completa, no la del sequence —
// por eso propagamos la duración local de la escena por contexto.
const SceneDurationContext = React.createContext<number | null>(null);
const useSceneDuration = (): number => {
  const ctx = React.useContext(SceneDurationContext);
  const { durationInFrames } = useVideoConfig();
  return ctx ?? durationInFrames;
};

// Una escena = un <Sequence> que reinicia el frame a 0 y expone su duración.
export const Scene: React.FC<{
  from: number;
  durationInFrames: number;
  children: React.ReactNode;
}> = ({ from, durationInFrames, children }) => (
  <Sequence from={from} durationInFrames={durationInFrames}>
    <SceneDurationContext.Provider value={durationInFrames}>
      {children}
    </SceneDurationContext.Provider>
  </Sequence>
);

// Paleta consistente con el sitio
export const COL = {
  bg: "#0e1a24",
  fg: "#e8eef5",
  muted: "#aebcc7",
  acc: "#4aa3df",
  bad: "#c0392b",
  ok: "#27ae60",
  sand: "#d8b88c",
};

// Imagen con Ken Burns (zoom + paneo lento) y viñeta para legibilidad del texto.
export const KenBurns: React.FC<{
  src: string;
  from?: number;
  to?: number;
  panX?: number;
  panY?: number;
}> = ({ src, from = 1.06, to = 1.18, panX = 0, panY = -3 }) => {
  const frame = useCurrentFrame();
  const durationInFrames = useSceneDuration();
  const scale = interpolate(frame, [0, durationInFrames], [from, to], {
    extrapolateRight: "clamp",
  });
  const x = interpolate(frame, [0, durationInFrames], [0, panX]);
  const y = interpolate(frame, [0, durationInFrames], [0, panY]);
  return (
    <AbsoluteFill style={{ backgroundColor: COL.bg, overflow: "hidden" }}>
      <Img
        src={staticFile(src)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale}) translate(${x}%, ${y}%)`,
        }}
      />
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(14,26,36,.15) 0%, rgba(14,26,36,.0) 35%, rgba(14,26,36,.55) 78%, rgba(14,26,36,.92) 100%)",
        }}
      />
    </AbsoluteFill>
  );
};

// Aparición/desaparición suave por opacidad según el frame local de la escena.
export const useFade = (inEnd = 18, outStart?: number) => {
  const frame = useCurrentFrame();
  const durationInFrames = useSceneDuration();
  const os = outStart ?? durationInFrames - 18;
  return interpolate(
    frame,
    [0, inEnd, os, durationInFrames],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
};

// Bajada narrativa (lower-third) con entrada desde abajo.
export const Caption: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const op = useFade();
  const y = interpolate(frame, [0, 22], [26, 0], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill
      style={{ justifyContent: "flex-end", padding: "0 110px 90px" }}
    >
      <div
        style={{
          opacity: op,
          transform: `translateY(${y}px)`,
          color: COL.fg,
          fontFamily: SANS,
          fontSize: 40,
          lineHeight: 1.4,
          maxWidth: 1250,
          textShadow: "0 2px 24px rgba(0,0,0,.7)",
        }}
      >
        {children}
      </div>
    </AbsoluteFill>
  );
};

// Cifra grande sobreimpresa (callout de dato).
export const DataCallout: React.FC<{
  num: string;
  label: string;
  color?: string;
}> = ({ num, label, color = COL.acc }) => {
  const op = useFade(14);
  const frame = useCurrentFrame();
  const pop = interpolate(frame, [0, 16], [0.82, 1], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
      <div
        style={{
          opacity: op,
          transform: `scale(${pop})`,
          textAlign: "center",
          textShadow: "0 4px 40px rgba(0,0,0,.8)",
        }}
      >
        <div style={{ fontFamily: SERIF, fontWeight: 700, fontSize: 200, color, lineHeight: 1 }}>
          {num}
        </div>
        <div style={{ fontFamily: SANS, fontSize: 38, color: COL.fg, marginTop: 14 }}>
          {label}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Tarjeta de título y de cierre.
export const TitleCard: React.FC<{
  kicker?: string;
  title: string;
  subtitle?: string;
}> = ({ kicker, title, subtitle }) => {
  const op = useFade(20);
  const frame = useCurrentFrame();
  const y = interpolate(frame, [0, 26], [22, 0], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: 80 }}>
      <div style={{ opacity: op, transform: `translateY(${y}px)`, textAlign: "center" }}>
        {kicker && (
          <div
            style={{
              fontFamily: SANS,
              letterSpacing: 8,
              textTransform: "uppercase",
              color: COL.acc,
              fontSize: 26,
              marginBottom: 22,
            }}
          >
            {kicker}
          </div>
        )}
        <div
          style={{
            fontFamily: SERIF,
            fontWeight: 700,
            color: COL.fg,
            fontSize: 110,
            lineHeight: 1.05,
            textShadow: "0 4px 40px rgba(0,0,0,.8)",
          }}
        >
          {title}
        </div>
        {subtitle && (
          <div
            style={{
              fontFamily: SANS,
              color: COL.muted,
              fontSize: 40,
              marginTop: 26,
              maxWidth: 1100,
            }}
          >
            {subtitle}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};
