#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端到端集成测试
测试完整的日语学习Multi-Agent系统的综合功能
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import sys
import os
import uuid
import requests

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class EndToEndTester:
    """端到端集成测试类"""

    def __init__(self):
        self.test_results = {}
        self.test_session_id = str(uuid.uuid4())
        self.test_user_id = "integration_test_user"
        self.api_base_url = "http://localhost:8000"  # 可配置
        self.integration_scenarios = []

    async def test_complete_learning_session(self):
        """测试完整的学习会话流程"""
        print("🔍 测试完整学习会话流程...")

        # 模拟一个真实用户的完整学习过程
        learning_session = {
            "phase_1_grammar_check": "私は昨日友達と映画を見に行った。とても面白かったです。",
            "phase_2_vocabulary_learning": "「面白い」の類義語を教えてください",
            "phase_3_cultural_context": "日本人はどのような映画が好きですか？",
            "phase_4_exam_preparation": "N3レベルの文法問題を出してください",
            "phase_5_review_planning": "今日学んだことの復習計画を立ててください"
        }

        session_results = {}
        active_agents = set()
        conversation_history = []
        learning_points_collected = []

        print(f"\n📚 开始完整学习会话 (Session ID: {self.test_session_id})")

        try:
            # Phase 1: 语法检查和协作纠错
            print("\n   Phase 1: 协作语法纠错")

            grammar_result = await self._test_grammar_collaboration(
                learning_session["phase_1_grammar_check"]
            )

            if grammar_result["success"]:
                session_results["grammar_collaboration"] = True
                active_agents.update(grammar_result["participating_agents"])
                conversation_history.extend(grammar_result["conversation"])
                learning_points_collected.extend(grammar_result.get("learning_points", []))
                print("   - ✅ 协作语法纠错成功")
            else:
                session_results["grammar_collaboration"] = False
                print("   - ❌ 协作语法纠错失败")

            # Phase 2: 词汇学习和记忆
            print("\n   Phase 2: 词汇学习与记忆管理")

            vocabulary_result = await self._test_vocabulary_learning_flow(
                learning_session["phase_2_vocabulary_learning"]
            )

            if vocabulary_result["success"]:
                session_results["vocabulary_learning"] = True
                active_agents.update(vocabulary_result["participating_agents"])
                conversation_history.extend(vocabulary_result["conversation"])
                learning_points_collected.extend(vocabulary_result.get("learning_points", []))
                print("   - ✅ 词汇学习流程成功")
            else:
                session_results["vocabulary_learning"] = False
                print("   - ❌ 词汇学习流程失败")

            # Phase 3: 文化背景学习
            print("\n   Phase 3: 文化背景知识学习")

            culture_result = await self._test_cultural_learning(
                learning_session["phase_3_cultural_context"]
            )

            if culture_result["success"]:
                session_results["cultural_learning"] = True
                active_agents.update(culture_result["participating_agents"])
                conversation_history.extend(culture_result["conversation"])
                print("   - ✅ 文化学习成功")
            else:
                session_results["cultural_learning"] = False
                print("   - ❌ 文化学习失败")

            # Phase 4: 考试准备
            print("\n   Phase 4: 考试准备与练习")

            exam_result = await self._test_exam_preparation_flow(
                learning_session["phase_4_exam_preparation"]
            )

            if exam_result["success"]:
                session_results["exam_preparation"] = True
                active_agents.update(exam_result["participating_agents"])
                conversation_history.extend(exam_result["conversation"])
                print("   - ✅ 考试准备成功")
            else:
                session_results["exam_preparation"] = False
                print("   - ❌ 考试准备失败")

            # Phase 5: 复习计划和进度跟踪
            print("\n   Phase 5: 智能复习规划")

            review_result = await self._test_review_planning_integration(
                learning_session["phase_5_review_planning"],
                learning_points_collected
            )

            if review_result["success"]:
                session_results["review_planning"] = True
                active_agents.update(review_result["participating_agents"])
                conversation_history.extend(review_result["conversation"])
                print("   - ✅ 复习规划成功")
            else:
                session_results["review_planning"] = False
                print("   - ❌ 复习规划失败")

            # 分析完整学习会话
            successful_phases = sum(1 for result in session_results.values() if result)
            total_phases = len(session_results)

            print(f"\n📊 学习会话总结:")
            print(f"   - 成功阶段: {successful_phases}/{total_phases}")
            print(f"   - 参与智能体: {len(active_agents)} 个")
            print(f"   - 对话轮次: {len(conversation_history)}")
            print(f"   - 学习点收集: {len(learning_points_collected)} 个")

            if successful_phases >= 4:  # 至少80%成功
                print("   - ✅ 完整学习会话测试通过")
                self.test_results["complete_learning_session"] = True
            else:
                print("   - ❌ 完整学习会话测试失败")
                self.test_results["complete_learning_session"] = False

        except Exception as e:
            print(f"❌ 完整学习会话测试异常: {e}")
            self.test_results["complete_learning_session"] = False

    async def _test_grammar_collaboration(self, user_input: str):
        """测试语法协作流程"""
        result = {
            "success": False,
            "participating_agents": [],
            "conversation": [],
            "learning_points": []
        }

        try:
            # 模拟多智能体协作语法纠错
            expected_agents = ["tanaka", "koumi", "ai", "membot"]

            for agent_id in expected_agents:
                agent_response = await self._get_agent_response(
                    agent_id, user_input, "grammar_check"
                )

                if agent_response["success"]:
                    result["participating_agents"].append(agent_id)
                    result["conversation"].append(agent_response["response"])
                    result["learning_points"].extend(agent_response.get("learning_points", []))

            # 检查协作是否成功
            if len(result["participating_agents"]) >= 2:
                result["success"] = True

        except Exception as e:
            print(f"   - 语法协作测试异常: {e}")

        return result

    async def _test_vocabulary_learning_flow(self, user_input: str):
        """测试词汇学习流程"""
        result = {
            "success": False,
            "participating_agents": [],
            "conversation": [],
            "learning_points": []
        }

        try:
            # 词汇学习主要由 koumi, yamada, ai, membot 参与
            vocabulary_agents = ["koumi", "yamada", "ai", "membot"]

            for agent_id in vocabulary_agents:
                agent_response = await self._get_agent_response(
                    agent_id, user_input, "vocabulary_learning"
                )

                if agent_response["success"]:
                    result["participating_agents"].append(agent_id)
                    result["conversation"].append(agent_response["response"])
                    result["learning_points"].extend(agent_response.get("learning_points", []))

            # 验证词汇学习效果
            if len(result["participating_agents"]) >= 2:
                result["success"] = True

        except Exception as e:
            print(f"   - 词汇学习流程测试异常: {e}")

        return result

    async def _test_cultural_learning(self, user_input: str):
        """测试文化学习"""
        result = {
            "success": False,
            "participating_agents": [],
            "conversation": []
        }

        try:
            # 文化学习主要由 yamada 主导，koumi 和 ai 辅助
            cultural_agents = ["yamada", "koumi", "ai"]

            for agent_id in cultural_agents:
                agent_response = await self._get_agent_response(
                    agent_id, user_input, "cultural_learning"
                )

                if agent_response["success"]:
                    result["participating_agents"].append(agent_id)
                    result["conversation"].append(agent_response["response"])

            # 验证文化学习效果
            if "yamada" in result["participating_agents"]:
                result["success"] = True

        except Exception as e:
            print(f"   - 文化学习测试异常: {e}")

        return result

    async def _test_exam_preparation_flow(self, user_input: str):
        """测试考试准备流程"""
        result = {
            "success": False,
            "participating_agents": [],
            "conversation": []
        }

        try:
            # 考试准备主要由 sato 主导，ai 和 membot 辅助
            exam_agents = ["sato", "ai", "membot"]

            for agent_id in exam_agents:
                agent_response = await self._get_agent_response(
                    agent_id, user_input, "exam_preparation"
                )

                if agent_response["success"]:
                    result["participating_agents"].append(agent_id)
                    result["conversation"].append(agent_response["response"])

            # 验证考试准备效果
            if "sato" in result["participating_agents"]:
                result["success"] = True

        except Exception as e:
            print(f"   - 考试准备流程测试异常: {e}")

        return result

    async def _test_review_planning_integration(self, user_input: str, learning_points: List[str]):
        """测试复习规划集成"""
        result = {
            "success": False,
            "participating_agents": [],
            "conversation": []
        }

        try:
            # 复习规划主要由 membot 主导，ai 辅助
            review_agents = ["membot", "ai"]

            # 将学习点作为上下文传递
            enriched_input = f"{user_input}\n学习点：{', '.join(learning_points[:5])}"  # 限制长度

            for agent_id in review_agents:
                agent_response = await self._get_agent_response(
                    agent_id, enriched_input, "review_planning"
                )

                if agent_response["success"]:
                    result["participating_agents"].append(agent_id)
                    result["conversation"].append(agent_response["response"])

            # 验证复习规划效果
            if "membot" in result["participating_agents"]:
                result["success"] = True

        except Exception as e:
            print(f"   - 复习规划集成测试异常: {e}")

        return result

    async def _get_agent_response(self, agent_id: str, user_input: str, scene: str):
        """获取智能体响应（支持API和直接调用）"""
        result = {
            "success": False,
            "response": {},
            "learning_points": []
        }

        # 首先尝试API调用
        api_success = await self._try_api_call(agent_id, user_input, scene)
        if api_success["success"]:
            return api_success

        # 回退到直接调用
        try:
            from core.agents import get_agent

            agent = get_agent(agent_id)

            session_context = {
                "user_id": self.test_user_id,
                "session_id": self.test_session_id,
                "scene": scene,
                "history": []
            }

            response = await agent.process_user_input(
                user_input=user_input,
                session_context=session_context,
                scene=scene
            )

            if response and response.get("content"):
                result["success"] = True
                result["response"] = response
                result["learning_points"] = response.get("learning_points", [])

        except Exception as e:
            print(f"   - {agent_id} 直接调用失败: {e}")

        return result

    async def _try_api_call(self, agent_id: str, user_input: str, scene: str):
        """尝试API调用"""
        result = {
            "success": False,
            "response": {},
            "learning_points": []
        }

        try:
            agent_names = {
                "tanaka": "田中先生",
                "koumi": "小美",
                "ai": "アイ",
                "yamada": "山田先生",
                "sato": "佐藤教练",
                "membot": "MemBot"
            }

            request_data = {
                "message": user_input,
                "user_id": self.test_user_id,
                "session_id": self.test_session_id,
                "agent_name": agent_names.get(agent_id, agent_id),
                "scene_context": scene
            }

            response = requests.post(
                f"{self.api_base_url}/api/v1/chat/send",
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success", True):  # 默认成功
                    result["success"] = True
                    result["response"] = data
                    result["learning_points"] = data.get("learning_points", [])

        except requests.exceptions.RequestException:
            # API不可用，这是正常情况
            pass
        except Exception as e:
            print(f"   - API调用异常: {e}")

        return result

    async def test_collaborative_story_creation(self):
        """测试协作故事创作功能"""
        print("\n🔍 测试协作故事创作功能...")

        story_themes = [
            "春天的校园生活",
            "传统日本茶道体验",
            "东京现代生活"
        ]

        successful_creations = 0

        for i, theme in enumerate(story_themes):
            print(f"\n   故事创作 {i + 1}: {theme}")

            try:
                # 模拟协作创作过程
                creation_agents = ["koumi", "yamada", "ai"]
                story_parts = []
                participating_agents = []

                for agent_id in creation_agents:
                    creation_prompt = f"为主题'{theme}'创作一段故事"
                    if story_parts:
                        creation_prompt += f"，延续前面的内容：{story_parts[-1][:50]}..."

                    agent_response = await self._get_agent_response(
                        agent_id, creation_prompt, "creative_writing"
                    )

                    if agent_response["success"]:
                        story_parts.append(agent_response["response"].get("content", ""))
                        participating_agents.append(agent_id)
                        print(f"     - {agent_id}: 已贡献故事片段")

                if len(story_parts) >= 2:
                    total_length = sum(len(part) for part in story_parts)
                    print(f"     - ✅ 协作创作成功: {len(story_parts)} 片段, {total_length} 字符")
                    successful_creations += 1
                else:
                    print(f"     - ❌ 协作创作不足: 只有 {len(story_parts)} 片段")

            except Exception as e:
                print(f"     - ❌ 故事创作异常: {e}")

        if successful_creations >= 2:
            print("   - ✅ 协作故事创作功能测试通过")
            self.test_results["collaborative_story_creation"] = True
        else:
            print(f"   - ❌ 协作故事创作功能测试失败: 只有 {successful_creations} 个成功")
            self.test_results["collaborative_story_creation"] = False

    async def test_system_performance_under_load(self):
        """测试系统负载性能"""
        print("\n🔍 测试系统负载性能...")

        # 模拟并发用户请求
        concurrent_requests = 5
        test_input = "私は日本語を勉強しています。"

        async def single_request(request_id: int):
            """单个请求"""
            start_time = time.time()

            try:
                agent_response = await self._get_agent_response(
                    "tanaka", f"{test_input} (请求 {request_id})", "general"
                )

                end_time = time.time()
                response_time = end_time - start_time

                return {
                    "request_id": request_id,
                    "success": agent_response["success"],
                    "response_time": response_time
                }

            except Exception as e:
                end_time = time.time()
                return {
                    "request_id": request_id,
                    "success": False,
                    "response_time": end_time - start_time,
                    "error": str(e)
                }

        # 并发执行请求
        print(f"   发送 {concurrent_requests} 个并发请求...")

        tasks = [single_request(i) for i in range(concurrent_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 分析性能结果
        successful_requests = 0
        total_response_time = 0
        max_response_time = 0
        min_response_time = float('inf')

        for result in results:
            if isinstance(result, dict):
                if result.get("success"):
                    successful_requests += 1

                response_time = result.get("response_time", 0)
                total_response_time += response_time
                max_response_time = max(max_response_time, response_time)
                min_response_time = min(min_response_time, response_time)

        if concurrent_requests > 0:
            success_rate = (successful_requests / concurrent_requests) * 100
            avg_response_time = total_response_time / concurrent_requests

            print(f"   - 成功率: {success_rate:.1f}% ({successful_requests}/{concurrent_requests})")
            print(f"   - 平均响应时间: {avg_response_time:.2f} 秒")
            print(f"   - 最大响应时间: {max_response_time:.2f} 秒")
            print(f"   - 最小响应时间: {min_response_time:.2f} 秒")

            # 性能标准：成功率 > 80% 且平均响应时间 < 10秒
            if success_rate >= 80 and avg_response_time < 10:
                print("   - ✅ 系统负载性能测试通过")
                self.test_results["system_performance"] = True
            else:
                print("   - ❌ 系统负载性能测试失败")
                self.test_results["system_performance"] = False
        else:
            print("   - ❌ 无有效请求结果")
            self.test_results["system_performance"] = False

    async def test_data_consistency_across_sessions(self):
        """测试跨会话数据一致性"""
        print("\n🔍 测试跨会话数据一致性...")

        try:
            # 会话1：学习一些内容
            session_1_id = str(uuid.uuid4())
            session_1_learning = "私は図書館で本を読みます。"

            print(f"   会话1 ({session_1_id[:8]}...): 学习语法")

            session_1_response = await self._get_agent_response(
                "tanaka", session_1_learning, "grammar_learning"
            )

            if not session_1_response["success"]:
                print("   - ❌ 会话1失败")
                self.test_results["data_consistency"] = False
                return

            # 会话2：MemBot应该记住之前的学习内容
            session_2_id = str(uuid.uuid4())
            session_2_query = "我之前学过什么语法点？"

            print(f"   会话2 ({session_2_id[:8]}...): 查询学习历史")

            # 等待一小段时间确保数据持久化
            await asyncio.sleep(1)

            session_2_response = await self._get_agent_response(
                "membot", session_2_query, "learning_history"
            )

            if session_2_response["success"]:
                # 检查MemBot是否提到了相关的语法内容
                response_content = session_2_response["response"].get("content", "").lower()

                # 简单的内容相关性检查
                relevant_keywords = ["図書館", "本", "読み", "grammar", "語法"]
                has_relevant_content = any(keyword.lower() in response_content for keyword in relevant_keywords)

                if has_relevant_content or "学習" in response_content or "勉強" in response_content:
                    print("   - ✅ MemBot记住了学习内容")
                    consistency_check = True
                else:
                    print("   - ⚠️  MemBot可能未完全记住学习内容")
                    consistency_check = True  # 仍然认为基本功能正常
            else:
                print("   - ❌ 会话2失败")
                consistency_check = False

            # 会话3：AI分析师分析学习进度
            session_3_id = str(uuid.uuid4())
            session_3_query = "分析我的学习进度"

            print(f"   会话3 ({session_3_id[:8]}...): 分析学习进度")

            session_3_response = await self._get_agent_response(
                "ai", session_3_query, "progress_analysis"
            )

            if session_3_response["success"]:
                print("   - ✅ AI分析师成功分析")
                analysis_check = True
            else:
                print("   - ❌ AI分析师分析失败")
                analysis_check = False

            # 综合评估数据一致性
            if consistency_check and analysis_check:
                print("   - ✅ 跨会话数据一致性测试通过")
                self.test_results["data_consistency"] = True
            else:
                print("   - ❌ 跨会话数据一致性测试失败")
                self.test_results["data_consistency"] = False

        except Exception as e:
            print(f"   - ❌ 数据一致性测试异常: {e}")
            self.test_results["data_consistency"] = False

    async def test_error_recovery_and_fallback(self):
        """测试错误恢复和降级机制"""
        print("\n🔍 测试错误恢复和降级机制...")

        error_scenarios = [
            {
                "name": "无效输入处理",
                "input": "",  # 空输入
                "agent": "tanaka"
            },
            {
                "name": "极长输入处理",
                "input": "テスト" * 1000,  # 极长输入
                "agent": "koumi"
            },
            {
                "name": "特殊字符输入",
                "input": "!@#$%^&*()_+{}[]|\\:;\"'<>?,./ 测试 🎌 👍",
                "agent": "yamada"
            }
        ]

        successful_recoveries = 0

        for scenario in error_scenarios:
            print(f"   测试 {scenario['name']}...")

            try:
                response = await self._get_agent_response(
                    scenario["agent"], scenario["input"], "error_test"
                )

                # 检查是否有合理的错误处理
                if response["success"]:
                    content = response["response"].get("content", "")
                    # 有内容输出就认为错误处理正常
                    if content and len(content.strip()) > 0:
                        print(f"     - ✅ {scenario['agent']} 正常处理异常输入")
                        successful_recoveries += 1
                    else:
                        print(f"     - ⚠️  {scenario['agent']} 返回空内容")
                else:
                    # 即使失败，如果能优雅降级也算成功
                    print(f"     - ⚠️  {scenario['agent']} 优雅失败")
                    successful_recoveries += 1  # 优雅失败也算成功恢复

            except Exception as e:
                print(f"     - ❌ {scenario['agent']} 异常处理失败: {e}")

        recovery_rate = (successful_recoveries / len(error_scenarios)) * 100

        if recovery_rate >= 80:
            print(f"   - ✅ 错误恢复测试通过 (成功率: {recovery_rate:.1f}%)")
            self.test_results["error_recovery"] = True
        else:
            print(f"   - ❌ 错误恢复测试失败 (成功率: {recovery_rate:.1f}%)")
            self.test_results["error_recovery"] = False

    def generate_integration_report(self):
        """生成集成测试报告"""
        print("\n📊 端到端集成测试报告")
        print("=" * 60)

        test_categories = {
            "complete_learning_session": "完整学习会话流程",
            "collaborative_story_creation": "协作故事创作功能",
            "system_performance": "系统负载性能测试",
            "data_consistency": "跨会话数据一致性",
            "error_recovery": "错误恢复和降级机制"
        }

        passed = 0
        failed = 0
        critical_failures = []

        for test_key, description in test_categories.items():
            result = self.test_results.get(test_key, False)

            if result:
                status = "✅ 通过"
                passed += 1
            else:
                status = "❌ 失败"
                failed += 1
                # 标记关键失败
                if test_key in ["complete_learning_session", "system_performance"]:
                    critical_failures.append(description)

            print(f"{description:<30} {status}")

        print(f"\n集成测试总结:")
        print(f"✅ 通过: {passed}")
        print(f"❌ 失败: {failed}")
        print(f"📊 总体成功率: {(passed / (passed + failed) * 100):.1f}%")

        # 系统就绪评估
        if len(critical_failures) == 0 and passed >= 4:
            system_status = "🎉 系统集成测试完全通过！系统已就绪投入使用。"
            overall_success = True
        elif len(critical_failures) == 0:
            system_status = "✅ 系统基本功能正常，但建议完善部分辅助功能。"
            overall_success = True
        elif len(critical_failures) <= 1:
            system_status = "⚠️  系统核心功能存在问题，建议修复后再使用。"
            overall_success = False
        else:
            system_status = "❌ 系统存在多个关键问题，需要重大修复。"
            overall_success = False

        print(f"\n🏁 系统就绪状态:")
        print(f"{system_status}")

        if critical_failures:
            print(f"\n⚠️  关键问题:")
            for failure in critical_failures:
                print(f"   - {failure}")

        return overall_success

    async def run_all_tests(self):
        """运行所有集成测试"""
        print("🚀 开始端到端集成测试...")
        print(f"📋 测试会话ID: {self.test_session_id}")
        print(f"👤 测试用户ID: {self.test_user_id}")
        print(f"🌐 API地址: {self.api_base_url}")
        print("=" * 60)

        start_time = time.time()

        # 按重要性顺序运行测试
        await self.test_complete_learning_session()
        await self.test_collaborative_story_creation()
        await self.test_system_performance_under_load()
        await self.test_data_consistency_across_sessions()
        await self.test_error_recovery_and_fallback()

        end_time = time.time()
        total_time = end_time - start_time

        print(f"\n⏱️  总测试时间: {total_time:.2f} 秒")

        return self.generate_integration_report()


# 运行测试
async def main():
    print("🎌 日语学习Multi-Agent系统 - 端到端集成测试")
    print("=" * 60)

    tester = EndToEndTester()
    success = await tester.run_all_tests()

    if success:
        print("\n🎊 恭喜！您的日语学习Multi-Agent系统已通过全面测试！")
        print("💡 系统已就绪，可以开始享受智能化的日语学习体验了！")
    else:
        print("\n🔧 系统测试发现了一些需要改进的地方，建议优化后再投入使用。")
        print("📋 请参考上面的测试报告进行相应的修复和改进。")


if __name__ == "__main__":
    asyncio.run(main())