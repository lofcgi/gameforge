// gameforge 브리지. `gf engine ...` 명령이 게임을 조종하고 관찰하는 유일한 통로다.
// 계약은 templates/README.md 에 있다. 이 파일은 web-2d 와 web-3d 에서 같은 내용이어야 한다.
//
// 게임 루프(고정 틱 + 렌더)를 브리지가 소유한다. 그래야 하네스가 틱을 하나씩 진행할 수 있다.
// URL 쿼리: gf_manual=1 (step() 으로만 진행), gf_seed=N (난수 시드), gf_record=1 (입력·상태 기록),
//           gf_audio=1 (소리 측정)

const VERSION = 1;
// 하네스와 맞추는 브리지 버전. 명령이나 동작이 바뀌면 올린다 (tools/gf/engine/adapter.py 의 BRIDGE_VERSION).
const BRIDGE = 2;
const TICK_RATE = 60;
const TICK_SECONDS = 1 / TICK_RATE;
const SAMPLE_TICKS = 6;
const MAX_CATCH_UP_SECONDS = 0.25;
const AUDIO_SAMPLE_MS = 50;
const AUDIO_WINDOW = 4096;
const AUDIO_FLOOR_DB = -200;
// 이보다 작은 표본(-80 dBFS)이 이어지면 끊김으로 센다.
const AUDIO_SILENT_LEVEL = 0.0001;

const params = new URLSearchParams(location.search);

export const seed = Number(params.get("gf_seed") ?? 0);

let randomState = seed >>> 0;

// 시드가 같으면 같은 수열을 내는 난수(mulberry32). 게임 로직은 Math.random 대신 이것을 쓴다.
export function random() {
  randomState = (randomState + 0x6d2b79f5) >>> 0;
  let t = randomState;
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
}

const decibels = (level) => (level > 0 ? Math.max(20 * Math.log10(level), AUDIO_FLOOR_DB) : AUDIO_FLOOR_DB);

// 소리 측정. 게임 코드를 고치지 않고 Web Audio 를 가로채, 스피커(destination)로 가는 연결을 분석기를 거치게 한다.
// 잰 것은 브라우저 안의 최종 신호이고 스피커에서 난 소리가 아니다. <audio> 요소는 재생 호출만 센다.
function installAudioProbe(currentTick) {
  const startedAt = performance.now();
  const contexts = [];
  const events = [];
  const timeline = [];
  const urls = new WeakMap();
  const connect = AudioNode.prototype.connect;
  const elapsed = () => Math.round(performance.now() - startedAt);

  function register(context) {
    const input = context.createGain();
    const analyser = context.createAnalyser();
    analyser.fftSize = AUDIO_WINDOW;
    connect.call(input, analyser);
    connect.call(input, context.destination);
    contexts.push({
      context, input, analyser, samples: new Float32Array(AUDIO_WINDOW),
      created: { ms: elapsed(), tick: currentTick(), after_gesture: navigator.userActivation.hasBeenActive },
    });
  }

  window.AudioContext = class extends window.AudioContext {
    constructor(...options) {
      super(...options);
      register(this);
    }
  };

  AudioNode.prototype.connect = function (target, ...rest) {
    const tapped = contexts.find((entry) => target === entry.context.destination);
    connect.call(this, tapped ? tapped.input : target, ...rest);
    return target;
  };

  // 받아 온 파일 → 디코딩한 버퍼로 주소를 이어 붙여, 재생된 소리가 어느 파일인지 알 수 있게 한다.
  const arrayBuffer = Response.prototype.arrayBuffer;
  Response.prototype.arrayBuffer = async function () {
    const data = await arrayBuffer.call(this);
    urls.set(data, new URL(this.url).pathname);
    return data;
  };
  const decode = BaseAudioContext.prototype.decodeAudioData;
  BaseAudioContext.prototype.decodeAudioData = function (data, onDone, onError) {
    const url = urls.get(data);
    const done = (buffer) => {
      if (url) urls.set(buffer, url);
      return buffer;
    };
    if (onDone) return decode.call(this, data, (buffer) => onDone(done(buffer)), onError);
    return decode.call(this, data).then(done);
  };

  // 반복 재생되는 버퍼의 양 끝: 앞뒤 무음과 이음매의 표본 차이.
  function edges(buffer) {
    const data = buffer.getChannelData(0);
    let lead = 0;
    while (lead < data.length && Math.abs(data[lead]) < AUDIO_SILENT_LEVEL) lead += 1;
    let tail = 0;
    while (tail < data.length && Math.abs(data[data.length - 1 - tail]) < AUDIO_SILENT_LEVEL) tail += 1;
    return {
      lead_silence_ms: (1000 * lead) / buffer.sampleRate,
      tail_silence_ms: (1000 * tail) / buffer.sampleRate,
      seam_jump_db: decibels(Math.abs(data[0] - data[data.length - 1])),
    };
  }

  const start = AudioBufferSourceNode.prototype.start;
  AudioBufferSourceNode.prototype.start = function (...when) {
    const buffer = this.buffer;
    events.push({
      kind: "start", tick: currentTick(), t: currentTick() / TICK_RATE, ms: elapsed(),
      sound: (buffer && urls.get(buffer)) ?? null, length_s: buffer ? buffer.duration : null, loop: this.loop,
      context_state: this.context.state, ...(buffer && this.loop ? edges(buffer) : {}),
    });
    return start.apply(this, when);
  };
  const play = HTMLMediaElement.prototype.play;
  HTMLMediaElement.prototype.play = function () {
    events.push({
      kind: "element", tick: currentTick(), t: currentTick() / TICK_RATE, ms: elapsed(),
      sound: this.currentSrc ? new URL(this.currentSrc).pathname : null, length_s: null, loop: this.loop,
    });
    return play.call(this);
  };

  let quietRun = 0;
  setInterval(() => {
    let peak = 0;
    let squares = 0;
    let quiet = quietRun;
    for (const entry of contexts) {
      if (entry.context.state !== "running") continue;
      entry.analyser.getFloatTimeDomainData(entry.samples);
      // 창(85ms)이 표본 간격(50ms)보다 길어 겹친다. 끊김 길이는 겹치지 않는 뒤쪽 부분에서만 센다.
      const fresh = entry.samples.length - Math.round((AUDIO_SAMPLE_MS / 1000) * entry.context.sampleRate);
      entry.samples.forEach((sample, index) => {
        const level = Math.abs(sample);
        if (level > peak) peak = level;
        squares += sample * sample;
        if (index < fresh) return;
        quietRun = level < AUDIO_SILENT_LEVEL ? quietRun + 1 : 0;
        if (quietRun > quiet) quiet = quietRun;
      });
    }
    const running = contexts.filter((entry) => entry.context.state === "running");
    timeline.push({
      ms: elapsed(), tick: currentTick(), peak_db: decibels(peak),
      rms_db: decibels(Math.sqrt(squares / (AUDIO_WINDOW * Math.max(1, running.length)))),
      quiet_ms: running.length ? (1000 * quiet) / running[0].context.sampleRate : 0,
      running: running.length,
    });
    if (!running.length) quietRun = 0;
  }, AUDIO_SAMPLE_MS);

  return () => ({
    contexts: contexts.map((entry) => ({
      state: entry.context.state, sample_rate: entry.context.sampleRate, created: entry.created,
    })),
    timeline: timeline.splice(0),
    events: events.splice(0),
  });
}

let ticks = 0;
const audioProbe = params.has("gf_audio") ? installAudioProbe(() => ticks) : null;

// info: {dim, actions: {이름: {keys: [KeyboardEvent.code], move?: [x, y(, z)]}}, probe: [이름]}
// getState: () => 상태 스냅샷, tick: (dt) => 로직 한 틱, render: () => 그리기, perfCounters?: () => 객체
export function installBridge({ info, getState, tick, render, perfCounters }) {
  const manual = params.has("gf_manual");
  const recording = params.has("gf_record");
  const recorded = [];
  let fps = 0;
  let lastFrame = null;
  let backlog = 0;
  let perfOn = false;
  let frameMs = [];
  let workMs = [];

  const time = () => ticks / TICK_RATE;
  const state = () => ({ ...getState(), tick: ticks, t: time(), fps });

  function advance() {
    tick(TICK_SECONDS);
    ticks += 1;
    if (recording && ticks % SAMPLE_TICKS === 0) {
      recorded.push({ type: "state", tick: ticks, t: time(), state: state() });
    }
  }

  function frame(now) {
    requestAnimationFrame(frame);
    const elapsed = lastFrame === null ? 0 : now - lastFrame;
    lastFrame = now;
    if (elapsed > 0) {
      fps = Math.round(1000 / elapsed);
      if (perfOn) frameMs.push(elapsed);
    }
    if (manual) {
      // step() 은 한 화면 프레임 안에 여러 번 불릴 수 있다. 렌더러 중에는 화면 프레임마다 한 번만 갱신하는 것(three 의
      // 그림자 맵 등)이 있어, 프레임마다 다시 그려야 스크린샷이 지금 상태와 맞는다. 상태는 바꾸지 않는다.
      render();
      return;
    }
    const workStart = performance.now();
    backlog = Math.min(backlog + elapsed / 1000, MAX_CATCH_UP_SECONDS);
    while (backlog >= TICK_SECONDS) {
      advance();
      backlog -= TICK_SECONDS;
    }
    render();
    if (perfOn) workMs.push(performance.now() - workStart);
  }

  function actionsFor(code) {
    return Object.keys(info.actions).filter((name) => info.actions[name].keys.includes(code));
  }

  function recordInput(fields) {
    recorded.push({ type: "input", tick: ticks, t: time(), ...fields });
  }

  if (manual) {
    // 자동 실행의 Chrome 은 포커스를 잃지 않는다(Playwright 가 포커스를 흉내 낸다. 실측: 다른 탭·다른 앱을 앞으로
    // 보내도 blur 0건). 그래도 blur 가 오면 게임이 눌린 키를 놓아 결과가 달라지므로 오류로 남긴다.
    window.addEventListener("blur", () => {
      console.error(`gf bridge: 자동 실행 중에 창이 포커스를 잃었다 (tick ${ticks}). 눌러 둔 키가 풀렸을 수 있다. 다시 돌린다.`);
    });
  }

  if (recording) {
    // 누르고 있는 키. 창이 포커스를 잃으면 브라우저는 keyup 을 주지 않으므로, 그때 뗀 것으로 적는다
    // (게임도 blur 에서 키를 놓는다: src/input.js). 적지 않으면 재생이 그 키를 계속 누른다.
    const down = new Set();
    window.addEventListener("keydown", (event) => {
      if (event.repeat) return;
      down.add(event.code);
      recordInput({ down: true, device: "key", code: event.code, actions: actionsFor(event.code) });
    }, true);
    window.addEventListener("keyup", (event) => {
      if (!down.delete(event.code)) return;
      recordInput({ down: false, device: "key", code: event.code, actions: actionsFor(event.code) });
    }, true);
    window.addEventListener("blur", () => {
      for (const code of down) {
        recordInput({ down: false, device: "key", code, actions: actionsFor(code), cause: "blur" });
      }
      down.clear();
    });
    for (const [type, down] of [["mousedown", true], ["mouseup", false]]) {
      window.addEventListener(type, (event) => {
        recordInput({ down, device: "mouse", code: event.button, pos: [event.clientX, event.clientY] });
      }, true);
    }
  }

  window.__gf = {
    version: VERSION,
    bridge: BRIDGE,
    tickRate: TICK_RATE,
    info,
    state,
    step(count) {
      if (!manual) throw new Error("step 은 gf_manual=1 일 때만 쓴다");
      for (let i = 0; i < count; i += 1) advance();
      render();
      return state();
    },
    drain: () => recorded.splice(0),
    audio() {
      if (!audioProbe) throw new Error("소리 측정은 gf_audio=1 일 때만 쓴다");
      return audioProbe();
    },
    perfStart() {
      frameMs = [];
      workMs = [];
      perfOn = true;
    },
    perfStop() {
      perfOn = false;
      const average = (values) => values.reduce((sum, value) => sum + value, 0) / (values.length || 1);
      const counters = { ...(perfCounters ? perfCounters() : {}), work_ms_avg: average(workMs) };
      if (performance.memory) counters.memory_mb = performance.memory.usedJSHeapSize / 1048576;
      return { frame_ms: frameMs, counters };
    },
    ready: true,
  };

  render();
  requestAnimationFrame(frame);
}
