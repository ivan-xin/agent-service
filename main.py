import uvicorn
import asyncio
from app.api import app
from app.config import settings

if __name__ == "__main__":
    try:
        # 验证配置
        settings.validate()
        
        # 设置环境变量
        settings.setup_environment()
        
        # 启动服务
        uvicorn.run(
            "app.api:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=settings.DEBUG
        )
    except Exception as e:
        print(f"启动失败: {str(e)}")