from fastapi import APIRouter
from app.api.v1 import auth, base, dict, rk, integrations, chat, task


api_router = APIRouter()

# 认证相关路由
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# 基础服务路由
api_router.include_router(base.router, prefix="/base", tags=["base"])

# 字典服务路由
api_router.include_router(dict.router, prefix="/dict", tags=["dict"])

# 招聘业务核心路由
api_router.include_router(rk.router, prefix="/rk", tags=["rk"])

# 集成服务路由（SharePoint、Teams、Email等）
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])

# AI对话路由
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

# 任务管理路由
api_router.include_router(task.router, prefix="/task", tags=["task"])