#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多智能体协作功能测试
测试智能体协作语法纠错、分歧展示和协作创作功能
"""

import asyncio
import json
from typing import Dict, List, Any
import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class CollaborationTester:
    """多智能体协作测试类"""

    def __init__(self):
        self.test_results = {}
        self.collaboration_scenarios = []

    async def test_grammar_correction_workflow(self):
        """测试协作语法纠错流程"""
        print("🔍 测试协作语法纠错流程...")

        test_cases = [
            {
                "input": "私は昨日学校に行きました。でも、友達は来ませんでした。",
                "expected_agents": ["tanaka", "koumi", "ai", "membot"],
                "expected_corrections": ["grammar", "style", "context"]
            },
            {
                "input": "今日はとても暑い日ですね。あなたはどう思いますか？",
                "expected_agents": ["tanaka", "koumi"],
                "expected_corrections": ["politeness", "natural_expression"]
            },
            {
                "input": "私の日本語が上手になりたいです。",  # 明显的语法错误
                "expected_agents": ["tanaka", "ai", "membot"],
                "expected_corrections": ["verb_form", "expression"]
            }
        ]

        try:
            # 这里应该调用你的协作工作流
            # 假设存在一个CollaborationWorkflow类
            from core.workflows import CollaborationWorkflow  # 根据实际路径调整

            workflow = CollaborationWorkflow()

            for i, test_case in enumerate(test_cases):
                print(f"\n测试用例 {i + 1}: {test_case['input']}")

                try:
                    # 调用协作语法纠错流程
                    result = await workflow.grammar_correction_workflow(
                        user_input=test_case["input"]
                    )

                    # 验证协作结果
                    assert isinstance(result, dict), "协作结果必须是字典格式"
                    assert "corrections" in result, "结果必须包含corrections字段"
                    assert "participating_agents" in result, "结果必须包含participating_agents字段"
                    assert "consensus" in result, "结果必须包含consensus字段"

                    participating_agents = result["participating_agents"]
                    corrections = result["corrections"]

                    print(f"✅ 协作完成，参与智能体: {', '.join(participating_agents)}")
                    print(f"   - 纠错内容: {len(corrections)} 项")

                    # 检查是否有预期的智能体参与
                    expected_agents = set(test_case["expected_agents"])
                    actual_agents = set(participating_agents)

                    if expected_agents.intersection(actual_agents):
                        print("   - ✅ 预期智能体参与正常")
                    else:
                        print(f"   - ⚠️  预期智能体 {expected_agents} 但实际参与 {actual_agents}")

                    self.test_results[f"grammar_correction_{i}"] = True

                except Exception as e:
                    print(f"❌ 协作语法纠错测试失败: {e}")
                    self.test_results[f"grammar_correction_{i}"] = False

        except ImportError as e:
            print(f"⚠️  协作工作流模块未找到，使用模拟测试: {e}")
            # 模拟协作测试
            await self._simulate_grammar_correction_test(test_cases)

        return True

    async def _simulate_grammar_correction_test(self, test_cases):
        """模拟协作语法纠错测试（当真实模块不可用时）"""
        print("📍 使用模拟协作测试...")

        try:
            from core.agents import get_agent

            for i, test_case in enumerate(test_cases):
                print(f"\n模拟测试用例 {i + 1}: {test_case['input']}")

                corrections = []
                participating_agents = []

                # 模拟多个智能体的协作过程
                for agent_id in test_case["expected_agents"]:
                    try:
                        agent = get_agent(agent_id)
                        agent_name = dict([("tanaka", "田中先生"), ("koumi", "小美"),
                                           ("ai", "アイ"), ("membot", "MemBot")])[agent_id]

                        session_context = {
                            "user_id": "collaboration_test",
                            "session_id": f"collab_session_{i}",
                            "scene": "grammar_check",
                            "history": []
                        }

                        response = await agent.process_user_input(
                            user_input=test_case["input"],
                            session_context=session_context,
                            scene="grammar_check"
                        )

                        participating_agents.append(agent_id)
                        corrections.append({
                            "agent": agent_name,
                            "correction": response.get("content", ""),
                            "learning_points": response.get("learning_points", [])
                        })

                        print(f"   - {agent_name}: 已参与协作")

                    except Exception as e:
                        print(f"   - ❌ {agent_id} 协作失败: {e}")

                if len(participating_agents) >= 2:
                    print(f"✅ 模拟协作成功: {len(participating_agents)} 个智能体参与")
                    self.test_results[f"grammar_correction_sim_{i}"] = True
                else:
                    print(f"❌ 模拟协作失败: 只有 {len(participating_agents)} 个智能体参与")
                    self.test_results[f"grammar_correction_sim_{i}"] = False

        except Exception as e:
            print(f"❌ 模拟协作测试失败: {e}")

    async def test_agent_disagreement_resolution(self):
        """测试智能体分歧处理"""
        print("\n🔍 测试智能体分歧处理机制...")

        # 设计会产生分歧的测试用例
        disagreement_cases = [
            {
                "input": "友達と映画を見に行くつもりだ",  # つもり vs つもりです的敬语分歧
                "expected_disagreement": "politeness_level",
                "agents": ["tanaka", "koumi"]  # 田中先生(正式) vs 小美(随意)
            },
            {
                "input": "この本はとても面白いと思います",  # と思います的自然度
                "expected_disagreement": "naturalness",
                "agents": ["koumi", "yamada"]  # 年轻用语 vs 传统用语
            }
        ]

        for i, case in enumerate(disagreement_cases):
            print(f"\n分歧测试 {i + 1}: {case['input']}")

            try:
                # 这里应该调用分歧处理机制
                # 假设存在DisagreementResolver类
                try:
                    from core.collaboration import DisagreementResolver
                    resolver = DisagreementResolver()

                    result = await resolver.handle_disagreement(
                        user_input=case["input"],
                        involved_agents=case["agents"]
                    )

                    assert "disagreements" in result, "结果必须包含disagreements字段"
                    assert "resolution_options" in result, "结果必须包含resolution_options字段"
                    assert "user_arbitration_needed" in result, "结果必须包含user_arbitration_needed字段"

                    print("✅ 分歧检测和处理机制正常")
                    print(f"   - 检测到分歧: {len(result['disagreements'])} 个")
                    print(f"   - 需要用户仲裁: {result['user_arbitration_needed']}")

                    self.test_results[f"disagreement_resolution_{i}"] = True

                except ImportError:
                    # 模拟分歧处理测试
                    await self._simulate_disagreement_test(case, i)

            except Exception as e:
                print(f"❌ 分歧处理测试失败: {e}")
                self.test_results[f"disagreement_resolution_{i}"] = False

    async def _simulate_disagreement_test(self, case, case_index):
        """模拟分歧处理测试"""
        print("📍 使用模拟分歧处理测试...")

        try:
            from core.agents import get_agent

            responses = {}

            # 获取多个智能体的不同观点
            for agent_id in case["agents"]:
                agent = get_agent(agent_id)

                session_context = {
                    "user_id": "disagreement_test",
                    "session_id": f"disagree_session_{case_index}",
                    "scene": "grammar_analysis",
                    "history": []
                }

                response = await agent.process_user_input(
                    user_input=case["input"],
                    session_context=session_context,
                    scene="grammar_analysis"
                )

                responses[agent_id] = response

            # 分析是否存在不同观点
            different_suggestions = len(set(resp.get("content", "")[:50] for resp in responses.values()))

            if different_suggestions > 1:
                print("✅ 检测到智能体间的不同观点")
                print(f"   - 不同建议数量: {different_suggestions}")
                self.test_results[f"disagreement_sim_{case_index}"] = True
            else:
                print("⚠️  未检测到明显分歧，可能需要调整测试用例")
                self.test_results[f"disagreement_sim_{case_index}"] = False

        except Exception as e:
            print(f"❌ 模拟分歧处理测试失败: {e}")
            self.test_results[f"disagreement_sim_{case_index}"] = False

    async def test_collaborative_creation(self):
        """测试协作创作功能"""
        print("\n🔍 测试协作创作功能...")

        creation_scenarios = [
            {
                "theme": "春天的校园故事",
                "expected_elements": ["setting", "characters", "plot"],
                "participating_agents": ["koumi", "yamada", "ai"]
            },
            {
                "theme": "日本传统节日体验",
                "expected_elements": ["cultural_context", "characters", "description"],
                "participating_agents": ["yamada", "koumi", "tanaka"]
            }
        ]

        for i, scenario in enumerate(creation_scenarios):
            print(f"\n协作创作测试 {i + 1}: {scenario['theme']}")

            try:
                # 尝试调用协作创作功能
                try:
                    from core.workflows import CollaborationWorkflow
                    workflow = CollaborationWorkflow()

                    result = await workflow.novel_creation_workflow(
                        theme=scenario["theme"]
                    )

                    assert "story_content" in result, "结果必须包含story_content字段"
                    assert "participating_agents" in result, "结果必须包含participating_agents字段"
                    assert "creation_process" in result, "结果必须包含creation_process字段"

                    print("✅ 协作创作完成")
                    print(f"   - 参与智能体: {', '.join(result['participating_agents'])}")
                    print(f"   - 故事长度: {len(result['story_content'])} 字符")

                    self.test_results[f"collaborative_creation_{i}"] = True

                except ImportError:
                    # 模拟协作创作测试
                    await self._simulate_creation_test(scenario, i)

            except Exception as e:
                print(f"❌ 协作创作测试失败: {e}")
                self.test_results[f"collaborative_creation_{i}"] = False

    async def _simulate_creation_test(self, scenario, scenario_index):
        """模拟协作创作测试"""
        print("📍 使用模拟协作创作测试...")

        try:
            from core.agents import get_agent

            story_parts = []
            participating_agents = []

            for agent_id in scenario["participating_agents"]:
                try:
                    agent = get_agent(agent_id)
                    agent_name = {"koumi": "小美", "yamada": "山田先生", "ai": "アイ", "tanaka": "田中先生"}[agent_id]

                    # 构建创作提示
                    creation_prompt = f"请为主题'{scenario['theme']}'创作一小段故事"
                    if story_parts:
                        creation_prompt += f"，延续以下内容：{story_parts[-1][:100]}..."

                    session_context = {
                        "user_id": "creation_test",
                        "session_id": f"creation_session_{scenario_index}",
                        "scene": "creative_writing",
                        "history": []
                    }

                    response = await agent.process_user_input(
                        user_input=creation_prompt,
                        session_context=session_context,
                        scene="creative_writing"
                    )

                    if response.get("content"):
                        story_parts.append(response["content"])
                        participating_agents.append(agent_name)
                        print(f"   - {agent_name}: 已贡献故事片段")

                except Exception as e:
                    print(f"   - ❌ {agent_id} 创作失败: {e}")

            if len(story_parts) >= 2:
                total_length = sum(len(part) for part in story_parts)
                print(f"✅ 模拟协作创作成功")
                print(f"   - 故事片段数: {len(story_parts)}")
                print(f"   - 总长度: {total_length} 字符")
                self.test_results[f"collaborative_creation_sim_{scenario_index}"] = True
            else:
                print(f"❌ 模拟协作创作失败: 只生成了 {len(story_parts)} 个故事片段")
                self.test_results[f"collaborative_creation_sim_{scenario_index}"] = False

        except Exception as e:
            print(f"❌ 模拟协作创作测试失败: {e}")
            self.test_results[f"collaborative_creation_sim_{scenario_index}"] = False

    async def test_multi_agent_conversation_flow(self):
        """测试多智能体对话流程"""
        print("\n🔍 测试多智能体对话流程...")

        conversation_test = {
            "initial_message": "私は日本語を勉強していますが、敬語がよく分かりません。",
            "expected_flow": [
                {"agent": "tanaka", "focus": "grammar_explanation"},
                {"agent": "koumi", "focus": "practical_examples"},
                {"agent": "yamada", "focus": "cultural_context"},
                {"agent": "ai", "focus": "learning_analysis"}
            ]
        }

        try:
            # 模拟多智能体对话流程
            from core.agents import get_agent

            conversation_history = []
            current_context = conversation_test["initial_message"]

            for step in conversation_test["expected_flow"]:
                agent_id = step["agent"]
                agent = get_agent(agent_id)
                agent_name = {"tanaka": "田中先生", "koumi": "小美", "yamada": "山田先生", "ai": "アイ"}[agent_id]

                session_context = {
                    "user_id": "conversation_test",
                    "session_id": "multi_agent_conversation",
                    "scene": "learning_discussion",
                    "history": conversation_history
                }

                response = await agent.process_user_input(
                    user_input=current_context,
                    session_context=session_context,
                    scene="learning_discussion"
                )

                if response.get("content"):
                    conversation_history.append({
                        "agent": agent_name,
                        "content": response["content"],
                        "focus": step["focus"]
                    })

                    print(f"   - {agent_name}: 已参与对话 (关注点: {step['focus']})")

                    # 更新上下文为包含之前的对话
                    current_context += f"\n{agent_name}的观点：{response['content'][:100]}..."

            if len(conversation_history) >= 3:
                print("✅ 多智能体对话流程测试成功")
                print(f"   - 对话轮次: {len(conversation_history)}")
                self.test_results["multi_agent_conversation"] = True
            else:
                print(f"❌ 多智能体对话流程不完整: 只有 {len(conversation_history)} 轮")
                self.test_results["multi_agent_conversation"] = False

        except Exception as e:
            print(f"❌ 多智能体对话流程测试失败: {e}")
            self.test_results["multi_agent_conversation"] = False

    def generate_collaboration_report(self):
        """生成协作测试报告"""
        print("\n📊 多智能体协作测试报告")
        print("=" * 50)

        passed = 0
        failed = 0

        categories = {
            "grammar_correction": "协作语法纠错",
            "disagreement": "分歧处理机制",
            "creation": "协作创作功能",
            "conversation": "多智能体对话"
        }

        for category, description in categories.items():
            category_tests = [k for k in self.test_results.keys() if category in k]
            category_passed = sum(1 for k in category_tests if self.test_results[k] is True)
            category_total = len(category_tests)

            if category_total > 0:
                success_rate = (category_passed / category_total) * 100
                print(f"{description:<20} {category_passed}/{category_total} ({success_rate:.1f}%)")

                if success_rate >= 80:
                    passed += 1
                else:
                    failed += 1

        print(f"\n协作功能模块通过率:")
        print(f"✅ 通过: {passed}")
        print(f"❌ 需要改进: {failed}")

        overall_success = failed == 0

        if overall_success:
            print("\n🎉 多智能体协作功能测试通过！")
        else:
            print(f"\n⚠️  有 {failed} 个功能模块需要改进")

        return overall_success

    async def run_all_tests(self):
        """运行所有协作测试"""
        print("🚀 开始多智能体协作功能测试...\n")

        await self.test_grammar_correction_workflow()
        await self.test_agent_disagreement_resolution()
        await self.test_collaborative_creation()
        await self.test_multi_agent_conversation_flow()

        return self.generate_collaboration_report()


# 运行测试
async def main():
    tester = CollaborationTester()
    success = await tester.run_all_tests()

    if success:
        print("\n✅ 多智能体协作测试通过 - 可以继续数据持久化测试")
    else:
        print("\n⚠️  多智能体协作测试发现问题 - 建议修复后再继续")


if __name__ == "__main__":
    asyncio.run(main())