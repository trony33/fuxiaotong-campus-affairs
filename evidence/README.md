# 本地验证证据

本目录保存离线补充原型与正式 PDF 的本地可复核证据。原型验证于 2026-11-03 完成，使用合成浏览器数据；测试结束后恢复了测试前的 `localStorage`，不会把测试记录留在用户浏览器中。两份 8 页正式 PDF 于 2026-11-09 完成最终文本与视觉复核。

## 文件

- `prototype-smoke-report.json`：11 项交互冒烟结果；全部 `PASS`，控制台事件、运行时异常和错误日志均为空。
- `viewport-report.json`：`320、390、760、768、1024、1440px` 六个视口的布局数据、元素越界检查和文档横向滚动检查。
- `viewport-390.png`、`viewport-1440.png`：强制清缓存刷新后生成的移动端和桌面端截图。
- `final-pdf-review-report.json`：两份正式 PDF 的页数、文件大小、团队名与占位符检查结果。
- `final-system-pdf-contact.png`、`final-database-pdf-contact.png`：两份 8 页正式 PDF 的逐页联系表。
- 旧的 `pdf-review-report.json`、`system-pdf-contact.png`、`database-pdf-contact.png` 对应早期 18/12 页扩展构建，已被正式 8 页版本取代，不纳入 GitHub 提交。

## 可复核结论

- 原型交互：导航、政策筛选/搜索、收藏、问答来源、材料清单、提醒取消与确认、画像保存、管理端核验提示、刷新持久化和空问题边界均通过。
- 响应式布局：六个视口的元素越界数组为空，且 `documentElement.clientWidth === scrollWidth`；`320px` 下实际 `scrollLeft` 为 0，`768px` 保持 200px 侧栏、隐藏画像栏和单列问答布局。
- 图示构建：16 张 Mermaid SVG 成功生成并通过 XML 校验。
- 正式 PDF：系统设计与数据库设计均为 8 页；文本层中“待填写”残留为 0，团队名可检索；逐页联系表未见裁切、重叠或空白页。

## 范围与限制

这些证据只覆盖本地 Markdown→SVG→HTML 构建、正式 PDF 文本/视觉检查和 `prototype/index.html` 离线补充原型。它们不证明正式墨刀链接、后端接口、实时政策检索、学校审批系统、真实通知服务或未经团队核验的政策事实已经可用。
