class_name Sound
extends RefCounted
## 소리 재생기를 만든다. 재생(play)은 규칙의 결과에서만 부르고, 소리가 게임 상태를 바꾸지 않게 한다.


## path 의 소리를 낼 AudioStreamPlayer. 씬에 add_child 한 뒤 play() 한다.
## loop 가 참이면 끝에서 처음으로 이어 반복한다. 반복할 소리는 `gf post audio-loop` 로 다듬은 .wav 를 쓴다
## (mp3 는 압축이 이음매를 흐트러뜨릴 수 있다).
static func player(path: String, volume_db := 0.0, loop := false, bus := &"Master") -> AudioStreamPlayer:
	var node := AudioStreamPlayer.new()
	node.stream = load(path)
	node.volume_db = volume_db
	node.bus = bus
	if loop and node.stream is AudioStreamWAV:
		var wav: AudioStreamWAV = node.stream
		wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
		wav.loop_begin = 0
		wav.loop_end = roundi(wav.get_length() * wav.mix_rate)
	elif loop:
		node.stream.set("loop", true)
	return node
