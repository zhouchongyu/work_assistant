from fastapi import APIRouter, Depends
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse, ChatHistoryRequest, ChatHistoryResponse, ConversationListRequest, ConversationListResponse
from app.services.chat_service import ChatService
from app.api.v1.auth import get_current_user


router = APIRouter()
chat_service = ChatService()


@router.post("/completion", response_model=ChatMessageResponse)
async def chat_completion(
    request: ChatMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """聊天补全接口"""
    return await chat_service.chat_completion(request)


@router.post("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    request: ChatHistoryRequest,
    current_user: dict = Depends(get_current_user)
):
    """获取聊天历史"""
    return await chat_service.get_chat_history(request)


@router.post("/conversations", response_model=ConversationListResponse)
async def get_conversations_list(
    request: ConversationListRequest,
    current_user: dict = Depends(get_current_user)
):
    """获取会话列表"""
    result = await chat_service.get_conversations_list(
        user_id=current_user.get("id", "default_user"),
        limit=request.limit,
        offset=request.offset
    )
    
    return ConversationListResponse(**result)


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "chat"}