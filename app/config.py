"""
应用配置文件
"""
from pydantic_settings import BaseSettings
import os
from typing import Dict, Any

class Settings(BaseSettings):
    """环境变量配置"""
    # 万邦接口配置 - 生产环境使用
    WANBANG_APP_KEY: str
    WANBANG_APP_SECRET: str
    # 千问模型配置
    QIANWEN_API_KEY: str
    QIANWEN_API_BASE: str
    
    class Config:
        env_file = ".env"

settings = Settings()

# 运行模式
RUN_MODE = os.getenv("RUN_MODE", "mock")  # mock 或 prod

# API 配置
API_CONFIG = {
    "mock": {
        "api_module": "app.core.mock_data",
        "api_class": "MockTaobaoApi"
    },
    "prod": {
        "api_module": "app.core.taobao_api",
        "api_class": "TaobaoApi"
    }
}

# LLM 配置
LLM_CONFIG = {
    "model_name": "qwen-turbo",  # 使用千问模型
    "temperature": 0.7,
    "max_tokens": 1000,
    "api_key": settings.QIANWEN_API_KEY,
    "api_base": settings.QIANWEN_API_BASE
}

# WebSocket 配置
WS_CONFIG = {
    "ping_interval": 20,  # 心跳间隔（秒）
    "ping_timeout": 20    # 心跳超时（秒）
}

# SSE 配置
SSE_CONFIG = {
    "retry": 1000,  # 重试间隔（毫秒）
    "ping": 30000   # 心跳间隔（毫秒）
}

# 缓存配置
CACHE_CONFIG = {
    "ttl": 3600,  # 缓存时间（秒）
    "max_size": 1000  # 最大缓存条目数
}

# 日志配置
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "app.log"
} 