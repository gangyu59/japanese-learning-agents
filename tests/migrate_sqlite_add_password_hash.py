#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import sqlite3
from pathlib import Path

def resolve_db_path(cli_db: str | None) -> Path:
    """
    优先使用 --db；否则从 tests/test_config.json 里解析 sqlite:///...；
    再否则默认 ./japanese_learning.db
    """
    if cli_db:
        return Path(cli_db).resolve()

    # 尝试从根目录的 test_config.json 读取（通常 run_all_tests 用这个）
    cfg_path_candidates = [
        Path(__file__).parent / "test_config.json",
        Path(__file__).parent.parent / "test_config.json",
        Path("test_config.json")
    ]
    db_url = None
    for p in cfg_path_candidates:
        if p.exists():
            try:
                cfg = json.loads(p.read_text(encoding="utf-8"))
                db_url = (cfg.get("database", {}) or {}).get("url")
                break
            except Exception:
                pass

    if db_url and db_url.startswith("sqlite:///"):
        # 形如 sqlite:///./japanese_learning.db
        rel = db_url.replace("sqlite:///", "", 1)
        return Path(rel).resolve()

    # 兜底
    return Path("./japanese_learning.db").resolve()

def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table,))
    return cur.fetchone() is not None

def column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    cur = conn.execute(f"PRAGMA table_info({table});")
    cols = [row[1] for row in cur.fetchall()]  # row[1] 是列名
    return column in cols

def ensure_users_table(conn: sqlite3.Connection):
    """
    若不存在 users 表，则以“最新结构”创建（包含 password_hash）。
    若存在但缺少 password_hash，则做 ALTER TABLE ADD COLUMN。
    """
    if not table_exists(conn, "users"):
        print("📦 users 表不存在，创建带 password_hash 的最新结构…")
        conn.execute("""
            CREATE TABLE users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                password_hash TEXT,         -- 这就是要新增的列
                learning_level TEXT,
                target_jlpt_level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        print("✅ 已创建 users 表（包含 password_hash）")
        return

    # 表已存在，检查列
    if not column_exists(conn, "users", "password_hash"):
        print("🔧 users 表存在，但缺少 password_hash，准备新增列…")
        conn.execute("ALTER TABLE users ADD COLUMN password_hash TEXT;")
        conn.commit()
        print("✅ 已为 users 表新增 password_hash 列")
    else:
        print("✅ users 表已存在且包含 password_hash，无需变更")

def main():
    parser = argparse.ArgumentParser(description="SQLite migration: add users.password_hash if missing")
    parser.add_argument("--db", help="SQLite 文件路径（默认从 test_config.json 或 ./japanese_learning.db 推导）")
    args = parser.parse_args()

    db_path = resolve_db_path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"🔧 使用的 SQLite 文件: {db_path}")

    conn = sqlite3.connect(str(db_path))
    try:
        ensure_users_table(conn)
    finally:
        conn.close()

    print("🎉 迁移完成")

if __name__ == "__main__":
    main()
