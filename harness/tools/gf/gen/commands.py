from gf.core.output import GfError
from gf.core.paths import project_dir
from gf.gen.runner import generate, media


def _media(args, values: list[str] | None) -> list:
    return [media(project_dir(args), value) for value in values or []]


def image(args) -> int:
    refs = _media(args, args.ref)
    semantic = {"prompt": args.prompt, "image": refs}
    direct = {"aspect_ratio": args.aspect, "resolution": args.resolution, "num_images": args.count, "seed": args.seed}
    try:
        return generate(args, "image.concept", "image", semantic, direct)
    except GfError as exc:
        if refs and "'image' 입력" in str(exc):
            raise GfError(
                f"{exc} → image.concept 역할의 모델은 참조 이미지를 받지 않는다. 참조 이미지를 쓰려면 "
                '`gf gen edit "<프롬프트>" --image <참조 이미지>` (image.edit 역할)을 쓴다.'
            ) from exc
        raise


def edit(args) -> int:
    semantic = {"prompt": args.prompt, "image": _media(args, args.image)}
    direct = {"aspect_ratio": args.aspect, "resolution": args.resolution, "num_images": args.count, "seed": args.seed}
    return generate(args, "image.edit", "image", semantic, direct)


def rembg(args) -> int:
    return generate(args, "image.rembg", "image", {"image": _media(args, [args.image])}, {})


def video(args) -> int:
    semantic = {
        "prompt": args.prompt,
        "image": _media(args, [args.image]),
        "end_image": _media(args, [args.end_image] if args.end_image else []),
        "duration": args.duration,
    }
    direct = {"resolution": args.resolution, "generate_audio": args.audio}
    try:
        return generate(args, args.role, "video", semantic, direct)
    except GfError as exc:
        if args.end_image and "'end_image' 입력" in str(exc):
            other = "`--role video.look` 을 쓰고" if args.role != "video.look" else "`--model` 로 끝 프레임을 받는 모델을 지정하고"
            raise GfError(
                f"{exc} → {args.role} 역할의 모델은 마지막 프레임 이미지를 받지 않는다. 끝 프레임을 고정하려면 {other}, "
                "스프라이트 반복 구간은 --end-image 없이 만든 뒤 `gf post loop` 로 찾는다."
            ) from exc
        raise


def model3d(args) -> int:
    direct = {"face_limit": args.face_limit, "pbr": args.pbr, "quad": args.quad, "texture": args.texture}
    return generate(args, "model3d.gen", "model3d", {"image": _media(args, [args.image])}, direct)


def rig(args) -> int:
    direct = {
        "height_meters": args.height,
        "enable_animation": args.animate,
        "animation_action_id": args.animation_id,
    }
    return generate(args, "model3d.rig", "model3d", {"model": _media(args, [args.mesh])}, direct)


def sfx(args) -> int:
    return generate(args, "audio.sfx", "audio", {"prompt": args.prompt, "duration": args.duration}, {"loop": args.loop})


def tts(args) -> int:
    direct = {"voice": args.voice, "language_code": args.language}
    return generate(args, "audio.tts", "audio", {"prompt": args.text}, direct)


def music(args) -> int:
    semantic = {"prompt": args.prompt, "duration": args.duration}
    return generate(args, "audio.music", "audio", semantic, {"force_instrumental": args.instrumental})


def _common(parser, func) -> None:
    parser.add_argument("--name", help="결과 파일 이름 (기본: 종류-시각)")
    parser.add_argument("--out", help="결과 폴더 (기본: assets/raw/<종류>)")
    parser.add_argument("--model", help="역할에 설정된 모델 대신 쓸 fal 엔드포인트")
    parser.add_argument("--max-usd", type=float, help="추정 비용 한도 (기본: 설정의 max_usd_per_call)")
    parser.add_argument("--estimate-usd", type=float, help="단가를 환산할 수 없는 모델에 쓸 직접 추정한 비용 (한도와 비교한다)")
    parser.add_argument("--allow-unknown-cost", action="store_true",
                        help="비용을 추정할 수 없어도 호출한다 (한도 확인 없음). 없으면 그런 호출은 거부된다")
    parser.add_argument("--dry-run", action="store_true", help="호출하지 않고 엔드포인트·인자·추정 비용만 출력")
    parser.add_argument("--keep", action="store_true", help="프롬프트를 prompts.jsonl 에 채택본으로 남긴다")
    parser.add_argument("--arg", action="append", metavar="필드=값", help="모델 고유 필드를 직접 넣는다. @경로 는 파일 업로드")
    parser.add_argument("--refresh", action="store_true", help="캐시된 스키마·단가를 다시 받는다")
    parser.set_defaults(func=func)


def _image_options(parser) -> None:
    parser.add_argument("--aspect", help="가로세로 비율 (예: 1:1, 16:9)")
    parser.add_argument("--resolution", help="해상도 (모델의 enum 값. 예: 0.5K, 1K)")
    parser.add_argument("--count", type=int, help="생성할 장수")
    parser.add_argument("--seed", type=int)


def register(sub) -> None:
    p = sub.add_parser("gen", help="역할 기반 생성 (모델은 설정에서 읽는다)")
    s = p.add_subparsers(dest="cmd", required=True)

    q = s.add_parser("image", help="프롬프트로 이미지를 만든다 (image.concept)")
    q.add_argument("prompt")
    q.add_argument("--ref", action="append", help="참조 이미지. 기본 image.concept 모델은 받지 않는다 (참조는 gen edit --image 로 준다)")
    _image_options(q)
    _common(q, image)

    q = s.add_parser("edit", help="이미지를 프롬프트로 고친다 (image.edit)")
    q.add_argument("prompt")
    q.add_argument("--image", action="append", required=True, help="입력 이미지. 여러 번 쓸 수 있다")
    _image_options(q)
    _common(q, edit)

    q = s.add_parser("rembg", help="배경을 지운다 (image.rembg)")
    q.add_argument("image")
    _common(q, rembg)

    q = s.add_parser("video", help="이미지에서 영상을 만든다 (video.look / video.sprite)")
    q.add_argument("image", help="첫 프레임 이미지")
    q.add_argument("--prompt", help="움직임 설명")
    q.add_argument("--role", choices=["video.look", "video.sprite"], default="video.sprite")
    q.add_argument("--duration", type=float, help="길이(초)")
    q.add_argument("--resolution", help="해상도 (모델의 enum 값. 예: 480p)")
    q.add_argument("--end-image", help="마지막 프레임 이미지. 기본 video.sprite 모델은 받지 않는다 (--role video.look 은 받는다)")
    q.add_argument("--audio", action="store_true", default=None, help="소리를 함께 만든다")
    q.add_argument("--no-audio", dest="audio", action="store_false", help="소리를 만들지 않는다")
    _common(q, video)

    q = s.add_parser("model3d", help="이미지에서 3D 모델(GLB)을 만든다 (model3d.gen)")
    q.add_argument("image")
    q.add_argument("--face-limit", type=int, help="면 수 상한")
    q.add_argument("--pbr", action="store_true", default=None, help="PBR 재질 맵을 만든다")
    q.add_argument("--no-pbr", dest="pbr", action="store_false")
    q.add_argument("--texture", action="store_true", default=None, help="텍스처를 만든다")
    q.add_argument("--no-texture", dest="texture", action="store_false")
    q.add_argument("--quad", action="store_true", default=None, help="사각형 토폴로지")
    _common(q, model3d)

    q = s.add_parser("rig", help="GLB 에 뼈대를 넣는다 (model3d.rig)")
    q.add_argument("mesh", help="GLB 파일")
    q.add_argument("--height", type=float, help="캐릭터 키(미터)")
    q.add_argument("--animate", action="store_true", default=None, help="애니메이션 프리셋을 입힌다")
    q.add_argument("--animation-id", type=int, help="애니메이션 프리셋 ID")
    _common(q, rig)

    q = s.add_parser("sfx", help="효과음을 만든다 (audio.sfx)")
    q.add_argument("prompt")
    q.add_argument("--duration", type=float, help="길이(초). 없으면 모델이 정하고 비용은 추정할 수 없다")
    q.add_argument("--loop", action="store_true", default=None, help="매끄럽게 반복되는 소리")
    _common(q, sfx)

    q = s.add_parser("tts", help="대사를 음성으로 만든다 (audio.tts)")
    q.add_argument("text")
    q.add_argument("--voice")
    q.add_argument("--language", help="언어 코드 (ISO 639-1)")
    _common(q, tts)

    q = s.add_parser("music", help="배경음악을 만든다 (audio.music)")
    q.add_argument("prompt")
    q.add_argument("--duration", type=float, help="길이(초). 없으면 모델이 정하고 비용은 추정할 수 없다")
    q.add_argument("--instrumental", action="store_true", default=None, help="보컬 없는 연주곡으로 고정")
    _common(q, music)
