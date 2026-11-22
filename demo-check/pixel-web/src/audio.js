// 소리. 파일을 SOUNDS 에 등록하고 main.js 에서 `const audio = await loadAudio()` 로 읽는다.
//   SOUNDS = { jump: { url: "./assets/game/audio/jump.mp3", volume: 0.5 }, theme: { url: "...", volume: 0.2, loop: true } }
//
// 브라우저는 사용자의 첫 입력 전에 소리를 내지 못하고, 그 전에 AudioContext 를 만들면 콘솔 경고를 낸다.
// 그래서 파일만 먼저 받아 두고(없는 파일은 여기서 실패한다), 첫 키·클릭·터치에서 컨텍스트를 만든다.
// 입력 전에 요청된 효과음은 버리고, 반복 재생(음악)은 기억했다가 입력이 오면 시작한다.
// 재생은 게임 상태를 바꾸지 않는다. 규칙의 결과를 받아 소리만 낸다.

export const SOUNDS = {
  jump: { url: "./assets/game/audio/jump.mp3", volume: 0.4 },
  goal: { url: "./assets/game/audio/goal.mp3", volume: 0.5 },
  theme: { url: "./assets/game/audio/theme.wav", volume: 0.25, loop: true },
};

const UNLOCK_EVENTS = ["keydown", "pointerdown", "touchstart"];

export async function loadAudio() {
  const encoded = {};
  for (const [name, sound] of Object.entries(SOUNDS)) {
    const response = await fetch(sound.url);
    if (!response.ok) throw new Error(`오디오를 읽지 못했다: ${sound.url} (HTTP ${response.status})`);
    encoded[name] = await response.arrayBuffer();
  }

  let context = null;
  const buffers = {};
  const waiting = new Set();
  const looping = {};
  const started = {};

  function start(name) {
    started[name] = (started[name] ?? 0) + 1;
    const sound = SOUNDS[name];
    const source = context.createBufferSource();
    const gain = context.createGain();
    source.buffer = buffers[name];
    source.loop = Boolean(sound.loop);
    gain.gain.value = sound.volume ?? 1;
    source.connect(gain).connect(context.destination);
    source.start();
    if (sound.loop) looping[name] = source;
  }

  async function unlock() {
    for (const type of UNLOCK_EVENTS) window.removeEventListener(type, unlock, true);
    context = new AudioContext();
    await Promise.all(Object.entries(encoded).map(async ([name, data]) => {
      buffers[name] = await context.decodeAudioData(data);
    }));
    for (const name of waiting) start(name);
    waiting.clear();
  }

  if (Object.keys(SOUNDS).length) {
    for (const type of UNLOCK_EVENTS) window.addEventListener(type, unlock, true);
  }

  return {
    // 등록한 이름의 소리를 낸다. 반복 소리는 이미 나고 있으면 다시 시작하지 않는다.
    play(name) {
      if (!SOUNDS[name]) throw new Error(`등록되지 않은 소리: ${name}`);
      if (SOUNDS[name].loop && (looping[name] || waiting.has(name))) return;
      if (buffers[name]) start(name);
      // 첫 입력이 곧 소리를 내는 행동(점프)일 수 있다. 디코딩이 끝나는 대로 내도록 잠깐 맡아 둔다.
      else if (SOUNDS[name].loop || context) waiting.add(name);
    },
    // 사용자의 입력으로 소리가 풀렸는가, 이름별로 실제 재생을 시작한 횟수 (확인용).
    unlocked: () => context !== null && context.state === "running",
    started,
  };
}
