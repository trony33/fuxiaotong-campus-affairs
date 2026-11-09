from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "diagrams"
MERMAID_CLI = "@mermaid-js/mermaid-cli@11.12.0"
MERMAID_BLOCK = re.compile(r"```mermaid\s*\n(.*?)\n```", re.DOTALL)

SOURCE_MAPS = {
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
}

MERMAID_CONFIG = {
    "theme": "base",
    "securityLevel": "strict",
    "fontFamily": "Microsoft YaHei, Noto Sans SC, Arial, sans-serif",
    "themeVariables": {
        "fontFamily": "Microsoft YaHei, Noto Sans SC, Arial, sans-serif",
        "background": "#ffffff",
        "primaryColor": "#e8f4ee",
        "primaryTextColor": "#18352c",
        "primaryBorderColor": "#2b8061",
        "secondaryColor": "#e5f0f7",
        "secondaryTextColor": "#18352c",
        "secondaryBorderColor": "#4f84a5",
        "tertiaryColor": "#fff0d7",
        "tertiaryTextColor": "#6f4b16",
        "tertiaryBorderColor": "#b87820",
        "lineColor": "#61736a",
        "textColor": "#18352c",
        "mainBkg": "#e8f4ee",
        "nodeBorder": "#2b8061",
        "clusterBkg": "#f8faf8",
        "clusterBorder": "#b8c9bf",
        "actorBkg": "#e8f4ee",
        "actorBorder": "#2b8061",
        "actorTextColor": "#18352c",
        "signalColor": "#61736a",
        "signalTextColor": "#18352c",
        "labelBoxBkgColor": "#fff0d7",
        "labelBoxBorderColor": "#b87820",
        "labelTextColor": "#6f4b16",
    },
    "flowchart": {
        "curve": "linear",
        "htmlLabels": False,
        "nodeSpacing": 34,
        "rankSpacing": 42,
        "useMaxWidth": True,
    },
    "sequence": {
        "actorMargin": 42,
        "diagramMarginX": 24,
        "diagramMarginY": 18,
        "messageMargin": 32,
        "mirrorActors": False,
        "useMaxWidth": True,
        "wrap": True,
    },
}


def find_npx() -> str:
    executable = shutil.which("npx.cmd") or shutil.which("npx")
    if not executable:
        raise SystemExit("未找到 npx。请安装 Node.js 20+ 后重新生成 Mermaid 图示。")
    return executable


def extract_blocks(source_path: Path, expected_names: list[str]) -> list[str]:
    blocks = MERMAID_BLOCK.findall(source_path.read_text(encoding="utf-8"))
    if len(blocks) != len(expected_names):
        raise ValueError(
            f"{source_path.name} 包含 {len(blocks)} 个 Mermaid 块，"
            f"但图示映射定义了 {len(expected_names)} 个文件"
        )
    return [block.strip() + "\n" for block in blocks]


def render_block(
    npx: str,
    source: str,
    output_path: Path,
    build_dir: Path,
    config_path: Path,
) -> None:
    input_path = build_dir / f"{output_path.stem}.mmd"
    input_path.write_text(source, encoding="utf-8")
    command = [
        npx,
        "--yes",
        MERMAID_CLI,
        "--input",
        str(input_path),
        "--output",
        str(output_path),
        "--configFile",
        str(config_path),
        "--backgroundColor",
        "white",
        "--width",
        "1800",
        "--quiet",
    ]
    try:
        subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    except subprocess.CalledProcessError as exc:
        details = (exc.stderr or exc.stdout or "Mermaid CLI 未返回错误详情").strip()
        raise RuntimeError(f"生成 {output_path.name} 失败：\n{details}") from exc

    ET.parse(output_path)
    rendered = output_path.read_text(encoding="utf-8")
    if "<svg" not in rendered or "Syntax error" in rendered:
        raise RuntimeError(f"{output_path.name} 不是有效的 Mermaid SVG 输出")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    npx = find_npx()
    rendered_count = 0

    with tempfile.TemporaryDirectory(prefix="campus-affairs-mermaid-") as temp_dir:
        build_dir = Path(temp_dir)
        config_path = build_dir / "mermaid-config.json"
        config_path.write_text(
            json.dumps(MERMAID_CONFIG, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        for source_name, output_names in SOURCE_MAPS.items():
            source_path = ROOT / source_name
            blocks = extract_blocks(source_path, output_names)
            for source, output_name in zip(blocks, output_names, strict=True):
                output_path = OUT / output_name
                render_block(npx, source, output_path, build_dir, config_path)
                rendered_count += 1
                print(f"wrote {output_name} from {source_name}")

    print(f"rendered {rendered_count} Mermaid diagrams")


if __name__ == "__main__":
    main()
