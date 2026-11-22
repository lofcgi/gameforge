// 게임 규칙. three.js 도 DOM 도 모른다: 같은 입력을 같은 순서로 넣으면 항상 같은 결과가 나온다.
// 충돌은 축 정렬 상자(AABB)만 쓴다. 플레이어 좌표는 몸통 중심이다.

export const PLAYER = { size: [0.8, 1.8, 0.8], speed: 5, jumpSpeed: 7, gravity: 18 };

const X = 0;
const Y = 1;
const Z = 2;

export function createGame(level) {
  return {
    level,
    player: { pos: [...level.spawn], vel: [0, 0, 0], onFloor: false, facing: yaw(0, -1), walkTime: 0 },
    deaths: 0,
    goalReached: false,
    jumpWasDown: false,
  };
}

// 모델의 정면(+Z)이 수평 방향 (x, z) 를 보게 하는 y 회전. 방향 규약은 하네스의 templates/README.md 7절.
export function yaw(x, z) {
  return Math.atan2(x, z);
}

function overlaps(pos, box) {
  return [X, Y, Z].every((axis) => Math.abs(pos[axis] - box.center[axis]) < (PLAYER.size[axis] + box.size[axis]) / 2);
}

function moveAxis(player, solids, axis, delta) {
  player.pos[axis] += delta;
  for (const solid of solids) {
    if (!overlaps(player.pos, solid)) continue;
    const reach = (PLAYER.size[axis] + solid.size[axis]) / 2;
    player.pos[axis] = solid.center[axis] + (delta > 0 ? -reach : reach);
    player.vel[axis] = 0;
    if (axis === Y && delta < 0) player.onFloor = true;
  }
}

function respawn(game) {
  game.deaths += 1;
  Object.assign(game.player, { pos: [...game.level.spawn], vel: [0, 0, 0], onFloor: false });
}

// input: {left, right, forward, back, jump} 불리언. 이동은 월드 축 기준이다(forward = -z).
export function step(game, input, dt) {
  const { player, level } = game;
  const moveX = (input.right ? 1 : 0) - (input.left ? 1 : 0);
  const moveZ = (input.back ? 1 : 0) - (input.forward ? 1 : 0);
  const length = Math.hypot(moveX, moveZ) || 1;
  player.vel[X] = (moveX / length) * PLAYER.speed;
  player.vel[Z] = (moveZ / length) * PLAYER.speed;
  player.vel[Y] -= PLAYER.gravity * dt;
  if (input.jump && !game.jumpWasDown && player.onFloor) player.vel[Y] = PLAYER.jumpSpeed;
  game.jumpWasDown = input.jump;
  if (moveX !== 0 || moveZ !== 0) player.facing = yaw(moveX, moveZ);

  player.onFloor = false;
  moveAxis(player, level.solids, X, player.vel[X] * dt);
  moveAxis(player, level.solids, Z, player.vel[Z] * dt);
  moveAxis(player, level.solids, Y, player.vel[Y] * dt);

  // 걷기 애니메이션의 시각. 규칙이 세므로 재생·캡처에서 같은 자세가 나온다.
  if ((moveX !== 0 || moveZ !== 0) && player.onFloor) player.walkTime += dt;

  if (player.pos[Y] < level.killY || level.hazards.some((hazard) => overlaps(player.pos, hazard))) {
    respawn(game);
  } else if (overlaps(player.pos, level.goal)) {
    game.goalReached = true;
  }
}

export function snapshot(game) {
  const { player, level } = game;
  return {
    level: level.name,
    player: { pos: [...player.pos], vel: [...player.vel], on_floor: player.onFloor },
    goal: { pos: [...level.goal.center], reached: game.goalReached },
    deaths: game.deaths,
  };
}
