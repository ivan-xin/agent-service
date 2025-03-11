from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import asyncio

from app.agents.agent import CounselorAgent
from app.database import ConversationMemory
from app.config import settings
import logging
import traceback

# 初始化FastAPI应用
app = FastAPI(title="心理咨询Agent API")

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中设置为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化组件
counselor_agent = CounselorAgent()
memory = ConversationMemory()

# 数据模型
class Message(BaseModel):
    role: str  # 'user' 或 'assistant'
    content: str
    timestamp: Optional[str] = None

class ConversationRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ConversationResponse(BaseModel):
    conversation_id: str
    response: str
    messages: List[Message]
    details: Optional[Dict[str, Any]] = None

# API端点
@app.post("/api/chat", response_model=ConversationResponse)
async def chat(request: ConversationRequest):
    try:
        # 获取或创建会话ID
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # 记录请求信息
        logger.info(f"Received chat request for conversation_id: {conversation_id}")
        
        # 获取历史对话（LangChain消息格式）
        chat_history = memory.get_messages(conversation_id)
        
        # 添加用户消息到历史 - 修改这里的调用
        # 查看ConversationMemory.add_message方法的签名，调整参数
        # 可能的选项1: 如果方法只需要会话ID和完整消息对象
        memory.add_message(
            conversation_id, 
            {"role": "user", "content": request.message}
        )
        
        # 或者选项2: 如果方法接收会话ID和消息内容
        # memory.add_message(conversation_id, request.message)
        
        # 获取Agent响应
        logger.info("Calling LLM for response...")
        result = await counselor_agent.generate_response(
            request.message,
            chat_history
        )
        
        # 添加Agent响应到历史 - 同样修改这里
        # 与上面使用相同的格式
        memory.add_message(
            conversation_id, 
            {"role": "assistant", "content": result["response"]}
        )
        # 或者
        # memory.add_message(conversation_id, result["response"])
        
        # 获取原始对话历史
        messages = memory.get_conversation(conversation_id)
        
        return {
            "conversation_id": conversation_id,
            "response": result["response"],
            "messages": messages,
            "details": {"steps": result.get("intermediate_steps", [])}
        }
    
    except Exception as e:
        # 详细记录错误信息
        logger.error(f"Error processing chat request: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/conversations/{conversation_id}", response_model=List[Message])
async def get_conversation(conversation_id: str):
    try:
        conversation = memory.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}