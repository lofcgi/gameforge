# HN·Reddit 원문 보강: AI-first 1인 게임 제작 (2026-10-22 ~ 2026-11-22)

> 수집일 2026-11-22. 수집 경로와 결과:
> - **Hacker News Algolia API**: 정상 동작. `created_at_i>1792627200,created_at_i<1795392000` (2026-10-22 00:00 UTC ~ 2026-11-23 00:00 UTC, `date -u`로 검증)로 스토리 검색어 50개, 댓글 검색어 9개를 돌렸고 스레드 약 30개를 `items/<id>`로 받았다. 아래 점수·댓글 수·작성 시각은 모두 이 API가 2026-11-22에 돌려준 값이다.
> - **Reddit: 전 경로 실패.** `www.reddit.com/r/aigamedev/top.json` → HTTP 403, `api.reddit.com/...` → 403, `www.reddit.com/r/gamedev/search.json` → 403, `www.reddit.com/.../top/.rss`와 `/r/aigamedev/.rss` → 429, `old.reddit.com/.../.json`·`.rss` → 302로 로그인 페이지(`/login/?reason=lor2`)로 이동. 인증 우회는 시도하지 않았다. **따라서 이 노트에는 Reddit 원문에서 직접 확인한 내용이 하나도 없다.**
> - **Lobsters**: `t/games.json`, `t/ai.json`, `t/vibecoding.json` 모두 200. 기간 내 AI 게임 제작 관련 글은 없었다(`vibecoding` 태그는 빈 결과).
> - 링크된 블로그 원문(notesbylex.com, simonwillison.net, sandromaglione.com)은 curl로 직접 읽었다. GitHub 스타는 GitHub API, Steam 정보는 Steam `appdetails` API로 2026-11-22에 조회했다.
> - 표기: **[1차]** = 제작자 본인의 글/댓글, **[커뮤니티]** = 제3자 의견. "댓글 순서"는 HN 실제 랭킹이 아니라 답글 수 기준으로 정렬해 읽었다(Algolia가 댓글 점수를 제공하지 않음).

## 1. 기간 내 참여도가 높았던 글과, 작성자가 실제로 한 일

### Takeaway
기간 내 HN에서 "AI로 만든 게임/워크플로" 글 중 참여도 1위는 Lex Toumbourou의 "Fable 5.2 one-shotted my nephew's dream game"(506점, 댓글 456)이고, 구체적인 방법론 밀도가 가장 높은 글은 Sandro Maglione의 "Indie Game Development with AI"(31점, 댓글 43)와 Simon Willison의 "The October inflection point for vibe game development"(47점, 댓글 54)다. 기간 내 상위 글은 거의 전부 **브라우저(HTML/JS, three.js) + Claude 계열 코딩 에이전트** 조합이며, Godot/Unity/Unreal로 출시까지 간 1차 사례는 댓글 수준에서만 확인된다.

### Cited Findings

**기간 내 글 목록 (점수 순, 모두 API 타임스탬프 기준)**

| 작성일(UTC) | 점수 / 댓글 | 구분 | 제목 | HN 링크 |
|---|---|---|---|---|
| 2026-11-09 | 506 / 456 | 1차 | Fable 5.2 one-shotted my nephew's dream game | https://news.ycombinator.com/item?id=50433659 |
| 2026-11-15 | 232 / 68 | 제3자 제출(제작 측 댓글 있음) | WebGL Flight Simulator with seed generated terrain (Baron) | https://news.ycombinator.com/item?id=50510296 |
| 2026-10-31 | 196 / 124 | 뉴스 | Anthropic takes steps to block Claude from reverse-engineering video games | https://news.ycombinator.com/item?id=50320255 |
| 2026-11-14 | 174 / 44 | 1차 | Show HN: A terminal-native idle factory game (terminactory, Rust+ratatui) | https://news.ycombinator.com/item?id=50497132 |
| 2026-11-16 | 166 / 83 | 1차 | My Quest to push native Three.js quality match AAA Game Engines | https://news.ycombinator.com/item?id=50523291 |
| 2026-11-18 | 149 / 72 | 1차(AI 사용 여부 본인 미언급) | Show HN: Type Fighter 2 | https://news.ycombinator.com/item?id=50544821 |
| 2026-11-03 | 129 / 76 | 1차 | Show HN: Uncracked City, detective game where you question LLM suspects that lie | https://news.ycombinator.com/item?id=50358352 |
| 2026-10-30 | 126 / 144 | 뉴스 | Anthropic Cracking Down on Video Game Rewrites | https://news.ycombinator.com/item?id=50304358 |
| 2026-11-08 | 117 / 22 | 1차(제작법 미공개) | Show HN: Ghanaian street games you can play in the browser | https://news.ycombinator.com/item?id=50414117 |
| 2026-11-15 | 89 / 21 | 1차 | Show HN: The Last Complication (Zachtronics풍 퍼즐) | https://news.ycombinator.com/item?id=50511718 |
| 2026-10-30 | 85 / 43 | 1차 | Show HN: I built a multiplayer game where you're an aerial fighter cat (catcopter) | https://news.ycombinator.com/item?id=50305320 |
| 2026-11-10 | 73 / 90 | 제3자 제출 | Saltline: First-person shooter built by Fable 5.2 | https://news.ycombinator.com/item?id=50444850 |
| 2026-11-12 | 72 / 61 | 1차 | Show HN: Fable52.games – Play and inspect Fable 5.2 single-file HTML games | https://news.ycombinator.com/item?id=50469007 |
| 2026-11-20 | 58 / 60 | 뉴스 | Epic Games Turns to AI Coding for the Unreal Engine | https://news.ycombinator.com/item?id=50573681 |
| 2026-10-28 | 47 / 54 | 1차 | The October inflection point for vibe game development | https://news.ycombinator.com/item?id=50273753 |
| 2026-11-16 | 43 / 99 | 뉴스 | Generative AI Usage in the Games Industry (노조 매니페스토) | https://news.ycombinator.com/item?id=50519043 |
| 2026-11-09 | 31 / 43 | 1차 | Indie Game Development with AI | https://news.ycombinator.com/item?id=50432523 |
| 2026-11-21 | 27 / 25 | 1차 | Show HN: I made a PS1 style racing game (Outpost Racer) | https://news.ycombinator.com/item?id=50589184 |
| 2026-11-01 | 21 / 15 | 1차 | I vibecoded a 2d pixel game in 6h yesterday | https://news.ycombinator.com/item?id=50326721 |
| 2026-11-20 | 5 / 1 | 1차 | Open-source harness that makes Claude better for game dev (WASD Engine) | https://news.ycombinator.com/item?id=50578508 |

**(a) Lex Toumbourou – Aiden's Revenge, 12스테이지 4인용 beat 'em up [1차]**
- 조카가 그린 손그림(영웅 5명, 보스 12명, 스토리 개요)을 기획서로 삼았다. 6월 버전은 Claude Code(Opus 4.8, Fable 5)와 AIOriented.dev의 횡스크롤 템플릿으로 만들었지만 "2~3분 이상 할 가치가 없었다"고 한다. — [notesbylex.com](https://notesbylex.com/fable-5-2-one-shotted-my-nephews-dream-game)
- Fable 5.2(얼리 액세스)에 자기 전에 프롬프트 하나를 던졌다. 프롬프트 요지: "현대판 Ninja Turtles 아케이드처럼, 최대한 재미있게", 이미지 생성은 OpenAI ChatGPT Images 2.5, 효과음은 ElevenLabs(키 파일 경로 제공), `generation/scans`의 스캔 그림을 스프라이트시트로 변환, 컨트롤러 4인 플레이, "Commit as you go… Start fresh where it makes sense". — [notesbylex.com](https://notesbylex.com/fable-5-2-one-shotted-my-nephews-dream-game)
- 결과: 기존 코드 대부분을 버리고 다시 썼고, 첫 실행에서 이미지 약 175장과 오디오 약 140개를 생성했다. 요청하지 않은 컷신, 부술 수 있는 상자, 엔딩이 들어갔다. — [notesbylex.com](https://notesbylex.com/fable-5-2-one-shotted-my-nephews-dream-game)
- 테스트: 추론 기록을 보니 에이전트가 **게임을 플레이하는 봇을 작성해 headless 브라우저로 12스테이지를 모두 돌리고 스크린샷을 검사**했다. — [notesbylex.com](https://notesbylex.com/fable-5-2-one-shotted-my-nephews-dream-game)
- 이후 반복: 아이들과 플레이테스트 → 캐릭터 특수기 추가, 가족 사진 몇 장을 참고로 주고 캐릭터를 5명에서 18명으로 확장. 캐릭터를 추가할 때마다 Claude가 컷신 아트와 스토리를 다시 만들었다. — [notesbylex.com](https://notesbylex.com/fable-5-2-one-shotted-my-nephews-dream-game)
- 최종 사용량: Claude 약 600 요청/2일(캐시 읽기 약 320M 토큰, 캐시 쓰기 19M, 출력 1M), OpenAI 이미지 약 500장, ElevenLabs 음악 11곡·효과음 약 100개·아나운서 대사 90개. — [notesbylex.com](https://notesbylex.com/fable-5-2-one-shotted-my-nephews-dream-game)
- 비용: 테스트 당시 토큰은 무료였고, Fable 5.2 API 가격이면 Claude 토큰만 약 $300였을 것이라고 본인이 댓글로 밝혔다. — [HN 50433659](https://news.ycombinator.com/item?id=50433659)
- 배포: `aidens-revenge.pages.dev`(Cloudflare Pages 도메인)에 올라가 있음이 댓글의 애셋 URL로 확인된다. — [HN 50433659](https://news.ycombinator.com/item?id=50433659)

**(b) Simon Willison – 브라우저 게임 4종 [1차]**
- 주장: 2026년 10월이 vibe coding 게임의 변곡점이며, Claude Opus 5.5가 3D 모델링, 음악 생성, 게임 디자인에서 의미 있게 좋아졌다. "Make it a LOT more fun"이라는 지시가 실제로 통했다고 한다. GPT-6 Astra는 "아직 그 수준은 아니다"라는 인상(본인이 체계적 비교는 아니라고 밝힘). — [simonwillison.net](https://simonwillison.net/2026/Oct/28/vibe-game-development/)
- 스택: 네 게임 모두 HTML+JavaScript, 브라우저 실행, 정적 호스팅(GitHub Pages 또는 Cloudflare Pages). "three.js를 쓰라고 하면 잘 된다. Claude는 이미지 생성 모델이 없지만 풀컬러 3D 모델을 코드로 만든다." — [simonwillison.net](https://simonwillison.net/2026/Oct/28/vibe-game-development/)
- 과정: Tree Appreciator는 일반 Claude 채팅에서 프롬프트 1회로 완성. Emberwick은 "엔진 데모 → 지형·지하·동굴 추가 → 실제 게임화(플레이 영역 4배, 플롯, 마법 시스템)" 3단계로 올렸고, 퀘스트 진행 버그 때문에 추가 플레이테스트와 프롬프트가 꽤 필요했다(약 15분 분량 스토리). — [simonwillison.net](https://simonwillison.net/2026/Oct/28/vibe-game-development/)
- Battle Drones(RTS): 7월 Claude Fable 5로 2D 버전 → Opus 5.5에 "Make it a LOT more fun", 이어서 "Port this game to three.js". 현재 2~4인 멀티플레이(vibe coded WebSockets 릴레이 서버), 리플레이, 맵 7개, 랜덤 맵 생성기, mutator, LLM끼리 대전하는 모드(5초 진행 후 일시정지)가 있다. — [simonwillison.net](https://simonwillison.net/2026/Oct/28/vibe-game-development/)
- Quarter Sun Cove(농장 시뮬): 브레인스토밍 세션 → `SPEC.md` 작성 → "Opus 5.5 Ultracode가 수백만 토큰과 거의 이틀을 써서" 구현. "surprise and delight the user frequently"라는 지시로 이스터에그가 다수 생겼다. 본인은 "메커니즘은 아직 확신이 없다"고 평가. — [simonwillison.net](https://simonwillison.net/2026/Oct/28/vibe-game-development/)
- 투입 시간: 어느 프로젝트도 본인 작업 4시간을 넘지 않았다(에이전트 단독 실행 시간은 별도). 권장 순서는 "chatgpt.com/claude.ai에서 `Build a mobile-friendly three.js game where...`로 시작 → PoC를 넘기면 Codex나 Claude Code로 전환". — [simonwillison.net](https://simonwillison.net/2026/Oct/28/vibe-game-development/)
- 스스로 둔 선: 전통적인 게임잼/대회에는 내지 않겠다고 했고, 댓글에서 "나쁜 게임을 Steam에 올리지 말라, Reddit에 slop을 뿌리지 말라"고 썼다. — [HN 50273753](https://news.ycombinator.com/item?id=50273753)

**(c) Sandro Maglione – Inkline Town(3D 타운 빌더), Spirit Call(3D 탑다운 슈터) [1차]**
- "코드를 한 줄도 쓰지 않았고 읽지도 않았다." 작업 환경은 채팅, 플레이테스트 링크, 3D 모델 미리보기 웹페이지뿐이었다. 그래도 "몇 주간 그 어느 때보다 힘들고 강도 높았다"고 한다. — [sandromaglione.com](https://www.sandromaglione.com/articles/indie-game-development-with-ai)
- 핵심 원칙: "게임을 고르는 것이 곧 병목을 고르는 것. AI가 못 하는 파이프라인 단계는 전부 당신의 풀타임 업무가 된다." — [sandromaglione.com](https://www.sandromaglione.com/articles/indie-game-development-with-ai)
- 실패 사례: Genshin풍 애니메 캐릭터를 에이전트로 3D화하려고 이틀간 여러 방법(레퍼런스 시트, 기성 모델, 스튜디오식 파이프라인)을 시도했지만 품질이 나쁘고 재현되지 않았다. "단순한 stylized 모델은 잘 되고, 디테일한 애니메 캐릭터는 매번 실패." 그래서 게임이 아니라 **스타일을 바꿨다**. — [sandromaglione.com](https://www.sandromaglione.com/articles/indie-game-development-with-ai)
- 애셋 파이프라인(캐릭터당 약 20분): ChatGPT로 2D 디자인 → ChatGPT로 low-poly 버전 → ChatGPT로 3D 모델링용 뷰별 분해도 → **Blender MCP**로 3D 모델링. 스피릿 10종을 손으로 만들면 약 한 달로 추정했고, Spirit Call 전체는 3주가 걸렸다. — [sandromaglione.com](https://www.sandromaglione.com/articles/indie-game-development-with-ai)
- 검증 체계: ECS 아키텍처(시스템끼리 서로 호출하지 않고, 읽고 쓰는 컴포넌트를 선언) 위에 타입 체크, headless 테스트·시뮬레이션(수천 프레임), 반복 실수를 잡는 lint("같은 게 두 번 깨지면 lint를 요청"), 버그마다 테스트 추가, 플레이 세션 기록, 디버그 세션을 쌓았다. 본인이 만든 Ritmo(본문에 0.9.0 언급)에 이 체크가 내장돼 있지만 "원칙은 어떤 엔진에서도 통한다"고 한다. — [sandromaglione.com](https://www.sandromaglione.com/articles/indie-game-development-with-ai)
- 일정: Inkline Town은 X에서 본 스타일 레퍼런스 영상을 재현하는 데 5분, 타운 시뮬 코어까지 약 20분, 플레이 가능한 상태까지 2일, 이후 콘텐츠·재미·밸런스에 6일. 커밋의 3/4이 처음 이틀 이후에 나왔다. — [sandromaglione.com](https://www.sandromaglione.com/articles/indie-game-development-with-ai)
- 플레이테스트 방식: 약 45분간 플레이어로서 플레이하고, 지배 전략·경제를 깨는 exploit·막힌 순간·빠진 메커니즘만 보고한다. 숫자는 한 번도 직접 건드리지 않았다. — [sandromaglione.com](https://www.sandromaglione.com/articles/indie-game-development-with-ai)
- 봇의 한계: 첫날부터 봇이 경제를 플레이했지만 "어장만 지으면 빵이 무의미해지는" 밸런스 붕괴를 하나도 잡지 못했다. 에이전트에게 **경제 수학 모델**을 테스트로 작성하게 하자 깨진 규칙 12개가 드러났고, 원장 작성부터 수정까지 1시간이 안 걸렸다. — [sandromaglione.com](https://www.sandromaglione.com/articles/indie-game-development-with-ai)

**(d) 그 외 1차 사례 (스택이 명시된 것만)**
- catcopter(웹 멀티플레이): Opus 5.5(오브젝트/리깅/모션), 막힌 요소는 Tripo3d, 최적화(CPU/네트워킹)는 Fable. 백엔드 Node.js + WebSockets + Rapier 물리, 프런트는 주로 three.js. 반복 작업은 약 1주였는데, 이전 프로젝트(flat.social)의 머티리얼·셰이더·조명 세팅을 재사용했다. 애셋은 전부 생성물이며 "고양이 얼굴이 가장 어려웠다". — [HN 50305320](https://news.ycombinator.com/item?id=50305320)
- Outpost Racer(PS1풍 레이싱): "chatgpt codex"로 4일. three.js, 물리는 Rapier 3D compat 빌드, Phaser/PixiJS 같은 엔진은 쓰지 않음. 먼저 PSX풍 레벨 에디터를 만들고 거기서 게임으로 키웠다. 모르는 큰 시스템은 "기존 설계 레퍼런스를 찾게 한 뒤 조사 → 구현" 순서로 시켰다. 상대 AI는 vibecoded 자작이라 약하며 전용 라이브러리를 쓸 걸 그랬다고 한다. — [HN 50589184](https://news.ycombinator.com/item?id=50589184)
- 2D 픽셀 게임 6시간: Claude Code + Opus 5.5만 사용, 외부 라이브러리 없는 plain JS/HTML. 첫 스테이지에만 Matt Pocock의 `/wayfinder` skill을 썼고, ChatGPT 음성 받아쓰기로 원하는 스테이지를 말로 설명해 넣었다. 첫 스테이지는 30분 thinking 후 완성, 이후 스테이지는 "보통 95%를 one-shot". 계기는 Sprite Fusion의 Opus 5.5 픽셀아트 글. — [HN 50326721](https://news.ycombinator.com/item?id=50326721)
- Uncracked City(LLM 용의자 심문 추리 게임): 1인 창업자, "AI를 집중적으로 쓴 한 달 작업". 케이스는 파이프라인으로 생성한다(본인이 아이디어·도시 선택 → Claude와 피치 개발 → 본인 승인 → 엔진이 케이스 생성 → **여러 모델이 탐정 역할로 플레이해 풀 수 있는지 검증**). 용의자는 자기 타임라인만 알고, 서버 측 harness가 스토리 이탈과 조기 자백을 막는다. 응답은 AWS Lambda에서 Haiku가 1~2초에 처리. — [HN 50358352](https://news.ycombinator.com/item?id=50358352)
- terminactory(터미널 팩토리 게임): Rust + ratatui, "5.5 claude 모델들"과 베이스를 만들었다고 밝힘. Claude Code hooks로 에이전트 응답을 게임 안 "telegram"으로 받는 기능이 있다. — [HN 50497132](https://news.ycombinator.com/item?id=50497132)
- The Last Complication: 작성자 댓글은 "Fable 5.2 creation" 한 줄뿐이다. — [HN 50511718](https://news.ycombinator.com/item?id=50511718)
- Baron(WebGL 복엽기 비행): dai.studio의 "design"(타입이 붙은 요소들로 게임의 필러·세부를 기술한 다이어그램)을 에이전트에 `Build https://dai.studio/ted/ex-baron/raw`로 넘겨 생성했다는 설명. 소스는 BSD 2-Clause로 공개. — [HN 댓글 50517636](https://news.ycombinator.com/item?id=50517636)
- WASD Engine: Godot 4.7 런타임(빌드·플레이테스트), Blender, GIMP, 이미지 생성, ElevenLabs를 묶은 오픈소스 MCP 서버 겸 데스크톱 앱. "Claude가 전부 코드로만 만들어서 AI 게임이 각지고 로봇 같은 소리가 난다"는 문제의식. 웹/Windows/macOS로 내보낸다. — [HN 댓글 50578509](https://news.ycombinator.com/item?id=50578509)
- Past Visiting Hours(1v3 비대칭 멀티 호러, Steam 출시 예정): Godot + Blender + Qwen3 TTS, "Deepseek Flash w/ Pi"를 많이 사용. 몇 달째 작업 중이며 빠른 프로토타이핑으로 "무엇이 재미있는지" 찾는 것이 핵심이었다고 한다. — [HN 댓글 50430795](https://news.ycombinator.com/item?id=50430795)
- 무명의 FPS(개발자 mrdootdoot): 게임 개발 경험 0, Opus 4.8 때 시작해 약 반년. "첫 모델과 레벨은 직접 만든 것이 핵심"이었고 지금은 주 1레벨 속도. 본인이 테스트한 뒤 자동 업데이트되는 베타 테스터에게 배포하고 익명 피드백을 받는다. 총 투입 약 $5k. 엔진은 밝히지 않았다. — [HN 댓글 50446267](https://news.ycombinator.com/item?id=50446267), [50448112](https://news.ycombinator.com/item?id=50448112)
- 자작 Rust 엔진(soniczentropy): 직접 고른 crate 목록을 Kimi와 계획하고 Deepseek Flash가 "저녁 두어 번"에 구현. 2주 차에 고정소수점 결정론적 물리, 네트워킹 + 클라이언트 예측 + 결정론 테스트 스위트, 오디오 파이프라인을 갖췄다고 주장. "기성 엔진은 이제 인디에게 함정"이라는 의견. — [HN 댓글 50527800](https://news.ycombinator.com/item?id=50527800)
- Rally Rama(iOS/Android 랠리 타임트라이얼): "게임 개발 경험 0, Claude로 여기까지 왔다"는 한 줄 소개. 스택 상세 없음. — [HN 댓글 50421477](https://news.ycombinator.com/item?id=50421477)
- Epoptes(ramigb): Claude, Codex, Pi, Antigravity를 장시간(최장 20시간 이상) 자율 실행하면서 모니터링·조향하는 오픈소스 도구. 게임 제작에 쓰려고 만들었다고 한다. — [HN 댓글 50419530](https://news.ycombinator.com/item?id=50419530)

### Inferences
- 기간 내 HN에서 화제가 된 "AI 게임"은 대부분 **단기(수 시간~수 주) 브라우저 게임**이다. 상용 엔진으로 Steam 출시까지 간 사례는 상위 글에 없고 댓글에서만 보인다(Past Visiting Hours는 출시 전).
- 검증을 에이전트에게 넘기는 패턴이 세 사례에서 독립적으로 나타난다: headless 브라우저 봇 + 스크린샷 검사(Lex), headless 시뮬레이션 + 경제 수학 모델(Sandro), 여러 모델이 플레이어 역할로 풀이 가능성 검증(Uncracked City).
- "모델 한 번에 one-shot"으로 소개된 사례도 실제로는 기존 코드베이스·템플릿·이전 프로젝트 자산 위에서 시작했다(Lex는 6월 버전과 템플릿, catcopter는 flat.social 자산, Battle Drones는 7월 2D 버전).

### Gaps
- Reddit(r/aigamedev, r/gamedev, r/godot, r/ClaudeAI 등 13개 서브레딧)의 기간 내 상위 글은 확인하지 못했다. 사유는 위 접근 경로 결과 참조.
- Sandro Maglione 글의 최초 게시일은 확인하지 못했다(본문에 "9 Nov 2026 개정"만 있음, HN 제출은 2026-11-09). 글 일부(약 2,100자)는 읽지 못했다.
- Type Fighter 2, Ghanaian street games는 댓글에서 "slop" 의심을 받았지만 제작자가 AI 사용 여부나 도구를 밝히지 않았다.
- Saltline 프롬프트는 제3자(simonw)가 X 게시물을 인용해 전한 것이며 전체 세션은 공개되지 않았다. — [HN 50444850](https://news.ycombinator.com/item?id=50444850)

## 2. 링크된 게임의 검증 가능한 반응 (플레이어, 판매, 리뷰)

### Takeaway
**기간 내 HN 글에서 판매량, 플레이어 수, Steam 리뷰 수 같은 상업적 지표를 제시한 AI 게임은 하나도 찾지 못했다.** 검증 가능한 수치는 HN 점수, GitHub 스타, 제작 비용뿐이다.

### Cited Findings
- Aiden's Revenge: HN 506점/댓글 456. 가족용 무료 웹 게임이며 판매·플레이어 수치는 없다. 제작 비용은 API 가격 기준 Claude 약 $300 상당. — [HN 50433659](https://news.ycombinator.com/item?id=50433659), [게임 링크가 있는 원문](https://notesbylex.com/fable-5-2-one-shotted-my-nephews-dream-game)
- Battle Drones: Apache 2.0 공개. 공개 다음 날 제3자가 스팀펑크 테마 포크 Panache를 냈다. GitHub API 조회(2026-11-22) 기준 `simonw/battledrones` 스타 69·포크 13, `menufactory43/panache` 스타 7·포크 2. — [simonwillison.net](https://simonwillison.net/2026/Oct/28/vibe-game-development/), [GitHub simonw/battledrones](https://github.com/simonw/battledrones), [GitHub panache](https://github.com/menufactory43/panache/)
- Baron: HN 232점/댓글 68. `dai-studio/ex-baron` 스타 15·포크 2(2026-11-22 조회). 플레이 https://baron.by.dai.studio/ — [HN 50510296](https://news.ycombinator.com/item?id=50510296), [GitHub](https://github.com/dai-studio/ex-baron)
- Uncracked City: Android 무료, iOS 앱스토어 등록, 브라우저 버전(https://uncracked.city/play) 공개, 6개 언어. 추론 비용은 본인 부담으로 "연간 수천(a few thousand a year)"이라고 했고 통화는 밝히지 않았다. 유료 기능은 도달·리텐션을 본 뒤로 미룸. 플레이어 수는 공개하지 않았다. — [HN 50358352](https://news.ycombinator.com/item?id=50358352)
- Fable52.games: HN 프런트 페이지 트래픽으로 Cloudflare Worker 무료 티어 한도를 넘겨 다운됐다가 복구. 방문자 수는 없다. 운영자는 중국의 1인 개발자. — [HN 50469007](https://news.ycombinator.com/item?id=50469007)
- Past Visiting Hours: Steam `appdetails` 조회(2026-11-22) 결과 `coming_soon: true`, 출시 예정 "Q4 2026", 개발사 "Squabblin' Goblins". 미출시라 리뷰·판매 수치가 없다. 제작자는 출시가가 약 $5일 것이라고 했다. — [Steam](https://store.steampowered.com/app/1440860/Past_Visiting_Hours/), [HN 댓글 50430795](https://news.ycombinator.com/item?id=50430795)
- WASD Engine: HN 5점/댓글 1, GitHub 스타 10(2026-11-22 조회). 반응은 미미하다. — [HN 50578508](https://news.ycombinator.com/item?id=50578508), [GitHub](https://github.com/WASDEngine/WASD-Engine)
- catcopter(https://catcopter.com) 85점, Outpost Racer(https://outpostracer.com) 27점, The Last Complication(https://lastcomplication.com/) 89점, terminactory(https://gitlab.com/snipedbywifi/terminactory) 174점: 모두 무료이고 HN 점수 외의 지표는 제시되지 않았다. — [HN 50305320](https://news.ycombinator.com/item?id=50305320), [HN 50589184](https://news.ycombinator.com/item?id=50589184), [HN 50511718](https://news.ycombinator.com/item?id=50511718), [HN 50497132](https://news.ycombinator.com/item?id=50497132)
- 플랫폼 측 신호: itch.io가 생성형 AI 공개 여부 필터를 사이트의 더 많은 위치로 확대한다는 글(19점/댓글 20, 2026-11-03)과, itch.io가 업로드 급증에 대응해 "테라바이트" 규모의 AI slop을 삭제했다는 Kotaku 기사 제출(13점, 2026-11-03)이 있었다. 기사 본문은 직접 읽지 않았고 제목만 확인했다. — [HN 50350730](https://news.ycombinator.com/item?id=50350730), [HN 50356704](https://news.ycombinator.com/item?id=50356704)

### Inferences
- 이 기간 HN에서 AI 게임의 "성공"은 판매가 아니라 주목도(점수, 포크)로만 측정된다. 수익화 근거를 찾는다면 이 노트가 아닌 다른 출처가 필요하다.
- 무료 웹 배포(Cloudflare Pages, GitHub Pages, 자체 도메인)가 기본값이고, Steam은 예정 단계 사례 하나뿐이다.

### Gaps
- 어떤 게임도 DAU, 플레이 횟수, 위시리스트 수를 공개하지 않았다. 제작자에게 직접 묻지 않는 한 확인할 방법이 없었다.
- HN에 "IT THINKS! – Build Your Own GPU"(Steam, 2026-11-19 출시, $11.99, 13점)가 올라왔지만 AI 사용 여부를 제작자가 밝히지 않아 AI 게임 사례로 넣지 않았다. — [HN 50565099](https://news.ycombinator.com/item?id=50565099)
- Steam `appreviews` 엔드포인트는 두 앱 모두 빈 응답이어서 리뷰 수를 확인하지 못했다.

## 3. 상위 댓글이 말하는 것: 통하는 것과 실패하는 것, 칭찬과 slop 판정

### Takeaway
HN 댓글의 다수는 회의적이거나 적대적이다. 칭찬은 "개인적 맥락이 있는 게임", "사람이 직접 한 부분이 보이는 게임", "빠른 프로토타이핑과 검증"에 몰리고, 비판은 "일관성 없는 애니메이션과 AI 티 나는 애셋", "AI가 쓴 README·글", "프롬프트 몇 줄짜리 저노력 결과물", "서류상으로만 재미있는 기능 추가"에 몰린다.

### Cited Findings

**통한다고 보고된 것**
- [1차] 아이가 직접 그린 캐릭터와 보스를 재료로 쓴 것. 작성자는 비판에 "모든 캐릭터와 보스는 Aiden이 직접 그렸고 게임은 그 그림에서 만들어졌다"고 답했다. — [HN 50433659](https://news.ycombinator.com/item?id=50433659)
- [1차] 게임 필(feel)을 초반에 잡는 능력: catcopter 제작자는 "Opus 5.5가 처음부터 게임플레이 감각을 맞추는 데 놀랍도록 좋았다"고 했다. — [HN 50305320](https://news.ycombinator.com/item?id=50305320)
- [1차] 턴제 전략·보드게임 이식은 단일 HTML 파일 빌드에 잘 맞는다는 관찰(3D FPS 데모와 달리 Pointer Lock이 필요 없음). 예: https://civilwarstrategy.com/ , https://harmonies.eamag.me/ — [HN 50469007](https://news.ycombinator.com/item?id=50469007)
- [1차] 기존 게임 엔진·서버 작업의 가속: "게임 엔진에서 주당 수십 개 티켓을 처리하고, 몇 년간 구상만 하던 아키텍처를 구현 중"(2001zhaozhao). — [HN 50273753](https://news.ycombinator.com/item?id=50273753)
- [1차] 모든 작업과 결정을 `.md`로 문서화해 서로 참조시키면 Claude가 과거 결정과 충돌하는 요청을 스스로 잡아낸다(게임 한정 아님, Marco012). 에이전트가 쓴 코드베이스의 70% 이상을 테스트·벤치마크·실험으로 채운다(mpd). — [HN 50444380](https://news.ycombinator.com/item?id=50444380)
- [커뮤니티] "게임이 재미있기만 하면 vibe coded든 손코딩이든 상관없다. 나는 HN에서 소수파일 것"(ajjenkins). — [HN 50432523](https://news.ycombinator.com/item?id=50432523)

**실패한다고 보고된 것**
- [커뮤니티] 스프라이트 애니메이션 일관성: 주인공 걷기 사이클 8프레임이 서로 일관되지 않는다는 구체적 지적(vunderba). ControlNet 등으로 "명목상 수용 가능한" 사이클은 만들 수 있지만 수작업이 여전히 필요하다고 했다. — [HN 50433659](https://news.ycombinator.com/item?id=50433659)
- [1차] 에이전트가 자기가 Blender로 만든 벽 타일 모델의 텍스처 규격을 몇 시간 동안 정확히 답하지 못했다(Godot PoC, Opus 5.5, joshkojoras). — [HN 댓글 50438214](https://news.ycombinator.com/item?id=50438214)
- [1차] PBR 애셋 팩 밖의 특정 비주얼 스타일에 도달하는 것이 현재 에이전트 게임 개발의 어려운 점(LarsDu88). — [HN 댓글 50446461](https://news.ycombinator.com/item?id=50446461)
- [1차] 코드는 Claude로 많이 되지만 그래픽(로컬 모델로 드로잉, 3D 모델, 리깅, 스프라이트)을 붙이는 일은 여전히 "수작업"이 많다(snicky). — [HN 댓글 50390934](https://news.ycombinator.com/item?id=50390934)
- [1차] AAA급 디스플레이스먼트 효과 하나에 Claude max 계정 토큰 한 달치와 수백 프롬프트를 썼지만 원하는 결과를 얻지 못했다(holoduke, 코드를 보지 않고 3D 엔진을 vibe coding하는 실험). — [HN 50573681](https://news.ycombinator.com/item?id=50573681)
- [1차] Unreal로 게임을 만드는 개발자(vblanco): 자신과 주변 개발자 모두 AI를 많이 쓰지만 **공식 Unreal Engine MCP는 "거의 쓸모없어서" 아무도 쓰지 않고 각자 자체 MCP를 돌린다**. 애셋이 텍스트 형식이 아니어서 에이전트의 grep이 통하지 않는 것이 문제라고 했다. — [HN 50573681](https://news.ycombinator.com/item?id=50573681)
- [커뮤니티] 프로그래밍을 모르는 지인이 한 달째 vibe coding 중이지만 게임에 근접한 것도 없다는 반례(david2ndaccount). 작성자 simonw는 "아마 Opus 5.5를 안 쓰는 것 같다"고 답했다. — [HN 50273753](https://news.ycombinator.com/item?id=50273753)
- [커뮤니티] Opus 5.5로 게임 디자인 아이디어를 탐색하려 했지만 자꾸 결정을 내리도록 몰아가고 지시를 따르지 않아 쓸모없었다(jakubmazanec). — [HN 50273753](https://news.ycombinator.com/item?id=50273753)
- [커뮤니티] "make it fun"으로 추가된 것은 오프너, 콜다운 파워, 목표물, 진행 시스템 같은 기능 목록인데, "서류상의 재미이지 실제 재미의 체감과는 다르다"(xyzsparetimexyz). 실제로 플레이해 보니 "재미없었다"는 댓글도 있다(arm32). — [HN 댓글 50283118](https://news.ycombinator.com/item?id=50283118), [HN 50273753](https://news.ycombinator.com/item?id=50273753)
- [1차] 봇은 밸런스 감각이 없다: 다른 전략을 무의미하게 만드는 지배 전략도 봇에게는 그냥 하나의 전략으로 보인다. — [sandromaglione.com](https://www.sandromaglione.com/articles/indie-game-development-with-ai)
- [1차] LLM이 쓴 스토리는 평면적이라는 지적에 Uncracked City 제작자가 동의했고, 인력을 쓸 수 있게 되면 가장 먼저 아트워크와 스토리텔링을 맡기겠다고 했다. AI 번역(이탈리아어)도 품질 지적을 받았다. — [HN 50358352](https://news.ycombinator.com/item?id=50358352)

**slop으로 판정되는 신호**
- [커뮤니티] AI가 쓴 README: "프로젝트의 첫인상인데 Claudeism으로 가득하면 신경 안 쓴다는 뜻이고 전체가 slopware라는 신호"(brian-armstrong). 제작자는 README를 직접 다시 썼고, "코드는 보이지 않지만 lore는 보인다"며 게임 내 lore도 직접 다시 쓰겠다고 했다. — [HN 50497132](https://news.ycombinator.com/item?id=50497132)
- [커뮤니티] AI가 쓴 기술 블로그: three.js 5위 커미터가 400시간 작업을 AI로 정리한 글에도 "네가 쓰지 않았으면 안 읽는다"는 반응이 상위에 올랐다. — [HN 50523291](https://news.ycombinator.com/item?id=50523291)
- [커뮤니티] UI의 AI 흔적: "그림자 달린 떠 있는 칩에 숫자를 채운 UI는 뻔한 AI 디자인"(Inkline Town에 대한 지적). 아트 스타일을 트윗에서 가져왔다는 점도 "taste를 어디서 발휘했나"라는 비판을 받았다. — [HN 50432523](https://news.ycombinator.com/item?id=50432523)
- [커뮤니티] 저노력 대량 공개: "한 번에 여러 게임을 내지 말고 게임 하나하나에 훨씬 더 공을 들여라"(Ghanaian street games). "프롬프트 몇 줄로 나온 gameslop에 왜 내 시간을 쓰나, 차라리 내 취향대로 직접 생성하겠다"(Fable52.games). — [HN 50414117](https://news.ycombinator.com/item?id=50414117), [HN 50469007](https://news.ycombinator.com/item?id=50469007)
- [커뮤니티] Saltline FPS: 답글이 가장 많이 달린 댓글이 "끔찍한 게임"이었고, D 키가 동작하지 않거나 Firefox에서 실행되지 않는다는 보고가 있었다. — [HN 50444850](https://news.ycombinator.com/item?id=50444850)
- [커뮤니티] AI 사용 자체를 거부하는 층: "AI를 썼으면 인디든 아니든 플레이하지 않는다"(free_bip). "예술은 AI로 만들지 말아야 할 영역"(scuttlebutt98). itch.io의 AI 공개 표시는 "등에 '차 주세요' 스티커를 붙이는 것"(vegnus). — [HN 50432523](https://news.ycombinator.com/item?id=50432523), [HN 50350730](https://news.ycombinator.com/item?id=50350730)
- [커뮤니티] 게임 노조의 생성형 AI 매니페스토 스레드에서는 "반대의 대부분은 노동자가 아니라 플레이어에게서 나온다"는 댓글에 답글이 가장 많이 달렸다(29개). — [HN 50519043](https://news.ycombinator.com/item?id=50519043)

**제작 측 스스로의 평가**
- [1차] Fable52.games 운영자: "기술 스택과 기본 메커니즘은 놀랍게 좋지만, 진짜 game feel, 페이싱, 일관된 아트 디렉션은 여전히 사람의 취향을 요구한다. 브라우저 게임 개발자를 대체한다기보다 엔진 세팅 단계를 건너뛰는 느낌." — [HN 50469007](https://news.ycombinator.com/item?id=50469007)
- [1차] Godot에서 Claude로 뮤직비디오를 만들었지만 "내 작품인가"라는 위화감 때문에 폐기했고, 이후 AI는 도구 제작 같은 저수준 작업에만 쓰기로 했다(_spduchamp). — [HN 댓글 50575571](https://news.ycombinator.com/item?id=50575571)

**정책 변화 (워크플로에 직접 영향)**
- 기간 내 Anthropic이 Claude의 게임 클론·리버스 엔지니어링 요청을 막기 시작했다는 글이 여러 건 올라왔다(196점/124, 126점/144 등). 댓글에는 "클라이언트 측 시스템 프롬프트 수정이라 우회 가능하다"는 주장(미검증)과, "가드레일 추가 전 Opus 5.5 버전이 더 재미있었고 Fable 5.2는 원작과 같게 해 달라는 프롬프트에도 메커니즘을 바꿨다"는 사용자 보고가 있다. — [HN 50320255](https://news.ycombinator.com/item?id=50320255), [HN 50304358](https://news.ycombinator.com/item?id=50304358), [HN 50433659](https://news.ycombinator.com/item?id=50433659)

### Inferences
- 사람이 직접 한 부분(그림, lore, README, 첫 모델과 레벨)을 눈에 보이는 곳에 두는 것이 HN에서 slop 판정을 피하는 가장 일관된 요인으로 보인다. terminactory 제작자가 비판을 받고 README와 lore를 직접 다시 쓴 것이 그 사례다.
- 실패 보고는 코드가 아니라 애셋 쪽(애니메이션 일관성, 특정 화풍, 리깅, 텍스처 규격, 고급 셰이더)에 몰려 있다. Sandro의 "AI가 반복 생산할 수 있는 스타일을 먼저 고르라"는 조언과 방향이 같다.
- 기존 유명 게임을 본뜬 프로젝트는 이 기간에 모델 측 제한의 영향을 받을 수 있다. 다만 제한의 실제 범위는 댓글 주장만으로는 확정할 수 없다.

### Gaps
- HN 댓글 개별 점수는 API가 제공하지 않아 "상위 댓글"을 답글 수로 대신 판단했다. 실제 화면 순서와 다를 수 있다.
- Reddit 쪽 여론(특히 r/gamedev, r/IndieDev의 반AI 정서와 r/aigamedev의 실무 팁)은 확인하지 못했다. HN에 제출된 Reddit 링크 2건(`r/Games`의 "Thoughts on AI in game development (from the trenches)", 2026-10-22, HN 2점 / `r/aigamedev`의 Fable 5.2 게임 글, 2026-11-12, HN 1점)은 제목만 확인했고 본문은 읽지 못했다. — [HN 50201604](https://news.ycombinator.com/item?id=50201604), [HN 50465997](https://news.ycombinator.com/item?id=50465997)
- Anthropic 정책의 공식 문구는 직접 확인하지 않았다(HN 제목과 댓글만 확인).

## 4. 실제로 무언가를 낸 사람들이 가장 많이 언급한 엔진·에이전트·애셋 도구

### Takeaway
기간 내 HN 1차 사례 기준으로 가장 자주 나온 조합은 **Claude 계열 모델(Opus 5.5, Fable 5.2) + Claude Code + three.js/plain HTML·JS**이고, 애셋은 이미지에 ChatGPT(Images 2.5), 오디오에 ElevenLabs, 3D에 "모델이 코드로 직접 생성"하거나 Blender(MCP)를 쓰는 패턴이다. Godot는 Steam을 목표로 하는 사례에서 나오고, Unity는 1차 사례에서 한 번도 나오지 않았다.

### Cited Findings

**언급 횟수 집계 (이 노트에 인용한 1차 사례 기준, 직접 센 값)**

| 분류 | 도구 | 언급한 1차 사례 |
|---|---|---|
| 모델/에이전트 | Claude Opus 5.5 | Simon Willison 4종, catcopter, 6시간 픽셀 게임, terminactory("5.5 claude 모델들") |
| | Claude Fable 5.2 | Aiden's Revenge, The Last Complication, Saltline, Fable52.games 수록작, civilwarstrategy.com |
| | Claude Code | Aiden's Revenge, 6시간 픽셀 게임, terminactory(hooks), Simon Willison(PoC 이후 단계) |
| | ChatGPT Codex | Outpost Racer |
| | Deepseek Flash | Past Visiting Hours(Pi와 함께), soniczentropy의 Rust 엔진 |
| | Kimi | soniczentropy(계획 단계) |
| | GLM 5.3 Flash(셀프 호스팅) | rimpark.gg 기능 추가 |
| | Haiku | Uncracked City(런타임 NPC 응답) |
| 엔진/런타임 | three.js | Simon Willison 4종, catcopter, Outpost Racer |
| | plain HTML/JS(단일 파일 포함) | 6시간 픽셀 게임, Fable52.games 수록작 |
| | Godot | Past Visiting Hours, WASD Engine(4.7), joshkojoras의 PoC |
| | Rust(ratatui 또는 자작 엔진) | terminactory, soniczentropy |
| | Unreal Engine | vblanco(자체 MCP 사용, 공식 MCP는 미사용) |
| | Unity | 1차 사례 없음 |
| 물리/네트워크 | Rapier | catcopter, Outpost Racer |
| | WebSockets | Battle Drones, catcopter |
| 2D 이미지 | OpenAI ChatGPT Images 2.5 / ChatGPT | Aiden's Revenge(약 500장), Sandro Maglione(2D 디자인, low-poly 시안, 뷰 분해) |
| 3D | 모델이 코드로 직접 생성 | Simon Willison(Battle Drones 모델 브라우저), catcopter(Opus 5.5로 오브젝트·리깅·모션) |
| | Blender / Blender MCP | Sandro Maglione, Past Visiting Hours, WASD Engine |
| | Tripo3d | catcopter(막힌 요소 일부) |
| | Meshy | 기간 내 게임 제작 맥락의 언급을 찾지 못함 |
| 오디오 | ElevenLabs | Aiden's Revenge(음악 11곡, SFX 약 100개, 대사 90개), WASD Engine |
| | Qwen3 TTS | Past Visiting Hours |
| | 모델이 Web Audio로 직접 합성 | Fable52.games 운영자의 소스 관찰, Simon Willison(음악 생성) |
| 배포 | Cloudflare Pages / GitHub Pages | Aiden's Revenge, Simon Willison |
| | Steam(예정) | Past Visiting Hours |
| | Android / iOS | Uncracked City, Rally Rama |

출처: [notesbylex.com](https://notesbylex.com/fable-5-2-one-shotted-my-nephews-dream-game), [simonwillison.net](https://simonwillison.net/2026/Oct/28/vibe-game-development/), [sandromaglione.com](https://www.sandromaglione.com/articles/indie-game-development-with-ai), [HN 50305320](https://news.ycombinator.com/item?id=50305320), [HN 50589184](https://news.ycombinator.com/item?id=50589184), [HN 50326721](https://news.ycombinator.com/item?id=50326721), [HN 50497132](https://news.ycombinator.com/item?id=50497132), [HN 50358352](https://news.ycombinator.com/item?id=50358352), [HN 50469007](https://news.ycombinator.com/item?id=50469007), [HN 50511718](https://news.ycombinator.com/item?id=50511718), [HN 댓글 50430795](https://news.ycombinator.com/item?id=50430795), [HN 댓글 50527800](https://news.ycombinator.com/item?id=50527800), [HN 댓글 50419052](https://news.ycombinator.com/item?id=50419052), [HN 댓글 50578509](https://news.ycombinator.com/item?id=50578509), [HN 50573681](https://news.ycombinator.com/item?id=50573681)

**도구 선택에 대한 발언**
- [1차] "Frontier 모델은 three.js와 Phaser 같은 라이브러리를 이미 안다. 모바일 웹 게임이 네이티브 경험과 구분되지 않는다(내가 만들려는 종류의 게임에 한해)." — [simonwillison.net](https://simonwillison.net/2026/Oct/28/vibe-game-development/)
- [커뮤니티] "three.js 없이도 LLM이 잘 쓴다. 라이브러리가 없으면 프로젝트에 맞는 구조를 자유롭게 쓴다"(greggman65, 자신의 생성 도시 데모 링크 제시). 반대로 "glTF 임포터, SSR, UV 언랩, BRDF를 다시 쓰면 토큰이 많이 든다"(bhouston)는 반론이 있다. — [HN 50523291](https://news.ycombinator.com/item?id=50523291)
- [1차] Godot를 고른 이유: Unity와 Unreal을 조금 써 봤지만 Godot의 철학이 좋고 엔진을 어디까지 밀 수 있는지 보고 싶었다(Past Visiting Hours). — [HN 댓글 50430795](https://news.ycombinator.com/item?id=50430795)
- [1차] 모델 비교: senko의 개인 벤치마크(Warcraft 클론, Minecraft 클론, 복엽기 도그파이트)에서 Fable 5.2는 그래픽은 "오히려 나빠 보이지만" 세 게임 모두에 깊이를 더했다(탐험 목표에 맞춰 비행선 유닛 추가 등). 본인이 과학적 테스트가 아니라고 밝혔다. — [HN 댓글 50433004](https://news.ycombinator.com/item?id=50433004)
- [1차] 같은 DX-Ball 프롬프트로 Opus 5.5와 Fable 5.2를 비교한 사용자는 "Fable이 분명히 나은 부분이 있지만 주관적으로 Opus 5.5 버전이 더 재미있다"고 했다. — [HN 50433659](https://news.ycombinator.com/item?id=50433659)
- [1차] 비음성 사운드(음악, 효과음)와 모션 이해(캐릭터 움직임)는 frontier 모델 회사들도 아직 잘 못한다는 인상(lhk931122, 여러 도구를 시험 중인 단계). — [HN 스레드 50417407](https://news.ycombinator.com/item?id=50417407)

### Inferences
- HN 표본은 웹 개발자 비중이 높아 three.js/HTML 쪽으로 기울어 있을 가능성이 크다. Godot/Unity/Unreal 실무자의 목소리는 Reddit에 더 많을 것으로 예상되지만 이번 수집으로는 확인하지 못했다.
- 3D 애셋은 "전용 생성 서비스(Meshy, Tripo)"보다 "LLM이 코드나 Blender 스크립트로 직접 만든다"는 보고가 더 많았다. Tripo3d는 보조 용도로 한 번 언급됐다.
- 로컬·저가 모델(Deepseek Flash, GLM 5.3 Flash, Kimi, Qwen3 TTS)을 쓰는 사례가 댓글 층에서 여럿 보인다. 상위 글은 전부 Claude 계열이다.

### Gaps
- Unity MCP, Unreal MCP의 구체적 제품명이나 설정은 기간 내 HN에서 찾지 못했다("Unity MCP" 스토리 검색 7건, "Unreal MCP" 1건 모두 관련 실무 글이 아니었음).
- Meshy, Tripo 검색 결과(각각 41건, 99건)는 대부분 무관한 부분 일치였고, 게임 제작 맥락의 언급은 catcopter의 Tripo3d 한 건뿐이었다.
- 집계는 이 노트에 인용한 사례를 직접 센 것으로, 통계적 표본이 아니다.

### 배경(기간 외)
- Battle Drones 최초 소개 글 "Battle Drones – a vibe coded RTS with audio-based multiplayer"는 2026-10-20 게시(기간 이틀 전)이고, 같은 URL의 HN 제출은 2026-10-20(8점/댓글 3)과 2026-10-21에 있었다. 기간 내 재제출(2026-10-22, 4점)도 있다. — [simonwillison.net](https://simonwillison.net/2026/Oct/20/battledrones/), [HN 50173389](https://news.ycombinator.com/item?id=50173389)
- Battle Drones의 첫 2D 버전은 2026년 7월 Claude Fable 5로 만들어졌다(GitHub 저장소 생성일 2026-07-17). — [simonwillison.net](https://simonwillison.net/2026/Oct/28/vibe-game-development/), [GitHub](https://github.com/simonw/battledrones)
- Aiden's Revenge의 첫 버전은 2026년 6월(Claude Code, Opus 4.8, Fable 5, AIOriented.dev 템플릿)이고 구상은 2026년 1월경이다. — [notesbylex.com](https://notesbylex.com/fable-5-2-one-shotted-my-nephews-dream-game)
- Spirit Call과 Inkline Town의 개발 자체는 2026-10-04 ~ 10-18 무렵으로 본문에 날짜가 찍혀 있다(기간 직전). 글과 HN 토론은 기간 내다. — [sandromaglione.com](https://www.sandromaglione.com/articles/indie-game-development-with-ai)
- catcopter는 이전 프로젝트 flat.social의 렌더링·최적화 자산을 재사용했다(해당 프로젝트 시점은 미확인). — [HN 50305320](https://news.ycombinator.com/item?id=50305320)
