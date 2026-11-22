// GLB 모델 로더. 모델은 assets/game/models/ 에 두고 MODELS 에 등록한다.
// 등록되지 않은 것은 그레이박스 도형으로 그린다. 규약: 원점은 발밑, 모델의 정면은 +Z, 1 단위 = 1 m.
// 플레이어 모델은 정면(+Z)이 이동 방향을 보도록 돌려진다 (core.js 의 yaw).
//   player: "./assets/game/models/player.glb"

import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

export const MODELS = {};

export async function loadModels() {
  const loader = new GLTFLoader();
  const loaded = {};
  for (const [name, url] of Object.entries(MODELS)) {
    const gltf = await loader.loadAsync(url);
    // 리깅된 모델의 애니메이션은 장면과 따로 온다. 그리는 쪽이 쓸 수 있게 붙여 둔다.
    gltf.scene.userData.animations = gltf.animations;
    loaded[name] = gltf.scene;
  }
  return loaded;
}
