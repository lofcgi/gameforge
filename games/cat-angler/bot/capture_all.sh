#!/bin/zsh
# 화면마다의 스크린샷을 captures/screens/ 아래에 다시 찍는다(SCREENSHOTS.md 가 이 파일들을 쓴다).
# 실행: zsh bot/capture_all.sh   (게임 폴더에서)
cd "$(dirname "$0")/.."
HARNESS="${GF_HARNESS:-$PWD/../../harness/tools}"
gf() { uv run -q --project "$HARNESS" gf --project "$PWD" "$@"; }
shot() {  # shot <폴더> <CA_START> <스크립트 또는 -> <시각들> [추가 인자...]
  local out=captures/screens/$1 start=$2 script=$3 at=$4; shift 4
  rm -f $out/*.png(N)
  local args=(engine capture --out $out --at $at "$@")
  [[ $script != - ]] && args+=(--script bot/$script)
  CA_START="$start" gf $args | tail -1 | cut -c1-160
}
shot title "" - 1
shot start "" shot_start.json 0.62,2.5,5.2,8.5
shot town "scene=town" - 1.1
shot forage "scene=town" shot_forage.json 1.95,3.4
shot in_bait "scene=in_bait,mats=3,guide=0" shot_shop.json 0.25,0.9,2.0,2.6
shot in_market "scene=in_market,hold=anchovy+scad+flounder,guide=0" shot_shop.json 0.25,0.9,2.0,2.6
shot in_yard "scene=in_yard,coins=700,dur=10,guide=0" shot_shop.json 0.25,0.9,2.0,2.6
shot in_tackle "scene=in_tackle,coins=500,guide=0" shot_shop.json 0.25,0.9,2.0,2.6
shot sea_shallow "x=500,baits=5,guide=0" shot_sail.json 2,6
shot sea_open "x=1000,boat=2,rod=2,baits=5,guide=0" shot_sail.json 2,6
shot sea_deep "x=1900,boat=3,rod=3,baits=5,guide=0" shot_sail.json 2,6
shot anchored "x=520,baits=5,guide=0" shot_anchor.json 4.4,6.5
shot fishing "x=520,baits=5,guide=0" shot_fish.json 0.6,2.5,6
shot seabed_shallow "x=600,baits=0,guide=0" shot_fish_deep.json 5
shot seabed_open "x=1500,boat=2,rod=2,baits=0,guide=0" shot_fish_deep.json 13
shot seabed_deep "x=2100,boat=3,rod=3,baits=0,guide=0" shot_fish_deep.json 14.5
shot reef "x=1170,boat=2,rod=2,baits=0,guide=0" shot_fish_deep.json 6
shot wreck_site "x=1640,boat=2,rod=2,baits=0,guide=0" shot_fish_deep.json 13
shot island "scene=island,guide=0" shot_island.json 0.2,3.3
shot codex "scene=town,caught=anchovy+scad" shot_codex.json 1.5
shot hold "x=520,hold=anchovy+scad,guide=0" shot_hold.json 1.5
shot pause "scene=town" shot_pause.json 1.5
shot help "scene=town" shot_help.json 1.8
shot wreck "x=1000,dur=8,guide=0" shot_wreck.json 5,6
shot debug "scene=town" shot_debug.json 1
shot size_1920 "x=520,baits=5,guide=0" shot_anchor.json 4.4 --size 1920x1080
shot size_1000x700 "x=520,baits=5,guide=0" shot_anchor.json 4.4 --size 1000x700
