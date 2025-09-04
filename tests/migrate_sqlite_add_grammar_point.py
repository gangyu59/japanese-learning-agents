#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
from pathlib import Path

DB_PATH = Path("./japanese_learning.db")

def has_col(conn, table, col):
    rows = conn.execute(f'PRAGMA table_info("{table}")').fetchall()
    return any(r[1] == col for r in rows)

def add_col(conn, table, col, ddl):
    if not has_col(conn, table, col):
        print(f"🔧 adding {table}.{col} ...")
        conn.execute(f'ALTER TABLE {table} ADD COLUMN {col} {ddl}')
        print("   ✅ done")
    else:
        print(f"   ✅ {table}.{col} already exists")

def main():
    if not DB_PATH.exists():
        raise SystemExit(f"❌ DB not found: {DB_PATH}")

    conn = sqlite3.connect(str(DB_PATH))
    try:
        # SQLite 只能用“常量默认值”，所以用空串，避免你上次遇到的 DEFAULT 表达式错误
        add_col(conn, "learning_progress", "grammar_point", 'TEXT DEFAULT ""')
        conn.commit()
        print("🎉 migration finished.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
