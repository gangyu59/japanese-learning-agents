# tests/migrate_sqlite_fix_learning_progress.py
import sqlite3

def add_column(conn, table, col, ddl):
    try:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {ddl}")
        print(f"✅ Added column {col} to {table}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print(f"⚠️ Column {col} already exists in {table}, skipping")
        else:
            raise

def main():
    conn = sqlite3.connect("japanese_learning.db")

    # 必要列
    add_column(conn, "learning_progress", "progress_id", "TEXT")
    add_column(conn, "learning_progress", "grammar_point", "TEXT")
    add_column(conn, "learning_progress", "mastery_level", "REAL DEFAULT 0.0")
    add_column(conn, "learning_progress", "last_reviewed", "TIMESTAMP")
    add_column(conn, "learning_progress", "practice_count", "INTEGER DEFAULT 0")

    conn.commit()
    conn.close()
    print("🎉 Migration completed")

if __name__ == "__main__":
    main()
