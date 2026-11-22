// 그리기. 게임 상태를 읽기만 하고 바꾸지 않는다.

import * as THREE from "three";
import { PLAYER } from "./core.js";

const COLORS = { sky: 0xb8c7d9, solid: 0x8c949f, hazard: 0xe6402f, goal: 0x4dd973, player: 0xf2cc4d };
const CAMERA_OFFSET = new THREE.Vector3(0, 6, 9);
const LOOK_AHEAD = new THREE.Vector3(0, 0, -2);

function boxMesh(box, color) {
  const mesh = new THREE.Mesh(
    new THREE.BoxGeometry(...box.size),
    new THREE.MeshStandardMaterial({ color, roughness: 0.9 }),
  );
  mesh.position.set(...box.center);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

function playerVisual(model) {
  if (model) {
    model.position.y = -PLAYER.size[1] / 2;
    model.traverse((node) => {
      if (node.isMesh) node.castShadow = true;
    });
    return new THREE.Group().add(model);
  }
  const radius = PLAYER.size[0] / 2;
  const mesh = new THREE.Mesh(
    new THREE.CapsuleGeometry(radius, PLAYER.size[1] - radius * 2),
    new THREE.MeshStandardMaterial({ color: COLORS.player, roughness: 0.8 }),
  );
  mesh.castShadow = true;
  return mesh;
}

function prop(model, position, yaw) {
  const copy = model.clone();
  copy.position.set(...position);
  copy.rotation.y = yaw;
  copy.traverse((node) => {
    if (node.isMesh) node.castShadow = true;
  });
  return copy;
}

function addLights(scene) {
  scene.add(new THREE.HemisphereLight(0xdfe9f5, 0x4a4e57, 1.2));
  const sun = new THREE.DirectionalLight(0xfff4e0, 2.5);
  sun.position.set(12, 20, 8);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -30, right: 30, top: 30, bottom: -30, far: 80 });
  scene.add(sun);
}

// renderer.init() 이 끝난 뒤에야 그릴 수 있어 비동기다.
export async function createView(canvas, hud, level, models) {
  const renderer = new THREE.WebGPURenderer({ canvas, antialias: true });
  await renderer.init();
  renderer.shadowMap.enabled = true;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(COLORS.sky);
  addLights(scene);
  for (const solid of level.solids) scene.add(boxMesh(solid, COLORS.solid));
  for (const hazard of level.hazards) scene.add(boxMesh(hazard, COLORS.hazard));
  if (models.beacon) {
    // 목표와 길가의 등불. 팻말(모델의 정면 +Z)이 길 쪽을 보게 돌린다.
    const [gx, gy, gz] = level.goal.center;
    scene.add(prop(models.beacon, [gx, gy - level.goal.size[1] / 2, gz], 0));
    scene.add(prop(models.beacon, [-3.4, 0, -2], Math.PI / 2));
    scene.add(prop(models.beacon, [3.4, 0, -8], -Math.PI / 2));
    scene.add(prop(models.beacon, [-3.4, 0, -15], Math.PI / 2));
  } else {
    scene.add(boxMesh(level.goal, COLORS.goal));
  }
  const player = playerVisual(models.player);
  scene.add(player);
  // 리깅된 플레이어 모델(gf gen rig 의 걷기 GLB)이면 첫 애니메이션을 걷기로 쓴다.
  const clips = models.player?.userData.animations ?? [];
  const walk = clips.length ? new THREE.AnimationMixer(models.player) : null;
  if (walk) walk.clipAction(clips[0]).play();

  const camera = new THREE.PerspectiveCamera(60, 1, 0.1, 200);

  function resize() {
    // 레티나에서는 물리 해상도로 그린다. 배율 3 이상인 화면은 2 로 묶어 그릴 픽셀 수를 막는다.
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    renderer.setSize(innerWidth, innerHeight, false);
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
  }
  window.addEventListener("resize", resize);
  resize();

  return {
    backend: renderer.backend.isWebGPUBackend ? "webgpu" : "webgl2",
    render(game) {
      player.position.set(...game.player.pos);
      player.rotation.y = game.player.facing;
      if (walk) walk.setTime(game.player.walkTime);
      camera.position.copy(player.position).add(CAMERA_OFFSET);
      camera.lookAt(player.position.clone().add(LOOK_AHEAD));
      renderer.render(scene, camera);
      hud.textContent = game.goalReached ? "GOAL!" : `deaths ${game.deaths}`;
    },
    counters() {
      const { drawCalls, triangles } = renderer.info.render;
      return { draw_calls: drawCalls, triangles, objects: scene.children.length };
    },
  };
}
