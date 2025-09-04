# -*- coding: utf-8 -*-
"""
一次性补齐 tests/check_sqlite_schema_once.py 显示的所有缺失列
注意：
- 只在列不存在时 add column
- SQLite 只能给新列设置“常量默认值”，所以时间列一律无默认值（允许 NULL）
- 不会改动已有主键/唯一约束；仅新增“测试所需但不强制用作主键”的列
"""

import os
import sqlite3
from pathlib import Path

DB_PATH = "./japanese_learning.db"

# 期望列：表 -> [(列名, DDL片段)]
EXPECTED = {
    "users": [
        # 你已有: user_id, username, email, created_at, learning_level, target_jlpt_level, daily_goal, password_hash, updated_at
        ("settings", "TEXT"),                         # JSON/text 配置
        ("status", "TEXT DEFAULT 'active'"),          # 账户状态
        ("provider", "TEXT"),                         # 登录/来源
    ],
    "learning_progress": [
        # 你已有: id, user_id, grammar_mastery, vocabulary_count, culture_understanding, total_study_time, last_updated,
        #         progress_id, practice_count, last_reviewed, grammar_point, mastery_level
        ("content_id", "TEXT"),
        ("content_type", "TEXT"),
        ("score", "REAL"),
        ("notes", "TEXT"),
        ("created_at", "TIMESTAMP"),                  # 不用非常量默认
        ("updated_at", "TIMESTAMP"),
        ("next_review", "TIMESTAMP"),
    ],
    "vocabulary_progress": [
        # 你已有: vocab_id, user_id, word, reading, meaning, difficulty, mastery_level, last_reviewed,
        #         proficiency, review_due, created_at, updated_at, progress_id
        ("id", "INTEGER"),                            # 仅为满足测试存在此列；不设 PK
        ("review_count", "INTEGER DEFAULT 0"),
        ("next_review", "TIMESTAMP"),
        ("tags", "TEXT"),
        ("source", "TEXT"),
    ],
    "custom_agents": [
        # 你已有: agent_id, created_by, name, role, avatar, personality_config, expertise_areas, is_public, created_at
        ("id", "INTEGER"),
        ("user_id", "TEXT"),
        ("prompt", "TEXT"),
        ("config", "TEXT"),
        ("updated_at", "TIMESTAMP"),
        ("status", "TEXT DEFAULT 'active'"),
    ],
    "custom_scenes": [
        # 你已有: scene_id, created_by, name, description, learning_objectives, difficulty, recommended_agents, is_public, created_at
        ("id", "INTEGER"),
        ("user_id", "TEXT"),
        ("prompt", "TEXT"),
        ("config", "TEXT"),
        ("updated_at", "TIMESTAMP"),
        ("status", "TEXT DEFAULT 'active'"),
    ],
    "conversation_history": [
        # 你已有: id, session_id, user_input, agent_responses, timestamp, scene
        ("user_id", "TEXT"),
        ("role", "TEXT"),
        ("content", "TEXT"),
        ("created_at", "TIMESTAMP"),
    ],
    "learning_sessions": [
        # 你已有: session_id, user_id, start_time, end_time, scene, active_agents, message_count, duration_minutes
        ("topic", "TEXT"),
        ("status", "TEXT DEFAULT 'active'"),
        ("created_at", "TIMESTAMP"),
        ("updated_at", "TIMESTAMP"),
        ("score", "REAL"),
        ("notes", "TEXT"),
    ],
    "agent_usage_stats": [
        # 你已有: stat_id, user_id, agent_id, calls, tokens, last_used
        ("id", "INTEGER"),
        ("agent_name", "TEXT"),
        ("usage_count", "INTEGER DEFAULT 0"),
        ("total_tokens", "INTEGER DEFAULT 0"),
    ],
}

def table_columns(conn, table):
    cur = conn.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cur.fetchall()}  # name set

def add_column(conn, table, name, ddl):
    print(f"  -> {table}: ADD COLUMN {name} {ddl}")
    conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}")

def main():
    if not Path(DB_PATH).exists():
        raise SystemExit(f"❌ 数据库不存在: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    try:
        print(f"🛠️  连接: {DB_PATH}")

        # 检查所有目标表都存在
        existing_tables = {
            r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        for table in EXPECTED.keys():
            if table not in existing_tables:
                print(f"❌ 缺少表: {table}（请先跑初始化脚本创建该表）")

        # 逐表新增缺列
        for table, cols in EXPECTED.items():
            if table not in existing_tables:
                continue
            present = table_columns(conn, table)
            missing = [(n, ddl) for (n, ddl) in cols if n not in present]
            if not missing:
                print(f"✅ {table}: 无缺列")
                continue
            for name, ddl in missing:
                add_column(conn, table, name, ddl)
            conn.commit()
            print(f"✅ {table}: 新增 {len(missing)} 列完成")

        # 可选：对某些新加列做一次性回填（避免 NULL 导致的测试逻辑分支）
        # 示例：把 users.status 为 NULL 的行设为 'active'
        conn.execute("UPDATE users SET status='active' WHERE status IS NULL")
        # 示例：初始化 agent_usage_stats.usage_count/total_tokens 为 0（虽然已经有默认值）
        conn.execute("UPDATE agent_usage_stats SET usage_count=0 WHERE usage_count IS NULL")
        conn.execute("UPDATE agent_usage_stats SET total_tokens=0 WHERE total_tokens IS NULL")
        conn.commit()

        print("🎉 所有缺失列补齐完成。")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
