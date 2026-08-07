---
title: JWT 数字认证与 payload 详解
description: 从 create_access_token 出发，彻底搞懂 JWT 的三个部分
---

# JWT 数字认证与 payload 详解

这是我用 `agent_engineer` 做博客项目第 3 课时的补课笔记。当时我看到 `create_access_token` 里那一坨 `payload` 是懵的，后来发现只要把它当成“一张带印章的信封”，一切都通了。

## JWT 是什么

JWT 不是加密，而是一张带签名的 JSON 通行证。它长这样：

```text
xxxxx.yyyyy.zzzzz
```

- `xxxxx` = header：声明用了什么算法
- `yyyyy` = payload：你想装的信息
- `zzzzz` = signature：服务端盖的防伪章

我们的登录接口返回的一长串 token，就是这三个部分用 `.` 拼出来的。

## payload 逐字段翻译

我们的 `create_access_token` 里写的是：

```python
payload = {
    "sub": str(user_id),
    "type": "access",
    "iat": now,
    "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
}
```

| 字段 | 英文全称 | 含义 | 为什么这么设计 |
| --- | --- | --- | --- |
| `sub` | subject | 令牌的主人 | 服务端从 `sub` 知道“你是谁”，也就是用户 id |
| `type` | 自定义 | 令牌类型 | 以后加 refresh token 时，可以区分 access / refresh |
| `iat` | issued at | 签发时间 | 审计、判断 token 是不是很久以前签的 |
| `exp` | expires at | 过期时间 | PyJWT 验证时自动检查，过期直接报错 |

几个值得记住的细节：

- `sub` 要转成字符串。JWT 规范建议 subject 是字符串，避免不同语言之间的类型混乱。
- `type` 不是 JWT 标准字段，是我们自己加的约定。JWT 允许自定义字段，但别放敏感信息。
- `iat` / `exp` 传的是带时区的 datetime，PyJWT 会自动转成 Unix 时间戳。

## 签名到底在保护什么

HS256 的签名过程可以理解成：

```text
signature = HMAC-SHA256(header + "." + payload, SECRET_KEY)
```

验证时：

```text
1. 用同样的 SECRET_KEY 重新算一遍指纹
2. 和 token 里带的 signature 比较
3. 一致 → 内容和签名匹配，通过
4. 不一致 → 说明有人改过 payload，直接 401
```

所以“数字认证”在这里的意思是：**服务器能证明这张令牌确实是它自己签发的，而且内容没有被偷改**。

攻击者可以解码 payload 看到内容（因为只是 base64，不是加密），但他不知道 `SECRET_KEY`，改一个字符后无法重新算出正确签名。

## 登录到鉴权的完整流程

```text
用户登录
  → 密码校验通过
  → create_access_token(user.id)
  → 返回 token
  → 前端存起来
  → 每次请求带 Authorization: Bearer <token>
  → get_current_user 验签 + 查过期
  → 从 sub 拿到 user_id → 查出用户
```

我们的 `get_current_user` 里的 `decode_access_token(credentials.credentials)` 就是那个“验签 + 查过期”的步骤。

## 三个必须记住的坑

1. payload 是明信片，不是信封。谁都能 base64 解码，永远别放密码、密钥。
2. `exp` 一定要设，否则 token 永不过期。
3. `SECRET_KEY` 要随机且只存在服务端。丢了等于任何人都能伪造 token。

## 面试一句话总结

JWT 的 payload 是写在明信片上的信息，签名是服务端盖的防伪章；`sub` 告诉服务器你是谁，`exp` 告诉服务器这封信什么时候作废。
