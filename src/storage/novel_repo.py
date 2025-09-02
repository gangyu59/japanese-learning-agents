# src/storage/novel_repo.py
from __future__ import annotations
import os, json, datetime as dt
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# 优先使用你的环境变量/统一数据库；否则退回到本地 sqlite
DB_URL = os.getenv("NOVEL_DB_URL") or os.getenv("DATABASE_URL") or "sqlite:///./data/novel.db"

engine = create_engine(DB_URL, future=True, echo=False)
SessionLocal = sessionmaker(engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

class NovelProject(Base):
    __tablename__ = "novel_projects"
    id = Column(String(256), primary_key=True)   # session_id:project
    session_id = Column(String(128), index=True, nullable=False)
    project = Column(String(256), index=True, nullable=False)
    outline = Column(Text)       # JSON
    manuscript = Column(Text)    # JSON
    updated_at = Column(DateTime, default=dt.datetime.utcnow)

def init_db():
    os.makedirs("./data", exist_ok=True)
    Base.metadata.create_all(engine)

def save_project(session_id: str, project: str, outline: List[Dict[str, Any]], manuscript: List[Dict[str, Any]]):
    init_db()
    pid = f"{session_id}:{project}"
    now = dt.datetime.utcnow()
    with SessionLocal() as db:
        obj = db.get(NovelProject, pid)
        if obj is None:
            obj = NovelProject(
                id=pid, session_id=session_id, project=project,
                outline=json.dumps(outline, ensure_ascii=False),
                manuscript=json.dumps(manuscript, ensure_ascii=False),
                updated_at=now
            )
            db.add(obj)
        else:
            obj.outline = json.dumps(outline, ensure_ascii=False)
            obj.manuscript = json.dumps(manuscript, ensure_ascii=False)
            obj.updated_at = now
        db.commit()
    return {"ok": True, "id": pid, "updated_at": now.isoformat()+"Z"}

def load_project(session_id: str, project: str) -> Optional[Dict[str, Any]]:
    init_db()
    pid = f"{session_id}:{project}"
    with SessionLocal() as db:
        obj = db.get(NovelProject, pid)
        if not obj:
            return None
        return {
            "session_id": obj.session_id,
            "project": obj.project,
            "outline": json.loads(obj.outline) if obj.outline else [],
            "manuscript": json.loads(obj.manuscript) if obj.manuscript else [],
            "updated_at": (obj.updated_at or dt.datetime.utcnow()).isoformat()+"Z"
        }
