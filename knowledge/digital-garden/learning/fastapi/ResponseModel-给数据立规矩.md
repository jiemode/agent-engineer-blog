# 为什么会出现Response Model？
现在ai agent返回的数据越来越复杂：
```
{
    "answer":"你好",

    "tool_calls":[...],

    "reasoning":"...",

    "usage":{

        "prompt_tokens":100,

        "completion_tokens":50

    },

    "finish_reason":"stop"
}
```
不能让大家想到什么就return什么，要不然项目会爆炸，所以要统一度量衡，在这种情况下，响应模型应运而生

大家现在都喜欢
先定义：
```
class ChatResponse(BaseModel):

    ...
```
(basemodel是pydantic中重要的类)
再
```
@app.post(
    "/chat",
    response_model=ChatResponse
)
```