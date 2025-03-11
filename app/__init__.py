"""
心理咨询Agent服务应用包

此包包含使用LangChain构建的心理咨询Agent所需的所有组件。
"""

__version__ = "0.1.0"

# 导出主要组件
from app.config import settings


"""
提示模板模块

包含所有用于Agent的提示模板。
"""

from app.prompts.counseling_prompts import COUNSELOR_SYSTEM_PROMPT, COUNSELOR_CHAT_PROMPT, RISK_ASSESSMENT_PROMPT

__all__ = ["COUNSELOR_SYSTEM_PROMPT", "COUNSELOR_CHAT_PROMPT", "RISK_ASSESSMENT_PROMPT"]