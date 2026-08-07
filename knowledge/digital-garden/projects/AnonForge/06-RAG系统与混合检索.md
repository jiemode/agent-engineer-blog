# RAG 系统与混合检索

## RAG 在项目里的位置

```
小说章节 → 事件清洗（LLM 结构化）→ 章节事件
    ↓
RAG 索引（分块 + 向量化 + Chroma）
    ↓
用户提问 → 意图解析 → 混合检索 → 上下文注入 Agent
```

不是所有问题都要全量检索。项目先把问题分成几类：

```
“第 20 章发生了什么”      → 章节事件精确查找
“李明的眼睛颜色”          → 字段级查找（元数据）
“导演风格/镜头/画面”       → 视觉资料检索
“请生成故事骨架”          → 阶段创作专用检索
“帮我改一下集数”          → 配置链路，根本不走 RAG
```

## 向量化：本地 Embedding

`core/agent/embedding.py` 用本地模型 `bge-small-zh-v1.5`：

```
ONNX Runtime 推理 + tokenizers 分词
批量 encode → mean pooling → L2 归一化
```

为什么本地而不是调 API？

- 隐私（小说内容不出机器）
- 零成本、低延迟
- 本地模型对中文足够好

`AgentEmbeddingDiagnostics` 记录模型/分词器就绪状态，向量服务不可用时系统能优雅降级到词法检索。

## 向量库：Chroma

`core/harness/memory/vector.py` 的 `ChromaVectorMemory`：

```python
upsert(chunks)            # 批量写入/更新
query(isolation_key, ...) # 按会话隔离查询
replace_scope(...)        # 重建某会话的索引
delete_ids(...)           # 删除陈旧文档
```

隔离是关键：每个 `isolation_key`（项目 + 用户 + 会话）有自己的检索空间，A 用户的创作资料不会被 B 用户检索到。

## 分块策略

```
chunk_chars = 900
chunk_overlap = 120
```

重叠是为了避免语义被截断在边界。`_chunk_id(source_id, index)` 保证每个 chunk 有稳定 ID，`_chunk_content_hash` 用于增量判断“文档变没变”。

## 混合检索：多条腿走路

`ScreenwritingRagIndex.retrieve_context` 按意图组合多条检索路径：

```
1. 向量检索        → 语义相似（余弦距离转分数）
2. 词法检索        → 关键词命中（lexical_score）
3. 元数据精确命中   → 章节号、事件 ID、字段值
4. 章节范围查询     → “第 20-25 章”直接按索引区间取
5. 字段查询        → “李明的眼睛”查人物资料字段
6. 视觉意图检索     → 导演/镜头/画面关键词走技能资料
```

最后 `_merge_ranked_hits` 做分数融合与去重，返回：

```
text      → 已编排的上下文全文（可直接注入提示词）
hits      → 命中明细（来源、标题、得分、片段）
runtime   → 检索模式诊断（面试时可讲可观测性）
```

## 意图解析：规则优先，LLM 兜底

`query_intent.py` 用正则解析：

```
“第 20 章”        → ChapterRangeIntent
“20-25 章”        → ChapterRangeIntent
“李明的眼睛颜色”   → FieldLookupIntent
```

为什么不用 LLM 做所有意图识别？因为规则：

- 零延迟
- 可测试
- 结果确定

复杂问题再交给 `query_intent_llm.py`。这是“能规则就规则，规则不够再上模型”的工程范式。

## 检索结果如何进入 Agent

```
prepare_rag_context() → RagContext(text, hits, runtime)
  → build_system_prompt_with_rag(base_prompt, context)
  → get_rag_context 工具可让 Agent 按需再取完整命中
```

系统提示词放“精选摘要”，Agent 需要更多细节时可以调用工具。这避免上下文爆炸。

## 面试怎么答“RAG 怎么做的”

> “先通过章节事件清洗把小说变成结构化事实，再本地 bge 模型向量化进 Chroma，按会话隔离。检索不是单一向量召回：我们根据问题意图组合章节范围、字段元数据、词法、视觉技能资料等多条路径，最后融合排序。规则能确定的问题走规则，复杂问题走 LLM 意图识别，保证延迟和可测试性。”

加分句：**增量索引**（内容 hash 判断文档是否变化）、**降级路径**（向量不可用时回退词法）、**检索诊断 runtime**。
