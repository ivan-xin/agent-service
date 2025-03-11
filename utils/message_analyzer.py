from app.llm import get_specialized_llm

class LLMMessageAnalyzer:
    """使用LLM进行高级消息内容分析"""
    
    MESSAGE_ANALYSIS_TEMPLATE = """
    请分析以下用户消息，判断是否与提案/投票相关还是与心理健康咨询相关。
    
    用户消息: "{message}"
    
    首先，判断消息是否包含提案相关内容(如提案、投票、社区决策等)。
    其次，判断消息是否包含心理健康咨询相关内容(如情绪问题、心理困扰等)。
    
    请以JSON格式返回分析结果，包含以下字段:
    1. is_proposal_related: 布尔值，表示是否与提案相关
    2. is_counseling_related: 布尔值，表示是否与心理咨询相关
    3. primary_type: 字符串，"proposal"、"counseling"或"general"
    4. confidence: 0到1之间的数字，表示判断的置信度
    
    只返回JSON对象，不要有其他文字。
    """
    
    @classmethod
    async def analyze_message(cls, message: str) -> dict:
        """
        使用LLM分析消息内容
        
        Args:
            message: 用户消息文本
            
        Returns:
            分析结果字典
        """
        # 快速关键词检查（优化性能）
        basic_analyzer = MessageAnalyzer()
        basic_result = basic_analyzer.analyze_message_type(message)
        
        # 如果基本分析已经很明确，直接返回结果
        if (basic_result["is_proposal_related"] and not basic_result["is_counseling_related"]) or \
           (basic_result["is_counseling_related"] and not basic_result["is_proposal_related"]):
            return basic_result
        
        # 对于不明确的情况，使用LLM进行深入分析
        try:
            # 获取LLM实例
            llm = get_specialized_llm(temperature=0.1)  # 低温度确保一致性
            
            # 创建分析提示
            prompt = cls.MESSAGE_ANALYSIS_TEMPLATE.format(message=message)
            
            # 调用LLM
            response = llm.invoke(prompt)
            
            # 解析JSON结果
            import json
            result = json.loads(response.content)
            
            return result
        except Exception as e:
            # 发生错误时回退到基本分析结果
            print(f"LLM分析失败: {e}")
            return basic_result


class MessageAnalyzer:
    """分析用户消息内容的工具类"""
    
    # 提案相关关键词库
    PROPOSAL_KEYWORDS = [
        # 核心提案词
        "提案", "proposal", "motion", "提议", "提交提案", "建议", "议案",
        # 投票相关
        "投票", "vote", "支持", "反对", "赞成", "反对", "同意", "不同意",
        # 决策相关
        "决议", "决定", "采纳", "接受", "拒绝", "通过", "否决",
        # 治理相关
        "治理", "governance", "社区决策", "community decision", 
        # 提案ID模式
        "提案#", "proposal#", "#"
    ]
    
    # 心理健康关键词库
    COUNSELING_KEYWORDS = [
        "焦虑", "抑郁", "压力", "困扰", "难过", "伤心", "愤怒", "恐惧",
        "心理", "情绪", "感受", "感觉", "therapy", "counseling", "anxiety",
        "depression", "stress", "upset", "sad", "angry", "scared", "emotion",
        "feeling", "mental health", "心理健康", "困难", "挣扎", "痛苦"
    ]
    
    @classmethod
    def is_proposal_related(cls, message: str) -> bool:
        """
        检测消息是否与提案相关
        
        Args:
            message: 用户消息文本
        
        Returns:
            布尔值表示是否与提案相关
        """
        message = message.lower()
        
        # 检查提案关键词
        for keyword in cls.PROPOSAL_KEYWORDS:
            if keyword.lower() in message:
                return True
        
        # 检查提案ID模式 (#加数字字母)
        import re
        if re.search(r'#[a-zA-Z0-9]+', message):
            return True
        
        return False
    
    @classmethod
    def is_counseling_related(cls, message: str) -> bool:
        """
        检测消息是否与心理咨询相关
        
        Args:
            message: 用户消息文本
        
        Returns:
            布尔值表示是否与心理咨询相关
        """
        message = message.lower()
        
        for keyword in cls.COUNSELING_KEYWORDS:
            if keyword.lower() in message:
                return True
                
        return False
    
    @classmethod
    def analyze_message_type(cls, message: str) -> dict:
        """
        综合分析消息类型，返回多个维度的分析结果
        
        Args:
            message: 用户消息文本
        
        Returns:
            包含多个分析维度的字典
        """
        is_proposal = cls.is_proposal_related(message)
        is_counseling = cls.is_counseling_related(message)
        
        # 更倾向的类型 - 如果两者都匹配，优先考虑提案相关
        # 这可以根据业务需求调整优先级
        primary_type = "proposal" if is_proposal else "counseling" if is_counseling else "general"
        
        return {
            "is_proposal_related": is_proposal,
            "is_counseling_related": is_counseling,
            "primary_type": primary_type,
            "has_mixed_content": is_proposal and is_counseling
        }