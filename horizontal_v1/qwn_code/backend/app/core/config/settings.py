from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """应用配置类"""
    
    # 项目基本信息
    PROJECT_NAME: str = "Work Assistant API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "面向人力资源招聘场景的智能分析系统API"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # CORS配置
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://username:password@localhost:5432/work_assistant"
    DATABASE_ECHO: bool = False
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # RabbitMQ配置
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    
    # MQTT配置
    MQTT_BROKER_URL: str = "mqtt://localhost:1883"
    MQTT_USERNAME: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None
    
    # 认证配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Azure配置
    AZURE_TENANT_ID: Optional[str] = None
    AZURE_CLIENT_ID: Optional[str] = None
    AZURE_CLIENT_SECRET: Optional[str] = None
    AZURE_SHAREPOINT_SITE_ID: Optional[str] = None
    AZURE_GRAPH_DRIVE_ID: Optional[str] = None
    
    # SharePoint配置
    SHAREPOINT_SITE_URL: Optional[str] = None
    SHAREPOINT_FOLDER_PATH: str = "/Shared Documents"
    
    # Azure Blob Storage配置
    AZURE_STORAGE_ACCOUNT_NAME: Optional[str] = None
    AZURE_STORAGE_ACCOUNT_KEY: Optional[str] = None
    AZURE_STORAGE_CONTAINER_NAME_RESUME: str = "resumes"
    
    # OpenAI配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Dify配置
    DIFY_API_KEY: Optional[str] = None
    DIFY_BASE_URL: str = "https://api.dify.ai/v1"
    
    # 第三方分析服务配置
    THIRD_PARTY_ANALYSIS_URL: Optional[str] = None
    THIRD_PARTY_CALLBACK_URL: str = "http://localhost:8000/api/v1/resume/analyze/callback"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # 请求ID头
    REQUEST_ID_HEADER: str = "x-request-id"

    # Docker环境变量（用于兼容Docker Compose）
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    REDIS_PASSWORD: Optional[str] = None
    RABBITMQ_DEFAULT_USER: Optional[str] = None
    RABBITMQ_DEFAULT_PASS: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()


# 确保日志目录存在
log_dir = Path(settings.LOG_FILE).parent
log_dir.mkdir(parents=True, exist_ok=True)