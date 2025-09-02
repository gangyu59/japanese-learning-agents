# src/api/routers/novel.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from importlib import import_module

from src.core.workflows import novel_collab as flow

router = APIRouter()

def _get_agents_or_503():
    """运行时从 main 里取出全局 agents_system，未初始化则 503。"""
    main_mod = import_module("main")
    agents = getattr(main_mod, "agents_system", None)
    if not agents:
        raise HTTPException(status_code=503, detail="智能体系统未初始化")
    return agents

# ---------- 输入模型（兼容旧字段名） ----------

class BrainstormIn(BaseModel):
    theme: Optional[str] = None          # 旧字段
    topic: Optional[str] = None          # 新字段
    session_id: str
    user_id: Optional[str] = None
    agents: Optional[List[str]] = None

class CharacterIn(BaseModel):
    session_id: str

class RoundRobinIn(BaseModel):
    seed: str
    turns: int = Field(3, ge=1, le=12)
    session_id: str

class LiveDiscussionIn(BaseModel):
    question: Optional[str] = None
    # 兼容旧 discuss 的字段
    conflict: Optional[str] = None
    options: Optional[List[str]] = None
    session_id: str

class ArbitrateIn(BaseModel):
    decision: Optional[str] = None
    # 兼容旧字段
    choice: Optional[str] = None
    reason: str = "user"

# 兼容旧前端 /next 端点
class NextCompatIn(BaseModel):
    outline: Dict[str, Any] = {}
    last_paragraph: str = ""
    user_hint: str = ""
    turns: int = Field(3, ge=1, le=12)
    order: Optional[List[str]] = None
    user_id: Optional[str] = None
    session_id: str


# ---------- 路由 ----------

@router.post("/brainstorm")
async def brainstorm(payload: BrainstormIn):
    try:
        agents = _get_agents_or_503()
        # 兼容 theme/topic 两种写法
        topic = payload.topic or payload.theme or "未命名主题"
        return await flow.brainstorm_meeting(agents, topic, payload.session_id)
    except HTTPException:
        raise
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


@router.post("/characters")
async def characters(payload: CharacterIn):
    try:
        agents = _get_agents_or_503()
        return await flow.character_world_building(agents, payload.session_id)
    except HTTPException:
        raise
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


@router.post("/round_robin")
async def round_robin(payload: RoundRobinIn):
    try:
        agents = _get_agents_or_503()
        return await flow.round_robin_writing(
            agents=agents,
            seed=payload.seed,
            turns=payload.turns,
            session_id=payload.session_id
        )
    except HTTPException:
        raise
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


@router.post("/live_discussion")
async def live_discussion(payload: LiveDiscussionIn):
    try:
        agents = _get_agents_or_503()
        question = payload.question or payload.conflict or "请就当前剧情的关键分歧给出立场与理由"
        # flow.live_discussion 目前不使用 options，这里仅透传 question
        return await flow.live_discussion(agents, question, payload.session_id)
    except HTTPException:
        raise
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


@router.post("/arbitrate")
async def arbitrate(payload: ArbitrateIn):
    try:
        decision = payload.decision or payload.choice or "未指定"
        return flow.user_arbitrate(decision, payload.reason)
    except HTTPException:
        raise
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


# ---------- 兼容旧端点：/next -> round_robin ----------

@router.post("/next")
async def next_compat(payload: NextCompatIn):
    try:
        agents = _get_agents_or_503()
        seed = (payload.last_paragraph or "")
        if payload.user_hint:
            seed = (seed + "\n" + payload.user_hint).strip()
        if not seed:
            seed = "（起始空白）"
        return await flow.round_robin_writing(
            agents=agents,
            seed=seed,
            turns=payload.turns,
            session_id=payload.session_id
        )
    except HTTPException:
        raise
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


# === 保存 / 载入 进度 ===
from pydantic import BaseModel
from typing import List

class SaveIn(BaseModel):
    session_id: str
    project: str
    outline: List[dict] = []
    manuscript: List[dict] = []

@router.post("/save")
async def save(payload: SaveIn):
    try:
        from src.storage import novel_repo as repo
        return repo.save_project(payload.session_id, payload.project, payload.outline, payload.manuscript)
    except HTTPException:
        raise
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}

@router.get("/load")
async def load(session_id: str, project: str):
    try:
        from src.storage import novel_repo as repo
        data = repo.load_project(session_id, project)
        return data or {"not_found": True}
    except HTTPException:
        raise
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}
