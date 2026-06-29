import { Config } from "@remotion/cli/config";
import path from "path";

// El footage del repo vive en docs/footage. Lo exponemos como public dir
// para poder usar staticFile("wikimedia/atardecer_caburgua.jpg").
Config.setPublicDir(path.join(process.cwd(), "..", "docs", "footage"));
Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
