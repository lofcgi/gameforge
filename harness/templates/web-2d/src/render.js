// 그리기. 게임 상태를 읽기만 하고 바꾸지 않는다.

import { PLAYER } from "./core.js";
import { drawFrame, frameAt, snap } from "./sprites.js";
import { VIEW } from "./view.js";

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
  ctx.fillStyle = COLORS.sky;
  ctx.fillRect(0, 0, VIEW.w, VIEW.h);
  ctx.save();
  ctx.translate(-cameraX, 0);
  fillRects(ctx, level.solids, COLORS.solid);
  fillRects(ctx, level.hazards, COLORS.hazard);
  fillRects(ctx, [level.goal], COLORS.goal);
  drawPlayer(ctx, player, art.sheets.player, seconds);
  ctx.restore();
}
