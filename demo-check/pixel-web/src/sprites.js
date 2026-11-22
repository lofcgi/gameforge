// 그림 로더와 그리기 도우미. 에셋을 넣으면 SHEETS / IMAGES 에 등록한다. 등록되지 않은 것은 그레이박스 도형으로 그린다.
// 좌표와 크기는 모두 레벨 단위(기준 해상도 320x180)다. 그림 픽셀 ÷ VIEW.ppu = 화면에서의 크기.
//
// SHEETS (애니메이션). player 를 등록하면 플레이어가 그레이박스 사각형 대신 그것을 쓴다.
//   `gf post sheet` 의 매니페스트:  player: { manifest: "./assets/game/sprites/player_walk.json" }
//     매니페스트의 애니메이션이 "run" 이 되고 첫 프레임이 "idle" 이 된다. 그림은 오른쪽을 보게 만든다.
//   같은 크기 칸의 격자 시트:       player: { url: "./assets/game/player_sheet.png", cell: 16, fps: 8, animations: { idle: [0, 1], run: [2, 3, 4, 5] } }
// IMAGES (정지 그림):               ground: "./assets/game/sprites/ground.png"

import { VIEW } from "./view.js";

export const SHEETS = {
  player: { manifest: "./assets/game/sprites/player_walk.json" },
};
export const IMAGES = {
  ground: "./assets/game/sprites/ground.png",
  cactus: "./assets/game/sprites/cactus.png",
  flag: "./assets/game/sprites/flag.png",
};

async function loadImage(url) {
  const image = new Image();
  image.src = url;
  await image.decode();
  return image;
}

async function loadManifest(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`스프라이트 매니페스트를 읽지 못했다: ${url} (HTTP ${response.status})`);
  const data = await response.json();
  const [animation] = Object.values(data.animations);
  const frames = animation.frames;
  return {
    image: await loadImage(new URL(data.image, new URL(url, location.href)).href),
    frames,
    fps: animation.fps,
    animations: { idle: [0], run: frames.map((_, index) => index) },
  };
}

async function loadGrid({ url, cell, fps = 8, animations }) {
  const image = await loadImage(url);
  const columns = Math.floor(image.width / cell);
  const count = columns * Math.floor(image.height / cell);
  const frames = Array.from({ length: count }, (_, index) => ({
    x: (index % columns) * cell, y: Math.floor(index / columns) * cell, w: cell, h: cell,
  }));
  return { image, frames, fps, animations };
}

export async function loadSheets() {
  const loaded = {};
  for (const [name, sheet] of Object.entries(SHEETS)) {
    loaded[name] = sheet.manifest ? await loadManifest(sheet.manifest) : await loadGrid(sheet);
  }
  return loaded;
}

export async function loadImages() {
  const loaded = {};
  for (const [name, url] of Object.entries(IMAGES)) loaded[name] = await loadImage(url);
  return loaded;
}

// 픽셀 아트는 화면 픽셀에 맞춰야 번지지 않는다. 고해상도 2D 는 소수 좌표 그대로 그린다.
export function snap(value) {
  return VIEW.smooth ? value : Math.round(value);
}

// 지금 시각의 애니메이션 프레임 번호.
export function frameAt(sheet, animation, seconds) {
  const frames = sheet.animations[animation];
  return frames[Math.floor(seconds * sheet.fps) % frames.length];
}

// 시트의 index 번째 프레임을, 아래 가운데(발)가 (x, feetY) 에 오게 그린다. flip 이면 좌우를 뒤집는다.
export function drawFrame(ctx, sheet, index, x, feetY, flip = false) {
  const { x: sx, y: sy, w, h } = sheet.frames[index];
  ctx.save();
  ctx.translate(snap(x), snap(feetY));
  if (flip) ctx.scale(-1, 1);
  ctx.drawImage(sheet.image, sx, sy, w, h, snap(-w / 2 / VIEW.ppu), -h / VIEW.ppu, w / VIEW.ppu, h / VIEW.ppu);
  ctx.restore();
}

// 정지 그림을, 아래 가운데가 상자(rect)의 아래 가운데에 오게 그린다. 그림이 상자보다 커도 늘리지 않는다.
export function drawStanding(ctx, image, rect) {
  const w = image.width / VIEW.ppu;
  const h = image.height / VIEW.ppu;
  ctx.drawImage(image, snap(rect.x + rect.w / 2 - w / 2), snap(rect.y + rect.h - h), w, h);
}

// 그림의 일부(source: 그림 픽셀 {x, y, w, h}, 없으면 전체)를 상자(rect)에 늘리지 않고 반복해서 깐다. 넘치는 부분은 잘린다.
export function drawTiled(ctx, image, rect, source = { x: 0, y: 0, w: image.width, h: image.height }) {
  const w = source.w / VIEW.ppu;
  const h = source.h / VIEW.ppu;
  ctx.save();
  ctx.beginPath();
  ctx.rect(rect.x, rect.y, rect.w, rect.h);
  ctx.clip();
  for (let y = rect.y; y < rect.y + rect.h; y += h) {
    for (let x = rect.x; x < rect.x + rect.w; x += w) {
      ctx.drawImage(image, source.x, source.y, source.w, source.h, x, y, w, h);
    }
  }
  ctx.restore();
}
