# /// script
# dependencies = ["markdown>=3.6", "pygments>=2.17"]
# ///
"""교육 자료의 Markdown 을 같은 자리에 HTML 로 만든다.

    uv run docs/education/build_html.py

각 `X.md` 옆에 `X.html` 을 쓰고 `README.md` 는 `index.html` 이 된다.
같은 폴더에 두기 때문에 그림과 저장소 파일을 가리키는 상대 링크가 그대로 맞는다.
"""

import html
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
SKIP = {"_writing-notes.md"}
GROUPS = {
    "": "시작",
    "explanations": "설명",
    "tutorials": "학습",
    "how-tos": "문제 해결",
    "reference": "참조",
}

TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · gameforge 교육 자료</title>
<link rel="stylesheet" href="{base}assets/style.css">
</head>
<body>
<header class="top">
  <a class="brand" href="{base}index.html">gameforge 교육 자료</a>
  <button class="menu" aria-label="목차 열기" onclick="document.body.classList.toggle('nav-open')">목차</button>
</header>
<div class="layout">
<nav class="side" aria-label="문서 목차">
{nav}
</nav>
<main>
<article>
{badge}
{body}
</article>
<footer class="pager">
{prev}
{next}
</footer>
</main>
<aside class="toc" aria-label="이 문서의 목차">
{toc}
</aside>
</div>
</body>
</html>
"""


def title_of(text: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else fallback


def doc_type_of(text: str) -> str | None:
    match = re.search(r"^>\s*문서 유형:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def out_path(md: Path) -> Path:
    if md.name == "README.md" and md.parent == ROOT:
        return ROOT / "index.html"
    return md.with_suffix(".html")


def ordered_pages() -> list[Path]:
    """README 에 링크된 순서를 학습 순서로 쓴다. 링크되지 않은 문서는 뒤에 붙인다."""
    readme = ROOT / "README.md"
    pages = [readme]
    for target in re.findall(r"\]\(([^)#]+\.md)(?:#[^)]*)?\)", readme.read_text()):
        path = (ROOT / target).resolve()
        if path.is_file() and ROOT in path.parents and path not in pages and path.name not in SKIP:
            pages.append(path)
    for path in sorted(ROOT.rglob("*.md")):
        if path not in pages and path.name not in SKIP:
            pages.append(path)
    return pages


def rewrite_links(body: str, md: Path) -> str:
    """교육 자료 안의 .md 링크만 .html 로 바꾼다. 저장소의 다른 파일 링크는 그대로 둔다."""

    def swap(match: re.Match) -> str:
        href, anchor = match.group(1), match.group(2) or ""
        target = (md.parent / href).resolve()
        if ROOT not in target.parents and target != ROOT:
            return match.group(0)
        if not target.is_file() or target.name in SKIP:
            return match.group(0)
        new = out_path(target)
        rel = Path(*([".."] * len(md.parent.relative_to(ROOT).parts))) / new.relative_to(ROOT)
        return f'href="{rel.as_posix()}{anchor}"'

    return re.sub(r'href="([^":#]+\.md)(#[^"]*)?"', swap, body)


def nav_html(pages: list[Path], current: Path, base: str, titles: dict[Path, str]) -> str:
    groups: dict[str, list[Path]] = {key: [] for key in GROUPS}
    for page in pages:
        key = page.parent.relative_to(ROOT).as_posix()
        groups.setdefault("" if key == "." else key, []).append(page)
    parts = []
    for key, label in GROUPS.items():
        if not groups.get(key):
            continue
        parts.append(f'<p class="group">{label}</p><ul>')
        for page in groups[key]:
            href = base + out_path(page).relative_to(ROOT).as_posix()
            active = ' class="active" aria-current="page"' if page == current else ""
            parts.append(f'<li><a{active} href="{href}">{html.escape(titles[page])}</a></li>')
        parts.append("</ul>")
    return "\n".join(parts)


def build() -> int:
    pages = ordered_pages()
    texts = {page: page.read_text() for page in pages}
    titles = {page: title_of(texts[page], page.stem) for page in pages}
    for index, page in enumerate(pages):
        depth = len(page.parent.relative_to(ROOT).parts)
        base = "../" * depth
        text = re.sub(r"^>\s*문서 유형:.*\n", "", texts[page], flags=re.MULTILINE)
        converter = markdown.Markdown(
            extensions=["tables", "fenced_code", "codehilite", "toc", "sane_lists"],
            extension_configs={
                "codehilite": {"guess_lang": False, "css_class": "code"},
                "toc": {"toc_depth": "2-3", "permalink": False},
            },
        )
        body = rewrite_links(converter.convert(text), page)
        body = body.replace("<table>", '<div class="table"><table>').replace("</table>", "</table></div>")
        kind = doc_type_of(texts[page])
        badge = f'<p class="badge">{html.escape(kind)}</p>' if kind else ""
        toc = converter.toc if converter.toc_tokens else ""

        def pager(target: Path | None, label: str, css: str) -> str:
            if target is None:
                return "<span></span>"
            href = base + out_path(target).relative_to(ROOT).as_posix()
            return f'<a class="{css}" href="{href}"><small>{label}</small>{html.escape(titles[target])}</a>'

        out_path(page).write_text(
            TEMPLATE.format(
                title=html.escape(titles[page]),
                base=base,
                nav=nav_html(pages, page, base, titles),
                badge=badge,
                body=body,
                toc=f"<p>이 문서에서</p>{toc}" if toc else "",
                prev=pager(pages[index - 1] if index else None, "이전", "prev"),
                next=pager(pages[index + 1] if index + 1 < len(pages) else None, "다음", "next"),
            )
        )
    return len(pages)


if __name__ == "__main__":
    print(f"{build()}개 문서를 HTML 로 만들었다")
