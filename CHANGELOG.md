# Changelog

本项目遵循 [Semantic Versioning 2.0.0](https://semver.org/lang/zh-CN/)。在 `0.x` 阶段，次版本号用于标识可复核的阶段性产品/交付包，预发布标识用于说明尚未达到生产稳定性。

## [0.1.0-alpha.1] - 2026-11-12

### Added

- Alpha 冲刺计划、总结草稿、事实登记表和 14 天日志结构。
- 工作量登记、燃尽图、风险清单、政策证据表和 API 契约草案。
- 风险驱动测试计划、Vlog 分镜和答辩 PPT 初稿。
- `scripts/validate-alpha-sprint.py` 及 GitHub Actions 结构验证流程。
- Alpha 版本文件和本发布说明。

### Verified baseline

- 离线原型既有 12 项交互冒烟测试记录为 12/12 PASS。
- 六个视口的既有响应式检查记录通过。
- 本版本仍是原型/设计交付包，不包含可宣称为生产可用的后端、真实审批接口、实时政策服务或真实通知服务。

### Known limitations

- 14 天实际会议、成员角色、工时、贡献比例、过程体会和 Vlog 成片需要在冲刺结束前由团队补录确认。
- `alpha-sprint/burndown.csv` 当前只包含计划曲线；实际曲线必须依据每日记录补齐。
- 最终作业博客链接需要由队长发布后写回 `alpha-sprint/sprint-summary.md`。
