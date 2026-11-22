// 그리기. 게임 상태를 읽기만 하고 바꾸지 않는다.

import { PLAYER } from "./core.js";
import { drawFrame, drawStanding, drawTiled, frameAt, snap } from "./sprites.js";
import { VIEW } from "./view.js";

// 바닥 타일(32x32)의 위 절반은 모래, 아래 절반은 벽돌이다. 모래는 맨 윗줄에만 깐다.
const GROUND_TOP = { x: 0, y: 0, w: 32, h: 16 };
const GROUND_FILL = { x: 0, y: 16, w: 32, h: 16 };
const BACKDROP = { sky: "#0b111d", haze: "#18283a", far: "#1f3a4a", near: "#274653" };

function drawBackdrop(ctx, level, cameraX) {
  ctx.fillStyle = BACKDROP.sky;
  ctx.fillRect(0, 0, VIEW.w, VIEW.h);
  ctx.fillStyle = BACKDROP.haze;
  ctx.fillRect(0, 96, VIEW.w, VIEW.h - 96);
  // 먼 바위 기둥: 카메라의 절반 속도로 움직인다. 전경보다 어둡고 차갑다.
  const shift = Math.round(cameraX / 2);
  for (let x = 20; x < level.width; x += 96) {
    const tall = 50 + ((x * 7) % 45);
    ctx.fillStyle = BACKDROP.far;
    ctx.fillRect(x - shift, 156 - tall, 22, tall);
    ctx.fillStyle = BACKDROP.near;
    ctx.fillRect(x - shift - 3, 156 - tall, 28, 5);
  }
}

function drawGround(ctx, image, solid) {
  const top = Math.min(16, solid.h);
  drawTiled(ctx, image, { x: solid.x, y: solid.y, w: solid.w, h: top }, GROUND_TOP);
  if (solid.h > top) drawTiled(ctx, image, { x: solid.x, y: solid.y + top, w: solid.w, h: solid.h - top }, GROUND_FILL);
}

const COLORS = { sky: "#1c1f29", solid: "#6b7385", hazard: "#e6402f", goal: "#4dd973", player: "#f2d959" };

function fillRects(ctx, rects, color) {
  ctx.fillStyle = color;
  for (const rect of rects) ctx.fillRect(rect.x, rect.y, rect.w, rect.h);
}

function drawPlayer(ctx, player, sheet, seconds) {
  if (!sheet) {
    ctx.fillStyle = COLORS.player;
    ctx.fillRect(snap(player.x - PLAYER.w / 2), snap(player.y - PLAYER.h / 2), PLAYER.w, PLAYER.h);
    return;
  }
  const index = frameAt(sheet, player.vx !== 0 ? "run" : "idle", seconds);
  drawFrame(ctx, sheet, index, player.x, player.y + PLAYER.h / 2, player.facing < 0);
}

// art: { sheets, images } (sprites.js 의 loadSheets, loadImages 결과)
export function draw(ctx, game, art, seconds) {
  const { level, player } = game;
  const cameraX = snap(Math.min(Math.max(player.x - VIEW.w / 2, 0), level.width - VIEW.w));
  // 캔버스가 기준 해상도보다 크면(고해상도 2D) 그만큼 확대해 그린다. 아래의 좌표는 전부 레벨 단위다.
  const zoom = ctx.canvas.width / VIEW.w;
  ctx.setTransform(zoom, 0, 0, zoom, 0, 0);
  ctx.imageSmoothingEnabled = VIEW.smooth;
  ctx.imageSmoothingQuality = "high";
  drawBackdrop(ctx, level, cameraX);
  ctx.save();
  ctx.translate(-cameraX, 0);
  for (const solid of level.solids) drawGround(ctx, art.images.ground, solid);
  for (const hazard of level.hazards) drawStanding(ctx, art.images.cactus, hazard);
  drawStanding(ctx, art.images.flag, level.goal);
  drawPlayer(ctx, player, art.sheets.player, seconds);
  ctx.restore();
}
