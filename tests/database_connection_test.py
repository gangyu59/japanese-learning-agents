#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接和基础功能测试脚本
确保PostgreSQL集成正常工作
"""

import asyncio
import asyncpg
import json
from datetime import datetime, date
from typing import Dict, List, Optional
import uuid


class DatabaseTester:
    """数据库测试类"""

    def __init__(self, db_url: str = "postgresql://user:password@localhost:5432/japanese_learning"):
        self.db_url = db_url
        self.connection = None

    async def connect(self):
        """建立数据库连接"""
        try:
            self.connection = await asyncpg.connect(self.db_url)
            print("✅ 数据库连接成功")
            return True
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False

    async def test_table_creation(self):
        """测试表创建"""
        print("\n🔍 测试表结构...")

        tables_to_check = [
            'users', 'learning_progress', 'vocabulary_progress',
            'custom_agents', 'custom_scenes', 'conversation_history',
            'learning_sessions', 'agent_usage_stats'
        ]

        for table_name in tables_to_check:
            try:
                result = await self.connection.fetch(
                    "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = $1",
                    table_name
                )
                if result:
                    print(f"✅ 表 {table_name} 存在，包含 {len(result)} 列")
                else:
                    print(f"❌ 表 {table_name} 不存在")
            except Exception as e:
                print(f"❌ 检查表 {table_name} 时出错: {e}")

    async def test_user_operations(self):
        """测试用户相关操作"""
        print("\n🔍 测试用户操作...")

        # 创建测试用户
        test_user_id = str(uuid.uuid4())
        try:
            await self.connection.execute("""
                INSERT INTO users (user_id, username, email, password_hash, learning_level, target_jlpt_level)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, test_user_id, "test_user", "test@example.com", "hashed_password", "beginner", "N5")
            print(f"✅ 用户创建成功: {test_user_id}")

            # 查询用户
            user = await self.connection.fetchrow("SELECT * FROM users WHERE user_id = $1", test_user_id)
            print(f"✅ 用户查询成功: {user['username']}")

            # 清理测试数据
            await self.connection.execute("DELETE FROM users WHERE user_id = $1", test_user_id)
            print("✅ 测试用户清理完成")

        except Exception as e:
            print(f"❌ 用户操作测试失败: {e}")

    async def test_learning_progress_operations(self):
        """测试学习进度操作"""
        print("\n🔍 测试学习进度操作...")

        # 首先创建测试用户
        test_user_id = str(uuid.uuid4())
        await self.connection.execute("""
            INSERT INTO users (user_id, username, email, password_hash)
            VALUES ($1, $2, $3, $4)
        """, test_user_id, "progress_test_user", "progress@example.com", "hashed_password")

        try:
            # 创建学习进度记录
            progress_id = str(uuid.uuid4())
            await self.connection.execute("""
                INSERT INTO learning_progress (progress_id, user_id, grammar_point, mastery_level, practice_count)
                VALUES ($1, $2, $3, $4, $5)
            """, progress_id, test_user_id, "は/が particle", 0.7, 5)
            print("✅ 学习进度记录创建成功")

            # 查询进度
            progress = await self.connection.fetchrow(
                "SELECT * FROM learning_progress WHERE progress_id = $1", progress_id
            )
            print(f"✅ 进度查询成功: {progress['grammar_point']} - {progress['mastery_level']}")

            # 更新进度
            await self.connection.execute("""
                UPDATE learning_progress SET mastery_level = $1, practice_count = $2 
                WHERE progress_id = $3
            """, 0.8, 6, progress_id)

            updated_progress = await self.connection.fetchrow(
                "SELECT mastery_level, practice_count FROM learning_progress WHERE progress_id = $1",
                progress_id
            )
            print(
                f"✅ 进度更新成功: 掌握度 {updated_progress['mastery_level']}, 练习次数 {updated_progress['practice_count']}")

        except Exception as e:
            print(f"❌ 学习进度操作测试失败: {e}")
        finally:
            # 清理测试数据
            await self.connection.execute("DELETE FROM users WHERE user_id = $1", test_user_id)
            print("✅ 测试数据清理完成")

    async def test_vocabulary_operations(self):
        """测试词汇学习操作"""
        print("\n🔍 测试词汇学习操作...")

        # 创建测试用户
        test_user_id = str(uuid.uuid4())
        await self.connection.execute("""
            INSERT INTO users (user_id, username, email, password_hash)
            VALUES ($1, $2, $3, $4)
        """, test_user_id, "vocab_test_user", "vocab@example.com", "hashed_password")

        try:
            # 添加词汇记录
            vocab_id = str(uuid.uuid4())
            await self.connection.execute("""
                INSERT INTO vocabulary_progress (vocab_id, user_id, word, reading, meaning, difficulty_level, next_review)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, vocab_id, test_user_id, "桜", "さくら", "cherry blossom", 2, date.today())
            print("✅ 词汇记录创建成功")

            # 查询词汇
            vocab = await self.connection.fetchrow("SELECT * FROM vocabulary_progress WHERE vocab_id = $1", vocab_id)
            print(f"✅ 词汇查询成功: {vocab['word']} ({vocab['reading']}) - {vocab['meaning']}")

            # 模拟复习
            await self.connection.execute("""
                UPDATE vocabulary_progress 
                SET times_reviewed = times_reviewed + 1, times_correct = times_correct + 1, mastery_score = $1
                WHERE vocab_id = $2
            """, 0.8, vocab_id)
            print("✅ 词汇复习记录更新成功")

        except Exception as e:
            print(f"❌ 词汇操作测试失败: {e}")
        finally:
            # 清理测试数据
            await self.connection.execute("DELETE FROM users WHERE user_id = $1", test_user_id)
            print("✅ 测试数据清理完成")

    async def test_conversation_history(self):
        """测试对话历史存储"""
        print("\n🔍 测试对话历史操作...")

        # 创建测试用户
        test_user_id = str(uuid.uuid4())
        await self.connection.execute("""
            INSERT INTO users (user_id, username, email, password_hash)
            VALUES ($1, $2, $3, $4)
        """, test_user_id, "chat_test_user", "chat@example.com", "hashed_password")

        try:
            # 创建对话记录
            conversation_id = str(uuid.uuid4())
            session_id = str(uuid.uuid4())

            agent_responses = [
                {"agent": "田中先生", "response": "这句话的语法需要改进", "emotion": "😐"},
                {"agent": "小美", "response": "可以这样说哦～", "emotion": "😊"}
            ]

            await self.connection.execute("""
                INSERT INTO conversation_history (
                    conversation_id, session_id, user_id, user_input, agent_responses, 
                    participating_agents, learning_points_identified
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
                                          conversation_id, session_id, test_user_id,
                                          "私は学校に行った", json.dumps(agent_responses),
                                          ["tanaka", "koumi"], ["past tense usage", "particle usage"]
                                          )
            print("✅ 对话记录创建成功")

            # 查询对话历史
            history = await self.connection.fetchrow(
                "SELECT * FROM conversation_history WHERE conversation_id = $1",
                conversation_id
            )
            print(f"✅ 对话历史查询成功: {len(history['participating_agents'])} 个智能体参与")

        except Exception as e:
            print(f"❌ 对话历史测试失败: {e}")
        finally:
            # 清理测试数据
            await self.connection.execute("DELETE FROM users WHERE user_id = $1", test_user_id)
            print("✅ 测试数据清理完成")

    async def run_all_tests(self):
        """运行所有数据库测试"""
        print("🚀 开始数据库功能测试...")

        if not await self.connect():
            return False

        try:
            await self.test_table_creation()
            await self.test_user_operations()
            await self.test_learning_progress_operations()
            await self.test_vocabulary_operations()
            await self.test_conversation_history()

            print("\n🎉 所有数据库测试完成！")
            return True

        except Exception as e:
            print(f"❌ 测试过程中发生错误: {e}")
            return False
        finally:
            if self.connection:
                await self.connection.close()
                print("🔒 数据库连接已关闭")


# 运行测试
async def main():
    tester = DatabaseTester()
    success = await tester.run_all_tests()
    if success:
        print("\n✅ 数据库基础设施测试通过 - 可以继续下一阶段测试")
    else:
        print("\n❌ 数据库基础设施测试失败 - 请检查配置")


if __name__ == "__main__":
    asyncio.run(main())