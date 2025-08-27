"""田中先生智能体测试"""
import pytest
from unittest.mock import AsyncMock
import asyncio

from src.core.agents.core_agents.tanaka import TanakaAgent
from src.data.models.agent import Agent
from src.data.models.base import AgentPersonality


@pytest.fixture
def tanaka_agent():
    """创建田中先生智能体实例"""
    personality = AgentPersonality(
        strictness=8,
        humor=3,
        patience=6,
        creativity=4,
        formality=9
    )

    config = Agent(
        name="田中先生",
        description="严格的语法老师",
        personality=personality,
        expertise_areas=["grammar", "formal_japanese"],
        system_prompt="You are a strict Japanese grammar teacher."
    )

    return TanakaAgent(config)


@pytest.mark.asyncio
async def test_tanaka_basic_response(tanaka_agent):
    """测试基本响应功能"""
    message = "こんにちは"
    response = await tanaka_agent.process_message(message)

    assert response.agent_id == tanaka_agent.config.id
    assert response.content is not None
    assert len(response.content) > 0
    assert 0.0 <= response.confidence <= 1.0


@pytest.mark.asyncio
async def test_tanaka_grammar_correction(tanaka_agent):
    """测试语法纠错功能"""
    # 使用非日语文本测试
    message = "Hello, how are you?"
    response = await tanaka_agent.process_message(message)

    assert "日本語" in response.content
    assert response.metadata.get("response_type") == "correction"


@pytest.mark.asyncio
async def test_tanaka_praise_response(tanaka_agent):
    """测试表扬响应"""
    message = "今日は良い天気ですね。"
    response = await tanaka_agent.process_message(message)

    # 应该是表扬而不是纠错
    assert response.metadata.get("response_type") == "praise"
    assert response.confidence > 0.7


def test_tanaka_personality_traits(tanaka_agent):
    """测试性格特征访问"""
    assert tanaka_agent.get_personality_trait("strictness") == 8
    assert tanaka_agent.get_personality_trait("patience") == 6
    assert tanaka_agent.get_personality_trait("nonexistent") == 5  # 默认值


def test_tanaka_system_prompt(tanaka_agent):
    """测试系统提示词生成"""
    prompt = tanaka_agent.get_system_prompt()
    assert "田中先生" in prompt
    assert "厳格度: 8/10" in prompt
    assert "忍耐度: 6/10" in prompt