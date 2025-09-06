
# config_loader.py
"""
确保智能体正确加载环境变量配置
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

class ConfigLoader:
    """配置加载器 - 确保环境变量正确加载"""

    def __init__(self):
        self.config = {}
        self._load_env_file()
        self._validate_config()

    def _load_env_file(self):
        """加载.env文件"""
        # 尝试多个可能的.env文件位置
        possible_paths = [
            Path.cwd() / ".env",
            Path.cwd().parent / ".env", 
            Path(__file__).parent / ".env",
            Path(__file__).parent.parent / ".env"
        ]

        for env_path in possible_paths:
            if env_path.exists():
                load_dotenv(env_path, override=True)
                print(f"✅ 已加载环境变量: {env_path}")
                break
        else:
            print("⚠️  未找到.env文件，使用系统环境变量")

    def _validate_config(self):
        """验证配置完整性"""
        self.config = {
            "llm_provider": os.getenv("LLM_PROVIDER", "deepseek"),
            "deepseek_api_key": os.getenv("DEEPSEEK_API_KEY"),
            "deepseek_api_base": os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
            "deepseek_model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            "ark_api_key": os.getenv("ARK_API_KEY"),
            "ark_api_base": os.getenv("ARK_API_BASE", "https://ark.cn-beijing.volces.com/api/v3"),
            "ark_model": os.getenv("ARK_MODEL", "ep-20250313161944-69jw8"),
            "database_url": os.getenv("DATABASE_URL", "sqlite:///./japanese_learning.db"),
            "debug": os.getenv("DEBUG", "false").lower() == "true"
        }

        # 检查必要的配置
        provider = self.config["llm_provider"]
        if provider == "deepseek" and not self.config["deepseek_api_key"]:
            raise ValueError("DeepSeek API密钥未配置")
        elif provider == "ark" and not self.config["ark_api_key"]:
            raise ValueError("ARK API密钥未配置")

    def get_llm_config(self) -> Dict[str, Any]:
        """获取LLM配置"""
        provider = self.config["llm_provider"]

        if provider == "deepseek":
            return {
                "provider": "deepseek",
                "api_key": self.config["deepseek_api_key"],
                "api_base": self.config["deepseek_api_base"], 
                "model": self.config["deepseek_model"],
                "timeout": 30
            }
        elif provider == "ark":
            return {
                "provider": "ark",
                "api_key": self.config["ark_api_key"],
                "api_base": self.config["ark_api_base"],
                "model": self.config["ark_model"], 
                "timeout": 30
            }
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}")

    def get_database_config(self) -> str:
        """获取数据库配置"""
        return self.config["database_url"]

    def is_debug_mode(self) -> bool:
        """是否调试模式"""
        return self.config["debug"]

# 全局配置实例
try:
    config_loader = ConfigLoader()
    print("✅ 配置加载器初始化成功")
except Exception as e:
    print(f"❌ 配置加载器初始化失败: {e}")
    config_loader = None
