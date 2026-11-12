from __future__ import annotations

"""Build the Alpha sprint defense deck.

The deck is deliberately generated from the repository baseline instead of
embedding claims that are not supported by evidence.  Re-run this script after
the team fills the actual burndown/workload data and replace the marked
"待补录" labels before the final defense.
"""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE, MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "alpha-sprint-defense.pptx"

GREEN = RGBColor(0x12, 0x6B, 0x52)
GREEN_DARK = RGBColor(0x0B, 0x57, 0x42)
GREEN_SOFT = RGBColor(0xE8, 0xF4, 0xEE)
INK = RGBColor(0x17, 0x2B, 0x25)
MUTED = RGBColor(0x6D, 0x7E, 0x75)
LINE = RGBColor(0xD9, 0xE5, 0xDE)
CANVAS = RGBColor(0xF6, 0xF8, 0xF6)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
AMBER = RGBColor(0xA9, 0x6A, 0x12)
AMBER_SOFT = RGBColor(0xFF, 0xF2, 0xDE)
BLUE = RGBColor(0x39, 0x70, 0x9A)
BLUE_SOFT = RGBColor(0xEA, 0xF2, 0xF8)
VIOLET = RGBColor(0x70, 0x5C, 0xA6)
VIOLET_SOFT = RGBColor(0xF1, 0xEE, 0xF9)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
FONT = "Microsoft YaHei"


def set_fill(shape, color: RGBColor, transparency: int = 0) -> None:
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    if transparency:
        shape.fill.transparency = transparency


def set_line(shape, color: RGBColor = LINE, width: float = 1.0, dash=None) -> None:
    shape.line.color.rgb = color
    shape.line.width = Pt(width)
    if dash is not None:
        shape.line.dash_style = dash


def add_box(slide, x, y, w, h, fill=WHITE, line=LINE, radius=True, transparency=0):
    kind = MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE if radius else MSO_AUTO_SHAPE_TYPE.RECTANGLE
    shape = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    set_fill(shape, fill, transparency)
    set_line(shape, line, 0.8 if line != fill else 0)
    return shape


def add_text(slide, text, x, y, w, h, size=16, color=INK, bold=False,
             align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP, margin=0.08,
             font=FONT, italic=False):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(margin)
    tf.margin_right = Inches(margin)
    tf.margin_top = Inches(margin)
    tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return box


def add_rich_text(slide, runs, x, y, w, h, size=14, color=INK, align=PP_ALIGN.LEFT,
                  valign=MSO_ANCHOR.TOP, margin=0.08):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(margin)
    tf.margin_right = Inches(margin)
    tf.margin_top = Inches(margin)
    tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    for item in runs:
        run = p.add_run()
        run.text = item.get("text", "")
        run.font.name = item.get("font", FONT)
        run.font.size = Pt(item.get("size", size))
        run.font.bold = item.get("bold", False)
        run.font.color.rgb = item.get("color", color)
        if item.get("hyperlink"):
            run.hyperlink.address = item["hyperlink"]
    return box


def add_bullets(slide, items, x, y, w, h, size=15, color=INK, bullet_color=GREEN,
                spacing=5):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(0.08)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.04)
    tf.margin_bottom = Inches(0.04)
    for index, item in enumerate(items):
        p = tf.paragraphs[0] if index == 0 else tf.add_paragraph()
        p.text = item
        p.level = 0
        p.font.name = FONT
        p.font.size = Pt(size)
        p.font.color.rgb = color
        p.space_after = Pt(spacing)
        p.bullet = True
    return box


def add_title(slide, kicker, title, subtitle=None, page=None):
    add_text(slide, kicker.upper(), 0.55, 0.35, 5.5, 0.25, size=9, color=GREEN, bold=True)
    add_text(slide, title, 0.55, 0.68, 11.8, 0.58, size=27, color=INK, bold=True)
    if subtitle:
        add_text(slide, subtitle, 0.58, 1.30, 11.5, 0.38, size=11, color=MUTED)
    if page is not None:
        add_text(slide, f"{page:02d}", 12.25, 0.37, 0.5, 0.25, size=9, color=MUTED, align=PP_ALIGN.RIGHT)


def add_footer(slide, label="奶娃工程 · 福晓通 Alpha 冲刺"):
    line = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(0.55), Inches(7.08), Inches(12.2), Inches(0.012))
    set_fill(line, LINE)
    set_line(line, LINE, 0)
    add_text(slide, label, 0.58, 7.12, 5.5, 0.18, size=7.5, color=MUTED)
    add_text(slide, "2026-11-12 初稿 · 结项前更新实际数据", 7.5, 7.12, 5.2, 0.18, size=7.5, color=MUTED, align=PP_ALIGN.RIGHT)


def base_slide(prs, background=CANVAS):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = background
    return slide


def add_metric(slide, x, y, w, h, value, label, fill=WHITE, value_color=GREEN):
    add_box(slide, x, y, w, h, fill=fill, line=LINE)
    add_text(slide, value, x + 0.15, y + 0.18, w - 0.3, 0.45, size=25, color=value_color, bold=True)
    add_text(slide, label, x + 0.15, y + 0.72, w - 0.3, h - 0.82, size=10, color=MUTED)


def add_image(slide, path: Path, x, y, w=None, h=None):
    if not path.is_file():
        add_box(slide, x, y, w or 2, h or 1.2, fill=WHITE, line=LINE)
        add_text(slide, f"素材缺失：{path.name}", x + 0.1, y + 0.35, (w or 2) - 0.2, 0.4, size=9, color=AMBER)
        return
    kwargs = {}
    if w is not None:
        kwargs["width"] = Inches(w)
    if h is not None:
        kwargs["height"] = Inches(h)
    slide.shapes.add_picture(str(path), Inches(x), Inches(y), **kwargs)


def add_table(slide, rows, cols, data, x, y, w, h, header_fill=GREEN, font_size=9):
    table_shape = slide.shapes.add_table(rows, cols, Inches(x), Inches(y), Inches(w), Inches(h))
    table = table_shape.table
    for col in range(cols):
        table.columns[col].width = Inches(w / cols)
    for r in range(rows):
        for c in range(cols):
            cell = table.cell(r, c)
            cell.text = str(data[r][c])
            cell.margin_left = Inches(0.06)
            cell.margin_right = Inches(0.06)
            cell.margin_top = Inches(0.04)
            cell.margin_bottom = Inches(0.04)
            set_fill(cell, header_fill if r == 0 else WHITE)
            cell.border if False else None
            for p in cell.text_frame.paragraphs:
                p.font.name = FONT
                p.font.size = Pt(font_size if r else font_size - 0.3)
                p.font.bold = r == 0
                p.font.color.rgb = WHITE if r == 0 else INK
                p.alignment = PP_ALIGN.LEFT
    return table_shape


def add_line(slide, x1, y1, x2, y2, color=GREEN, width=2, dash=None):
    line = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    set_line(line, color, width, dash)
    return line


def build_deck() -> None:
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    # 1. Cover
    slide = base_slide(prs, GREEN_DARK)
    accent = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.OVAL, Inches(9.2), Inches(-1.0), Inches(5.2), Inches(5.2))
    set_fill(accent, GREEN, 18)
    set_line(accent, GREEN, 0)
    accent2 = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.OVAL, Inches(10.8), Inches(4.2), Inches(3.5), Inches(3.5))
    set_fill(accent2, RGBColor(0xD0, 0xEC, 0xDE), 82)
    set_line(accent2, RGBColor(0xD0, 0xEC, 0xDE), 0)
    add_text(slide, "奶娃工程", 0.72, 0.72, 4, 0.35, size=13, color=RGBColor(0xB9, 0xE1, 0xCD), bold=True)
    add_text(slide, "福晓通", 0.68, 1.55, 6, 0.9, size=48, color=WHITE, bold=True)
    add_text(slide, "校园事务智能办事助手", 0.73, 2.55, 6.5, 0.5, size=21, color=RGBColor(0xE3, 0xF3, 0xEB))
    add_text(slide, "Alpha 冲刺答辩 · 14 天过程与阶段成果", 0.75, 3.45, 6.5, 0.4, size=14, color=RGBColor(0xB9, 0xD6, 0xC8))
    add_box(slide, 0.72, 5.55, 5.7, 0.72, fill=RGBColor(0x0E, 0x61, 0x4B), line=RGBColor(0x3A, 0x8B, 0x6E))
    add_text(slide, "2026.11.08—2026.11.21  ·  GitHub 交付包", 0.9, 5.76, 5.3, 0.25, size=11, color=WHITE)
    add_text(slide, "课程：202601 软件工程（福州大学）", 0.76, 6.55, 5.5, 0.25, size=9, color=RGBColor(0xB9, 0xD6, 0xC8))
    add_text(slide, "当前版本包含初稿标识；结项时更新实际数据", 7.35, 6.55, 5.2, 0.25, size=9, color=RGBColor(0xB9, 0xD6, 0xC8), align=PP_ALIGN.RIGHT)

    # 2. Problem/value
    slide = base_slide(prs)
    add_title(slide, "01 · 项目起点", "先解决“找得到”，再解决“办得成”", "福晓通面向福州大学学生，把政策、流程、材料和提醒组织成一条可核验的办事路径。", 2)
    add_metric(slide, 0.65, 2.0, 2.65, 1.35, "71.43%", "受访者认为信息分散是主要困难", GREEN_SOFT, GREEN)
    add_metric(slide, 3.55, 2.0, 2.65, 1.35, "73.22%", "愿意使用校园事务智能办事助手", BLUE_SOFT, BLUE)
    add_metric(slide, 6.45, 2.0, 2.65, 1.35, "78.58%", "希望获得截止时间提醒", AMBER_SOFT, AMBER)
    add_metric(slide, 9.35, 2.0, 2.65, 1.35, "73.21%", "担心回答不准确或来源不可靠", VIOLET_SOFT, VIOLET)
    add_box(slide, 0.65, 3.85, 5.75, 2.15, fill=WHITE, line=LINE)
    add_text(slide, "用户真正需要的不是“万能聊天”", 0.9, 4.1, 5.1, 0.35, size=17, color=INK, bold=True)
    add_bullets(slide, ["知道哪一版政策适用", "知道下一步先做什么", "知道材料是否齐全", "知道回答何时需要人工核验"], 0.95, 4.65, 4.9, 1.05, size=12)
    add_box(slide, 6.7, 3.85, 5.75, 2.15, fill=GREEN_DARK, line=GREEN_DARK)
    add_text(slide, "产品判断", 6.98, 4.1, 2, 0.3, size=10, color=RGBColor(0xB9, 0xE1, 0xCD), bold=True)
    add_text(slide, "把“答案”拆成证据、风险和动作", 6.96, 4.48, 4.9, 0.8, size=23, color=WHITE, bold=True)
    add_text(slide, "有证据才给结论；没有证据就保守降级，并把用户引向官方渠道。", 6.98, 5.43, 4.9, 0.4, size=11, color=RGBColor(0xD6, 0xEA, 0xE0))
    add_footer(slide)

    # 3. Baseline
    slide = base_slide(prs)
    add_title(slide, "02 · 上阶段基线", "从原型与设计包开始冲刺", "上次作业已经把产品语言、系统边界和验证证据搭起来；Alpha 要把它变成可持续推进的工程基线。", 3)
    add_image(slide, ROOT / "evidence" / "viewport-1440.png", 0.65, 1.95, w=6.35)
    add_box(slide, 7.35, 1.95, 5.2, 4.35, fill=WHITE, line=LINE)
    add_text(slide, "已有交付", 7.65, 2.22, 2.2, 0.3, size=16, color=GREEN, bold=True)
    add_bullets(slide, [
        "可交互离线原型：问答、办事指南、清单、提醒、画像、管理端",
        "系统设计书、数据库设计书与 16 张 UML/数据库图示",
        "原型冒烟 12/12 PASS；六个视口无横向溢出",
        "墨刀公开只读预览与本地运行入口",
    ], 7.62, 2.72, 4.55, 1.8, size=11.5, spacing=7)
    add_box(slide, 7.62, 4.9, 4.55, 1.05, fill=AMBER_SOFT, line=RGBColor(0xF1, 0xDF, 0xBF))
    add_text(slide, "边界必须说清", 7.82, 5.1, 1.7, 0.25, size=11, color=AMBER, bold=True)
    add_text(slide, "当前仓库仍以原型与设计为主，不等于真实后端、审批或通知服务已经上线。", 7.82, 5.4, 4.05, 0.4, size=9.5, color=RGBColor(0x8A, 0x7A, 0x62))
    add_footer(slide)

    # 4. Plan
    slide = base_slide(prs)
    add_title(slide, "03 · Alpha 计划", "14 天只做一件事：验证最小闭环", "计划区间：2026-11-08—2026-11-21；站会约 10 分钟，细节问题转 Issue 或专项会议。", 4)
    stages = [
        ("启动与冻结", "11/08—11/09", "P0、角色、证据格式"),
        ("原型与契约", "11/10—11/12", "稳定演示闭环"),
        ("实现与联调", "11/13—11/16", "证据与最小实现"),
        ("测试与修复", "11/17—11/19", "回归与风险收敛"),
        ("发布与包装", "11/20—11/21", "PPT、Vlog、博客"),
    ]
    x = 0.68
    for i, (name, date, detail) in enumerate(stages):
        width = 2.35
        fill = GREEN_SOFT if i < 2 else WHITE
        add_box(slide, x, 2.05, width, 1.35, fill=fill, line=LINE)
        add_text(slide, f"0{i+1}", x + 0.14, 2.22, 0.38, 0.27, size=10, color=GREEN, bold=True)
        add_text(slide, name, x + 0.58, 2.19, 1.58, 0.28, size=13, color=INK, bold=True)
        add_text(slide, date, x + 0.58, 2.57, 1.55, 0.22, size=9, color=GREEN)
        add_text(slide, detail, x + 0.58, 2.88, 1.55, 0.28, size=9, color=MUTED)
        if i < len(stages) - 1:
            add_line(slide, x + width, 2.72, x + width + 0.27, 2.72, color=GREEN, width=2)
        x += 2.55
    add_box(slide, 0.68, 4.05, 12.0, 1.85, fill=WHITE, line=LINE)
    add_text(slide, "P0 验收口径", 0.98, 4.32, 2.0, 0.3, size=16, color=GREEN, bold=True)
    cards = [
        ("闭环", "提问 → 证据/风险 → 清单或提醒"),
        ("证据", "来源、版本、适用对象、核验状态"),
        ("质量", "测试报告、风险清单、可回滚 release"),
        ("协作", "14 天日志、实际工时、PPT、Vlog"),
    ]
    for i, (head, body) in enumerate(cards):
        cx = 3.0 + (i % 2) * 4.55
        cy = 4.22 + (i // 2) * 0.72
        add_text(slide, head, cx, cy, 0.65, 0.22, size=11, color=INK, bold=True)
        add_text(slide, body, cx + 0.78, cy, 3.45, 0.28, size=10, color=MUTED)
    add_footer(slide)

    # 5. Burndown
    slide = base_slide(prs)
    add_title(slide, "04 · 进度追踪", "燃尽图：计划曲线已建立，实际曲线待每日补录", "答辩时必须用真实日志更新实际剩余工作量；当前不把计划曲线冒充实际进度。", 5)
    chart_x, chart_y, chart_w, chart_h = 0.9, 2.0, 8.15, 3.95
    add_box(slide, chart_x - 0.2, chart_y - 0.2, chart_w + 0.45, chart_h + 0.5, fill=WHITE, line=LINE)
    for i in range(5):
        yy = chart_y + i * (chart_h / 4)
        add_line(slide, chart_x, yy, chart_x + chart_w, yy, color=LINE, width=0.7)
        add_text(slide, str(78 - i * 19.5), chart_x - 0.52, yy - 0.1, 0.4, 0.2, size=8, color=MUTED, align=PP_ALIGN.RIGHT)
    for i in range(14):
        xx = chart_x + i * (chart_w / 13)
        add_line(slide, xx, chart_y, xx, chart_y + chart_h, color=RGBColor(0xEE, 0xF2, 0xEF), width=0.5)
        if i in (0, 3, 6, 9, 13):
            add_text(slide, f"D{i+1}", xx - 0.15, chart_y + chart_h + 0.1, 0.32, 0.2, size=8, color=MUTED, align=PP_ALIGN.CENTER)
    planned = [78 - i * 6 for i in range(14)]
    planned[-1] = 0
    def point(i, value):
        return chart_x + i * (chart_w / 13), chart_y + chart_h - (value / 78) * chart_h
    for i in range(13):
        x1, y1 = point(i, planned[i])
        x2, y2 = point(i + 1, planned[i + 1])
        add_line(slide, x1, y1, x2, y2, color=GREEN, width=2.5)
    for i in range(14):
        x1, y1 = point(i, planned[i])
        dot = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.OVAL, Inches(x1 - 0.055), Inches(y1 - 0.055), Inches(0.11), Inches(0.11))
        set_fill(dot, GREEN)
        set_line(dot, GREEN, 0)
    # Placeholder actual line: a light dashed baseline to communicate missing data.
    add_line(slide, chart_x, chart_y + chart_h * 0.78, chart_x + chart_w, chart_y + chart_h * 0.78, color=RGBColor(0xB8, 0xC4, 0xBD), width=1.4, dash=MSO_LINE_DASH_STYLE.DASH)
    add_text(slide, "实际曲线：待补录", chart_x + 5.85, chart_y + chart_h * 0.78 - 0.28, 1.8, 0.25, size=9, color=MUTED)
    add_box(slide, 9.55, 2.0, 2.85, 3.95, fill=WHITE, line=LINE)
    add_text(slide, "当前读法", 9.85, 2.28, 2.2, 0.3, size=16, color=GREEN, bold=True)
    add_text(slide, "计划总量", 9.85, 2.95, 1.0, 0.2, size=9, color=MUTED)
    add_text(slide, "78 h", 11.25, 2.88, 0.75, 0.3, size=18, color=INK, bold=True, align=PP_ALIGN.RIGHT)
    add_text(slide, "实际剩余", 9.85, 3.55, 1.0, 0.2, size=9, color=MUTED)
    add_text(slide, "待补录", 11.0, 3.48, 1.0, 0.3, size=15, color=AMBER, bold=True, align=PP_ALIGN.RIGHT)
    add_text(slide, "数据来源", 9.85, 4.16, 1.0, 0.2, size=9, color=MUTED)
    add_text(slide, "burndown.csv\n+ 每日日志", 9.85, 4.45, 2.1, 0.55, size=11, color=INK, bold=True)
    add_box(slide, 9.85, 5.25, 2.1, 0.42, fill=AMBER_SOFT, line=AMBER_SOFT)
    add_text(slide, "计划 ≠ 实际", 10.08, 5.37, 1.65, 0.16, size=9, color=AMBER, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide)

    # 6. Architecture
    slide = base_slide(prs)
    add_title(slide, "05 · 实际架构", "用证据门禁把 Agent 放在可控边界内", "当前为设计架构基线；后端实现、部署和真实模型调用状态需在结项时按证据更新。", 6)
    layers = [
        ("表示层", "Web / H5 用户端 · 管理端", BLUE_SOFT, BLUE),
        ("应用层", "API · 鉴权 · 会话 · 政策 · 清单 · 提醒", GREEN_SOFT, GREEN),
        ("领域层", "事务 Agent · Evidence Gate · 受控工具注册表", VIOLET_SOFT, VIOLET),
        ("基础设施层", "关系数据库 · 检索索引 · 原文存储 · 审计日志", AMBER_SOFT, AMBER),
    ]
    for i, (head, body, fill, accent_color) in enumerate(layers):
        y = 1.9 + i * 0.95
        add_box(slide, 0.8, y, 7.1, 0.68, fill=fill, line=accent_color)
        add_text(slide, head, 1.05, y + 0.15, 1.35, 0.25, size=12, color=accent_color, bold=True)
        add_text(slide, body, 2.55, y + 0.16, 4.85, 0.24, size=11, color=INK)
        if i < len(layers) - 1:
            add_line(slide, 4.35, y + 0.68, 4.35, y + 0.95, color=LINE, width=1.4)
    add_box(slide, 8.45, 1.9, 3.95, 3.55, fill=GREEN_DARK, line=GREEN_DARK)
    add_text(slide, "回答链路", 8.78, 2.2, 2.1, 0.3, size=16, color=RGBColor(0xB9, 0xE1, 0xCD), bold=True)
    chain = ["识别事务与必要条件", "检索适用政策证据", "检查来源 / 版本 / 时效", "生成结构化回答", "执行动作前请求确认", "无证据时保守降级"]
    for i, item in enumerate(chain):
        cy = 2.78 + i * 0.38
        add_text(slide, f"{i+1}", 8.82, cy, 0.25, 0.22, size=9, color=RGBColor(0xB9, 0xE1, 0xCD), bold=True, align=PP_ALIGN.CENTER)
        add_text(slide, item, 9.25, cy, 2.65, 0.23, size=10, color=WHITE)
    add_box(slide, 0.8, 6.0, 11.6, 0.57, fill=WHITE, line=LINE)
    add_text(slide, "关键不变量：Agent 不直接访问数据库；只有已发布且未过期的证据包才能支撑确定性回答。", 1.05, 6.18, 11.1, 0.22, size=11, color=INK, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide)

    # 7. Demo
    slide = base_slide(prs)
    add_title(slide, "06 · 作品演示", "从问题到行动：一条可解释的用户路径", "现场演示建议控制在 4 分钟，并主动说明本地原型的边界。", 7)
    add_image(slide, ROOT / "evidence" / "viewport-1440.png", 0.65, 1.85, w=7.35)
    add_image(slide, ROOT / "evidence" / "viewport-390.png", 8.55, 1.85, w=1.85)
    add_box(slide, 10.6, 1.85, 1.85, 4.35, fill=WHITE, line=LINE)
    demo_steps = [("01", "提问", "病假 5 天怎么申请"), ("02", "看证据", "来源卡片 + 风险状态"), ("03", "做准备", "生成并勾选材料清单"), ("04", "设提醒", "个人计划，不冒充官方通知")]
    for i, (num, head, body) in enumerate(demo_steps):
        yy = 2.13 + i * 0.92
        add_text(slide, num, 10.82, yy, 0.35, 0.2, size=9, color=GREEN, bold=True)
        add_text(slide, head, 11.25, yy - 0.01, 0.9, 0.22, size=11, color=INK, bold=True)
        add_text(slide, body, 10.82, yy + 0.28, 1.36, 0.34, size=8.7, color=MUTED)
    add_box(slide, 0.65, 6.25, 9.3, 0.55, fill=AMBER_SOFT, line=RGBColor(0xF1, 0xDF, 0xBF))
    add_text(slide, "演示边界：页面交互与本地状态可演示；不连接真实审批、实时政策检索、大模型或通知服务。", 0.9, 6.43, 8.8, 0.2, size=9.5, color=AMBER, bold=True)
    add_footer(slide)

    # 8. Testing
    slide = base_slide(prs)
    add_title(slide, "07 · 测试与质量", "先证明已测范围，再公开未测风险", "测试结论遵循证据：PASS 只对对应测试范围负责，不把原型证据外推为后端质量。", 8)
    add_metric(slide, 0.7, 1.95, 2.55, 1.25, "12 / 12", "离线原型交互冒烟通过", GREEN_SOFT, GREEN)
    add_metric(slide, 3.5, 1.95, 2.55, 1.25, "6", "响应式视口覆盖", BLUE_SOFT, BLUE)
    add_metric(slide, 6.3, 1.95, 2.55, 1.25, "0", "既有报告中的运行时异常", VIOLET_SOFT, VIOLET)
    add_metric(slide, 9.1, 1.95, 2.55, 1.25, "待测", "API / 权限 / 并发 / 恢复", AMBER_SOFT, AMBER)
    add_box(slide, 0.7, 3.65, 5.6, 2.25, fill=WHITE, line=LINE)
    add_text(slide, "已执行证据", 0.98, 3.95, 2.3, 0.3, size=16, color=GREEN, bold=True)
    add_bullets(slide, ["导航、筛选、收藏、问答、来源弹窗", "清单、提醒、画像和管理端状态", "空问题边界与 localStorage 刷新持久化", "320—1440px 布局与横向溢出检查"], 1.0, 4.35, 4.8, 1.25, size=11)
    add_box(slide, 6.65, 3.65, 5.6, 2.25, fill=AMBER_SOFT, line=RGBColor(0xF1, 0xDF, 0xBF))
    add_text(slide, "必须补齐的测试", 6.95, 3.95, 2.5, 0.3, size=16, color=AMBER, bold=True)
    add_bullets(slide, ["认证、权限和多用户数据隔离", "政策版本一致性、幂等、超时和重试", "模型不可用时的降级、审计和告警", "部署启动、回滚和真实通知边界"], 6.98, 4.35, 4.8, 1.25, size=11, bullet_color=AMBER)
    add_footer(slide)

    # 9. Risks
    slide = base_slide(prs)
    add_title(slide, "08 · 问题与解决", "把风险变成可跟踪的工程任务", "Alpha 不回避尚未完成的部分，而是为每个高风险项指定证据、负责人和下一步。", 9)
    data = [
        ["问题", "影响", "解决思路", "当前状态"],
        ["政策可能过期/冲突", "错误办事建议", "版本 + 核验日期 + 双人复核", "开放"],
        ["原型被误解为生产系统", "答辩/用户误导", "界面、README、PPT 明确边界", "已建立"],
        ["后端/API 尚未落地", "无法证明可部署", "先做最小垂直切片和契约测试", "开放"],
        ["协作过程证据不足", "贡献难以核验", "每日日志、Issue/PR、工时确认", "补录中"],
    ]
    add_table(slide, 5, 4, data, 0.7, 1.95, 11.9, 2.55, header_fill=GREEN, font_size=9.5)
    add_box(slide, 0.7, 4.9, 11.9, 1.0, fill=GREEN_DARK, line=GREEN_DARK)
    add_text(slide, "决策原则", 1.02, 5.17, 1.5, 0.25, size=13, color=RGBColor(0xB9, 0xE1, 0xCD), bold=True)
    add_text(slide, "宁可明确“待核验”，也不根据往年经验猜一个看似完整的答案。", 2.45, 5.12, 9.6, 0.35, size=20, color=WHITE, bold=True)
    add_footer(slide)

    # 10. Collaboration / roles
    slide = base_slide(prs)
    add_title(slide, "09 · 团队协作", "分工以证据为准，不以学号或作者名推断", "最终总结需要由每位成员确认实际工作、工时、贡献比例和过程体会。", 10)
    add_box(slide, 0.7, 1.9, 5.8, 4.1, fill=WHITE, line=LINE)
    add_text(slide, "Alpha 工作包", 1.0, 2.18, 2.2, 0.3, size=16, color=GREEN, bold=True)
    work_items = [
        ("WP-01", "仓库工程化 / 版本发布"),
        ("WP-02", "原型闭环 / 交互体验"),
        ("WP-03", "政策来源 / 证据核验"),
        ("WP-04", "架构 / API / 数据契约"),
        ("WP-05", "风险驱动测试 / 质量"),
        ("WP-06", "日志 / PPT / Vlog / 博客"),
    ]
    for i, (code, body) in enumerate(work_items):
        yy = 2.75 + i * 0.46
        add_text(slide, code, 1.02, yy, 0.72, 0.2, size=10, color=GREEN, bold=True)
        add_text(slide, body, 1.9, yy, 3.9, 0.23, size=11, color=INK)
    add_box(slide, 6.85, 1.9, 5.75, 4.1, fill=WHITE, line=LINE)
    add_text(slide, "成员贡献表（结项填写）", 7.15, 2.18, 3.2, 0.3, size=16, color=GREEN, bold=True)
    add_text(slide, "9 名成员：实际内容 / 实际工时 / 比例 / 证据 / 本人确认", 7.15, 2.65, 4.7, 0.35, size=12, color=MUTED)
    add_box(slide, 7.15, 3.35, 4.95, 1.25, fill=AMBER_SOFT, line=RGBColor(0xF1, 0xDF, 0xBF))
    add_text(slide, "当前状态：待补录", 7.42, 3.67, 2.2, 0.3, size=17, color=AMBER, bold=True)
    add_text(slide, "计划工时不能直接转成实际贡献比例。最终比例按确认工时计算，合计 100%。", 7.42, 4.08, 4.2, 0.35, size=10, color=RGBColor(0x8A, 0x7A, 0x62))
    add_text(slide, "记录入口：alpha-sprint/workload.csv · meeting-log.md · daily-logs/", 7.15, 5.05, 4.9, 0.35, size=9.5, color=GREEN)
    add_footer(slide)

    # 11. Reflection/next
    slide = base_slide(prs)
    add_title(slide, "10 · 复盘与下一步", "Alpha 的终点，是可验证的 Beta 起点", "把本次冲刺的亮点沉淀为下一阶段的实现顺序。", 11)
    add_box(slide, 0.7, 1.95, 3.75, 3.95, fill=GREEN_DARK, line=GREEN_DARK)
    add_text(slide, "我们学到的", 1.03, 2.3, 2.5, 0.3, size=17, color=RGBColor(0xB9, 0xE1, 0xCD), bold=True)
    add_bullets(slide, ["证据比口号更重要", "边界设计也是产品能力", "站会只同步阻塞，细节进入 Issue", "测试要公开未测范围"], 1.02, 2.85, 2.95, 1.7, size=12, color=WHITE, bullet_color=RGBColor(0xB9, 0xE1, 0xCD))
    add_box(slide, 4.72, 1.95, 3.75, 3.95, fill=WHITE, line=LINE)
    add_text(slide, "下一阶段 P0", 5.05, 2.3, 2.5, 0.3, size=17, color=GREEN, bold=True)
    add_bullets(slide, ["政策证据表完成双人核验", "实现一个最小后端垂直切片", "补齐认证、权限和引用审计", "开展 API/集成/恢复测试"], 5.05, 2.85, 2.95, 1.7, size=12)
    add_box(slide, 8.74, 1.95, 3.75, 3.95, fill=WHITE, line=LINE)
    add_text(slide, "提交前动作", 9.07, 2.3, 2.5, 0.3, size=17, color=GREEN, bold=True)
    add_bullets(slide, ["补齐 14 天日志和出席情况", "确认每人实际工时与体会", "完成 3—5 分钟 Vlog", "运行 --strict 并发布博客"], 9.07, 2.85, 2.95, 1.7, size=12)
    add_box(slide, 0.7, 6.25, 11.8, 0.5, fill=GREEN_SOFT, line=GREEN_SOFT)
    add_text(slide, "Alpha 不是把所有功能做完，而是把最重要的风险变得可见、可测、可继续。", 1.0, 6.4, 11.2, 0.2, size=12, color=GREEN_DARK, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide)

    # 12. Links / close
    slide = base_slide(prs, GREEN_DARK)
    add_text(slide, "奶娃工程 · Alpha 冲刺", 0.75, 0.7, 5.4, 0.35, size=13, color=RGBColor(0xB9, 0xE1, 0xCD), bold=True)
    add_text(slide, "谢谢观看", 0.72, 1.48, 5.8, 0.8, size=39, color=WHITE, bold=True)
    add_text(slide, "把校园事务，变成清晰、可信、可行动的下一步。", 0.77, 2.48, 7.5, 0.45, size=18, color=RGBColor(0xE3, 0xF3, 0xEB))
    add_box(slide, 0.75, 3.65, 7.1, 1.7, fill=RGBColor(0x0E, 0x61, 0x4B), line=RGBColor(0x3A, 0x8B, 0x6E))
    add_text(slide, "GitHub", 1.05, 3.98, 1.05, 0.25, size=11, color=RGBColor(0xB9, 0xE1, 0xCD), bold=True)
    add_rich_text(slide, [{"text": "trony33/fuxiaotong-campus-affairs", "color": WHITE, "size": 14, "hyperlink": "https://github.com/trony33/fuxiaotong-campus-affairs"}], 2.0, 3.91, 5.35, 0.35, size=14)
    add_text(slide, "Alpha 材料：alpha-sprint/ · 版本：0.1.0-alpha.1", 1.05, 4.55, 5.95, 0.25, size=10, color=RGBColor(0xD6, 0xEA, 0xE0))
    add_text(slide, "最终博客、Vlog 和实际成员贡献数据将在冲刺结束前补入。", 0.78, 6.55, 7.1, 0.25, size=9.5, color=RGBColor(0xB9, 0xD6, 0xC8))
    add_text(slide, "12", 12.25, 0.37, 0.5, 0.25, size=9, color=RGBColor(0xB9, 0xD6, 0xC8), align=PP_ALIGN.RIGHT)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT)
    print(f"wrote {OUT} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    build_deck()
