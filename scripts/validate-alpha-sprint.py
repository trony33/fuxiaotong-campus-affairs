from __future__ import annotations

"""Validate the Alpha sprint submission package.

The default mode checks structure and the evidence that already exists in the
repository.  ``--strict`` is intentionally stricter: it is the final-submit
gate and refuses to pass while team-confirmation placeholders remain.

This script uses only the Python standard library so it can run in CI without
installing the document-generation dependencies.
"""

import argparse
import csv
import json
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
ALPHA = ROOT / "alpha-sprint"
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
EXPECTED_LOG_DAYS = [f"day-{day:02d}.md" for day in range(1, 15)]
# These patterns intentionally target bracketed field values rather than prose
# such as “待补录项必须由成员确认”.  Otherwise the final-submit gate could
# remain red even after all actual data had been entered.
PLACEHOLDER_PATTERNS = (
    re.compile(r"\[(?:待|需)[^\]\r\n]+\]"),
    re.compile(r"\[队长发布后补入\]"),
)


class Validation:
    def __init__(self, strict: bool = False) -> None:
        self.strict = strict
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)

    def require_file(self, relative: str) -> Path | None:
        path = ROOT / relative
        if not path.is_file():
            self.error(f"缺少文件：{relative}")
            return None
        return path

    def read_text(self, relative: str) -> str:
        path = self.require_file(relative)
        if path is None:
            return ""
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            self.error(f"文件不是 UTF-8：{relative}（{exc}）")
            return ""

    def check_required_files(self) -> None:
        required = [
            "alpha-sprint/README.md",
            "alpha-sprint/FACT-REGISTER.md",
            "alpha-sprint/sprint-plan.md",
            "alpha-sprint/sprint-summary.md",
            "alpha-sprint/meeting-log.md",
            "alpha-sprint/workload.csv",
            "alpha-sprint/burndown.csv",
            "alpha-sprint/risks-and-issues.md",
            "alpha-sprint/test-plan.md",
            "alpha-sprint/vlog-script.md",
            "alpha-sprint/ppt-outline.md",
            "alpha-sprint/policy-evidence.md",
            "alpha-sprint/api-contract.md",
            "docs/alpha-sprint-defense.pptx",
            "scripts/validate-alpha-sprint.py",
        ]
        for relative in required:
            self.require_file(relative)

        logs = ALPHA / "daily-logs"
        for filename in EXPECTED_LOG_DAYS:
            path = logs / filename
            if not path.is_file():
                self.error(f"缺少 14 天日志：alpha-sprint/daily-logs/{filename}")

    def check_team_members(self) -> None:
        roster = self.read_text("team-roster.md")
        plan = self.read_text("alpha-sprint/sprint-plan.md")
        summary = self.read_text("alpha-sprint/sprint-summary.md")
        for student_id, name in MEMBERS:
            for label, text in (("team-roster.md", roster), ("sprint-plan.md", plan), ("sprint-summary.md", summary)):
                if student_id not in text or name not in text:
                    self.error(f"{label} 缺少成员：{student_id}-{name}")

    def check_links(self) -> None:
        files = [
            "alpha-sprint/sprint-plan.md",
            "alpha-sprint/sprint-summary.md",
            "alpha-sprint/README.md",
        ]
        required_urls = (
            "https://github.com/trony33/fuxiaotong-campus-affairs",
            "https://edu.cnblogs.com/campus/fzu/202601SofwareEngineering",
        )
        for relative in files:
            text = self.read_text(relative)
            for url in required_urls:
                if url not in text:
                    self.error(f"{relative} 缺少链接：{url}")

        # Catch malformed explicit HTTP(S) links while allowing placeholders.
        url_pattern = re.compile(r"https?://[^\s)>'\"]+")
        for relative in files:
            for url in url_pattern.findall(self.read_text(relative)):
                parsed = urlparse(url.rstrip(".,"))
                if not parsed.netloc:
                    self.error(f"链接格式异常：{relative}: {url}")

    def check_evidence_json(self) -> None:
        path = self.require_file("evidence/prototype-smoke-report.json")
        if path is None:
            return
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            self.error(f"原型冒烟报告不是有效 JSON：{exc}")
            return
        summary = report.get("summary", {})
        if summary.get("total") != 12 or summary.get("passed") != 12 or summary.get("failed") != 0:
            self.error("原型冒烟报告不是 12/12 PASS：请核对 evidence/prototype-smoke-report.json")
        if len(report.get("tests", [])) != 12:
            self.error("原型冒烟报告测试条目数量不是 12")

        viewport = self.require_file("evidence/viewport-report.json")
        if viewport is not None:
            try:
                viewport_report = json.loads(viewport.read_text(encoding="utf-8"))
                checks = viewport_report.get("checks", {})
                if checks.get("noElementOverflow") is not True or checks.get("noDocumentHorizontalScroll") is not True:
                    self.error("响应式报告未确认无元素越界和横向滚动")
                expected_widths = {320, 390, 760, 768, 1024, 1440}
                if set(viewport_report.get("widths", [])) != expected_widths:
                    self.error("响应式报告未覆盖约定的六个视口")
            except json.JSONDecodeError as exc:
                self.error(f"响应式报告不是有效 JSON：{exc}")

    def check_csv(self) -> None:
        workload = self.require_file("alpha-sprint/workload.csv")
        if workload is not None:
            with workload.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(row for row in handle if not row.startswith("#")))
            expected_ids = [student_id for student_id, _ in MEMBERS] + ["TOTAL"]
            actual_ids = [row.get("member_id") for row in rows]
            if actual_ids != expected_ids:
                self.error(f"工作量表成员顺序/数量错误：{actual_ids}")
            if rows and rows[-1].get("workload_percent") != "100%":
                self.error("工作量表合计行必须为 100%")

        burndown = self.require_file("alpha-sprint/burndown.csv")
        if burndown is not None:
            with burndown.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(row for row in handle if not row.startswith("#")))
            if len(rows) != 14:
                self.error(f"燃尽图应有 14 天数据，实际为 {len(rows)}")
            else:
                days = [int(row["day"]) for row in rows]
                if days != list(range(1, 15)):
                    self.error("燃尽图 day 必须从 1 连续到 14")
                planned = [float(row["planned_remaining_hours"]) for row in rows]
                if planned[0] <= planned[-1] or planned[-1] != 0:
                    self.error("计划燃尽曲线必须从正数下降到 0")
                actual = [row.get("actual_remaining_hours", "") for row in rows]
                if all(actual):
                    try:
                        actual_values = [float(value) for value in actual]
                        if any(value < 0 for value in actual_values):
                            self.error("实际剩余工作量不能为负数")
                    except ValueError:
                        self.error("燃尽图实际剩余工作量必须是数字")
                elif self.strict:
                    self.error("严格模式要求补齐 14 天实际剩余工作量")
                else:
                    self.warning("实际燃尽曲线尚未补齐；当前只能展示计划曲线")

    def check_ppt(self) -> None:
        path = self.require_file("docs/alpha-sprint-defense.pptx")
        if path is None:
            return
        try:
            with zipfile.ZipFile(path) as archive:
                names = set(archive.namelist())
                required = {"[Content_Types].xml", "ppt/presentation.xml", "ppt/slides/slide1.xml"}
                missing = required - names
                if missing:
                    self.error(f"PPTX 缺少结构文件：{sorted(missing)}")
                slide_count = len([name for name in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)])
                if slide_count < 10:
                    self.error(f"PPT 至少需要 10 页，实际为 {slide_count} 页")
        except (zipfile.BadZipFile, OSError) as exc:
            self.error(f"PPTX 无法读取：{exc}")

    def check_placeholders(self) -> None:
        if not self.strict:
            return
        check_files = [
            "alpha-sprint/sprint-plan.md",
            "alpha-sprint/sprint-summary.md",
            "alpha-sprint/meeting-log.md",
            "alpha-sprint/workload.csv",
            "alpha-sprint/FACT-REGISTER.md",
            "alpha-sprint/risks-and-issues.md",
        ]
        for relative in check_files:
            text = self.read_text(relative)
            for marker in PLACEHOLDER_PATTERNS:
                match = marker.search(text)
                if match:
                    self.error(f"严格模式发现未替换占位符：{relative} -> {match.group(0)}")

        # Every daily record is part of the required process evidence.  Do not
        # check the index/README here because it may legitimately describe the
        # workflow and the placeholder convention.
        for filename in EXPECTED_LOG_DAYS:
            relative = f"alpha-sprint/daily-logs/{filename}"
            text = self.read_text(relative)
            for marker in PLACEHOLDER_PATTERNS:
                match = marker.search(text)
                if match:
                    self.error(f"严格模式发现未替换占位符：{relative} -> {match.group(0)}")

        summary = self.read_text("alpha-sprint/sprint-summary.md")
        if "[待补入最终视频链接或仓库路径]" in summary:
            self.error("严格模式要求在总结中填写 Vlog 成片链接")
        if "[队长发布后补入]" in summary:
            self.error("严格模式要求在总结中填写博客正式链接")

    def run(self) -> int:
        self.check_required_files()
        self.check_team_members()
        self.check_links()
        self.check_evidence_json()
        self.check_csv()
        self.check_ppt()
        self.check_placeholders()

        for warning in self.warnings:
            print(f"WARN: {warning}")
        for error in self.errors:
            print(f"ERROR: {error}")
        if self.errors:
            print(f"验证失败：{len(self.errors)} 个错误，{len(self.warnings)} 个警告。")
            return 1
        print(f"验证通过：结构和既有证据检查完成，{len(self.warnings)} 个警告。")
        if not self.strict:
            print("提示：最终博客提交前请运行 --strict，并先补齐成员、会议、实际工时、Vlog 和实际燃尽图。")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="最终提交门禁：拒绝所有待确认/待补录占位符")
    args = parser.parse_args()
    return Validation(strict=args.strict).run()


if __name__ == "__main__":
    sys.exit(main())
