// 게임 규칙. DOM 도 캔버스도 모른다: 같은 입력을 같은 순서로 넣으면 항상 같은 결과가 나온다.
// 플레이어 좌표는 몸통 중심이다. facing 은 마지막으로 움직인 방향(1: 오른쪽, -1: 왼쪽)이고 멈춰도 유지된다.

export const PLAYER = { w: 10, h: 14, speed: 90, jumpSpeed: 230, gravity: 700 };

export function createGame(level) {
  return {
    level,
    player: { x: level.spawn.x, y: level.spawn.y, vx: 0, vy: 0, onFloor: false, facing: 1 },
    deaths: 0,
    goalReached: false,
    events: { jump: 0, death: 0, goal: 0 },
    jumpWasDown: false,
  };
}

function bodyRect(player) {
  return { x: player.x - PLAYER.w / 2, y: player.y - PLAYER.h / 2, w: PLAYER.w, h: PLAYER.h };
}

function overlaps(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}

function moveX(player, solids, dx) {
  player.x += dx;
  for (const solid of solids) {
    if (!overlaps(bodyRect(player), solid)) continue;
    player.x = dx > 0 ? solid.x - PLAYER.w / 2 : solid.x + solid.w + PLAYER.w / 2;
    player.vx = 0;
  }
}

function moveY(player, solids, dy) {
  player.y += dy;
  player.onFloor = false;
  for (const solid of solids) {
    if (!overlaps(bodyRect(player), solid)) continue;
    if (dy > 0) {
      player.y = solid.y - PLAYER.h / 2;
      player.onFloor = true;
    } else {
      player.y = solid.y + solid.h + PLAYER.h / 2;
    }
    player.vy = 0;
  }
}

function respawn(game) {
  game.deaths += 1;
  Object.assign(game.player, { x: game.level.spawn.x, y: game.level.spawn.y, vx: 0, vy: 0, onFloor: false, facing: 1 });
}

// input: {left, right, jump} 불리언.
// 이번 틱에 일어난 일의 이름들("jump", "death", "goal")을 돌려준다. 효과음·이펙트는 이것을 받아 낸다(main.js).
export function step(game, input, dt) {
  const { player, level } = game;
  const events = [];
  player.vy += PLAYER.gravity * dt;
  if (input.jump && !game.jumpWasDown && player.onFloor) {
    player.vy = -PLAYER.jumpSpeed;
    events.push("jump");
  }
  game.jumpWasDown = input.jump;
  player.vx = ((input.right ? 1 : 0) - (input.left ? 1 : 0)) * PLAYER.speed;
  if (player.vx !== 0) player.facing = Math.sign(player.vx);
  moveX(player, level.solids, player.vx * dt);
  moveY(player, level.solids, player.vy * dt);

  const body = bodyRect(player);
  if (player.y > level.killY || level.hazards.some((hazard) => overlaps(body, hazard))) {
    respawn(game);
    events.push("death");
  } else if (overlaps(body, level.goal) && !game.goalReached) {
    game.goalReached = true;
    events.push("goal");
  }
  for (const event of events) game.events[event] += 1;
  return events;
}

export function snapshot(game) {
  const { player, level } = game;
  return {
    level: level.name,
    player: { pos: [player.x, player.y], vel: [player.vx, player.vy], on_floor: player.onFloor },
    goal: { pos: [level.goal.x + level.goal.w / 2, level.goal.y + level.goal.h / 2], reached: game.goalReached },
    deaths: game.deaths,
    jumps: game.events.jump,
  };
}
