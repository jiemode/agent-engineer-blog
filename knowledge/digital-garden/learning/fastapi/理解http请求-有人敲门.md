# 理解http请求才能更好理解fastapi
结合fastapi中的path，query，body，我们可以画出一下图表：
```
                👤 用户
                  │
                  ▼
         浏览器 / 前端(Vue、React)
                  │
          发送 HTTP 请求
                  │
                  ▼
      Uvicorn（真正监听 8000 端口）
                  │
                  ▼
       FastAPI（负责处理请求）
                  │
        根据路由查找函数
                  │
          @app.get() / @app.post()
                  │
                  ▼
      解析请求中的数据
      ├── Path（路径参数）
      ├── Query（查询参数）
      └── Body（JSON 请求体）
                  │
                  ▼
    Pydantic(BaseModel)
    JSON → Python 对象
                  │
                  ▼
        调用你的 Python 函数
                  │
                  ▼
            return 返回结果
                  │
                  ▼
   Python 对象 → JSON（FastAPI 自动完成）
                  │
                  ▼
         Uvicorn 返回 HTTP Response
                  │
                  ▼
        浏览器显示最终结果
```

另外附上http请求方法的区别：
```
| 方法     | 作用        | 是否通常有 Body | 是否修改服务器 |
| ------ | --------- | ---------- | ------- |
| GET    | 获取资源      | 通常没有       | ❌ 不修改   |
| POST   | 创建资源、提交数据 | ✅ 有        | ✅ 通常会修改 |
| PUT    | 整体更新资源    | ✅ 有        | ✅ 会修改   |
| PATCH  | 局部更新资源    | ✅ 有        | ✅ 会修改   |
| DELETE | 删除资源      | 一般没有（也可以有） | ✅ 会修改   |

```
> **把一次 HTTP 请求，翻译成一次普通的 Python 函数调用。**

当建立了这个整体模型之后，再去阅读 FastAPI 或 AI Agent 项目的源码，就不会觉得是在记忆零散的知识点，而是在理解一套完整而统一的设计思想。

这也是我目前学习 FastAPI 最大的收获。