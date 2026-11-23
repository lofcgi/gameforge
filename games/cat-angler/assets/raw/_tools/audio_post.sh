#!/bin/zsh
# 효과음: 앞 무음을 자르고 끝을 짧게 줄여(딸깍 소리 방지) wav 로, 그 뒤 audio_norm.py 로 크기를 맞춘다.
# 음악: gf post audio-loop 로 이음매를 다듬어 wav 로. 인자로 music 을 주면 음악만, sfx 를 주면 효과음만 한다.
cd /Users/iyeonsang/Desktop/game/games/cat-angler
gf() { uv run -q --project /Users/iyeonsang/Desktop/game/harness/tools gf --project /Users/iyeonsang/Desktop/game/games/cat-angler "$@"; }
mkdir -p assets/game/audio
WHAT=${1:-all}
# 박이 또렷한데 audio-loop 의 반복 길이가 박의 배수가 아니었던 곡. 박의 정수배로 자른다(audio_recut.py).
RECUT=(cutscene_intro cutscene_ending)
MUSIC=(title town sea_shallow sea_open sea_deep fight legend_fight cutscene_intro cutscene_ending)
[ $WHAT = music ] || uv run -q --project /Users/iyeonsang/Desktop/game/harness/tools python assets/raw/_tools/audio_talk.py || exit 1
for f in assets/raw/audio/*.mp3; do
  n=${f:t:r}
  if (( ${MUSIC[(Ie)$n]} )); then
    [ $WHAT = sfx ] && continue
    if (( ${RECUT[(Ie)$n]} )); then
      uv run -q --project /Users/iyeonsang/Desktop/game/harness/tools python assets/raw/_tools/audio_recut.py $f assets/game/audio/$n.wav || exit 1
      continue
    fi
    gf post audio-loop $f --out assets/game/audio/$n.wav | tail -1 | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print('$n', d.get('ok'), d.get('error') or d.get('after', {}))" 
  else
    [ $WHAT = music ] && continue
    ffmpeg -v error -y -i $f -af "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.005,areverse,afade=t=in:d=0.02,areverse" -ar 44100 -ac 1 -c:a pcm_s16le assets/game/audio/$n.wav || exit 1
  fi
done
[ $WHAT = music ] || uv run -q --project /Users/iyeonsang/Desktop/game/harness/tools python assets/raw/_tools/audio_norm.py
