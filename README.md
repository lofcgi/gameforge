# game

AI로 1인이 게임을 만들기 위한 작업 저장소다. 조사, 제작 하네스, 그 하네스로 만드는 게임이 함께 들어 있다.

| 폴더 | 내용 |
|---|---|
| `reports/`, `research_notes/` | 2026-10-22 ~ 11-22 기간의 AI 1인 게임 제작 방법론 조사 |
| `harness/` | Claude Code 플러그인 `gameforge`. 기획부터 공개까지 단계별로 진행하는 하네스. 설명은 `harness/README.md` |
| `demo-check/` | 하네스 검증용 데모 6종 (Godot·웹 × 픽셀·일반 2D·3D)과 증거 목록 `EVIDENCE.md` |
| `games/cat-angler/` | 별주부전 모티브의 2D 픽셀 낚시 게임. 현재 그레이박스 단계 |
| `.claude/handoffs/` | 작업 인계 기록. 이어서 작업할 때 가장 최근 파일부터 읽는다 |

## 시작하기

```sh
brew install uv ffmpeg node bun
brew install --cask godot blender
cp .env.example .env        # FAL_KEY 를 채운다
cd harness/tools && uv sync && uv run pytest -q
```

게임 실행:

```sh
uv run -q --project harness/tools gf --project games/cat-angler engine run
```

하네스로 새 게임 시작:

```sh
cd <게임 폴더>
claude --plugin-dir <이 저장소>/harness
# 세션 안에서 /gameforge:gf-start
```

## 알아 둘 것

- 생성 API(fal) 호출은 돈이 든다. 호출 기록은 각 게임의 `.gf/ledger.jsonl` 에 남는다.
- 수집한 레퍼런스 이미지는 남의 저작물이라 저장소에 없다. 출처가 든 메타만 있다.
- 문서 안의 `/Users/iyeonsang/Desktop/game/...` 경로는 처음 작업한 컴퓨터의 절대 경로다. 다른 컴퓨터에서는 이 저장소의 위치로 바꿔 읽는다.
