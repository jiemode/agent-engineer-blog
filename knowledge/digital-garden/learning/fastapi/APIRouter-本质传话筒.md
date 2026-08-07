我们在写大项目时，因为API过多，一般不会直接：
```
app = FastAPI()

@app.get("/users")
async def users():
    ...

@app.post("/chat")
async def chat():
    ...

@app.get("/models")
async def models():
    ...

@app.post("/login")
async def login():
    ...
```
这样写在main.py里面，那样会显得太臃肿
所以我们需要建立routers文件夹这样一个“传话筒”：
```
backend/

├── routers/
│
├── chat.py
├── user.py
├── workflow.py
├── auth.py
├── agent.py
├── tool.py
└── knowledge.py
```
每一个py文件只负责一类接口
例如：
```
# routers/chat.py

router = APIRouter()

@router.post("/chat")
async def chat():
    ...
```
# 那APIRouter到底时什么？
是fastapi的“子路由”
可以把它理解成：

以前：

只有一本通讯录。

```
FastAPI

↓

所有电话

都记这里
```

后来人越来越多。

于是：

```
家庭一本

公司一本

朋友一本

客户一本
```

最后需要的时候再合并

APIRouter就是这个意思

# 真正的大项目启动过程

```
app = FastAPI()

app.include_router(chat_router)

app.include_router(user_router)

app.include_router(auth_router)
```

这里FastAPI其实在干：

```
chat.py

↓

所有chat接口

↓

加入总路由
```

然后：

```
user.py

↓

加入总路由
```

最后FastAPI拥有全部API

大项目的目录一般都是：
```
backend/

app/

│

├── routers/

│      chat.py

│      auth.py

│      workflow.py

│      agent.py

│      tool.py

│      user.py

│

├── services/

├── repositories/

├── models/

├── schemas/

├── core/

├── config/

└── main.py
```