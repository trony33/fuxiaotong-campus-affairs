# 奶娃工程｜Alpha 冲刺材料

> 本目录对应“2026 秋软工实践团队作业-第三次（Alpha 冲刺）”。文档以仓库中能够复核的证据为准；带有“待确认/待补录”标记的内容，必须由队长和对应成员在最终提交前核实后再发布。

## 冲刺信息

| 项目 | 内容 |
|---|---|
| 团队 | 奶娃工程 |
| 项目 | 福晓通——校园事务智能办事助手 |
| 课程 | [202601 软件工程（福州大学）](https://edu.cnblogs.com/campus/fzu/202601SofwareEngineering) |
| 作业入口 | [2026 秋软工实践团队作业-第三次（Alpha 冲刺）](https://edu.cnblogs.com/campus/fzu/202601SofwareEngineering/homework/) |
| 计划冲刺区间 | 2026-11-08—2026-11-21（含首尾 14 个自然日；如团队实际启动日不同，请统一调整） |
| 博客截止时间 | 2026-11-21 23:59 |
| GitHub | <https://github.com/trony33/fuxiaotong-campus-affairs> |
| 当前材料状态 | 计划与交付骨架已建立；成员分工、每日会议、实际工时和 Vlog 成片待团队补录 |

## 材料导航

### 博客稿

- [冲刺计划](sprint-plan.md)
- [冲刺总结（提交前需核实）](sprint-summary.md)
- [事实登记表](FACT-REGISTER.md)

### 过程证据

- [站立会议记录](meeting-log.md)
- [每日日志目录与模板](daily-logs/README.md)
- [工作量登记表](workload.csv)
- [燃尽图数据](burndown.csv)
- [风险与问题清单](risks-and-issues.md)

### 测试与答辩

- [Alpha 测试计划与当前测试报告](test-plan.md)
- [Vlog 分镜与剪辑脚本](vlog-script.md)
- [答辩 PPT 说明](ppt-outline.md)
- [答辩 PPT 文件](../docs/alpha-sprint-defense.pptx)

## 当前可核验基线

以下内容来自仓库已有提交和 `evidence/` 文件，不代表后端或正式生产系统已经完成：

- 已有可交互离线原型，覆盖智能问答、办事指南、材料清单、提醒、历史收藏、办事画像和管理端示例入口。
- `evidence/prototype-smoke-report.json` 记录 12 项交互冒烟测试，12 项均为 `PASS`。
- `evidence/viewport-report.json` 覆盖 320、390、760、768、1024、1440px 六个视口，横向溢出检查通过。
- 仓库已有系统设计书、数据库设计书、16 张 UML/数据库图示以及墨刀只读预览链接。
- 当前仓库仍是原型与设计交付包，尚未提供可运行的后端、真实政策实时检索、学校审批接口或真实通知服务；这些限制在博客和答辩中必须主动说明。

## 提交前最小动作

1. 队长确认 9 名成员的实际角色、实际工时、工作量比例和过程体会。
2. 将每日站会的时间、参会情况、会议照片/截图和 GitHub 证据补入 `meeting-log.md` 与 `daily-logs/`。
3. 用实际剩余工作量更新 `burndown.csv`，再重新生成 PPT 中的进度图。
4. 完成 3—5 分钟 Vlog，按 [vlog-script.md](vlog-script.md) 替换视频链接或文件路径。
5. 把博客园正式链接填回 `sprint-summary.md`，并由队长按题目要求提交标题为 **奶娃工程-冲刺总结** 的博客。
6. 运行 `python scripts/validate-alpha-sprint.py --strict`；严格模式通过后再提交最终版本。

## 事实边界

不要把计划表中的“拟议负责人”复制成实际分工，也不要把原型冒烟测试结果表述为后端接口测试结果。所有百分比必须由实际工时计算：

```text
成员工作量比例 = 该成员确认的实际工时 / 全体成员确认的实际工时 × 100%
```
