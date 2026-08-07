# Harness-Agent 底座与多 Agent 创作

## 什么是 Harness Agent

“Harness”意思是“约束带”。Harness Agent 不是全能 Agent，而是：

> 一个只能围绕剧本创作对话、状态和资料工具工作的有边界 Agent。

`data/skills/harness_agent.md` 写得非常清楚：

```
- 不直接处理文件系统、命令执行或通用任务代理能力
- 优先使用显式传入的剧本创作业务工具
- 记忆文档必须按 isolation_key 隔离
```

这是 Agent 工程最重要的一课：**能力边界不是缺陷，是设计**。

## 运行时协议：可以换引擎

```python
class ScriptAgentRuntime(Protocol):
    def stream_chat(self, request: ScriptAgentInput) -> AsyncIterator[ScriptAgentEvent]: ...

class HarnessAgent:
    def __init__(self, *, runtime: ScriptAgentRuntime): ...
```

业务层只依赖 `HarnessAgent` 门面，实际跑在：

```
DeepAgentsRuntime（默认，deepagents 框架）
CrewAIStageRuntime（团队创作）
```

换 Agent 框架 = 换一个 runtime 实现，业务零改动。这就是协议（Protocol）的威力。

## 统一事件流

不同框架吐出来的 chunk 不一样，所以 `ScriptAgentEvent` 统一成：

```python
ScriptAgentEvent(type="message.delta", content=..., data={...})
ScriptAgentEvent(type="done", content=..., data={...})
ScriptAgentEvent(type="structured_response", ...)
```

`DeepAgentsRuntime._chunk_to_event` 负责把：

```
BaseMessage / tuple / dict / messages 列表
```

全部归一化成事件。前端和业务层永远只看一种协议。

## 工具：业务工具 + 网关工具

剧本创作 Agent 有四个业务工具：

```
get_workspace      读取三阶段工作区
get_project_config 读取创作配置
get_novel_events   按章节范围读取事件
get_rag_context    读取已召回资料
```

它们以 Markdown 文档定义（`data/script/tools/*.md`），包括用途、参数、使用时机，甚至“禁止凭记忆编造”的约束。工具文档即代码。

Agent 的模型接入走：

```
ProviderGatewayChatModel（LangChain BaseChatModel）
  → ModelGatewayAdapter
  → ProviderModelGateway
```

`bind_tools` 让 deepagents 能发起工具调用，而模型能力来自项目自己的 Provider 体系。

## 记忆：三层隔离

```
短期记忆  InProcessShortTermMemory  会话运行态 + asyncio 锁
长期记忆  deepagents AGENTS.md 文档  按 isolation_key 生成路径
向量记忆  ChromaVectorMemory         项目资料检索
```

`HarnessMemoryScope._safe_scope_name` 把会话 key 变成安全文件名，避免路径注入。

## 多 Agent：三阶段 + 团队

创作流程是状态机：

```
创作配置 → 故事骨架(skeleton) → 改编策略(strategy) → 剧本(script)
```

每个阶段有独立 Skill：

```
data/skills/screenwriting/
  creation_config_agent        创作配置助理
  story_skeleton_agent         故事骨架助理
  adaptation_strategy_agent    改编策略助理
  screenplay_generation_agent  剧本生成助理
```

`CrewAIStageRuntime` 支持把“剧本生成”拆成一个小队：

```
导演 / 编剧 / 节奏 / 台词……（按阶段配置成员）
```

每个成员有 role、goal、backstory，任务描述里注入当前上下文。这就是 CrewAI 的多 Agent 协作。

## 质量护栏：生成完必须自检

```
生成 → clean_stage_output → ensure_stage_output_quality
  → 不合格 → build_stage_repair_message → 自修复（最多 2 次）
  → 仍失败 → 明确报错，不硬塞
```

质量检查包括：

```
骨架：有没有模板占位词（“主角的核心目标”这类）
剧本：场景数、对白行数、动作行数、集时长比例、分集是否连续
```

这是“AI 输出不可控 → 用规则做护栏”的标准解法。

## 面试怎么答“Agent 怎么设计的”

> “我们设计了一个 Harness 底座：统一运行时协议、统一事件流、业务工具按文档注册、记忆按会话隔离；单 Agent 先跑通三阶段创作，再通过 CrewAI 做阶段团队协作。每个阶段有独立 Skill 提示词和运行时契约，生成结果经过规则质量校验，不合格自动携带失败原因自修复。换模型、换 Agent 框架都不影响业务层。”

面试官最想听的不是“我用了 LangGraph”，而是**边界、协议、可替换性、质量闭环**。
