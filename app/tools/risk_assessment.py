from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import json
from typing import Optional, Type, List  # 添加导入

from app.config import settings
from app.prompts.counseling_prompts import RISK_ASSESSMENT_PROMPT

class RiskAssessmentTool(BaseTool):
    name: str = "risk_assessment"  # 添加类型注解
    description: str = "评估用户消息中是否存在心理健康风险信号"  # 添加类型注解
    
    def _run(self, message: str) -> str:
        """执行风险评估"""
        
        # 创建评估提示
        prompt = PromptTemplate(
            template=RISK_ASSESSMENT_PROMPT,
            input_variables=["message"]
        )
        
        # 使用LLM进行评估
        llm = ChatOpenAI(
            temperature=0.0,
            model_name=settings.OPENAI_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # 获取评估结果
        risk_prompt = prompt.format(message=message)
        risk_result = llm.invoke(risk_prompt)
        
        try:
            # 尝试解析JSON结果
            risk_data = json.loads(risk_result.content)
            
            # 检查高风险情况
            high_risks = []
            for category, level in risk_data.items():
                if level.lower() in ["高风险", "high risk", "high"]:
                    high_risks.append(category)
            
            if high_risks:
                return f"""检测到高风险信号：{', '.join(high_risks)}。
                建议提供危机支持资源，并鼓励用户寻求专业帮助。"""
            
            return "未检测到高风险信号。继续提供支持性对话。"
            
        except (json.JSONDecodeError, AttributeError):
            # 如果无法解析JSON，返回原始结果
            return f"风险评估结果: {risk_result.content}"
    
    def _arun(self, message: str) -> str:
        """异步执行，调用同步方法"""
        return self._run(message)