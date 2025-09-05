# test_multi_agent_collaboration.py
"""
多智能体协作功能完整测试脚本
测试智能体间的协作、冲突解决、工作流编排等核心功能
"""

import asyncio
import json
import time
from datetime import datetime
from typing import List, Dict, Any
import aiohttp
import pytest


class MultiAgentCollaborationTester:
    """多智能体协作测试器"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.test_results = []

    async def setup(self):
        """初始化测试环境"""
        self.session = aiohttp.ClientSession()
        print("🔧 初始化测试环境...")

        # 检查所有智能体是否在线
        agents = ["tanaka", "koumi", "ai", "yamada", "sato", "membot"]
        for agent in agents:
            status = await self.check_agent_status(agent)
            assert status == "online", f"智能体 {agent} 未在线"

        print("✅ 所有智能体已上线")

    async def cleanup(self):
        """清理测试环境"""
        if self.session:
            await self.session.close()

        # 生成测试报告
        await self.generate_test_report()

    async def check_agent_status(self, agent_id: str) -> str:
        """检查智能体状态"""
        try:
            async with self.session.get(f"{self.base_url}/api/v1/agents/{agent_id}/status") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("status", "offline")
                return "offline"
        except Exception:
            return "offline"

    async def test_grammar_correction_collaboration(self):
        """测试1: 语法纠错协作流程"""
        print("\n🧪 测试1: 语法纠错协作流程")
        test_start = time.time()

        user_input = "今日は学校に行きました。でも友達に会いませんでした。"
        session_id = f"grammar_test_{int(time.time())}"

        try:
            # 1. 发送给田中先生进行语法分析
            tanaka_result = await self.send_message(
                message=user_input,
                agent_name="田中先生",
                session_id=session_id,
                task_type="grammar_analysis"
            )

            # 2. 小美提供口语化建议
            koumi_result = await self.send_message(
                message=f"基于语法分析：{tanaka_result.get('content', '')}，请提供口语化建议",
                agent_name="小美",
                session_id=session_id,
                task_type="casual_suggestion"
            )

            # 3. アイ进行综合分析
            ai_result = await self.send_message(
                message=f"综合分析：语法分析={tanaka_result.get('content', '')}，口语建议={koumi_result.get('content', '')}",
                agent_name="アイ",
                session_id=session_id,
                task_type="synthesis"
            )

            # 4. 验证协作质量
            collaboration_quality = await self.evaluate_collaboration([
                tanaka_result, koumi_result, ai_result
            ])

            test_duration = time.time() - test_start

            result = {
                "test_name": "语法纠错协作",
                "success": True,
                "duration": test_duration,
                "participants": ["田中先生", "小美", "アイ"],
                "collaboration_quality": collaboration_quality,
                "responses": {
                    "tanaka": tanaka_result,
                    "koumi": koumi_result,
                    "ai": ai_result
                }
            }

            # 验证关键指标
            assert collaboration_quality["completeness"] > 0.8, "协作完整性不足"
            assert collaboration_quality["coherence"] > 0.7, "协作连贯性不足"
            assert test_duration < 15, "协作响应时间过长"

            print(f"✅ 语法纠错协作测试通过 (耗时: {test_duration:.2f}s)")

        except Exception as e:
            result = {
                "test_name": "语法纠错协作",
                "success": False,
                "error": str(e),
                "duration": time.time() - test_start
            }
            print(f"❌ 语法纠错协作测试失败: {e}")

        self.test_results.append(result)
        return result

    async def test_cultural_discussion_collaboration(self):
        """测试2: 文化话题讨论协作"""
        print("\n🧪 测试2: 文化话题讨论协作")
        test_start = time.time()

        topic = "日本的お花見文化和现代社会的变化"
        session_id = f"culture_test_{int(time.time())}"

        try:
            # 1. 山田先生提供文化背景
            yamada_result = await self.send_message(
                message=f"请详细解释：{topic}",
                agent_name="山田先生",
                session_id=session_id,
                task_type="cultural_explanation"
            )

            # 2. 小美分享现代观点
            koumi_result = await self.send_message(
                message=f"基于山田先生的解释：{yamada_result.get('content', '')}，分享年轻人的现代观点",
                agent_name="小美",
                session_id=session_id,
                task_type="modern_perspective"
            )

            # 3. 田中先生补充语言表达
            tanaka_result = await self.send_message(
                message=f"基于文化讨论，补充相关的日语表达和用法",
                agent_name="田中先生",
                session_id=session_id,
                task_type="language_supplement"
            )

            # 4. アイ进行数据分析和总结
            ai_result = await self.send_message(
                message=f"分析整个讨论，提供学习建议和知识点总结",
                agent_name="アイ",
                session_id=session_id,
                task_type="discussion_analysis"
            )

            collaboration_quality = await self.evaluate_collaboration([
                yamada_result, koumi_result, tanaka_result, ai_result
            ])

            test_duration = time.time() - test_start

            result = {
                "test_name": "文化讨论协作",
                "success": True,
                "duration": test_duration,
                "participants": ["山田先生", "小美", "田中先生", "アイ"],
                "collaboration_quality": collaboration_quality,
                "topic": topic
            }

            # 验证协作效果
            assert collaboration_quality["depth"] > 0.8, "讨论深度不足"
            assert collaboration_quality["diversity"] > 0.7, "观点多样性不足"

            print(f"✅ 文化讨论协作测试通过 (耗时: {test_duration:.2f}s)")

        except Exception as e:
            result = {
                "test_name": "文化讨论协作",
                "success": False,
                "error": str(e),
                "duration": time.time() - test_start
            }
            print(f"❌ 文化讨论协作测试失败: {e}")

        self.test_results.append(result)
        return result

    async def test_novel_creation_collaboration(self):
        """测试3: 小说创作协作"""
        print("\n🧪 测试3: 小说创作协作")
        test_start = time.time()

        theme = "桜の季節の初恋"
        session_id = f"novel_test_{int(time.time())}"

        try:
            # 1. 头脑风暴阶段 - 所有智能体参与
            brainstorm_results = []
            agents = ["小美", "山田先生", "田中先生"]

            for agent in agents:
                result = await self.send_message(
                    message=f"为主题'{theme}'贡献创作想法和故事框架",
                    agent_name=agent,
                    session_id=session_id,
                    task_type="brainstorming"
                )
                brainstorm_results.append(result)

            # 2. 轮流创作阶段
            story_parts = []
            for round_num in range(3):  # 3轮创作
                for agent in agents:
                    previous_context = "\n".join([part.get("content", "") for part in story_parts[-2:]])

                    part_result = await self.send_message(
                        message=f"继续故事创作，前文：{previous_context}",
                        agent_name=agent,
                        session_id=session_id,
                        task_type="story_writing",
                        round=round_num
                    )
                    story_parts.append(part_result)

            # 3. 评估创作质量
            story_quality = await self.evaluate_story_creation(story_parts)

            test_duration = time.time() - test_start

            result = {
                "test_name": "小说创作协作",
                "success": True,
                "duration": test_duration,
                "participants": agents,
                "story_parts_count": len(story_parts),
                "story_quality": story_quality,
                "theme": theme
            }

            # 验证创作效果
            assert story_quality["creativity"] > 0.7, "创意性不足"
            assert story_quality["coherence"] > 0.8, "故事连贯性不足"
            assert len(story_parts) >= 6, "创作内容不足"

            print(f"✅ 小说创作协作测试通过 (耗时: {test_duration:.2f}s, 创作段落: {len(story_parts)})")

        except Exception as e:
            result = {
                "test_name": "小说创作协作",
                "success": False,
                "error": str(e),
                "duration": time.time() - test_start
            }
            print(f"❌ 小说创作协作测试失败: {e}")

        self.test_results.append(result)
        return result

    async def test_conflict_resolution(self):
        """测试4: 智能体冲突解决机制"""
        print("\n🧪 测试4: 智能体冲突解决")
        test_start = time.time()

        controversial_topic = "现代日语中外来语的使用是否过多？"
        session_id = f"conflict_test_{int(time.time())}"

        try:
            # 1. 获取不同智能体的观点（预期会有分歧）
            opinions = {}

            # 田中先生的保守观点
            tanaka_opinion = await self.send_message(
                message=controversial_topic,
                agent_name="田中先生",
                session_id=session_id,
                task_type="opinion"
            )
            opinions["tanaka"] = tanaka_opinion

            # 小美的现代观点
            koumi_opinion = await self.send_message(
                message=controversial_topic,
                agent_name="小美",
                session_id=session_id,
                task_type="opinion"
            )
            opinions["koumi"] = koumi_opinion

            # 山田先生的历史文化观点
            yamada_opinion = await self.send_message(
                message=controversial_topic,
                agent_name="山田先生",
                session_id=session_id,
                task_type="opinion"
            )
            opinions["yamada"] = yamada_opinion

            # 2. 检测分歧程度
            conflict_analysis = await self.analyze_conflict(opinions)

            # 3. アイ进行冲突调解
            resolution_result = await self.send_message(
                message=f"分析以下观点分歧并提供平衡的解决方案：田中观点={tanaka_opinion.get('content', '')}，小美观点={koumi_opinion.get('content', '')}，山田观点={yamada_opinion.get('content', '')}",
                agent_name="アイ",
                session_id=session_id,
                task_type="conflict_resolution"
            )

            test_duration = time.time() - test_start

            result = {
                "test_name": "冲突解决机制",
                "success": True,
                "duration": test_duration,
                "conflict_detected": conflict_analysis["has_conflict"],
                "conflict_intensity": conflict_analysis["intensity"],
                "resolution_quality": await self.evaluate_resolution(resolution_result),
                "opinions": opinions,
                "resolution": resolution_result
            }

            # 验证冲突解决效果
            assert conflict_analysis["has_conflict"], "未检测到预期的观点分歧"
            assert conflict_analysis["intensity"] > 0.5, "分歧强度不足"

            print(f"✅ 冲突解决机制测试通过 (耗时: {test_duration:.2f}s)")

        except Exception as e:
            result = {
                "test_name": "冲突解决机制",
                "success": False,
                "error": str(e),
                "duration": time.time() - test_start
            }
            print(f"❌ 冲突解决机制测试失败: {e}")

        self.test_results.append(result)
        return result

    async def test_realtime_collaboration_workflow(self):
        """测试5: 实时协作工作流"""
        print("\n🧪 测试5: 实时协作工作流")
        test_start = time.time()

        session_id = f"realtime_test_{int(time.time())}"

        try:
            # 1. 启动协作会话
            collab_session = await self.start_collaboration_session(
                session_id=session_id,
                participants=["田中先生", "小美", "アイ"],
                task_type="complex_learning",
                topic="JLPT N2 语法综合练习"
            )

            # 2. 模拟用户提问
            user_question = "「〜ばかりに」和「〜ために」的区别是什么？"

            # 3. 智能体并行处理
            tasks = []
            agents_config = [
                {"agent": "田中先生", "focus": "语法解析"},
                {"agent": "小美", "focus": "实际使用例子"},
                {"agent": "アイ", "focus": "学习建议"}
            ]

            for config in agents_config:
                task = self.send_message(
                    message=f"{user_question} (专注于{config['focus']})",
                    agent_name=config["agent"],
                    session_id=session_id,
                    task_type="parallel_processing"
                )
                tasks.append(task)

            # 等待所有智能体完成
            results = await asyncio.gather(*tasks)

            # 4. 合成最终回答
            synthesis_result = await self.synthesize_responses(results, session_id)

            # 5. 评估工作流效率
            workflow_metrics = await self.evaluate_workflow(collab_session, results, synthesis_result)

            test_duration = time.time() - test_start

            result = {
                "test_name": "实时协作工作流",
                "success": True,
                "duration": test_duration,
                "participants": len(agents_config),
                "parallel_processing_time": max([r.get("response_time", 0) for r in results]),
                "workflow_efficiency": workflow_metrics["efficiency"],
                "synthesis_quality": workflow_metrics["synthesis_quality"]
            }

            # 验证工作流效果
            assert workflow_metrics["efficiency"] > 0.7, "工作流效率不足"
            assert workflow_metrics["synthesis_quality"] > 0.8, "合成质量不足"

            print(f"✅ 实时协作工作流测试通过 (耗时: {test_duration:.2f}s)")

        except Exception as e:
            result = {
                "test_name": "实时协作工作流",
                "success": False,
                "error": str(e),
                "duration": time.time() - test_start
            }
            print(f"❌ 实时协作工作流测试失败: {e}")

        self.test_results.append(result)
        return result

    async def send_message(self, message: str, agent_name: str, session_id: str,
                           task_type: str = "general", **kwargs) -> Dict[str, Any]:
        """发送消息给指定智能体"""
        start_time = time.time()

        payload = {
            "message": message,
            "user_id": "test_user",
            "session_id": session_id,
            "agent_name": agent_name,
            "scene_context": task_type,
            "metadata": kwargs
        }

        try:
            async with self.session.post(f"{self.base_url}/api/v1/chat/send",
                                         json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    response_time = time.time() - start_time
                    data["response_time"] = response_time
                    return data
                else:
                    error_text = await resp.text()
                    raise Exception(f"API错误 {resp.status}: {error_text}")
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time
            }

    async def evaluate_collaboration(self, responses: List[Dict]) -> Dict[str, float]:
        """评估协作质量"""
        if not responses:
            return {"completeness": 0, "coherence": 0, "quality": 0}

        # 简化的评估逻辑
        successful_responses = [r for r in responses if r.get("success", False)]
        completeness = len(successful_responses) / len(responses)

        # 检查回答长度和相关性
        avg_length = sum(len(r.get("response", "")) for r in successful_responses) / len(
            successful_responses) if successful_responses else 0
        coherence = min(1.0, avg_length / 100)  # 假设100字符为基准

        overall_quality = (completeness + coherence) / 2

        return {
            "completeness": completeness,
            "coherence": coherence,
            "quality": overall_quality,
            "depth": min(1.0, avg_length / 200),
            "diversity": min(1.0, len(set(r.get("agent_name", "") for r in responses)) / 3)
        }

    async def evaluate_story_creation(self, story_parts: List[Dict]) -> Dict[str, float]:
        """评估故事创作质量"""
        if not story_parts:
            return {"creativity": 0, "coherence": 0, "completeness": 0}

        total_length = sum(len(part.get("response", "")) for part in story_parts)
        creativity = min(1.0, total_length / 500)  # 基于长度估算创意性
        coherence = min(1.0, len(story_parts) / 6)  # 基于段落数评估连贯性
        completeness = min(1.0, total_length / 800)  # 基于总长度评估完整性

        return {
            "creativity": creativity,
            "coherence": coherence,
            "completeness": completeness,
            "engagement": (creativity + coherence) / 2
        }

    async def analyze_conflict(self, opinions: Dict[str, Dict]) -> Dict[str, Any]:
        """分析观点冲突"""
        # 简化的冲突检测逻辑
        opinion_lengths = [len(op.get("response", "")) for op in opinions.values()]
        avg_length = sum(opinion_lengths) / len(opinion_lengths) if opinion_lengths else 0

        # 假设如果所有观点都很详细，说明有分歧
        has_conflict = avg_length > 50 and len(opinions) >= 2
        intensity = min(1.0, avg_length / 200) if has_conflict else 0

        return {
            "has_conflict": has_conflict,
            "intensity": intensity,
            "participants": len(opinions)
        }

    async def evaluate_resolution(self, resolution: Dict) -> float:
        """评估冲突解决质量"""
        resolution_text = resolution.get("response", "")
        # 基于回答长度和关键词评估解决质量
        quality_indicators = ["平衡", "考虑", "观点", "建议", "综合"]
        keyword_score = sum(1 for keyword in quality_indicators if keyword in resolution_text)
        length_score = min(1.0, len(resolution_text) / 150)

        return (keyword_score / len(quality_indicators) + length_score) / 2

    async def start_collaboration_session(self, session_id: str, participants: List[str],
                                          task_type: str, topic: str) -> Dict[str, Any]:
        """启动协作会话"""
        return {
            "session_id": session_id,
            "participants": participants,
            "task_type": task_type,
            "topic": topic,
            "status": "active",
            "start_time": datetime.now().isoformat()
        }

    async def synthesize_responses(self, responses: List[Dict], session_id: str) -> Dict[str, Any]:
        """合成多个智能体的回答"""
        combined_content = "\n---\n".join([r.get("response", "") for r in responses if r.get("success")])

        # 使用アイ进行最终合成
        synthesis = await self.send_message(
            message=f"请综合以下智能体的回答，提供完整的学习建议：\n{combined_content}",
            agent_name="アイ",
            session_id=session_id,
            task_type="synthesis"
        )

        return synthesis

    async def evaluate_workflow(self, session: Dict, responses: List[Dict],
                                synthesis: Dict) -> Dict[str, float]:
        """评估工作流效率"""
        # 计算效率指标
        successful_responses = [r for r in responses if r.get("success", False)]
        success_rate = len(successful_responses) / len(responses) if responses else 0

        avg_response_time = sum(r.get("response_time", 0) for r in successful_responses) / len(
            successful_responses) if successful_responses else 0
        efficiency = max(0, 1 - avg_response_time / 10)  # 假设10秒为基准

        synthesis_quality = min(1.0, len(synthesis.get("response", "")) / 200) if synthesis.get("success") else 0

        return {
            "efficiency": (success_rate + efficiency) / 2,
            "synthesis_quality": synthesis_quality,
            "response_time": avg_response_time
        }

    async def generate_test_report(self):
        """生成测试报告"""
        report = {
            "test_timestamp": datetime.now().isoformat(),
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for r in self.test_results if r.get("success", False)),
            "failed_tests": sum(1 for r in self.test_results if not r.get("success", True)),
            "total_duration": sum(r.get("duration", 0) for r in self.test_results),
            "detailed_results": self.test_results
        }

        # 计算总体成功率
        success_rate = report["passed_tests"] / report["total_tests"] if report["total_tests"] > 0 else 0
        report["success_rate"] = success_rate

        # 保存报告
        with open(f"multi_agent_test_report_{int(time.time())}.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        # 打印摘要
        print(f"\n📊 测试报告摘要:")
        print(f"总测试数: {report['total_tests']}")
        print(f"通过测试: {report['passed_tests']}")
        print(f"失败测试: {report['failed_tests']}")
        print(f"成功率: {success_rate:.1%}")
        print(f"总耗时: {report['total_duration']:.2f}秒")

        if success_rate >= 0.8:
            print("🎉 多智能体协作功能测试总体通过！")
        else:
            print("⚠️ 多智能体协作功能需要进一步优化")

        return report


async def run_full_collaboration_tests():
    """运行完整的多智能体协作测试套件"""
    print("🚀 开始多智能体协作功能完整测试")
    print("=" * 60)

    tester = MultiAgentCollaborationTester()

    try:
        # 初始化测试环境
        await tester.setup()

        # 执行所有测试
        tests = [
            tester.test_grammar_correction_collaboration(),
            tester.test_cultural_discussion_collaboration(),
            tester.test_novel_creation_collaboration(),
            tester.test_conflict_resolution(),
            tester.test_realtime_collaboration_workflow()
        ]

        # 并发执行部分测试以提高效率
        await asyncio.gather(*tests, return_exceptions=True)

        print("\n" + "=" * 60)
        print("🏁 所有测试执行完成")

    except Exception as e:
        print(f"❌ 测试执行过程中发生错误: {e}")

    finally:
        # 清理和生成报告
        await tester.cleanup()


# 单独的测试函数，用于pytest集成
@pytest.mark.asyncio
async def test_grammar_collaboration():
    """pytest兼容的语法协作测试"""
    tester = MultiAgentCollaborationTester()
    await tester.setup()
    try:
        result = await tester.test_grammar_correction_collaboration()
        assert result["success"], f"语法协作测试失败: {result.get('error', 'Unknown error')}"
    finally:
        await tester.cleanup()


@pytest.mark.asyncio
async def test_cultural_collaboration():
    """pytest兼容的文化协作测试"""
    tester = MultiAgentCollaborationTester()
    await tester.setup()
    try:
        result = await tester.test_cultural_discussion_collaboration()
        assert result["success"], f"文化协作测试失败: {result.get('error', 'Unknown error')}"
    finally:
        await tester.cleanup()


@pytest.mark.asyncio
async def test_novel_collaboration():
    """pytest兼容的小说协作测试"""
    tester = MultiAgentCollaborationTester()
    await tester.setup()
    try:
        result = await tester.test_novel_creation_collaboration()
        assert result["success"], f"小说协作测试失败: {result.get('error', 'Unknown error')}"
    finally:
        await tester.cleanup()


@pytest.mark.asyncio
async def test_conflict_resolution():
    """pytest兼容的冲突解决测试"""
    tester = MultiAgentCollaborationTester()
    await tester.setup()
    try:
        result = await tester.test_conflict_resolution()
        assert result["success"], f"冲突解决测试失败: {result.get('error', 'Unknown error')}"
    finally:
        await tester.cleanup()


@pytest.mark.asyncio
async def test_realtime_workflow():
    """pytest兼容的实时工作流测试"""
    tester = MultiAgentCollaborationTester()
    await tester.setup()
    try:
        result = await tester.test_realtime_collaboration_workflow()
        assert result["success"], f"实时工作流测试失败: {result.get('error', 'Unknown error')}"
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    # 直接运行完整测试套件
    asyncio.run(run_full_collaboration_tests())