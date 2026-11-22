// 레벨 데이터. 단위는 미터, y 가 위, forward 입력은 -z 로 간다. 상자는 중심과 크기로 적는다.
// 그레이박스 단계에서는 이 파일만 고쳐 레벨을 바꾼다.

export const LEVEL = {
  name: "graybox-1",
  killY: -8,
  spawn: [0, 1, 0],
  solids: [
    { center: [0, -0.5, -4], size: [8, 1, 14] },
    { center: [0, -0.5, -21], size: [8, 1, 16] },
    { center: [0, 0.375, -18], size: [8, 0.75, 2] },
  ],
  hazards: [
    { center: [0, -2.5, -12], size: [8, 1, 2] },
    { center: [-1.5, 0.2, -24], size: [3, 0.4, 1] },
  ],
  goal: { center: [0, 1, -27], size: [1.5, 2, 1.5] },
};
