#!/bin/zsh
# 효과음을 만든다(talk 는 audio_talk.py 가 계산으로 만든다). 고르지 않은 시안은 assets/raw/audio/_alt/ 에 있다
# (bite·pick 의 첫 시안은 순간 피크뿐이고 몸통이 25 dB 작았고, page 의 첫 시안은 0.2초 늦게 시작했다). 형식: 이름|길이(초)|설명
cd /Users/iyeonsang/Desktop/game/games/cat-angler
gf() { uv run -q --project /Users/iyeonsang/Desktop/game/harness/tools gf --project /Users/iyeonsang/Desktop/game/games/cat-angler "$@"; }
S="cozy retro game sound effect, soft, clean, no voice, no music"
while IFS='|' read -r name dur desc; do
  [ -z "$name" ] && continue
  [ -f assets/raw/audio/$name.mp3 ] && continue
  gf gen sfx "$desc, $S" --duration $dur --out assets/raw/audio --name $name --keep | tail -1 | cut -c1-120
done <<'LIST'
step|0.5|one single soft footstep of a small paw on a wooden plank, short light tap
pick|0.5|short soft plucked pop followed by a tiny leaf rustle, picking a berry from a bush, immediate attack
door|0.8|small wooden shop door opening with a short creak and a tiny bell jingle
coin|0.5|a few small coins clinking softly, bright short chime
buy|0.7|coins dropping into a wooden box followed by a short happy two-note chime
craft|1.0|wooden mortar tapping three times then a soft sparkle, crafting complete
anchor_down|1.0|small anchor dropping into water with a plop and a short chain rattle
anchor_up|1.0|short chain rattle winding up then a small anchor lifting out of water with drips
cast|0.6|fishing line cast, a short whip swish followed by a tiny water plip
nibble|0.5|tiny soft water blip, a small fish nibbling at bait, very subtle bubble pop
bite|0.6|bright short marimba alert ding ringing for half a second together with a quick water splash, a fish takes the bait, starts instantly
reel|0.8|fishing reel clicking quickly, fast soft wooden ratchet clicks
line_strain|1.0|fishing line under tension, a tight string creaking and whining upward in pitch
snap|0.5|a tight string snapping with a sharp twang
slip|0.6|a fish slipping off the hook, soft descending whoosh and a small plop
catch_small|0.8|small fish pulled out of water with a light splash and a short cheerful rising three-note jingle
catch_big|1.5|big fish hauled out of water with a heavy splash followed by a triumphant short plucked string fanfare
wave_hit|0.8|a big wave thumping against a wooden boat hull, low wooden thud with a splash
splash|0.6|medium water splash, something dropping into the sea
ui_move|0.5|very short soft wooden tick, menu cursor move blip
ui_ok|0.5|short bright confirm blip, two quick rising soft chiptune notes
ui_cancel|0.5|short soft cancel blip, two quick falling soft chiptune notes
codex_new|1.2|page turning then a gentle magical chime arpeggio, a new entry discovered
page|0.5|a single crisp page flip of a paper book, quick paper swish, starts instantly
repair|1.0|small wooden mallet hammering a wooden boat plank three times, dry woody knocks, workshop
pickup|0.8|a small wooden object lifted out of calm water, short watery scoop with a few drips
release|0.7|a small fish gently slipped back into calm water, soft plop and a tiny bubbly swirl
LIST
echo SFX_DONE
