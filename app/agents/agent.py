from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.messages import SystemMessage
from langchain.prompts import ChatPromptTemplate
from typing import List, Optional, Dict, Any

from app.config import settings
from app.tools import RiskAssessmentTool,ProposalTool
from app.prompts.counseling_prompts import COUNSELOR_SYSTEM_PROMPT, COUNSELOR_CHAT_PROMPT
from app.prompts.proposal_prompts import PROPOSAL_SYSTEM_PROMPT, PROPOSAL_EXAMPLES
from app.llm import get_chat_llm_instance
from app.tools.role_manager import RoleManagerTool, AgentRole
from app.prompts.counseling_prompts import COUNSELOR_SYSTEM_PROMPT
from utils.message_analyzer import MessageAnalyzer, LLMMessageAnalyzer

class CounselorAgent:
    """使用LangChain实现的多角色Agent"""
    
    def __init__(self):
        # 使用工厂方法获取LLM
        self.llm = get_chat_llm_instance(temperature=0.5)
         # 初始化角色管理工具
        self.role_manager = RoleManagerTool()
        # 初始化工具
        self.tools = [
            RiskAssessmentTool(),
            # ResourceFinderTool()
            ProposalTool(),
            self.role_manager
        ]
        
        # 创建系统消息
        self.counselor_system_message = SystemMessage(content=COUNSELOR_SYSTEM_PROMPT)
        self.proposal_system_message = SystemMessage(content=PROPOSAL_SYSTEM_PROMPT)
        
        # 创建Agent
        self._create_agent()

        # self.agent = create_openai_functions_agent(
        #     llm=self.llm,
        #     tools=self.tools,
        #     prompt=COUNSELOR_CHAT_PROMPT
        # )
        
        # 创建Agent执行器
        # self.agent_executor = AgentExecutor(
        #     agent=self.agent,
        #     tools=self.tools,
        #     verbose=True,
        #     handle_parsing_errors=True
        # )
    
    def _create_agent(self):
        """创建Agent，根据当前角色使用适当的系统提示"""
        # 确定当前角色对应的系统消息
        if self.role_manager.is_counselor():
            system_message = self.counselor_system_message
        else:
            system_message = self.proposal_system_message
        
        # 创建提示模板
        prompt = COUNSELOR_CHAT_PROMPT

        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=COUNSELOR_CHAT_PROMPT
        )

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )

    async def generate_response(self, 
                          user_input: str, 
                          chat_history: Optional[List] = None) -> Dict[str, Any]:
        """生成对用户输入的回应"""
        
        if chat_history is None:
            chat_history = []
        
        # 使用Agent处理用户输入
        response = await self.agent_executor.ainvoke(
            {
                "input": user_input,
                "chat_history": chat_history
            }
        )
        
        return {
            "response": response["output"],
            "intermediate_steps": response.get("intermediate_steps", [])
        }
    
    def generate_response_sync(self, 
                         user_input: str, 
                         chat_history: Optional[List] = None) -> Dict[str, Any]:
        """同步版本的响应生成（用于非异步上下文）"""
        
        if chat_history is None:
            chat_history = []
        
        # 使用Agent处理用户输入
        response = self.agent_executor.invoke(
            {
                "input": user_input,
                "chat_history": chat_history
            }
        )
        
        return {
            "response": response["output"],
            "intermediate_steps": response.get("intermediate_steps", [])
        }