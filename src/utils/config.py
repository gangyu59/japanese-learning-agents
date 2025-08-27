"""应用程序配置管理"""
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import os


@dataclass  
class Settings:
    """应用程序设置"""
    app_name: str = "Japanese Learning Multi-Agent System"
    debug: bool = False
    version: str = "0.1.0"
    database_url: str = "sqlite:///./japanese_learning.db"
    openai_api_key: Optional[str] = None
    model_name: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7
    data_dir: Path = Path("./data")
    logs_dir: Path = Path("./logs")

    def __post_init__(self):
        """初始化后处理"""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.debug = os.getenv('DEBUG', 'False').lower() == 'true'
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)


settings = Settings()
