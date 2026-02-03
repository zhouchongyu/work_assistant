// frontend/src/api/modules/chat.ts
import http from '../http';
import { AxiosPromise } from 'axios';

// 聊天消息请求类型
export interface ChatMessageRequest {
  query: string;
  conversationId?: string;
  inputs?: { [key: string]: any };
  responseMode?: string;
}

// 聊天消息响应类型
export interface ChatMessageResponse {
  code: number;
  message: string;
  result: {
    answer: string;
    conversationId: string;
    messageId: string;
  };
  requestId?: string;
}

// 聊天历史请求类型
export interface ChatHistoryRequest {
  conversationId: string;
  limit?: number;
  offset?: number;
}

// 聊天历史项类型
export interface ChatHistoryItem {
  id: string;
  query: string;
  answer: string;
  createdAt: string;
}

// 聊天历史响应类型
export interface ChatHistoryResponse {
  code: number;
  message: string;
  result: {
    items: ChatHistoryItem[];
    total: number;
  };
  requestId?: string;
}

// 会话列表请求类型
export interface ConversationListRequest {
  limit?: number;
  offset?: number;
}

// 会话类型
export interface Conversation {
  id: string;
  name: string;
  createdAt: string;
  updatedAt: string;
}

// 会话列表响应类型
export interface ConversationListResponse {
  code: number;
  message: string;
  result: {
    items: Conversation[];
    total: number;
  };
  requestId?: string;
}

/**
 * 发送聊天消息
 * @param data 聊天消息请求数据
 * @returns 聊天消息响应
 */
export const sendChatMessage = (data: ChatMessageRequest): AxiosPromise<ChatMessageResponse> => {
  return http.post('/chat/chat', data);
};

/**
 * 获取聊天历史
 * @param params 聊天历史请求参数
 * @returns 聊天历史响应
 */
export const getChatHistory = (params: ChatHistoryRequest): AxiosPromise<ChatHistoryResponse> => {
  return http.post('/chat/messages_detail', params);
};

/**
 * 获取会话列表
 * @param params 会话列表请求参数
 * @returns 会话列表响应
 */
export const getConversationList = (params: ConversationListRequest): AxiosPromise<ConversationListResponse> => {
  return http.post('/chat/messages', params);
};