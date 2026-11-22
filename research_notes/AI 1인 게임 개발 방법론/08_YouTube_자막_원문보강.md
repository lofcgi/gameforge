# YouTube 자막 원문 보강 — AI 1인 게임 개발자들이 실제로 말한 워크플로 (2026-10-22 ~ 2026-11-22)

> 조사일: 2026-11-22. 방법: `yt-dlp 2026.03.17`로 메타데이터(`--dump-json`)와 자막(`--write-auto-subs --write-subs`)을 직접 내려받아 읽음. 검색은 YouTube 검색의 "이번 달 + 조회수순" 필터로 15개 질의를 돌림(이 버전에서 `ytsearchdate`는 동작하지 않았음).
> 표기 규칙
> - **[개발자 발언]** = 영상 속 개발자 본인의 말. **[진행자/해설자]** = 인터뷰어나 제3자 해설. **[메타데이터]** = 영상 설명란·YouTube/Steam 수치.
> - 타임스탬프는 자막을 30초 단위로 묶어 읽은 것이라 **해당 30초 구간의 시작 시각**이다(±30초 오차).
> - 조회수는 2026-11-22 수집 시점 값. 매출·판매량은 전부 **자가 보고(검증 안 됨)**.
> - 자동 생성 자막의 오인식이 의심되는 도구명·숫자는 `(자막: "…")`로 원문을 병기했다.
> - 원문 자막 텍스트는 `/private/tmp/claude-501/-Users-iyeonsang-Desktop-game/e8b95f8e-a207-4d0a-8285-e725e4467949/scratchpad/yt/` 에 `<영상ID>.txt`로 있음(임시 폴더라 재부팅 시 사라질 수 있음).

## 1. 슬롯바운드(Slotbound): 개발자 김민이 직접 말한 스택·작업 방식·수치

### Takeaway
개발자 본인 발언 기준 스택은 **`LÖVE`(LÖVE2D) + ChatGPT `Codex`(약 3만 원 요금제 2계정 번갈아) + Gemini 나노바나나 + "픽셀 스내퍼"(픽셀화 도구) + ElevenLabs/구매 에셋 효과음 + 사람 작곡가의 음악**이고, 출시 한 달 전에만 "200달러짜리"(자막상 "클라우드", 문맥상 Claude로 추정)를 추가했다. Cursor·VS Code Copilot·PixelLab은 인터뷰에 **한 번도 나오지 않으며**, 하네스·규칙 파일·LLM 위키 같은 고도화는 "할 줄 몰라서 안 했다"고 명시했다. 성패를 가른 것으로 본인이 꼽은 것은 도구가 아니라 "한눈에 보이는 재미"에 대한 집착, 재미없던 프로토타입을 갈아엎은 것, 데모와 100시간 이상 플레이어 5명의 피드백이다.

### Cited Findings

**영상 기본 정보 [메타데이터]**
- 조코딩 JoCoding, 「1인 혼자 만든 첫 게임으로 출시 3일만에 마케팅비 없이 8억 매출 낸 방법 | 슬롯바운드 개발자 김민님 인터뷰」, 업로드 2026-11-18, 조회수 322,650, 길이 39분 48초. 한국어 자막은 **자동 생성**(수동 자막 없음). 설명란 요약: "3만 원짜리 코덱스 2개, 에디터 없는 엔진 러브2D, 나노바나나로 만든 개발 환경", "출시 시점 위시리스트 14만, 마케팅비 0원으로 3일 만에 8억" — [YouTube](https://www.youtube.com/watch?v=6_cqj13abyI)
- 인터뷰 녹화 시점은 출시 3일 차(개발자: "아직까지 3일차니까") — [18:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=1080s). Steam API상 출시일은 2026-11-12, 정가 ₩12,000, 지원 언어 13개, 개발·배급 Optima Arch — [Steam appdetails API](https://store.steampowered.com/api/appdetails?appids=4459590&l=english)

**엔진 [개발자 발언]**
- "러브투디라는 엔진이 있는데 이게 발라트로라는 유명한 게임도 이 엔진을 썼어요. 근데 이 엔진은 에디터가 없는 엔진이에요. 그래서 그냥 AI한테 연결해 주고 … 결국 이걸 선택하게 된 게 그냥 에디터가 없어서." — [13:30~14:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=810s)
- 그 전에 Unity·Unreal을 설치해 배워 보려 했지만 "이게 뭐가 뭔지 모르겠더라고요"라며 포기했다고 말함 — [03:00~03:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=180s)

**코딩 에이전트 [개발자 발언]**
- "AI는 계속 바꿔가면서 많이 썼었는데 일단 그 이미지나 이런 건 제미나이를 중점적으로 많이 썼고요. 그리고 주로는 챗GPT 코덱스를 제일 많이 썼던 거 같아요. 대부분의 개발 기간 동안은 코덱스 그 3만 원짜리 있죠? 제가 … 돈이 없었으니까 그 3만 원짜리 두 개를 돌렸었어요." — [14:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=840s)
- "출시하기 한 한 달 남았을 때 개발 속도를 끌어 올려야겠다 해서 정말 큰 맘 먹고 클라우드 200달러짜리 질렀습니다 … 앞에 부분에서는 거의 두 개로 그냥 왔다 갔다 하면서 개발했었습니다." (자막: "클라우드 200달러짜리". 뒤에서 진행자가 "코덱스와 클라우드 코드 생으로 하고 계시니"라고 받으므로 Claude 200달러 요금제로 추정되나 자막만으로 확정 불가) — [14:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=870s), [37:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=2220s)
- 사용 형태: "그냥 그 코덱스 앱 있죠? 지금 그거랑 이 클라우드 앱 쓰고 있긴 한데 전에는 무슨 막 프롬프트 창같이 보여 가지고 … 그런 거 바로 그냥 꺼요. 뭔지 몰라서" — 터미널/CLI가 아니라 **데스크톱 앱**을 쓴다는 뜻으로 읽힘 — [34:00~34:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=2040s)
- 토큰이 떨어지면 쉬지 않고 음악·소리·SNS 글 작성 같은 다른 작업으로 넘어갔다고 말함 — [14:30~15:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=870s)

**하네스·컨텍스트 관리 [개발자 발언]**
- 진행자가 "어떤 하네스를 만드셨다거나 LLM 위키로 관리한다거나" 물었을 때: "저는 이 노드 같은 거 연결하고 이런 LLM 쓰고 이런 것도 못 해요, 사실. 할 줄 몰라요. 그래서 … 그냥 여러분들이 흔히 쓰시는 그런 챗GPT, 뭐 그냥 코덱스, 그리고 이미지나 이런 것도 그냥 거의 다 나노 바나나" / "오프라인 LLM 이런 복잡한 거 아무것도 없고 그냥 기존에 있는 일반 사용자들이 접근할 수 있는 그런 걸로만 만들었어요." — [33:30~34:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=2010s)
- 최초의 바이브 코딩 경험: "AI한테 W A S D로 움직이는 상자 하나 만들어 줘 했는데 … 제가 말한 대로 [움직였다]". 슬롯바운드 이전에는 "뚜렷한 결과를 낸 건 아예 없죠" — [03:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=210s), [05:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=300s)
- AI의 역할: "AI가 없었다면 못 했을 겁니다. AI랑 상의를 굉장히 많이 했어요. 브레인스토밍 같은 것도 아이디어 같은 것도" — [30:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=1800s)
- 정보원: 조코딩 주간 AI 뉴스 라이브를 약 1년간 매주 보며 "게임 개발에 활용할 만한 것들을 다 쫙 저장"해 뒀다고 말함 — [39:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=2340s)

**이미지 [개발자 발언]**
- 이미지는 "거의 다 나노 바나나". 진행자가 "구글 제미나이로 들어가서 나노 바나나"냐고 확인하자 "네 그거예요" — [34:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=2040s)
- "그나마 좀 고도화된 AI"로 꼽은 것: "픽셀 스내퍼라고 나노 바나나에서 나온 이미지를 실제 픽셀 이미지로 만들어 주는 게 있거든요" (자막: "픽셀 스내퍼", "나노 방화". 정확한 제품명 철자는 확인 못 함) — [36:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=2160s)
- Steam 상점의 AI 고지문: "various visual assets and promotional materials for Slotbound were created with the assistance of generative AI tools. All AI-generated content was reviewed, refined, and integrated by the developer…" — [Steam 상점 페이지](https://store.steampowered.com/app/4459590/?l=english)

**오디오 [개발자 발언]**
- 효과음: "일레븐 랩스 거기서 많이 가져왔고요. 그리고 에셋도 사서 좀 구매해서 활용했고요." — [34:30~35:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=2070s)
- 음악: 데모 전에 Reddit에서 예고편을 보고 먼저 연락한 아마추어 작곡가가 스테이지 음악 전부를 무료로 제작. 메인 메뉴 음악은 "저렴한" 구매 에셋 — [35:00~36:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=2100s)
- 진행자가 음악 생성 AI를 썼는지 묻자 "아니요. 스노우도 안 썼고요"(자막: "스노우". Suno로 추정) — [35:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=2130s)

**테스트·플레이테스트 [개발자 발언]**
- "출시하기 한 2, 3주 전에 데모를 플레이한 유저 중에 100시간을 넘긴 … 분들 한 다섯 분 정도만 풀 버전을 플레이할 수 있게 해드렸어요 … 그 피드백들을 기반으로 출시 하루 전날까지도 계속 고쳤어요." — [22:00~22:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=1320s)
- 지표 트래킹은 하지 않음: "그런 거는 따로 관리하진 않고 그냥 플레이어들이 피드백 주는 거를 하나하나 놓치지 않고" — [13:00~13:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=780s)
- 데모 피드백으로 "코어"(아이템) 시스템을 "아예 처음부터 다시 만들었"다고 말함. "게임 자체를 아예 바꿀 수준으로도 할 준비가 돼 있었어요" — [21:00~21:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=1260s)
- 자동화 테스트·유닛 테스트·CI에 대한 언급은 인터뷰 전체에 없음(자막 전문 확인) — [YouTube](https://www.youtube.com/watch?v=6_cqj13abyI)

**기간·일정 [개발자 발언, 일부 진행자]**
- 형(컴공 졸업, 게임 개발 경험자)이 "작년 중후반"에 바이브 코딩을 알려줬고 "작년 말쯤" 시작 — [03:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=180s)
- 원래 계획은 4개월. 2~3개월 뒤 나온 중간 버전이 "굉장히 재미가 없었"고 그때 "그냥 갈아 엎었어요 … 재밌을 때까지 만든다는 마인드" — [08:30~09:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=510s)
- Steam 페이지는 3월 오픈, 데모는 7월 10일 공개, 데모까지 "한 8개월 정도" — [11:00~11:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=660s), [15:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=900s)
- 데모 공개 당시 "제가 만들어 놓은 게 100%가 데모 버전"이었고 그것이 현재 게임의 20~30% 분량 — [11:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=660s)
- 총 기간은 진행자가 "약 1년 남짓"으로 소개, 개발자도 "1년 정도"라고 자기소개 **[진행자/개발자 둘 다]** — [00:30~01:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=30s)
- 큰 번아웃 두 번: (1) 초반 "게임이 게임으로 안 느껴질 때", (2) 큰 콘텐츠 분량을 선택한 뒤 약 일주일 개발 중단 — [32:00~33:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=1920s)

**사람이 한 일(기획·디자인) [개발자 발언]**
- 아이디어: Steam 게임 「CloverPit」(자막: "클로버 핏")을 하다가 "창 심볼 세 개에서 창병이 나와서 나를 위해 싸워 주면 재밌겠다"는 생각이 들었고, 찾아보니 그런 게임이 없었다 — [06:30~07:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=390s)
- 재미를 만든 설계 변경 세 가지로 희귀도 추가, 승급·전직, 퀘스트를 꼽음 — [10:00~10:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=600s)
- 가장 오래 고민한 것은 유닛이 서로 겹치지 않게 하는 것과 6개 스테이지마다 다른 재미(돌진형·후열 저격형 적, 자폭 적, 늪, 레인 분할)를 주는 것 — [30:00~31:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=1800s)
- 범위 결정: 작은 스케일안과 큰 스케일안 중 큰 쪽을 골랐고 "개발에 힘든 거 말고 플레이어들이 원하는 게 뭘까"를 기준으로 삼았다고 말함 — [29:00~30:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=1740s)
- 코드를 직접 작성했는지, 그림을 손으로 고쳤는지에 대한 구체 발언은 없음. 본인을 "비개발자"로 확인("네, 네, 맞습니다") — [00:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=30s)

**위시리스트·마케팅(비용 0원) [개발자 발언]**
- 3월 Steam 페이지 오픈 후 Reddit·Threads에 글을 썼지만 "거의 반응이 없었"고 위시리스트도 거의 없었음 — [11:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=690s)
- 7월 10일 저녁 데모 공개 후 "자고 일어났는데 400명이 플레이를 하고 있는 거예요 … 스팀 전체 데모 순위 2위까지" — [12:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=720s)
- 원인에 대한 본인 해석: "홍보는 아예 안 먹혔던 건데 그냥 스팀 알고리즘을 좀 탔던 거 같아요 … 인플루언서들이 이걸 그냥 알아서 플레이해주면서" — [12:00~12:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=720s)
- 알고리즘을 탄 이유로 든 것: "한 눈에 보이는 재미 … 문장만 들어도 머릿속에서 그려지는 재미"에 "집착" — [12:30~13:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=750s)
- 위시리스트 10만의 주원인: "데모가 진짜 그냥 메인". 데모를 끄고도 다음 희귀도·전직이 궁금하게 설계 — [19:00~20:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=1140s)
- "마케팅에는 비용을 아예 안 썼죠. 쓸 여유도 없고." 마케팅은 "인플루언서랑 릴스, 쇼츠 타면 끝"이라고 봄. 다만 "제가 직접 움직여서 되는 홍보는 사실 거의 없었어요" — 예고편 채널들에 보낸 메일은 아무도 올려주지 않음 — [16:30~17:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=990s)
- 구독자 약 20만 해외 유튜버(자막: "고조", 이름 불확실)의 체험판 영상이 조회수 80만 이상. 풍월량은 메일을 보낸 뒤 플레이했으나 그 때문인지는 모른다고 말함 — [25:00~26:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=1500s)
- Steam을 고른 이유: 모바일의 무료+인앱결제 방식을 좋아하지 않고 "돈을 딱 한 번 내고" 즐기는 문화가 Steam에 있어서 — [18:30~19:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=1110s)

**수치(전부 자가 보고) [개발자 발언]**
- "출시했을 때 위시가 14만 명이었거든요 … 하루만에 2억을 넘었고 그리고 이틀만에 4억 7천이고 지금 3일차 지금 8억이거든요." (영상 첫머리 하이라이트 자막은 "7개월에 4억 7천이고 3년차 지금 8억"으로 **오인식**되어 있음. 23:30 구간과 설명란 기준 "이틀만에 / 3일차"가 맞음) — [23:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=1410s)
- 수익금은 다음 달에 들어오며 인터뷰 시점엔 "다음 월세 낼 돈도 없는 상태"라고 말함. 8억이 총매출(gross)인지 순수익인지는 밝히지 않음 — [24:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=1440s)
- 구매자 중 중국 플레이어가 많은 것 같다고 말함. 대형 유튜버는 아직 다루지 않았다고 말함 — [23:30~24:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=1410s)
- 진행자의 "1년 수익 100억도 넘을 수 있을 것 같다"는 **[진행자]의 추측**이며 근거 제시 없음 — [36:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=2160s)
- 외부 보도와의 대조: 개발사가 X에서 48시간 총매출 35.6만 달러·5만 장, 11월 17일 누적 10만 장을 발표했다고 보도됨(둘 다 개발사 발표 인용) — [AUTOMATON 2026-11-19](https://automaton-media.com/articles/newsjp/20261119-479967/), [Mein-MMO 2026-11-17](https://mein-mmo.de/euro-in-2-tagen-vibecoder-entwickelt-solo-game-steam-hit/)
- Steam 평가: AUTOMATON 기사 시점 약 1,200건·약 79% 긍정("やや好評"). Steam API의 recommendations total은 2026-11-22 기준 1,705 — [AUTOMATON](https://automaton-media.com/articles/newsjp/20261119-479967/), [Steam appdetails API](https://store.steampowered.com/api/appdetails?appids=4459590&l=english)

**복제 게임 [개발자 발언]**
- WeChat·Douyin 미니게임에 복제작 두 종이 올라왔고(하나는 거의 그대로, 하나는 "더 잘 만든" 새 모드), 둘 다 **데모**를 복제한 것. 신고했지만 하나는 아직 남아 있음. 대응은 "내가 더 잘 만들면 되지" + 지속 업데이트 — [26:30~28:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=1590s)

### Inferences
- **스택 충돌의 결론:** 개발자 본인 육성과 영상 설명란은 `Codex` 2계정 + `LÖVE` + 나노바나나로 일치한다. Cursor·VS Code Copilot은 등장하지 않는다. 다만 본인이 "AI는 계속 바꿔가면서 많이 썼었는데"라고 했으므로 초기에 다른 도구를 썼을 가능성까지 부정되지는 않는다. "ChatGPT/Claude/Gemini 로테이션"은 Codex(주력) → Claude(막판 한 달) + Gemini(이미지)라는 발언과 대체로 양립한다.
- 영어권 보도의 "Pixelab"은 본인이 말한 "픽셀 스내퍼"(나노바나나 이미지를 픽셀 그리드에 맞추는 도구)를 옮기는 과정에서 바뀌었을 가능성이 있다. 확인된 사실이 아니라 추정이다.
- "3만 원짜리 코덱스"는 가격대로 보아 ChatGPT 유료 최저 요금제 2계정으로 보이지만 요금제 이름은 본인이 말하지 않았다.
- 본인이 설명한 방식은 스펙 문서·규칙 파일·기능 단위 분할 같은 구조화된 방법론이 아니라 "앱에 말로 시키고, 직접 플레이해 보고, 재미없으면 갈아엎기"의 반복이다. 구조화의 빈자리를 메운 것은 에디터 없는 코드 전용 엔진(에이전트가 전부 텍스트로 다룰 수 있음)과 개발자의 플레이어 관점이다.
- 79% 긍정이라는 평가와 "아직은 부족하죠 많이"라는 본인 발언을 보면, 판매 성과가 완성도 평가와 동일하지는 않다.

### Gaps
- 프롬프트 작성 요령, 한 번에 맡기는 작업 단위, 버전 관리(git) 사용 여부, 코드 규모는 인터뷰에서 묻지도 답하지도 않았다.
- Cursor·Copilot·PixelLab을 언급했다는 영어 기사는 이번 검색에서 찾지 못했다. 검색에 걸린 기사들은 도구명을 적지 않았다([AUTOMATON](https://automaton-media.com/articles/newsjp/20261119-479967/), [Mein-MMO](https://mein-mmo.de/euro-in-2-tagen-vibecoder-entwickelt-solo-game-steam-hit/), [iXBT 2026-11-14](https://ixbt.games/en/news/2026/11/14/v-stean-vysel-pravilnyi-neiroslop-azartnyi-rogalik-slotbound-privlek-tysiaci-igrokov-i-polucil-ocen-polozitelnye-otzyvy.html)).
- X(`x.com/OptimaArchGames`)는 HTTP 402로 열리지 않았다. 우회하지 않았으므로 X 게시물 원문은 2차 보도 인용으로만 확인했다.
- 자막 불명확 구간: 가장 많았던 데모 피드백이 "게임 동참이 안 된다"로 찍혀 있어 실제 단어를 알 수 없다([20:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=1230s)). 진행자가 복제 위험으로 언급한 "아리에"도 불명확하다(다른 영상에 나오는 "Reverse Engineer Anything(REA)"일 수 있으나 추정) ([27:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=1620s)).
- Steam 리뷰 요약 API는 응답을 받지 못해 긍정 비율을 직접 확인하지 못했다.
- Slotbound 분석 영상 Biskey Games 「How a Vibe-Coded Steam Game Sold 100,000 Copies」(2026-11-16, 22,395회)는 자막 요청이 HTTP 429로 거절돼 읽지 못했다 — [YouTube](https://www.youtube.com/watch?v=D1e29_DYQZ4)

## 2. 기간 내 다른 영상: 1인·소규모 개발자의 실제 AI 게임 파이프라인

### Takeaway
기간 내 조회수 상위권은 대부분 모델 비교·튜토리얼·강의 판매 영상이고, **실제 출시·운영 수치를 본인이 공개한 영상은 한국어 소형 채널에 몰려 있다**(모바일 방치형 2달 반 결산, 3주 출시 도전, 출시 후 감독 비용 회고, 웹 포털 심사 탈락 분석). 영어권에서는 Stefan 3D AI의 구독자 게임 쇼케이스와 본인 개발기가 가장 구체적인 도구·비용 목록을 담고 있으나 제휴 링크와 자체 강의 홍보가 섞여 있다. 일본어는 검색 결과에 조건에 맞는 개발기가 없었다.

### Cited Findings

**A. 출시·운영 수치를 본인이 공개한 영상(한국어)**

- **1인 개발 | 출시까지 갑니다 — 「클로드로 만든 게임, 두 달 반 수익 현실 (광고비·AI 비용까지 전부 공개)」** 2026-10-29, 675,557회, 4분 28초(자동 자막, 내레이션은 AI 음성이라고 영상에서 밝힘). 게임: 도트 모바일 방치형 「전설의 대장간 후예」, 2026-08-17 출시. **[개발자 발언, 자가 보고]** 두 달 반 수입 1,328만 원, 남은 돈 206만 원. 보상형 광고 4,428달러(약 592만 원) + 광고 제거(6,600원) 1,132건·실수령 약 569만 원. 구글 광고비 594만 원으로 약 12,700 설치(건당 평균 428원). Claude는 6월 월 22달러 → 7월 말부터 월 220달러 Max, 5개월 902달러. 이미지·영상용 Higgsfield(자막: "스필드/픽스필드", 설명란에 "힉스필드") 1년치 1,800달러. "기획부터 코드, 검증, 번역까지. 같이 쓴 코드가 27,000줄. 빌드는 86번. … 4개 언어 … 비정상 종료율은 0.06%, 평점은 4.66점". 결산 숫자도 Claude가 브라우저로 대시보드 5곳을 읽어 모았다고 말함 — [YouTube](https://www.youtube.com/watch?v=m5EE54v3QGI), [02:00~02:30](https://www.youtube.com/watch?v=m5EE54v3QGI&t=120s), [03:30](https://www.youtube.com/watch?v=m5EE54v3QGI&t=210s)
- **같은 채널 — 「클로드로 만든 1인 개발 게임, 서버비용 현실」** 2026-11-05, 34,944회. **[개발자 발언]** 하루 약 1,000명 플레이에 서버비 0원(무료 한도의 7%). 게임 로직은 전부 기기에서 돌리고 랭킹 한 줄만 전송, 전송 주기 제한, Firebase 보안 규칙으로 비정상 기록 차단(30일간 통과 21만·차단 3,200), 하루 한두 번 직접 기록 확인, 예산 알림 설정 — [YouTube](https://www.youtube.com/watch?v=XHMY9Gfd-Lk)
- **개발자 김뽑희 — 「AI로 혼자 만든 게임, 출시 첫날 결제까지 들어왔습니다 [3주 안에 스토어 출시 도전 EP 3]」** 2026-10-31, 46,237회. 게임: 「데미지드 스피릿」(Google Play). **[개발자 발언]** "게임을 만드는 건 AI랑 같이 하니까 생각보다 빨랐어요. 오히려 오래 걸린 건 서류, 기다림, 그리고 제 욕심" — 사업자·게임제작업·통신판매업 등록, 개인 개발자 필수인 테스터 12명·14일 비공개 테스트(10/14 시작), 프로덕션 신청서. 주변 테스터 의견으로 안내 문구·버튼 위치 수정. 범위를 "출시 전에 꼭 있어야 하는 것"과 "출시 후 채워도 되는 것"으로 분리. 출시 전 점검 목록 20개를 AI에게 정리시킴. 스토어 스크린샷은 "한 개당 100번씩" 고쳤다고 말함. 10/31 출시, 첫날 결제 약 15,000원(자가 보고). 이 편에서는 코딩 에이전트 이름을 말하지 않음 — [YouTube](https://www.youtube.com/watch?v=k1V2cF894_A), [10:00](https://www.youtube.com/watch?v=k1V2cF894_A&t=600s)
- **GIVEPRO — 「AI로 게임 만들어 팔아 보니 딸깍은 없었습니다 | 1인 개발 후기」** 2026-10-31, 19,964회(수동 한국어 자막). 설명란: 코드는 Claude Code와 Codex. 두 스토어에서 판매 중, 8월 18일 첫 승인 후 버전 1.25. **[개발자 발언]** 지시 범위 문제: "자동 카메라를 넣지 않는다고만 적었는데, AI가 이걸 넓게 읽어서 잘 있던 방 확대 기능을 지웠습니다" → "그날부터 지시에 어디까지 바꿔도 되는지를 적습니다. 바꿀 수 없는 것 일곱 줄도 그래서 생겼습니다" ([02:00~03:00](https://www.youtube.com/watch?v=18MnAQUaVS8&t=120s)). 검증 문제: 새 작업 폴더에 소리 파일이 없었는데 빌드·자동 테스트가 통과해 스토어에 무음 버전이 나감 → "이제는 소리 파일이 빠지면 빌드가 멈춥니다"; AI가 통과시킨 그림에 손이 세 개 ([03:30~04:00](https://www.youtube.com/watch?v=18MnAQUaVS8&t=210s)). "다 됐다는 보고를 받으면 폰을 들고 직접 눌러 봅니다" ([04:30](https://www.youtube.com/watch?v=18MnAQUaVS8&t=270s)). 실사용 문제: 313층 플레이어의 옛 세이브가 업데이트 후 멈춤, 특정 iOS 기기 실행 직후 종료는 구매자 제보로 발견 ([05:00~05:30](https://www.youtube.com/watch?v=18MnAQUaVS8&t=300s)). 병렬 에이전트: 6개를 동시에 돌린 날 서로의 변경을 가져가 상점 코드 약 500줄이 다른 폴더로 넘어감, 그림 승인 칸 35건을 한 번도 안 눌렀음 → "두 번 잡은 실수는 규칙으로 만들어서, AI가 명령을 실행하기 직전에 막히게 했습니다. 이 장치가 지금까지 18번 막았습니다" ([07:00~07:30](https://www.youtube.com/watch?v=18MnAQUaVS8&t=420s)). 매출 수치는 공개하지 않음 — [YouTube](https://www.youtube.com/watch?v=18MnAQUaVS8)
- **HBJB Studio — 「AI 바이브코딩으로 게임 만들어서 출시했더니 광탈함ㅋㅋ (평점 10점인데 왜?)」** 2026-11-09, 18,144회. 게임: 픽셀 오토배틀러 「쪼꼬미 용병단」(직업 100개·스킬 600개). **[개발자 발언]** CrazyGames Basic Launch에서 데스크톱 5/15, 모바일 6/15(합격선 9)로 탈락. 평균 플레이 8분 34초, D1 리텐션 2.35%/4.08%, 1분 이상 플레이 전환율 42.86%/18.42%. 자체 계측 결과 첫 전투까지 중간값 74초, 신규 401명 중 42%가 첫 전투 전에 이탈. 심사 일주일 동안 빌드를 18번 교체했고 한 번은 컴파일 안 되는 빌드가 나감. "AI랑 만들면 직업 하나 추가하는 건 정말 딸깍이거든요. 그래서 첫 1분을 다듬을 시간에 저희는 직업을 하나 더 만들고 있었습니다" ([05:30](https://www.youtube.com/watch?v=YYbxyeU0D0k&t=330s)), "AI는 콘텐츠를 무한히 찍어 주지만 플레이어의 첫 1분은 대신 봐 주지 않습니다" ([08:00](https://www.youtube.com/watch?v=YYbxyeU0D0k&t=480s)). 교훈: 출시 전 계측 심기, 평점이 아닌 퍼널 보기, 심사 기간 빌드 동결, 번역, 모바일 별도 설계. 코딩 도구명은 말하지 않음. **실패 사례**임 — [YouTube](https://www.youtube.com/watch?v=YYbxyeU0D0k)
- **채솔 — 「코딩 0인 30대가 클로드로 만든 MMORPG, 한 달 운영 현실」** 2026-11-11, 21,630회. 브라우저 픽셀 온라인 RPG 「솔리온」. **[개발자 발언, 자가 보고]** 가입 계정 229개, 하루 약 50명 로그인, 최고 동접 16명, 업데이트 158건(하루 약 5건), 서버비 월 5달러, 에셋 구매 40달러, Claude Max 요금제, 수익 0원(후원으로 서버비 충당). "AI가 코드를 쓴다. 하지만 무엇을 만들지, 어떤 느낌이어야 할지, 언제 멈출지는 전부 내가 정한다." 확률 조작 의심을 받자 강화 판정을 서버로 옮기고 확률을 공개. 내려받은 `ko` 자막 트랙의 내용이 영어여서 위 인용은 영어 문장을 옮긴 것이다. 규모가 작아 "호평받은 결과"로 보기는 어렵다 — [YouTube](https://www.youtube.com/watch?v=lVuYcl2xPEc)
- **웹핵 — 「AI로 게임을 만들며 생각이 바뀐 것들」** 2026-10-23, 20,558회. **[개발자 발언]** 엔진을 LÖVE2D에서 Godot으로 변경(자막: "러투/럽투디", "고닷/고다"; 설명란에 "Love2D에서 Godot으로"). 이유: LÖVE2D는 "아무것도 없는 곳에서 … 기능들을 구현해야 했는데" Godot은 내장 기능을 AI가 활용, 모바일 해상도·Steam 배포가 수월. 단점은 빌드 용량(CrazyGames 용량 제한 때문에 콘텐츠 대부분 삭제). "작은 규모의 2D 게임은 이전처럼 [LÖVE2D]로, 규모가 조금 있는 게임은 [Godot]". `AGENTS.md`식 사전 규칙은 "이제는 거의 안 쓰고" 스킬·맵 추가 시 검토 규칙처럼 "앞으로 기억해야 될 일"만 마크다운에 기록시킴. 하루 6시간 몰입 + 주 1일 12시간 — [YouTube](https://www.youtube.com/watch?v=yf3UmMMIO8s), [00:00~01:30](https://www.youtube.com/watch?v=yf3UmMMIO8s&t=0s)
- **MGD - Midnight Game Devs — 「AI로 게임 만들 때 쓰는 도구 총정리」** 2026-10-26, 90,342회(2인 팀, 도구 소개 영상이며 출시 성과는 언급 없음). **[개발자 발언]** 메인은 Claude Code, Codex 병용(Codex는 이미지도 생성). 규칙 파일에 "물어보지 않고 코딩하지 말 것, 직접 실행해서 확인하기 전에 다 됐다고 하지 말 것". 엔진은 Godot(텍스트 씬 파일, 명령어 실행 가능). Git을 "세이브 포인트"로 사용. Blender·Aseprite로 마무리, Tripo·Meshy·Rodin·PixelLab은 시작용이고 "결과를 그대로 쓰긴 어려워요". 효과음·음성은 ElevenLabs. 팔 애니메이션을 AI에게 맡기자 "매끈한 파이프처럼" 나와 파트너의 스케치 + AI가 짠 보간 프로그램 + 손 수정으로 해결 — [YouTube](https://www.youtube.com/watch?v=kZM0qx4hDbg), [02:00~05:30](https://www.youtube.com/watch?v=kZM0qx4hDbg&t=120s)

**B. 영어권: 구체 파이프라인이 나오는 영상(홍보 요소 포함 여부 표기)**

- **Stefan 3D AI — 「Made a Game With a $20 AI Plan and Already Got Sales」** 2026-11-02, 248,017회. **홍보 포함**(Higgsfield 제휴 링크, 자체 3D AI 강의 광고). 진행자가 구독자 제출작을 플레이하며 개발자가 알려준 정보를 전달하는 형식이므로 아래는 모두 **[해설자가 전한 개발자 자가 보고]**다. 자막 오인식 주의: "Cenet 5.5"(Sonnet 5.5로 추정), "hicksville"(Higgsfield), 코드 작성 주체가 "Tripo"로 찍힌 구간이 여러 곳 있음(문맥상 Claude로 추정) — [YouTube](https://www.youtube.com/watch?v=iJ83GYk2BIA)
  - After the Wind(1인, 약 6주, Godot): 코딩 Opus 5.5, 아트 주로 ChatGPT, 3D 모델 Tripo, Godot MCP, 애니메이션 Cascadeur. 세션마다 handoff를 남기고 새 세션을 시작해 프로젝트 지식을 유지. 월 약 400달러 — [01:00~05:30](https://www.youtube.com/watch?v=iJ83GYk2BIA&t=60s)
  - Iron Curtain Call(튀르키예 1인, 한 달 미만, Godot, Steam 데모 공개): Opus 5.5, 영상 레퍼런스를 만들어 모델에게 동작을 재현시키는 방식, Blender 병용. Max 20x 구독 6개를 돌려 하루에 주간 한도 하나씩 소진했다고 전함(자막은 "max x20 Tripo subscription", 금액 "1500"은 해설자 추정) — [06:00~10:30](https://www.youtube.com/watch?v=iJ83GYk2BIA&t=360s)
  - What the Sea Keeps(불가리아 1인, 본업·자녀 있음, Unity 경험 0): Opus 5.5 + Meshy + Suno + ChatGPT 이미지, Claude 200달러 Max. "Unity에서 플레이 버튼만 누르고 피드백을 줬다", 스토리텔링이 가장 어려웠다고 전함 — [11:00~17:00](https://www.youtube.com/watch?v=iJ83GYk2BIA&t=660s)
  - 절차적 성 짓기 게임(컴퓨터 엔지니어, 20달러 요금제, 에셋 0개 전부 절차 생성): 출시 2주 App Store 약 400달러, Google Play 약 25달러(자가 보고, 게임명은 자막에서 불명확) — [17:00~21:30](https://www.youtube.com/watch?v=iJ83GYk2BIA&t=1020s)
  - 호러 게임(Take Back Studios, 경력 개발자, 2개월, 월 약 200달러): ElevenLabs 음성, Tripo 모델, 일부는 손 모델링, Claude Max 5x — [21:30~25:30](https://www.youtube.com/watch?v=iJ83GYk2BIA&t=1290s)
  - Piñata Smash(전문 개발자 3인 팀, 약 5개월, Steam 데모): 코드는 100% AI, 자체 Unity MCP 제작, **최종 아트는 사람 아티스트**이고 AI 아트는 목업·레퍼런스에만 사용, 월 약 1,200달러 — [25:30~29:00](https://www.youtube.com/watch?v=iJ83GYk2BIA&t=1530s)
  - Beyond the Cradle(Steam 데모, 2개월, 총 600달러): Opus 5.5 + GPT-6 Astra, 아트 대부분 절차 생성 — [31:30~33:30](https://www.youtube.com/watch?v=iJ83GYk2BIA&t=1890s)
- **Stefan 3D AI — 「My Dream Game is Finally Ready to Play After 25 Days With AI」** 2026-11-01, 161,799회. **홍보 포함**(Tripo 제휴, 자체 강의). **[개발자 발언]** Unreal에서 Unity로 변경("code first"라 AI에 친화적). 게임 정보를 담은 위키를 만들고 "First information goes to wiki then it's reflected into the game"이라는 파이프라인으로 여러 에이전트가 공유 ([01:30~02:30](https://www.youtube.com/watch?v=LNfvjmtY0Qk&t=90s)). 첫 3~4일은 프리미티브로 전투 프로토타입 ([02:30](https://www.youtube.com/watch?v=LNfvjmtY0Qk&t=150s)). 첫 레벨 지형은 직접 손으로 칠함 — "you need to understand what you're asking" ([04:30~05:00](https://www.youtube.com/watch?v=LNfvjmtY0Qk&t=270s)). 애니메이션은 영상 생성으로 레퍼런스를 만든 뒤 모델에게 Blender에서 재현시킴, VFX는 이미지와 HTML 타이밍 도해를 먼저 만듦. 사운드는 여러 모델을 써 보고 음성·효과음·음악을 각각 다른 서비스로 결정. 22~23일 차는 새로 만들지 않고 직접 플레이하며 다듬었고 친구들에게 플레이를 부탁. 워크스페이스는 GitHub에 공개했다고 말함. 25작업일에 2레벨·유닛 18종. Steam 데모는 서류 승인 지연으로 **미공개** — 외부 플레이어 반응은 없음 — [YouTube](https://www.youtube.com/watch?v=LNfvjmtY0Qk), [19:00~20:00](https://www.youtube.com/watch?v=LNfvjmtY0Qk&t=1140s)
- **Clydiie — 「I Spent 12 Days Making a Game With Claude... I Almost Quit」** 2026-11-12, 146,200회(구독자 18,900). 같은 전투 게임을 Godot → Unity → Unreal Engine 5 순서로 Claude Opus 5.5에게 만들게 한 실험이며 **출시작 아님**. **[개발자 발언]** 캡슐만으로 전투 프로토타입부터 시작, Fab 에셋 라이브러리 활용, Higgsfield로 콘셉트 아트를 만들어 목표 이미지로 제공. Godot 약 8일(사용 한도 대기 포함), Unity 약 21시간, Unreal 약 37시간·자동 작업 700건 이상. Unreal에서 한꺼번에 여러 변경을 맡겼다가 막혔고 "we took everything step by step. We made a change, I tested it, reviewed the results, and only then we moved on"으로 바꿈 ([07:00](https://www.youtube.com/watch?v=gxeMisB4J9E&t=420s)). 결론 세 가지: "Get the combat right with the capsules first, give the AI a picture to aim for, not just a description. And once things get complicated, make one change at a time and test it before you move on." ([12:00](https://www.youtube.com/watch?v=gxeMisB4J9E&t=720s)) — [YouTube](https://www.youtube.com/watch?v=gxeMisB4J9E)
- **Garry Seto — 「How an AI-Coded Steam Game Got Past the AI Slop Stigma」** 2026-11-20, 21,593회(구독자 1,790). Steam 게임 「Zombies Aren't Real」에 대한 **제3자 해설**. **[해설자]** 출시 약 1주, 리뷰 약 2,000건·96% 긍정, GameDiscoverCo 추정 20만 장·총매출 170만 달러(추정치), 개발 약 3.5개월, 개발자는 이전에 게임 2개를 낸 16년 차 독학 프로그래머이자 구독자 약 2만의 유튜버. Steam AI 고지문은 AI 코딩 도구 사용과 인게임 텍스트·번역·UI 일부의 AI 보조를 밝힘 ([02:30](https://www.youtube.com/watch?v=iNcFOsDFZjs&t=150s)). 해설 영상에 삽입된 **[개발자 본인 육성]**: "Nowadays, I use AI myself for programming, but I still pay artists and … sound effect design artists and composers to do the artistic parts of my game while I delegate to AI for the technical parts" ([11:00~12:00](https://www.youtube.com/watch?v=iNcFOsDFZjs&t=660s)), 복제에 대해 "I don't think the idea in and of itself is valuable. I think that the execution of the idea is what is going to make my game fun" ([06:30](https://www.youtube.com/watch?v=iNcFOsDFZjs&t=390s)). 해설자는 화면에 스프라이트가 안 보인다며 아트 관련 주장에 의문을 제기함. 해설자가 복제 영상 날짜를 10월 3일과 10월 18일로 엇갈리게 말함 — [YouTube](https://www.youtube.com/watch?v=iNcFOsDFZjs)
- **마일드코드 — 「바이브코딩으로 만든 월 5천만원버는 게임」** 2026-10-26, 18,948회. 미국 스포츠 유튜버의 퀴즈 게임에 대한 **제3자 해설**이며 끝부분은 자기 다른 영상으로 유도. **[해설자]** Claude 채팅으로 명세서를 먼저 정리하고 Claude Code에서 막힐 때마다 명세서로 돌아가는 것을 반복해 주말에 첫 버전 제작, 닷새 뒤 하루 15만 명, 점수 공유 버튼 사용률 53%, 팔로워 400만이 넘지만 본인 계정 유입은 약 2%. 첫 주 이후 개발은 4인 팀으로 넘어감, 월 약 4만 달러(대부분 광고). 원출처는 영상에서 제시되지 않음 — [YouTube](https://www.youtube.com/watch?v=Zi55WGDKn2o), [03:00~04:30](https://www.youtube.com/watch?v=Zi55WGDKn2o&t=180s)

**C. 조회수는 높지만 제외하거나 참고만 한 영상**

- Brendan Jowett 「I Gave Claude 100 Hours to Build a Video Game (WTF!)」 2026-10-29, 554,229회 — 설명란 첫 줄이 유료 Skool 강의·제휴 링크. **강의 판매 채널**로 분류, 자막은 HTTP 429로 받지 못함 — [YouTube](https://www.youtube.com/watch?v=tpbXZyRxWNY)
- Chong-U — AI Oriented Dev 「Making Games With Claude Fable 5.2 & Unreal Engine 5.9 Is... UNREAL」 2026-11-12, 62,234회 — **홍보**(VibeGameDev, Insiders Club, 30일 강의). 피클볼 데모를 "less than a day"에 제작, API 가격 기준 약 420달러·토큰 약 7.5억, 캐릭터 모델은 Tripo, 에디터는 플레이 버튼 누를 때만 열었다고 말함. 문서와 릴리스 노트를 에이전트에게 읽혀 엔진 버전용 스킬을 갱신. 출시작이 아닌 데모 — [YouTube](https://www.youtube.com/watch?v=0G8air5h3_s), [02:30~04:00](https://www.youtube.com/watch?v=0G8air5h3_s&t=150s)
- Stefan 3D AI 「I Reverse Engineered Mario 64 to Make My Own Game」 2026-10-22, 282,455회 — 역공학 도구로 이동 수치를 뽑아 3D 플랫포머를 만든 실험. 스폰서 포함, 출시작 아님. 앞부분만 읽음 — [YouTube](https://www.youtube.com/watch?v=6MpHBHw30OE)
- Unreal Sensei 「How to Make Games in Unreal Engine 5 with AI」 2026-10-28, 157,871회(2시간 22분 튜토리얼), Boffy 「I Vibe Coded Minecraft From Scratch」 2026-10-31, 456,572회, Stefan 3D AI 「You Can Now Build UE 5 Games with 0$ Budget」 2026-10-28, 106,515회, Matteo AI 「How To Build Your First AI Video Game with Claude」 2026-11-05, 55,053회 — 날짜·조회수만 메타데이터로 확인, **자막은 읽지 않음** — [Unreal Sensei](https://www.youtube.com/watch?v=R_HFCPd5eAw), [Boffy](https://www.youtube.com/watch?v=I1aBncW7lgY), [Stefan](https://www.youtube.com/watch?v=UtY2DsOUCjE), [Matteo AI](https://www.youtube.com/watch?v=sfbuU51vlIE)
- 김플립 - LLM 코딩 「100% AI 코딩으로 하루 만에 3D RPG 게임을 만들면, 어디까지 될까?」 2026-10-30, 37,457회 — 하루짜리 실험, 자막 미열람 — [YouTube](https://www.youtube.com/watch?v=_3JR1CKHdsg)

**배경(기간 외)**

- Mr omi 「How to Make a Game With Claude Code and Publish It on Steam (Full Workflow)」 — 업로드 **2026-10-18**(기간 4일 전), 139,034회. 자막 미열람 — [YouTube](https://www.youtube.com/watch?v=r2z01arn2aE)
- PixelLab 「AI Builds a Godot Game From Scratch | PixelLab MCP + Claude Code Workflow」 — 업로드 **2025-10-03**, 90,249회. 도구 제작사의 자사 홍보 영상 — [YouTube](https://www.youtube.com/watch?v=THwZYWuOdZI)
- Garry Seto 영상이 인용한 「Zombies Aren't Real」 개발자 본인의 영상들은 해설자에 따르면 2026-10-03, 10-18 게시로 기간 이전이다. 원본 영상은 직접 확인하지 않았다 — [YouTube](https://www.youtube.com/watch?v=iNcFOsDFZjs&t=330s)

### Inferences
- 조회수와 정보 밀도는 반비례에 가깝다. 60만 회대 영상 중 실제 출시 결산은 「전설의 대장간 후예」 한 건이고, 운영·실패 데이터를 가장 자세히 공개한 채널(GIVEPRO, HBJB Studio)은 구독자 200~1,500명 규모다.
- 엔진 선택은 "에이전트가 텍스트로 전부 다룰 수 있는가"로 수렴한다. Slotbound(LÖVE), 웹핵(LÖVE→Godot), MGD(Godot), Stefan(Unreal→Unity, "code first"), Clydiie(Unreal은 headless가 안 돼서 가장 고생)가 같은 방향을 가리킨다.
- 3D 쪽은 생성 모델(Tripo/Meshy)이 초안, 마무리는 Blender·사람 손이라는 하이브리드가 공통이고, 애니메이션은 "영상 레퍼런스를 먼저 만들고 모델에게 재현시킨다"는 방식이 Stefan과 그 구독자들 사이에서 반복된다. 다만 이들 중 다수는 같은 채널의 방법을 따라 한 것이라 독립적인 근거로 보기는 어렵다.

### Gaps
- 일본어: "個人開発 AI ゲーム", "Claude Code ゲーム開発" 검색 결과는 영어 영상의 자동 번역 제목이나 포켓몬 검증 실험류였고, 1인 개발자의 출시 파이프라인 영상은 찾지 못했다.
- X/Twitter 게시물은 접근하지 못했다(Section 1 Gaps 참고). 영상에서 언급된 X 계정들의 원문도 확인하지 않았다.
- 자막 요청 HTTP 429로 Brendan Jowett, Biskey Games 두 영상은 읽지 못했다.
- Stefan 쇼케이스의 개발 기간·비용은 구독자가 보낸 자가 보고를 진행자가 읽어 준 것이라 2차 전달이다. 각 게임의 실제 판매·리뷰 수치는 대부분 없다.
- "Unity CLI Codex", "Unreal MCP" 질의에서 출시작을 가진 1인 개발자의 영상은 나오지 않았다(모델 비교·설치 튜토리얼 위주).

## 3. 실제로 플레이어를 얻은 개발자들에게서 반복되는 실천

### Takeaway
플레이어를 얻은 사례들이 공통으로 말하는 것은 도구 구성이 아니라 **(1) 그래픽보다 먼저 핵심 재미를 검증하고, (2) AI의 "완료" 보고를 믿지 않고 직접 플레이하며, (3) 실제 플레이어의 피드백·데이터로 고치는 것**이다. 고급 하네스는 필수가 아니었고(Slotbound는 앱만 사용), 반대로 AI가 콘텐츠를 싸게 찍어 주는 탓에 첫 경험을 방치한 사례는 실패했다.

### Cited Findings
- **핵심 재미를 먼저 검증하고, 재미없으면 갈아엎는다.** Slotbound는 2~3개월 차 버전이 "굉장히 재미가 없었"다며 갈아엎었다 — [08:30~09:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=510s). Stefan은 첫 3~4일을 프리미티브 전투 프로토타입에 썼다 — [02:30](https://www.youtube.com/watch?v=LNfvjmtY0Qk&t=150s). Clydiie는 "Get the combat right with the capsules first" — [12:00](https://www.youtube.com/watch?v=gxeMisB4J9E&t=720s)
- **"한눈에 읽히는 훅"이 유입을 만든다.** Slotbound: "한 눈에 보이는 재미 … 문장만 들어도 머릿속에서 그려지는 재미" — [12:30~13:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=750s). 퀴즈 게임 사례는 튜토리얼 없이 링크만 누르면 바로 열리는 구조와 점수 공유가 유입의 대부분이었다고 해설됨 **[해설자]** — [01:00~01:30](https://www.youtube.com/watch?v=Zi55WGDKn2o&t=60s). 반대 사례로 HBJB는 첫 전투까지 74초가 걸려 42%가 이탈 — [04:00~05:30](https://www.youtube.com/watch?v=YYbxyeU0D0k&t=240s)
- **데모·소규모 테스터의 피드백을 출시 직전까지 반영한다.** Slotbound: 100시간 이상 플레이어 5명, 출시 전날까지 수정 — [22:00~22:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=1320s). 김뽑희: 테스터 12명·14일 비공개 테스트 의견으로 문구·버튼 수정 — [02:00~03:00](https://www.youtube.com/watch?v=k1V2cF894_A&t=120s). Stefan: 22~23일 차는 직접 플레이와 친구 테스트 — [18:00~19:00](https://www.youtube.com/watch?v=LNfvjmtY0Qk&t=1080s)
- **AI의 "다 됐다"를 믿지 않고 사람이 직접 실행해 본다.** GIVEPRO: "다 됐다는 보고를 받으면 폰을 들고 직접 눌러 봅니다. 테스트를 다 통과한 버전도 몇 분 만지면 돌아올 길이 없는 화면이 나왔습니다" — [04:30~05:00](https://www.youtube.com/watch?v=18MnAQUaVS8&t=270s). MGD 규칙 파일: "직접 실행해서 확인하기 전에 다 됐다고 하지 말 것" — [02:30](https://www.youtube.com/watch?v=kZM0qx4hDbg&t=150s). What the Sea Keeps 개발자는 플레이 버튼을 누르고 피드백을 주는 것이 본인 역할이었다고 전해짐 **[해설자 전달]** — [14:30](https://www.youtube.com/watch?v=iJ83GYk2BIA&t=870s)
- **한 번에 하나씩 바꾸고 확인한다.** Clydiie: "make one change at a time and test it before you move on" — [12:00](https://www.youtube.com/watch?v=gxeMisB4J9E&t=720s). GIVEPRO는 에이전트 6개 병렬 실행이 코드 유실과 검수 병목을 만들었다고 말함 — [07:00](https://www.youtube.com/watch?v=18MnAQUaVS8&t=420s)
- **반복된 실수는 사람의 기억이 아니라 자동 차단 장치로 만든다.** GIVEPRO: 소리 파일 누락 시 빌드 중단, 명령 실행 직전 차단 규칙이 18번 작동 — [04:00](https://www.youtube.com/watch?v=18MnAQUaVS8&t=240s), [07:30](https://www.youtube.com/watch?v=18MnAQUaVS8&t=450s). MGD: Git을 되돌리기용 "세이브 포인트"로 사용 — [04:00](https://www.youtube.com/watch?v=kZM0qx4hDbg&t=240s)
- **지시에는 "바꾸면 안 되는 것"의 범위를 적는다.** GIVEPRO: "지시에 어디까지 바꿔도 되는지를 적습니다. 바꿀 수 없는 것 일곱 줄" — [03:00](https://www.youtube.com/watch?v=18MnAQUaVS8&t=180s). 반면 웹핵은 모델이 좋아져 사전 규칙 파일을 "거의 안 쓰고" 기억할 사항만 기록한다고 말함 — [01:00~01:30](https://www.youtube.com/watch?v=yf3UmMMIO8s&t=60s); Slotbound 개발자는 규칙 파일·하네스 자체를 쓰지 않았다 — [33:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=2010s). **이 항목은 사례 간 의견이 갈린다.**
- **프로젝트 지식을 세션 밖에 둔다.** Stefan: 위키 → 게임 순서의 파이프라인 — [02:00](https://www.youtube.com/watch?v=LNfvjmtY0Qk&t=120s). After the Wind 개발자: 세션마다 handoff 후 새 세션 **[해설자 전달]** — [05:00](https://www.youtube.com/watch?v=iJ83GYk2BIA&t=300s). 퀴즈 게임: 명세서로 되돌아가기 반복 **[해설자]** — [03:00](https://www.youtube.com/watch?v=Zi55WGDKn2o&t=180s)
- **에이전트가 텍스트로 다룰 수 있는 엔진을 고른다.** Slotbound: 에디터가 없어서 LÖVE 선택 — [14:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=840s). MGD: Godot은 씬이 텍스트 파일이고 명령어로 실행 가능 — [03:00](https://www.youtube.com/watch?v=kZM0qx4hDbg&t=180s). Stefan: Unity가 "code first" — [01:00](https://www.youtube.com/watch?v=LNfvjmtY0Qk&t=60s)
- **소리와 음악은 AI에만 맡기지 않는 경우가 많다.** Slotbound: 사람 작곡가 + 구매 에셋 + ElevenLabs 효과음 — [34:30~36:00](https://www.youtube.com/watch?v=6_cqj13abyI&t=2070s). Zombies Aren't Real 개발자: 아티스트·사운드 디자이너·작곡가에게 비용을 지불한다고 말함 — [11:00](https://www.youtube.com/watch?v=iNcFOsDFZjs&t=660s). Piñata Smash: 최종 아트는 사람 **[해설자 전달]** — [26:00](https://www.youtube.com/watch?v=iJ83GYk2BIA&t=1560s)
- **AI 사용을 숨기지 않는다.** Slotbound와 Zombies Aren't Real 모두 Steam에 AI 고지를 올렸다 — [Steam 상점 페이지](https://store.steampowered.com/app/4459590/?l=english), [02:30](https://www.youtube.com/watch?v=iNcFOsDFZjs&t=150s). 해설자 Garry Seto는 얼굴을 드러낸 개발자(96%)와 그렇지 않은 Slotbound(79%)의 평가 차이를 신뢰도 차이로 해석했으나 이는 **[해설자]의 추론**이다 — [20:00](https://www.youtube.com/watch?v=iNcFOsDFZjs&t=1200s)
- **출시 후에도 빠르게 고친다.** Slotbound: "쉬지 않고 고쳤습니다. 물론 지금도 고치고 있[고]" — [22:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=1350s). 채솔: 한 달 158건 업데이트 — [01:30](https://www.youtube.com/watch?v=lVuYcl2xPEc&t=90s). GIVEPRO: 8월 첫 승인 후 버전 1.25 — [06:00](https://www.youtube.com/watch?v=18MnAQUaVS8&t=360s)
- **비용 규모.** 저예산 구간은 월 20~30달러 요금제 1~2개(Slotbound의 대부분 기간, 절차 생성 게임), 본격 구간은 월 200~220달러(Slotbound 막판 한 달, 전설의 대장간 후예, What the Sea Keeps, MGD는 월 100달러 이상 권장) — [14:00~14:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=840s), [02:00](https://www.youtube.com/watch?v=m5EE54v3QGI&t=120s), [16:30](https://www.youtube.com/watch?v=iJ83GYk2BIA&t=990s), [01:00](https://www.youtube.com/watch?v=kZM0qx4hDbg&t=60s)
- **유료 광고의 한계.** 전설의 대장간 후예: "광고비를 확 늘려도 설치는 그만큼 늘지 않는다" — 일 광고비를 70% 넘게 올렸는데 설치는 약 10% 증가 — [01:30](https://www.youtube.com/watch?v=m5EE54v3QGI&t=90s), [03:30~04:00](https://www.youtube.com/watch?v=m5EE54v3QGI&t=210s). Slotbound는 직접 한 홍보(Reddit·Threads·메일)가 거의 효과 없었고 데모 자체가 유입원이었다고 말함 — [17:30](https://www.youtube.com/watch?v=6_cqj13abyI&t=1050s)

### Inferences
- 성과가 큰 두 사례(Slotbound, Zombies Aren't Real)는 정반대 프로필이다. 한쪽은 코딩 경험이 없는 첫 개발자가 앱만으로, 다른 쪽은 16년 차 프로그래머가 기존 구독자 2만 명을 가지고 만들었다. 공통점은 그래픽 요구가 낮은 장르(픽셀 로그라이크 디펜스, 벡터 그래픽 전략), 한 문장 훅, 10달러 안팎의 가격, 출시 전에 이미 확보된 관심(데모 또는 유튜브)이다. 표본이 둘뿐이라 일반화에는 주의가 필요하다.
- AI가 콘텐츠 생산 비용을 낮추면 병목이 "첫 1분, 검수, 운영"으로 옮겨 간다는 것이 GIVEPRO·HBJB·김뽑희·채솔 네 영상의 공통 결론이다. Slotbound 개발자가 스스로 큰 콘텐츠 분량을 선택한 뒤 번아웃을 겪은 것도 같은 맥락으로 읽을 수 있다.
- 규칙 파일·하네스의 필요성은 모델 세대와 프로젝트 성격에 따라 갈린다. 출시 후 운영 중인 유료 제품(GIVEPRO)은 차단 규칙을 늘렸고, 신규 프로토타입 위주 개발자(웹핵)는 줄였다. "반드시 필요하다"는 근거는 이번 자료에 없다.
- 이번에 확인한 수치는 모두 개발자 자가 보고 또는 제3자 추정치이므로, 보고서에서는 "~라고 밝혔다" 수준으로 써야 한다.

### Gaps
- "플레이어를 얻었다"고 볼 만한 사례가 기간 내 영상 기준으로 Slotbound, Zombies Aren't Real(2차 해설), 전설의 대장간 후예, 퀴즈 게임(2차 해설) 정도라 표본이 작다.
- 자동화 테스트(헤드리스 실행, 스크린샷 검증 등)를 출시작에 체계적으로 적용했다는 1차 발언은 GIVEPRO의 "자동 테스트" 언급 외에 찾지 못했다. Clydiie의 headless 실행은 출시작이 아닌 실험이다.
- 각 개발자의 실제 프롬프트 원문이나 규칙 파일 내용이 영상에 공개된 경우는 없었다(Chong-U의 프롬프트는 유료·가입 자료로 유도됨).
