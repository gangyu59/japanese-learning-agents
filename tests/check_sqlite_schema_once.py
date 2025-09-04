import sqlite3, json

REQUIRED = {
    "users": ["user_id","username","email","password_hash","created_at","updated_at","settings","status","provider"],
    "learning_progress": [
        "progress_id","user_id","content_id","content_type",
        "grammar_point","mastery_level","score","notes",
        "created_at","updated_at","last_reviewed","next_review"
    ],
    "vocabulary_progress": [
        "id","user_id","word","reading","meaning",
        "proficiency","review_count","last_reviewed","next_review","created_at","updated_at","tags","source"
    ],
    "custom_agents": ["id","user_id","name","role","prompt","config","created_at","updated_at","status"],
    "custom_scenes": ["id","user_id","name","description","prompt","config","created_at","updated_at","status"],
    "conversation_history": ["id","user_id","session_id","role","content","created_at"],
    "learning_sessions": ["session_id","user_id","topic","status","created_at","updated_at","score","notes"],
    "agent_usage_stats": ["id","agent_name","user_id","usage_count","last_used","total_tokens"],
}

def main(db="./japanese_learning.db"):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    ok = True
    for table, cols in REQUIRED.items():
        cur.execute(f"PRAGMA table_info({table})")
        present = [row[1] for row in cur.fetchall()]
        missing = [c for c in cols if c not in present]
        print(f"== {table} ==")
        print("  present:", present)
        if missing:
            ok = False
            print("  MISSING:", missing)
        else:
            print("  OK")
    conn.close()
    print("\nSCHEMA OK?" , ok)

if __name__ == "__main__":
    main()
