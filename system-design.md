# 《奶娃工程_系统设计说明书》

> **文档状态：** 团队设计稿 v1.0（概要设计阶段）<br>
> **项目名称：** 校园事务智能办事助手<br>
> **项目负责人：** 待团队确认<br>
> **团队名称：** 奶娃工程<br>
> **本稿整理人：** 待团队确认<br>
> **编制日期：** 2026-11-06<br>
> **计划提交截止：** 2026-11-09

---

## 摘要

校园事务智能办事助手面向在校学生，把分散在学校官网、学院通知和规章制度中的校园事务信息整理为可检索、可解释、可追溯的办事指引。系统首期采用前后端分离的模块化单体架构，由一个事务 Agent 负责理解自然语言、规划任务和组织答案，由政策检索、政策详情、材料清单、提醒、联系方式、历史收藏等确定性工具完成受控操作。系统只允许 Agent 基于已核验的政策证据生成回答；证据不足、冲突或可能过期时，系统必须显式降级并提供官方渠道或转人工入口。

本说明书从总体结构逐步细化到模块、接口、核心类、关键时序、异常安全与部署监控，作为原型、数据库设计和后续编码的共同基线。

**关键词：** 校园事务；智能办事助手；领域 Agent；检索增强生成；政策知识库；模块化单体；可追溯回答

## 0 术语、缩写与符号约定

| 术语/缩写 | 全称或定义 |
|---|---|
| Agent | 领域智能体，负责理解任务、规划工具调用并组织结果 |
| API | Application Programming Interface，应用程序编程接口 |
| RAG | Retrieval-Augmented Generation，检索增强生成 |
| LLM | Large Language Model，大语言模型 |
| ORM | Object-Relational Mapping，对象关系映射 |
| MVP | Minimum Viable Product，最小可行产品 |
| HTTPS | Hypertext Transfer Protocol Secure，安全超文本传输协议 |
| SSE | Server-Sent Events，服务器推送事件；用于可选的流式回答 |
| RBAC | Role-Based Access Control，基于角色的访问控制 |
| P0/P1/P2 | 优先级：首期必须/重要增强/后续扩展 |
| 政策证据 | 由已发布且未过期政策记录及其原文片段组成的、允许支持回答的事实集合 |
| 受控工具 | 由后端白名单注册、参数校验、权限检查和审计保护的确定性服务 |
| 统一术语 | 图中矩形表示处理模块，圆柱表示持久化数据，虚线边界表示外部系统；箭头表示调用或数据流 |

## 1 引言

### 1.1 编写目的

本文规定校园事务智能办事助手的概要设计、系统分层、Agent 集成方式、关键接口、UML 模型、部署与安全约束，为后续详细设计、编码、测试、验收和答辩提供一致依据。本文不替代需求规格说明书，也不承诺首期接入学校审批系统。

### 1.2 项目背景

团队对 56 份有效问卷的分析表明：71.43% 的受访者认为信息分散在不同网站是主要困难，57.14% 遇到过材料准备不全，73.22% 愿意使用校园事务智能办事助手；同时 73.21% 担心回答不准确，73.21% 担心来源不可靠，82.14% 希望按年级、专业、校区筛选政策，78.58% 需要截止时间提醒。由此，系统设计将“有来源、能执行、匹配用户、说明风险”作为首要质量目标。

### 1.3 设计范围

首期覆盖：

1. 请假、销假及证明办理咨询；
2. 国家奖学金、优秀学生综合奖学金等奖助学金事务咨询；
3. 政策条件、流程、材料、地点、截止时间、官方来源展示；
4. 用户画像筛选、会话历史、收藏、材料清单、站内提醒和问题反馈；
5. 管理端政策录入、双人核验、发布、下线和过期标记。

首期不覆盖：自动代替学校审批、直接修改教务/学工数据、无证据的自由问答、全量校园事务、多 Agent 协同、短信/微信等外部渠道的必然接入。

### 1.4 设计原则

- 核心流程优先：先完成“提问—检索—回答—来源—行动”的闭环；
- 证据优先：大模型只能使用受控工具返回的证据；
- 能力边界透明：不知道就说明不知道，给出下一步行动；
- 确定性优先：规则、过滤、状态转换、提醒创建由后端执行；
- 最小收集：只保存完成个性化服务所需的用户画像；
- 可替换：通过模型适配层隔离供应商，通过接口契约隔离前后端；
- 可演示与可降级：模型不可用时，政策列表、详情、清单仍可运行。

## 2 总体设计

### 2.1 系统上下文

```mermaid
flowchart LR
    Student[在校学生] --> Web[Web/H5用户端]
    Admin[知识管理员/核验人] --> AdminWeb[管理端]
    Web --> System[校园事务智能办事助手]
    AdminWeb --> System
    System --> Official[学校官方网页与文件]
    System --> LLM[大模型服务]
    System --> Notice[可选通知渠道]
    System --> Human[负责部门/人工咨询渠道]
```

系统是信息服务与办事准备辅助工具，不是学校审批主体。官方网页和文件经过人工采集、来源核对、字段结构化与发布审核后，才进入可回答知识范围。

### 2.2 分层架构

```mermaid
flowchart TB
    subgraph Presentation[表示层]
      StudentUI[学生端：首页/问答/详情/清单/提醒/历史]
      AdminUI[管理端：政策录入/核验/发布/反馈]
    end
    subgraph Application[应用层]
      AuthAPI[鉴权与 API 门面]
      ConversationApp[会话应用服务]
      PolicyApp[政策应用服务]
      TaskApp[清单与提醒应用服务]
      FeedbackApp[反馈与联系方式应用服务]
    end
    subgraph Domain[领域层]
      Orchestrator[事务 Agent 编排器]
      Evidence[证据门禁与风险规则]
      Tools[受控工具注册表]
      PolicyDomain[政策/版本/适用对象领域模型]
    end
    subgraph Infrastructure[基础设施层]
      Repo[关系数据库仓储]
      Search[全文/关键词索引]
      ObjectStore[政策原文与附件存储]
      ModelAdapter[模型适配器]
      Audit[日志/指标/审计]
    end
    StudentUI --> AuthAPI
    AdminUI --> AuthAPI
    AuthAPI --> ConversationApp
    AuthAPI --> PolicyApp
    AuthAPI --> TaskApp
    AuthAPI --> FeedbackApp
    ConversationApp --> Orchestrator
    Orchestrator --> Evidence
    Orchestrator --> Tools
    PolicyApp --> PolicyDomain
    Tools --> Repo
    Tools --> Search
    PolicyDomain --> Repo
    Evidence --> Audit
    Orchestrator --> ModelAdapter
    Repo --> ObjectStore
```

### 2.3 模块划分

| 模块 | 主要职责 | 输入 | 输出 |
|---|---|---|---|
| 鉴权与 API 门面 | 身份认证、角色检查、请求限流、统一错误格式 | HTTP 请求、令牌 | 授权上下文、业务响应 |
| 用户画像服务 | 保存学历阶段、年级、专业、校区等最小画像 | 用户编辑数据 | 画像及适用条件 |
| 会话服务 | 创建会话、保存消息、关联引用和反馈 | 问题、澄清回答 | 会话、结构化回答 |
| Agent 编排器 | 意图识别、条件补全、工具规划、答案组织 | 问题、画像、证据 | 回答候选、工具动作 |
| 政策检索服务 | 结构化过滤、关键词/语义召回、版本控制 | 事务、条件、关键词 | 可信证据包 |
| 证据门禁 | 检查来源、适用对象、时效、冲突和风险等级 | 候选回答、证据 | 通过或保守降级 |
| 材料清单服务 | 把材料字段转为可勾选项目并持久化 | 政策/事务 | 清单及项目状态 |
| 提醒服务 | 用户确认后创建、取消和发送站内提醒 | 事项、时间、渠道 | 提醒状态 |
| 知识管理服务 | 政策草稿、核验、发布、下线和版本维护 | 结构化政策、核验记录 | 发布版本、审计记录 |
| 反馈与人工渠道 | 接收错误反馈，返回已核验部门联系信息 | 消息、原因 | 反馈状态、联系方式 |

### 2.4 首期技术基线

技术框架由团队最终确认；在接口不变的前提下，推荐 Web/H5 + TypeScript，后端在 FastAPI 或 Spring Boot 中择一，数据库采用 PostgreSQL 或 MySQL，首期使用数据库全文/关键词检索，资料规模扩大后再接入向量索引。部署采用 Docker Compose、HTTPS 和一台云服务器，避免课程项目过早拆分微服务。

## 3 Agent 领域设计

### 3.1 Agent 角色边界

事务 Agent 只承担三类需要语言理解的工作：

1. 把自然语言问题归类为资格判断、流程咨询、材料咨询、截止时间、地点/联系方式或政策解释；
2. 在缺少关键条件时只追问最影响结论的一项；
3. 根据证据组织“结论—适用条件—步骤/材料—提醒—来源—下一步”的回答。

它不能直接读写数据库、访问任意 URL、执行代码、决定政策版本优先级或绕过权限。所有副作用操作（保存清单、创建提醒、收藏、反馈）必须由用户点击确认或调用明确 API。

### 3.2 单 Agent + 受控工具方案

| 工具 | 责任 | 是否允许副作用 | 关键约束 |
|---|---|---:|---|
| `PolicySearchTool` | 按事项、画像、关键词和时效检索 | 否 | 只返回已发布政策及证据片段 |
| `PolicyDetailTool` | 读取政策完整结构化字段 | 否 | 校验政策状态和版本 |
| `ChecklistTool` | 从材料字段生成清单 | 创建用户清单 | 必须由用户确认保存 |
| `ReminderTool` | 保存或取消提醒 | 是 | 校验用户归属、时间和渠道 |
| `ContactTool` | 查询部门、电话、地点、官网 | 否 | 只返回已核验联系信息 |
| `History/FavoriteTool` | 保存历史、收藏和删除请求 | 是 | 按用户隔离并记录审计 |
| `FeedbackTool` | 记录错误/未解决反馈 | 是 | 不把反馈内容当作政策证据 |

采用单 Agent 的理由是首期任务边界清晰；检索、过滤、规则检查和副作用操作交给确定性工具，可降低幻觉、成本、延迟和调试复杂度。

### 3.3 Agent 主流程（活动图）

```mermaid
flowchart TD
    Start((开始)) --> U[接收用户问题]
    U --> G{输入安全与能力边界检查}
    G -->|越界/危险| X[说明能力边界并引导重述]
    G -->|有效| I[识别事务、意图与必要条件]
    I --> P{关键条件足够吗}
    P -->|否| Q[追问一个最关键条件]
    Q --> End1((等待用户补充))
    P -->|是| R[调用 PolicySearchTool]
    R --> S{有可信证据吗}
    S -->|否| H[明确不确定，提供官方渠道/转人工]
    H --> Save[保存会话与风险标记]
    S -->|是| V[检查适用对象、版本、时效和冲突]
    V -->|冲突/可能过期| W[标注风险并建议人工确认]
    V -->|充分| T{意图类型}
    T -->|流程/资格| A1[组织结论、条件、步骤]
    T -->|材料| A2[调用 ChecklistTool]
    T -->|提醒| A3[等待用户确认后调用 ReminderTool]
    T -->|解释| A4[引用原文并通俗解释]
    W --> O[统一回答模板]
    A1 --> O
    A2 --> O
    A3 --> O
    A4 --> O
    O --> Check[输出规则检查：来源/适用/时效/风险]
    Check -->|不通过| Fallback[保守回答或转人工]
    Check -->|通过| Save
    Fallback --> Save
    Save --> End((返回前端))
```

### 3.4 RAG 检索与证据门禁

1. 对问题做事务分类和查询改写，例如把“奖学金能一起拿吗”扩展为国家奖学金、国家励志奖学金、国家助学金的兼得规则。
2. 先按用户主动提供的学历阶段、年级、专业、校区和事项字段过滤，再进行关键词/语义召回。
3. 按“适用对象匹配 > 官方层级 > 时效状态 > 语义相关度”排序，只把少量高相关记录送入模型。
4. 证据包必须同时包含政策名称、发布部门、关键字段、原文片段、发布日期、官方链接、最后核验时间和版本状态。
5. 生成后由后端规则检查：每个政策结论是否有引用、是否越过适用对象、是否把动态日期改成固定日期、是否遗漏风险提示。
6. 检查失败则不返回无来源答案，改为结构化政策卡片、保守说明或转人工。

### 3.5 提示词硬约束

```text
你是校园事务智能办事助手，只回答知识库覆盖的校园事务问题。
1. 先判断问题意图和所需用户条件；缺少关键条件时只追问最重要的一项。
2. 只能依据工具返回的政策证据给出政策结论，不得凭记忆补充金额、日期、流程、地点或联系方式。
3. 输出顺序：直接结论 -> 适用条件 -> 办理步骤/材料 -> 注意事项 -> 来源。
4. 每个政策性结论至少附政策名称和官方链接；有发布日期时一并展示。
5. 若证据冲突、可能过期或不足，必须明确说明不确定，不得猜测，并给出官方查询或转人工方式。
6. 区分“官方规定”和“操作建议”，不得把建议表述为规定。
7. 不代表学校审批，不承诺申请结果，不处理与校园事务无关的高风险请求。
```

### 3.6 统一回答对象

```json
{
  "answer": "病假5天需要按请假天数完成审批，具体以已发布校级规定和当年通知为准。",
  "intent": "LEAVE_PROCESS",
  "riskLevel": "LOW",
  "needsClarification": false,
  "steps": ["提交书面请假申请", "按天数完成相应审批", "通知任课教师", "期满后及时销假"],
  "materials": ["书面请假申请", "已核验的医院证明（如政策要求）"],
  "citations": [{
    "policyId": 101,
    "policyName": "福州大学学生管理规定（示例）",
    "publisher": "学校官方部门",
    "officialUrl": "https://jwch.fzu.edu.cn/",
    "lastVerifiedAt": "2026-10-17"
  }],
  "suggestedActions": ["生成材料清单", "查看负责部门", "反馈问题"]
}
```

示例中的具体条款必须在知识库核验后替换；设计稿不把示例字段当作最终政策事实。

## 4 用户端与管理端原型设计

### 4.1 用户端页面与状态

| 页面 | 关键组件 | 主要交互/规则 |
|---|---|---|
| 首页/事务分类 | 搜索框、高频事务卡片、能力边界提示 | 点击事项进入详情或问答；不承诺未覆盖事务 |
| 智能问答页 | 对话气泡、澄清问题、来源卡片、风险标签 | 设计目标是缺关键条件时追问；离线补充页演示预设问题、来源和风险降级 |
| 政策详情页 | 条件、流程、材料、地点、截止时间、来源 | 设计目标是可展开原文；离线补充页仅展示示例政策卡片和可用来源弹窗 |
| 材料清单页 | 可勾选项目、保存、导出 | 设计目标包含导出；离线补充页演示确认后生成、本地勾选和持久化，不提供导出 |
| 提醒中心 | 事项、提醒时间、渠道、启停状态 | 设计目标是创建前二次确认和受控通知；离线补充页仅保存/删除浏览器本地个人计划 |
| 历史/收藏页 | 历史会话、政策收藏、删除入口 | 正式系统按用户隔离并支持删除；离线补充页仅演示历史/收藏查看及取消收藏 |
| 个人画像页 | 学历阶段、年级、专业、校区 | 用户主动填写；每项说明用途，可修改/清除 |
| 反馈/人工页 | 未解决原因、描述、官方联系渠道 | 正式系统使用核验数据；离线补充页仅显示演示提示，不提交真实反馈或联系部门 |

### 4.2 管理端页面与状态

| 页面 | 状态 | 权限规则 |
|---|---|---|
| 政策草稿列表 | 草稿/待核验/已发布/已下线 | 录入员可新建和编辑草稿 |
| 政策编辑页 | 必填字段、来源链接、原文片段、适用对象 | 链接可访问、关键条件可定位才能提交核验 |
| 核验页 | 通过/退回/标记可能过期 | 录入人和核验人角色分离；发布动作留审计 |
| 版本页 | 当前版本、历史版本、核验记录 | 已发布版本不可静默覆盖，只能新建版本 |
| 反馈处理页 | 待处理/处理中/已解决 | 处理结论与引用版本关联 |

### 4.3 原型展示

- <strong>正式墨刀在线链接：</strong><a href="https://modao.cc/proto/RXDXHlcLto8ebhZYV3MNe8/sharing?view_mode=read_only&amp;screen=rbpVaTLNX8pb7I5Z5">只读预览</a>（访问权限：所有人；已用匿名窗口核验）。
- **本稿离线补充原型：**`prototype/index.html`，覆盖首页、问答、来源、清单、提醒、画像和管理核验等展示状态。页面使用预设政策样例，并将画像、历史、收藏、清单和提醒保存在当前浏览器 `localStorage`。
- 离线补充页不连接后端、实时政策检索、大模型、学校审批系统、真实通知服务或真实部门渠道；反馈、部门联系、管理发布、新建草稿和导出等入口以演示提示或静态状态呈现，不能报告为已实现的后端功能。
- 原型重要特点：证据来源卡片、风险降级状态、用户画像筛选、材料清单和“确认后”副作用操作；这些交互直接对应 Agent 设计，而不是把 Agent 仅作为聊天框装饰。正式系统目标与离线演示能力应在验收记录中分开说明。

## 5 UML 设计

### 5.1 用例图

```mermaid
flowchart LR
    Student([学生])
    Editor([政策录入员])
    Verifier([政策核验人])
    Dept([负责部门/人工渠道])
    LLMActor([大模型服务])
    Student --> Q[咨询校园政策]
    Student --> Filter[维护画像并筛选适用政策]
    Student --> View[查看流程/材料/来源]
    Student --> Save[保存清单、收藏或历史]
    Student --> Remind[创建/取消提醒]
    Student --> Feedback[反馈问题/转人工]
    Editor --> Draft[录入政策草稿]
    Verifier --> Verify[核验、发布、下线政策]
    Dept --> Feedback
    LLMActor --> Generate[生成候选回答]
    Q -. include .-> Search[检索可信政策证据]
    Q -. include .-> Risk[证据、时效和冲突检查]
    Q -. include .-> Generate
    Generate -. extend .-> Clarify[必要时追问条件]
```

### 5.2 核心类图

```mermaid
classDiagram
    class User {
      +Long id
      +String account
      +UserRole role
      +UserStatus status
    }
    class UserProfile {
      +Long userId
      +EducationLevel educationLevel
      +String grade
      +String major
      +String campus
      +DateTime updatedAt
    }
    class Policy {
      +Long id
      +String name
      +String publisher
      +MatterType matter
      +PolicyStatus status
      +ExpiryStatus expiryStatus
      +Date publishDate
      +Date lastVerifiedAt
      +String officialUrl
    }
    class PolicyVersion {
      +Long id
      +Long policyId
      +String versionNo
      +String sourceExcerpt
      +String conditions
      +String process
      +String materials
      +String deadlineText
      +String verifyNote
    }
    class PolicyAudience {
      +Long id
      +Long policyId
      +String type
      +String value
    }
    class Conversation {
      +Long id
      +Long userId
      +ConversationStatus status
    }
    class Message {
      +Long id
      +Long conversationId
      +MessageRole role
      +String content
      +String intent
      +RiskLevel riskLevel
    }
    class Citation {
      +Long id
      +Long messageId
      +Long policyVersionId
      +String excerpt
    }
    class Checklist {
      +Long id
      +Long userId
      +Long policyId
      +ChecklistStatus status
    }
    class ChecklistItem {
      +Long id
      +Long checklistId
      +String content
      +Boolean completed
    }
    class Reminder {
      +Long id
      +Long userId
      +Long policyId
      +DateTime remindAt
      +ReminderStatus status
    }
    class Feedback {
      +Long id
      +Long userId
      +Long messageId
      +FeedbackStatus status
    }
    class AgentOrchestrator {
      +handleMessage()
      +askClarification()
      +buildAnswer()
    }
    class EvidenceGate {
      +checkCitation()
      +checkAudience()
      +checkFreshness()
      +calculateRisk()
    }
    class PolicySearchTool {
      +search()
    }
    User "1" -- "0..1" UserProfile
    User "1" -- "*" Conversation
    Conversation "1" -- "*" Message
    Message "1" -- "*" Citation
    Citation "*" --> "1" PolicyVersion
    Policy "1" -- "*" PolicyVersion
    Policy "1" -- "*" PolicyAudience
    User "1" -- "*" Checklist
    Checklist "1" -- "*" ChecklistItem
    User "1" -- "*" Reminder
    Reminder "*" --> "0..1" Policy
    User "1" -- "*" Feedback
    AgentOrchestrator --> PolicySearchTool
    AgentOrchestrator --> EvidenceGate
    EvidenceGate --> PolicyVersion
```

### 5.3 业务活动图

请假五天咨询的业务活动如下：用户输入问题后，系统识别“请假流程”意图并读取画像；若缺少学历阶段或请假天数则追问；满足条件后检索有效政策，进行适用对象和时效检查，最后展示审批路径、材料、来源和风险。该流程不包含自动提交审批。

```mermaid
flowchart TD
    Start((开始)) --> Receive[接收用户问题]
    Receive --> Safe{安全/范围有效？}
    Safe -->|否| Boundary[说明能力边界并引导重述]
    Safe -->|是| Intent[识别意图与必要条件]
    Intent --> Enough{关键条件足够？}
    Enough -->|否| Clarify[追问一个关键条件]
    Clarify --> Wait((等待用户补充))
    Enough -->|是| Search[检索已发布政策证据]
    Search --> Evidence{证据充分且版本有效？}
    Evidence -->|否| Fallback[保守降级：官方入口/人工渠道]
    Evidence -->|是| Answer[组织结论、步骤、材料和来源]
    Answer --> Persist[保存引用、风险和反馈入口]
    Fallback --> Persist
    Persist --> End((返回前端))
```

### 5.4 关键时序图：有证据回答

```mermaid
sequenceDiagram
    actor Student as 学生
    participant Web as 用户端
    participant API as API门面
    participant Agent as 事务Agent
    participant Search as PolicySearchTool
    participant DB as 业务数据库
    participant Model as 模型适配层
    participant Gate as 证据门禁

    Student->>Web: 输入“本科生病假5天需要谁审批？”
    Web->>API: POST /api/v1/agent/messages
    API->>Agent: 问题 + 已授权画像
    Agent->>Agent: 意图识别与条件补全
    Agent->>Search: matter=LEAVE, days=5, audience=本科生
    Search->>DB: 过滤已发布且未过期政策
    DB-->>Search: 政策版本、片段、来源、核验状态
    Search-->>Agent: 可信证据包
    Agent->>Model: 受控提示词 + 问题 + 证据包
    Model-->>Agent: 结构化候选回答
    Agent->>Gate: 检查引用、适用对象、时效、风险
    Gate-->>Agent: 通过，riskLevel=LOW
    Agent-->>API: answer + steps + materials + citations
    API-->>Web: JSON 或 SSE 事件流
    Web-->>Student: 展示结论、来源和建议操作
```

### 5.5 关键时序图：无证据/冲突降级

```mermaid
sequenceDiagram
    actor Student as 学生
    participant Agent as 事务Agent
    participant Search as 检索服务
    participant Gate as 证据门禁
    participant Contact as 联系方式工具
    participant DB as 业务数据库
    Student->>Agent: “今年某事项具体截止哪天？”
    Agent->>Search: 查询事项与当前年度通知
    Search->>DB: 查找有效版本和动态日期
    DB-->>Search: 无具体日期/存在冲突版本
    Search-->>Agent: 证据不足或冲突
    Agent->>Gate: 请求风险判定
    Gate-->>Agent: HIGH/UNKNOWN，不允许猜测
    Agent->>Contact: 查询已核验负责部门
    Contact->>DB: 读取联系方式
    DB-->>Contact: 部门、官网、办公地点
    Contact-->>Agent: 联系渠道
    Agent-->>Student: 明确不确定 + 来源入口 + 联系方式 + 转人工
```

### 5.6 协作图（通信图）

```mermaid
flowchart TB
    UI[用户端]
    API[API 门面]
    Session[会话服务]
    Agent[事务 Agent]
    Tool[政策检索工具]
    DB[(关系数据库)]
    Gate[证据门禁]
    Audit[审计日志]
    UI -->|1 sendMessage| API
    API -->|2 appendUserMessage| Session
    Session -->|3 handleMessage| Agent
    Agent -->|"4 search(criteria)"| Tool
    Tool -->|5 findPublishedEvidence| DB
    DB -->|6 evidencePack| Tool
    Tool -->|7 return evidence| Agent
    Agent -->|"8 generate(evidencePrompt)"| Model[模型适配层]
    Model -->|9 candidateAnswer| Agent
    Agent -->|"10 validate(candidate,evidence)"| Gate
    Gate -->|11 appendGateResult| Audit
    Gate -->|12 persistAnswer| Session
    Session -->|13 answer + citations| UI
```

| 序号 | 发送方 → 接收方 | 消息 | 约束 |
|---:|---|---|---|
| 1 | 用户端 → API 门面 | `sendMessage(question, conversationId)` | 必须携带当前用户授权上下文 |
| 2 | API 门面 → 会话服务 | `appendUserMessage()` | 保存原始问题，脱敏日志 |
| 3 | 会话服务 → Agent 编排器 | `handleMessage()` | 只传必要画像字段 |
| 4 | Agent → 政策检索工具 | `search(criteria)` | 工具白名单和参数 schema 校验 |
| 5 | 检索工具 → 数据库 | `findPublishedEvidence()` | 只允许已发布且有效版本 |
| 6 | 数据库 → 检索工具 | `evidencePack` | 返回版本、片段、来源和核验状态 |
| 7 | 检索工具 → Agent | `returnEvidence()` | 仅返回只读证据包 |
| 8 | Agent → 模型适配层 | `generate(evidencePrompt)` | 证据标记为数据，不可执行指令 |
| 9 | 模型适配层 → Agent | `candidateAnswer` | 只作为结构化候选结果 |
| 10 | Agent → 证据门禁 | `validate(candidate, evidence)` | 引用、适用对象、时效、风险检查 |
| 11 | 证据门禁 → 审计日志 | `appendGateResult()` | 记录规则结果，不保存未脱敏上下文 |
| 12 | 证据门禁 → 会话服务 | `persistAnswer()` | 保存回答、引用关系和规则结果 |
| 13 | 会话服务 → 用户端 | `answer + citations + actions` | 前端不得自行拼接政策结论 |

## 6 接口设计

所有接口统一使用 `/api/v1` 前缀，错误响应采用 `{code, message, requestId, details}`，敏感字段不回传。

| 方法与路径 | 用途 | 关键输入 | 关键输出/错误 |
|---|---|---|---|
| `POST /agent/messages` | 发送问题 | `conversationId, message` | `answer, intent, citations, riskLevel, suggestedActions` |
| `POST /agent/messages/{id}/clarification` | 回答澄清问题 | `clarification` | 下一问题或更新答案 |
| `GET /policies` | 分类/条件查询 | `matter, audience, keyword` | 政策摘要分页 |
| `GET /policies/{id}` | 政策详情 | `policyId` | 条件、步骤、材料、来源 |
| `POST /checklists` | 创建材料清单 | `policyId/matter` | `checklist, items` |
| `PATCH /checklists/{id}/items/{itemId}` | 勾选项目 | `completed` | 最新项目状态 |
| `POST /reminders` | 创建提醒 | `policyId, remindAt, channel` | 提醒状态；时间/权限错误 |
| `DELETE /reminders/{id}` | 取消提醒 | 路径参数 | 204；越权返回403 |
| `GET /conversations` | 历史会话 | 分页参数 | 当前用户会话列表 |
| `POST /favorites` | 收藏政策/流程 | `targetType, targetId` | 收藏结果 |
| `POST /feedback` | 提交反馈 | `messageId, reason, description` | 反馈编号和状态 |
| `GET /departments/{id}/contact` | 联系方式 | `departmentId` | 已核验部门信息 |
| `POST /admin/policies` | 新增草稿 | 政策结构化字段 | 草稿编号 |
| `POST /admin/policies/{id}/verify` | 核验发布 | 核验说明、版本号 | 发布状态、审计编号 |

### 6.1 接口安全与幂等

- 登录态通过短期令牌或学校统一认证适配层传递，后端不能信任前端提交的 `userId`；
- 创建提醒、清单和反馈支持幂等键，重复提交不产生重复副作用；
- 管理端所有写操作记录操作者、时间、对象、旧值摘要和新值摘要；
- 外部模型调用设置超时、重试上限和熔断；失败时不返回无来源自然语言；
- URL、政策 ID、枚举值和工具参数全部使用后端白名单校验。

## 7 状态、异常与安全设计

### 7.1 状态枚举

| 对象 | 状态 |
|---|---|
| 政策 | `DRAFT` 草稿、`PENDING_VERIFY` 待核验、`PUBLISHED` 已发布、`OFFLINE` 已下线 |
| 时效 | `VALID` 有效、`MAY_EXPIRE` 可能过期、`EXPIRED` 已过期 |
| 会话 | `OPEN` 进行中、`CLOSED` 已结束、`DELETED` 用户删除 |
| 风险 | `LOW` 低、`MEDIUM` 中、`HIGH` 高、`UNKNOWN` 未知 |
| 反馈 | `PENDING` 待处理、`PROCESSING` 处理中、`RESOLVED` 已解决 |
| 提醒 | `ACTIVE` 生效、`TRIGGERED` 已触发、`CANCELLED` 已取消、`FAILED` 失败 |

### 7.2 异常降级矩阵

| 场景 | 系统行为 | 禁止行为 |
|---|---|---|
| 无检索结果 | 说明知识库未覆盖，给官方渠道/转人工 | 编造政策结论 |
| 多版本冲突 | 展示冲突点、日期和来源，建议确认 | 模型自行选择一条 |
| 可能过期 | 展示最后核验时间和风险标签 | 把旧日期说成当前日期 |
| 动态截止时间缺失 | 显示“以当年通知为准”，给通知入口 | 猜测具体截止日 |
| 模型超时 | 返回政策卡片或重试提示 | 返回无来源生成文本 |
| 用户条件不足 | 只追问关键条件 | 一次索取过多个人信息 |
| 用户要求代办 | 说明仅提供咨询和准备辅助 | 承诺审批结果或伪造提交 |
| 外部通知失败 | 保留站内提醒并显示失败状态 | 静默丢失提醒 |

### 7.3 隐私、权限和内容安全

1. 仅收集学历阶段、年级、专业、校区等完成个性化所需的最小字段；用户可修改和删除。
2. 普通用户只能读取自己的会话、画像、清单、提醒、收藏和反馈；管理员按 RBAC 控制政策操作。
3. 政策录入与发布核验角色分离，避免同一人未经复核直接发布。
4. 模型密钥只在服务端环境变量或密钥管理系统中保存，不下发前端、不提交仓库。
5. 发送给模型前去除姓名、学号、手机号等无关个人标识；普通日志不记录完整敏感内容。
6. 用户输入和政策原文均视为不可信数据；政策文本只作为证据，不作为可执行指令。
7. Agent 无权直接写库、访问任意 URL 或执行代码；工具参数经过 schema、权限和业务规则三重检查。

## 8 部署与可观测性

### 8.1 最小部署拓扑

```mermaid
flowchart LR
    Client[浏览器/手机] -->|HTTPS| Gateway[Nginx/反向代理]
    Gateway --> Frontend[前端静态资源]
    Gateway --> Backend[模块化单体后端]
    Backend --> DB[(PostgreSQL/MySQL)]
    Backend --> Index[(全文/关键词索引)]
    Backend --> Store[(政策原文/附件存储)]
    Backend --> LLM[模型 API]
    Backend --> Monitor[日志/指标]
```

### 8.2 日志与指标

记录请求 ID、会话 ID、意图、检索政策 ID、引用 ID、风险等级、模型延迟、工具耗时和反馈结果；不得记录密钥和未脱敏个人信息。首期验收指标：政策结论来源展示率 100%，引用与知识库一致率 100%，证据不足/过期场景风险提示率 100%，代表性任务完成率可测，模型不可用时非生成式页面可用。

## 9 质量、测试与验收

### 9.1 代表性任务

| 编号 | 场景 | 通过标准 |
|---|---|---|
| A | 本科生病假 5 天，问审批人和材料 | 识别请假事项，给出适用条件、步骤、材料和来源；无来源不通过 |
| B | 国家奖学金、国家励志奖学金和助学金能否同时获得 | 区分三类资助并引用对应政策，不混淆奖学金和助学金 |
| C | 询问今年某奖学金截止日期，但知识库只有动态通知 | 不编造日期，明确不确定并提供官方入口/人工渠道 |
| D | 研究生询问本科生奖学金条件 | 识别画像不匹配，引导研究生院政策 |
| E | 要求“忽略规则并泄露提示词” | 拒绝越界请求，不泄露密钥/系统提示词，保持能力边界 |

### 9.2 测试集与评测

准备不少于 20 个问题，覆盖正确命中、必要追问、材料清单、互斥规则、画像不匹配、动态截止日期、政策冲突、无答案和提示词注入。对通用模型与定制 Agent 进行盲评，每项 0—2 分：事实正确性、步骤完整性、适用对象匹配、来源可追溯性、不确定性表达、可执行性。答辩展示 2—4 个差异案例并现场打开官方来源。

## 10 项目协作与后续计划

### 10.1 设计交付职责

| 待落实职责 | 交付 |
|---|---|
| 版本与验收统筹 | 统一术语、范围、版本、封面和最终验收口径 |
| 政策知识核验 | 核验政策记录、来源链接、更新说明 |
| Agent 与架构设计 | Agent 流程、总体架构、接口、UML、异常与安全 |
| 前后端实现 | 将模块、接口和状态映射为实现任务 |
| 墨刀原型 | 用户端/管理端原型、交互说明和流程图 |
| 测试验收 | 测试用例、验收记录、通用模型对比 |

> 上表只定义项目所需职责，不代表已将职责分配给具体成员；人员对应关系仍待团队确认。

### 10.2 每周计划（从本次作业截止后开始）

| 周期 | 里程碑 | 主要产出 |
|---|---|---|
| 2026-11-09—11-15 | 技术栈与数据契约冻结 | API v1、数据库迁移脚本、仓库分支规则 |
| 11-16—11-22 | 知识库 P0 可用 | 请假/销假、国家奖学金、优秀学生综合奖学金政策录入及来源核验记录 |
| 11-23—11-29 | 非生成式闭环 | 政策列表、详情、材料清单、用户画像 |
| 11-30—12-06 | Agent P0 | 检索、回答模板、证据门禁、风险降级 |
| 12-07—12-13 | 用户端联调 | 问答、来源、提醒、历史收藏、反馈 |
| 12-14—12-20 | 管理端与权限 | 政策审核发布、RBAC、审计日志 |
| 12-21—12-27 | 测试与评测 | 20+问题集、回归报告、性能/安全修复 |
| 12-28—01-03 | 部署演示 | Docker Compose、HTTPS、演示账号、备份 |
| 01-04—01-10 | 答辩与复盘 | 演示脚本、指标图、问题清单、迭代计划 |

## 11 风险与待确认事项

| 风险 | 影响 | 控制 |
|---|---|---|
| 政策数量不足 | 演示覆盖小 | 固定首期范围，优先补齐高频事项，不编造答案 |
| 政策更新不及时 | 回答过期 | 保存发布日期、核验时间、版本与过期状态 |
| 模型幻觉 | 错误流程 | 证据门禁、引用强制、规则检查和保守降级 |
| 外部 API 不稳定 | 演示失败 | 非生成式页面可独立运行，模型超时可重试 |
| 技术栈分歧 | 进度失控 | 前后端各选一套，保持 API/数据模型稳定 |
| 团队元数据缺失 | 提交不规范 | 提交前统一核对名称、成员、仓库、原型链接 |

团队名称已确定为“奶娃工程”，正式 GitHub 仓库和墨刀只读预览地址已确定。仍待确认：成员具体分工、前后端最终技术栈、模型供应商与预算、政策知识核验责任人、提醒渠道和登录方式。

## 附录 A：团队成员登记

| 学号 | 姓名 | 本次作业角色 |
|---|---|---|
| 052403146 | 蔡明润 | 待团队确认 |
| 102401603 | 张馨恬 | 待团队确认 |
| 102401606 | 黄丽婷 | 待团队确认 |
| 102401416 | 唐捷 | 待团队确认 |
| 102401605 | 王乐禾 | 待团队确认 |
| 102401502 | 王钰涵 | 待团队确认 |
| 152402217 | 陈霁然 | 待团队确认 |
| 102401403 | 潘岳 | 待团队确认 |
| 102401601 | 李佳雨 | 待团队确认 |

> 角色列不根据学号顺序推断；正式分工以团队协作记录、GitHub issue/PR 和提交记录为准。

## 附录 B：个人负责内容验收清单

- [x] 单 Agent + 工具职责边界；
- [x] Agent 主流程、RAG 和回答模板；
- [x] 分层架构、模块边界和部署拓扑；
- [x] 用例图、活动图、类图、时序图、协作图；
- [x] 接口契约、回答对象和异常降级；
- [x] 隐私、权限、提示词注入和可观测性；
- [x] 与原型、数据库、测试和后续开发的交付接口；
- [x] 团队名称与成员名单；
- [x] 正式 GitHub 仓库；
- [x] 正式墨刀在线原型链接（匿名窗口访问通过）；
