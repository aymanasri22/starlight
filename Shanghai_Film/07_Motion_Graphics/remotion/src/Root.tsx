import { Composition } from "remotion";
import { TitleTest } from "./TitleTest";

// Pipeline-test composition only. Real film titles are designed with the
// Motion Designer once the creative direction exists.
export const RemotionRoot: React.FC = () => (
  <Composition id="TitleTest" component={TitleTest} durationInFrames={96} fps={24} width={1920} height={1080} />
);
