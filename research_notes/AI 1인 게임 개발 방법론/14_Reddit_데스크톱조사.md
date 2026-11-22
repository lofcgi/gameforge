# Reddit 데스크톱 조사 — 1인 설계·AI 제작 플레이어블 게임과 제작 방법 (2026-10-22 ~ 2026-11-22)

> 조사일 2026-11-22. 사용자 데스크톱 Chrome(로그인된 Reddit 세션)의 새 창 1개를 cmux-cua로 읽기 전용 조작. 투표·댓글·가입·저장 없음.
> **품질 판단은 게시물 본문·점수·댓글 관찰에 근거하며, 게임을 직접 플레이하지 않았다.**
> 날짜 표기: `정확` = 스레드 페이지의 "this post was submitted on" 값. `≈` = 목록의 "N days ago"에서 역산(검증한 5건에서 N 또는 N+1일 전으로 나와 ±1일 오차). 점수·댓글 수는 조회 시점 값.
> URL 표기: 스레드를 실제로 연 글만 permalink를 적었다. 나머지는 접근성 트리에 링크 주소가 노출되지 않아 **permalink 미확보** — 본문은 old.reddit 검색 결과 페이지에 표시된 전문을 읽었고, 재확인용 검색 URL을 "조사 방법"에 적었다. 플레이 링크는 본문에 텍스트로 적힌 것만 기록(하이퍼링크 텍스트만 있고 주소가 안 보인 경우 "주소 미노출").
> 게시물에 등장하는 모델·도구명(Opus 5.5, Fable 5.2, Astra, Jev, GPT-6 Luna, Tripo P2 등)은 **작성자가 쓴 표기 그대로** 옮겼으며 별도 검증하지 않았다.

## 1. 기간 내 Reddit에 올라온 플레이어블·1인 설계·(거의) 전부 AI 제작 게임 중 관찰 품질이 가장 높은 것과 플레이 링크

### Takeaway
기간 내 최고 관찰 품질 후보는 **Voltane**(브라우저 RC 레이싱, r/aigamedev 1,436점)과 **Don't Touch the Dirt**(브라우저 WebGPU 협동 서바이벌), 그리고 Godot 계열의 **RUSuper 항해 시뮬(주간 연재, 무료 데모)** 이다. 이들은 모두 "웹/무료 데모로 즉시 플레이 + 본문에 스택·비용 공개" 형태이며, r/aigamedev 규칙 4가 워크플로 공개를 사실상 강제한다.

### Cited Findings

**A. 선정(플레이 가능 + 1인 + AI 제작 비중 높음 + 호평) — 모두 1차(제작자 본인 글)**

| # | 게임 / 제목 | 서브·작성자 | 날짜 | 점수 / 댓글 | 플레이 링크(본문 표기) | AI 범위(자기보고) |
|---|---|---|---|---|---|---|
| 1 | **Voltane** — "9 days ago I posted the game I built with Opus 5.5 … so I shipped 98 updates since. Here's Voltane now." | r/aigamedev · u/MacXou34 | 2026-10-26 (정확) | 1,436 (97%) / 288 | `playvoltane.com` (브라우저, 게스트 플레이) | 코드 전부 Claude Code+Opus 5.5, 3D는 gpt-image→Tripo→Blender(Claude 구동), 음향 ElevenLabs·Suno |
| 2 | **Don't Touch the Dirt** — "6 weeks, ~700 prompts, a browser game built with Claude Code [trailer]" | r/aigamedev · u/Robotron1980 | ≈2026-11-10 | 276~280 / 61 | `https://playharmony.ai/share/6ed50d48/Dont-Touch-the-Dirt` | 코드·Blender 모델·오디오 가공·트레일러 음악까지 Claude Code. 캐릭터 베이스/클립은 Mixamo, 효과음은 CC0 녹음 |
| 3 | **(제목 미표기) 항해·낚시 시뮬** — "15 weeks of making game with Claude Opus in Godot" | r/aigamedev · u/RUSuper (r/ClaudeAI에도 588점 교차게시) | 2026-11-09 (정확) | 497 (96%) / 88 | "DEMO LINK DOWNLOAD - FREE" (주소 미노출) | 코드 전부 Opus 5.5(Claude Code), 3D는 Tripo + Blender MCP, 목업 OpenAI 이미지 API, 음향 ElevenLabs. 음악은 예외("Yeah except for music") |
| 4 | **Hiraeth** — "One month building Hiraeth: a Moebius-inspired adventure game, with Opus 5.5, Astra, Tripo & Suno" | r/aigamedev · u/4nf (r/threejs 585점 교차게시). 플레어 Commercial Self Promotion | ≈2026-11-04 | 443~448 / 74 | "Play it here" (주소 미노출), Android 빌드 언급 | Opus 5.5+Astra 개발, Midjourney 레퍼런스, Tripo/Meshy/코드 생성 3D, Suno 음악 |
| 5 | **Neon Terrarium** (코지 사이버펑크 시티빌더) | r/aigamedev · u/senpai_go_away | ≈2026-11-02 | 524~530 / 104 | `https://jannstudios.itch.io/neon-terrarium` (브라우저·모바일) | "give it a shot with AI" — 건물 전부 절차 생성. 세부 도구는 본문에 없음 |
| 6 | **Ram Altman** (브라우저 스텔스 풍자) | r/aigamedev · u/cormaction | ≈2026-11-08 | 652~656 / 68 | `https://ckxlab.itch.io/ram-altman` | 코드는 Claude, **아트는 본인(3D 아티스트)** → "전부 AI"는 아님 |
| 7 | **fableflight** (Rust 오픈월드 비행 시뮬) | r/aigamedev · u/ImpactIntelligent218 | 2026-11-14 (정확) | 869 (87%) / 257 | `https://github.com/Rolandjg/fableflight` (`cargo run --release` 빌드 필요) | 1주, Claude Plus 구독 2개. Fable 5.2=렌더링·기체 모델, Opus 5.5=시스템. 지형은 Google tiles API |
| 8 | **Riposte: Frontline** (브라우저 FPS, MIT 소스 공개) | r/aigamedev · u/Inevitable_Salad_128 | ≈2026-10-26 | 261 / 42 | `https://www.playriposte.com`, 소스 `https://github.com/BenDBSS/Riposte-Frontline-Source` | Claude Code + three.js, 임포트 3D 모델 없음(전부 코드). 음악·병사 애니메이션은 MIT 제외 |
| 9 | **Waiting Room** (1인칭 호러) | r/aigamedev · u/Bill_Buffet. Commercial Self Promotion | ≈2026-10-30 | 197 / 33 | `https://tiborholtman.itch.io/waiting-room` (Win/Mac) | 자체 엔진(Metal/Vulkan)까지 Claude Code만으로. 에셋은 무료 에셋 |
| 10 | **The Last One: From Ashby** (턴제 판타지 RPG) | r/aigamedev · u/No_Calligrapher_9518 (r/vibecoding 492점). Commercial Self Promotion | ≈2026-11-19 | 387 / 58 | `https://thelastone.net` (브라우저, 게스트) | 49세 비개발자, 약 1,000시간, "AI tools"(구체 도구 미기재) |

- Voltane 제작자 진술: "Me: design, taste, testing, and saying 'no, that's not fun yet' a lot. The AI writes the code, but deciding what makes a jump feel good is still the job." (나는 설계·취향·테스트, 그리고 "아직 재미없다"는 말을 많이 한다. 코드는 AI가 쓰지만 점프가 기분 좋게 느껴지는지 정하는 건 여전히 사람 일) — [r/aigamedev, u/MacXou34](https://old.reddit.com/r/aigamedev/comments/1xgcszc/9_days_ago_i_posted_the_game_i_built_with_opus_55/)
- Voltane 댓글 평가: "One of the most polished thing I have seen so far on this sub."(이 서브에서 본 것 중 가장 완성도 높은 축), "I hate AI slop games, but I can't hate AI masterpiece games." / 비판: "after playing it was disapointing the car handling and feel is much better in the original game"(해보니 조작감은 원작이 훨씬 낫다), Re-Volt(1999)와 이름·콘셉트가 닮았다는 지적 다수 → **기존 게임 강한 오마주라는 점 주의**(리메이크/포트는 아님, 제작자도 영향 인정) — [같은 스레드](https://old.reddit.com/r/aigamedev/comments/1xgcszc/9_days_ago_i_posted_the_game_i_built_with_opus_55/)
- fableflight 댓글은 건물 파괴 물리에 대한 농담이 주류("he takes down an entire 100x100 ft concrete office building with a 1900 lbs plane", 202점)이고 9·11 연상으로 "sensitive topic" 지적(115점). 제작자: "All I asked for was to 'make the building destruction more satisfying'" — [r/aigamedev, u/ImpactIntelligent218](https://old.reddit.com/r/aigamedev/comments/1xwf9rv/im_a_huge_fan_of_microsoft_flight_sim_2024_but/)
- RUSuper 누적 비용(자기보고): "Claude Max 200$ x 4 = 800$ / Astra 100$ x 1 / ElevenLabs 11$ / TripoAI 20$ x 2 / OpenAI API credits 80$ / … Around 1100-1150$" — [r/aigamedev, u/RUSuper](https://old.reddit.com/r/aigamedev/comments/1xrknnf/15_weeks_of_making_game_with_claude_opus_in_godot/)

**B. 플레이 불가(또는 링크 없음/회수) — 주목할 쇼케이스**

- **SirKnighty의 아케이드 농사 게임** — "My game got removed from gamedev subs for using AI, so here's exactly how I made it with Claude", r/ClaudeAI, 2026-11-12(정확), **3,275점(89%) / 506댓글**. 링크는 Steam 스토어 `https://store.steampowered.com/app/5341880`(데모/출시 여부는 본문·상위 댓글에서 확인 못함). 19년차 개발자의 5주 1인 파이프라인 — [r/ClaudeAI, u/SirKnighty](https://old.reddit.com/r/ClaudeAI/comments/1xul18m/my_game_got_removed_from_gamedev_subs_for_using/)
- **Ragnarok Online × Monster Hunter풍 Godot 게임** — "No coding or gamedev background, 6 weeks with Opus 5.5 + Godot — from drawings to a playable game", r/ClaudeAI, u/Delicious-Shower8401, ≈2026-10-24, **3,116점 / 230댓글**. 작성자가 1인 개발자를 인터뷰한 **2차 전달 글**, 플레이 링크 없음 (permalink 미확보)
- **Meltbelt** (Godot+C++ 유체 시뮬 채굴 게임) — r/aigamedev, u/Professional_Job_307, ≈2026-11-21, 387~392점 / 49. 3주(주말 위주), 코드·셰이더·텍스처 전부 Opus 5.5+약간의 Fable. **플레이 링크를 본인이 삭제**: "I removed the playable link to the game out of fear that someone rips the web build." (permalink 미확보)
- **Liliput** 로우폴리 에셋 파이프라인 — u/randomforest99, ≈2026-10-29, 443~445점 / 101 (게임 미공개, 3번 질문 참조)
- **North Atlantic islands / Earth-sized planet (Unity 6)** — u/imlo2, ≈2026-11-05(368~377점) / ≈2026-11-21(294점). 기술 프로토타입, 게임 아님
- **Hostarro의 코지 콜로니 시뮬(Godot)** — ≈2026-11-13, 200~202점 / 117. 얼리 액세스 예정, 18개월. **3D 아티스트·작곡가를 고용**했으므로 "전부 AI" 아님(워크플로만 참고)
- **I Just Wanted to Fish** (Unity+Claude) — u/ForkedPush, ≈2026-10-25, 1,001~1,007점 / 186, Commercial Self Promotion, Steam 위시리스트 링크 `https://store.steampowered.com/app/5350560/I_Just_Wanted_to_Fish/` (이후 "updated my demo" 글 있으나 미확인)
- **Gambo7592의 2D 플랫포머(45레벨)** — ≈2026-11-09, 241~242점. itch 링크는 DM으로만 제공

**C. 제외·별도 표기**
- "This guy asked Fable 5.2 to 'go wild' making a game and it made a Pong clone…" (r/aigamedev, u/throwaway_user_1994, ≈2026-11-12, 1,664점 / 377, 링크 도메인 `tennis.sixfingerpunch.com`) — 제목에 "Not my game btw"라 적힌 **제3자 소개 글**이고 Pong 변주. 스레드 미개방.
- "We're a team of 8 building a GTA-inspired game with a 100 km² map of Bangkok…"(2,557점) — 8인 팀이라 제외. NFS Underground 2 브라우저 포트(606점), WoW 에셋 데이터마이닝 Slay the Spire 클론(202점) — 포트/클론이라 제외.
- AutoSprite(u/beelllllll, 891점·248점), "concept to rigged animation" 앱(u/No-Dragonfruit-675) — **툴 벤더/자기 툴 홍보**(AutoSprite는 Commercial Self Promotion 플레어, 후자는 Demo | Project | Workflow 플레어지만 자작 앱 소개).

**D. Slotbound 관련**
- 개발자 Reddit 계정은 **u/OptimaArch**. 기간 내 2차 글: "GOOD vibecoded game made $1 million+ within the FIRST WEEK" (r/aigamedev, u/dedaistgeil, ≈2026-11-21, 727~733점 / 436) — "He made more than $1 million in the first week after launch. This is no AI slop or one-prompt game. He worked on it for many months."(제3자 주장, 수치 미검증). "How a Vibe-Coded Steam Game Sold 100,000 Copies (Slotbound Breakdown)" (u/Comet7777, youtu.be 링크, ≈2026-11-17, 369~375점 / 148) (둘 다 permalink 미확보)
- OptimaArch 본인 글 "My first game just reached 100k wishlists…" (r/SoloDevelopment, 248점 / 299, "1 month ago" — **기간 경계, 날짜 미확정**)
- **배경(기간 외)** — OptimaArch 1차 글(전부 "4~6 months ago" 표기):
  - "I'm not a developer and this slot machine roguelike defense game was built almost entirely with AI" (r/aigamedev, 6 months ago, 402점 / 202): "100% of the game's code was generated with AI. I absolutely cannot code a single line at all. / Many visuals, animations, UI elements, Backgrounds, Main menu pixel arts & animations are also AI-generated / Only few assets were bought or edited manually". 이후 추가된 문구: "#Updated# 26/10/19: This post was talking about Demo at that time and for full release version there's lots of hard works and effort was in the game and lots of hand drawn human arts." (정식판에는 손그림 아트가 많이 들어갔다고 본인이 정정)
  - "I still can't code. But after 8 months, the Steam demo I built with AI is finally live!" (r/aigamedev, 4 months ago, 599점 / 137), 데모 `https://store.steampowered.com/app/4906570/Slotbound_Demo/`, itch `https://optimaarch.itch.io/slotbound`
  - r/love2d 글(4 months ago, 70점): "my first solo project in Love2D called Slotbound" → **엔진은 LÖVE(Love2D)**
  - 본문들에는 "ai coding tools"라고만 적혀 있고 **구체 모델/에이전트 이름은 본문에 없음**(댓글은 열지 못함)
  - 출처: Reddit 사이트 검색 `https://old.reddit.com/search?q=Slotbound&sort=top&t=all` 결과 페이지

### Inferences
- 기간 내 고득점 "플레이어블 + 1인 + AI" 사례는 거의 전부 **three.js/WebGPU 브라우저 게임** 아니면 **Godot** 이다. Unity·Unreal은 기술 데모/위시리스트 단계 글이 많고 즉시 플레이 링크가 드물다.
- "전부 AI"에 가장 가까운 것은 Voltane·Don't Touch the Dirt·RUSuper 게임·Riposte·Waiting Room. 다만 이들도 Mixamo, 무료 에셋, CC0 음원, 음악 예외 등 **비-AI 소재가 섞여 있다**.
- Voltane은 Re-Volt 오마주 색이 짙어 "기존 게임 리메이크 제외" 기준의 경계선에 있다.

### Gaps
- 표 2~6, 8~10번과 B·C·D 대부분은 **permalink를 확보하지 못했다**(접근성 트리에 href 미노출, 화면 밖 링크 클릭 실패). 제목·작성자·서브로 재검색 필요.
- Hiraeth·RUSuper 데모의 실제 플레이 주소는 하이퍼링크 텍스트만 보여 기록 못함. 플레이 페이지 로딩 확인은 한 건도 하지 못했다(외부 사이트 미방문).
- r/indiegames, r/WebGames, r/playmygame, r/IndieDev 단독 조회는 하지 못했다(IndieDev·SoloDevelopment·gamedev는 다중 서브 검색 1회만).

## 2. 제작자들이 밝힌 구체적 방법과 "슬롭을 넘게 한 요인"

### Takeaway
공통 패턴은 **(1) 설계 문서/티켓을 먼저 확정, (2) 에이전트가 게임을 직접 실행·스크린샷·계측해 자기 작업을 확인하는 루프, (3) 이미지 목업/레퍼런스와의 비교 평가, (4) 사람은 "재미·취향" 판정만 반복** 이다. 품질 상승 요인으로 제작자들이 직접 꼽은 것은 반복 횟수(98회 업데이트, ~700 프롬프트, Gauntlet-Loop 10라운드)와 봇 플레이테스트·프로파일러 같은 측정 도구다.

### Cited Findings

**Voltane (u/MacXou34, 1차)** — [스레드](https://old.reddit.com/r/aigamedev/comments/1xgcszc/9_days_ago_i_posted_the_game_i_built_with_opus_55/)
- "Code: Claude Code + Opus 5.5, every day. three.js on WebGPU, Rapier physics, a Node server for online play. / 3D models: concept sheets in gpt-image, turned into 3D with Tripo, cleaned up in Blender (also driven by Claude). / Sound: ElevenLabs for SFX, Suno for the level music."
- 9일간 플레이어 대상 업데이트 98건(게임 내 체인지로그), 댓글 피드백을 기능으로 반영(가입 화면 이탈 → 게스트 플레이 추가). 물리 튜닝: "it has been mostly test, see, iterate, again & again". 제작자 배경은 MMORPG 서버 프로그래머("I'm unable to draw anything").
- 댓글(u/RemarkableWish2508): "OP's 98 updates in 9 days, is not exactly one-shot. You need to iterate more, that part isn't optional."(원샷이 아니라 반복이 필수)

**Don't Touch the Dirt (u/Robotron1980, 1차)** — r/aigamedev, ≈2026-11-10 (permalink 미확보)
- 규모: "6 weeks (Sep 28 – Nov 9), about 33 days of actual work / ~700 prompts over 100 Claude Code sessions … / 221 commits, ~75k lines of TypeScript (sim, client, tests) / Almost all of it on Claude Opus, with Sonnet for some subagents"
- 테스트 루프: "It also ran and playtested the game in its built-in browser: ~5,000 JavaScript probes into the running page and ~1,000 clicks and screenshots, checking its own changes" (Claude Code 데스크톱 앱 내장 브라우저로 스스로 플레이·검증)
- 스택: three.js(WebGPU, TSL 셰이더), Rapier, Vite, TypeScript, Vitest, PeerJS(호스트 브라우저가 시뮬레이션, 서버 없음)
- 3D: "Blender, driven by Claude through an MCP bridge: every vehicle and building is a Python build script (box modeling and lofts, not primitive kitbash), modeled from reference photos and blueprints". 캐릭터는 Mixamo. 텍스처는 "ChatGPT / Codex image generation: … painting textures over Claude's clay renders of the models (~50 image prompts)"
- 오디오: CC0 필드 레코딩을 Python으로 편집. 트레일러 음악은 Claude가 numpy+CC0 오케스트라 샘플로 합성: "It can't hear, so it checked levels and spectra by measurement while I listened and gave notes."
- 단계별 프롬프트 수: 프로토타입 1~4일(~165) → 월드/아트 2주차(~70) → **디자인 리셋**("I stopped and wrote a design doc before building more") → 콘텐츠 3~4주(~155) → 필·폴리시 4주차(~220, 최다) → 트레일러·성능 5~6주(~90, iGPU 30fps 고정, iPhone Safari GPU 메모리 650MB→~220MB)
- 본인이 꼽은 "What worked": "Settling the design before the implementation. Most of my wasted prompts came from building before the design was settled." / "Telling it what's wrong in plain words and giving references: film stills, real photos, 'this looks like shiny plastic.'" / "Bots that play the level as tests, so a tuning change that breaks a route shows up right away." / "Measuring instead of guessing: a frame profiler and load logs it reads itself"

**RUSuper Godot 게임 (1차)** — [스레드](https://old.reddit.com/r/aigamedev/comments/1xrknnf/15_weeks_of_making_game_with_claude_opus_in_godot/)
- **Gauntlet-Loop**: OpenAI 이미지 API로 도시 목업 24장(6뷰×4시간대)을 만들고, "critic" 에이전트가 게임 화면과 목업을 **블라인드 비교**. "if a piece wins against the mockup twice, it's done and no more polishing. 31 out of 33 pieces won." 부작용: 목업에 없다는 이유로 등대 빔을 지워 "loops can't remove things the game already has just because a picture doesn't have them" 규칙 추가. Claude 아티팩트 링크 공유: `https://claude.ai/artifact/3BnUXUZQd9xLws6RxiyAtW`(미열람)
- 성능: 게임 내 성능 패널+`--perf-log` 로그를 만들고 Opus가 전체를 훑어 보고서 작성 → HUD 매 프레임 재그리기 제거(1080p 15~19% 향상), 지도 VRAM 4GB→0.3GB 타일 베이크, 시작 26초→13초
- Tripo 사용법: "I make one image with all 4 sides of the model (front, back, left and right), Opus splits it into 4 images, and I upload those to Tripo. Tripo works much better when it gets all 4 sides. After that, Opus fixes the model in Blender through MCP if needed."
- 역할 분담 댓글: "Blender MCP is for more boxy models and simple objects that are pretty from afar but not as good when zoomed in." / UI: "You can't make UI using code only, it will look like slop."(코드만으로 UI를 만들면 슬롭처럼 보임 → 이미지 생성한 테두리·버튼 텍스처를 얹음) / 오디오: "Gave ElevenLabs API key to Claude and asked Claude to do all the sound problems by itself." / 프롬프트: "there is no magic technique I use for prompting, just saying what I want, test playing and tweaking and fixing"
- 사용량: 주간 한도 94% 도달로 Max 플랜 추가 구독. "Jev"가 작업별 effort 수준을 정한다고 기술(Jev가 무엇인지는 본문에 설명 없음).

**SirKnighty Unity 6 파이프라인 (1차)** — [스레드](https://old.reddit.com/r/ClaudeAI/comments/1xul18m/my_game_got_removed_from_gamedev_subs_for_using/)
- "Claude (Opus 5.5) in Claude Code wrote basically all of the C#." / "Funplay MCP + Unity 6 let Claude drive the Unity editor directly. It can inspect scenes, change values, take screenshots and play the game, so it can see what it built instead of guessing. Having tested several MCPs: Funplay is the best one IMO" / Magnific(콘셉트·텍스처·머티리얼 맵) → Tripo(3D) → "Blender + MCP, driven by scripts, to clean up, split, rescale and fix those models"
- 야간 자동화: "A runner script takes one card at a time while I'm away (like sleeping), with a hard time and money budget per card. It works in its own branch, builds the game headlessly, runs tests, drives the built game to measure handling, takes screenshots, and only lands the change if everything passes."
- 마케팅도 자동화: 게임 내 스크립트 카메라 촬영 → 쇼츠 편집 → 게시 예약. "I still made every taste call: how it feels, how it looks, what's fun."

**Hiraeth (u/4nf, 1차)** — r/aigamedev ≈2026-11-04 (permalink 미확보)
- "Design audits: I tried to turn gaming design principles into reusable agent skills, then regularly audit the game against them. Across all 14 temples, does each one teach a mechanic, test it, then give it a twist?" / "Serendipity map: I built a map that highlights walkable ground more than 50 meters from anything to discover." / "Visual changelog: Every visual change gets a screenshot from the running game."
- three.js 기반 + JS 브리지로 Unity 빌드 병행. 3D는 "back and forth between Tripo, Meshy, and models built directly in Three.js".

**Godot 6주 사례 (u/Delicious-Shower8401 전달, 2차)** — r/ClaudeAI ≈2026-10-24 (permalink 미확보)
- Claude Code + Opus 5.5, "Claude Max 20× subscription". 커스텀 스킬: "'route' assesses the task and delegates suitable work to Sonnet or Haiku, with Opus reviewing the results" / "'handoff' starts a fresh session with the same setup and the context needed to continue" / "'Re-searcher' checks research claims and stores the findings in Obsidian"
- 아트 일관성: "There's a dedicated skill for describing the game's art direction, and every successful image prompt gets saved as JSON to guide future generations." VFX·셰이더 레이어 구성도 Obsidian에 문서화. 3D는 Tripo P2(큰 에셋) + Blender 모델링 후 Tripo 텍스처링(구독 약 $20/월).

**Hostarro Godot 워크플로 (1차, 플레이 불가·비-전부AI)** — r/aigamedev ≈2026-11-13 (permalink 미확보)
- Cursor에서 Claude·Codex 구독 사용, "Claude Opus 5.5 High and Extra High. I will run anywhere between 5-15 agents at a time". Linear를 API/CLI로 연결해 마일스톤·인수 기준 관리: "it allows agents to hold context SO much better than .md files"
- "Claude+Codex+Godot linked via custom MCP bridge and Godot's headless CLI / Claude+Codex+Blender linked via official MCP". "I run my entire workflow through Godot headless CLI and Godot Windowed Mode for visual testing … automated testing, unit tests, smoke tests, visual tests."
- 에이전트 역할: developer, game designer, QA tester, adversarial tester, reviewer, blind tester 등. 비용: "my biggest burn months were something like £2000-3000". 주 60~70시간, 절반은 기획·문서.
- 교훈: "Do not let your AI models freeball and just run blindly … Always keep them controlled and contained with tickets, design documents". "The models are extremely good at UI for example but REALLY bad if you just let them run free."

**기타 1차 진술**
- Meltbelt: "My workflow is playtest, write a list all the stuff I want changed to Claude … The only bottleneck is playtesting" — r/aigamedev, u/Professional_Job_307
- ForkedPush(Unity): "Animations took the most back and forth. AI gets you something that technically works really fast, but making it feel natural still needs a lot o…"(본문 잘림)
- Gambo7592: "Claude Opus 5.5 built the game and wrote the image prompts for assets / GPT-6 Luna drew the art from claude's prompts / Built in three.js / AI music (ACE-Step), real recorded sound effects"
- 위 3건·Hiraeth·Hostarro 등 본문 출처: `https://old.reddit.com/r/aigamedev/search?q=itch.io+OR+%22play+it%22+OR+%22free+to+play%22+OR+%22steam+demo%22+OR+playtest&restrict_sr=on&sort=top&t=month` 및 `…search?q=Unity+OR+Godot+OR+Unreal+MCP&restrict_sr=on&sort=top&t=month` 결과 페이지

### Inferences
- "슬롭을 넘는" 요인으로 반복 등장하는 것은 도구가 아니라 **검증 루프의 밀도**다: 에이전트가 실행 화면을 보고(스크린샷·내장 브라우저·MCP 플레이), 목업과 비교하고, 봇이 레벨을 돌고, 프로파일러 수치를 읽는다.
- 설계 문서를 먼저 고정한 시점이 품질·효율의 전환점이었다는 진술(Don't Touch the Dirt, Hostarro)이 일치한다.
- UI는 코드만으로 만들면 슬롭처럼 보인다는 지적(RUSuper)과 "UI는 잘하지만 풀어놓으면 최악"(Hostarro)이 함께 나온다 → UI에는 생성 이미지 텍스처 + 강한 제약이 쓰인다.

### Gaps
- 공유된 스킬/프롬프트 원문 저장소는 확인하지 못했다(RUSuper의 Claude 아티팩트 링크, HugoDzz의 write-up은 주소만 확인·미열람).
- 프롬프트 전문을 공개한 글은 314t의 벤치마크 프롬프트(3번 질문) 외에 찾지 못했다.
- OP 답글은 "top 200 comments" 범위만 읽었고 접힌 답글("load more comments")은 펼치지 않았다.

## 3. Godot/Unity/Unreal 실무자가 말하는 에이전트+엔진 워크플로, 3D 생성기, 2D/스프라이트 파이프라인

### Takeaway
엔진 연동은 **Godot = headless CLI + 커스텀 MCP**, **Unity = Funplay MCP 또는 자작 도구**, **Unreal = 에이전트 대기 시간·토큰이 크게 늘어난다**는 벤치마크 보고가 핵심이다. 3D 생성기는 Tripo가 가장 많이 쓰이지만 "4면 이미지 입력 + Blender MCP 후처리"가 전제이고, 데시메이션·폴리 수 때문에 못 쓴다는 반대 보고도 있다. 2D는 "생성 영상/GIF → 스크립트로 키잉·그리드 정렬·팔레트 통일" 방식이 구체적으로 공유됐다.

### Cited Findings

**엔진 연동**
- **Godot vs Unreal 벤치마크** (u/314t, "Opus5.5 Low to Max - Godot 4.7 vs Unreal 5.8", r/aigamedev, ≈2026-10-30, 261~265점 / 84, 1차): 같은 디오라마 프롬프트로 effort별 비교. 표 발췌 — low: Godot 1.87M 토큰·5m42s vs Unreal 5.33M·25m58s / high: Godot 7.00M·18m1s vs Unreal 25.88M·1h18m47s / max: Godot 54.52M·1h35m22s vs Unreal 71.42M·1h37m57s. "Claude performed worse on Low in Unreal than Godot, and completely skipped the rain in all Unreal scenes … What I observed that took up good chunks of these times were assets importing into Unreal, and rendering captures to review its own work, overall just engine overhead." 사용 프롬프트(Godot): "Build a moody Godot 4 diorama: overgrown cyberpunk alley at blue hour, rain-slicked PBR surfaces, neon emissive signs with bloom, volumetric fog, SDFGI, ACES tonemapping, tilt-shift depth of field, scattered set dressing, low-angle hero shot." (permalink 미확보)
- Godot가 에이전트에 유리한 이유(2차, Delicious-Shower8401): "Godot helps because it's open source, easy to build custom tools for, and supports running scripts headlessly". Voltane 스레드 댓글(u/duskaception): "i was struggling with unreal and bevy. Once I switched to godot everything was so intuitive" / (u/azicre): "Three JS makes a lot of sense these days. Agents have a lot of training data for web stack in general."
- **three.js → Godot 포팅 후 복귀** (u/Conscious-Desk6823, 아트 디렉터·비개발자, ≈2026-11-18, 265~268점 / 68, 1차): Godot 포트는 잘 됐지만 "maintaining two versions quickly became a headache", 성능 문제는 커스텀 안티에일리어싱으로 해결("I only discovered this thanks to Fable 5.2"), "being able to share the game instantly through a browser is still a huge advantage".
- **Unity**: SirKnighty의 Funplay MCP 평가(2번 질문). u/imlo2(Unity 6 URP 절차 지형): "I direct and judge, look into issues, Claude Code builds it and fixes bugs … Claude writes the code, shaders and tools, and measures its own work before I look." 셰이딩 디버그 뷰(노멀·알베도·투과 등)를 런타임 토글로 만들어 에이전트·사람이 함께 확인. u/Cheesewizard06(r/Unity3D, ≈2026-11-16, 16점): 여러 git worktree의 Claude Code/Codex 에이전트가 **Unity 에디터 1개를 공유**하는 도구 — .uss 변경을 실행 중 게임에 반영하고 스크린샷 반환, Play 모드 락, 두 번째 에디터 없이 컴파일·테스트. u/dechichi "Unity update their terms of services. You can only use 3 instances of the editor per machine." (r/aigamedev, ≈2026-11-21, 217점 / 153, 제목만 확인 — 다중 에이전트 운용에 영향 가능)
- **Unreal**: r/unrealengine에서 조건에 맞는 에이전트 워크플로 고득점 글은 검색에 잡히지 않았다. r/aigamedev에 "I've been experimenting with dragon flight in Unreal Engine"(u/No-Blacksmith7127, 515점)이 있으나 본문 미확인.

**3D 에셋 생성·게임 레디**
- Tripo 긍정: RUSuper(4면 시트 입력 권장, "Tripo saves me a huge amount of time on modelling"), Voltane(gpt-image 콘셉트 시트→Tripo→Blender), SirKnighty(Magnific→Tripo→Blender MCP 스크립트로 정리·분할·리스케일), Delicious-Shower8401(Tripo P2).
- Tripo 부정(Hostarro, 1차): "Tripo and similar 3D modelling tools - they make nice stuff, I haven't been able to get them working for my 3D game. Decimation processes are poor and destroy the model, triangle counts are always so overblown and won't perform well in game. I also just feel Astra is better at it." (데시메이션이 모델을 망가뜨리고 삼각형 수가 과다)
- 댓글(u/Furyan9x, Voltane 스레드): "I'm using paid 3d ai Studio tools, cleaning models with Claude in blender … The models are ok, but obviously ai. I've tried using their built in fixer and clean up and retopology tools, but they never produce the desired results."
- **에이전트 직접 모델링 파이프라인** (u/randomforest99, Liliput, ≈2026-10-29, 443~445점 / 101, 1차): "I approve or reject the designs and give notes. Once a design is approved, the agents handle the modelling, texturing and checks. About 50 minutes per asset … The models have to fit the game's budgets. The beetle in the video is 876 triangles with four animation clips. / This is somewhere past iteration 20 of the pipeline itself. Feedback gets turned into instructions and checks for later builds."
- 코드 전용 3D: Riposte("There are no imported 3D models"), Don't Touch the Dirt(Blender Python 빌드 스크립트 + 이미지 모델로 클레이 렌더 위 텍스처 페인트오버).
- 리깅/애니메이션: Don't Touch the Dirt는 Mixamo 사용. "NVIDIA has released the weights for MotionBricks on HuggingFace"(u/Recoil42, 913~919점, News — 제목만 확인). 영상 생성은 Hostarro가 "$500 넘게 실험했지만 실패"라 보고.

**2D·스프라이트·픽셀**
- **GIF→픽셀 이펙트** (u/KasperzackGames, "How I turn ChatGPT's new GIFs into game-ready pixel art effects (full method + free kit)", ≈2026-11-10, 415~418점 / 26, 1차): 프롬프트 처방 — 지면 고정 "The bottom edge of the frame is the ground line, and the explosion hits the ground at the bottom centre, at the same point in every frame." / 픽셀 크기 "each art pixel is only 2 to 3 image pixels wide" / 키잉 "flat solid pure magenta #FF00FF in every frame"(보라색 이펙트는 #00FF00). 후처리 스크립트: 배경 키잉, 전 프레임 단일 픽셀 그리드·단일 팔레트(폭발 26색), 흔들림 0.43→0.30px, 스프라이트 시트+JSON. Godot 타격감: "a 4 to 6 frame hit-stop, 1 or 2 black-and-white impact frames, a 40% flash, screen shake in whole pixels … smoke held for 1.8 s". 한계: "it draws 'HD pixel art' …, it ignores size requests (I asked for at least 512 x 512 and got 316 x 301)".
- **코드 기반 픽셀 VFX** (u/HugoDzz, "How to make good pixel art effects with Claude", ≈2026-10-29, 856~858점 / 70, 1차): "Treat code as clay … Ask your agent to generate many option as video records, then pick one, and repeat until it feels right." / "the quality bar is on you" / Houdini·영화·Path of Exile 2를 레퍼런스로. 이펙트 소스 포함 write-up 공유(주소 미노출).
- **영상 1회로 캐릭터 10명 걷기** (u/Bill_Buffet, ≈2026-11-11, 182~185점 / 26, 1차): 이미지 모델로 캐릭터(~$0.04) → 그린스크린 2×5 슬롯 배치 → "One image-to-video generation (Seedance 2.0 Fast via OpenRouter, 720p, 5 s, $0.46) with the prompt 'everyone walks in place, don't interact'" → Python/ffmpeg로 슬롯 크롭·키잉·발 정렬·루프 탐색·Godot SpriteFrames 출력. "10 per clip = $0.046. Quality holds at game size (~200 px tall)". 대안 평가: 컷아웃 본 리그는 "looked like a paper puppet".
- **스프라이트→스켈레톤** (u/GeorgiaWitness1, "Fable 5.2 was the first model capable of doing reliable sprite to skeleton", ≈2026-11-12, 413~417점 / 50, 1차): Spine 사용, 저장소 `https://github.com/enoch3712/spine-hero-skill`(미열람).
- **2D 리깅 컴파일러** (u/firejune, rig-c, ≈2026-10-24, 177점 / 24, 1차·자작 OSS): "I stopped treating the rig as something the agent writes and started treating it as something the agent submits to a compiler." 에이전트는 JSON 2개(rig/motion spec)만 쓰고 rigc가 명명된 어서션(기본 36개, 엄격 50개)을 통과해야 Spine 4.3 데이터를 출력. 문제 인식: "the agent's only feedback was whether the file parsed … The file loads, the agent says 'done', and it isn't lying." 저장소 `https://github.com/rig-c`, 데모 `https://rig-c.org/examples/`(미열람).
- 자기 툴 홍보성 팁(u/No-Dragonfruit-675, ≈2026-11-11, 270점): 3D는 A-포즈·단색 배경·다각도 캐릭터 시트, "One-shot is mostly a myth"; 2D는 스탠드인 스프라이트에 애니메이션을 만든 뒤 모델이 덧그리게 하고, "have a coding agent redraw your AI pixels on to a real pixel grid". **벤더성 글로 표기.**
- 위 2D 항목 출처: `https://old.reddit.com/r/aigamedev/search?q=sprite+OR+spritesheet+OR+%22pixel+art%22+OR+rigging+OR+Meshy+OR+retopology+OR+skeleton&restrict_sr=on&sort=top&t=month` 결과 페이지

### Inferences
- 에이전트 관점에서 엔진 선택의 실질 변수는 "headless 실행·빠른 캡처·낮은 임포트 오버헤드"다. Godot와 웹 스택이 유리하고 Unreal은 같은 작업에 시간·토큰이 더 든다는 보고가 한 건(314t) 있다 — 단일 작성자 벤치마크라 일반화는 주의.
- 3D 생성기는 "원거리 카메라·스타일라이즈드" 게임에서 호평, "근접 3D·폴리 예산 엄격" 게임에서 불만이라는 구도다.
- 2D는 "모델이 진짜 픽셀아트를 못 그린다"를 전제로 후처리 스크립트·컴파일러식 검증을 두는 접근이 수렴한다.

### Gaps
- Meshy에 대한 구체적 장단점 진술은 Hiraeth의 병용 언급 외에 찾지 못했다. Unity MCP 종류 비교, Unreal MCP, Godot MCP 제품명 수준의 글도 확인 못함(쿼리 "Unity MCP/Unreal MCP/Godot MCP" 개별 검색은 미실행).
- r/blender, r/StableDiffusion은 다중 검색 1회에 포함됐을 뿐 개별 확인하지 않았다(잡힌 글: r/blender u/wolfinganger "I recreated an AI Generated Asset by hand for my game" 1,748점 — 본문 미확인).

## 4. 댓글이 칭찬하는 것과 슬롭이라 부르는 것, AI 콘텐츠 관련 서브레딧 규칙

### Takeaway
칭찬은 "디테일·반복·즉시 플레이 가능성·투명한 스택 공개"에, 비판은 "원작 대비 조작감, 기존 게임 유사성, 게임플레이를 안 보여주는 트레일러"에 몰린다. 공유 장소는 사실상 갈린다: **r/aigamedev·r/ClaudeAI는 워크플로 공개를 조건으로 환영, r/godot은 규칙 4 "No AI"로 프로젝트·스크린샷·코드까지 금지**, 일반 gamedev 계열에서는 삭제·"슬롭" 낙인 사례가 보고된다.

### Cited Findings
- **r/aigamedev 규칙** (규칙 페이지 원문): "4. Game Promotion Posts Allowed, with Requirements — You must discuss your game within the context of how it was developed using AI. Share with the community and give something for the community to talk about in your development experience with AI. A fire and forget video/image with no text, chatGPT bullet list may be removed by mods. If your game is being sold, you MUST apply the 'Commercial Self Promotion' flair." / "3. No promotion of commercial services or products — Commercial GAMES are OK…" / "5. No AI art or artist bashing" / "10. English Only Posts" — [r/aigamedev rules](https://old.reddit.com/r/aigamedev/about/rules)
- **r/godot 규칙** (사이드바 원문): "4. No AI — Don't make posts or comments here that are generated by AI. This also applies to projects, screenshots, videos, art, and code. Translation is fine, asking AI to write your post is not." — r/godot 사이드바(검색 페이지 `https://old.reddit.com/r/godot/search?q=Claude+OR+MCP+OR+LLM+OR+%22AI+agent%22+OR+vibe&restrict_sr=on&sort=top&t=month`에서 확인)
- r/godot 분위기(기간 내 상위 글, permalink 미확보): "Don't Use LLMs, Just Read The Documentation"(u/PleaseCallMeKelly, ≈2026-11-16, 1,621점 / 827), "What's with the slop bros taking over this subreddit?"(u/kcorac, ≈2026-11-15, 1,009점 / 596 — "lately I'm only getting AI-SLOP whether as a full on vibe-coded project or a request for help with writing specs for a prompt in an obvious disguise"), 반론 "No AI, Stack Overflow is dying, and tech posts get removed. How are we supposed to code?"(u/El_M4estro, ≈2026-11-13, 1,216점 / 1,080 — "Even Godot's own contribution guidelines allow some AI coding assistance").
- 삭제 사례(1차): SirKnighty "A couple of gamedev subs removed my posts as I disclosed AI use" / "In one of the subs I included a disclosure, in another I didn't include it but still got removed claiming 'it was all AI'." — [r/ClaudeAI](https://old.reddit.com/r/ClaudeAI/comments/1xul18m/my_game_got_removed_from_gamedev_subs_for_using/)
- 오인 사례(1차): u/Sudden_Bite_4808, r/SoloDevelopment ≈2026-11-15, 146점 / 635 — 3년 만든 게임이 "AI slop" 취급: "I didn't even use AI aside from debugging, but the mob decided I am a fraud."
- 공개의 역풍(1차): u/civerooni "I disclosed every AI-made part of my solo game on Steam. The disclaimer is one of the main things people comment on." (r/ClaudeAI, ≈2026-11-13, 1,016점 / 937) — 인용된 타 서브 반응: "Ditch the AI and I'll play it", "it's ironic to me that a game with so much effort put into representing a non-artificial world would sabotage itself with an AI menu song". r/aigamedev에도 "PSA: if you post your game here, it gets marked by anti ai users for review bomb at launch"(u/Alarmed-Quail7617, ≈2026-11-13, 470점, 제목만 확인).
- 칭찬 포인트 예: Voltane "the way you choose the car from the boxes is a great level of detail"(20점), "putting a guest mode on would be 3 weeks and 12 meetings … at a game company, but you're just a dude, so you just did the reasonable thing"(69점). 비판 포인트 예: "next trailer should show more racing without interruptions. I can't get a sense of how driving might feel"; RUSuper도 게임플레이가 안 보인다는 지적에 "my gameplay presentation just suck ass … how bad I am with making trailers"라 인정.
- "프로토타입 ≠ 게임" 정서: "I'm happy you made something in 3 days but it's a prototype not a game"(u/SeasawPhilosopher, ≈2026-11-19, 331점), "hot take: ai game development is far, FAR HARDER than most people assume it is"(u/Apprehensive_Golf_21, ≈2026-11-02, 339~348점 / 252) — 둘 다 r/aigamedev, 제목만 확인.
- **Steam AI 공개 통계 원출처**: "[OC] Share of new Steam games that disclose AI-generated content, from 1.7% in January 2024 to 49.9% in October 2026", r/dataisbeautiful, u/ploz, **2026-11-01(정확), 2,404점(98%) / 427댓글**. 작성자 설명: "I went through every game released on Steam between January 2024 and October 2026 (63,596 games) and read the AI content flag that Valve keeps in each game's app data … It's self-reported … Since January 2026 the disclosure only covers AI content players see or hear, in the game and in its marketing. AI tools used during development don't have to be declared … Yearly: 2024 13.2%, 2025 24.0%, 2026 so far 40.1%". 추가 답글: 리뷰 수 비중은 "2026 so far: 40.0% of games, 12.2% of reviews"; 리뷰 100개 이상 게임만 보면 2024-01 2.8% → 2026-10 27.1%, 리뷰 10개 이상은 1.8% → 35.5%; "More than half of all releases have fewer than 10 reviews." — [r/dataisbeautiful, u/ploz](https://old.reddit.com/r/dataisbeautiful/comments/1xlebcj/oc_share_of_new_steam_games_that_disclose/)
- Steam 판매 데이터(1차·자기보고): u/drive_wave(업계 12년+, Coin Harvest, ≈2026-10-24, 348점 / 274) — AI 공개(스토어 아트·일부 렌더 에셋), "About 4,500 copies in the first 36 hours, ~6,900 now … Refunds are at 11% overall … US and Japan are at 5-6% … China, Korea and CIS are almost 3x that". u/Shalke97(≈2026-11-12, 364점 / 128, Commercial Self Promotion) — 리뷰 50개(85% 긍정), 1,500장, 환불률 27%→15%("Don't have a community.. instead, be part of the community").
- 클론 이슈: "Anthropic has quietly told Claude Code to stop remaking existing video games"(r/aigamedev, ≈2026-10-31, 703점 / 372, madrobot.blog 링크), r/ClaudeAI "Anthropic confirms new Claude Code limits to prevent game cloning"(≈2026-11-03, 1,803점), r/IndieDev "HUGE news, Claude will stop allowing users to recreate existing games!!"(≈2026-10-31, 2,342점) — 모두 제목만 확인, 내용 미검증.

### Inferences
- 같은 게임이라도 **어디에 올리느냐**가 반응을 좌우한다. AI 제작을 전면에 내세우려면 r/aigamedev(워크플로 서술 + 판매 시 플레어)·r/ClaudeAI가 안전하고, r/godot은 규칙상 불가다.
- 49.9% 통계는 "보이는/들리는 AI 콘텐츠의 자기신고"이며 코딩 보조는 빠져 있고, 리뷰 비중으로 보면 12% 안팎이라는 작성자 보충이 붙어 있다 — 인용 시 이 한정을 같이 써야 한다.

### Gaps
- r/gamedev, r/IndieDev, r/SoloDevelopment, r/Unity3D, r/unrealengine의 AI 관련 규칙 원문은 확인하지 못했다(SirKnighty가 말한 "gamedev subs"가 어디인지도 미확인).
- 댓글 여론은 스레드 4개(Voltane, fableflight, RUSuper, SirKnighty)와 통계 스레드만 직접 읽었다.

## 5. 플레이 가능하면서 AAA급 충실도에 근접한 것이 있는가

### Takeaway
이번 조사 범위에서는 **없다**. 고충실도에 가까운 것은 기술 데모(Unity 절차 지형·행성)이거나 팀 프로젝트이고, 플레이 가능한 1인 AI 게임은 스타일라이즈드·로우폴리·브라우저 규모다.

### Cited Findings
- 가장 사실적인 비주얼 사례는 u/imlo2의 Unity 6 URP 작업이나 본인이 게임이 아니라고 명시: "I've still not decided what to make out of this - does it stay as a proof of concept, or will I develop a game out of it." (섬 약 42,000그루, RTX 3090 1440p 60fps 이상) / 행성 데모는 "prototyping game graphics tech" — r/aigamedev, ≈2026-11-05·≈2026-11-21 (permalink 미확보)
- 스케일이 가장 큰 쇼케이스 "GTA-inspired game with a 100 km² map of Bangkok"(2,557점)는 **8인 팀 + 자체 엔진**이라 1인 기준 밖 — r/aigamedev 월간 1위(본문 미확인)
- fableflight는 실사 지형처럼 보이지만 Google tiles API 데이터를 쓰며, 제작자 스스로 "plenty of room for improvement, particularly in flight realism, graphics, optimization, UI, and aircraft models" — [r/aigamedev](https://old.reddit.com/r/aigamedev/comments/1xwf9rv/im_a_huge_fan_of_microsoft_flight_sim_2024_but/)
- 실무자 인식: SirKnighty(전 AAA 근무) "some of them are heavily investing into AI"; r/gamedev에는 Simon Willison 글을 소개한 "The October inflection point for vibe game development"(u/danwin, ≈2026-10-29, 191점 / 180, 링크 `https://simonwillison.net/2026/Oct/28/vibe-game-development/`, 미열람)
- r/ClaudeCode "korean solo dev, 5 months making WW2 RTS with Claude Code…"(u/greenlight91, ≈2026-10-30, 517점 / 389): "people said it looks like Gates of Hell" — Steam 링크는 댓글에 있다고만 적혀 있고 미확인

### Inferences
- "AAA 근접"은 렌더링 기술(지형·대기·식생) 단위에서만 관찰되고, 콘텐츠·애니메이션·게임플레이까지 갖춘 플레이어블 1인작에서는 관찰되지 않았다.
- 고득점 플레이어블 사례들은 의도적으로 원거리 카메라·스타일라이즈드·절차 생성으로 충실도 요구를 낮추고 있다(RUSuper: "Given my camera is from afar I don't mind that too much").

### Gaps
- 영상은 재생하지 않았으므로 비주얼 수준은 본문 서술과 댓글 반응으로만 판단했다.
- greenlight91 WW2 RTS, No-Blacksmith7127 Unreal 드래곤 비행, mescal_ "Claude + Unity + Atlas" 발견 푸티지 게임(475점)은 본문·댓글을 확인하지 못했다.

### 조사 방법·실행 기록 (부록)
- **접근**: Chrome 새 창 1개 → 주소창에 URL 입력(AX set_value + Return) → `get_window_state` 접근성 트리를 파일로 받아 웹 영역 텍스트만 파싱. 스크린샷 미사용. 사용자의 기존 창·탭은 조작하지 않음.
- **실행한 페이지(약 20회 로드)**: `r/aigamedev/top/?t=month`(25개·100개), r/aigamedev 검색 5회(작성자, "Unity OR Godot OR Unreal MCP", sprite/rigging/Meshy 계열, itch.io/play it/steam demo/playtest 계열), 사이트 검색 `Slotbound`(t=all), 사이트 검색 Steam AI 49.9%, r/dataisbeautiful 검색, r/godot 검색, 다중 서브 검색 2회(Unity3D+unrealengine+gamedev+IndieDev+SoloDevelopment / ClaudeAI+ClaudeCode+codex+vibecoding+threejs+Unity3D+unrealengine+StableDiffusion+blender), r/aigamedev 규칙 페이지, 스레드 5개(Voltane, fableflight, RUSuper, ploz 통계, SirKnighty).
- **잘 된 것**: old.reddit 검색 결과 페이지가 글 본문 전문을 보여줘 한 번 로드로 여러 글의 방법론을 읽을 수 있었다. 스레드 페이지에서는 정확한 게시일·점수·추천 비율을 얻었다.
- **안 된 것**: (1) `page get_text`는 브라우저 메뉴·방문 기록까지 섞여 나와 첫 1회 후 사용 중단(해당 내용은 기록하지 않음). (2) JS 실행은 CDP 포트가 없어 불가. (3) 접근성 트리에 링크 href가 없어 permalink는 스레드를 열어야만 확보. (4) 화면 밖 링크는 AX 클릭이 실패(-25202)했고, 화면 안 링크도 첫 클릭이 무반응이라 두 번째 클릭에서 이동. (5) `.rss` 피드는 "Not Found". (6) `author:A OR author:B` 검색은 일부 작성자만 반환.
- **차단 여부**: 로그인 벽·CAPTCHA·차단 페이지는 나타나지 않았다.
- **미실행**: r/indiegames, r/WebGames, r/playmygame 개별 조회, 쿼리 "Blender MCP", "Unity CLI", "AI playtest", "postmortem AI" 개별 검색, 외부 플레이 페이지·저장소 README 확인.
