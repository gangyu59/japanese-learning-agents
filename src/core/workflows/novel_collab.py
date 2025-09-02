# src/core/workflows/novel_collab.py
from typing import Dict, Any, List
import asyncio

# ---- 放在 novel_collab.py 顶部的 import 附近 ----
import inspect
from typing import Any, Dict

async def _maybe_await(x):
    if inspect.isawaitable(x):
        return await x
    return x

def _norm_response(ret: Any) -> str:
    if ret is None:
        return ""
    if isinstance(ret, dict):
        # 尽量兼容各种返回形态
        for k in ("response", "text", "output", "result", "msg"):
            if k in ret and isinstance(ret[k], (str, bytes)):
                return ret[k].decode("utf-8") if isinstance(ret[k], bytes) else ret[k]
        # 兜底：把 dict 压成简短字符串
        return str(ret)
    return str(ret)

async def _call_agent(agent, message: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
    """
    兼容不同Agent实现：
    - 首选 async def process_message(message=..., context=...)
    - 次选 async def process_user_input(text, ctx) / process_input(text, ctx)
    - 再次选 __call__(text, ctx) / 同步函数
    - 捕获 TypeError 自动退化为不带 ctx 的版本
    """
    name = getattr(agent, "name", getattr(agent, "agent_id", "agent"))

    # 候选方法名与调用方式
    candidates = [
        ("process_message", {"kw": True}),          # func(message=..., context=...)
        ("process_user_input", {"kw": False}),      # func(text, ctx)
        ("process_input", {"kw": False}),           # func(text, ctx)
        ("__call__", {"kw": False}),                # func(text, ctx)
    ]
    last_err = None

    for method, meta in candidates:
        func = getattr(agent, method, None)
        if not func:
            continue
        try:
            if meta["kw"]:  # 关键字参数版本
                ret = await _maybe_await(func(message=message, context=ctx))
            else:           # 位置参数版本
                try:
                    ret = await _maybe_await(func(message, ctx))
                except TypeError:
                    # 退化：有些实现只接 text
                    ret = await _maybe_await(func(message))
            return {
                "agent_id": getattr(agent, "agent_id", name),
                "response": _norm_response(ret)
            }
        except Exception as e:
            last_err = e
            continue

    # 全都失败，返回错误信息（避免 500 直接炸）
    return {
        "agent_id": getattr(agent, "agent_id", name),
        "response": "",
        "error": f"{type(last_err).__name__}: {last_err}" if last_err else "No callable interface"
    }


# 1. 头脑风暴
async def brainstorm_meeting(agents: Dict[str, object], topic: str, session_id: str) -> Dict[str, Any]:
    ctx = {"mode": "novel_brainstorm", "session_id": session_id, "topic": topic}
    items = []
    for aid, ag in agents.items():
        prompt = (
            f"我们要创作小说，主题：{topic}。"
            "请给出3个有冲突点的设定建议，并各用一句话解释亮点。中日双语更好。"
        )
        res = await _call_agent(ag, prompt, ctx)   # ← 返回 dict: {agent_id, response, error?}
        # 规范化为 {agent_id, response}
        items.append({
            "agent_id": aid,
            "response": res.get("response", ""),
            **({"error": res.get("error")} if res.get("error") else {})
        })
    return {"stage": "brainstorm", "topic": topic, "items": items}


# 2. 角色设定
async def character_world_building(agents: Dict[str, object], session_id: str) -> Dict[str, Any]:
    ctx = {"mode": "novel_characters", "session_id": session_id}
    items = []
    for aid, ag in agents.items():
        prompt = "请各自提一名角色（含性格、动机、缺点）和一条世界观规则。最好用JSON列出，并附中文说明。"
        res = await _call_agent(ag, prompt, ctx)
        items.append({
            "agent_id": aid,
            "response": res.get("response", ""),
            **({"error": res.get("error")} if res.get("error") else {})
        })
    return {"stage": "characters", "items": items}


# 3. 轮流写作
async def round_robin_writing(agents: Dict[str, object], seed: str, turns: int, session_id: str) -> List[Dict[str, Any]]:
    ctx = {"mode": "novel_round_robin", "session_id": session_id}
    order = list(agents.keys())  # 小美→山田→田中 等顺序按字典插入顺序
    history: List[Dict[str, Any]] = [{"by": "seed", "text": str(seed or "")}]
    text = str(seed or "")

    for i in range(turns):
        aid = order[i % len(order)]
        ag = agents[aid]
        prompt = (
            "基于以下文本续写100-150字，并在最后给出1行《修改建议》：\n"
            f"{text}\n"
            "要求：推进剧情或加深人物冲突，避免重复表述。日文为主，附中文对照更好。"
        )
        res = await _call_agent(ag, prompt, ctx)       # dict
        piece_text = res.get("response", "")            # ← 取字符串
        history.append({"by": aid, "text": piece_text}) # ← history 只放字符串
        if piece_text:
            text += "\n" + piece_text                   # ← 这里不再拼 dict

    return {"stage": "round_robin", "history": history}


# 4. 实时讨论（简化版）
async def live_discussion(agents: Dict[str, object], question: str, session_id: str) -> Dict[str, Any]:
    ctx = {"mode": "novel_live_discussion", "session_id": session_id}
    items = []
    ask = f"讨论问题：{question}。请给出立场与理由（80字以内，中/日均可）。"
    for aid, ag in agents.items():
        res = await _call_agent(ag, ask, ctx)
        items.append({
            "agent_id": aid,
            "response": res.get("response", ""),
            **({"error": res.get("error")} if res.get("error") else {})
        })
    return {"stage": "debate", "items": items}


# 5. 用户仲裁（只负责聚合）
def user_arbitrate(decision: str, reason: str) -> Dict[str, Any]:
    return {"decision": decision, "reason": reason}
