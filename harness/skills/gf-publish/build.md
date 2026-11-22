# 엔진별 빌드

`gf` 에는 빌드·내보내기 명령이 없다. 아래는 엔진의 일반적인 방법이고 **하네스에서 끝까지 시험되지 않았다.** 처음 할 때는 한 단계씩 결과를 확인하고, 실패하면 오류를 그대로 사용자에게 보여 준다. 빌드 결과는 게임 폴더의 `build/` 아래에 둔다.

## web (web-2d, web-3d)

템플릿은 번들러 없이 브라우저가 소스를 그대로 읽는다. 배포물은 실행에 필요한 파일만 모은 정적 폴더다.

들어가는 것:

- `index.html`, `src/`, `gf/`(브리지. 쿼리 인자가 없으면 일반 게임 루프로 돈다), `assets/game/`
- web-3d: `index.html` 의 import map 이 가리키는 `node_modules/three/build/` 와 `node_modules/three/examples/jsm/`(쓰는 애드온). `bun add` 로 넣은 다른 패키지도 import map 경로대로.

빼는 것: `.gf/`, `.env*`, `assets/raw/`, `captures/`, `references/`, `design/`, `bot/`, `AGENTS.md`, `node_modules` 의 나머지.

```sh
cd <게임 폴더>
rm -rf build/web && mkdir -p build/web
rsync -a index.html src gf build/web/
rsync -a assets/game build/web/assets/
# web-3d 만:
mkdir -p build/web/node_modules/three
rsync -a node_modules/three/build node_modules/three/package.json build/web/node_modules/three/
rsync -a --relative node_modules/three/examples/jsm build/web/
du -sh build/web
```

- 복사 뒤 `build/web` 안에 `.env`, `.gf`, 원본 에셋이 없는지 `find build/web -name ".env*" -o -name ".gf"` 로 확인한다(출력이 비어야 한다).
- 용량이 크면 쓰지 않는 애드온 폴더와 큰 에셋을 줄인다. itch.io 의 HTML5 업로드는 파일 수·용량 제한이 있다. 올리기 전에 그 사이트의 현재 제한을 확인한다.
- WebGPU 가 없는 브라우저에서는 three 가 WebGL2 로 내려간다. 두 경로 모두에서 화면이 나오는지 사람에게 다른 브라우저로 확인받는다.
- 업로드용: `cd build/web && zip -r ../<이름>-web.zip .` (`index.html` 이 zip 의 최상위에 있어야 한다).

## godot (godot-2d, godot-3d)

필요한 것: 엔진 버전과 같은 **export templates**(Godot 에디터의 Editor → Manage Export Templates, 또는 `~/Library/Application Support/Godot/export_templates/<버전>/`)와 게임 폴더의 `export_presets.cfg`.

1. `export_presets.cfg` 가 없으면 사용자가 Godot 에디터에서 Project → Export → Add… 로 프리셋(Web, macOS, Windows Desktop 등)을 만드는 것이 가장 확실하다. 에이전트가 손으로 쓰지 않는다(버전마다 항목이 다르다).
2. 내보내기에서 뺄 것을 프리셋의 exclude 필터에 넣는다: `assets/raw/*`, `captures/*`, `references/*`, `design/*`, `bot/*`, `.gf/*`.
3. 내보낸다:

   ```sh
   cd <게임 폴더>
   mkdir -p build/web
   godot --headless --path . --export-release "Web" build/web/index.html
   # 데스크톱 예: godot --headless --path . --export-release "macOS" build/mac/<이름>.zip
   ```

   프리셋 이름은 `export_presets.cfg` 의 `name=` 값과 같아야 한다. Godot 은 오류가 나도 종료 코드 0 을 낼 수 있다. 출력에서 `ERROR` 를 찾고 결과 파일이 실제로 생겼는지 본다.
4. 웹 내보내기는 스레드 사용 여부에 따라 호스팅에 특정 응답 헤더(cross-origin isolation)가 필요할 수 있다. 프리셋의 스레드 옵션과 올릴 사이트의 지원을 확인한다. itch.io 는 프로젝트 설정에 SharedArrayBuffer 지원 옵션이 있다.
5. 브리지(`GfBridge`)는 실행 인자가 없으면 아무 일도 하지 않으므로 그대로 둔다.

## 공통: 빌드를 다시 확인한다

```sh
cd <게임 폴더>/build/web && python3 -m http.server 8765
```

- 사용자가 `http://127.0.0.1:8765` 에서 한 판을 끝까지 한다. 소리, 재시작, 창 크기 변경을 본다.
- 서버 로그에 404 가 없어야 한다. 있으면 빠진 파일을 넣고 다시 만든다.
- 개발 폴더에서 찍은 스크린샷과 같은 위치의 화면을 빌드에서 사람이 눈으로 비교한다. "개발 폴더에서는 됐다"는 빌드의 근거가 아니다.
- 데스크톱 빌드는 사용자가 실행 파일을 직접 열어 확인한다. macOS 는 서명되지 않은 앱 경고가 뜬다는 것을 배포 페이지에 적는다.
