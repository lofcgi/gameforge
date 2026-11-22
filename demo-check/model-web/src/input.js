// 키보드 입력. 액션 이름 → KeyboardEvent.code 목록. 게임 로직은 액션 이름으로만 읽는다.

export const KEYMAP = {
  left: ["ArrowLeft", "KeyA"],
  right: ["ArrowRight", "KeyD"],
  forward: ["ArrowUp", "KeyW"],
  back: ["ArrowDown", "KeyS"],
  jump: ["Space"],
};

const MAPPED = new Set(Object.values(KEYMAP).flat());

export function createInput() {
  const held = new Set();
  // 틱과 틱 사이에 눌렸다 떼어진 키. 짧게 친 키나 프레임이 밀린 동안 친 키도 한 틱은 눌린 것으로 읽힌다.
  const tapped = new Set();
  window.addEventListener("keydown", (event) => {
    if (MAPPED.has(event.code)) event.preventDefault();
    held.add(event.code);
    tapped.add(event.code);
  });
  window.addEventListener("keyup", (event) => held.delete(event.code));
  window.addEventListener("blur", () => held.clear());
  return {
    // 틱마다 한 번 부른다.
    read() {
      const actions = {};
      for (const [action, codes] of Object.entries(KEYMAP)) {
        actions[action] = codes.some((code) => held.has(code) || tapped.has(code));
      }
      tapped.clear();
      return actions;
    },
  };
}
