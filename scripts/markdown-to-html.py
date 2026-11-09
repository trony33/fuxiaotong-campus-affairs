from __future__ import annotations

import html
import re
import sys
from pathlib import Path

try:
    from markdown_it import MarkdownIt
except ImportError as exc:  # pragma: no cover
    raise SystemExit("需要 markdown-it-py：python -m pip install markdown-it-py") from exc


DIAGRAM_MAPS = {
    # The order follows the Mermaid blocks in each source document. Keeping the
    # mapping per document prevents a block in one document from shifting every
    # later image in another document.
    "system-design.md": [
        "context.svg",
        "architecture.svg",
        "agent-flow.svg",
        "use-case.svg",
        "class-model.svg",
        "activity.svg",
        "sequence.svg",
        "fallback-sequence.svg",
        "collaboration.svg",
        "deployment.svg",
    ],
    "database-design.md": [
        "lifecycle.svg",
        "er-model.svg",
        "er-identity.svg",
        "er-evidence.svg",
        "er-workflow.svg",
        "agent-boundary.svg",
    ],
    "blog-post.md": ["architecture.svg"],
}


def replace_mermaid_fences(markdown: str, root: Path, source_name: str) -> str:
    # Static SVGs are used for reliable PDF rendering. Keep the source Mermaid
    # blocks in Markdown, but replace each one with the matching generated SVG.
    mapping = DIAGRAM_MAPS.get(source_name, [])
    pattern = re.compile(r"```mermaid\s*\n.*?\n```", re.S)

    def convert(match: re.Match[str]) -> str:
        index = convert.counter
        convert.counter += 1
        if index >= len(mapping):
            raise ValueError(f"{source_name} contains more Mermaid blocks than its static diagram map")
        filename = mapping[index]
        diagram_class = f"design-diagram-{Path(filename).stem}"
        return (
            f'\n<figure class="design-diagram {diagram_class}">'
            f'<img src="diagrams/{filename}" alt="设计图 {index + 1}" />'
            "</figure>\n"
        )

    convert.counter = 0
    converted = pattern.sub(convert, markdown)
    if convert.counter != len(mapping):
        raise ValueError(
            f"{source_name} contains {convert.counter} Mermaid blocks, "
            f"but its static diagram map contains {len(mapping)} entries"
        )
    for filename in mapping:
        diagram_path = root / "diagrams" / filename
        if not diagram_path.is_file():
            raise FileNotFoundError(f"Missing static diagram: {diagram_path}")
    return converted


def render(md_path: Path, output_path: Path, title: str) -> None:
    markdown = md_path.read_text(encoding="utf-8")
    markdown = replace_mermaid_fences(markdown, md_path.parent, md_path.name)
    # Markdown links to local SVGs are retained; the HTML is always opened from
    # the project folder, so relative links remain portable.
    rendered = MarkdownIt("commonmark", {"html": True, "linkify": True}).enable("table").render(markdown)
    css = """
    @page { size: A4; margin: 18mm 16mm 19mm; }
    :root { color: #18352c; font-family: 'Microsoft YaHei','Noto Sans SC',Arial,sans-serif; }
    body { margin: 0; font-size: 10.2pt; line-height: 1.65; color: #24382f; }
    h1 { break-before: page; page-break-before: always; font-size: 24pt; color: #0b5742; border-bottom: 2px solid #b8d6c3; padding-bottom: 9px; }
    body > h1:first-of-type { break-before: auto; page-break-before: auto; }
    h2 { margin-top: 23px; padding: 7px 10px; border-left: 4px solid #2b8061; background: #edf6f0; color: #174d39; font-size: 16pt; page-break-after: avoid; }
    h3 { margin-top: 17px; color: #2d6950; font-size: 12.5pt; page-break-after: avoid; }
    h4 { color: #506b5d; page-break-after: avoid; }
    p { margin: 7px 0; }
    blockquote { margin: 12px 0; padding: 8px 13px; border-left: 4px solid #d6a45a; background: #fff8eb; color: #6b5a3e; }
    table { width: 100%; border-collapse: collapse; margin: 10px 0 14px; font-size: 8.6pt; line-height: 1.45; break-inside: avoid; page-break-inside: avoid; }
    thead { display: table-header-group; }
    th { background: #e4f1e9; color: #21533d; font-weight: 700; }
    th, td { border: 1px solid #cbdad0; padding: 4px 6px; vertical-align: top; }
    tr { page-break-inside: avoid; }
    code { padding: 1px 3px; border-radius: 3px; background: #f1f4f2; color: #7c4c1e; font-family: Consolas,monospace; font-size: .9em; }
    pre { padding: 10px; overflow-wrap: anywhere; white-space: pre-wrap; background: #f4f7f5; border: 1px solid #d9e3dc; border-radius: 5px; font-size: 8pt; line-height: 1.45; page-break-inside: avoid; }
    img { display: block; width: 100%; max-height: 210mm; object-fit: contain; margin: 12px auto; page-break-inside: avoid; }
    .design-diagram { margin: 12px 0; break-inside: avoid; page-break-inside: avoid; }
    .design-diagram img { margin: 0 auto; }
    @media print {
      .design-diagram-lifecycle img { width: auto; max-width: 100%; height: 150mm; }
    }
    a { color: #126b52; overflow-wrap: anywhere; }
    li { margin: 3px 0; }
    hr { border: 0; border-top: 1px solid #dce6df; margin: 18px 0; }
    .cover-note { padding: 12px 14px; border: 1px solid #d5e5da; border-radius: 6px; background: #f2f8f3; }
    footer { margin-top: 22px; padding-top: 8px; border-top: 1px solid #dce6df; text-align: center; color: #91a097; font-size: 8pt; break-inside: avoid; page-break-inside: avoid; }
    """
    document = f"""<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'><title>{html.escape(title)}</title><style>{css}</style></head><body><div class='cover-note'><strong>校园事务智能办事助手（福晓通）</strong><br>奶娃工程 · 概要设计材料 · V1.0 · 2026-11-06<br>正式墨刀链接与成员具体分工仍待团队确认。</div>{rendered}<footer>{html.escape(title)} · 奶娃工程 · 2026-11-06</footer></body></html>"""
    output_path.write_text(document, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise SystemExit("用法：python markdown-to-html.py input.md output.html 标题")
    render(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3])
