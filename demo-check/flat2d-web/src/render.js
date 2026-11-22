// 그리기. 게임 상태를 읽기만 하고 바꾸지 않는다.

import { PLAYER } from "./core.js";
import { drawFrame, drawStanding, drawTiled, frameAt, snap } from "./sprites.js";
import { VIEW } from "./view.js";

// 바닥 타일(128x128 px = 32 단위)의 위 절반은 이끼, 아래 절반은 바위다. 이끼는 맨 윗줄에만 깐다.
const GROUND_TOP = { x: 0, y: 0, w: 128, h: 64 };
const GROUND_FILL = { x: 0, y: 64, w: 128, h: 64 };
const TOP_UNITS = 16;
const BACKDROP = { sky: "#1d1a3a", glow: "#2a2552", far: "#262148", near: "#2f2a5c", star: "#f3e9c8" };

function drawBackdrop(ctx, level, cameraX) {
  ctx.fillStyle = BACKDROP.sky;
  ctx.fillRect(0, 0, VIEW.w, VIEW.h);
  ctx.fillStyle = BACKDROP.glow;
  ctx.fillRect(0, 100, VIEW.w, VIEW.h - 100);
  // 별과 먼 언덕: 카메라보다 느리게 움직인다. 전경보다 어둡고 채도가 낮다.
  ctx.fillStyle = BACKDROP.star;
  for (let index = 0; index < 40; index += 1) {
    const x = ((index * 97) % 700) - cameraX / 4;
    const y = (index * 53) % 95;
    ctx.fillRect(x, y, 1, 1);
  }
  for (const [colour, base, radius, speed] of [[BACKDROP.far, 150, 70, 3], [BACKDROP.near, 168, 55, 2]]) {
    ctx.fillStyle = colour;
    for (let x = -40; x < level.width + 80; x += 120) {
      ctx.beginPath();
      ctx.ellipse(x + radius - cameraX / speed, base, radius, radius * 0.7, 0, Math.PI, 2 * Math.PI);
      ctx.fill();
    }
    ctx.fillRect(0, base, VIEW.w, VIEW.h - base);
  }
}

function drawGround(ctx, image, solid) {
  const top = Math.min(TOP_UNITS, solid.h);
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
  for (const hazard of level.hazards) drawStanding(ctx, art.images.urchin, hazard);
  drawStanding(ctx, art.images.lantern, level.goal);
  drawPlayer(ctx, player, art.sheets.player, seconds);
  ctx.restore();
}
