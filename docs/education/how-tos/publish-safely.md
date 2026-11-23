# 공개 저장소에 안전하게 올리기

> 문서 유형: 문제 해결 (How-to 가이드)

이 가이드를 따라 하면 AI 에이전트와 함께 만든 작업 폴더를 공개 저장소로 올릴 때 비밀 값, 남의 저작물, 다시 만들 수 있는 큰 파일을 빼고 올릴 수 있어요. 이 저장소(https://github.com/lofcgi/gameforge)가 실제로 쓴 `.gitignore`를 예시로 써요.

게임 빌드를 플레이 링크로 배포하는 절차는 이 문서의 범위가 아니에요. 그것은 `harness/skills/gf-publish/SKILL.md`에 있어요.

## 이럴 때 쓰세요

- 생성 API 키가 든 `.env`가 있는 폴더를 처음 공개하려 할 때
- 인터넷에서 모은 참고 이미지가 작업 폴더에 섞여 있을 때
- 에이전트가 남긴 실행 기록과 캐시 때문에 저장소가 커졌을 때

에이전트와 일하면 작업 폴더에 파일이 빠르게 쌓여요. 스크린샷, 봇 기록, 생성 원본, 수집한 이미지가 섞여 있어서 "전부 올리기"도 "전부 빼기"도 답이 아니에요. 종류별로 나눠서 정해요.

## 준비하기

- git이 설치돼 있어야 해요.
- **첫 커밋을 하기 전에** 이 가이드를 끝내세요. 한 번 커밋한 비밀 값은 기록에 남아요.

git은 작업 초기에 만드세요. 이 프로젝트는 한동안 git 없이 진행했고, 그 때문에 기능 하나(레퍼런스 수집용 Chrome 확장과 수신 서버)를 걷어 낼 때 되돌릴 방법이 없어서 지운 파일을 삭제하지 않고 휴지통으로 옮겼어요(`demo-check/EVIDENCE.md`의 "확인하지 못한 것", 세션 기록).

## 1. 올리지 않을 것을 네 종류로 나누기

작업 폴더의 파일을 아래 표로 분류하세요. 오른쪽 열은 이 저장소의 `.gitignore`가 실제로 쓴 규칙이에요.

| 종류 | 올리지 않는 이유 | 이 저장소의 규칙 |
|---|---|---|
| 자격증명 | 키가 새면 남이 여러분의 계정으로 생성 호출을 해요 | `.env`, `.env.*`, `*.key`, `*.pem`, `secrets/` (`!.env.example`은 올려요) |
| 남의 저작물 | 수집한 레퍼런스 이미지는 여러분의 것이 아니에요 | `**/references/inbox/*.jpg` 등 이미지 확장자, `**/references/sheets/*.png` |
| 도구가 다시 만드는 것 | 설치나 실행으로 복구돼요 | `.venv/`, `node_modules/`, `__pycache__/`, `.godot/`, `**/.gf/cache/` |
| 다시 만들 수 있는 큰 실행 기록 | 용량만 차지해요 | `**/captures/sessions/*.jsonl`, `**/captures/bot/` |

반대로 **올리는 것**도 정하세요. 이 저장소는 설계 문서, 단계 승인 기록(`.gf/state.json`), 비용 기록(`.gf/ledger.jsonl`), 심사 기록, 결과 스크린샷을 올렸어요. 과정을 보여 주는 증거이기 때문이에요.

## 2. 비밀 값 빼기

`.gitignore`의 맨 위에 자격증명 규칙을 넣으세요.

```gitignore
.env
.env.*
!.env.example
*.key
*.pem
secrets/
```

- `.env.example`에는 변수 이름만 적고 값은 비워 두세요. 내려받은 사람이 이 파일을 `.env`로 복사해 자기 키를 넣어요.
- 에이전트가 키를 읽지 못하게 하세요. gameforge에서는 훅이 `.env` 읽기와 출력을 막고, 코드가 실행 시점에 환경변수로만 키를 불러와요(`harness/README.md`, `harness/AGENTS.md`).

## 3. 남의 이미지는 빼고 출처만 남기기

수집한 레퍼런스 이미지와 그것으로 만든 모음판은 올리지 마세요. 대신 출처 주소가 든 메타 파일은 올리세요. 그러면 다른 사람이 같은 이미지를 다시 받을 수 있고, 무엇을 참고했는지도 투명하게 남아요.

```gitignore
**/references/inbox/*.jpg
**/references/inbox/*.png
**/references/picked/*.jpg
**/references/picked/*.png
!**/references/picked/traits-palette.png
**/references/sheets/*.png
```

- `!`로 시작하는 줄은 예외예요. `traits-palette.png`는 고른 이미지에서 뽑은 색 견본이라 직접 만든 결과물이에요.
- 이 저장소에서 `references/` 아래에 올라간 것은 메타 파일(`.json`) 199개, 분석 문서 1개, 색 견본 2개뿐이에요. 이미지 원본은 한 장도 없어요.
- 메타 파일의 `source_url`이나 `image_url`로 `gf ref add`를 다시 돌리면 이미지를 복구할 수 있어요.

생성한 그림과 소리를 올릴지는 여러분이 쓰는 생성 서비스의 약관을 직접 확인하고 정하세요. 이 자료는 그 판단을 대신하지 않아요.

## 4. 큰 파일과 캐시 빼기

다시 만들 수 있는 것은 빼세요. 다시 만들 수 **없는** 증거(승인 기록, 심사 기록, 사용자가 본 스크린샷)는 남기세요.

```gitignore
.venv/
node_modules/
.godot/
**/.gf/cache/
**/captures/sessions/*.jsonl
**/captures/bot/
```

주의할 점이 하나 있어요. `.gitignore`에 규칙을 나중에 넣어도 **이미 커밋한 파일은 계속 추적돼요**. 이 저장소에서도 `**/captures/bot/` 규칙이 있지만 `demo-check/pixel-godot/captures/bot/` 아래의 파일은 올라가 있어요. 이미 올린 파일을 빼려면 `git rm --cached <경로>`로 추적을 끊어야 해요.

## 5. 문서 속 개인 경로 알리기

에이전트가 쓴 문서에는 작업한 컴퓨터의 절대 경로가 남아요. 전부 고치기 어렵다면 README에 한 줄로 알리세요. 이 저장소의 `README.md`는 이렇게 적었어요.

> 문서 안의 `/Users/iyeonsang/Desktop/game/...` 경로는 처음 작업한 컴퓨터의 절대 경로다. 다른 컴퓨터에서는 이 저장소의 위치로 바꿔 읽는다.

경로에 실명이나 계정 이름이 들어 있어 공개하고 싶지 않다면 올리기 전에 바꾸세요.

## 결과 확인하기

커밋하기 전에 네 가지를 확인하세요.

**무시 규칙이 걸리는지 봐요.** 빼려는 파일이 어느 규칙에 걸리는지 알려 줘요.

```sh
git check-ignore -v games/cat-angler/references/picked/manual-001b1463eff2.jpg
```

```
.gitignore:35:**/references/picked/*.jpg	games/cat-angler/references/picked/manual-001b1463eff2.jpg
```

**올라갈 목록에 이미지 원본이 없는지 세요.** 0이 나와야 해요.

```sh
git ls-files | grep -E 'references/.*\.(jpg|jpeg|webp|gif)$' | wc -l
```

**올라갈 목록에 자격증명 파일이 없는지 세요.** 0이 나와야 해요.

```sh
git ls-files | grep -E '\.(key|pem)$' | wc -l
git ls-files | grep -E '(^|/)\.env$' | wc -l
```

**가장 큰 파일을 훑어봐요.** 뜻밖의 큰 파일이 있으면 올릴지 다시 정하세요. 이 저장소에서 가장 큰 파일은 7MB대의 음악 `.wav`예요.

```sh
git ls-files -z | xargs -0 ls -l | sort -k5 -n -r | head -10
```

처음 스테이징한 뒤에는 `git status`로 목록을 직접 읽으세요. 에이전트에게 맡기더라도 무엇이 올라가는지는 사람이 한 번 봐야 해요.

## 더 보기

- 레퍼런스를 모으는 절차: [레퍼런스 모으고 고르기](collect-references.md)
- 게임 빌드를 배포하고 공개 글을 쓰는 절차: `harness/skills/gf-publish/SKILL.md`
- 원문: 저장소 루트의 `.gitignore`, `README.md`
