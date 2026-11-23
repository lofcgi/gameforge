# 작성 기준 메모

이 폴더의 문서를 쓸 때 적용한 기준이에요. 토스의 테크니컬 라이팅 가이드(https://technical-writing.dev/)를 2026-11-23에 직접 읽고 정리했어요. 문서를 고치거나 새 페이지를 더할 때 이 기준을 그대로 따르세요.

## 읽은 페이지

모두 2026-11-23에 열람했어요.

| 영역 | 페이지 |
|---|---|
| 시작하기 | https://technical-writing.dev/overview.html |
| 튜토리얼 | https://technical-writing.dev/tutorial/basic-documents.html, https://technical-writing.dev/tutorial/structure.html, https://technical-writing.dev/tutorial/review-prompt.html |
| 문서 유형 정하기 | https://technical-writing.dev/type/index.html, https://technical-writing.dev/type/learning.html, https://technical-writing.dev/type/problem-solving.html, https://technical-writing.dev/type/reference.html, https://technical-writing.dev/type/explanation.html |
| 정보 구조 만들기 | https://technical-writing.dev/architecture/index.html, https://technical-writing.dev/architecture/one-thing-per-one-page.html, https://technical-writing.dev/architecture/value-first-cost-later.html, https://technical-writing.dev/architecture/heading.html, https://technical-writing.dev/architecture/overview.html, https://technical-writing.dev/architecture/predictability.html, https://technical-writing.dev/architecture/background.html |
| 문장 다듬기 | https://technical-writing.dev/sentence/index.html, https://technical-writing.dev/sentence/subject.html, https://technical-writing.dev/sentence/compactness.html, https://technical-writing.dev/sentence/concreteness.html, https://technical-writing.dev/sentence/natural-kor-expression.html, https://technical-writing.dev/sentence/consistency.html |

`review-prompt.html`은 본문이 GPT 봇을 만드는 절차뿐이고 프롬프트 내용은 정적 페이지에 없어서, 이 문서 세트에는 적용할 내용이 없었어요.

## 1. 문서 유형을 먼저 정한다

가이드는 독자의 목적에 따라 문서를 네 가지로 나눠요. 이 폴더의 모든 페이지는 맨 위에 자기 유형을 적고, 한 페이지에 한 유형만 담아요.

| 유형 | 독자의 목적 | 이 폴더에서 지킨 것 |
|---|---|---|
| 학습 | 처음 접해서 흐름을 알고 싶다 | 목표 → 준비 → 단계 → 최종 결과 순서. 모든 명령을 실제로 실행해 보고 그 출력을 기대 결과로 적었어요. 단계마다 성공 여부를 스스로 확인할 수 있어요. 막히는 경우는 본문이 아니라 끝의 FAQ에 모았어요 |
| 문제 해결 | 배경지식은 있고 특정 작업을 끝내고 싶다 | 문제 상황 → 준비 → 해결 단계 → 확인 방법 순서. 바로 쓸 수 있는 명령을 넣고, 왜 그 방법이 통하는지 한 줄로 적었어요 |
| 참조 | 사용법을 빠르게 찾고 싶다 | 표 위주, 같은 열 구조, 저장소 파일과 대조한 값만 적었어요 |
| 설명 | 원리와 배경을 깊이 이해하고 싶다 | 배경과 결정 과정을 먼저 쓰고, 구조는 표나 ASCII 다이어그램으로 보여 줘요 |

가이드는 유형을 섞어도 된다고 하지만(권장 사항), 이 세트는 독자가 "지금 무엇을 하려고 이 페이지를 열었는지"를 헷갈리지 않도록 섞지 않았어요. 설명이 더 필요한 곳은 다른 페이지로 링크했어요(크로스링크).

## 2. 정보 구조

- **한 페이지에서 하나만 다뤄요.** 제목 깊이는 `###`(H3)까지만 써요. `####`가 필요해지면 페이지를 나눠요. 여러 주제를 소개해야 하는 곳은 개요 페이지(`README.md`)가 맡아요.
- **가치를 먼저 줘요.** 첫 문단은 "이 페이지를 읽으면 무엇을 할 수 있는지"예요. 연혁과 세부 설정은 뒤에 둬요.
- **제목은 핵심 키워드를 넣은 30자 이내 평서문이에요.** 물음표와 느낌표를 쓰지 않아요. 같은 수준의 제목은 같은 형태로 맞췄어요: 학습·문제 해결 문서의 단계는 "숫자 + ~하기", 설명·참조 문서는 명사형이에요.
- **개요를 빠뜨리지 않아요.** 제목 바로 아래에서 문서의 목표와 핵심 내용을 요약해요.
- **예측할 수 있게 써요.** 같은 유형의 페이지는 같은 섹션 이름과 순서를 써요. 코드 블록 앞에는 그 코드가 무엇을 하는지 먼저 적어요. 기본 개념 → 사용법 → 예시 → 심화 순으로 놓아요.
- **자세히 설명해요.** 새 개념은 처음 나올 때 한두 문장으로 정의하고, 값에는 단위와 조건을 붙여요. 용어는 [용어집](glossary.md)에 한 번 정의하고 그 형태로만 써요.

같은 유형의 페이지가 공통으로 쓰는 섹션 이름이에요.

| 유형 | 섹션 순서 |
|---|---|
| 학습 | 목표 / 준비하기 / 1…N단계 / 최종 결과 확인하기 / 자주 막히는 곳 / 다음에 읽을 문서 |
| 문제 해결 | 이럴 때 쓰세요 / 준비하기 / 1…N단계 / 결과 확인하기 / 더 보기 |
| 설명 | (주제별 섹션) / 정리 / 더 보기 |
| 참조 | (표) / 더 보기 |

## 3. 문장

- **주체를 분명히 해요.** 독자가 하는 일은 독자를 주어로 쓰고("이 명령을 실행하면 ~할 수 있어요"), 도구의 동작을 설명할 때만 도구를 주어로 써요. 이 세트에서는 "누가 했는지"가 특히 중요해서 사용자, 메인 세션, 제작 에이전트, 심사자를 문장마다 밝혀요.
- **능동형으로 써요.** "~되어야 합니다" 대신 "~하세요"를 써요.
- **한 문장에 한 가지 생각만 담아요.** 메타 담화("앞서 설명했듯이", "결론적으로", "아시다시피")를 쓰지 않아요.
- **명사 대신 동사를 써요.** "검증 수행", "설정 진행" 같은 표현을 "검증해요", "설정해요"로 써요. '수행하다', '진행하다' 같은 한자어를 빼요.
- **모호한 표현 대신 수치와 기준을 써요.** "가끔 실패한다" 대신 "45번 중 39번"처럼 저장소에 남은 값을 적어요. 값이 없으면 없다고 적어요.
- **번역체를 피해요.** "~를 통해"는 "~로", "~에 대한"은 가능한 한 풀어서 써요.
- **용어를 일관되게 써요.** 공식 기술 용어는 공식 표기(Claude Code, Godot, three.js, Blender, fal)를 따르고, 약어는 처음에 풀어 써요.
- **어미는 해요체예요.** 가이드는 어미를 문서 분위기에 맞게 고르라고 해요. 이 세트는 가이드 본문과 같은 해요체로 통일했어요.

## 4. 이 세트에만 있는 규칙

가이드에 없지만 내용의 성격 때문에 더한 규칙이에요.

- **출처를 구분해요.** 저장소 파일로 확인한 내용은 그 파일의 경로를 붙여요. 저장소에 없고 작업 세션의 기록으로만 전해지는 내용은 "(세션 기록)"이라고 표시해요.
- **확인하지 못한 것을 적어요.** 저장소 문서가 "확인 못 했다"고 적은 것은 이 교육 자료에서도 그대로 전해요.
- **움직이는 값에는 날짜를 붙여요.** cat-angler는 이 문서를 쓰는 동안에도 다듬는 중이었어요. 에셋 수, 비용, 심사 결과에는 기준 시점을 적었어요.

## 5. 검토에 쓴 점검표

가이드의 유형별 체크리스트와 원칙별 체크리스트를 합친 거예요.

- [ ] 페이지 맨 위에 유형이 하나만 적혀 있나요?
- [ ] 제목 아래 개요만 읽어도 주제와 얻는 것을 알 수 있나요?
- [ ] 제목이 30자 이내 평서문이고, 같은 수준끼리 형태가 같은가요?
- [ ] H4 이상이 없나요?
- [ ] (학습) 목표를 제시했고, 직접 따라 했을 때 오류가 없고, 단계별이고, 실행할 수 있는 예제가 있나요?
- [ ] (문제 해결) 문제 상황을 정의했고, 바로 적용할 해결 방법이 있고, 환경 차이를 적었나요?
- [ ] (참조) 찾기 쉽고, 정확하고, 구조가 일관되나요?
- [ ] (설명) 배경과 원리를 설명했고, 복잡한 구조를 시각화했고, 선행 지식을 안내했나요?
- [ ] 문장마다 누가 하는지 드러나나요? 수동형, 메타 담화, 명사 나열이 없나요?
- [ ] 용어가 용어집의 형태와 같은가요?
- [ ] 링크와 그림 경로가 열리나요? 명령이 `gf --help`에 있나요?
