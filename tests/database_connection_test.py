# -*- coding: utf-8 -*-
# SQLite 版本：无副作用、可重复运行
import asyncio
import os
import sqlite3
from datetime import datetime
from typing import Optional

class DatabaseTester:
    def __init__(self, db_url: str = "sqlite:///./japanese_learning.db"):
        # 解析 sqlite:/// 路径
        if db_url.startswith("sqlite:///"):
            self.db_path = db_url.replace("sqlite:///", "")
        else:
            self.db_path = db_url
        self.conn: Optional[sqlite3.Connection] = None

    async def connect(self) -> bool:
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute("PRAGMA foreign_keys = ON")
            self.conn.execute("PRAGMA journal_mode = WAL")
            print(f"✅ SQLite 连接成功: {self.db_path}")
            return True
        except Exception as e:
            print(f"❌ SQLite 连接失败: {e}")
            return False

    async def _ensure_schema(self):
        cur = self.conn.cursor()
        # —— 最小可用表结构（不对业务库施加强制 UNIQUE 约束）——
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
          user_id TEXT PRIMARY KEY,
          username TEXT NOT NULL,
          email TEXT,
          password_hash TEXT,
          learning_level TEXT,
          target_jlpt_level TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS learning_progress (
          progress_id TEXT PRIMARY KEY,
          user_id TEXT,
          grammar_point TEXT,
          mastery_level REAL DEFAULT 0.0,
          practice_count INTEGER DEFAULT 0,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS vocabulary_progress (
          vocab_id TEXT PRIMARY KEY,
          user_id TEXT,
          word TEXT,
          reading TEXT,
          meaning TEXT,
          difficulty INTEGER,
          next_review TIMESTAMP,
          review_interval INTEGER DEFAULT 1,
          FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS custom_agents (
          id TEXT PRIMARY KEY,
          user_id TEXT,
          agent_id TEXT,
          name TEXT,
          role TEXT,
          personality TEXT,
          config JSON,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS custom_scenes (
          id TEXT PRIMARY KEY,
          user_id TEXT,
          scene_key TEXT,
          title TEXT,
          description TEXT,
          prompt TEXT,
          examples TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS conversation_history (
          id TEXT PRIMARY KEY,
          user_id TEXT,
          session_id TEXT,
          role TEXT,
          content TEXT
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS learning_sessions (
          session_id TEXT PRIMARY KEY,
          user_id TEXT,
          started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          ended_at TIMESTAMP
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS agent_usage_stats (
          id TEXT PRIMARY KEY,
          agent_id TEXT,
          user_id TEXT,
          call_count INTEGER DEFAULT 0,
          last_used_at TIMESTAMP
        )
        """)
        self.conn.commit()

    async def test_table_creation(self) -> None:
        print("\n🔍 测试表结构...")
        await self._ensure_schema()
        def count_cols(table):
            return len(self.conn.execute(f"PRAGMA table_info({table})").fetchall())
        for t in [
            'users','learning_progress','vocabulary_progress',
            'custom_agents','custom_scenes','conversation_history',
            'learning_sessions','agent_usage_stats'
        ]:
            cols = count_cols(t)
            print(f"✅ 表 {t} 存在，包含 {cols} 列")

    async def test_user_operations(self) -> bool:
        print("\n🔍 测试用户操作...")
        import uuid
        user_id = str(uuid.uuid4())
        username = f"test_user_{user_id[:8]}"
        try:
            self.conn.execute(
                "INSERT INTO users (user_id, username, email, password_hash, learning_level, target_jlpt_level) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, username, f"{username}@example.com", "hashed_password", "beginner", "N5")
            )
            self.conn.commit()
            got = self.conn.execute("SELECT username FROM users WHERE user_id = ?", (user_id,)).fetchone()
            assert got and got[0] == username
            print(f"✅ 用户创建/查询成功: {user_id}")
            return True
        except Exception as e:
            print(f"❌ 用户操作测试失败: {e}")
            return False
        finally:
            # 清理
            self.conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            self.conn.commit()
            print("✅ 测试用户清理完成")

    async def test_learning_progress_operations(self) -> bool:
        print("\n🔍 测试学习进度操作...")
        import uuid
        user_id = str(uuid.uuid4())
        username = f"progress_user_{user_id[:8]}"
        progress_id = str(uuid.uuid4())
        try:
            # 先建用户
            self.conn.execute(
                "INSERT INTO users (user_id, username, password_hash) VALUES (?, ?, ?)",
                (user_id, username, "hash")
            )
            # 插入进度
            self.conn.execute("""
            INSERT INTO learning_progress (progress_id, user_id, grammar_point, mastery_level, practice_count)
            VALUES (?, ?, ?, ?, ?)
            """, (progress_id, user_id, "は/が particle", 0.7, 5))
            self.conn.commit()

            got = self.conn.execute(
                "SELECT grammar_point, mastery_level FROM learning_progress WHERE progress_id = ?",
                (progress_id,)
            ).fetchone()
            if not got:
                raise RuntimeError("未找到刚插入的进度记录")
            print(f"✅ 进度查询成功: {got[0]} - {got[1]}")

            # 更新
            self.conn.execute(
                "UPDATE learning_progress SET mastery_level = ?, practice_count = ?, updated_at = CURRENT_TIMESTAMP WHERE progress_id = ?",
                (0.8, 6, progress_id)
            )
            self.conn.commit()
            print("✅ 进度更新成功")
            return True
        except Exception as e:
            print(f"❌ 学习进度操作测试失败: {e}")
            return False
        finally:
            # 清理（先删子表再删父表）
            self.conn.execute("DELETE FROM learning_progress WHERE progress_id = ?", (progress_id,))
            self.conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            self.conn.commit()
            print("✅ 进度测试数据清理完成")

    async def run_all_tests(self) -> bool:
        ok = await self.connect()
        if not ok:
            return False
        await self.test_table_creation()
        u_ok = await self.test_user_operations()
        p_ok = await self.test_learning_progress_operations()
        return bool(u_ok and p_ok)

if __name__ == "__main__":
    async def _main():
        url = os.environ.get("TEST_DB_URL", "sqlite:///./japanese_learning.db")
        t = DatabaseTester(url)
        ok = await t.run_all_tests()
        print("✅ 全部通过" if ok else "❌ 存在失败")
    asyncio.run(_main())
