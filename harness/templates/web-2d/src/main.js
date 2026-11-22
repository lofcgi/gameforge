// 조립: 입력 → 규칙(core) → 그리기(render), 그리고 브리지 등록.

import { installBridge } from "../gf/bridge.js";
import { SOUNDS, loadAudio } from "./audio.js";
import { createGame, snapshot, step } from "./core.js";
import { KEYMAP, createInput } from "./input.js";
import { LEVEL } from "./level.js";
import { draw } from "./render.js";
import { loadImages, loadSheets } from "./sprites.js";
import { VIEW } from "./view.js";

const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const hud = document.getElementById("hud");
const stage = document.getElementById("stage");

// 픽셀 아트: 기준 해상도 캔버스를 화면의 물리 픽셀 기준 정수배로만 확대한다(nearest). 배율(devicePixelRatio)이
// 1.25 나 1.5 인 화면에서 CSS 픽셀로 정수배를 하면 게임 픽셀마다 굵기가 달라지기 때문이다. 남는 자리는 배경색 띠다.
// 고해상도 2D(VIEW.smooth): 창에 맞는 크기로 캔버스 자체를 만들어, 그림과 글자가 화면 해상도로 그려지게 한다.
function fitCanvas() {
  const fit = Math.min(innerWidth / VIEW.w, innerHeight / VIEW.h);
  const scale = VIEW.smooth ? fit : Math.max(1, Math.floor(fit * devicePixelRatio)) / devicePixelRatio;
  const pixels = VIEW.smooth ? scale * devicePixelRatio : 1;
  const width = Math.round(VIEW.w * pixels);
  const height = Math.round(VIEW.h * pixels);
  if (canvas.width !== width || canvas.height !== height) {
    canvas.width = width;
    canvas.height = height;
  }
  canvas.style.width = `${VIEW.w * scale}px`;
  canvas.style.height = `${VIEW.h * scale}px`;
  // 가운데에 두되 물리 픽셀 경계에 맞춘다. 반 픽셀에 걸치면 브라우저가 다시 표본화해 픽셀 굵기가 들쭉날쭉해진다.
  // 배율이 1.25·1.5 일 때는 CSS 정수 픽셀 중에서 물리 픽셀로도 정수인 자리를 고른다(실측: 분수 CSS 값은 어긋났다).
  const snap = (space) => {
    let offset = Math.max(0, Math.floor(space / 2));
    for (let tries = 0; tries < 8 && offset > 0 && !Number.isInteger(offset * devicePixelRatio); tries += 1) offset -= 1;
    return offset;
  };
  stage.style.left = `${snap(innerWidth - VIEW.w * scale)}px`;
  stage.style.top = `${snap(innerHeight - VIEW.h * scale)}px`;
  canvas.style.imageRendering = VIEW.smooth ? "auto" : "pixelated";
  hud.style.fontSize = `${8 * scale}px`;
}
window.addEventListener("resize", fitCanvas);
fitCanvas();

const sheets = await loadSheets();
const images = await loadImages();
const audio = await loadAudio();
// 콘솔에서 소리 상태를 볼 수 있게 둔다: __audio.unlocked(), __audio.started
window.__audio = audio;
// 음악은 "theme" 으로 등록하면 첫 입력 뒤부터 반복 재생된다.
if (SOUNDS.theme) audio.play("theme");
const input = createInput();
const game = createGame(LEVEL);
let seconds = 0;

installBridge({
  info: {
    dim: "2d",
    actions: {
      left: { keys: KEYMAP.left, move: [-1, 0] },
      right: { keys: KEYMAP.right, move: [1, 0] },
      jump: { keys: KEYMAP.jump },
    },
    probe: ["right", "left", "jump"],
  },
  getState: () => snapshot(game),
  tick: (dt) => {
    // 규칙이 낸 사건 중 같은 이름으로 등록된 소리가 있으면 낸다 (jump, death, goal).
    for (const event of step(game, input.read(), dt)) {
      if (SOUNDS[event]) audio.play(event);
    }
    seconds += dt;
  },
  render: () => {
    draw(ctx, game, { sheets, images }, seconds);
    const text = game.goalReached ? "GOAL!" : `deaths ${game.deaths}`;
    if (hud.textContent !== text) hud.textContent = text;
  },
});
