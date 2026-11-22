# 목표 화면을 먼저 그리고 심사 루프로 쫓는다

최근 한 달(2026-10-22 ~ 2026-11-22) X·Hacker News 자료에서 "1인 기획 + AI (거의) 풀 제작 + 지금 플레이 가능 + 답글·수치로 관찰되는 높은 품질"을 함께 충족하는 게임은 **Sumiro, Felix Rieseberg의 one-shot FPS(Saltline), Starry Night Rider, 雾锁山门(guizang-game-skill), What the water keeps, Small Magic/Oilpaint, Fall Line, Aiden's Revenge**이고, Steam 무료 데모가 있는 **Iron Curtain Call**은 설계·레벨을 사람이 쥐고 코드를 AI가 쓴 부분 충족 사례다. 방법 설명이 가장 정교한 @MengTo의 Dark Souls풍 게임과 규모가 가장 큰 AOD는 공개 빌드가 없어 "플레이 불가"로 분리하되 방법론 근거로 쓴다. 이들의 방법을 겹치면 파이프라인은 다섯 동작으로 수렴한다. **(1) 영상·컨셉 이미지로 목표 룩을 먼저 고정하고, (2) 컨셉 이미지 → Tripo 등으로 GLB → 코드 또는 Blender로 리깅하거나 아예 모델·텍스처를 셰이더와 함수로 쓰고, (3) 같은 카메라의 전후 스크린샷을 블라인드 심사 에이전트가 채점하게 하고, (4) 영역별 병렬 에이전트가 파일을 나눠 갖고, (5) 사람이 매 빌드를 직접 플레이한다.** 생성 도구 목록보다 검증 장치(블라인드 심사, 자동 체크 193개, 입력 기록 재생)가 품질 설명의 중심이었다. 비용은 자가 보고 기준 8시간·약 550달러(API가)부터 반나절·4.5억 토큰, 7일·약 1,520커밋까지 퍼져 있다. 한계도 일관된다. 캐릭터 애니메이션과 사운드는 제작자 본인들이 약점으로 인정했고, 넓은 범위·높은 충실도·공개 플레이를 동시에 만족한 **AAA급 범위의 1인 AI 제작물은 찾지 못했다.** 이 보고서의 품질 판단은 게시물·참여 수치·답글을 읽은 것이며 게임을 직접 플레이하거나 플레이 링크를 열어 본 평가가 아니다.

**표기 규칙.** [1차] 제작자 본인 글, [자가 보고] 독립 검증 없는 본인 수치(시간·토큰·비용 전부 해당), [논평] 제3자 답글·게시물, [랩 직원]·[벤더] AI 연구소 직원이나 자사 제품을 파는 쪽의 시연, [2차] 매체 정리, [추정] 조사자의 추론, [배경·기간 외] 2026-10-22 이전 자료. 참여 수치는 답글 · 좋아요 · 조회 순이며 2026-11-22 열람 시점 값이다. X 인용문은 추출 과정에서 `% ? = & ;`가 빠졌으므로 **문자 그대로의 인용이 아니라 근사 인용**으로 읽어야 하고, 해당 문자가 들어갈 자리는 가급적 한국어로 풀어 썼다. 중국어 게시물은 X 자동 번역 또는 oEmbed 원문 기준이다.

## 플레이 가능한 고퀄 후보는 아홉 축, 전부 브라우저이거나 무료 데모다

선정 기준은 상업적 검증이 아니라 "플레이 가능 + 1인 기획 + AI 풀 제작 + 관찰되는 품질"이다. 아래 표는 게시글에 플레이 링크가 적혀 있는 것만 담았고, 링크는 게시글에서 옮겨 적었을 뿐 열어서 확인하지 않았다.

| 게임 / 제작자 | 게시일 | 플레이 링크(게시글 기재) | 답글 · 좋아요 · 조회 | 형태·제작 시간 [자가 보고] | 기준 충족 메모 | 출처 |
|---|---|---|---|---|---|---|
| Sumiro / @xikhar | 2026-11-04 | https://xikhar.github.io/sumiro | 1,090 · 15,698 · 6.45M | 3D 어드벤처, 24시간 | 충족. 7단계 워크플로 공개 | [X](https://x.com/xikhar/status/2117776295534997818), [링크 답글](https://x.com/xikhar/status/2117837699327594997) |
| one-shot FPS(Saltline) / @felixrieseberg | 2026-11-09 | claude.ai/artifact/BGY1SztrAYcJQHSsnHHGmp… (게시글에서 잘림) | 862 · 15,036 · 4.48M | 작은 레벨의 3D FPS, 8시간 | [랩 직원] Anthropic 소속으로 알려진 인물의 모델 시연 | [X](https://x.com/felixrieseberg/status/2119925633564463609), [AIGamer](https://www.aigamer.gg/games/saltline) |
| Starry Night Rider / @ebbyamir | 2026-11-10 | https://starrynightrider.com | 503 · 17,950 · 1.99M | 고흐풍 라이딩, 6~8시간 | 충족. 반응 최상, 방법 설명은 거의 없음 | [X](https://x.com/ebbyamir/status/2120284261089673376) |
| 雾锁山门 / @op7418(歸藏) | 2026-11-12 (UTC) | https://op7418.github.io/guizang-game-skill/… | 275 · 1,169 · 300K | 3D 액션, 반나절, 30MB 단일 HTML | 충족. 스킬 repo 공개 | [X](https://x.com/op7418/status/2120694045299327187) |
| What the water keeps / @kevin_t_ngo | 2026-11-09 | what-the-water-keeps.vercel.app | 176 · 4,285 · 514K | 8개 월드 보트 라이드 | 충족. 파이프라인은 음악만 공개 | [X](https://x.com/kevin_t_ngo/status/2119868968307695818) |
| Small Magic / Oilpaint / @BlendiByl | 2026-11-14 / 11-11 | https://patch.gg/play/blendi/small-magic… / patch.gg/blendi/oil-paint… | 133 · 2,562 · 165K / 393 · 8,016 · 457K | 전부 코드, 1일 / 1시간 미만 | 충족. patch.gg 플랫폼 홍보 성격 가능성 [추정] | [X](https://x.com/BlendiByl/status/2121594536153718972), [X](https://x.com/BlendiByl/status/2120341251178594532) |
| Fall Line / @BananaOfMercy | 2026-11-18 | https://fallline-9zo.pages.dev | 26 · 284 · 17K | three.js 다운힐 MTB, 7일 | 충족. 조작감 반복 방법이 가장 구체적, 참여는 작음 | [X](https://x.com/BananaOfMercy/status/2123037856398733438) |
| Aiden's Revenge / Lex Toumbourou | HN 제출 2026-11-09 | aidens-revenge.pages.dev (HN 댓글의 에셋 URL로 확인) | HN 506점 · 댓글 456 | 2D 4인 beat 'em up, 약 2일 | 충족. 캐릭터 원화는 조카의 손그림, 6월 구버전 위에서 시작 | [블로그](https://notesbylex.com/fable-5-2-one-shotted-my-nephews-dream-game), [HN](https://news.ycombinator.com/item?id=50433659) |
| Iron Curtain Call / @whaledevstudios | 2026-11-06 (데모 10-23) | https://store.steampowered.com/app/5417460/Iron_Curtain_Call/ | 133 · 1,423 · 110K | Godot 카툰 FPS, Steam 무료 데모 | **부분 충족.** 코드는 AI, 레벨·무기 감각·디자인은 사람 | [X](https://x.com/whaledevstudios/status/2118500903783141660) |

雾锁山门의 게시일은 status ID 역산과 oEmbed가 11-12 01:43 UTC를 가리키며, X 검색 노트의 표에는 11-11로 적혀 있다. 그 아래 등급의 플레이 가능작도 있다. MAAD Maxxing(@Andrew_Blumson, 11-11, https://maad-maxxing.vercel.app, 64 · 248 · 122K)은 에셋 없이 코드만으로 3스테이지를 만들었고([X](https://x.com/Andrew_Blumson/status/2120599812512833557)), dimension9(@apekshik, 11-06, http://dimension9.space, 127 · 3,754 · 256K)은 Opus 5.5가 런타임에 방을 계속 생성하는 멀티플레이 Backrooms다([X](https://x.com/apekshik/status/2118847014071120179)). Getting There(@Rubzem, 11-15, tesana.com, 144 · 2,658 · 160K)는 2D·4시간·14챕터를 내세웠지만 본문은 에셋과 사운드가 전부 절차적이라고 하고 답글은 Claude가 fal API로 GPT6-Astra 이미지와 스프라이트를 만들었다고 해 서로 맞지 않는다([본문](https://x.com/Rubzem/status/2122013352755126431), [답글](https://x.com/Rubzem/status/2122938540455788718)). fly(@creativedash, https://remix.ui8.ai/fly, 87 · 2,980 · 57K)는 "3D 엔진 없음, 폴리곤 없음, 32KB"를 내세우나 AI 사용 여부가 읽은 본문에 없고([X](https://x.com/creativedash/status/2122389375673913491)), GREY FLIGHT(@TheLateBuild, 11-16, https://valentino718.itch.io/grey-flight, 2 · 3 · 84)는 Unreal 잼작이지만 반응이 거의 없어 품질을 판단할 수 없다([X](https://x.com/TheLateBuild/status/2122470896690733369)). Simon Willison의 브라우저 게임 4종(Tree Appreciator, Emberwick, Battle Drones, Quarter Sun Cove)도 정적 호스팅으로 공개돼 있고 방법 근거로 쓴다([simonwillison.net, 2026-10-28, 1차](https://simonwillison.net/2026/Oct/28/vibe-game-development/)).

이 목록에서 세 가지가 읽힌다. 첫째, **Steam 데모 하나를 빼면 전부 브라우저 빌드다.** 조회수 상위 셋(Sumiro, Felix FPS, Starry Night Rider)은 모두 본문이나 첫 답글에 바로 열리는 링크를 붙였다. 둘째, 반응이 가장 좋은 작품은 인물이 없는 풍경·추상 스타일(Starry Night Rider, Oilpaint, What the water keeps)이고, 방법을 가장 자세히 쓴 작품은 참여가 작다(Fall Line). 셋째, 고충실도 3D를 플레이 가능하게 공개한 사례는 범위를 극단적으로 줄였거나(Felix의 작은 레벨과 드론 적) 고정 카메라를 썼다는 것이 조사 노트의 추론이다 [추정].

### 플레이 불가: 방법은 정교하지만 빌드가 없는 것

| 게임 / 제작자 | 게시일 | 답글 · 좋아요 · 조회 | 플레이 불가 사유 | 방법론 가치 | 출처 |
|---|---|---|---|---|---|
| Dark Souls풍 Three.js 게임 / @MengTo | 2026-11-15 | 167 · 1,025 · 90K | "플레이 가능한 데모"라고만 하고 링크 미게시. 컴퓨터가 계속 생성 중이라 못 보여 준다고 답함 | 최상. dream loop, 블라인드 심사, 코드 리깅 공개 | [X](https://x.com/MengTo/status/2121896633848017145) |
| AOD - Age of Dragon / @M__Houser | 2026-11-10 | 257 · 2,665 · 393K | 11-13 "이번 주 출시" → 11-21 "아직 라이브 아님" | critic loop 규모 주장. Tesana·Tripo 추천 코드가 반복되는 홍보성 | [X](https://x.com/M__Houser/status/2120253236309569696), [11-21](https://x.com/M__Houser/status/2124153573718307003) |
| Kun-Zhi-Line / @Grummz | 2026-11-10 | 좋아요 1,751 | 데스크톱 빌드, 다운로드 링크 미확인 | [벤더] 자체 엔진 홍보 데모 | [X](https://x.com/Grummz/status/2120255060957659498) |
| 일섬 / @OhChadol (한국) | 2026-11-15경 | 미집계 | 데모 완성 글은 있으나 링크 미확인 | "AI slop 티를 없애는 방법" 글. 모션 처방 | [X](https://x.com/OhChadol/status/2121831462974685633) |
| After the Wind / @afterthewinddev | 2026-10-22~23 | 미확인 | 첫 플레이테스트 전 | Godot, 다중 에이전트 | [X](https://x.com/afterthewinddev/status/2113646187844891110) |

기준에서 뺀 것도 밝혀 둔다. 3인 팀인 "A: Alice, the Gathering"(4일·70억 토큰·이미지 1,603장·3D 모델 119개, [X, 2026-11-15경](https://x.com/Stefan_3D_AI/status/2122228612913131938)), 기존 게임 포팅·팬게임(@levelsio의 Battlefield 1942 웹 포트, [X, 2026-11-02](https://x.com/levelsio/status/2117374984192512391)), AI 비중이 약 30%라고 밝힌 Solitaire: Kingdom in Chains([X](https://x.com/bigbropatchwork/status/2114371892664479751)), 그리고 [벤더] 시연인 Meshy의 "한 번의 채팅으로 만든 슈터, 총 80달러 이상, 약 2시간에 첫 플레이"([X](https://x.com/MeshyAI/status/2120513250446217725))와 Higgsfield의 "4시간에 만든 AAA 게임"([X](https://x.com/higgsfield_ai/status/2119926932343324795))은 사례로 세지 않았다. 스레드를 열지 못해 플레이 여부를 모르는 후보도 있다(@Rubzem의 SF FPS [11-20](https://x.com/Rubzem/status/2123816232109719894), @ChrisGPT 수중 생존 [11-18](https://x.com/ChrisGPT/status/2122866766590173419), @chongdashu Unreal 5.9 피클볼 [11-10](https://x.com/chongdashu/status/2120154573356793883), @nazimadakli National Xenographic [11-15](https://x.com/nazimadakli/status/2122100333099016436) 등).

## 제작자들은 생성 도구보다 검증 장치를 설명했다

게임별로 공개된 스택과 단계, 스스로 인정한 한계를 정리한다. 별도 표기가 없으면 전부 [1차]·[자가 보고]다.

**Sumiro (@xikhar).** 스택은 Opus 5.5 + Flux 3 Max + GPT Image + Tripo + Blender + Three.js다. 순서는 다음과 같다. Flux 3 Max(fal)로 영상 한 편을 만들어 룩·월드·캐릭터 전체의 기준으로 삼는다. 영상 스크린샷을 보고 Blender에서 에셋을 다시 만들어 Three.js에 배치하며, Claude Code의 dynamic workflows로 에이전트가 병렬 제작·검증한다. 캐릭터는 GPT Image로 4면도를 만들어 Tripo로 3D화하고 Opus가 천 물리와 애니메이션을 붙인다. 더 만들기 전에 프로토타입을 플레이해 확인하고, 레벨마다 컨셉아트를 최대 8장 만든 뒤 "플레이 → 버그 보고 → 에이전트 수정"을 반복한다. 모델 설정은 Opus 5.5 high effort + ultracode였고 비용·토큰은 밝히지 않았다([스레드, 2026-11-04](https://x.com/xikhar/status/2117776295534997818), [기준 영상 단계](https://x.com/xikhar/status/2117776297913106657)). 본인이 인정한 한계는 세 가지다. 데모 영상은 Claude가 녹화한 봇 플레이이고([X](https://x.com/xikhar/status/2117853548381982939)), 음악은 "Claude가 듣지 못해서" 나쁘며([X](https://x.com/xikhar/status/2117987456956141642)), 수익화 의도 없는 워크플로 실험이다. 답글 칭찬은 "영상 레퍼런스는 좋은 요령"([논평](https://x.com/kernel_trick/status/2117848079957463211))이었고, 비판은 "싸움이 0번인 사무라이 게임"(좋아요 510, [논평](https://x.com/CharleMarx/status/2117979092226105396))과 "생기 없고 지루하다"(좋아요 437, [논평](https://x.com/xsxsxsxsxsxsd/status/2118308200269136250))였다. 제작자는 후자에 "민감한 주제다. 조금 다르게 했어야 했다"고 답했다([X](https://x.com/xikhar/status/2118796739809517696)). 매체 AIGamer는 24시간 주장을 검증하지 못했다고 적었다([AIGamer, 게시일 미확인, 2차](https://www.aigamer.gg/games/sumiro)).

**one-shot FPS / Saltline (@felixrieseberg) [랩 직원].** 사람 피드백 없는 one-shot으로 Fable 5.2를 시험했고, 모델·사운드·텍스처를 전부 새로 만들었으며 API가 약 550달러, 출력 약 270만·입력 4.45억 토큰(대부분 캐시), 8시간이 들었다([X, 2026-11-09](https://x.com/felixrieseberg/status/2119925633564463609)). 프롬프트는 "FPS도 하나 만들어 줘. 미친 듯이 디테일하게, AAA와 견줄 비주얼로. 범위는 작게(아주 작은 레벨), 그 대신 인상적인 포토리얼 그래픽" 취지의 한 문단이고, `claude.md`는 비어 있었다고 한다([프롬프트 답글](https://x.com/felixrieseberg/status/2119927483994907024)). 핵심 기법은 "전부 코드"다. 텍스처와 모델이 모두 함수이고 이미지·3D 모델 파일이 없으며 Claude는 그린 것이 아니라 셰이더를 썼다([X, 2026-11-10](https://x.com/felixrieseberg/status/2120245629725409758)). 다만 매체 정리에 따르면 공개 링크의 버전은 one-shot 그대로가 아니라 무기 모델·사운드·게임플레이를 약 2시간 더 손본 것이고, 제작 영상에는 두 번째 Claude가 스크린샷을 채점하는 장면이 나온다([AIGamer, 게시일 미확인, 2차](https://www.aigamer.gg/games/saltline)). 답글은 "진짜 트리플 A 퀄리티"([논평](https://x.com/jarrodwatts/status/2119928453097255344))와 "슬롯머신에 500달러를 내고 형편없는 Half-Life 2 모드를 만든 것"([논평](https://x.com/liboar/status/2119932743488348386))으로 갈렸다. 가장 유용한 관찰은 "사람 적을 넣지 않은 게 영리하다. 모델의 약점이 드러나는 곳"이라는 지적이다([논평](https://x.com/NilesSankey/status/2119939493121950034)). HN에서도 답글이 가장 많이 달린 댓글은 혹평이었다([HN, 2026-11-10, 논평](https://news.ycombinator.com/item?id=50444850)). 모델 제작사 직원의 시연이므로 재현 가능성의 근거로는 약하게 다뤄야 한다.

**雾锁山门 / guizang-game-skill (@op7418).** Fable 5.2가 반나절에 모델·장면·동작 설계·최적화를 맡아 30MB 단일 HTML로 묶었다([X, 2026-11-12](https://x.com/op7418/status/2120694045299327187)). 토큰은 45억이 아니라 4.5억이라고 본인이 정정했다([X](https://x.com/op7418/status/2120695897956995075)). 에이전트가 即梦(Jimeng) CLI로 설정화를 만들고 Tripo로 3D 모델과 리깅을 했으며 원본 100MB 이상을 30MB로 압축했다([X](https://x.com/op7418/status/2120694594409312403)). 본인이 "one-shot이 아니다. 여러 차례 수정시켰다"고 밝혔고, 그 과정에서 "요구 확인 → 도구 조사 → 자체 진행·점검·대조"를 하고 전투 기법·타격감·최적화 지식을 담은 스킬을 정리해 GitHub `op7418/guizang-game-skill`로 공개했다([X](https://x.com/op7418/status/2120695301204005060)). 스킬 README를 정리한 매체에 따르면 사람이 7회 플레이하며 회당 문제 5~10개를 평이한 말로 전달했고, 텍스트에서 바로 만든 3D 모델은 품질이 낮아 컨셉 이미지를 먼저 만드는 편이 훨씬 나았으며, 에이전트는 프레임 단위 스테핑·단계 건너뛰기 URL·F3 진단 패널·자체 스크린샷으로 검증했다([AIGamer, 게시일 미확인, 2차](https://www.aigamer.gg/games/mist-locked-gate)).

**Iron Curtain Call (@whaledevstudios).** 9-29 첫 커밋, 10-23 Steam 무료 데모, 4,558커밋이고 "코드는 거의 쓰지 않았다"고 한다([X, 2026-11-06](https://x.com/whaledevstudios/status/2118500903783141660)). 첫 커밋에 디자인 문서, 대사 스크립트, 스펙, 툰 렌더링 룩, Blender 키트가 들어 있었고 "에이전트는 쓴 것을 만든다. 그러니 글이 먼저"라는 원칙을 밝혔다. 에이전트 브리프 규칙은 "스스로 결정하라, 초록불을 위해 테스트를 약화하지 마라, 자기 영역에 머물러라, 생성된 씬이 아니라 생성기를 고쳐라"다. 에이전트마다 브랜치(git worktree)를 주고 코디네이터가 테스트 통과 후 병합하며, 폴리시 라운드 한 번에 약 17개를 동시에 돌렸다([X](https://x.com/whaledevstudios/status/2118500912729665687)). 데모 빌드는 자동 체크 193개를 통과했고, 그와 별개로 "매일 모든 빌드를 플레이하고 그 메모가 다음 브리프가 된다". 에셋은 Blender MCP로 컨셉 → 선택 → 모델링 후 일부를 손으로 정리하고, 대사는 본인이 쓰고 디렉팅해 ElevenLabs로 생성한다. 범위 공개가 정직하다. 11-01 기준 GDScript 274,688줄·924파일이지만 레벨, 무기 감각, 페이싱, 모든 디자인 결정은 본인 것이고 AI 도구는 음성, 아트 일부, 음악 큐 몇 개에 썼다. 매체 정리에는 Blender 모델을 "메시를 생성하는 Python 스크립트"로 만들어 스크립트 310개가 모델 807개를 생성했다는 개발자 주장이 있다([AIGamer, 게시일 미확인, 2차](https://www.aigamer.gg/news/iron-curtain-call-godot-ai-agents-pipeline)). 첫 커밋은 기간 이전이고 데모와 방법 스레드가 기간 내다.

**Fall Line (@BananaOfMercy).** "Claude Fable 5.2는 자전거를 느낄 수 없다. 나는 느낀다. 그래서 7일 동안 모든 빌드를 타고 무엇이 어색한지 말했다"가 출발점이다([X, 2026-11-18](https://x.com/BananaOfMercy/status/2123037856398733438)). 플레이의 모든 키 누름·뗌과 초당 10회의 자전거 상태를 기록하고, **자전거가 응답하지 않는 입력을 버그로 정의**했다. 게임플레이가 먼저, 그래픽이 나중이었고 기록된 입력을 재생해 로우폴리판과 현재판을 나란히 비교했다. 역할 분담은 Fable 5.2가 지휘, Opus 5.5가 대부분 구현, GPT Sol이 엔진 리뷰이며 7일간 약 1,520커밋, 기록 세션 59개, 에이전트 스레드 89개였다. 그래픽 개선은 "프롬프트 3개와 몇 시간"으로 오히려 쉬운 부분이었다고 한다. 답글의 평가는 "사람이 끼는 반복이야말로 대부분이 건너뛰고 슬롭을 내는 지점"이었다([논평](https://x.com/devpabs/status/2123321747462091000)).

**Small Magic / Oilpaint (@BlendiByl).** Small Magic은 주문 7개, 부술 수 있는 물리 조각 약 1,800개, 3D 모델과 텍스처 0개로 전부 코드이며 오픈소스다([X, 2026-11-14](https://x.com/BlendiByl/status/2121594536153718972)). Oilpaint는 프레임마다 약 150만 붓 터치를 브라우저에서 200fps로 그린다고 했으나 "4090을 쓴다"고 보정했고([X](https://x.com/BlendiByl/status/2120404667922522160)), 게임플레이가 "돌아다니며 풍경을 즐기는 정도"임을 스스로 인정했다([X](https://x.com/BlendiByl/status/2120343693706293494)). 프롬프트와 비용은 미공개다.

**Starry Night Rider, What the water keeps, MAAD Maxxing, dimension9.** Starry Night Rider는 "다른 일을 하면서 6~8시간"이라는 말 외에 방법 설명이 없고, 출시 당일 걷기 모드·극장 모드·컨트롤러 지원을 추가했다([X, 2026-11-10](https://x.com/ebbyamir/status/2120458786460819632)). What the water keeps는 트레일러 음악을 Fable 5.2가 CC0 악기 샘플로 작곡했고 게임 내 음악은 Suno v6라고만 밝혔다([X, 2026-11-09](https://x.com/kevin_t_ngo/status/2119880812254601655)). MAAD Maxxing 제작자는 비결이 프롬프트가 아니라 2년간 이전 게임 빌드의 교훈을 쌓은 약 5만 단어의 `skill.md`(미공개)라고 했고 오디오는 ElevenLabs다([X, 2026-11-11](https://x.com/Andrew_Blumson/status/2120812356942897514)). dimension9은 방 생성 오류와 충돌을 고치는 correction loop를 두고 convex, fal serverless, cloudflare로 운영한다([X, 2026-11-06](https://x.com/apekshik/status/2118847014071120179)).

**Aiden's Revenge (Lex Toumbourou).** 조카의 손그림(영웅 5명, 보스 12명, 스토리 개요)을 기획서로 삼았다. 6월 버전은 "2~3분 이상 할 가치가 없었"고, Fable 5.2에 프롬프트 하나("현대판 Ninja Turtles 아케이드처럼", ChatGPT Images 2.5로 이미지, ElevenLabs로 효과음, 스캔 그림을 스프라이트시트로, 컨트롤러 4인, "Commit as you go")를 던지자 기존 코드 대부분을 버리고 다시 써 첫 실행에서 이미지 약 175장과 오디오 약 140개를 생성했다. 에이전트는 스스로 **게임을 플레이하는 봇을 작성해 headless 브라우저로 12스테이지를 돌리고 스크린샷을 검사**했다. 이후 아이들과 플레이테스트하며 특수기를 넣고 캐릭터를 18명으로 늘렸다. 최종 사용량은 Claude 약 600요청/2일(캐시 읽기 약 3.2억 토큰, 출력 100만), OpenAI 이미지 약 500장, ElevenLabs 음악 11곡·효과음 약 100개·대사 90개이며 API가로 약 300달러 상당이다([notesbylex.com, HN 제출 2026-11-09, 1차](https://notesbylex.com/fable-5-2-one-shotted-my-nephews-dream-game); [HN](https://news.ycombinator.com/item?id=50433659)). HN의 가장 구체적인 비판은 주인공 걷기 사이클 8프레임이 서로 일관되지 않는다는 것이었다(같은 HN 스레드, 논평). 첫 버전과 구상은 기간 이전이다.

**@MengTo의 Dark Souls풍 게임 (플레이 불가, 방법론 근거).** 스택은 Claude Code의 Fable 5.2 + Opus 5.5, Seedream 5.0 Pro, Tripo 3D, 빌드 단계 없는 Three.js다([스레드, 2026-11-15](https://x.com/MengTo/status/2121896633848017145)). 첫 단계는 Fable 5.2에 프롬프트 하나와 스킬 셋(@anshuc의 dream-loop, 본인의 workflow-score-to-target, design-action-combat)을 주는 것이었고 6시간·프롬프트 12개 뒤에 플레이 가능한 레벨과 보스가 나왔다. Fable 5.2가 조명·이펙트·캐릭터·소품·UI·사운드 영역마다 Opus 5.5 사이드 스레드를 최대 9개까지 조율하고 각 스레드가 자기 파일을 소유한다([X](https://x.com/MengTo/status/2121896696108200213)). 모델은 Seedream이 회색 배경의 엄격한 A-포즈 컨셉을 그리고 Tripo가 GLB로 바꾼 29개가 들어갔으며, 리깅 없이 나오므로 **에이전트가 리그와 애니메이션을 코드로 썼다**([X](https://x.com/MengTo/status/2121896705679638593)). dream loop는 게임 스크린샷을 Seedream이 "카메라·프레이밍·레이아웃·포즈는 정확히 같고 렌더링만 더 좋은" 그림으로 다시 그려 목표로 삼고 에이전트가 그것을 쫓는 방식이다([X](https://x.com/MengTo/status/2121896725501919348)). 블라인드 심사는 모든 변경마다 같은 카메라의 4K 전후 샷을 찍고, 새 심사 에이전트가 X·Y로 섞인 두 장을 보며, 이기거나 비긴 변경만 남긴다. 전체 라운드는 심사 2명과 10점 루브릭을 쓰고 낮은 점수를 채택하며 목표는 9점이다([X](https://x.com/MengTo/status/2121896794456228186)). 실제 지시문은 "10점 중 8점이 될 때까지 계속", "항상 전후 스크린샷을, 애니메이션은 전후 영상을 달라"였다. 본인 평가는 냉정하다. 영상은 스크립트된 봇이고 모든 장면이 연출이며, 엄격한 심사는 여전히 대부분을 5~6점으로 매기고, 로딩은 10초가 넘고, 걷기는 네 번 반려됐다([X](https://x.com/MengTo/status/2121896852497039431)). 걷기와 달리기가 프롬프트를 가장 많이 먹었고([X](https://x.com/MengTo/status/2121898061970706465)), 에이전트는 절차적 합성음으로 하는 사운드 디자인에 형편없다고 했다([X](https://x.com/MengTo/status/2121901329803362378)). 바위·항아리 등은 Poly Haven CC0 스캔이라 전부 AI 생성은 아니다. 답글 비판은 "근접 전투 게임에 히트스턴이 없는 건 나쁜 설계"였다([논평](https://x.com/OG_Tibbs/status/2121937468689715583)). 공유물은 github.com/MengTo/Skills, github.com/achimala/dream-loop 등이며 본인 제품 링크가 섞여 있다.

**AOD (@M__Houser, 플레이 불가·홍보성).** Fable 5.2와 Opus 5.5, Tesana, Three.js, Tripo, Blender로 12x12km 오픈월드를 만든다고 하며 210억 토큰 이상을 썼다고 주장한다([스레드, 2026-11-10](https://x.com/M__Houser/status/2120253236309569696)). 모든 랜드마크를 먼저 그림으로 그렸고([X](https://x.com/M__Houser/status/2120374257914114515)), Tripo 출력은 정리 없이 썼으며, Claude가 Blender에서 공유 스켈레톤 하나와 체중별로 리타이밍한 모캡 라이브러리로 리깅했고, 사운드는 전부 fal 경유 ElevenLabs(음성 544줄, 효과음 772개, 음악 37곡)라고 한다. "비법은 critic loop"로 매 라운드 같은 카메라 샷을 블라인드 비평 에이전트에게 보이며 25라운드·스크린샷 19,347장을 돌렸다고 썼다([X](https://x.com/M__Houser/status/2120253576404775337)). 빌드가 없고 답글에 "복붙 광고"라는 지적([논평](https://x.com/oldaveragegame/status/2124188434126250453))이 있어 수치는 검증 불가 주장으로만 다룬다. 방법의 구조가 MengTo와 독립적으로 겹친다는 점만 근거로 쓴다.

**일섬 (@OhChadol, 플레이 불가).** 한국 개발자의 X Article은 AI slop의 핵심을 "에셋, 모션, 시각적 피드백" 셋으로 꼽고, 모션에서는 "무게감, 관성력, 개연성 있는 행동, 가만히 있지 않고 살아있는 듯한 움직임"이 핵심이며 Opus와 Fable 모두 무게감과 힘을 모으는 동작을 제대로 못 한다고 썼다([X, 2026-11-15경](https://x.com/OhChadol/status/2121831462974685633)). 답글에서 다른 개발자가 Seedance 2.5로 영상을 뽑은 뒤 Cascadeur로 키프레임 보간을 한다고 하자 "같은 방식, 이게 그나마 제일 퀄리티가 좋다"고 답했다. 비용은 "Claude 200달러짜리 2개를 쓰는데도 토큰이 너무 많이 든다"였다([X](https://x.com/OhChadol/status/2122563289611972970)). Article 본문은 약 2,500자까지만 읽혔다.

방법을 가장 구체적으로 쓴 세 사람(MengTo, whaledevstudios, BananaOfMercy)이 공통으로 설명한 것은 도구가 아니라 검증 장치다. 그리고 "one-shot"을 내세운 작품도 스레드 안에서는 다단계였다고 밝힌다(op7418의 여러 차례 수정, Grummz의 2단계, Rubzem의 "여러 프롬프트", 공개 빌드를 2시간 손본 Felix). Grummz는 Felix의 프롬프트를 그대로 써서 2.9시간·토큰 30% 절감을 주장하면서, 프롬프트에 없던 드론 적과 매우 비슷한 UI가 똑같이 나왔다고 관찰했다([X, 2026-11-10, 벤더](https://x.com/Grummz/status/2120255060957659498)). **모델의 기본값에 맡기면 결과가 수렴한다**는 뜻이고, 이것이 룩을 먼저 고정해야 하는 이유다.

## 겹쳐 보면 '룩 고정 → 생성 → 블라인드 심사 → 사람 플레이' 파이프라인이 나온다

```
[0] 범위 결정 ── 작은 레벨 / 인물 없는 풍경·추상 / 고정 카메라 중 무엇으로 약점을 피할지 먼저 정한다
        │
[1] 룩 고정 ──── 기준 영상 1편(Sumiro) 또는 컨셉 페인팅(AOD) 또는 툰 렌더 룩 + Blender 키트(Iron Curtain Call)
        │
[2] 글 먼저 ──── 디자인 문서·스펙·대사, 에이전트 브리프 규칙(테스트 약화 금지, 생성기를 고쳐라), 누적 skill.md
        │
[3] 그레이박스 ─ 조작감부터. 입력+상태 기록, "응답 없는 입력 = 버그" (Fall Line)  ◄── 사람이 매 빌드 플레이
        │
[4] 에셋 ───┬─ A. 코드 생성: 모델·텍스처·사운드를 함수와 셰이더로 (Felix FPS, Small Magic, MAAD Maxxing)
            └─ B. 이미지→3D: A-포즈 컨셉(Seedream/GPT Image) → Tripo GLB → 코드 리그 또는 Blender 공유 스켈레톤
        │
[5] 병렬화 ──── 지휘 모델 1 + 영역별 스레드(조명·이펙트·캐릭터·소품·UI·사운드), 파일 소유권·worktree, 테스트 후 병합
        │
[6] 심사 루프 ┌─ 같은 카메라의 전/후 4K 샷 → 섞어서 새 심사 에이전트에게 → 승·무만 유지 → 목표 점수까지 반복
              └─ dream loop: 현재 스크린샷을 이미지 모델이 "같은 구도, 더 좋은 렌더"로 다시 그려 목표 갱신
        │
[7] 사람 플레이 ─ 회당 문제 5~10개를 평이한 말로 전달(7회, 雾锁山门) / 매일 플레이 메모 = 다음 브리프
        │
[8] 공개 ────── 브라우저 링크를 본문·첫 답글에, AI가 한 것과 내가 한 것을 나눠 밝힘, 봇 녹화 영상이면 그렇다고 명시
```

| 단계 | 겹치는 방법 | 근거 사례(게시일) | 한계·주의 |
|---|---|---|---|
| 룩 고정 | 영상 1편을 룩·월드·캐릭터의 단일 기준으로, 또는 랜드마크를 먼저 그림으로 | [Sumiro](https://x.com/xikhar/status/2117776297913106657)(11-04), [AOD](https://x.com/M__Houser/status/2120374257914114515)(11-10), [MengTo](https://x.com/MengTo/status/2121896725501919348)(11-15) | 고정하지 않으면 드론 적·비슷한 UI로 수렴([Grummz](https://x.com/Grummz/status/2120255060957659498), 11-10) |
| 기획 | 첫 커밋에 디자인 문서·스펙·룩. 또는 브레인스토밍 → `SPEC.md`. 또는 한 줄 프롬프트로 시작해 단계적으로 키움 | [Iron Curtain Call](https://x.com/whaledevstudios/status/2118500903783141660)(11-06), [Willison](https://simonwillison.net/2026/Oct/28/vibe-game-development/)(10-28) | Willison은 스펙 기반으로 이틀·수백만 토큰을 쓴 게임보다 단순 반복으로 키운 Battle Drones가 낫다고 자평 |
| 코딩 에이전트 | Claude Code에서 Fable 5.2 지휘 + Opus 5.5 구현, 다른 모델이 리뷰. 9~17개 병렬, 파일 소유권 또는 worktree | [MengTo](https://x.com/MengTo/status/2121896696108200213), [whaledevstudios](https://x.com/whaledevstudios/status/2118500912729665687), [Fall Line](https://x.com/BananaOfMercy/status/2123037856398733438)(11-18) | 잼 devlog에는 같은 파일 동시 편집과 사용 한도로 병렬을 포기한 사례가 있음([SkyCut](https://d-kol.itch.io/skycut/devlog/1782355/2026-epic-ai-megajam), [Forest Barrier](https://etherealexperiences.itch.io/forest-barrier/devlog/1781901/2026-epic-ai-megajam-devlog), 11-15경) |
| 엔진 | 플레이 가능 상위작은 Three.js·단일 HTML·Claude artifact. 엔진 통합은 Godot(Steam 데모) 한 건 | 위 표 전체 | Unreal 5.9 내장 MCP는 Experimental([Epic 문서, 게시일 미표기](https://dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor)). 참가자 호평([논평, 11-12경](https://x.com/BrentCaulfield/status/2120693254391836878))과 "거의 쓸모없다"는 HN 실무자 평([HN, 11-20](https://news.ycombinator.com/item?id=50573681))이 엇갈림 |
| 3D 에셋 | 컨셉 이미지(4면도 또는 A-포즈) → Tripo → GLB. 텍스트에서 바로 3D는 품질이 낮음 | Sumiro, MengTo, 雾锁山门([AIGamer](https://www.aigamer.gg/games/mist-locked-gate)), AOD | Tripo가 네 사례에 공통. AOD는 추천 코드 포함 |
| 리깅·애니메이션 | 에이전트가 코드로 리그·애니메이션 작성, 또는 Blender에서 공유 스켈레톤 + 모캡 리타이밍, 또는 영상 생성 → Cascadeur 키프레임 보간 | [MengTo](https://x.com/MengTo/status/2121896705679638593), [AOD](https://x.com/M__Houser/status/2120253236309569696), [OhChadol](https://x.com/OhChadol/status/2121831462974685633) | 가장 약한 고리. 걷기 4회 반려, 사람 모델은 "못생긴 인형"([논평](https://x.com/AmirMushich/status/2120472481068650708)) |
| 셰이더·코드 그래픽 | 모델·텍스처를 함수로, 에셋 파일 0개 | [Felix](https://x.com/felixrieseberg/status/2120245629725409758)(11-10), [Small Magic](https://x.com/BlendiByl/status/2121594536153718972)(11-14), [Willison](https://simonwillison.net/2026/Oct/28/vibe-game-development/) | 풍경·추상·기계 적에 강하고 인물에 약함 |
| 2D | 손그림 스캔 → 스프라이트시트, 이미지 모델 수백 장 | [Aiden's Revenge](https://notesbylex.com/fable-5-2-one-shotted-my-nephews-dream-game) | 걷기 프레임 간 불일치 지적. 1x 크기에서 halo·프린지·팔레트 점검([itch.io 포럼, 약 11-16, 논평·서비스 홍보](https://itch.io/t/7429405/a-simple-1x-check-for-ai-pixel-art-and-a-free-cleanup-of-one-sprite)) |
| 오디오 | 음성·효과음은 ElevenLabs, 음악은 Suno 또는 샘플 기반 작곡, 대사는 사람이 쓰고 디렉팅 | Iron Curtain Call, MAAD Maxxing, [What the water keeps](https://x.com/kevin_t_ngo/status/2119880812254601655), Aiden's Revenge | 에이전트는 듣지 못함. 절차적 합성음은 제작자들이 혹평 |
| 스크린샷 심사 | 동일 카메라 전후 샷의 블라인드 비교, 2인 심사·낮은 점수 채택 | [MengTo](https://x.com/MengTo/status/2121896794456228186), [AOD](https://x.com/M__Houser/status/2120253576404775337), Saltline(두 번째 Claude 채점, [AIGamer](https://www.aigamer.gg/games/saltline)) | 엄격한 심사는 여전히 5~6점. 화면은 올려도 재미는 못 잼 |
| 플레이테스트 | 사람이 매 빌드 플레이, 입력 기록 재생, 봇이 스테이지 완주 후 스크린샷 검사, 자동 체크 193개 | Fall Line, Iron Curtain Call, Aiden's Revenge, 雾锁山门 | 자동 통과와 재미는 별개. "A human verdict outranks every automated PASS"([IN FRAME devlog, 약 11-16](https://nirvanadlaw.itch.io/in-frame/devlog/1782101/in-frame-dev-log-four-days-one-rule-a-crew-of-ai-agents)) |

### 룩과 범위를 먼저 고르는 것이 품질의 절반이다

상위작이 슬롭과 구분되는 첫 이유는 생성 품질이 아니라 **AI가 잘하는 영역으로 범위를 접은 선택**이다. 2D·분위기 게임이 빠른 이유를 한 제작자는 "분위기, 페이싱, 아름다움이 중심인 게임은 더 빨리 도달한다"고 설명했다([X, 2026-11-15경, 1차](https://x.com/Rubzem/status/2122215138963173888)). 같은 결론을 Sandro Maglione은 실패에서 얻었다. Genshin풍 애니메 캐릭터를 3D화하려고 이틀간 여러 방법을 시도했지만 매번 실패했고, 게임이 아니라 스타일을 바꿨다. "게임을 고르는 것이 곧 병목을 고르는 것이며 AI가 못 하는 파이프라인 단계는 전부 당신의 풀타임 업무가 된다"([sandromaglione.com, 2026-11-09 개정, 1차; 개발 자체는 10월 초중순으로 기간 직전](https://www.sandromaglione.com/articles/indie-game-development-with-ai)). 그의 대안 경로는 ChatGPT로 2D 디자인 → low-poly 버전 → 뷰별 분해도 → Blender MCP 모델링으로 캐릭터당 약 20분이었다. 기준 영상이나 컨셉 페인팅은 이 선택을 에이전트가 볼 수 있는 형태로 못 박는 장치다.

### 에셋은 두 갈래이고, 갈림길은 '인물이 필요한가'다

코드 생성 경로는 인물이 없을 때 가장 강하다. Felix FPS, Small Magic, MAAD Maxxing, Willison의 게임들은 에셋 파일 없이 셰이더와 절차적 지오메트리로 화면을 만들었고, Willison은 "three.js를 쓰라고 하면 잘 된다. Claude는 이미지 생성 모델이 없지만 풀컬러 3D 모델을 코드로 만든다"고 적었다([simonwillison.net, 2026-10-28](https://simonwillison.net/2026/Oct/28/vibe-game-development/)). 인물 애니메이션이 필요한 장르는 이미지 → 3D → 리깅 경로로 넘어가고 품질 불만이 여기에 몰린다. 벤더들도 이 구간을 손보고 있다. Meshy는 리깅에 `skeleton_template`(`mixamo`, `ue5_mannequin`)과 손가락 본(2026-11-10), 네발 리그(2026-11-18)를 추가했고([Meshy API changelog, 공식](https://docs.meshy.ai/en/api/changelog)), Rodin은 커스텀 스켈레톤을 텍스트로 기술하는 리깅을 냈다([Hyper3D changelog, 2026-11-03, 공식](https://hyper3d.ai/changelog/type/feature)). 이 발표들의 품질 수치는 벤더 자체 주장이고, 기간 내 상위작 중 이 기능을 썼다고 밝힌 사례는 없다. 자동화 스크립트를 짠다면 Meshy T1이 2026-11-30부터 모든 요청에 `400`을 돌려준다는 은퇴 일정도 함께 봐야 한다(같은 changelog).

### 심사 루프는 화면을 올리고, 사람 플레이는 감각을 올린다

두 검증은 대체재가 아니다. 블라인드 심사는 "같은 카메라, 섞인 전후, 새 심사자"라는 세 조건으로 에이전트의 자기 칭찬을 막고 시각 품질을 단조 증가시킨다. 그러나 이 루프를 가장 엄격하게 돌린 MengTo의 게임에서 답글이 지적한 것은 히트스턴 부재였고 걷기는 네 번 반려됐다. 감각은 사람 쪽에서만 올라갔다. Fall Line은 입력 기록으로 "느낌"을 재현 가능한 버그 리포트로 바꿨고, Iron Curtain Call은 매일의 플레이 메모를 다음 브리프로 삼았으며, AOD 제작자조차 "마지막 마법은 플레이테스트와 반복"이라고 인정했다. 봇의 한계는 Maglione의 기록이 선명하다. 첫날부터 봇이 경제를 플레이했지만 지배 전략을 하나도 잡지 못했고, 에이전트에게 경제 수학 모델을 테스트로 쓰게 하자 깨진 규칙 12개가 드러났다(같은 글). 답글의 현실적 평가도 같은 방향이다. "AI는 프로토타입의 80%까지 데려다준다. 실제로 기분 좋게 만드는 마지막 20%가 나머지 전부보다 오래 걸린다"([논평](https://x.com/VahnAeris/status/2120409915432869915)), "Fable로 12레벨을 약 8시간에 만들었지만 정말 좋게 만드는 데 6~8주가 더 걸리고 있다"([논평](https://x.com/mikeswarms/status/2122091859891875998)).

### 시간과 토큰: 하루짜리는 수백 달러, 일주일짜리는 구독 여러 개

| 사례 | 시간 | 토큰·비용 | 성격 | 출처 |
|---|---|---|---|---|
| Felix FPS | 8시간(+약 2시간 손질, 2차) | 출력 2.7M·입력 445M(캐시 다수), API가 약 550달러 | [랩 직원]·[자가 보고] | [X](https://x.com/felixrieseberg/status/2119925633564463609) |
| Aiden's Revenge | 약 2일 | Claude 약 600요청, API가 약 300달러 상당 + 이미지 500장 + ElevenLabs | [자가 보고] | [블로그](https://notesbylex.com/fable-5-2-one-shotted-my-nephews-dream-game) |
| 雾锁山门 | 반나절 + 플레이테스트 7회 | 4.5억 토큰 | [자가 보고] | [X](https://x.com/op7418/status/2120695897956995075) |
| Sumiro | 24시간 | 미공개 | [자가 보고], 매체 미검증 | [X](https://x.com/xikhar/status/2117776295534997818) |
| Fall Line | 7일 | 약 1,520커밋, 세션 59개, 스레드 89개. 비용 미공개 | [자가 보고] | [X](https://x.com/BananaOfMercy/status/2123037856398733438) |
| MengTo(플레이 불가) | 3일(첫 6시간에 레벨+보스) | 미공개 | [자가 보고] | [X](https://x.com/MengTo/status/2121896633848017145) |
| Iron Curtain Call | 약 3.5주 만에 데모, 이후 지속 | 4,558커밋, 비용 미공개 | [자가 보고] | [X](https://x.com/whaledevstudios/status/2118500903783141660) |
| Kun-Zhi-Line | 2.9시간 | API가 환산 약 280달러 | [벤더]·추정 환산 | [X](https://x.com/Grummz/status/2120255060957659498) |
| AOD(플레이 불가) | 미상 | 210억 토큰 이상 | 홍보성·검증 불가 | [X](https://x.com/M__Houser/status/2120253236309569696) |
| 일섬(플레이 불가) | 미상 | Claude 200달러 요금제 2개로도 부족 | [자가 보고] | [X](https://x.com/OhChadol/status/2122563289611972970) |
| Willison 4종 | 각 본인 작업 4시간 이하(에이전트 단독 실행 별도) | Quarter Sun Cove는 수백만 토큰·약 이틀 | [자가 보고] | [블로그](https://simonwillison.net/2026/Oct/28/vibe-game-development/) |

숫자를 밝힌 사례가 적고 전부 자가 보고여서 평균을 낼 수 없다. 읽을 수 있는 것은 구간이다. 범위를 접은 하루짜리 브라우저 3D는 API가로 수백 달러, 일주일 이상 조작감을 다듬는 프로젝트는 월 200달러급 구독 한두 개가 실질 예산이다.

참고로, 유료 흥행작 Slotbound의 스택은 이 파이프라인과 전혀 다르다. 개발자가 출연한 인터뷰 자막에 따르면 에디터 없는 `LÖVE`, 저가 `Codex` 구독 2개, 나노바나나 이미지, ElevenLabs 효과음과 구매 에셋, 사람 작곡가의 음악으로 약 1년을 반복했다([조코딩 인터뷰, 2026-11-18, 1차](https://www.youtube.com/watch?v=6_cqj13abyI)). 기간 내 본인 X 게시물 14건에는 스택 언급이 없었고, 11-20에 Steam의 AI 공시는 AI 생성 콘텐츠 대상이지 코딩 보조 도구가 아니라고 해명했다([X, 2026-11-20](https://x.com/OptimaArchGames/status/2123781531718308275)). 이 보고서는 품질과 방법을 다루므로 2차 참고로만 둔다. 시사점은 하나다. 긴 반복과 사람 플레이라는 축은 스택이 달라도 같다.

## 답글은 분위기를 칭찬하고, 게임플레이 부재와 봇 영상을 겨눴다

칭찬은 분위기·아트 스타일·"브라우저와 폰에서 바로 돈다"는 접근성에 몰리고, 비판은 게임플레이 부재, 어색한 애니메이션, 하루짜리 데모의 지속성, 봇이 찍은 연출 영상, 홍보성 서사에 몰린다. 아래 답글 가운데 어느 스레드에 달린 것인지 조사 노트가 명시하지 않은 것은 귀속하지 않았다.

| 구분 | 내용(근사 인용·요지) | 출처 [논평] |
|---|---|---|
| 칭찬: 분위기 | 모바일로 조금 해 봤는데 매우 차분하다 | [X](https://x.com/doganuraldesign/status/2120389801346240870) |
| 칭찬: 접근성 | 아이폰에서 울트라 설정으로 돌아간다 | [X](https://x.com/grepmoney/status/2119997558332535054) |
| 칭찬: 방법 | 영상 레퍼런스는 좋은 요령 / 사람이 끼는 반복이 슬롭과의 차이 | [X](https://x.com/kernel_trick/status/2117848079957463211), [X](https://x.com/devpabs/status/2123321747462091000) |
| 비판: 게임플레이 없음 | "이런 글은 전부 에셋 몇 개 얹은 휑한 숲을 걷는 사람일 뿐" | [X](https://x.com/rblx_tyridge77/status/2120559110232195281) |
| 비판: 기술 결함 | 오브젝트 텍스처가 월드 공간에 붙어 있다 / 브라우저가 5번 죽었다 / 로딩 화면에서 멈춤 | [X](https://x.com/RopTamen/status/2118737618624237614), [X](https://x.com/DeRonin_/status/2120126722867871864), [X](https://x.com/CougarTape/status/2121614706335179158) |
| 비판: 지속성 | "이런 프로젝트는 24시간 이후로 발전하지 않는 것 같다. 쌓을 기반이 없어서" | [X](https://x.com/runbund/status/2118719253553848333) |
| 비판: 홍보 의심 | 플레이어 수 대비 평균 플레이 시간이 25분이라는 지적 | [X](https://x.com/Enigmaticatt/status/2124198492356956574) |
| 대회의 아이러니 | Epic AI MegaJam에서 가장 인기 있던 게임은 AI 없이 만들어졌다 | [X](https://x.com/KenneyNL/status/2122797754728812680) |

이 반응에서 공개 방식의 요령이 나온다. 영상만 있고 링크가 없는 게시글의 품질 주장은 낮게 평가받고, 봇이 찍은 영상이면 제작자가 먼저 밝히는 편이 낫다(xikhar와 MengTo가 그렇게 했다). "AI가 한 것과 내가 한 것"을 나눠 쓴 Iron Curtain Call 스레드에서는 적대적 답글이 상위에 보이지 않았는데, 상위 답글만 본 것이므로 단정할 수 없다 [추정]. 반AI 답글이 수백 좋아요를 받는 환경이라는 점은 전제로 깔아야 한다. 답글 정서의 비율은 스레드당 상위 6~16개만 읽은 표본이다.

## 확인하지 못한 것: 직접 플레이, Reddit, 도구별 X 검색, AAA급 범위

**직접 플레이와 링크.** 어떤 게임도 플레이하지 않았고 영상도 재생하지 않았다(스틸 1장만 봄). 플레이 링크는 한 건도 열어 보지 않았으므로 현재 접속 가능 여부, 실제 조작감, 완성도는 미검증이다. Felix FPS의 artifact URL은 게시글에서 잘려 전체 주소를 확보하지 못했고, "Saltline"이라는 이름은 X 열람 본문이 아니라 매체 표기다. 이 보고서의 "고퀄"은 게시물·수치·답글에서 관찰되는 품질이다.

**Reddit.** 어떤 경로로도 원문에 접근하지 못했다. r/aigamedev, r/gamedev 등의 기간 내 글은 하나도 확인하지 못했고, Godot·Unity·Unreal 실무자의 기록은 그쪽에 더 많을 가능성이 있다.

**실행하지 못한 X 검색.** 로그인된 브라우저에서 영어 기본 쿼리와 "playable/play it" 쿼리, 잼 쿼리, 한·일·중 쿼리는 실행했다. 엔진·도구별 단일 키워드(three.js, WebGPU, Godot, Unity, Unreal, MCP, Blender, Meshy, Tripo, Hunyuan3D, Rodin, shader, sprite, "pixel art", Suno, ElevenLabs, "no human" 등)와 `filter:videos`·`filter:links` 변형은 돌리지 못했다. 따라서 Godot·Unity·Unreal 기반이나 2D 픽셀아트 계열의 플레이 가능작은 누락됐을 가능성이 크다. 검색은 X의 Top 정렬과 로그인 계정 개인화의 영향을 받고, 인용 게시글 탭은 열지 않았다. 스레드를 연 것은 18개뿐이며, 한·일·중 후보 단서(@csodafactory, @Konoyo_Wowari, @puglet_dev)와 Nenly의 「群侠传：幸存者」 회고 Article([X, 2026-10-28](https://x.com/Nenlyonis/status/2115414690092253209)), Octoberry가 소개한 "Opus 5.5 + Godot 6주" 게임의 원 게시글([논평](https://x.com/Octoberry/status/2113653280429478043))은 읽지 못했다. whaledevstudios의 브리프 발췌와 M__Houser의 critic loop 프롬프트는 이미지라 전문을 확보하지 못했다.

**AAA급 범위의 플레이 가능작 부재.** AAA급이라고 불린 플레이 가능작은 아주 작은 레벨의 Felix FPS 정도이고, 그것도 모델 제작사 직원의 시연이다. 규모가 큰 3D(AOD, MengTo)는 공개 빌드가 없으며, 가장 엄격한 자기 심사가 5~6점을 준다. "AI가 AAA를 만들 수준은 아니다"라는 답글([논평](https://x.com/OG_Tibbs/status/2121937468689715583))과 HN의 실무자 보고(AAA급 디스플레이스먼트 효과 하나에 Claude max 한 달치 토큰을 쓰고도 실패, [HN, 2026-11-20](https://news.ycombinator.com/item?id=50573681))가 같은 방향을 가리킨다. 넓은 범위, 높은 충실도, 공개 플레이를 동시에 만족한 1인 AI 제작물은 이번 조사에서 한 건도 찾지 못했다.

**소속과 이해관계.** @kevin_t_ngo의 소속, @BlendiByl과 patch.gg의 관계는 확인하지 못했다. @Rubzem과 @M__Houser는 Tesana와 Tripo 추천 코드를 반복해 홍보성으로 취급했다.

**배경으로만 쓴 기간 외 자료.** @icreatelife의 한자 학습 코지 게임(Opus 5.5, "6달러")은 2026-10-21 게시로 기간 하루 전이다([X](https://x.com/icreatelife/status/2113022598368067751)). After the Wind의 프로세스 글(2026-10-20, [X](https://x.com/afterthewinddev/status/2112557587254382604))과 제3자가 전한 수치(Claude Code 385억·Codex 29억 토큰, 동시 에이전트 최대 8개, [X, 2026-10-19, 논평](https://x.com/Stefan_3D_AI/status/2112130671015874614))도 기간 직전이다. Iron Curtain Call의 첫 커밋(09-29), Aiden's Revenge의 6월 버전, Battle Drones의 7월 2D 버전, Maglione 두 게임의 개발 시점(10월 초중순)도 기간 밖이며, 이 프로젝트들의 "단기간 제작" 수치는 그 선행 작업 위에 얹힌 것이다.

## Conclusion

이번 달 자료에서 슬롭과 고퀄을 가른 것은 모델이나 도구 목록이 아니라 **목표를 에이전트가 볼 수 있는 형태로 고정했는가, 그리고 결과를 에이전트 자신이 아닌 누군가가 판정했는가**였다. 목표는 영상 한 편이나 "같은 구도의 더 좋은 렌더"로, 판정은 맥락 없는 심사 에이전트와 매일 플레이하는 사람으로 구현됐다. 지금 따라 한다면 순서는 분명하다. 인물 애니메이션과 넓은 월드를 피하는 범위를 고르고, 기준 화면을 먼저 만들고, 조작감을 그레이박스에서 사람이 확정한 뒤, 에셋 경로(코드 생성 또는 컨셉 이미지 → Tripo → 코드 리그)를 붙이고, 고정 카메라 전후 샷의 블라인드 심사를 돌린다. 사운드와 걷기 애니메이션은 현재 사람 손이나 별도 도구(음성·효과음 생성기, 영상 → 키프레임 보간)가 필요한 구간으로 예산에 넣어야 한다.

판단을 바꿀 신호는 세 가지다. MengTo와 AOD가 실제 빌드를 공개했을 때 플레이어가 영상과 같은 품질을 보고하는지, Fall Line처럼 입력 기록 기반으로 감각을 다듬은 프로젝트가 오픈소스로 나와 재현되는지, 그리고 이번에 돌리지 못한 도구별 검색과 Reddit에서 엔진 기반 플레이 가능작이 나오는지다. 그 전까지 "AI 풀 제작 고퀄"은 작은 범위의 브라우저 3D와 코드 생성 그래픽에서만 증거가 있고, 그 증거도 직접 플레이가 아닌 관찰에 기대고 있다.
