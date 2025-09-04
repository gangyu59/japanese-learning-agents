#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据持久化功能测试（SQLite 版、无 Postgres 依赖）
- 用户创建/查询（用随机邮箱/用户名，避免 UNIQUE 冲突）
- 学习进度跟踪（learning_progress）
- 词汇记忆（vocabulary_progress）
"""
import asyncio
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os, uuid

DB_PATH = "./japanese_learning.db"

class PersistenceTester:
    def __init__(self):
        self.test_results: Dict[str, bool] = {}
        self.test_user_id: Optional[str] = None

    async def setup_test_user(self) -> bool:
        conn = sqlite3.connect(DB_PATH)
        try:
            # users 表（只保证测试字段足够用）
            conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                password_hash TEXT,
                learning_level TEXT,
                target_jlpt_level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")

            self.test_user_id = str(uuid.uuid4())
            # 避免 UNIQUE 冲突：随机化用户名/邮箱
            uname = f"persistence_{uuid.uuid4().hex[:8]}"
            email = f"{uname}@example.com"

            conn.execute("""
                INSERT INTO users (user_id, username, email, password_hash, learning_level, target_jlpt_level)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.test_user_id, uname, email, "test_hash", "beginner", "N5"))
            conn.commit()
            print(f"✅ 测试用户创建成功: {self.test_user_id}")
            return True
        finally:
            conn.close()

    async def test_learning_progress_tracking(self):
        print("\n🔍 测试学习进度跟踪功能.")
        if not self.test_user_id:
            print("❌ 无法测试学习进度：测试用户未创建")
            self.test_results["learning_progress"] = False
            return

        conn = sqlite3.connect(DB_PATH)
        try:
            # learning_progress 结构（加入 grammar_point / progress_id / last_reviewed）
            conn.execute("""
            CREATE TABLE IF NOT EXISTS learning_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                grammar_point TEXT,
                mastery_level REAL DEFAULT 0.0,
                practice_count INTEGER DEFAULT 0,
                progress_id TEXT,
                last_reviewed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_learning_progress_pid ON learning_progress(progress_id)")

            cases = [
                ("は/が particle", 0.3),
                ("past tense verbs", 0.6),
                ("keigo expressions", 0.1),
            ]
            pids: List[str] = []
            for gp, init in cases:
                pid = str(uuid.uuid4())
                conn.execute("""
                INSERT INTO learning_progress (user_id, grammar_point, mastery_level, practice_count, progress_id)
                VALUES (?, ?, ?, ?, ?)
                """, (self.test_user_id, gp, init, 1, pid))
                pids.append(pid)
            conn.commit()
            print(f"   - ✅ 创建进度记录: {len(pids)} 条")

            # 更新
            for pid in pids:
                conn.execute("""
                UPDATE learning_progress
                SET mastery_level = MIN(mastery_level + 0.2, 1.0),
                    practice_count = practice_count + 1,
                    last_reviewed = CURRENT_TIMESTAMP
                WHERE progress_id = ?
                """, (pid,))
            conn.commit()
            print("   - ✅ 进度更新成功")

            # 查询
            cur = conn.execute(
                "SELECT grammar_point, mastery_level, practice_count FROM learning_progress WHERE user_id = ?",
                (self.test_user_id,)
            )
            rows = cur.fetchall()
            assert len(rows) >= len(cases), "进度记录数量不足"
            print(f"   - ✅ 进度查询成功: {len(rows)} 条记录")

            self.test_results["learning_progress"] = True
        except Exception as e:
            print(f"❌ 学习进度跟踪测试失败: {e}")
            self.test_results["learning_progress"] = False
        finally:
            conn.close()

    async def test_vocabulary_memory(self):
        print("\n🔍 测试词汇记忆功能.")
        conn = sqlite3.connect(DB_PATH)
        try:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS vocabulary_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                word TEXT,
                proficiency REAL DEFAULT 0.0,
                review_due TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                progress_id TEXT
            )""")
            words = ["面白い", "大切", "静か", "美しい", "簡単"]
            due = (datetime.utcnow() + timedelta(days=1)).isoformat()
            for w in words:
                conn.execute("""
                INSERT INTO vocabulary_progress (user_id, word, proficiency, review_due, progress_id)
                VALUES (?, ?, ?, ?, ?)
                """, (self.test_user_id, w, 0.3, due, str(uuid.uuid4())))
            conn.commit()
            print(f"   - ✅ 插入词汇记录: {len(words)} 条")

            # 简单“记忆强化”：+0.2
            conn.execute("""
            UPDATE vocabulary_progress
            SET proficiency = MIN(proficiency + 0.2, 1.0),
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
            """, (self.test_user_id,))
            conn.commit()
            print("   - ✅ 词汇熟练度提升成功")
            self.test_results["vocabulary_memory"] = True
        except Exception as e:
            print(f"❌ 词汇记忆测试失败: {e}")
            self.test_results["vocabulary_memory"] = False
        finally:
            conn.close()

    async def run_all_tests(self) -> bool:
        ok = await self.setup_test_user()
        if not ok:
            return False
        await self.test_learning_progress_tracking()
        await self.test_vocabulary_memory()
        all_ok = all(self.test_results.get(k, False) for k in self.test_results)
        status = "✅ 通过" if all_ok else "❌ 失败"
        print(f"\n📊 持久化测试汇总: {status} -> {self.test_results}")
        return all_ok

if __name__ == "__main__":
    asyncio.run(PersistenceTester().run_all_tests())
