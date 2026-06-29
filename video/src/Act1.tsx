import React from "react";
import { AbsoluteFill } from "remotion";
import {
  Scene,
  KenBurns,
  Caption,
  DataCallout,
  TitleCard,
  COL,
} from "./components";

// Teaser del Acto 1 del STORYBOARD.md — "Un lago que se va".
// 28 s @ 30 fps. Footage real del repo (docs/footage), narración del guion.
export const Act1Teaser: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: COL.bg }}>
      {/* 1.1 Apertura aérea */}
      <Scene from={0} durationInFrames={180}>
        <KenBurns src="wikimedia/atardecer_caburgua.jpg" panX={-2} panY={-2} />
        <TitleCard
          kicker="Araucanía · 39°S"
          title="Un lago que se va"
          subtitle="A 23 km de Pucón hay un lago único en Chile: sus aguas no salen por un río, drenan bajo tierra."
        />
      </Scene>

      {/* 1.2 Los Ojos del Caburga */}
      <Scene from={180} durationInFrames={170}>
        <KenBurns src="wikimedia/ojos_2019_01.jpg" from={1.1} to={1.22} panY={-4} />
        <Caption>
          Es como una bañera con el tapón abajo. Si entra menos de lo que sale,
          el lago se vacía hacia adentro de la tierra.
        </Caption>
      </Scene>

      {/* 1.3 La crisis */}
      <Scene from={350} durationInFrames={200}>
        <KenBurns src="wikimedia/lago_caburgua_2022.jpg" from={1.05} to={1.2} />
        <DataCallout num="−25%" label="nivel promedio · 2000-2010 vs 2011-2020" color={COL.bad} />
        <Caption>
          Entre 2010 y 2022 aparecieron 300 metros de playa donde antes había un
          metro. Una caída sin precedentes en el registro moderno.
        </Caption>
      </Scene>

      {/* 1.4 Los datos */}
      <Scene from={550} durationInFrames={170}>
        <KenBurns src="prensa/laderasur_2021_caburgua.jpg" from={1.08} to={1.2} />
        <DataCallout num="−34%" label="lluvia estación Lago Caburga · post-2010 (CR2)" color={COL.acc} />
        <Caption>
          No es solo el lago: la cuenca completa perdió un tercio de su lluvia.
          Una megasequía sin precedentes en mil años.
        </Caption>
      </Scene>

      {/* 1.5 / cierre — la recuperación como evidencia */}
      <Scene from={720} durationInFrames={180}>
        <KenBurns src="prensa/terram_2024_recuperacion.jpg" from={1.05} to={1.18} />
        <Caption>
          En 2024 volvió El Niño y el lago recuperó 350 m de costa —
          sin remover el dique. El clima manda.
        </Caption>
      </Scene>

      {/* Tarjeta final */}
      <Scene from={900} durationInFrames={150}>
        <KenBurns src="wikimedia/atardecer_caburgua.jpg" from={1.12} to={1.0} panY={2} />
        <TitleCard
          kicker="Estudio abierto y reproducible"
          title="Los datos, no las trincheras"
          subtitle="github.com/MendozaVolcanic/lago-caburga"
        />
      </Scene>
    </AbsoluteFill>
  );
};
