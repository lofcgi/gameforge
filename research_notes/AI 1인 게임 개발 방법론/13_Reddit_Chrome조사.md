# Reddit Chrome 조사 (2026-10-22 ~ 2026-11-22) — 접근 실패 기록

조사일: 2026-11-22
상태: **Reddit 게시물을 한 건도 열지 못했다.** 이 파일에는 Reddit에서 얻은 사실이 없으며, 아래 모든 핵심 질문은 "미해결(Gaps)"이다. 게시물, URL, 점수, 날짜, 인용문은 하나도 수집하지 못했고 지어내지 않았다.

## 접근 경로와 실패 내용 (실행 로그)

| 순서 | 시도 | 결과 |
|---|---|---|
| 1 | `claude-in-chrome` skill 로드, Chrome 도구 8개를 ToolSearch 1회로 로드 | 성공 |
| 2 | `tabs_context_mcp(createIfEmpty: true)` — 조사 전용 새 탭 1개 생성 (`chrome://newtab/`) | 성공 |
| 3 | `navigate` → `https://www.reddit.com/r/aigamedev/top/?t=month` | 실패: `This site is not allowed due to safety restrictions.` |
| 4 | `navigate` → `https://old.reddit.com/r/aigamedev/top/?t=month` (지시된 1회 대체 시도) | 실패: 같은 오류 `This site is not allowed due to safety restrictions.` |
| 5 | 조사용 탭 닫기 | 실행함 |

- 차단 위치: Reddit의 로그인 벽이나 403/429가 아니라, **Claude in Chrome 확장(도구) 쪽의 사이트 차단**이다. 페이지 요청 자체가 나가지 않았고, 사이트 권한 프롬프트도 뜨지 않았다. 즉 사용자가 Chrome에서 권한을 허용해도 풀리는 종류인지 이 세션에서는 확인할 수 없다.
- 지시대로 old.reddit.com 대체 경로를 1회 시도한 뒤 중단했다. 미러 사이트, 프록시, 캐시, 다른 프런트엔드, 페이지 스크립트 등 우회는 시도하지 않았다.
- 사용자의 기존 탭/창은 열거나 읽거나 닫지 않았다. 게시, 투표, 팔로우, 로그인, 입력은 없었다. `cmux-cua` 도구는 쓰지 않았다.
- 실행하지 못한 것: 지정된 20개 서브레딧(aigamedev, gamedev, IndieDev, SoloDevelopment, indiegames, godot, Unity3D, unrealengine, threejs, ClaudeAI, ClaudeCode, codex, vibecoding, StableDiffusion, comfyui, blender, PixelArt, WebGames, playmygame, DestroyMyGame)과 지정 검색어 전부. 검색은 0건 실행됐다.

## 플레이 가능하고 1인 설계이며 AI로 만든 고품질 게임과 플레이 링크

### Takeaway
Reddit에 접근하지 못해 해당 기간의 게시물을 확인하지 못했다. 후보 목록 없음.

### Cited Findings
- 없음 (열람한 Reddit 페이지 0건).

### Inferences
- 없음. 근거가 없으므로 추정도 적지 않는다.

### Gaps
- 기간 내 게시물의 서브레딧, 제목, 작성자, URL, 날짜, 점수, 댓글 수, 플레이 링크 전부 미수집. 원인: Claude in Chrome의 reddit.com / old.reddit.com 차단.

## 제작자가 밝힌 제작 방법과 품질을 끌어올린 요인

### Takeaway
미확인. 제작자 1차 발언을 한 건도 읽지 못했다.

### Cited Findings
- 없음.

### Inferences
- 없음.

### Gaps
- 기획/GDD, 코딩 에이전트와 모델, 엔진, MCP/CLI 연동, 2D/3D 에셋 생성, 리깅/애니메이션, 셰이더/VFX, 오디오, 테스트 루프, 시간과 비용, 공유된 프롬프트/스킬/레포 모두 미수집.

## Godot/Unity/Unreal 실무자의 에이전트+엔진 워크플로, 3D 생성기, 2D/스프라이트 파이프라인 평가

### Takeaway
미확인. 이번 조사의 주목적이던 Reddit 실무자 의견 공백은 그대로 남아 있다.

### Cited Findings
- 없음.

### Inferences
- 없음.

### Gaps
- Godot MCP / Unity MCP / Unity CLI / Unreal MCP / Blender MCP, 헤드리스 테스트, Meshy / Tripo / Hunyuan3D의 게임 투입 가능성(리토폴로지, 리깅, 애니메이션), 스프라이트 시트 파이프라인에 대한 칭찬과 비판 모두 미수집.

## 댓글의 칭찬과 "slop" 비판, 서브레딧 AI 콘텐츠 규칙

### Takeaway
미확인. 댓글과 서브레딧 규칙 페이지를 열지 못했다.

### Cited Findings
- 없음.

### Inferences
- 없음.

### Gaps
- 각 서브레딧의 AI 콘텐츠 규칙(공개 표기 의무, 금지 여부, 전용 플레어)과 댓글 반응 경향 미수집.

## AAA급에 근접하면서 플레이 가능한 사례

### Takeaway
미확인.

### Cited Findings
- 없음.

### Inferences
- 없음.

### Gaps
- 해당 사례의 존재 여부 자체를 Reddit에서 확인하지 못했다.

## 배경(기간 외) 및 추가 확인 항목

### Takeaway
두 항목 모두 미확인.

### Cited Findings
- 없음.

### Inferences
- 없음.

### Gaps
- Slotbound / 슬롯바운드 개발자의 Reddit 게시물(2026년 여름, 스택 공개): 검색하지 못함.
- "2026년 10월 Steam 출시작의 49.9%가 AI 사용을 공개" 통계의 원 Reddit 게시물: 검색하지 못함.

## 다음에 시도할 수 있는 경로 (사용자 결정 필요)

- Claude in Chrome 확장 설정에서 reddit.com이 차단 목록에 있는지 사용자가 직접 확인한다. 도구 수준의 고정 차단이라면 설정으로 풀리지 않는다.
- 사용자가 관심 스레드를 직접 열어 본문을 텍스트/PDF로 저장해 주면 그 파일을 분석할 수 있다.
- Reddit 공식 API(사용자 본인 OAuth 앱)를 사용자가 직접 설정해 제공하는 방법이 있다. 자격증명은 에이전트가 입력하지 않는다.
- Reddit 대신 같은 제작자들이 올리는 다른 1차 출처(itch.io devlog, GitHub README, X, YouTube devlog, Hacker News Show HN)로 실무자 의견을 보완한다.
