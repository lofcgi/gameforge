// 조립: 입력 → 규칙(core) → 그리기(render), 그리고 브리지 등록.

import { installBridge } from "../gf/bridge.js";
import { createGame, snapshot, step } from "./core.js";
import { KEYMAP, createInput } from "./input.js";
import { LEVEL } from "./level.js";
import { loadModels } from "./models.js";
import { createView } from "./render.js";

const models = await loadModels();
const view = await createView(document.getElementById("game"), document.getElementById("hud"), LEVEL, models);
const input = createInput();
const game = createGame(LEVEL);

installBridge({
  info: {
    dim: "3d",
    renderer: view.backend,
    actions: {
      left: { keys: KEYMAP.left, move: [-1, 0, 0] },
      right: { keys: KEYMAP.right, move: [1, 0, 0] },
      forward: { keys: KEYMAP.forward, move: [0, 0, -1] },
      back: { keys: KEYMAP.back, move: [0, 0, 1] },
      jump: { keys: KEYMAP.jump },
    },
    probe: ["forward", "back", "left", "right", "jump"],
  },
  getState: () => snapshot(game),
  tick: (dt) => step(game, input.read(), dt),
  render: () => view.render(game),
  perfCounters: view.counters,
});
