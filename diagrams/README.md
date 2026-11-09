# 图示说明

本目录存放可直接插入博客或 PDF 的静态图示。`system-design.md` 与 `database-design.md` 中的 Mermaid 块是唯一语义源，构建脚本使用固定版本的 Mermaid CLI 直接生成 SVG，避免参与者、实体、关系和消息编号在两份稿件间漂移。

生成/刷新图示：

```powershell
python .\scripts\make-diagrams.py
```

生成环境需要 Python 3.10+、Node.js 20+ 和 `npx`；首次执行会下载固定版本 `@mermaid-js/mermaid-cli@11.12.0`。生成器会校验 Mermaid 块数量、CLI 退出状态和 SVG XML 有效性。

图示清单（共 16 张：系统 10 张、数据库 6 张）：

- `architecture.svg`：系统逻辑架构；
- `agent-flow.svg`：Agent 主流程与风险降级；
- `context.svg`：系统上下文与边界；
- `use-case.svg`：主要用例及参与者；
- `class-model.svg`：核心领域类及关系；
- `activity.svg`：有证据回答的业务活动；
- `sequence.svg`：有证据回答的关键时序；
- `fallback-sequence.svg`：无证据或冲突时的降级时序；
- `collaboration.svg`：对象协作与 1—13 号通信消息；
- `deployment.svg`：最小部署拓扑；
- `lifecycle.svg`：政策知识生命周期；
- `er-model.svg`：数据库 ER 总览；
- `er-identity.svg`：用户、角色与权限局部 ER；
- `er-evidence.svg`：政策、版本、来源与引用局部 ER；
- `er-workflow.svg`：会话、清单、提醒与反馈局部 ER；
- `agent-boundary.svg`：Agent、工具、数据库、索引与证据门禁边界；

`er-model.svg` 保留全量结构导航；三张局部 ER 图用于打印阅读字段较多的关系。局部图中的重复实体仍指向总览中的同一张表，不代表新增实体或关系。所有图的唯一语义源仍是两个 Markdown 源稿，SVG 不应手工单独修改。
