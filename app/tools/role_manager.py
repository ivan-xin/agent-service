from enum import Enum
from langchain.tools import BaseTool
from typing import Optional, Dict, Any

class AgentRole(Enum):
    """Agent的可能角色"""
    COUNSELOR = "counselor"
    PROPOSAL_EVALUATOR = "proposal_evaluator"

class RoleManagerTool(BaseTool):
    """管理Agent的当前角色"""
    
    name: str = "role_manager"
    description: str = "管理Agent的当前角色，在心理咨询师和提案评估者之间切换。"
    
    # 默认角色为心理咨询师
    current_role: AgentRole = AgentRole.COUNSELOR
    
    def _run(self, action: str, **kwargs: Any) -> Dict[str, Any]:
        """
        改变或查询当前角色
        
        Args:
            action: 'switch' 或 'get'
            role: 要切换到的角色 (当action为'switch'时)
        
        Returns:
            包含当前角色的字典
        """
        if action == "switch":
            role_str = kwargs.get("role", "").lower()
            
            if role_str in ["counselor", "心理咨询师"]:
                self.current_role = AgentRole.COUNSELOR
            elif role_str in ["proposal_evaluator", "提案评估者"]:
                self.current_role = AgentRole.PROPOSAL_EVALUATOR
            else:
                return {"error": f"未知角色: {role_str}", "current_role": self.current_role.value}
        
        return {"current_role": self.current_role.value}
    
    def _arun(self, action: str, **kwargs: Any) -> Dict[str, Any]:
        """异步运行(简单调用同步方法)"""
        return self._run(action, **kwargs)
    
    def is_counselor(self) -> bool:
        """检查当前是否为心理咨询师角色"""
        return self.current_role == AgentRole.COUNSELOR
    
    def is_proposal_evaluator(self) -> bool:
        """检查当前是否为提案评估者角色"""
        return self.current_role == AgentRole.PROPOSAL_EVALUATOR
    
    