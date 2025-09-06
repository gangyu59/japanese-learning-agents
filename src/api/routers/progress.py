from fastapi import APIRouter, HTTPException, Body
from typing import Dict
import logging
import sys
import os

# 添加src路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/progress", tags=["progress"])

progress_tracker = None


def get_progress_tracker():
    global progress_tracker
    if progress_tracker is None:
        try:
            from data.repositories.progress_tracker import ProgressTracker
            progress_tracker = ProgressTracker()
        except Exception as e:
            logger.error(f"无法初始化进度追踪器: {e}")
            return None
    return progress_tracker


@router.get("/summary")
async def get_progress_summary(user_id: str = "demo_user"):
    try:
        tracker = get_progress_tracker()
        if not tracker:
            raise HTTPException(status_code=500, detail="进度追踪器未初始化")
        summary = tracker.get_user_progress_summary(user_id)
        return {"success": True, "data": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取进度失败: {str(e)}")


@router.post("/track")
async def track_learning(
        payload: Dict = Body(...)
):
    try:
        user_input = payload.get("user_input")
        agent_responses = payload.get("agent_responses", {})
        session_id = payload.get("session_id")
        scene_context = payload.get("scene_context", "general")

        if not user_input or not session_id:
            return {"success": False, "error": "缺少必要参数"}

        tracker = get_progress_tracker()
        if not tracker:
            return {"success": False, "error": "进度追踪器未初始化"}

        learning_data = tracker.extract_learning_data(
            user_input, agent_responses, session_id, scene_context
        )

        return {
            "success": True,
            "learning_data": {
                "grammar_points_count": len(learning_data.get('grammar_points', [])),
                "vocabulary_count": len(learning_data.get('vocabulary', [])),
                "cultural_topics_count": len(learning_data.get('cultural_topics', [])),
                "corrections_count": len(learning_data.get('corrections', []))
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/recommendations")
async def get_learning_recommendations(user_id: str = "demo_user"):
    try:
        tracker = get_progress_tracker()
        if not tracker:
            raise HTTPException(status_code=500, detail="进度追踪器未初始化")
        summary = tracker.get_user_progress_summary(user_id)
        return {
            "success": True,
            "recommendations": summary.get('recommendations', []),
            "weak_points": summary.get('weak_points', [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取学习建议失败: {str(e)}")