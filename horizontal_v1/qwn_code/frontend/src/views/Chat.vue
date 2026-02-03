<template>
  <div class="chat">
    <h2>AI助手</h2>
    <div class="chat-container">
      <div class="chat-messages" ref="messagesRef">
        <div 
          v-for="(message, index) in messages" 
          :key="index" 
          :class="['message', message.role]"
        >
          <div class="message-content">{{ message.content }}</div>
          <div class="message-time">{{ formatDate(message.timestamp) }}</div>
        </div>
      </div>
      <div class="chat-input-area">
        <input
          v-model="inputMessage"
          type="text"
          placeholder="请输入您的问题..."
          @keyup.enter="handleSendMessage"
        />
        <button @click="handleSendMessage" :disabled="!inputMessage.trim()">
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';
import apiClient from '@/api/http';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const messages = ref<Message[]>([
  {
    id: '1',
    role: 'assistant',
    content: '您好！我是工作助手AI，我可以帮助您解答关于招聘、简历分析、需求匹配等方面的问题。',
    timestamp: new Date()
  }
]);
const inputMessage = ref('');
const messagesRef = ref<HTMLDivElement>();

const formatDate = (date: Date) => {
  return date.toLocaleString('zh-CN');
};

const scrollToBottom = async () => {
  await nextTick();
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight;
  }
};

const handleSendMessage = async () => {
  if (!inputMessage.value.trim()) return;

  const userMessage: Message = {
    id: Date.now().toString(),
    role: 'user',
    content: inputMessage.value.trim(),
    timestamp: new Date()
  };

  messages.value.push(userMessage);
  const messageToSend = inputMessage.value.trim();
  inputMessage.value = '';

  try {
    // 调用AI对话API
    const response = await apiClient.post('/chat/completion', {
      query: messageToSend,
      conversation_id: 'default_conversation'
    });

    if (response.code === 1000) {
      const aiMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: response.result.answer,
        timestamp: new Date()
      };
      messages.value.push(aiMessage);
    } else {
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `抱歉，AI服务暂时不可用：${response.message}`,
        timestamp: new Date()
      };
      messages.value.push(errorMessage);
    }
  } catch (error) {
    console.error('Chat error:', error);
    const errorMessage: Message = {
      id: Date.now().toString(),
      role: 'assistant',
      content: '抱歉，AI服务暂时不可用，请稍后再试。',
      timestamp: new Date()
    };
    messages.value.push(errorMessage);
  } finally {
    await scrollToBottom();
  }
};

onMounted(() => {
  scrollToBottom();
});
</script>

<style scoped>
.chat {
  padding: 2rem;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 600px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background-color: #f5f5f5;
}

.message {
  margin-bottom: 1rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  max-width: 80%;
}

.message.user {
  align-self: flex-end;
  background-color: #409eff;
  color: white;
  margin-left: auto;
}

.message.assistant {
  align-self: flex-start;
  background-color: #e6f3ff;
  color: #333;
  margin-right: auto;
}

.message-time {
  font-size: 0.8rem;
  color: #909399;
  text-align: right;
  margin-top: 0.25rem;
}

.chat-input-area {
  display: flex;
  padding: 1rem;
  border-top: 1px solid #e4e7ed;
  background-color: white;
}

.chat-input-area input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  margin-right: 0.5rem;
}

.chat-input-area button {
  padding: 0.5rem 1rem;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.chat-input-area button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>