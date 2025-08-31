#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎌 配置管理工具 - 简化版本，不依赖外部包
"""

import os
from typing import Dict, List, Any, Optional
from functools import lru_cache


class Settings:
    """系统配置类 - 简化版本"""

    def __init__(self):
        # 从环境变量加载配置
        self.load_from_env()

    def load_from_env(self):
        """从环境变量和.env文件加载配置"""
        # 尝试加载.env文件
        env_file = ".env"
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()

        # 基础配置
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "8000"))

        # LLM配置
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        self.PRIMARY_LLM = os.getenv("PRIMARY_LLM", "mock")  # mock, openai, anthropic

        # 数据库配置
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./japanese_learning.db")
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

        # 安全配置
        self.SECRET_KEY = os.getenv("SECRET_KEY", "japanese-learning-secret-key")
        origins = os.getenv("ALLOWED_ORIGINS", "*")
        self.ALLOWED_ORIGINS = [o.strip() for o in origins.split(",")]

        # 智能体配置
        self.CORE_AGENTS = {
            "tanaka": {"name": "田中先生", "role": "语法专家", "avatar": "👨‍🏫"},
            "koumi": {"name": "小美", "role": "对话伙伴", "avatar": "👧"},
            "ai": {"name": "アイ", "role": "分析师", "avatar": "🤖"},
            "yamada": {"name": "山田先生", "role": "文化专家", "avatar": "🎌"},
            "sato": {"name": "佐藤教练", "role": "考试专家", "avatar": "🎯"},
            "membot": {"name": "记忆管家", "role": "学习记录", "avatar": "🧠"}
        }

        # 场景配置
        self.SCENES = {
            "grammar": {
                "name": "语法学习",
                "description": "专注于日语语法规则的学习和练习",
                "recommended_agents": ["tanaka", "ai", "membot"]
            },
            "conversation": {
                "name": "日常对话",
                "description": "练习日常生活中的对话技巧",
                "recommended_agents": ["koumi", "yamada", "ai"]
            },
            "restaurant": {
                "name": "餐厅场景",
                "description": "在日式餐厅点餐和用餐的情境对话",
                "recommended_agents": ["koumi", "yamada"]
            },
            "shopping": {
                "name": "购物场景",
                "description": "在商店购物时的日语表达",
                "recommended_agents": ["koumi", "ai"]
            },
            "interview": {
                "name": "面试准备",
                "description": "商务日语和面试技巧训练",
                "recommended_agents": ["sato", "tanaka", "ai"]
            },
            "culture": {
                "name": "文化探索",
                "description": "深入了解日本文化和历史",
                "recommended_agents": ["yamada", "koumi"]
            },
            "jlpt": {
                "name": "JLPT考试",
                "description": "针对JLPT考试的专门训练",
                "recommended_agents": ["sato", "tanaka", "membot"]
            }
        }

    def get_agent_config(self, agent_id: str) -> Dict[str, Any]:
        """获取智能体配置"""
        return self.CORE_AGENTS.get(agent_id, {})

    def get_scene_config(self, scene_id: str) -> Dict[str, Any]:
        """获取场景配置"""
        return self.SCENES.get(scene_id, {})

    def get_recommended_agents_for_scene(self, scene_id: str) -> List[str]:
        """获取场景推荐的智能体"""
        scene_config = self.get_scene_config(scene_id)
        return scene_config.get("recommended_agents", [])


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例"""
    return Settings()


# 全局配置实例
settings = get_settings()


# 配置验证和打印
def print_config_status():
    """打印配置状态"""
    print("🎌 日语学习Multi-Agent系统配置")
    print("=" * 40)
    print(f"调试模式: {settings.DEBUG}")
    print(f"服务地址: {settings.HOST}:{settings.PORT}")
    print(f"主要LLM: {settings.PRIMARY_LLM}")
    print(f"数据库: {settings.DATABASE_URL}")
    print(f"核心智能体: {len(settings.CORE_AGENTS)}")
    print(f"学习场景: {len(settings.SCENES)}")
    print("=" * 40)


if __name__ == "__main__":
    print_config_status()