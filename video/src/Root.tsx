import React from "react";
import { Composition } from "remotion";
import { Act1Teaser } from "./Act1";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Act1Teaser"
        component={Act1Teaser}
        durationInFrames={1050}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
