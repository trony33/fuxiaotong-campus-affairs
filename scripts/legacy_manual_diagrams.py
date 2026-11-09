"""Legacy hand-authored SVG layouts retained for reference.

The active generator is ``make-diagrams.py``. It renders the Mermaid source
blocks directly so the published SVGs cannot drift from the design documents.
"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "diagrams"
OUT.mkdir(exist_ok=True)

COLORS = {
    "ink": "#18352c",
    "muted": "#61736a",
    "line": "#b8c9bf",
    "green": "#dff1e8",
    "green_stroke": "#2b8061",
    "blue": "#e5f0f7",
    "blue_stroke": "#4f84a5",
    "amber": "#fff0d7",
    "amber_stroke": "#b87820",
    "violet": "#eee9f7",
    "violet_stroke": "#7963a8",
    "paper": "#ffffff",
    "canvas": "#f8faf8",
}


def color(value: str) -> str:
    """Resolve a palette name while allowing callers to pass a raw CSS color."""
    return COLORS.get(value, value)


def text(x: float, y: float, value: str, size=14, weight=400, fill=None, anchor="middle") -> str:
    fill = color(fill or "ink")
    lines = str(value).split("\n")
    return "".join(
        f'<text x="{x}" y="{y + i * (size + 4)}" font-family="Microsoft YaHei, Noto Sans SC, Arial, sans-serif" font-size="{size}px" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(line)}</text>'
        for i, line in enumerate(lines)
    )


def circle(cx, cy, radius, label, fill="green", stroke="green_stroke", size=12):
    return f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{color(fill)}" stroke="{color(stroke)}" stroke-width="1.5"/>' + text(cx, cy + 4, label, size, 700, color(stroke))


def ellipse(cx, cy, rx, ry, label, fill="paper", stroke="green_stroke", size=11):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{color(fill)}" stroke="{color(stroke)}" stroke-width="1.5"/>' + text(cx, cy + 4, label, size, 600, color(stroke))


def diamond(cx, cy, w, h, label, fill="amber", stroke="amber_stroke", size=11):
    points = f"{cx},{cy - h / 2} {cx + w / 2},{cy} {cx},{cy + h / 2} {cx - w / 2},{cy}"
    return f'<polygon points="{points}" fill="{color(fill)}" stroke="{color(stroke)}" stroke-width="1.5"/>' + text(cx, cy + 4, label, size, 600, color(stroke))


def rect(x, y, w, h, label, fill="paper", stroke="line", radius=10, size=13, weight=600, subtitle=None):
    content = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{color(fill)}" stroke="{color(stroke)}" stroke-width="1.5"/>'
    if subtitle:
        content += text(x + w / 2, y + h / 2 - 7, label, size, weight)
        content += text(x + w / 2, y + h / 2 + 16, subtitle, 10, 400, COLORS["muted"])
    else:
        lines = label.split("\n")
        base = y + h / 2 - (len(lines) - 1) * 8
        content += text(x + w / 2, base, label, size, weight)
    return content


def group(x, y, w, h, label, fill="paper", stroke="line"):
    fill_color = color(fill)
    stroke_color = color(stroke)
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill_color}" stroke="{stroke_color}" stroke-width="1.2" stroke-dasharray="6 5"/><text x="{x + 15}" y="{y + 23}" font-family="Microsoft YaHei, Noto Sans SC, Arial, sans-serif" font-size="12px" font-weight="700" fill="{stroke_color}" text-anchor="start">{escape(label)}</text>'


def arrow(x1, y1, x2, y2, label=None, color=None, dashed=False):
    color = color or COLORS["green_stroke"]
    marker = "arrow-blue" if color == COLORS["blue_stroke"] else "arrow-amber" if color == COLORS["amber_stroke"] else "arrow"
    dash = ' stroke-dasharray="6 5"' if dashed else ""
    result = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.8" marker-end="url(#{marker})"{dash}/>'
    if label:
        result += text((x1 + x2) / 2, (y1 + y2) / 2 - 5, label, 10, 500, COLORS["muted"])
    return result


def svg(title, width, height, body):
    defs = f'''<defs>
      <marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="{COLORS['green_stroke']}"/></marker>
      <marker id="arrow-blue" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="{COLORS['blue_stroke']}"/></marker>
      <marker id="arrow-amber" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="{COLORS['amber_stroke']}"/></marker>
      <filter id="shadow" x="-10%" y="-10%" width="120%" height="130%"><feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#18352c" flood-opacity=".09"/></filter>
    </defs>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
      {defs}<rect width="100%" height="100%" fill="{COLORS['canvas']}"/>
      {text(28, 32, title, 19, 700, COLORS['ink'], "start")}
      {text(28, 55, "校园事务智能办事助手 · 概要设计图", 10, 400, COLORS['muted'], "start")}
      {body}
    </svg>'''


def architecture():
    body = ""
    body += group(28, 80, 864, 104, "表示层", "paper", "#9eb5a7")
    body += rect(55, 112, 238, 47, "学生端 Web/H5", "green", "green_stroke", subtitle="问答 · 详情 · 清单 · 提醒")
    body += rect(341, 112, 238, 47, "知识管理端", "green", "green_stroke", subtitle="录入 · 核验 · 发布 · 反馈")
    body += rect(627, 112, 238, 47, "官方/人工渠道", "amber", "amber_stroke", subtitle="来源查询 · 转人工")
    body += group(28, 212, 864, 142, "应用层 + 领域层", "paper", "#9eb5a7")
    body += rect(52, 248, 170, 58, "API 与鉴权", "blue", "blue_stroke", subtitle="RBAC · 限流 · 错误")
    body += rect(251, 248, 170, 58, "会话服务", "green", "green_stroke", subtitle="消息 · 历史 · 引用")
    body += rect(450, 248, 170, 58, "事务 Agent", "green", "green_stroke", subtitle="意图 · 规划 · 组织")
    body += rect(649, 248, 170, 58, "证据门禁", "amber", "amber_stroke", subtitle="来源 · 时效 · 风险")
    body += arrow(174, 159, 137, 248)
    body += arrow(460, 159, 336, 248)
    body += arrow(746, 159, 734, 248, color=COLORS["amber_stroke"])
    body += arrow(222, 277, 251, 277)
    body += arrow(421, 277, 450, 277)
    body += arrow(620, 277, 649, 277)
    body += group(28, 382, 864, 111, "基础设施层", "paper", "#9eb5a7")
    body += rect(53, 418, 180, 45, "政策检索工具", "blue", "blue_stroke", subtitle="结构化 + 全文")
    body += rect(267, 418, 180, 45, "清单/提醒工具", "green", "green_stroke", subtitle="用户确认后执行")
    body += rect(481, 418, 180, 45, "模型适配层", "violet", "violet_stroke", subtitle="供应商可替换")
    body += rect(695, 418, 170, 45, "审计与指标", "amber", "amber_stroke", subtitle="可追溯")
    body += arrow(535, 306, 143, 418)
    body += arrow(535, 306, 357, 418)
    body += arrow(535, 306, 571, 418)
    body += arrow(734, 306, 780, 418, color=COLORS["amber_stroke"])
    body += group(28, 522, 864, 78, "数据与外部服务", "paper", "#9eb5a7")
    body += rect(80, 548, 205, 34, "关系数据库", "blue", "blue_stroke", radius=8, size=11)
    body += rect(345, 548, 205, 34, "政策原文/附件", "blue", "blue_stroke", radius=8, size=11)
    body += rect(610, 548, 205, 34, "大模型 API（可选）", "violet", "violet_stroke", radius=8, size=11)
    body += arrow(143, 463, 182, 548, color=COLORS["blue_stroke"])
    body += arrow(357, 463, 447, 548, color=COLORS["green_stroke"])
    body += arrow(571, 463, 712, 548, color=COLORS["violet_stroke"])
    return svg("系统逻辑架构", 920, 630, body)


def context():
    body = ""
    body += rect(45, 118, 175, 52, "在校学生", "green", "green_stroke", subtitle="提出咨询与办事准备需求")
    body += rect(45, 248, 175, 52, "知识管理员/核验人", "green", "green_stroke", subtitle="维护政策与来源")
    body += group(285, 75, 365, 300, "校园事务智能办事助手", "paper", "#2b8061")
    body += rect(320, 120, 295, 48, "Web/H5 用户端", "green", "green_stroke", subtitle="问答 · 指南 · 清单 · 提醒")
    body += rect(320, 210, 295, 48, "管理端", "blue", "blue_stroke", subtitle="录入 · 核验 · 发布 · 反馈")
    body += rect(320, 300, 295, 48, "Agent + 证据门禁 + 受控工具", "amber", "amber_stroke", subtitle="只基于已核验证据回答")
    body += arrow(220, 144, 320, 144)
    body += arrow(220, 274, 320, 234)
    body += arrow(468, 168, 468, 210)
    body += arrow(468, 258, 468, 300)
    body += rect(725, 82, 160, 48, "学校官方网页/文件", "blue", "blue_stroke", subtitle="政策事实来源")
    body += rect(725, 166, 160, 48, "大模型服务", "violet", "violet_stroke", subtitle="候选文本生成")
    body += rect(725, 250, 160, 48, "可选通知渠道", "amber", "amber_stroke", subtitle="站内/消息提醒")
    body += rect(725, 334, 160, 48, "负责部门/人工", "amber", "amber_stroke", subtitle="不确定时转人工")
    body += arrow(650, 324, 725, 106, color=COLORS["blue_stroke"])
    body += arrow(650, 324, 725, 190, color=COLORS["violet_stroke"])
    body += arrow(650, 324, 725, 274, color=COLORS["amber_stroke"])
    body += arrow(650, 324, 725, 358, color=COLORS["amber_stroke"])
    return svg("系统上下文与边界", 920, 440, body)


def agent_flow():
    body = ""
    nodes = [(55, 91, 150, 42, "用户提问", "green"), (270, 91, 180, 42, "安全/范围检查", "blue"), (515, 91, 170, 42, "意图与条件识别", "green"), (745, 91, 125, 42, "需追问？", "amber")]
    for x, y, w, h, label, fill in nodes: body += rect(x, y, w, h, label, fill, f"{fill}_stroke", radius=9, size=12)
    body += arrow(205, 112, 270, 112); body += arrow(450, 112, 515, 112); body += arrow(685, 112, 745, 112)
    body += rect(747, 181, 123, 42, "追问一项", "amber", "amber_stroke", radius=9, size=12)
    body += arrow(807, 133, 807, 181, "是", COLORS["amber_stroke"])
    body += arrow(747, 202, 130, 202, "补充后继续", COLORS["amber_stroke"], True)
    body += rect(55, 270, 175, 48, "PolicySearchTool", "blue", "blue_stroke", subtitle="画像 + 事项 + 关键词")
    body += rect(295, 270, 175, 48, "可信证据包", "green", "green_stroke", subtitle="政策版本 + 原文 + 来源")
    body += rect(535, 270, 175, 48, "证据检查", "amber", "amber_stroke", subtitle="适用 · 时效 · 冲突")
    body += rect(765, 270, 105, 48, "可回答？", "amber", "amber_stroke", subtitle="门禁")
    body += arrow(807, 223, 143, 270, "否", COLORS["green_stroke"])
    body += arrow(230, 294, 295, 294); body += arrow(470, 294, 535, 294); body += arrow(710, 294, 765, 294)
    body += rect(55, 395, 175, 48, "结构化回答", "green", "green_stroke", subtitle="结论 · 步骤 · 材料")
    body += rect(295, 395, 175, 48, "用户确认动作", "green", "green_stroke", subtitle="清单 · 提醒 · 收藏")
    body += rect(535, 395, 175, 48, "统一来源卡", "blue", "blue_stroke", subtitle="链接 · 核验时间")
    body += rect(765, 395, 105, 48, "保守降级", "amber", "amber_stroke", subtitle="不确定/人工")
    body += arrow(817, 318, 143, 395, "通过")
    body += arrow(817, 318, 817, 395, "不足", COLORS["amber_stroke"])
    body += arrow(230, 419, 295, 419); body += arrow(470, 419, 535, 419)
    body += rect(300, 505, 320, 39, "保存会话、引用、风险等级与反馈入口", "paper", "green_stroke", radius=9, size=12)
    body += arrow(382, 443, 425, 505); body += arrow(817, 443, 575, 505, color=COLORS["amber_stroke"])
    return svg("Agent 主流程与风险降级", 920, 585, body)


def use_case():
    body = ""
    body += group(225, 75, 620, 455, "校园事务智能办事助手", "paper", "#2b8061")
    body += ellipse(385, 130, 112, 25, "咨询校园政策", "green", "green_stroke")
    body += ellipse(675, 130, 125, 25, "筛选适用政策", "green", "green_stroke")
    body += ellipse(385, 220, 125, 25, "查看流程/材料/来源", "blue", "blue_stroke")
    body += ellipse(675, 220, 112, 25, "保存清单/收藏", "green", "green_stroke")
    body += ellipse(385, 310, 112, 25, "创建/取消提醒", "green", "green_stroke")
    body += ellipse(675, 310, 125, 25, "反馈问题/转人工", "amber", "amber_stroke")
    body += ellipse(530, 405, 125, 25, "检索可信证据", "blue", "blue_stroke")
    body += ellipse(530, 475, 125, 25, "证据与风险检查", "amber", "amber_stroke")
    body += rect(45, 125, 125, 45, "学生", "green", "green_stroke", radius=22, size=12)
    body += rect(45, 235, 125, 45, "政策录入员", "green", "green_stroke", radius=22, size=12)
    body += rect(45, 345, 125, 45, "政策核验人", "green", "green_stroke", radius=22, size=12)
    body += rect(45, 455, 125, 45, "人工渠道", "amber", "amber_stroke", radius=22, size=12)
    body += rect(850, 125, 55, 45, "模型", "violet", "violet_stroke", radius=22, size=11)
    body += arrow(170, 147, 273, 130)
    body += arrow(170, 147, 550, 130)
    body += arrow(170, 147, 273, 220)
    body += arrow(170, 147, 563, 220)
    body += arrow(170, 147, 273, 310)
    body += arrow(170, 147, 613, 310)
    body += arrow(170, 367, 323, 130, dashed=True)
    body += arrow(170, 367, 613, 310, dashed=True)
    body += arrow(170, 257, 323, 130, dashed=True)
    body += arrow(170, 477, 613, 310, dashed=True)
    body += arrow(850, 147, 800, 405, color=COLORS["violet_stroke"], dashed=True)
    body += arrow(510, 155, 530, 380, "include", COLORS["blue_stroke"], True)
    body += arrow(592, 430, 592, 450, "include", COLORS["amber_stroke"], True)
    return svg("主要用例图", 920, 580, body)


def activity():
    body = ""
    body += circle(460, 86, 12, "", "green", "green_stroke", 1)
    body += rect(390, 110, 140, 40, "接收用户问题", "green", "green_stroke", radius=9, size=12)
    body += arrow(460, 98, 460, 110)
    body += diamond(460, 195, 190, 62, "安全/范围\n有效？")
    body += arrow(460, 150, 460, 164)
    body += rect(120, 175, 190, 42, "说明能力边界并引导重述", "amber", "amber_stroke", radius=9, size=11)
    body += arrow(365, 195, 310, 195, "否", COLORS["amber_stroke"])
    body += rect(390, 245, 140, 40, "识别意图与条件", "green", "green_stroke", radius=9, size=12)
    body += arrow(460, 226, 460, 245, "是")
    body += diamond(460, 330, 190, 62, "关键条件\n足够？")
    body += arrow(460, 285, 460, 299)
    body += rect(120, 310, 190, 42, "只追问一个关键条件", "amber", "amber_stroke", radius=9, size=11)
    body += arrow(365, 330, 310, 330, "否", COLORS["amber_stroke"])
    body += rect(390, 380, 140, 40, "检索政策证据", "blue", "blue_stroke", radius=9, size=12)
    body += arrow(460, 361, 460, 380, "是")
    body += diamond(460, 465, 190, 62, "证据充分且\n版本有效？")
    body += arrow(460, 420, 460, 434)
    body += rect(660, 445, 190, 42, "保守降级 + 官方渠道/人工", "amber", "amber_stroke", radius=9, size=11)
    body += arrow(555, 465, 660, 465, "否", COLORS["amber_stroke"])
    body += rect(390, 515, 140, 40, "组织结构化回答", "green", "green_stroke", radius=9, size=12)
    body += arrow(460, 496, 460, 515, "是")
    body += rect(390, 590, 140, 40, "保存引用与风险", "blue", "blue_stroke", radius=9, size=12)
    body += arrow(460, 555, 460, 590)
    body += circle(460, 675, 12, "", "green", "green_stroke", 1)
    body += arrow(460, 630, 460, 663)
    body += arrow(755, 487, 530, 610, color=COLORS["amber_stroke"])
    body += text(28, 735, "活动图强调：无证据、冲突或动态日期缺失时，不进入肯定性回答路径。", 11, 500, COLORS["muted"], "start")
    return svg("Agent 业务活动图", 920, 760, body)


def class_model():
    body = ""
    classes = [
        (35, 90, 205, 112, "User", ["id: Long", "account: String", "role: UserRole"]),
        (270, 90, 205, 112, "UserProfile", ["educationLevel", "grade", "major", "campus"]),
        (505, 90, 205, 112, "Policy", ["id: Long", "matter", "status", "officialUrl"]),
        (740, 90, 145, 112, "PolicyVersion", ["versionNo", "expiryStatus", "verifiedAt"]),
        (35, 290, 205, 112, "Conversation", ["id", "userId", "status"]),
        (270, 290, 205, 112, "Message", ["role", "content", "intent", "riskLevel"]),
        (505, 290, 205, 112, "Citation", ["messageId", "versionId", "excerpt"]),
        (740, 290, 145, 112, "Department", ["name", "phone", "officialUrl"]),
        (35, 490, 205, 112, "Checklist", ["userId", "policyId", "status"]),
        (270, 490, 205, 112, "ChecklistItem", ["content", "completed"]),
        (505, 490, 205, 112, "Reminder", ["remindAt", "channel", "status"]),
        (740, 490, 145, 112, "Feedback", ["reason", "status"]),
    ]
    for x, y, w, h, name, fields in classes:
        body += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{COLORS["paper"]}" stroke="{COLORS["green_stroke"]}" stroke-width="1.4" filter="url(#shadow)"/>'
        body += text(x + 10, y + 21, name, 13, 700, COLORS["green_stroke"], "start")
        body += f'<line x1="{x}" y1="{y+31}" x2="{x+w}" y2="{y+31}" stroke="{COLORS["line"]}"/>'
        for i, field in enumerate(fields): body += text(x + 10, y + 51 + i * 16, field, 10, 400, COLORS["muted"], "start")
    body += arrow(240, 146, 270, 146, "1:1")
    body += arrow(475, 146, 505, 146, "1:N")
    body += arrow(710, 146, 740, 146, "1:N")
    body += arrow(137, 202, 137, 290, "1:N")
    body += arrow(240, 346, 270, 346, "1:N")
    body += arrow(475, 346, 505, 346, "1:N")
    body += arrow(710, 346, 740, 346, "N:1")
    body += arrow(137, 402, 137, 490, "1:N")
    body += arrow(240, 546, 270, 546, "1:N")
    body += arrow(475, 546, 505, 546, "1:N")
    body += arrow(710, 546, 740, 546, "1:N")
    return svg("核心领域类模型", 920, 650, body)


def sequence():
    body = ""
    actors = [(70, "学生"), (215, "用户端"), (360, "API"), (505, "Agent"), (650, "检索工具"), (795, "证据门禁")]
    for x, label in actors:
        body += rect(x - 48, 83, 96, 35, label, "green" if label in ("学生", "用户端") else "blue", "green_stroke" if label in ("学生", "用户端") else "blue_stroke", radius=8, size=11)
        body += f'<line x1="{x}" y1="{118}" x2="{x}" y2="548" stroke="{COLORS["line"]}" stroke-dasharray="4 5"/>'
    messages = [(160, 215, "输入问题"), (215, 360, "POST /agent/messages"), (360, 505, "handleMessage + 画像"), (505, 650, "search(事项,条件)"), (650, 505, "可信证据包"), (505, 795, "候选回答 + 引用"), (795, 505, "通过/降级"), (505, 360, "answer + risk + citations"), (360, 215, "JSON/SSE"), (215, 70, "展示结果")]
    y = 154
    for x1, x2, label in messages:
        color = COLORS["amber_stroke"] if "降级" in label else COLORS["green_stroke"]
        body += arrow(x1, y, x2, y, label, color)
        y += 34
    body += rect(285, 510, 275, 38, "每个引用必须可回溯到 policy_version", "amber", "amber_stroke", radius=8, size=11)
    return svg("有证据回答的关键时序", 920, 590, body)


def fallback_sequence():
    body = ""
    actors = [(75, "学生"), (220, "用户端"), (365, "Agent"), (510, "检索服务"), (655, "证据门禁"), (800, "联系方式工具")]
    for x, label in actors:
        body += rect(x - 48, 83, 96, 35, label, "green" if label in ("学生", "用户端") else "amber" if label == "证据门禁" else "blue", "green_stroke" if label in ("学生", "用户端") else "amber_stroke" if label == "证据门禁" else "blue_stroke", radius=8, size=11)
        body += f'<line x1="{x}" y1="118" x2="{x}" y2="510" stroke="{COLORS["line"]}" stroke-dasharray="4 5"/>'
    messages = [
        (123, 220, "询问今年截止日期"),
        (220, 365, "问题 + 画像"),
        (365, 510, "检索当前年度通知"),
        (510, 365, "无日期/版本冲突"),
        (365, 655, "请求风险判定"),
        (655, 365, "HIGH / UNKNOWN"),
        (365, 800, "查询已核验部门"),
        (800, 365, "官网 + 联系方式"),
        (365, 220, "不确定 + 转人工"),
        (220, 75, "展示风险与来源入口"),
    ]
    y = 154
    for x1, x2, label in messages:
        body += arrow(x1, y, x2, y, label, COLORS["amber_stroke"] if "不确定" in label or "HIGH" in label else COLORS["green_stroke"])
        y += 31
    body += rect(280, 505, 360, 40, "禁止把历史日期或模型猜测展示为确定截止日", "amber", "amber_stroke", radius=8, size=11)
    return svg("无证据/冲突时的降级时序", 920, 575, body)


def collaboration():
    body = ""
    objects = [
        (45, 115, 150, 55, "用户端", "green", "输入与展示"),
        (280, 75, 165, 55, "API 门面", "blue", "鉴权/限流"),
        (520, 75, 165, 55, "会话服务", "green", "保存消息"),
        (520, 220, 165, 55, "事务 Agent", "green", "规划与组织"),
        (280, 365, 165, 55, "检索工具", "blue", "返回证据包"),
        (45, 365, 150, 55, "关系数据库", "blue", "政策/会话"),
        (760, 220, 120, 55, "证据门禁", "amber", "校验/降级"),
        (760, 365, 120, 55, "审计日志", "amber", "追溯"),
    ]
    for x, y, w, h, name, fill, subtitle in objects:
        body += rect(x, y, w, h, name, fill, f"{fill}_stroke", radius=10, size=12, subtitle=subtitle)
    body += arrow(195, 142, 280, 110, "1 sendMessage")
    body += arrow(445, 110, 520, 110, "2 appendUserMessage")
    body += arrow(602, 130, 602, 220, "3 handleMessage")
    body += arrow(520, 247, 445, 390, "4 search(criteria)")
    body += arrow(280, 390, 195, 390, "5 findPublishedEvidence")
    body += arrow(445, 390, 520, 247, "6 evidencePack")
    body += arrow(685, 247, 760, 247, "7 validate")
    body += arrow(760, 275, 685, 110, "8 persistAnswer")
    body += arrow(685, 110, 195, 142, "9 answer + citations")
    body += arrow(820, 275, 820, 365, "audit", COLORS["amber_stroke"])
    return svg("对象协作与通信消息", 920, 490, body)


def er_model():
    body = ""
    entities = [
        (45, 95, 170, 52, "USER", "green"), (275, 95, 190, 52, "USER_PROFILE", "green"), (545, 95, 180, 52, "POLICY", "green"), (785, 95, 105, 52, "DEPARTMENT", "blue"),
        (45, 235, 170, 52, "CONVERSATION", "blue"), (275, 235, 190, 52, "MESSAGE", "blue"), (545, 235, 180, 52, "CITATION", "amber"), (785, 235, 105, 52, "ANSWER", "amber"),
        (45, 375, 170, 52, "POLICY_VERSION", "green"), (275, 375, 190, 52, "SOURCE_DOCUMENT", "blue"), (545, 375, 180, 52, "CHECKLIST", "green"), (785, 375, 105, 52, "REMINDER", "green"),
        (45, 515, 170, 52, "POLICY_AUDIENCE", "green"), (275, 515, 190, 52, "FEEDBACK", "amber"), (545, 515, 180, 52, "TOOL_CALL_LOG", "blue"), (785, 515, 105, 52, "AUDIT_LOG", "blue"),
    ]
    for x, y, w, h, label, fill in entities: body += rect(x, y, w, h, label, fill, f"{fill}_stroke", radius=9, size=11)
    links = [(215, 121, 275, 121, "1:1"), (465, 121, 545, 121, "1:N"), (725, 121, 785, 121, "N:1"), (130, 147, 130, 235, "1:N"), (215, 261, 275, 261, "1:N"), (465, 261, 545, 261, "1:N"), (725, 261, 785, 261, "1:1"), (130, 287, 130, 375, "1:N"), (215, 401, 275, 401, "N:M"), (465, 401, 545, 401, "1:N"), (725, 401, 785, 401, "1:N"), (130, 427, 130, 515, "1:N"), (215, 541, 275, 541, "1:N"), (465, 541, 545, 541, "1:N"), (725, 541, 785, 541, "1:N")]
    for x1, y1, x2, y2, label in links: body += arrow(x1, y1, x2, y2, label, COLORS["line"])
    return svg("数据库核心 ER 模型", 920, 620, body)


def lifecycle():
    body = ""
    body += rect(45, 105, 150, 48, "官方制度/通知", "blue", "blue_stroke", subtitle="原始来源")
    body += rect(245, 105, 150, 48, "人工采集检查", "green", "green_stroke", subtitle="链接/字段/片段")
    body += rect(445, 105, 150, 48, "政策草稿", "green", "green_stroke", subtitle="policy + version")
    body += diamond(700, 129, 150, 62, "双人核验\n通过？")
    body += rect(795, 230, 100, 48, "退回修改", "amber", "amber_stroke", size=11)
    body += rect(445, 285, 150, 48, "发布有效版本", "green", "green_stroke", subtitle="PUBLISHED")
    body += rect(230, 405, 150, 48, "全文/关键词索引", "blue", "blue_stroke", subtitle="可检索")
    body += rect(465, 405, 150, 48, "Agent 证据包", "green", "green_stroke", subtitle="只读引用")
    body += rect(700, 405, 150, 48, "历史/下线版本", "amber", "amber_stroke", subtitle="可追溯")
    body += arrow(195, 129, 245, 129)
    body += arrow(395, 129, 445, 129)
    body += arrow(595, 129, 625, 129)
    body += arrow(775, 155, 820, 230, "否", COLORS["amber_stroke"])
    body += arrow(700, 160, 595, 285, "是")
    body += arrow(795, 254, 520, 153, "补齐后再核验", COLORS["amber_stroke"], True)
    body += arrow(520, 333, 305, 405)
    body += arrow(520, 333, 540, 405)
    body += arrow(595, 309, 775, 405, "更新/过期", COLORS["amber_stroke"])
    body += text(28, 510, "只有已发布且未过期的 policy_version 才能进入确定性回答证据包。", 11, 500, COLORS["muted"], "start")
    return svg("政策知识生命周期", 920, 535, body)


def agent_boundary():
    body = ""
    actors = [(95, "Agent 编排器"), (280, "PolicySearchTool"), (465, "关系数据库"), (650, "检索索引"), (835, "证据门禁")]
    for x, label in actors:
        body += rect(x - 63, 83, 126, 35, label, "green" if "Agent" in label else "blue" if "Tool" in label or "数据库" in label or "索引" in label else "amber", "green_stroke" if "Agent" in label else "blue_stroke" if "Tool" in label or "数据库" in label or "索引" in label else "amber_stroke", radius=8, size=10)
        body += f'<line x1="{x}" y1="118" x2="{x}" y2="510" stroke="{COLORS["line"]}" stroke-dasharray="4 5"/>'
    messages = [(158, 280, "查询条件"), (280, 465, "发布状态/版本/画像"), (280, 650, "关键词召回"), (650, 280, "候选 version_id"), (465, 280, "完整字段+来源"), (280, 95, "只读证据包"), (95, 835, "候选答案+证据"), (835, 95, "通过/降级")]
    y = 154
    for x1, x2, label in messages:
        body += arrow(x1, y, x2, y, label, COLORS["amber_stroke"] if "降级" in label else COLORS["green_stroke"])
        y += 38
    body += rect(245, 515, 430, 40, "Agent 不直接连接数据库；工具层负责权限、投影、脱敏与审计", "amber", "amber_stroke", radius=8, size=11)
    return svg("Agent 与数据边界", 920, 585, body)


def deployment():
    body = ""
    body += rect(55, 120, 180, 55, "浏览器 / 手机", "green", "green_stroke", subtitle="HTTPS")
    body += rect(300, 120, 180, 55, "Nginx / 网关", "blue", "blue_stroke", subtitle="静态资源 + 反向代理")
    body += rect(545, 120, 180, 55, "模块化单体后端", "green", "green_stroke", subtitle="API + Agent + 工具")
    body += rect(770, 120, 105, 55, "大模型 API", "violet", "violet_stroke", subtitle="可替换")
    body += arrow(235, 147, 300, 147); body += arrow(480, 147, 545, 147); body += arrow(725, 147, 770, 147, color=COLORS["violet_stroke"])
    body += rect(105, 310, 190, 55, "前端静态资源", "blue", "blue_stroke", subtitle="Web/H5")
    body += rect(365, 310, 190, 55, "关系数据库", "blue", "blue_stroke", subtitle="用户/政策/会话")
    body += rect(625, 310, 190, 55, "政策原文与索引", "blue", "blue_stroke", subtitle="对象存储 + 全文")
    body += arrow(390, 175, 200, 310); body += arrow(635, 175, 460, 310); body += arrow(635, 175, 720, 310)
    body += rect(245, 470, 190, 50, "备份与审计", "amber", "amber_stroke", subtitle="每日备份 · 追溯")
    body += rect(500, 470, 190, 50, "监控指标", "amber", "amber_stroke", subtitle="延迟 · 命中 · 风险")
    body += arrow(460, 365, 340, 470, color=COLORS["amber_stroke"]); body += arrow(720, 365, 595, 470, color=COLORS["amber_stroke"])
    return svg("最小部署拓扑", 920, 565, body)


GENERATORS = {
    "context.svg": context,
    "architecture.svg": architecture,
    "agent-flow.svg": agent_flow,
    "use-case.svg": use_case,
    "class-model.svg": class_model,
    "activity.svg": activity,
    "sequence.svg": sequence,
    "fallback-sequence.svg": fallback_sequence,
    "collaboration.svg": collaboration,
    "lifecycle.svg": lifecycle,
    "er-model.svg": er_model,
    "agent-boundary.svg": agent_boundary,
    "deployment.svg": deployment,
}

for filename, generator in GENERATORS.items():
    (OUT / filename).write_text(generator(), encoding="utf-8")
    print(f"wrote {filename}")
