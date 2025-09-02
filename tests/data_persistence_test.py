#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据持久化功能测试
测试学习进度跟踪、词汇记忆系统和MemBot智能复习提醒
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta
import sys
import os
import uuid

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PersistenceTester:
    """数据持久化测试类"""

    def __init__(self):
        self.test_results = {}
        self.test_user_id = None
        self.test_data_cleanup = []  # 记录需要清理的测试数据

    async def setup_test_user(self):
        """创建测试用户"""
        print("🔧 设置测试用户...")

        try:
            # 假设存在用户服务
            from backend.services.user_service import UserService

            user_service = UserService()

            self.test_user_id = await user_service.create_user(
                username="persistence_test_user",
                email="test@persistence.com",
                password_hash="test_hash",
                learning_level="beginner",
                target_jlpt_level="N5"
            )

            self.test_data_cleanup.append(("user", self.test_user_id))
            print(f"✅ 测试用户创建成功: {self.test_user_id}")

        except ImportError:
            # 直接使用数据库连接
            self.test_user_id = await self._create_test_user_direct()

        return self.test_user_id is not None

    async def _create_test_user_direct(self):
        """直接通过数据库创建测试用户"""
        try:
            import asyncpg

            connection = await asyncpg.connect(
                "postgresql://user:password@localhost:5432/japanese_learning"
            )

            user_id = str(uuid.uuid4())
            await connection.execute("""
                INSERT INTO users (user_id, username, email, password_hash, learning_level, target_jlpt_level)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, user_id, "persistence_test_user", "test@persistence.com", "test_hash", "beginner", "N5")

            await connection.close()

            self.test_data_cleanup.append(("user_direct", user_id))
            print(f"✅ 测试用户直接创建成功: {user_id}")
            return user_id

        except Exception as e:
            print(f"❌ 测试用户创建失败: {e}")
            return None

    async def test_learning_progress_tracking(self):
        """测试学习进度跟踪"""
        print("\n🔍 测试学习进度跟踪功能...")

        if not self.test_user_id:
            print("❌ 无法测试学习进度：测试用户未创建")
            self.test_results["learning_progress"] = False
            return

        try:
            # 假设存在学习进度服务
            try:
                from backend.services.learning_service import LearningProgressService

                progress_service = LearningProgressService()

                # 测试用例：不同的语法点学习
                test_grammar_points = [
                    {"point": "は/が particle", "initial_mastery": 0.3},
                    {"point": "past tense verbs", "initial_mastery": 0.6},
                    {"point": "keigo expressions", "initial_mastery": 0.1}
                ]

                created_progress_ids = []

                # 创建学习进度记录
                for grammar_point in test_grammar_points:
                    progress_id = await progress_service.create_progress_record(
                        user_id=self.test_user_id,
                        grammar_point=grammar_point["point"],
                        mastery_level=grammar_point["initial_mastery"]
                    )

                    created_progress_ids.append(progress_id)
                    self.test_data_cleanup.append(("progress", progress_id))
                    print(f"   - ✅ 创建进度记录: {grammar_point['point']}")

                # 测试进度更新
                for i, progress_id in enumerate(created_progress_ids):
                    new_mastery = test_grammar_points[i]["initial_mastery"] + 0.2
                    await progress_service.update_mastery_level(
                        progress_id=progress_id,
                        new_mastery_level=min(new_mastery, 1.0),
                        practice_increment=1
                    )
                    print(f"   - ✅ 更新进度: {test_grammar_points[i]['point']} -> {new_mastery:.1f}")

                # 测试进度查询
                user_progress = await progress_service.get_user_progress_summary(self.test_user_id)

                assert len(user_progress) >= len(test_grammar_points), "进度记录数量不匹配"
                print(f"   - ✅ 进度查询成功: {len(user_progress)} 条记录")

                # 测试学习分析
                weak_points = await progress_service.identify_weak_points(self.test_user_id, threshold=0.5)
                strong_points = await progress_service.identify_strong_points(self.test_user_id, threshold=0.7)

                print(f"   - ✅ 学习分析: {len(weak_points)} 个薄弱点, {len(strong_points)} 个强项")

                self.test_results["learning_progress"] = True

            except ImportError:
                # 使用直接数据库测试
                await self._test_progress_direct()

        except Exception as e:
            print(f"❌ 学习进度跟踪测试失败: {e}")
            self.test_results["learning_progress"] = False

    async def _test_progress_direct(self):
        """直接使用数据库测试学习进度"""
        print("📍 使用直接数据库测试学习进度...")

        try:
            import asyncpg

            connection = await asyncpg.connect(
                "postgresql://user:password@localhost:5432/japanese_learning"
            )

            # 创建进度记录
            progress_ids = []
            test_grammar_points = ["は particle", "past tense", "keigo"]

            for grammar_point in test_grammar_points:
                progress_id = str(uuid.uuid4())
                await connection.execute("""
                    INSERT INTO learning_progress (progress_id, user_id, grammar_point, mastery_level, practice_count)
                    VALUES ($1, $2, $3, $4, $5)
                """, progress_id, self.test_user_id, grammar_point, 0.5, 1)

                progress_ids.append(progress_id)
                self.test_data_cleanup.append(("progress_direct", progress_id))

            print(f"   - ✅ 直接创建 {len(progress_ids)} 条进度记录")

            # 更新进度
            for progress_id in progress_ids:
                await connection.execute("""
                    UPDATE learning_progress 
                    SET mastery_level = mastery_level + 0.2, practice_count = practice_count + 1
                    WHERE progress_id = $1
                """, progress_id)

            print("   - ✅ 进度更新成功")

            # 查询进度
            progress_records = await connection.fetch(
                "SELECT * FROM learning_progress WHERE user_id = $1",
                self.test_user_id
            )

            print(f"   - ✅ 查询到 {len(progress_records)} 条进度记录")

            await connection.close()
            self.test_results["learning_progress_direct"] = True

        except Exception as e:
            print(f"❌ 直接数据库进度测试失败: {e}")
            self.test_results["learning_progress_direct"] = False

    async def test_vocabulary_memory_system(self):
        """测试词汇记忆系统"""
        print("\n🔍 测试词汇记忆系统...")

        if not self.test_user_id:
            print("❌ 无法测试词汇系统：测试用户未创建")
            self.test_results["vocabulary_memory"] = False
            return

        try:
            # 测试词汇数据
            test_vocabulary = [
                {"word": "桜", "reading": "さくら", "meaning": "cherry blossom", "difficulty": 2},
                {"word": "勉強", "reading": "べんきょう", "meaning": "study", "difficulty": 1},
                {"word": "美しい", "reading": "うつくしい", "meaning": "beautiful", "difficulty": 3},
                {"word": "友達", "reading": "ともだち", "meaning": "friend", "difficulty": 1},
                {"word": "図書館", "reading": "としょかん", "meaning": "library", "difficulty": 2}
            ]

            try:
                from backend.services.vocabulary_service import VocabularyService

                vocab_service = VocabularyService()
                created_vocab_ids = []

                # 添加词汇
                for vocab in test_vocabulary:
                    vocab_id = await vocab_service.add_vocabulary(
                        user_id=self.test_user_id,
                        word=vocab["word"],
                        reading=vocab["reading"],
                        meaning=vocab["meaning"],
                        difficulty_level=vocab["difficulty"]
                    )

                    created_vocab_ids.append(vocab_id)
                    self.test_data_cleanup.append(("vocabulary", vocab_id))
                    print(f"   - ✅ 添加词汇: {vocab['word']} ({vocab['reading']})")

                # 模拟复习过程
                for vocab_id in created_vocab_ids[:3]:  # 只复习前3个词汇
                    # 模拟正确回答
                    await vocab_service.record_review_result(
                        vocab_id=vocab_id,
                        is_correct=True
                    )
                    print(f"   - ✅ 记录正确复习")

                # 模拟错误回答
                for vocab_id in created_vocab_ids[3:]:  # 后面的词汇回答错误
                    await vocab_service.record_review_result(
                        vocab_id=vocab_id,
                        is_correct=False
                    )
                    print(f"   - ✅ 记录错误复习")

                # 获取需要复习的词汇
                due_reviews = await vocab_service.get_due_reviews(self.test_user_id)
                print(f"   - ✅ 获取待复习词汇: {len(due_reviews)} 个")

                # 获取掌握度统计
                mastery_stats = await vocab_service.get_mastery_statistics(self.test_user_id)
                print(f"   - ✅ 掌握度统计: 平均 {mastery_stats.get('average_mastery', 0):.2f}")

                self.test_results["vocabulary_memory"] = True

            except ImportError:
                # 直接数据库测试
                await self._test_vocabulary_direct(test_vocabulary)

        except Exception as e:
            print(f"❌ 词汇记忆系统测试失败: {e}")
            self.test_results["vocabulary_memory"] = False

    async def _test_vocabulary_direct(self, test_vocabulary):
        """直接数据库测试词汇系统"""
        print("📍 使用直接数据库测试词汇系统...")

        try:
            import asyncpg

            connection = await asyncpg.connect(
                "postgresql://user:password@localhost:5432/japanese_learning"
            )

            vocab_ids = []

            # 添加词汇
            for vocab in test_vocabulary:
                vocab_id = str(uuid.uuid4())
                await connection.execute("""
                    INSERT INTO vocabulary_progress (vocab_id, user_id, word, reading, meaning, difficulty_level, next_review)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, vocab_id, self.test_user_id, vocab["word"], vocab["reading"],
                                         vocab["meaning"], vocab["difficulty"], date.today())

                vocab_ids.append(vocab_id)
                self.test_data_cleanup.append(("vocabulary_direct", vocab_id))

            print(f"   - ✅ 直接添加 {len(vocab_ids)} 个词汇")

            # 模拟复习
            for i, vocab_id in enumerate(vocab_ids):
                is_correct = i < 3  # 前3个正确，后面错误
                times_correct = 1 if is_correct else 0
                mastery_score = 0.8 if is_correct else 0.3

                await connection.execute("""
                    UPDATE vocabulary_progress 
                    SET times_reviewed = times_reviewed + 1, 
                        times_correct = times_correct + $2,
                        mastery_score = $3,
                        next_review = $4
                    WHERE vocab_id = $1
                """, vocab_id, times_correct, mastery_score,
                                         date.today() + timedelta(days=1 if is_correct else 0))

            print("   - ✅ 模拟复习记录更新完成")

            # 查询待复习词汇
            due_vocab = await connection.fetch("""
                SELECT word, reading, meaning FROM vocabulary_progress 
                WHERE user_id = $1 AND next_review <= $2
            """, self.test_user_id, date.today())

            print(f"   - ✅ 查询到 {len(due_vocab)} 个待复习词汇")

            await connection.close()
            self.test_results["vocabulary_memory_direct"] = True

        except Exception as e:
            print(f"❌ 直接数据库词汇测试失败: {e}")
            self.test_results["vocabulary_memory_direct"] = False

    async def test_membot_review_system(self):
        """测试MemBot智能复习提醒系统"""
        print("\n🔍 测试MemBot智能复习提醒系统...")

        if not self.test_user_id:
            print("❌ 无法测试MemBot：测试用户未创建")
            self.test_results["membot_review"] = False
            return

        try:
            # 获取MemBot智能体
            from src.core.agents.core_agents import get_agent

            membot = get_agent("membot")

            # 测试场景1：生成复习计划
            print("\n   场景1：生成个性化复习计划")

            session_context = {
                "user_id": self.test_user_id,
                "session_id": "membot_review_test",
                "scene": "review_planning",
                "history": []
            }

            review_request = "请帮我制定今天的复习计划，我想重点复习语法和词汇"

            response = await membot.process_user_input(
                user_input=review_request,
                session_context=session_context,
                scene="review_planning"
            )

            assert response.get("content"), "MemBot必须提供复习计划内容"
            print(f"   - ✅ MemBot复习计划: {response['content'][:100]}...")

            # 测试场景2：复习提醒
            print("\n   场景2：智能复习提醒")

            reminder_request = "提醒我需要复习的内容"

            reminder_response = await membot.process_user_input(
                user_input=reminder_request,
                session_context=session_context,
                scene="review_reminder"
            )

            assert reminder_response.get("content"), "MemBot必须提供复习提醒"
            print(f"   - ✅ MemBot复习提醒: {reminder_response['content'][:100]}...")

            # 测试场景3：学习进度分析
            print("\n   场景3：学习进度分析")

            analysis_request = "分析我的学习进度，告诉我哪些地方需要加强"

            analysis_response = await membot.process_user_input(
                user_input=analysis_request,
                session_context=session_context,
                scene="progress_analysis"
            )

            assert analysis_response.get("content"), "MemBot必须提供学习分析"
            print(f"   - ✅ MemBot学习分析: {analysis_response['content'][:100]}...")

            # 测试场景4：间隔重复算法建议
            print("\n   场景4：间隔重复算法建议")

            spaced_repetition_request = "根据遗忘曲线，建议我的复习间隔"

            algorithm_response = await membot.process_user_input(
                user_input=spaced_repetition_request,
                session_context=session_context,
                scene="spaced_repetition"
            )

            assert algorithm_response.get("content"), "MemBot必须提供间隔重复建议"
            print(f"   - ✅ MemBot间隔建议: {algorithm_response['content'][:100]}...")

            # 验证MemBot的记忆功能是否正常工作
            learning_points = []
            for response in [response, reminder_response, analysis_response, algorithm_response]:
                if response.get("learning_points"):
                    learning_points.extend(response["learning_points"])

            if learning_points:
                print(f"   - ✅ MemBot记录了 {len(learning_points)} 个学习点")
            else:
                print("   - ⚠️  MemBot未记录学习点")

            self.test_results["membot_review"] = True

        except Exception as e:
            print(f"❌ MemBot复习系统测试失败: {e}")
            self.test_results["membot_review"] = False

    async def test_conversation_persistence(self):
        """测试对话历史持久化"""
        print("\n🔍 测试对话历史持久化...")

        if not self.test_user_id:
            print("❌ 无法测试对话持久化：测试用户未创建")
            self.test_results["conversation_persistence"] = False
            return

        try:
            # 模拟一个完整的学习对话会话
            from core.agents import get_agent

            agents_to_test = ["tanaka", "koumi", "ai"]
            conversation_records = []

            session_id = str(uuid.uuid4())
            self.test_data_cleanup.append(("session", session_id))

            test_conversation = [
                {"input": "私は昨日図書館に行きました", "expected_agent": "tanaka"},
                {"input": "もっと自然な表現を教えて", "expected_agent": "koumi"},
                {"input": "私の学習進度を分析して", "expected_agent": "ai"}
            ]

            for i, conv in enumerate(test_conversation):
                agent = get_agent(agents_to_test[i])

                session_context = {
                    "user_id": self.test_user_id,
                    "session_id": session_id,
                    "scene": "learning_conversation",
                    "history": conversation_records
                }

                response = await agent.process_user_input(
                    user_input=conv["input"],
                    session_context=session_context,
                    scene="learning_conversation"
                )

                # 记录对话
                conversation_record = {
                    "user_input": conv["input"],
                    "agent_response": response.get("content", ""),
                    "agent_name": response.get("agent_name", ""),
                    "learning_points": response.get("learning_points", []),
                    "timestamp": datetime.now()
                }

                conversation_records.append(conversation_record)
                print(f"   - ✅ 记录对话 {i + 1}: {conv['input']}")

            # 测试对话历史存储（如果有相应的服务）
            try:
                from backend.services.conversation_service import ConversationService

                conv_service = ConversationService()

                conversation_id = await conv_service.save_conversation(
                    session_id=session_id,
                    user_id=self.test_user_id,
                    conversation_records=conversation_records
                )

                self.test_data_cleanup.append(("conversation", conversation_id))
                print(f"   - ✅ 对话历史保存成功: {conversation_id}")

                # 测试对话历史检索
                retrieved_history = await conv_service.get_conversation_history(
                    user_id=self.test_user_id,
                    session_id=session_id
                )

                assert len(retrieved_history) == len(conversation_records), "检索的对话记录数量不匹配"
                print(f"   - ✅ 对话历史检索成功: {len(retrieved_history)} 条记录")

            except ImportError:
                print("   - ⚠️  对话服务未找到，跳过持久化存储测试")

            # 验证对话连续性
            if len(conversation_records) >= 2:
                print("   - ✅ 对话连续性测试通过")
                self.test_results["conversation_persistence"] = True
            else:
                print("   - ❌ 对话连续性不足")
                self.test_results["conversation_persistence"] = False

        except Exception as e:
            print(f"❌ 对话历史持久化测试失败: {e}")
            self.test_results["conversation_persistence"] = False

    async def test_data_analytics_integration(self):
        """测试数据分析集成"""
        print("\n🔍 测试数据分析集成...")

        if not self.test_user_id:
            print("❌ 无法测试数据分析：测试用户未创建")
            self.test_results["data_analytics"] = False
            return

        try:
            # 使用AI分析师测试数据分析功能
            from core.agents import get_agent

            ai_analyzer = get_agent("ai")

            # 场景1：学习数据分析
            print("\n   场景1：学习数据分析")

            session_context = {
                "user_id": self.test_user_id,
                "session_id": "analytics_test",
                "scene": "data_analysis",
                "history": []
            }

            analysis_request = "分析我的整体学习情况，包括强项和弱项"

            analysis_response = await ai_analyzer.process_user_input(
                user_input=analysis_request,
                session_context=session_context,
                scene="data_analysis"
            )

            assert analysis_response.get("content"), "AI分析师必须提供分析结果"
            print(f"   - ✅ 学习数据分析: {analysis_response['content'][:100]}...")

            # 场景2：个性化推荐
            print("\n   场景2：个性化推荐生成")

            recommendation_request = "根据我的学习数据，推荐下一步学习内容"

            rec_response = await ai_analyzer.process_user_input(
                user_input=recommendation_request,
                session_context=session_context,
                scene="recommendation"
            )

            assert rec_response.get("content"), "AI分析师必须提供推荐内容"
            print(f"   - ✅ 个性化推荐: {rec_response['content'][:100]}...")

            # 场景3：学习效果预测
            print("\n   场景3：学习效果预测")

            prediction_request = "预测我达到N4水平需要多长时间"

            prediction_response = await ai_analyzer.process_user_input(
                user_input=prediction_request,
                session_context=session_context,
                scene="prediction"
            )

            assert prediction_response.get("content"), "AI分析师必须提供预测结果"
            print(f"   - ✅ 学习效果预测: {prediction_response['content'][:100]}...")

            self.test_results["data_analytics"] = True

        except Exception as e:
            print(f"❌ 数据分析集成测试失败: {e}")
            self.test_results["data_analytics"] = False

    async def cleanup_test_data(self):
        """清理测试数据"""
        print("\n🧹 清理测试数据...")

        if not self.test_data_cleanup:
            print("   - 无需清理的测试数据")
            return

        try:
            import asyncpg

            connection = await asyncpg.connect(
                "postgresql://user:password@localhost:5432/japanese_learning"
            )

            cleanup_count = 0

            for data_type, data_id in self.test_data_cleanup:
                try:
                    if data_type == "user" or data_type == "user_direct":
                        await connection.execute("DELETE FROM users WHERE user_id = $1", data_id)
                    elif data_type == "progress" or data_type == "progress_direct":
                        await connection.execute("DELETE FROM learning_progress WHERE progress_id = $1", data_id)
                    elif data_type == "vocabulary" or data_type == "vocabulary_direct":
                        await connection.execute("DELETE FROM vocabulary_progress WHERE vocab_id = $1", data_id)
                    elif data_type == "conversation":
                        await connection.execute("DELETE FROM conversation_history WHERE conversation_id = $1", data_id)
                    elif data_type == "session":
                        await connection.execute("DELETE FROM conversation_history WHERE session_id = $1", data_id)

                    cleanup_count += 1

                except Exception as e:
                    print(f"   - ⚠️  清理 {data_type} {data_id} 失败: {e}")

            await connection.close()
            print(f"   - ✅ 成功清理 {cleanup_count} 项测试数据")

        except Exception as e:
            print(f"   - ❌ 测试数据清理失败: {e}")

    def generate_persistence_report(self):
        """生成持久化测试报告"""
        print("\n📊 数据持久化功能测试报告")
        print("=" * 50)

        test_categories = {
            "learning_progress": "学习进度跟踪",
            "vocabulary_memory": "词汇记忆系统",
            "membot_review": "MemBot复习提醒",
            "conversation_persistence": "对话历史持久化",
            "data_analytics": "数据分析集成"
        }

        passed = 0
        failed = 0

        for test_key, description in test_categories.items():
            # 检查是否有该类别的测试结果（包括direct版本）
            category_results = [v for k, v in self.test_results.items() if test_key in k]

            if category_results:
                success = any(result is True for result in category_results)
                status = "✅ 通过" if success else "❌ 失败"

                if success:
                    passed += 1
                else:
                    failed += 1
            else:
                status = "⚠️  未测试"

            print(f"{description:<20} {status}")

        print(f"\n功能模块通过情况:")
        print(f"✅ 通过: {passed}")
        print(f"❌ 失败: {failed}")

        overall_success = failed == 0 and passed > 0

        if overall_success:
            print("\n🎉 数据持久化功能测试通过！")
        elif failed > 0:
            print(f"\n⚠️  有 {failed} 个功能模块测试失败")
        else:
            print("\n❌ 未能执行任何持久化功能测试")

        return overall_success

    async def run_all_tests(self):
        """运行所有持久化测试"""
        print("🚀 开始数据持久化功能测试...\n")

        # 设置测试环境
        setup_success = await self.setup_test_user()
        if not setup_success:
            print("❌ 测试环境设置失败，无法继续测试")
            return False

        try:
            # 运行各项测试
            await self.test_learning_progress_tracking()
            await self.test_vocabulary_memory_system()
            await self.test_membot_review_system()
            await self.test_conversation_persistence()
            await self.test_data_analytics_integration()

            return self.generate_persistence_report()

        finally:
            # 清理测试数据
            await self.cleanup_test_data()


# 运行测试
async def main():
    tester = PersistenceTester()
    success = await tester.run_all_tests()

    if success:
        print("\n✅ 数据持久化功能测试通过 - 可以进行端到端集成测试")
    else:
        print("\n⚠️  数据持久化功能测试发现问题 - 建议修复后再进行集成测试")


if __name__ == "__main__":
    asyncio.run(main())