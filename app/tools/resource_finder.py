from langchain.tools import BaseTool
import json
import os
from typing import Dict, List, Optional  # 添加导入

class ResourceFinderTool(BaseTool):
    name: str = "resource_finder"  # 添加类型注解
    description: str = "查找适合用户的心理健康资源"  # 添加类型注解
    
    def __init__(self, resource_path="data/resources/mental_health_resources.json"):
        super().__init__()
        self.resource_path = resource_path
        self.resources = self._load_resources()
    
    def _load_resources(self):
        """加载资源数据"""
        try:
            if not os.path.exists(self.resource_path):
                # 创建示例资源
                self._create_sample_resources()
            
            with open(self.resource_path, 'r', encoding='utf-8') as f:
                resources = json.load(f)
            return resources
        except Exception as e:
            print(f"加载资源失败: {str(e)}")
            return {
                "crisis_lines": [],
                "self_help": [],
                "professional_services": [],
                "apps": []
            }
    
    def _create_sample_resources(self):
        """创建示例资源数据"""
        sample_resources = {
            "crisis_lines": [
                {
                    "name": "全国心理健康危机热线",
                    "phone": "400-161-9995",
                    "description": "24/7心理健康支持热线"
                }
            ],
            "self_help": [
                {
                    "name": "正念冥想指南",
                    "type": "article",
                    "description": "介绍正念冥想的基础技巧和练习"
                },
                {
                    "name": "克服抑郁自助手册",
                    "type": "book",
                    "description": "基于CBT的抑郁自助指南"
                }
            ],
            "professional_services": [
                {
                    "name": "心理咨询师在线平台",
                    "type": "online",
                    "description": "连接专业心理咨询师的在线平台"
                }
            ],
            "apps": [
                {
                    "name": "正念冥想App",
                    "platform": "iOS/Android",
                    "description": "引导式冥想和呼吸练习应用"
                },
                {
                    "name": "情绪追踪器",
                    "platform": "iOS/Android",
                    "description": "记录和分析情绪变化的应用"
                }
            ]
        }
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self.resource_path), exist_ok=True)
        
        with open(self.resource_path, 'w', encoding='utf-8') as f:
            json.dump(sample_resources, f, ensure_ascii=False, indent=2)
    
    def _run(self, query: str) -> str:
        """根据查询找到相关资源"""
        # 简单的关键词匹配示例
        keywords = query.lower().split()
        matched_resources = {}
        
        for category, items in self.resources.items():
            matched = []
            for item in items:
                description = item.get("description", "").lower()
                name = item.get("name", "").lower()
                
                if any(keyword in description or keyword in name for keyword in keywords):
                    matched.append(item)
            
            if matched:
                matched_resources[category] = matched
        
        if not matched_resources:
            return "未找到与查询匹配的资源。请尝试提供更多信息或使用不同的关键词。"
        
        # 格式化结果
        result = "以下是可能有帮助的资源:\n\n"
        
        for category, items in matched_resources.items():
            category_name = {
                "crisis_lines": "危机热线",
                "self_help": "自助资源",
                "professional_services": "专业服务",
                "apps": "应用程序"
            }.get(category, category)
            
            result += f"## {category_name}\n"
            
            for item in items:
                result += f"- {item['name']}\n"
                result += f"  {item.get('description', '')}\n"
                if 'phone' in item:
                    result += f"  电话: {item['phone']}\n"
            
            result += "\n"
        
        return result
    
    def _arun(self, query: str) -> str:
        """异步执行，调用同步方法"""
        return self._run(query)