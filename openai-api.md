# OpenAI ChatGPT API 集成文档

本文档详细说明了与 OpenAI ChatGPT API 的集成方式，包括 API 接口定义、JWT Token 解析和错误处理策略。

---

## 1. ChatGPT API 接口定义

### 1.1 发送邀请

**接口信息**
```
POST https://chatgpt.com/backend-api/accounts/{account-id}/invites
```

**请求头**
```
Content-Type: application/json
Authorization: Bearer {AT}
chatgpt-account-id: {account-id}
```

**请求体**
```json
{
  "email_addresses": ["user@example.com"],
  "role": "standard-user",
  "resend_emails": true
}
```

**响应处理**
- `200/201`: 邀请成功
- `409`: 用户已是成员（需特殊处理，提示用户）
- `403`: Token 无效或权限不足
- `422`: 邮箱格式错误或 Team 已满
- `5xx`: 服务器错误，需重试

**重试策略**
- 最多重试 3 次
- 指数退避：1s, 2s, 4s
- 仅对 5xx 和网络超时错误重试
- 4xx 错误不重试，直接返回错误信息

---

### 1.2 查看团队成员

**接口信息**
```
GET https://chatgpt.com/backend-api/accounts/{account-id}/users?limit=50&offset=0
```

**请求头**
```
Authorization: Bearer {AT}
```

**响应格式**
```json
{
  "items": [
    {
      "id": "user-xxx",
      "account_user_id": "user-xxx__account-id",
      "email": "user@example.com",
      "verified_email": null,
      "name": "User Name",
      "role": "standard-user",
      "created_time": "2024-01-01T00:00:00Z",
      "is_scim_managed": false,
      "deactivated_time": null
    }
  ],
  "total": 3,
  "limit": 50,
  "offset": 0
}
```

**分页处理**
- 默认 limit=50，如果 total > 50 需要多次请求
- 使用 offset 参数获取后续页面
- 循环请求直到获取所有成员

**重试策略**
- 同发送邀请接口

---

### 1.3 获取 account-id 和订阅信息

**接口信息**
```
GET https://chatgpt.com/backend-api/accounts/check/v4-2023-04-27
```

**请求头**
```
Authorization: Bearer {AT}
```

**响应格式**
```json
{
  "accounts": {
    "{account-id}": {
      "account": {
        "account_id": "...",
        "name": "Team Name",
        "plan_type": "team",
        "...": "..."
      },
      "entitlement": {
        "subscription_plan": "chatgptteamplan",
        "expires_at": "2026-02-21T23:10:05+00:00",
        "renews_at": "2026-02-21T17:10:05+00:00",
        "has_active_subscription": true,
        "...": "..."
      },
      "features": []
    }
  },
  "account_ordering": []
}
```

**关键字段**
- `account.name`: Team 名称
- `account.plan_type`: 订阅类型（team/plus/free）
- `entitlement.expires_at`: 订阅到期时间
- `entitlement.subscription_plan`: 订阅计划
- `entitlement.has_active_subscription`: 是否有活跃订阅

**多 Team 处理**
- 优先选择 plan_type="team" 的账户
- 如果有多个 Team，选择 has_active_subscription=true 的
- 将所有 Team 类型的 account-id 存储到 team_accounts 表
- 默认使用第一个活跃的 Team 作为 primary

**重试策略**
- 同发送邀请接口

---

### 1.4 删除成员

**接口信息**
```
DELETE https://chatgpt.com/backend-api/accounts/{account-id}/users/{user-id}
```

**请求头**
```
Authorization: Bearer {AT}
chatgpt-account-id: {account-id}
```

**响应**
- 成功返回 200 或 204

**说明**
- user-id 格式为 `user-xxx`，从成员列表中获取
- 不能删除 owner 角色的成员

**错误处理**
- `403`: 无权限删除（可能是 owner）
- `404`: 用户不存在
- `5xx`: 服务器错误，需重试

**重试策略**
- 同发送邀请接口

---

## 2. JWT Access Token 解析

### 2.1 Access Token 结构

Access Token (AT) 是一个标准的 JWT，包含三部分：`Header.Payload.Signature`

**示例格式**
```
eyJhbGciOiJSUzI1NiIs...（Header）.eyJodHRwczovL2FwaS5vcGVuYWku...（Payload）.signature...（Signature）
```

---

### 2.2 Payload 关键字段

```json
{
  "https://api.openai.com/profile": {
    "email": "user@example.com",
    "email_verified": true
  },
  "https://api.openai.com/auth": {
    "user_id": "user-xxx",
    "chatgpt_compute_residency": "no_constraint",
    "chatgpt_data_residency": "no_constraint"
  },
  "exp": 1769877156,
  "iat": 1769013155
}
```

**字段说明**
- `https://api.openai.com/profile.email`: 用户邮箱
- `https://api.openai.com/profile.email_verified`: 邮箱是否已验证
- `https://api.openai.com/auth.user_id`: 用户 ID
- `exp`: Token 过期时间（Unix 时间戳）
- `iat`: Token 签发时间（Unix 时间戳）

---

### 2.3 解析实现

**Python 库**
- `PyJWT` 或 `python-jose`

**开发环境**
- 禁用签名验证（`verify=False`）

**提取邮箱**
```python
import jwt

# 生产环境：启用验证
payload = jwt.decode(
    token,
    key=public_key,
    algorithms=["RS256"],
    verify=True
)

# 提取邮箱
email = payload["https://api.openai.com/profile"]["email"]
```

---

### 2.4 错误处理

**验证失败场景**
- JWT 格式无效：拒绝导入并返回错误提示
- JWT 签名验证失败：拒绝导入并返回错误提示
- Token 过期（exp < 当前时间）：拒绝导入并提示用户更新 Token

**安全原则**
- 只有通过完整验证的 Token 才能存入数据库
- 生产环境必须启用签名验证
- 定期检查 Token 有效性

---

### 2.5 Token 正则表达式匹配

**AT Token 格式**
```regex
eyJhbGciOiJSUzI1NiIs[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+
```

**说明**
- JWT 以 `eyJhbGciOiJSUzI1NiIs` 开头（Base64 编码的 `{"alg":"RS256",`）
- 包含三部分，用 `.` 分隔
- 每部分由 Base64URL 字符组成（A-Z, a-z, 0-9, -, _）
