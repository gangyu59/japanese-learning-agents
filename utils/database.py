#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎌 数据库管理工具
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_path: str = "japanese_learning.db"):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None

    async def connect(self):
        """连接数据库"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # 使结果可以通过列名访问
            logger.info(f"✅ 数据库连接成功: {self.db_path}")
        except Exception as e:
            logger.error(f"❌ 数据库连接失败: {e}")
            raise

    async def create_tables(self):
        """创建数据表"""
        if not self.connection:
            await self.connect()

        cursor = self.connection.cursor()

        # 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                learning_level TEXT DEFAULT 'beginner',
                target_jlpt_level TEXT,
                daily_goal INTEGER DEFAULT 30
            )
        ''')

        # 学习会话表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                scene TEXT DEFAULT 'grammar',
                active_agents TEXT,
                message_count INTEGER DEFAULT 0,
                duration_minutes INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # 对话历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                user_input TEXT,
                agent_responses TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                scene TEXT,
                FOREIGN KEY (session_id) REFERENCES learning_sessions (session_id)
            )
        ''')

        # 学习进度表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                grammar_mastery REAL DEFAULT 0.0,
                vocabulary_count INTEGER DEFAULT 0,
                culture_understanding REAL DEFAULT 0.0,
                total_study_time INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # 自定义智能体表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_agents (
                agent_id TEXT PRIMARY KEY,
                created_by TEXT,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                avatar TEXT DEFAULT '🤖',
                personality_config TEXT,
                expertise_areas TEXT,
                is_public BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (user_id)
            )
        ''')

        # 自定义场景表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_scenes (
                scene_id TEXT PRIMARY KEY,
                created_by TEXT,
                name TEXT NOT NULL,
                description TEXT,
                learning_objectives TEXT,
                difficulty TEXT DEFAULT 'beginner',
                recommended_agents TEXT,
                is_public BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (user_id)
            )
        ''')

        # 成就记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                achievement_id TEXT,
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        self.connection.commit()
        logger.info("✅ 数据表创建完成")

    async def insert_sample_data(self):
        """插入示例数据"""
        if not self.connection:
            await self.connect()

        cursor = self.connection.cursor()

        # 示例用户
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, email, learning_level, target_jlpt_level)
            VALUES ('demo_user', 'demo', 'demo@example.com', 'beginner', 'N5')
        ''')

        # 示例学习进度
        cursor.execute('''
            INSERT OR IGNORE INTO learning_progress (user_id, grammar_mastery, vocabulary_count, culture_understanding)
            VALUES ('demo_user', 0.65, 1250, 0.40)
        ''')

        self.connection.commit()
        logger.info("✅ 示例数据插入完成")

    async def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("🛑 数据库连接已关闭")


# 全局数据库管理器实例
db_manager = DatabaseManager()


async def init_database():
    """初始化数据库"""
    try:
        await db_manager.connect()
        await db_manager.create_tables()
        await db_manager.insert_sample_data()
        logger.info("🎉 数据库初始化完成")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise


async def get_database():
    """获取数据库连接"""
    if not db_manager.connection:
        await db_manager.connect()
    return db_manager.connection