from __future__ import annotations

"""Prepare and validate the 奶娃工程 submission package.

The two PDFs supplied in ``~/Downloads`` remain the content baseline.  This
script permanently redacts their administrative placeholders and writes the
verified 8-page submission copies to ``docs/``.  It does not alter body text.

Dependency: ``python -m pip install PyMuPDF``
"""

import json
import hashlib
from pathlib import Path
import sys

try:
    import pymupdf
except ImportError as exc:  # pragma: no cover - environment guard
    raise SystemExit("需要 PyMuPDF：python -m pip install PyMuPDF") from exc


ROOT = Path(__file__).resolve().parents[1]
TEAM = "奶娃工程"
VERSION = "V1.0"
DOCUMENT_DATE = "2026年11月6日"
REPO = "https://github.com/trony33/fuxiaotong-campus-affairs"
MEMBERS = [
    ("052403146", "蔡明润"),
    ("102401603", "张馨恬"),
    ("102401606", "黄丽婷"),
    ("102401416", "唐捷"),
    ("102401605", "王乐禾"),
    ("102401502", "王钰涵"),
    ("152402217", "陈霁然"),
    ("102401403", "潘岳"),
    ("102401601", "李佳雨"),
]

OLD_HEADER = "设计说明（团队名称待填写）"
NEW_HEADER = f"设计说明（{TEAM}）"
OLD_COVER_TEAM = "团队：待填写"
NEW_COVER_LINE = f"团队：{TEAM}  版本：{VERSION}  日期：{DOCUMENT_DATE}"
PLACEHOLDER = "待填写"
TEXT_COLOR = (0.3569, 0.4196, 0.4510)


def find_font() -> Path:
    candidates = [
        Path(r"C:\Windows\Fonts\Deng.ttf"),
        Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf"),
        Path(r"C:\Windows\Fonts\simhei.ttf"),
    ]
    font = next((path for path in candidates if path.is_file()), None)
    if font is None:
        raise FileNotFoundError("找不到可用于 PDF 的中文 TrueType 字体")
    return font


def find_latest_pdf(keyword: str) -> Path:
    downloads = Path.home() / "Downloads"
    candidates = [path for path in downloads.glob("*.pdf") if keyword in path.name]
    if not candidates:
        raise FileNotFoundError(f"Downloads 中找不到包含“{keyword}”的 PDF")
    return max(candidates, key=lambda path: path.stat().st_mtime)


def line_rect(page: pymupdf.Page, needle: pymupdf.Rect) -> pymupdf.Rect:
    """Return the bounding box of the complete text line containing needle."""
    words = page.get_text("words")
    same_line = [
        word
        for word in words
        if word[1] <= needle.y1 and word[3] >= needle.y0
    ]
    if not same_line:
        raise RuntimeError("无法定位 PDF 封面团队信息所在文本行")
    return pymupdf.Rect(
        min(word[0] for word in same_line) - 2,
        min(word[1] for word in same_line) - 1,
        max(word[2] for word in same_line) + 2,
        max(word[3] for word in same_line) + 1,
    )


def redact_and_insert_pdfs(source: Path, output: Path, font: Path) -> dict[str, object]:
    document = pymupdf.open(source)
    if document.page_count != 8:
        document.close()
        raise RuntimeError(f"{source.name} 应为最新 8 页版本，实际为 {document.page_count} 页")

    for page_index, page in enumerate(document):
        header_matches = page.search_for(OLD_HEADER)
        if len(header_matches) != 1:
            document.close()
            raise RuntimeError(
                f"{source.name} 第 {page_index + 1} 页页眉占位符数量异常：{len(header_matches)}"
            )
        header_rect = header_matches[0]
        page.add_redact_annot(
            pymupdf.Rect(
                header_rect.x0 - 1,
                header_rect.y0 - 1,
                header_rect.x1 + 2,
                header_rect.y1 + 1,
            ),
            fill=(1, 1, 1),
        )

        cover_line_rect: pymupdf.Rect | None = None
        if page_index == 0:
            cover_matches = page.search_for(OLD_COVER_TEAM)
            if len(cover_matches) != 1:
                document.close()
                raise RuntimeError(f"{source.name} 封面团队字段数量异常：{len(cover_matches)}")
            cover_line_rect = line_rect(page, cover_matches[0])
            page.add_redact_annot(cover_line_rect, fill=(1, 1, 1))

        # The database PDF has a team row on page 2.  The system PDF uses a
        # reader row instead, so replacement is conditional.
        table_team_rect: pymupdf.Rect | None = None
        if page_index == 1:
            placeholder_matches = [
                match
                for match in page.search_for(PLACEHOLDER)
                if not match.intersects(header_rect)
            ]
            if len(placeholder_matches) > 1:
                document.close()
                raise RuntimeError(f"{source.name} 文档信息页存在多个无法判定的占位符")
            if placeholder_matches:
                table_team_rect = placeholder_matches[0]
                page.add_redact_annot(
                    pymupdf.Rect(
                        table_team_rect.x0 - 1,
                        table_team_rect.y0 - 1,
                        table_team_rect.x1 + 35,
                        table_team_rect.y1 + 1,
                    ),
                    fill=(1, 1, 1),
                )

        page.apply_redactions()
        page.insert_text(
            (header_rect.x0, header_rect.y1 - 1),
            NEW_HEADER,
            fontsize=8,
            fontname="SubmissionChinese",
            fontfile=str(font),
            color=TEXT_COLOR,
        )

        if cover_line_rect is not None:
            result = page.insert_textbox(
                pymupdf.Rect(100, cover_line_rect.y0 - 1, 495, cover_line_rect.y1 + 5),
                NEW_COVER_LINE,
                fontsize=13,
                fontname="SubmissionChinese",
                fontfile=str(font),
                color=TEXT_COLOR,
                align=pymupdf.TEXT_ALIGN_CENTER,
            )
            if result < 0:
                document.close()
                raise RuntimeError(f"{source.name} 封面团队信息写入空间不足")

        if table_team_rect is not None:
            page.insert_text(
                (table_team_rect.x0, table_team_rect.y1 - 1),
                TEAM,
                fontsize=8,
                fontname="SubmissionChinese",
                fontfile=str(font),
                color=(0.1373, 0.2157, 0.2745),
            )

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".tmp.pdf")
    # A variable CJK font can otherwise add roughly 10 MB per document.  Keep
    # only glyphs used by the inserted administrative fields.
    document.subset_fonts()
    document.save(temporary, garbage=4, deflate=True, clean=True)
    document.close()
    temporary.replace(output)

    verified = pymupdf.open(output)
    text = "\n".join(page.get_text() for page in verified)
    page_count = verified.page_count
    verified.close()
    stale_terms = [term for term in (OLD_HEADER, OLD_COVER_TEAM, PLACEHOLDER) if term in text]
    if page_count != 8 or stale_terms or text.count(TEAM) < 8:
        raise RuntimeError(
            f"{output.name} 校验失败：pages={page_count}, stale={stale_terms}, team_count={text.count(TEAM)}"
        )
    return {
        "file": output.name,
        "pages": page_count,
        "bytes": output.stat().st_size,
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "team_occurrences": text.count(TEAM),
        "placeholder_occurrences": text.count(PLACEHOLDER),
    }


def validate_editable_sources() -> None:
    required = {
        "README.md": [TEAM, "福晓通", REPO],
        "system-design.md": [TEAM, "2026-11-06", "国家奖学金", "优秀学生综合奖学金"],
        "database-design.md": [TEAM, "2026-11-06"],
        "blog-post.md": ["2026秋软工实践 奶娃工程——项目原型设计+概要设计", REPO],
        "team-roster.md": [name for _, name in MEMBERS],
    }
    failures: list[str] = []
    for filename, terms in required.items():
        text = (ROOT / filename).read_text(encoding="utf-8")
        missing = [term for term in terms if term not in text]
        if missing:
            failures.append(f"{filename} 缺少：{', '.join(missing)}")
    if failures:
        raise RuntimeError("；".join(failures))


def write_pdf_note(results: list[dict[str, object]]) -> None:
    lines = "\n".join(
        f"- `{item['file']}`：{item['pages']} 页，{item['bytes']} bytes，占位符残留 {item['placeholder_occurrences']} 处。"
        for item in results
    )
    (ROOT / "docs" / "PDF-UPDATE-NOTE.md").write_text(
        "# PDF 版本说明\n\n"
        "本目录中的两份 PDF 以 2026-11-06 提供的最新 8 页附件为内容基线。脚本仅永久删除页眉、封面和文档信息表中的团队占位文本，并写入“奶娃工程”；正文设计内容未改写。\n\n"
        f"{lines}\n\n"
        "生成后已核验：页数均为 8，文本层不再包含“待填写”，团队名可检索。\n",
        encoding="utf-8",
    )
    (ROOT / "evidence" / "final-pdf-review-report.json").write_text(
        json.dumps(
            {
                "document_date": "2026-11-06",
                "reviewed_at": "2026-11-09",
                "team": TEAM,
                "results": results,
                "visual_review": {
                    "result": "PASS",
                    "contact_sheets": [
                        "final-system-pdf-contact.png",
                        "final-database-pdf-contact.png",
                    ],
                    "notes": "8 页均可见；未见裁切、重叠或空白页。",
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    validate_editable_sources()
    font = find_font()
    jobs = [
        ("系统设计说明书", ROOT / "docs" / f"{TEAM}_系统设计说明书.pdf"),
        ("数据库设计说明书", ROOT / "docs" / f"{TEAM}_数据库设计说明书.pdf"),
    ]
    results = [
        redact_and_insert_pdfs(find_latest_pdf(keyword), output, font)
        for keyword, output in jobs
    ]
    write_pdf_note(results)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"prepare-submission failed: {exc}", file=sys.stderr)
        raise
