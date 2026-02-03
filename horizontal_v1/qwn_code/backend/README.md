# Work Assistant API

面向人力资源招聘场景的智能分析系统API，采用FastAPI + Python 3.11 + PostgreSQL + Redis的技术栈。

## 项目结构

```
/
├── backend/                    # 新的Python后端
│   ├── app/                   # 应用代码
│   │   ├── api/v1/           # API路由 (auth, base, dict, rk, integrations, chat, task)
│   │   ├── core/             # 核心组件 (config, events, middlewares, exceptions)
│   │   ├── db/               # 数据库相关 (session, dao)
│   │   ├── models/           # SQLAlchemy模型
│   │   ├── schemas/          # Pydantic模型
│   │   ├── services/         # 业务逻辑服务
│   │   └── workers/          # 消息队列消费者
│   ├── alembic/              # 数据库迁移
│   ├── main.py               # 应用入口
│   └── requirements.txt      # 依赖包
├── frontend/                 # 重构后的前端 (待实现)
│   └── src/
├── docker/                   # Docker相关配置
└── README.md
```

## 技术栈

- **后端**: Python 3.11 + FastAPI + LangChain
- **消息队列**: RabbitMQ (FastStream) + MQTT
- **数据**: PostgreSQL (主库) + Redis (缓存) + Socket.IO (消息更新)
- **文件**: Azure Blob Storage + SharePoint
- **AI/ML**: OpenAI GPT + LangChain + Dify (仅chat模式)
- **部署**: Docker + Kubernetes

## API规范

- **成功响应**: HTTP 200, Body `{ code: 1000, message: "success", result: ..., request_id: "..." }`
- **业务失败**: HTTP 200, Body `{ code: 1001, message: "错误提示", ... }`
- **字段命名**: 输出强制 `camelCase`，输入兼容 `snake_case` 和 `camelCase`
- **Header**: 必须读/回传 `x-request-id`，实现全链路日志追踪

## 路由策略

- **统一前缀**: `/api/v1/*`
- **兼容前缀**: `/v1/*` (保留用于与旧系统兼容)

## 快速启动

### 本地开发

```bash
# 安装依赖
pip install -r backend/requirements.txt

# 设置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env 文件配置数据库等连接信息

# 启动应用
python run_server.py
```

### Docker部署

```bash
# 构建镜像
docker build -t work-assistant-api .

# 运行容器
docker run -p 8000:8000 work-assistant-api
```

## 功能模块

- **Auth**: 认证授权模块 (登录、刷新令牌、权限验证)
- **Base**: 基础服务模块 (系统参数、菜单、部门、角色)
- **RK**: 招聘核心模块 (供应商、客户、简历、需求、匹配)
- **Chat**: AI对话模块 (Dify集成)
- **Task**: 任务管理模块 (定时任务、任务调度)
- **Integrations**: 集成服务模块 (SharePoint、Teams、Email)

## 约束与规范

- 严格遵守 `.qoder/repowiki-v1/zh/content/` 和 `wiki_improvement_suggestions_v1.md`
- 不得臆造新功能，不得删除现有可用功能
- 仅移除代码中明确标注 `deprecated` / `unused` / 注释掉 / 开关禁用的功能
- 所有HTTP响应遵循统一规范
- 使用异步非阻塞I/O操作
- 数据库操作使用SQLAlchemy (Async) + Alembic管理迁移
- 消息队列使用FastStream (RabbitMQ) + MQTT
- 遵循全链路日志追踪