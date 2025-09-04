#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
from typing import List, Tuple

DB_PATH = "./japanese_learning.db"

def get_cols(cur, table: str) -> List[str]:
    cur.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]

def add_col(cur, table: str, col_def: str):
    col_name = col_def.split()[0]
    cur.execute(f"ALTER TABLE {table} ADD COLUMN {col_def}")
    print(f"   - ✅ added {table}.{col_name}")

def ensure_table_and_cols(conn, table: str, create_sql: str, needed_cols: List[Tuple[str, str]]):
    cur = conn.cursor()
    cur.execute(f"CREATE TABLE IF NOT EXISTS {table} {create_sql}")
    existing = set(get_cols(cur, table))

    for col_name, ddl in needed_cols:
        if col_name not in existing:
            add_col(cur, table, ddl)

def ensure_index(conn, name: str, table: str, cols: str, unique: bool = False):
    cur = conn.cursor()
    kind = "UNIQUE" if unique else ""
    cur.execute(f"CREATE {kind} INDEX IF NOT EXISTS {name} ON {table}({cols})")
    print(f"   - ✅ ensured index {name} on {table}({cols})")

def main():
    print("🔧 Auditing & migrating SQLite schema ...")
    conn = sqlite3.connect(DB_PATH)

    # users
    ensure_table_and_cols(
        conn,
        "users",
        """(
           user_id TEXT PRIMARY KEY,
           username TEXT UNIQUE,
           email TEXT,
           password_hash TEXT,
           learning_level TEXT,
           target_jlpt_level TEXT,
           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
           updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        [
            ("user_id", "user_id TEXT"),               # no-op if exists
            ("username", "username TEXT"),
            ("email", "email TEXT"),
            ("password_hash", "password_hash TEXT"),
            ("learning_level", "learning_level TEXT"),
            ("target_jlpt_level", "target_jlpt_level TEXT"),
            ("created_at", "created_at TIMESTAMP"),
            ("updated_at", "updated_at TIMESTAMP"),
        ],
    )

    # learning_progress  —— 所有测试会用到的列
    ensure_table_and_cols(
        conn,
        "learning_progress",
        """(
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           user_id TEXT,
           grammar_point TEXT,
           mastery_level REAL DEFAULT 0.0,
           practice_count INTEGER DEFAULT 0,
           progress_id TEXT,
           last_reviewed TIMESTAMP
        )""",
        [
            ("user_id", "user_id TEXT"),
            ("grammar_point", "grammar_point TEXT"),
            ("mastery_level", "mastery_level REAL DEFAULT 0.0"),
            ("practice_count", "practice_count INTEGER DEFAULT 0"),
            ("progress_id", "progress_id TEXT"),
            # 不能在 SQLite 用函数作默认值，这里先无默认，再用 UPDATE 补
            ("last_reviewed", "last_reviewed TIMESTAMP"),
        ],
    )
    # 补充 last_reviewed 的初值
    conn.execute("UPDATE learning_progress SET last_reviewed = COALESCE(last_reviewed, CURRENT_TIMESTAMP) WHERE last_reviewed IS NULL")
    ensure_index(conn, "idx_learning_progress_pid", "learning_progress", "progress_id", unique=True)

    # vocabulary_progress —— 按 SQLite 测试版本
    ensure_table_and_cols(
        conn,
        "vocabulary_progress",
        """(
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           user_id TEXT,
           word TEXT,
           proficiency REAL DEFAULT 0.0,
           review_due TIMESTAMP,
           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
           updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
           progress_id TEXT
        )""",
        [
            ("user_id", "user_id TEXT"),
            ("word", "word TEXT"),
            ("proficiency", "proficiency REAL DEFAULT 0.0"),
            ("review_due", "review_due TIMESTAMP"),
            ("created_at", "created_at TIMESTAMP"),
            ("updated_at", "updated_at TIMESTAMP"),
            ("progress_id", "progress_id TEXT"),
        ],
    )

    conn.commit()
    conn.close()
    print("✅ migration done. You are ready to re-run tests.")

if __name__ == "__main__":
    main()
