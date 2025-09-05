# simple_collaboration_test.py
"""
简化的协作测试 - 使用你现有的工作代码
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))


async def test_existing_agents():
    """测试现有智能体是否可用"""
    print("测试现有智能体...")

    try:
        # 导入你的智能体
        from src.core.agents.core_agents.tanaka_sensei import TanakaSensei
        from src.core.agents.core_agents.koumi import KoumiAgent
        from src.core.agents.core_agents.ai_analyzer import AIAnalyzer

        # 创建智能体实例
        tanaka = TanakaSensei()
        koumi = KoumiAgent()
        ai = AIAnalyzer()

        print(f"田中先生: {tanaka.name}")
        print(f"小美: {koumi.name}")
        print(f"アイ: {ai.name}")

        # 测试简单响应
        test_input = "你好"
        session_context = {"session_id": "test", "user_id": "test_user"}

        tanaka_response = await tanaka.process_user_input(test_input, session_context)
        print(f"田中先生响应: {tanaka_response.get('content', 'No content')[:50]}...")

        return True

    except Exception as e:
        print(f"测试失败: {e}")
        return False


async def test_grammar_workflows():
    """测试语法工作流"""
    print("测试语法工作流...")

    try:
        from src.core.workflows.grammar_workflows import GrammarCollaborationWorkflows

        workflow = GrammarCollaborationWorkflows()

        # 测试你刚添加的方法
        result = await workflow.grammar_correction_workflow(
            "私は学校に行きました",
            {"session_id": "test"}
        )

        print(f"语法纠错结果: {result.get('success', False)}")
        if 'consensus' in result:
            print("包含consensus字段")

        return result.get('success', False)

    except Exception as e:
        print(f"语法工作流测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("=== 简化协作测试 ===")

    # 测试1: 基础智能体
    agents_ok = await test_existing_agents()

    # 测试2: 工作流
    workflows_ok = await test_grammar_workflows()

    if agents_ok and workflows_ok:
        print("基础协作功能正常")
        return True
    else:
        print("需要进一步修复")
        return False


if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)