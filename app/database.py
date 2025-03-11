from langchain_core.messages import HumanMessage, AIMessage
import json
import os
from typing import List, Dict, Optional
from datetime import datetime

class ConversationMemory:
    """简单的会话管理器，生产环境应使用数据库"""
    
    def __init__(self, storage_dir="./data/conversations"):
        self.storage_dir = storage_dir
        # 确保存储目录存在
        os.makedirs(self.storage_dir, exist_ok=True)
        self.conversations = {}
    
    def get_messages(self, conversation_id: str) -> List:
        """获取指定会话的消息记录 返回LangChain消息格式"""
        raw_messages = self.get_conversation(conversation_id)
        messages = []
        
        for msg in raw_messages:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        return messages
    
    def get_conversation(self, conversation_id: str) -> List[Dict]:
        """获取会话历史"""
        # 先从内存中查找
        if conversation_id in self.conversations:
            return self.conversations[conversation_id]
        
        # 从文件中加载
        file_path = os.path.join(self.storage_dir, f"{conversation_id}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                self.conversations[conversation_id] = json.load(f)
            return self.conversations[conversation_id]
        
        # 不存在则创建新会话
        self.conversations[conversation_id] = []
        return []
    
    def add_message(self, conversation_id: str, message: Dict[str, str]) -> None:
        """添加消息到会话"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        # 添加时间戳
        message["timestamp"] = datetime.now().isoformat()
        self.conversations[conversation_id].append(message)
        
        # 保存到文件
        self._save_conversation(conversation_id)
    

    # def add_message(self, conversation_id, role, content):
    #     """添加消息到对话历史
        
    #     Args:
    #         conversation_id: 对话ID
    #         role: 消息角色 ('user' 或 'assistant')
    #         content: 消息内容
    #     """
    #     if conversation_id not in self.conversations:
    #         self.conversations[conversation_id] = []
        
    #     self.conversations[conversation_id].append({
    #         "role": role,
    #         "content": content,
    #         "timestamp": datetime.now().isoformat()
    #     })
    
    def _save_conversation(self, conversation_id: str) -> None:
        """保存会话到文件"""
        file_path = os.path.join(self.storage_dir, f"{conversation_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.conversations[conversation_id], f, ensure_ascii=False, indent=2)