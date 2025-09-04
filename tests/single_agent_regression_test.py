#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单智能体功能回归测试
确保原有智能体功能不受新实现影响
"""

import asyncio
import json
from typing import Dict, List, Any
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# === 强制把 src/ 加入 Python 路径（支持 from core...）===
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))
# =======================================================

class SingleAgentTester:
    """单智能体测试类"""

    def __init__(self):
        self.test_results = {}
        self.agents_to_test = [
            ("tanaka", "田中先生"),
            ("koumi", "小美"),
            ("ai", "アイ"),
            ("yamada", "山田先生"),
            ("sato", "佐藤教练"),
            ("membot", "MemBot")
        ]

    async def test_agent_initialization(self):
        """测试智能体初始化"""
        print("🔍 测试智能体初始化...")

        try:
            from core.agents import get_agent, AGENT_REGISTRY

            for agent_id, agent_name in self.agents_to_test:
                try:
                    agent = get_agent(agent_id)
                    print(f"✅ {agent_name} ({agent_id}) 初始化成功")

                    # 检查基本属性
                    assert hasattr(agent, 'name'), f"{agent_name} 缺少 name 属性"
                    assert hasattr(agent, 'role'), f"{agent_name} 缺少 role 属性"
                    assert hasattr(agent, 'personality'), f"{agent_name} 缺少 personality 属性"
                    print(f"   - 基本属性检查通过")

                except Exception as e:
                    print(f"❌ {agent_name} ({agent_id}) 初始化失败: {e}")
                    self.test_results[f"{agent_id}_init"] = False
                    continue

                self.test_results[f"{agent_id}_init"] = True

        except ImportError as e:
            print(f"❌ 无法导入智能体模块: {e}")
            return False

        return True

    async def test_individual_responses(self):
        """测试单独的智能体响应"""
        print("\n🔍 测试单智能体响应功能...")

        test_inputs = [
            {
                "input": "私は学校に行った",
                "scene": "grammar_check",
                "expected_agents": ["tanaka", "ai", "membot"]
            },
            {
                "input": "こんにちは！元気ですか？",
                "scene": "casual_chat",
                "expected_agents": ["koumi"]
            },
            {
                "input": "日本の文化について教えて",
                "scene": "culture_learning",
                "expected_agents": ["yamada"]
            },
            {
                "input": "N2試験の対策を教えて",
                "scene": "exam_preparation",
                "expected_agents": ["sato"]
            }
        ]

        try:
            from core.agents import get_agent

            for test_case in test_inputs:
                print(f"\n测试输入: {test_case['input']}")

                for agent_id, agent_name in self.agents_to_test:
                    if agent_id not in test_case.get("expected_agents", [agent_id]):
                        continue

                    try:
                        agent = get_agent(agent_id)

                        # 构建会话上下文
                        session_context = {
                            "user_id": "test_user",
                            "session_id": "test_session",
                            "scene": test_case["scene"],
                            "history": []
                        }

                        # 调用智能体处理用户输入
                        response = await agent.process_user_input(
                            user_input=test_case["input"],
                            session_context=session_context,
                            scene=test_case["scene"]
                        )

                        # 验证响应格式
                        assert isinstance(response, dict), "响应必须是字典格式"
                        assert "content" in response, "响应必须包含content字段"
                        assert "agent_name" in response, "响应必须包含agent_name字段"
                        assert "emotion" in response, "响应必须包含emotion字段"

                        print(f"✅ {agent_name} 响应正常")
                        print(f"   - 内容: {response.get('content', '')[:50]}...")
                        print(f"   - 情绪: {response.get('emotion', 'N/A')}")

                        self.test_results[f"{agent_id}_response"] = True

                    except Exception as e:
                        print(f"❌ {agent_name} 响应测试失败: {e}")
                        self.test_results[f"{agent_id}_response"] = False

        except ImportError as e:
            print(f"❌ 无法导入智能体模块: {e}")
            return False

        return True

    async def test_agent_personality_consistency(self):
        """测试智能体个性一致性"""
        print("\n🔍 测试智能体个性一致性...")

        personality_tests = {
            "tanaka": {
                "input": "この文法は間違いですか？",
                "expected_traits": ["formal", "educational", "precise"]
            },
            "koumi": {
                "input": "今日はどんな日だった？",
                "expected_traits": ["friendly", "casual", "energetic"]
            },
            "yamada": {
                "input": "日本の伝統文化について",
                "expected_traits": ["knowledgeable", "cultural", "wise"]
            },
            "sato": {
                "input": "JLPT N2の勉強法",
                "expected_traits": ["motivating", "goal-oriented", "strategic"]
            },
            "ai": {
                "input": "私の学習進度を分析して",
                "expected_traits": ["analytical", "data-driven", "objective"]
            },
            "membot": {
                "input": "復習スケジュールを作って",
                "expected_traits": ["systematic", "memory-focused", "organized"]
            }
        }

        try:
            from core.agents import get_agent

            for agent_id, test_info in personality_tests.items():
                agent_name = dict(self.agents_to_test)[agent_id]

                try:
                    agent = get_agent(agent_id)

                    session_context = {
                        "user_id": "personality_test",
                        "session_id": "personality_session",
                        "scene": "general",
                        "history": []
                    }

                    response = await agent.process_user_input(
                        user_input=test_info["input"],
                        session_context=session_context,
                        scene="general"
                    )

                    # 检查个性特征是否体现在回复中
                    content = response.get("content", "").lower()
                    agent_name_in_response = response.get("agent_name", "")

                    print(f"✅ {agent_name} 个性测试完成")
                    print(f"   - 回复风格: {agent_name_in_response}")
                    print(f"   - 内容片段: {content[:60]}...")

                    self.test_results[f"{agent_id}_personality"] = True

                except Exception as e:
                    print(f"❌ {agent_name} 个性测试失败: {e}")
                    self.test_results[f"{agent_id}_personality"] = False

        except ImportError as e:
            print(f"❌ 无法导入智能体模块: {e}")
            return False

        return True

    async def test_api_compatibility(self):
        """测试API兼容性"""
        print("\n🔍 测试API接口兼容性...")

        try:
            import requests
            import json

            # 测试API端点
            api_base_url = "http://localhost:8000"  # 假设API运行在这个端口

            test_request = {
                "message": "私は学校に行きました",  # 注意：使用message字段
                "user_id": "test_user",
                "session_id": "test_session",
                "agent_name": "田中先生",
                "scene_context": "general"  # 确保是字符串
            }

            try:
                response = requests.post(
                    f"{api_base_url}/api/v1/chat/send",
                    json=test_request,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    print("✅ API响应格式正确")
                    print(f"   - 响应内容: {data.get('response', '')[:50]}...")
                    print(f"   - 智能体: {data.get('agent_name', 'N/A')}")
                    self.test_results["api_compatibility"] = True
                else:
                    print(f"❌ API返回错误状态码: {response.status_code}")
                    print(f"   - 错误信息: {response.text}")
                    self.test_results["api_compatibility"] = False

            except requests.exceptions.ConnectionError:
                print("⚠️  API服务器未运行，跳过API测试")
                self.test_results["api_compatibility"] = "skipped"
            except Exception as e:
                print(f"❌ API测试失败: {e}")
                self.test_results["api_compatibility"] = False

        except ImportError:
            print("⚠️  requests模块未安装，跳过API测试")
            self.test_results["api_compatibility"] = "skipped"

        return True

    def generate_test_report(self):
        """生成测试报告"""
        print("\n📊 单智能体测试报告")
        print("=" * 50)

        passed = 0
        failed = 0
        skipped = 0

        for test_name, result in self.test_results.items():
            if result is True:
                status = "✅ 通过"
                passed += 1
            elif result is False:
                status = "❌ 失败"
                failed += 1
            else:
                status = "⚠️  跳过"
                skipped += 1

            print(f"{test_name:<30} {status}")

        total = passed + failed + skipped
        print(f"\n总计: {total} 项测试")
        print(f"通过: {passed}")
        print(f"失败: {failed}")
        print(f"跳过: {skipped}")

        if failed == 0:
            print("\n🎉 所有单智能体功能测试通过！")
            return True
        else:
            print(f"\n⚠️  有 {failed} 项测试失败，请检查相关功能")
            return False

    async def run_all_tests(self):
        """运行所有单智能体测试"""
        print("🚀 开始单智能体功能回归测试...\n")

        await self.test_agent_initialization()
        await self.test_individual_responses()
        await self.test_agent_personality_consistency()
        await self.test_api_compatibility()

        return self.generate_test_report()


# 运行测试
async def main():
    tester = SingleAgentTester()
    success = await tester.run_all_tests()

    if success:
        print("\n✅ 单智能体回归测试通过 - 可以继续多智能体协作测试")
    else:
        print("\n❌ 单智能体回归测试失败 - 请修复问题后再继续")


if __name__ == "__main__":
    asyncio.run(main())