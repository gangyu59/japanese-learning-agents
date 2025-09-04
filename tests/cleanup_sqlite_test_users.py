# -*- coding: utf-8 -*-
import sqlite3
import re

DB = "./japanese_learning.db"

PATTERNS = [
    r"^test_.*",                # 常见的 test_ 前缀
    r"^persistence_.*",         # 持久化测试前缀
    r"^integration_.*",         # 集成测试前缀
    r"^sqlite_.*",
    r"^phase\d+_.*",
]

EMAIL_SUFFIXES = [
    "@example.com",
    "@test.local",
]

def main():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys=OFF")

    # 按 username 前缀清理
    usernames = [p.replace("^", "").replace(".*", "") for p in PATTERNS]
    for prefix in usernames:
        conn.execute("DELETE FROM users WHERE username LIKE ?", (f"{prefix}%",))

    # 按 email 后缀清理
    for suffix in EMAIL_SUFFIXES:
        conn.execute("DELETE FROM users WHERE email LIKE ?", (f"%{suffix}",))

    # 清理孤儿进度/词汇数据（防 FK 冲突）
    conn.execute("""
        DELETE FROM learning_progress
        WHERE user_id NOT IN (SELECT user_id FROM users)
    """)
    conn.execute("""
        DELETE FROM vocabulary_progress
        WHERE user_id NOT IN (SELECT user_id FROM users)
    """)

    conn.commit()
    conn.close()
    print("✅ Test users cleanup done.")

if __name__ == "__main__":
    main()
