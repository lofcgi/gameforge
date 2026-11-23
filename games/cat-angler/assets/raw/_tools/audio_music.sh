#!/bin/zsh
# 음악 9곡을 만든다. 형식: 이름|길이(초)|설명
cd /Users/iyeonsang/Desktop/game/games/cat-angler
gf() { uv run -q --project /Users/iyeonsang/Desktop/game/harness/tools gf --project /Users/iyeonsang/Desktop/game/games/cat-angler "$@"; }
B="instrumental game background music, seamless loop, plucked zither similar to a gayageum, breathy bamboo flute, soft hand drum, blended with mellow soft chiptune square-wave pads, warm, cozy, clean mix, constant volume from the first second to the last, no intro, no fade out"
while IFS='|' read -r name dur desc; do
  [ -z "$name" ] && continue
  [ -f assets/raw/audio/$name.mp3 ] && continue
  gf gen music "$desc, $B" --duration $dur --instrumental --out assets/raw/audio --name $name --keep | tail -1 | cut -c1-120
done <<'LIST'
sea_shallow|40|calm sunny morning on a quiet turquoise sea in a small rowboat, gentle swaying 6/8 feel, slow tempo 80 bpm, peaceful and light
town|40|friendly little harbor village, easygoing bouncy stroll, medium tempo 100 bpm, cheerful and homely
title|30|hopeful gentle main theme, memorable simple pentatonic melody on plucked zither, medium slow tempo 90 bpm, a small adventure begins
sea_open|30|wide open sea under a big sky, rolling waves, broader and more adventurous, flowing arpeggios, tempo 96 bpm
sea_deep|30|mysterious deep indigo sea, sparse slow notes, soft bell tones and low drone, glowing jellyfish, wonder not fear, tempo 70 bpm
fight|30|lively playful tug of war with a fish on the line, quick plucked ostinato, driving hand drum, energetic but lighthearted, tempo 132 bpm
legend_fight|30|dramatic but not dark battle with a legendary deep-sea fish, bold drum pattern, heroic pentatonic flute melody, urgent plucked strings, tempo 140 bpm
cutscene_intro|30|storybook folk tale opening in an undersea palace, slow tender and a little sad, solo bamboo flute over soft plucked zither, tempo 72 bpm
cutscene_ending|30|warm relieved storybook ending, gentle and grateful, rising hopeful melody, tempo 84 bpm
LIST
echo MUSIC_DONE
