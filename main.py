# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# 🎌 日语学习Multi-Agent系统 - 主应用入口
# """
#
# import asyncio
# import logging
# from pathlib import Path
# from contextlib import asynccontextmanager
# from datetime import datetime
# from typing import Dict, List, Any, Optional
#
# from pydantic import BaseModel
#
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
# from fastapi.staticfiles import StaticFiles
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import HTMLResponse, JSONResponse
# import uvicorn
#
# # 导入配置和工具
# from utils.config import settings
# from utils.database import init_database
# from utils.websocket_manager import WebSocketManager
# from utils.llm_client import get_llm_client
#
# from src.api.routers.novel import router as novel_router
#
# # 首先设置日志和创建logger
# from utils.logger import setup_logging
#
# import logging
# logger = logging.getLogger(__name__)
#
# DEMO_MODE = False
#
#
# # 导入智能体系统（全部真实类）
# AGENTS_AVAILABLE = False
# try:
#     from src.core.agents.core_agents.tanaka_sensei import TanakaSensei
#     from src.core.agents.core_agents.koumi import KoumiAgent
#     from src.core.agents.core_agents.yamada_sensei import YamadaSensei
#     from src.core.agents.core_agents.sato_coach import SatoCoach
#     from src.core.agents.core_agents.mem_bot import MemBot
#     from src.core.agents.core_agents.ai_analyzer import AIAnalyzer
#
#     AGENTS_AVAILABLE = True
#     logger.info("✅ 智能体已加载：田中 / 小美 / 山田 / 佐藤 / 记忆管家 / アイ")
# except ImportError as e:
#     logger.warning(f"⚠️  智能体模块部分可用: {e}")
#     AGENTS_AVAILABLE = False
#
#
# setup_logging()
# logger = logging.getLogger(__name__)
#
#
# # 添加请求和响应模型
# class ChatRequest(BaseModel):
#     message: str
#     user_id: str
#     session_id: str
#     agent_name: str = "田中先生"
#     scene_context: Optional[str] = "general"
#
#
# class ChatResponse(BaseModel):
#     success: bool
#     response: str
#     agent_name: str
#     learning_points: Optional[List[str]] = []
#     suggestions: Optional[List[str]] = []
#     timestamp: Optional[str] = None
#     error: Optional[str] = None
#
#
# class MultiAgentChatRequest(BaseModel):
#     message: str
#     user_id: str
#     session_id: str
#     active_agents: List[str]  # 多个智能体
#     collaboration_mode: str = "discussion"  # discussion, correction, creation, analysis
#     scene_context: str = "general"
#
# class MultiAgentChatResponse(BaseModel):
#     success: bool
#     responses: List[Dict[str, Any]]  # 多个智能体的回复
#     collaboration_mode: str
#     agents_participated: List[str]
#     conflicts: List[Dict[str, Any]] = []  # 冲突信息
#     final_recommendation: str = ""
#     user_arbitration_needed: bool = False
#     timestamp: str
#
#
# # 导入API路由 (这些文件稍后实现)
# API_ROUTES_AVAILABLE = False
# try:
#     from src.api.routers import chat, agents, learning, analytics
#
#     # 检查是否有router属性
#     if (hasattr(chat, 'router') and hasattr(agents, 'router') and
#             hasattr(learning, 'router') and hasattr(analytics, 'router')):
#         API_ROUTES_AVAILABLE = True
#     else:
#         print("⚠️  API路由模块未完全实现，将只启动基础服务")
# except ImportError:
#     print("⚠️  API路由模块尚未实现，将只启动基础服务")
#
#
# # 全局变量
# websocket_manager = WebSocketManager()
# agents_system = None
# collaboration_manager = None
#
#
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """应用生命周期管理"""
#     # 启动时初始化
#     logger.info("🚀 启动日语学习Multi-Agent系统...")
#
#     # 初始化数据库
#     await init_database()
#
#     # 初始化智能体系统
#     await init_agents_system()
#
#     logger.info("✅ 系统初始化完成")
#
#     yield
#
#     # 关闭时清理
#     logger.info("🛑 正在关闭系统...")
#     await cleanup_resources()
#     logger.info("✅ 系统已安全关闭")
#
#
# # 创建FastAPI应用
# app = FastAPI(
#     title="🎌 日语学习Multi-Agent系统",
#     description="智能化、游戏化的日语学习平台",
#     version="1.0.0",
#     docs_url="/docs" if settings.DEBUG else None,
#     redoc_url="/redoc" if settings.DEBUG else None,
#     lifespan=lifespan
# )
#
# app.include_router(novel_router, prefix="/api/v1/novel", tags=["novel"])
#
# FRONTEND_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
#     "http://localhost:5173",
#     "http://127.0.0.1:5173",
#     "http://localhost:8080",
#     "http://127.0.0.1:8080",
#     "http://localhost",
#     "http://127.0.0.1",
# ]
#
# # CORS中间件
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.ALLOWED_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
#
# # 静态文件服务
# app.mount("/static", StaticFiles(directory="frontend"), name="static")
#
#
# # 在main.py中CORS中间件后添加
# @app.middleware("http")
# async def add_utf8_header(request, call_next):
#     response = await call_next(request)
#     if "application/json" in response.headers.get("content-type", ""):
#         response.headers["content-type"] = "application/json; charset=utf-8"
#     return response
#
#
# async def cleanup_resources():
#     """清理系统资源"""
#     try:
#         # 关闭LLM客户端
#         llm_client = get_llm_client()
#         await llm_client.close()
#         logger.info("LLM客户端已关闭")
#     except Exception as e:
#         logger.error(f"关闭LLM客户端时出错: {str(e)}")
#
#     # 关闭所有WebSocket连接
#     await websocket_manager.close_all_connections()
#
#     # 保存智能体状态（如果需要）
#     if agents_system and AGENTS_AVAILABLE:
#         for agent in agents_system.values():
#             if hasattr(agent, 'save_state'):
#                 await agent.save_state()
#
#
# async def init_agents_system():
#     global agents_system, collaboration_manager
#
#     # 1) 若导入失败，直接抛错，阻止静默回退到模板
#     if not AGENTS_AVAILABLE:
#         raise RuntimeError("智能体模块导入失败：已禁止 Mock 回退，请修复导入后再启动。")
#
#     # 2) 正常情况下，实例化 6 个真实智能体
#     agents_system = {
#         'tanaka': TanakaSensei(),
#         'koumi':  KoumiAgent(),
#         'yamada': YamadaSensei(),
#         'sato':   SatoCoach(),
#         'membot': MemBot(),
#         'ai':     AIAnalyzer(),
#     }
#
#     # 3) 保持你现有的协作管理器用法（无需改动其它代码）
#     collaboration_manager = MixedCollaborationManager(agents_system)
#     logger.info("🤖 智能体系统初始化完成（全部真实 AI，已禁用 Mock 回退）")
#
#
# async def create_mock_agents():
#     """创建模拟智能体系统"""
#     return {
#         'tanaka': MockAgent('tanaka', '田中先生', '语法专家', '👨‍🏫'),
#         'koumi': MockAgent('koumi', '小美', '对话伙伴', '👧'),
#         'ai': MockAgent('ai', 'アイ', '分析师', '🤖'),
#         'yamada': MockAgent('yamada', '山田先生', '文化专家', '🎌'),
#         'sato': MockAgent('sato', '佐藤教练', '考试专家', '🎯'),
#         'membot': MockAgent('membot', '记忆管家', '学习记录', '🧠')
#     }
#
#
# class MockAgent:
#     """模拟智能体类"""
#
#     def __init__(self, agent_id: str, name: str, role: str, avatar: str):
#         self.agent_id = agent_id
#         self.name = name
#         self.role = role
#         self.avatar = avatar
#         self.current_emotion = "😊"
#
#     async def process_user_input(self, user_input: str, session_context: dict, scene: str = "grammar"):
#         """模拟处理用户输入"""
#         # 模拟思考时间
#         await asyncio.sleep(0.5)
#
#         # 基于智能体类型返回不同的模拟回应
#         mock_responses = {
#             'tanaka': f"語法分析：「{user_input}」の文法構造を確認しましょう。\n\n**中文提示：** 让我们分析这个句子的语法结构。",
#             'koumi': f"そうなんだ！「{user_input}」って面白い表現だね～\n\n**中文提示：** 这是个很有趣的表达呢！",
#             'ai': f"数据分析：输入文本长度 {len(user_input)} 字符，复杂度评分：中等。\n\n**学习建议：** 建议加强语法练习。",
#             'yamada': f"「{user_input}」には日本の文化的背景がありますね。\n\n**文化解释：** 这个表达背后有日本文化背景。",
#             'sato': f"JLPT対策：「{user_input}」はN3レベルの表現です！\n\n**考试要点：** 这是N3级别的重要表达！",
#             'membot': f"学習記録更新：「{user_input}」を記録しました。\n\n**进度更新：** 已记录您的学习内容。"
#         }
#
#         content = mock_responses.get(self.agent_id, f"{self.name}正在思考中...")
#
#         return {
#             "content": content,
#             "agent_id": self.agent_id,
#             "agent_name": self.name,
#             "emotion": self.current_emotion,
#             "is_mock": True
#         }
#
#     async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
#         """为了兼容真实智能体接口而添加的方法"""
#         response = await self.process_user_input(message, context or {})
#         return {
#             "response": response["content"],
#             "agent_name": self.name,
#             "success": True,
#             "learning_points": [f"模拟学习点: {message[:20]}..."],
#             "suggestions": [f"建议练习更多{self.role}相关内容"],
#             "timestamp": datetime.now().isoformat(),
#             "origin": "mock"
#         }
#
#
# class MixedCollaborationManager:
#     """混合协作管理器 - 支持真实和模拟智能体"""
#
#     def __init__(self, agents):
#         self.agents = agents
#
#     async def process_user_input(self, session_id: str, user_input: str, active_agents: list, scene: str):
#         """处理用户输入 - 混合模式"""
#         responses = []
#
#         for agent_id in active_agents:
#             if agent_id in self.agents:
#                 agent = self.agents[agent_id]
#
#                 try:
#                     if hasattr(agent, 'process_user_input') and not hasattr(agent, 'is_mock'):
#                         # 真实智能体（如田中先生）
#                         response = await agent.process_user_input(
#                             user_input=user_input,
#                             session_context={"session_id": session_id},
#                             scene=scene
#                         )
#                         responses.append(response)
#                     else:
#                         # 模拟智能体
#                         response = await agent.process_user_input(user_input, {}, scene)
#                         responses.append(response)
#
#                 except Exception as e:
#                     logger.error(f"❌ 智能体 {agent_id} 处理失败: {e}")
#                     # 降级到简单响应
#                     fallback_response = {
#                         "content": f"{agent.name}正在思考中，请稍等...\n\n**中文提示：** 智能体暂时无法回应。",
#                         "agent_id": agent_id,
#                         "agent_name": agent.name,
#                         "emotion": "🤔",
#                         "error": True
#                     }
#                     responses.append(fallback_response)
#
#         return responses
#
#     async def multi_agent_collaboration(
#             self,
#             user_input: str,
#             active_agents: List[str],
#             mode: str = "discussion",
#             session_context: Dict[str, Any] = None
#     ) -> Dict[str, Any]:
#         """多智能体协作处理"""
#
#         responses = []
#         conflicts = []
#
#         # 1. 获取所有智能体的初始回复
#         for agent_id in active_agents:
#             if agent_id in self.agents:
#                 try:
#                     agent = self.agents[agent_id]
#                     response = await agent.process_user_input(
#                         user_input=user_input,
#                         session_context=session_context or {},
#                         scene=mode
#                     )
#
#                     # 添加额外信息
#                     response['agent_id'] = agent_id
#                     response['confidence'] = 0.8  # 可以后续优化
#                     response['timestamp'] = datetime.now().isoformat()
#
#                     responses.append(response)
#
#                 except Exception as e:
#                     logger.error(f"智能体 {agent_id} 处理失败: {e}")
#                     # 添加错误回复
#                     responses.append({
#                         "content": f"{self.agents[agent_id].name}正在思考中，请稍等...",
#                         "agent_id": agent_id,
#                         "agent_name": self.agents[agent_id].name,
#                         "emotion": "🤔",
#                         "error": True,
#                         "confidence": 0.0,
#                         "timestamp": datetime.now().isoformat()
#                     })
#
#         # 2. 简单的冲突检测
#         conflicts = self._detect_simple_conflicts(responses)
#
#         # 3. 生成最终建议
#         final_recommendation = self._generate_collaboration_summary(responses, mode)
#
#         return {
#             "responses": responses,
#             "conflicts": conflicts,
#             "final_recommendation": final_recommendation,
#             "user_arbitration_needed": len(conflicts) > 0,
#             "collaboration_mode": mode,
#             "agents_participated": active_agents
#         }
#
#     def _detect_simple_conflicts(self, responses: List[Dict]) -> List[Dict]:
#         """简单的冲突检测"""
#         conflicts = []
#
#         # 检查是否有智能体给出明显不同的建议
#         for i, resp1 in enumerate(responses):
#             for j, resp2 in enumerate(responses[i + 1:], i + 1):
#                 content1 = resp1.get('content', '').lower()
#                 content2 = resp2.get('content', '').lower()
#
#                 # 简单的冲突关键词检测
#                 conflict_pairs = [
#                     ('正确', '错误'), ('对', '不对'), ('应该', '不应该'),
#                     ('建议', '不建议'), ('推荐', '不推荐')
#                 ]
#
#                 for word1, word2 in conflict_pairs:
#                     if word1 in content1 and word2 in content2:
#                         conflicts.append({
#                             "agent1": resp1.get('agent_id', ''),
#                             "agent2": resp2.get('agent_id', ''),
#                             "conflict_point": f"关于用户问题的不同观点",
#                             "conflict_id": f"conflict_{i}_{j}"
#                         })
#                         break
#
#         return conflicts
#
#     def _generate_collaboration_summary(self, responses: List[Dict], mode: str) -> str:
#         """生成协作总结"""
#         if not responses:
#             return "暂时无法生成协作总结。"
#
#         agent_names = [r.get('agent_name', '智能体') for r in responses]
#
#         if mode == "correction":
#             return f"📝 协作纠错总结：{', '.join(agent_names)}共同分析了您的问题，提供了专业的修正建议。"
#         elif mode == "creation":
#             return f"🎨 协作创作总结：{', '.join(agent_names)}协作完成了创作任务，展现了不同的创意角度。"
#         elif mode == "analysis":
#             return f"🔍 协作分析总结：{', '.join(agent_names)}从多个角度深入分析了问题，提供了全面的见解。"
#         else:  # discussion
#             return f"💬 协作讨论总结：{', '.join(agent_names)}进行了深入讨论，分享了各自的专业观点。"
#
#
# # =================== 路由定义 ===================
#
# # 在 main.py 或 app.py 中
# from frontend.assets.js.api.collaboration_api import router as collaboration_router
# app.include_router(collaboration_router, prefix="/api/v1/chat", tags=["collaboration"])
#
#
# @app.get("/", response_class=HTMLResponse)
# async def read_root():
#     """返回主页面"""
#     html_file = Path("frontend/pages/index.html")
#
#
#
# @app.get("/api/health")
# async def health_check():
#     """健康检查端点"""
#     return JSONResponse({
#         "status": "healthy",
#         "system": "Japanese Learning Multi-Agent System",
#         "version": "1.0.0",
#         "agents_available": AGENTS_AVAILABLE,
#         "api_routes_available": API_ROUTES_AVAILABLE,
#         "websocket": "ready"
#     })
#
#
# # 新增: 聊天API端点
# @app.post("/api/v1/chat/send")
# async def send_chat_message(request: ChatRequest):
#     """发送聊天消息到指定智能体"""
#     try:
#         logger.info(f"收到聊天请求: 用户={request.user_id}, 智能体={request.agent_name}")
#
#         # 将agent_name映射到agent_id
#         agent_mapping = {
#             "田中先生": "tanaka",
#             "小美": "koumi",
#             "アイ": "ai",
#             "山田先生": "yamada",
#             "佐藤教练": "sato",
#             "记忆管家": "membot"
#         }
#
#         agent_id = agent_mapping.get(request.agent_name, request.agent_name.lower())
#
#         # 获取指定的智能体
#         if agent_id in agents_system:
#             agent = agents_system[agent_id]
#
#             # 构建上下文
#             context = {
#                 "user_id": request.user_id,
#                 "session_id": request.session_id,
#                 "scene_context": request.scene_context,
#                 "timestamp": datetime.now().isoformat()
#             }
#
#             # 处理消息
#             result = await agent.process_message(
#                 message=request.message,
#                 context=context
#             )
#
#             if result.get("success", True):
#                 return ChatResponse(
#                     success=True,
#                     response=result["response"],
#                     agent_name=request.agent_name,
#                     learning_points=result.get("learning_points", []),
#                     suggestions=result.get("suggestions", []),
#                     timestamp=result.get("timestamp")
#                 ).dict() | {
#                     "origin": result.get("origin", "template"),
#                     "model": result.get("model")
#                 }
#             else:
#                 logger.error(f"智能体处理失败: {result.get('error', 'Unknown error')}")
#                 return ChatResponse(
#                     success=False,
#                     response="抱歉，我现在无法回答你的问题。请稍后再试。",
#                     agent_name=request.agent_name,
#                     error=result.get("error")
#                 )
#         else:
#             # 智能体不存在
#             logger.warning(f"请求的智能体不存在: {request.agent_name}")
#             return ChatResponse(
#                 success=False,
#                 response=f"智能体 {request.agent_name} 不存在",
#                 agent_name=request.agent_name,
#                 error="Agent not found"
#             )
#
#     except Exception as e:
#         logger.error(f"聊天请求处理出错: {str(e)}")
#         return ChatResponse(
#             success=False,
#             response="服务器内部错误，请稍后再试。",
#             agent_name=request.agent_name,
#             error=str(e)
#         )
#
#
# # 新增: LLM状态检查端点
# @app.get("/api/v1/llm/status")
# async def get_llm_status():
#     """获取LLM服务状态"""
#     try:
#         llm_client = get_llm_client()
#         provider_info = llm_client.get_provider_info()
#         connection_test = await llm_client.test_connection()
#
#         return {
#             "status": "online" if connection_test else "offline",
#             "provider": provider_info["provider"],
#             "model": provider_info["model"],
#             "api_base": provider_info["api_base"],
#             "has_api_key": provider_info["has_api_key"],
#             "connection_test": connection_test,
#             "timestamp": datetime.now().isoformat()
#         }
#     except Exception as e:
#         logger.error(f"LLM状态检查失败: {str(e)}")
#         return {
#             "status": "error",
#             "error": str(e),
#             "timestamp": datetime.now().isoformat()
#         }
#
#
# @app.get("/api/v1/mode")
# async def get_mode():
#     return {
#         "demo_mode": DEMO_MODE,
#         "agents_available": AGENTS_AVAILABLE,
#         "system_type": "real" if (not DEMO_MODE and AGENTS_AVAILABLE) else "mock"
#     }
#
#
# # 新增: 智能体列表端点
# @app.get("/api/v1/agents/list")
# async def get_agents_list():
#     """获取智能体列表"""
#     try:
#         if not agents_system:
#             return {"agents": [], "error": "智能体系统未初始化"}
#
#         agents_list = []
#         for agent_id, agent in agents_system.items():
#             agents_list.append({
#                 "id": agent_id,
#                 "name": agent.name,
#                 "role": agent.role,
#                 "avatar": agent.avatar,
#                 "description": getattr(agent, 'description', f"{agent.role}智能体"),
#                 "status": "active",
#                 "is_mock": getattr(agent, 'is_mock', not AGENTS_AVAILABLE or agent_id != 'tanaka')
#             })
#
#         return agents_list
#     except Exception as e:
#         logger.error(f"获取智能体列表失败: {str(e)}")
#         return {"agents": [], "error": str(e)}
#
#
# @app.get("/api/agents/status")
# async def get_agents_status():
#     """获取智能体状态"""
#     if not agents_system:
#         return JSONResponse({"error": "智能体系统未初始化"})
#
#     agents_status = []
#     for agent_id, agent in agents_system.items():
#         agents_status.append({
#             "agent_id": agent_id,
#             "name": agent.name,
#             "role": agent.role,
#             "avatar": agent.avatar,
#             "emotion": getattr(agent, 'current_emotion', '😊'),
#             "is_mock": getattr(agent, 'is_mock', not AGENTS_AVAILABLE)
#         })
#
#     return JSONResponse({
#         "agents": agents_status,
#         "total_count": len(agents_status),
#         "system_type": "real" if AGENTS_AVAILABLE else "mock"
#     })
#
#
# @app.post("/api/v1/collaboration/multi-agent-chat")
# async def multi_agent_chat(request: MultiAgentChatRequest):
#     """多智能体协作聊天"""
#     try:
#         logger.info(f"多智能体协作请求: {request.active_agents}")
#
#         # 验证智能体ID
#         valid_agents = [agent for agent in request.active_agents if agent in agents_system]
#
#         if len(valid_agents) < 2:
#             return MultiAgentChatResponse(
#                 success=False,
#                 responses=[],
#                 collaboration_mode=request.collaboration_mode,
#                 agents_participated=valid_agents,
#                 final_recommendation="需要至少2个智能体进行协作",
#                 timestamp=datetime.now().isoformat()
#             )
#
#         # 构建会话上下文
#         session_context = {
#             "user_id": request.user_id,
#             "session_id": request.session_id,
#             "scene": request.scene_context,
#             "collaboration_mode": request.collaboration_mode
#         }
#
#         # 执行多智能体协作
#         result = await collaboration_manager.multi_agent_collaboration(
#             user_input=request.message,
#             active_agents=valid_agents,
#             mode=request.collaboration_mode,
#             session_context=session_context
#         )
#
#         return MultiAgentChatResponse(
#             success=True,
#             responses=result["responses"],
#             collaboration_mode=request.collaboration_mode,
#             agents_participated=result["agents_participated"],
#             conflicts=result["conflicts"],
#             final_recommendation=result["final_recommendation"],
#             user_arbitration_needed=result["user_arbitration_needed"],
#             timestamp=datetime.now().isoformat()
#         )
#
#     except Exception as e:
#         logger.error(f"多智能体协作失败: {str(e)}")
#         return MultiAgentChatResponse(
#             success=False,
#             responses=[],
#             collaboration_mode=request.collaboration_mode,
#             agents_participated=[],
#             final_recommendation=f"协作处理失败: {str(e)}",
#             timestamp=datetime.now().isoformat()
#         )
#
#
# @app.get("/api/v1/collaboration/modes")
# async def get_collaboration_modes():
#     """获取协作模式列表"""
#     return {
#         "modes": [
#             {
#                 "id": "discussion",
#                 "name": "自由讨论",
#                 "description": "智能体们就话题进行自由讨论，展现不同观点"
#             },
#             {
#                 "id": "correction",
#                 "name": "协作纠错",
#                 "description": "多个智能体协作纠正语法、用法等问题"
#             },
#             {
#                 "id": "creation",
#                 "name": "协作创作",
#                 "description": "智能体们协作进行内容创作"
#             },
#             {
#                 "id": "analysis",
#                 "name": "深度分析",
#                 "description": "从多个角度深入分析问题"
#             }
#         ]
#     }
#
#
# @app.post("/api/v1/collaboration/resolve-conflict")
# async def resolve_conflict(request: dict):
#     """处理用户仲裁"""
#     try:
#         conflict_id = request.get("conflict_id")
#         user_choice = request.get("user_choice")
#
#         logger.info(f"用户仲裁冲突 {conflict_id}: 选择 {user_choice}")
#
#         # 这里可以记录用户的选择，用于改进协作算法
#         # 暂时简单返回确认
#
#         return {
#             "success": True,
#             "message": "仲裁结果已记录",
#             "conflict_id": conflict_id,
#             "user_choice": user_choice
#         }
#
#     except Exception as e:
#         logger.error(f"处理冲突仲裁失败: {str(e)}")
#         return {
#             "success": False,
#             "error": str(e)
#         }
#
#
# # =================== WebSocket 路由 ===================
#
# @app.websocket("/ws/{session_id}")
# async def websocket_endpoint(websocket: WebSocket, session_id: str):
#     """WebSocket连接处理"""
#     await websocket_manager.connect(websocket, session_id)
#     logger.info(f"📱 WebSocket连接建立: {session_id}")
#
#     try:
#         # 发送欢迎消息
#         await websocket_manager.send_message(session_id, {
#             "type": "system_message",
#             "content": "🎌 欢迎来到日语学习Multi-Agent系统！",
#             "timestamp": str(asyncio.get_event_loop().time())
#         })
#
#         # 发送智能体状态
#         await send_agents_status(session_id)
#
#         while True:
#             # 接收客户端消息
#             data = await websocket.receive_json()
#             await handle_websocket_message(session_id, data)
#
#     except WebSocketDisconnect:
#         logger.info(f"📱 WebSocket连接断开: {session_id}")
#         websocket_manager.disconnect(session_id)
#     except Exception as e:
#         logger.error(f"❌ WebSocket错误 {session_id}: {e}")
#         websocket_manager.disconnect(session_id)
#
#
# async def handle_websocket_message(session_id: str, data: dict):
#     """处理WebSocket消息"""
#     message_type = data.get("type", "")
#
#     try:
#         if message_type == "chat_message":
#             await handle_chat_message(session_id, data)
#         elif message_type == "agent_toggle":
#             await handle_agent_toggle(session_id, data)
#         elif message_type == "scene_change":
#             await handle_scene_change(session_id, data)
#         elif message_type == "ping":
#             await websocket_manager.send_message(session_id, {"type": "pong"})
#         else:
#             await websocket_manager.send_message(session_id, {
#                 "type": "error",
#                 "content": f"未知的消息类型: {message_type}"
#             })
#     except Exception as e:
#         logger.error(f"处理WebSocket消息错误: {e}")
#         await websocket_manager.send_message(session_id, {
#             "type": "error",
#             "content": "处理消息时发生错误"
#         })
#
#
# async def handle_chat_message(session_id: str, data: dict):
#     """处理聊天消息"""
#     user_input = data.get("content", "")
#     active_agents = data.get("active_agents", ["tanaka"])
#     scene = data.get("scene", "grammar")
#
#     if not user_input.strip():
#         return
#
#     logger.info(f"💬 处理聊天消息: {session_id}, 智能体: {active_agents}")
#
#     # 发送思考指示器
#     await websocket_manager.send_message(session_id, {
#         "type": "thinking_indicator",
#         "active": True
#     })
#
#     try:
#         # 使用协作管理器处理消息
#         responses = await collaboration_manager.process_user_input(
#             session_id=session_id,
#             user_input=user_input,
#             active_agents=active_agents,
#             scene=scene
#         )
#
#         # 逐个发送智能体回应
#         for i, response in enumerate(responses):
#             # 添加延迟模拟真实对话
#             await asyncio.sleep(i * 0.5 + 0.5)
#
#             await websocket_manager.send_message(session_id, {
#                 "type": "agent_response",
#                 "agent_id": response["agent_id"],
#                 "agent_name": response["agent_name"],
#                 "content": response["content"],
#                 "emotion": response.get("emotion", "😊"),
#                 "is_mock": response.get("is_mock", False),
#                 "timestamp": str(asyncio.get_event_loop().time())
#             })
#
#         # 发送学习进度更新（模拟）
#         await websocket_manager.send_message(session_id, {
#             "type": "progress_update",
#             "grammar_improvement": 2,
#             "vocabulary_growth": 1,
#             "culture_points": 1 if scene == "culture" else 0
#         })
#
#     finally:
#         # 关闭思考指示器
#         await websocket_manager.send_message(session_id, {
#             "type": "thinking_indicator",
#             "active": False
#         })
#
#
# async def handle_agent_toggle(session_id: str, data: dict):
#     """处理智能体切换"""
#     agent_id = data.get("agent_id")
#     action = data.get("action")  # "activate" or "deactivate"
#
#     if agent_id not in agents_system:
#         await websocket_manager.send_message(session_id, {
#             "type": "error",
#             "content": f"智能体 {agent_id} 不存在"
#         })
#         return
#
#     agent = agents_system[agent_id]
#
#     if action == "activate":
#         # 发送智能体加入消息
#         join_messages = {
#             'tanaka': "失礼します。田中です。皆さんの日本語学習をお手伝いさせていただきます。",
#             'koumi': "やっほー！小美だよ～！一緒に楽しく日本語を練習しよう！",
#             'ai': "こんにちは、アイです。データ分析を通じて、あなたの学習をサポートします。",
#             'yamada': "こんにちは。山田と申します。日本の文化について、色々とお話ししましょう。",
#             'sato': "佐藤だ！試験合格を目指して、しっかりと練習するぞ！",
#             'membot': "学習記録システム起動。あなたの進歩を記録・分析いたします。"
#         }
#
#         message = join_messages.get(agent_id, f"{agent.name}が参加しました。")
#
#         await websocket_manager.send_message(session_id, {
#             "type": "agent_response",
#             "agent_id": agent_id,
#             "agent_name": agent.name,
#             "content": message + "\n\n**中文提示：** 我已准备好帮助您学习日语！",
#             "timestamp": str(asyncio.get_event_loop().time())
#         })
#
#     # 发送更新后的智能体状态
#     await send_agents_status(session_id)
#
#
# async def handle_scene_change(session_id: str, data: dict):
#     """处理场景切换"""
#     scene_id = data.get("scene_id", "grammar")
#
#     scene_info = settings.get_scene_config(scene_id)
#     if not scene_info:
#         scene_info = {"name": scene_id, "description": "自定义场景"}
#
#     await websocket_manager.send_message(session_id, {
#         "type": "scene_changed",
#         "scene_id": scene_id,
#         "scene_name": scene_info.get("name", scene_id),
#         "description": scene_info.get("description", ""),
#         "recommended_agents": scene_info.get("recommended_agents", [])
#     })
#
#
# async def send_agents_status(session_id: str):
#     """发送智能体状态"""
#     agents_status = []
#     for agent_id, agent in agents_system.items():
#         agents_status.append({
#             "agent_id": agent_id,
#             "name": agent.name,
#             "is_active": False,  # 默认不激活
#             "emotion": getattr(agent, 'current_emotion', '😊')
#         })
#
#     await websocket_manager.send_message(session_id, {
#         "type": "agent_status_update",
#         "agents": agents_status,
#         "active_count": 1  # 默认田中先生激活
#     })
#
#
# # =================== 注册API路由（如果可用）===================
#
# if API_ROUTES_AVAILABLE:
#     app.include_router(chat.router, prefix="/api/chat", tags=["聊天"])
#     app.include_router(agents.router, prefix="/api/agents", tags=["智能体"])
#     app.include_router(learning.router, prefix="/api/learning", tags=["学习"])
#     app.include_router(analytics.router, prefix="/api/analytics", tags=["分析"])
#
# # ===================


# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎌 日语学习Multi-Agent系统 - 主应用入口
"""

import asyncio
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Any, Optional

from pydantic import BaseModel

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

# 导入配置和工具
from utils.config import settings
from utils.database import init_database
from utils.websocket_manager import WebSocketManager
from utils.llm_client import get_llm_client

from src.api.routers.novel import router as novel_router

# 首先设置日志和创建logger
from utils.logger import setup_logging

import logging

logger = logging.getLogger(__name__)

DEMO_MODE = False

# 导入智能体系统（全部真实类）
AGENTS_AVAILABLE = False
try:
    from src.core.agents.core_agents.tanaka_sensei import TanakaSensei
    from src.core.agents.core_agents.koumi import KoumiAgent
    from src.core.agents.core_agents.yamada_sensei import YamadaSensei
    from src.core.agents.core_agents.sato_coach import SatoCoach
    from src.core.agents.core_agents.mem_bot import MemBot
    from src.core.agents.core_agents.ai_analyzer import AIAnalyzer

    AGENTS_AVAILABLE = True
    logger.info("✅ 智能体已加载：田中 / 小美 / 山田 / 佐藤 / 记忆管家 / アイ")
except ImportError as e:
    logger.warning(f"⚠️ 智能体模块部分可用: {e}")
    AGENTS_AVAILABLE = False

setup_logging()
logger = logging.getLogger(__name__)


# 添加请求和响应模型
class ChatRequest(BaseModel):
    message: str
    user_id: str
    session_id: str
    agent_name: str = "田中先生"
    scene_context: Optional[str] = "general"


class ChatResponse(BaseModel):
    success: bool
    response: str
    agent_name: str
    learning_points: Optional[List[str]] = []
    suggestions: Optional[List[str]] = []
    timestamp: Optional[str] = None
    error: Optional[str] = None


class MultiAgentChatRequest(BaseModel):
    message: str
    user_id: str
    session_id: str
    active_agents: List[str]  # 多个智能体
    collaboration_mode: str = "discussion"  # discussion, correction, creation, analysis
    scene_context: str = "general"


class AgentResponse(BaseModel):
    agent_id: str
    agent_name: str
    content: str
    confidence: Optional[float] = None
    learning_points: List[str] = []
    suggestions: List[str] = []
    emotion: str = "😊"


class Disagreement(BaseModel):
    topic: str
    agents_involved: List[str]
    positions: Dict[str, str]
    severity: str
    type: Optional[str] = None


class MultiAgentChatResponse(BaseModel):
    success: bool
    responses: List[AgentResponse]
    disagreements: List[Disagreement] = []
    consensus: Optional[str] = None
    final_recommendation: Optional[str] = None
    user_arbitration_needed: bool = False
    session_id: str
    timestamp: str


# 导入API路由 (这些文件稍后实现)
API_ROUTES_AVAILABLE = False
try:
    from src.api.routers import chat, agents, learning, analytics, progress

    # 检查是否有router属性
    if (hasattr(chat, 'router') and hasattr(agents, 'router') and
            hasattr(learning, 'router') and hasattr(analytics, 'router') and
            hasattr(progress, 'router')):
        API_ROUTES_AVAILABLE = True
    else:
        print("⚠️ API路由模块未完全实现，将只启动基础服务")
except ImportError:
    print("⚠️ API路由模块尚未实现，将只启动基础服务")

# 全局变量
websocket_manager = WebSocketManager()
agents_system = None
collaboration_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("🚀 启动日语学习Multi-Agent系统...")

    # 初始化数据库
    await init_database()

    # 初始化智能体系统
    await init_agents_system()

    logger.info("✅ 系统初始化完成")

    yield

    # 关闭时清理
    logger.info("🛑 正在关闭系统...")
    await cleanup_resources()
    logger.info("✅ 系统已安全关闭")


# 创建FastAPI应用
app = FastAPI(
    title="🎌 日语学习Multi-Agent系统",
    description="智能化、游戏化的日语学习平台",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

app.include_router(novel_router, prefix="/api/v1/novel", tags=["novel"])

FRONTEND_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost",
    "http://127.0.0.1",
]

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/static", StaticFiles(directory="frontend"), name="static")


# 在main.py中CORS中间件后添加
@app.middleware("http")
async def add_utf8_header(request, call_next):
    response = await call_next(request)
    if "application/json" in response.headers.get("content-type", ""):
        response.headers["content-type"] = "application/json; charset=utf-8"
    return response


async def cleanup_resources():
    """清理系统资源"""
    try:
        # 关闭LLM客户端
        llm_client = get_llm_client()
        await llm_client.close()
        logger.info("LLM客户端已关闭")
    except Exception as e:
        logger.error(f"关闭LLM客户端时出错: {str(e)}")

    # 关闭所有WebSocket连接
    await websocket_manager.close_all_connections()

    # 保存智能体状态（如果需要）
    if agents_system and AGENTS_AVAILABLE:
        for agent in agents_system.values():
            if hasattr(agent, 'save_state'):
                await agent.save_state()


async def init_agents_system():
    global agents_system, collaboration_manager

    # 1) 若导入失败，直接抛错，阻止静默回退到模板
    if not AGENTS_AVAILABLE:
        raise RuntimeError("智能体模块导入失败：已禁止Mock回退，请修复导入后再启动。")

    # 2) 正常情况下，实例化 6 个真实智能体
    agents_system = {
        'tanaka': TanakaSensei(),
        'koumi': KoumiAgent(),
        'yamada': YamadaSensei(),
        'sato': SatoCoach(),
        'membot': MemBot(),
        'ai': AIAnalyzer(),
    }

    # 3) 保持你现有的协作管理器用法（无需改动其它代码）
    collaboration_manager = MixedCollaborationManager(agents_system)
    logger.info("🤖 智能体系统初始化完成（全部真实AI，已禁用Mock回退）")


async def create_mock_agents():
    """创建模拟智能体系统"""
    return {
        'tanaka': MockAgent('tanaka', '田中先生', '语法专家', '👨‍🏫'),
        'koumi': MockAgent('koumi', '小美', '对话伙伴', '👧'),
        'ai': MockAgent('ai', 'アイ', '分析师', '🤖'),
        'yamada': MockAgent('yamada', '山田先生', '文化专家', '🎌'),
        'sato': MockAgent('sato', '佐藤教练', '考试专家', '🎯'),
        'membot': MockAgent('membot', '记忆管家', '学习记录', '🧠')
    }


class MockAgent:
    """模拟智能体类"""

    def __init__(self, agent_id: str, name: str, role: str, avatar: str):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.avatar = avatar
        self.current_emotion = "😊"

    async def process_user_input(self, user_input: str, session_context: dict, scene: str = "grammar"):
        """模拟处理用户输入"""
        # 模拟思考时间
        await asyncio.sleep(0.5)

        # 基于智能体类型返回不同的模拟回应
        mock_responses = {
            'tanaka': f"語法分析：「{user_input}」の文法構造を確認しましょう。\n\n**中文提示：** 让我们分析这个句子的语法结构。",
            'koumi': f"そうなんだ！「{user_input}」って面白い表現だね～\n\n**中文提示：** 这是个很有趣的表达呢！",
            'ai': f"数据分析：输入文本长度 {len(user_input)} 字符，复杂度评分：中等。\n\n**学习建议：** 建议加强语法练习。",
            'yamada': f"「{user_input}」には日本の文化的背景がありますね。\n\n**文化解释：** 这个表达背后有日本文化背景。",
            'sato': f"JLPT対策：「{user_input}」はN3レベルの表現です！\n\n**考试要点：** 这是N3级别的重要表达！",
            'membot': f"学習記録更新：「{user_input}」を記録しました。\n\n**进度更新：** 已记录您的学习内容。"
        }

        content = mock_responses.get(self.agent_id, f"{self.name}正在思考中...")

        return {
            "content": content,
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "emotion": self.current_emotion,
            "is_mock": True
        }

    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """为了兼容真实智能体接口而添加的方法"""
        response = await self.process_user_input(message, context or {})
        return {
            "response": response["content"],
            "agent_name": self.name,
            "success": True,
            "learning_points": [f"模拟学习点: {message[:20]}..."],
            "suggestions": [f"建议练习更多{self.role}相关内容"],
            "timestamp": datetime.now().isoformat(),
            "origin": "mock"
        }


class MultiAgentCollaborationHandler:
    """多智能体协作处理器"""

    def __init__(self, agents_system):
        self.agents = agents_system
        self.agent_name_mapping = {
            'tanaka': '田中先生',
            'koumi': '小美',
            'ai': 'アイ',
            'yamada': '山田先生',
            'sato': '佐藤教练',
            'membot': 'MemBot'
        }

    async def process_collaboration(self, request: MultiAgentChatRequest) -> MultiAgentChatResponse:
        """处理多智能体协作请求"""

        # 验证智能体
        if len(request.active_agents) < 2:
            raise HTTPException(
                status_code=400,
                detail="至少需要2个智能体进行协作"
            )

        # 验证智能体ID
        invalid_agents = [agent for agent in request.active_agents if agent not in self.agents]
        if invalid_agents:
            raise HTTPException(
                status_code=400,
                detail=f"无效的智能体ID: {invalid_agents}"
            )

        try:
            # 1. 获取所有智能体的响应
            responses = await self._get_agent_responses(request)

            # 2. 检测分歧
            disagreements = await self._detect_disagreements(responses, request.message)

            # 3. 生成共识和建议
            consensus, final_recommendation = await self._generate_consensus(
                responses, disagreements, request.collaboration_mode
            )

            # 4. 确定是否需要用户仲裁
            user_arbitration_needed = len(disagreements) > 0 and any(
                d.severity in ['high', 'critical'] for d in disagreements
            )

            return MultiAgentChatResponse(
                success=True,
                responses=responses,
                disagreements=disagreements,
                consensus=consensus,
                final_recommendation=final_recommendation,
                user_arbitration_needed=user_arbitration_needed,
                session_id=request.session_id,
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"协作处理失败: {str(e)}")

    async def _get_agent_responses(self, request: MultiAgentChatRequest) -> List[AgentResponse]:
        """获取所有智能体的响应"""
        responses = []

        # 构建会话上下文
        session_context = {
            "user_id": request.user_id,
            "session_id": request.session_id,
            "scene": request.scene_context,
            "collaboration_mode": request.collaboration_mode,
            "history": []  # 可以从数据库加载历史记录
        }

        # 并发获取所有智能体响应
        tasks = []
        for agent_id in request.active_agents:
            task = self._get_single_agent_response(
                agent_id, request.message, session_context
            )
            tasks.append(task)

        # 等待所有响应
        agent_results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        for i, result in enumerate(agent_results):
            agent_id = request.active_agents[i]

            if isinstance(result, Exception):
                # 处理失败的智能体
                responses.append(AgentResponse(
                    agent_id=agent_id,
                    agent_name=self.agent_name_mapping.get(agent_id, agent_id),
                    content=f"抱歉，我暂时无法回应。错误：{str(result)}",
                    confidence=0.0,
                    emotion="😔"
                ))
            else:
                responses.append(result)

        return responses

    async def _get_single_agent_response(
            self,
            agent_id: str,
            message: str,
            session_context: Dict[str, Any]
    ) -> AgentResponse:
        """获取单个智能体的响应"""

        try:
            # 获取智能体实例
            agent = self.agents[agent_id]

            # 调用智能体处理
            result = await agent.process_user_input(
                user_input=message,
                session_context=session_context,
                scene=session_context.get("scene", "general")
            )

            # 构建响应
            return AgentResponse(
                agent_id=agent_id,
                agent_name=self.agent_name_mapping.get(agent_id, agent_id),
                content=result.get("content", ""),
                confidence=result.get("confidence", 0.8),
                learning_points=result.get("learning_points", []),
                suggestions=result.get("suggestions", []),
                emotion=result.get("emotion", "😊")
            )

        except Exception as e:
            raise Exception(f"智能体 {agent_id} 处理失败: {str(e)}")

    async def _detect_disagreements(
            self,
            responses: List[AgentResponse],
            user_input: str
    ) -> List[Disagreement]:
        """检测智能体间的分歧"""
        disagreements = []

        # 1. 基于智能体特性的预期分歧
        agent_names = [r.agent_name for r in responses]

        # 田中先生 vs 小美的教学方法分歧
        if '田中先生' in agent_names and '小美' in agent_names:
            disagreements.append(Disagreement(
                topic='教学方法偏好',
                agents_involved=['田中先生', '小美'],
                positions={
                    '田中先生': '严格正式的教学方法',
                    '小美': '轻松友好的交流方式'
                },
                severity='medium',
                type='personality_based'
            ))

        # 2. 内容分析检测实际分歧
        content_disagreements = await self._analyze_content_disagreements(responses)
        disagreements.extend(content_disagreements)

        return disagreements

    async def _analyze_content_disagreements(
            self,
            responses: List[AgentResponse]
    ) -> List[Disagreement]:
        """分析内容中的实际分歧"""
        disagreements = []

        # 分析语气和立场
        positive_agents = []
        negative_agents = []

        for response in responses:
            content = response.content.lower()

            # 积极关键词
            positive_keywords = ['正确', '对', '好', '推荐', '应该', 'です', 'ます']
            # 消极关键词
            negative_keywords = ['错误', '不对', '不好', '不推荐', '不应该', '问题']

            positive_score = sum(1 for word in positive_keywords if word in content)
            negative_score = sum(1 for word in negative_keywords if word in content)

            if positive_score > negative_score:
                positive_agents.append(response.agent_name)
            elif negative_score > positive_score:
                negative_agents.append(response.agent_name)

        # 如果有明显的正负分歧
        if positive_agents and negative_agents:
            disagreements.append(Disagreement(
                topic='表达正确性评估',
                agents_involved=positive_agents + negative_agents,
                positions={
                    **{agent: '积极评价' for agent in positive_agents},
                    **{agent: '消极评价' for agent in negative_agents}
                },
                severity='high',
                type='content_assessment'
            ))

        return disagreements

    async def _generate_consensus(
            self,
            responses: List[AgentResponse],
            disagreements: List[Disagreement],
            collaboration_mode: str
    ) -> tuple[Optional[str], Optional[str]]:
        """生成协作共识和最终建议"""

        try:
            # 如果没有分歧，尝试生成共识
            if not disagreements:
                consensus_points = []
                for response in responses:
                    if response.learning_points:
                        consensus_points.extend(response.learning_points)

                if consensus_points:
                    consensus = f"智能体们一致认为：{', '.join(set(consensus_points[:3]))}"
                else:
                    consensus = "智能体们对此问题有相似的观点"
            else:
                consensus = f"检测到 {len(disagreements)} 个观点分歧，需要进一步讨论"

            # 生成最终建议
            all_suggestions = []
            for response in responses:
                all_suggestions.extend(response.suggestions)

            if all_suggestions:
                final_recommendation = f"综合建议：{', '.join(set(all_suggestions[:3]))}"
            else:
                final_recommendation = "建议继续深入学习相关知识点"

            return consensus, final_recommendation

        except Exception as e:
            return None, f"建议生成过程中出现错误：{str(e)}"


class MixedCollaborationManager:
    """混合协作管理器 - 支持真实和模拟智能体"""

    def __init__(self, agents):
        self.agents = agents

    async def process_user_input(self, session_id: str, user_input: str, active_agents: list, scene: str):
        """处理用户输入 - 混合模式"""
        responses = []

        for agent_id in active_agents:
            if agent_id in self.agents:
                agent = self.agents[agent_id]

                try:
                    if hasattr(agent, 'process_user_input') and not hasattr(agent, 'is_mock'):
                        # 真实智能体（如田中先生）
                        response = await agent.process_user_input(
                            user_input=user_input,
                            session_context={"session_id": session_id},
                            scene=scene
                        )
                        responses.append(response)
                    else:
                        # 模拟智能体
                        response = await agent.process_user_input(user_input, {}, scene)
                        responses.append(response)

                except Exception as e:
                    logger.error(f"❌ 智能体 {agent_id} 处理失败: {e}")
                    # 降级到简单回应
                    fallback_response = {
                        "content": f"{agent.name}正在思考中，请稍等...\n\n**中文提示：** 智能体暂时无法回应。",
                        "agent_id": agent_id,
                        "agent_name": agent.name,
                        "emotion": "🤔",
                        "error": True
                    }
                    responses.append(fallback_response)

        return responses

    async def multi_agent_collaboration(
            self,
            user_input: str,
            active_agents: List[str],
            mode: str = "discussion",
            session_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """多智能体协作处理"""

        responses = []
        conflicts = []

        # 1. 获取所有智能体的初始回复
        for agent_id in active_agents:
            if agent_id in self.agents:
                try:
                    agent = self.agents[agent_id]
                    response = await agent.process_user_input(
                        user_input=user_input,
                        session_context=session_context or {},
                        scene=mode
                    )

                    # 添加额外信息
                    response['agent_id'] = agent_id
                    response['confidence'] = 0.8  # 可以后续优化
                    response['timestamp'] = datetime.now().isoformat()

                    responses.append(response)

                except Exception as e:
                    logger.error(f"智能体 {agent_id} 处理失败: {e}")
                    # 添加错误回复
                    responses.append({
                        "content": f"{self.agents[agent_id].name}正在思考中，请稍等...",
                        "agent_id": agent_id,
                        "agent_name": self.agents[agent_id].name,
                        "emotion": "🤔",
                        "error": True,
                        "confidence": 0.0,
                        "timestamp": datetime.now().isoformat()
                    })

        # 2. 简单的冲突检测
        conflicts = self._detect_simple_conflicts(responses)

        # 3. 生成最终建议
        final_recommendation = self._generate_collaboration_summary(responses, mode)

        return {
            "responses": responses,
            "conflicts": conflicts,
            "final_recommendation": final_recommendation,
            "user_arbitration_needed": len(conflicts) > 0,
            "collaboration_mode": mode,
            "agents_participated": active_agents
        }

    def _detect_simple_conflicts(self, responses: List[Dict]) -> List[Dict]:
        """简单的冲突检测"""
        conflicts = []

        # 检查是否有智能体给出明显不同的建议
        for i, resp1 in enumerate(responses):
            for j, resp2 in enumerate(responses[i + 1:], i + 1):
                content1 = resp1.get('content', '').lower()
                content2 = resp2.get('content', '').lower()

                # 简单的冲突关键字检测
                conflict_pairs = [
                    ('正确', '错误'), ('对', '不对'), ('应该', '不应该'),
                    ('建议', '不建议'), ('推荐', '不推荐')
                ]

                for word1, word2 in conflict_pairs:
                    if word1 in content1 and word2 in content2:
                        conflicts.append({
                            "agent1": resp1.get('agent_id', ''),
                            "agent2": resp2.get('agent_id', ''),
                            "conflict_point": f"关于用户问题的不同观点",
                            "conflict_id": f"conflict_{i}_{j}"
                        })
                        break

        return conflicts

    def _generate_collaboration_summary(self, responses: List[Dict], mode: str) -> str:
        """生成协作总结"""
        if not responses:
            return "暂时无法生成协作总结。"

        agent_names = [r.get('agent_name', '智能体') for r in responses]

        if mode == "correction":
            return f"🔍 协作纠错总结：{', '.join(agent_names)}共同分析了您的问题，提供了专业的修正建议。"
        elif mode == "creation":
            return f"🎨 协作创作总结：{', '.join(agent_names)}协作完成了创作任务，展现了不同的创意角度。"
        elif mode == "analysis":
            return f"🔍 协作分析总结：{', '.join(agent_names)}从多个角度深入分析了问题，提供了全面的见解。"
        else:  # discussion
            return f"💬 协作讨论总结：{', '.join(agent_names)}进行了深入讨论，分享了各自的专业观点。"


# 创建协作处理器实例
collaboration_handler = None


def get_collaboration_handler():
    global collaboration_handler
    if collaboration_handler is None and agents_system:
        collaboration_handler = MultiAgentCollaborationHandler(agents_system)
    return collaboration_handler


# =================== 路由定义 ===================

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回主页面"""
    html_file = Path("frontend/pages/index.html")
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(encoding='utf-8'))
    else:
        return HTMLResponse(content="<h1>欢迎使用日语学习Multi-Agent系统</h1><p>请确保前端文件存在</p>")


@app.get("/multi-agent")
async def multi_agent_page():
    """多智能体协作页面"""
    html_file = Path("frontend/multi_agent_collaboration.html")
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(encoding='utf-8'))
    else:
        return HTMLResponse(content="<h1>多智能体协作页面</h1><p>请确保前端文件存在</p>")


@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return JSONResponse({
        "status": "healthy",
        "system": "Japanese Learning Multi-Agent System",
        "version": "1.0.0",
        "agents_available": AGENTS_AVAILABLE,
        "api_routes_available": API_ROUTES_AVAILABLE,
        "websocket": "ready"
    })


# 新增: 聊天API端点
@app.post("/api/v1/chat/send")
async def send_chat_message(request: ChatRequest):
    """发送聊天消息到指定智能体"""
    try:
        logger.info(f"收到聊天请求: 用户={request.user_id}, 智能体={request.agent_name}")

        # 将agent_name映射到agent_id
        agent_mapping = {
            "田中先生": "tanaka",
            "小美": "koumi",
            "アイ": "ai",
            "山田先生": "yamada",
            "佐藤教练": "sato",
            "记忆管家": "membot"
        }

        agent_id = agent_mapping.get(request.agent_name, request.agent_name.lower())

        # 获取指定的智能体
        if agent_id in agents_system:
            agent = agents_system[agent_id]

            # 构建上下文
            context = {
                "user_id": request.user_id,
                "session_id": request.session_id,
                "scene_context": request.scene_context,
                "timestamp": datetime.now().isoformat()
            }

            # 处理消息
            result = await agent.process_message(
                message=request.message,
                context=context
            )

            if result.get("success", True):
                return ChatResponse(
                    success=True,
                    response=result["response"],
                    agent_name=request.agent_name,
                    learning_points=result.get("learning_points", []),
                    suggestions=result.get("suggestions", []),
                    timestamp=result.get("timestamp")
                ).dict() | {
                    "origin": result.get("origin", "template"),
                    "model": result.get("model")
                }
            else:
                logger.error(f"智能体处理失败: {result.get('error', 'Unknown error')}")
                return ChatResponse(
                    success=False,
                    response="抱歉，我现在无法回答你的问题。请稍后再试。",
                    agent_name=request.agent_name,
                    error=result.get("error")
                )
        else:
            # 智能体不存在
            logger.warning(f"请求的智能体不存在: {request.agent_name}")
            return ChatResponse(
                success=False,
                response=f"智能体 {request.agent_name} 不存在",
                agent_name=request.agent_name,
                error="Agent not found"
            )

    except Exception as e:
        logger.error(f"聊天请求处理出错: {str(e)}")
        return ChatResponse(
            success=False,
            response="服务器内部错误，请稍后再试。",
            agent_name=request.agent_name,
            error=str(e)
        )


# 新增: 多智能体协作API端点
@app.post("/api/v1/chat/multi-agent-collaboration", response_model=MultiAgentChatResponse)
async def multi_agent_collaboration(request: MultiAgentChatRequest):
    """
    多智能体协作端点

    处理多个智能体的协作对话，包括：
    - 获取所有智能体的响应
    - 检测智能体间的分歧
    - 生成协作共识
    - 确定是否需要用户仲裁
    """
    logger.info(f"收到协作请求: message={request.message}, agents={request.active_agents}")

    try:
        # 验证输入
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="消息不能为空")

        if len(request.active_agents) < 2:
            raise HTTPException(status_code=400, detail="至少需要2个智能体进行协作")

        # 获取协作处理器
        handler = get_collaboration_handler()
        logger.info(f"协作处理器状态: {handler is not None}")
        if not handler:
            logger.error("协作处理器未初始化")
            raise HTTPException(status_code=500, detail="协作处理器未初始化")

        # 处理协作请求
        result = await handler.process_collaboration(request)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"多智能体协作处理失败：{str(e)}"
        )


# 新增: LLM状态检查端点
@app.get("/api/v1/llm/status")
async def get_llm_status():
    """获取LLM服务状态"""
    try:
        llm_client = get_llm_client()
        provider_info = llm_client.get_provider_info()
        connection_test = await llm_client.test_connection()

        return {
            "status": "online" if connection_test else "offline",
            "provider": provider_info["provider"],
            "model": provider_info["model"],
            "api_base": provider_info["api_base"],
            "has_api_key": provider_info["has_api_key"],
            "connection_test": connection_test,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"LLM状态检查失败: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.get("/api/v1/mode")
async def get_mode():
    return {
        "demo_mode": DEMO_MODE,
        "agents_available": AGENTS_AVAILABLE,
        "system_type": "real" if (not DEMO_MODE and AGENTS_AVAILABLE) else "mock"
    }


# 新增: 智能体列表端点
@app.get("/api/v1/agents/list")
async def get_agents_list():
    """获取智能体列表"""
    try:
        if not agents_system:
            return {"agents": [], "error": "智能体系统未初始化"}

        agents_list = []
        for agent_id, agent in agents_system.items():
            agents_list.append({
                "id": agent_id,
                "name": agent.name,
                "role": agent.role,
                "avatar": agent.avatar,
                "description": getattr(agent, 'description', f"{agent.role}智能体"),
                "status": "active",
                "is_mock": getattr(agent, 'is_mock', not AGENTS_AVAILABLE or agent_id != 'tanaka')
            })

        return agents_list
    except Exception as e:
        logger.error(f"获取智能体列表失败: {str(e)}")
        return {"agents": [], "error": str(e)}


@app.get("/api/agents/status")
async def get_agents_status():
    """获取智能体状态"""
    if not agents_system:
        return JSONResponse({"error": "智能体系统未初始化"})

    agents_status = []
    for agent_id, agent in agents_system.items():
        agents_status.append({
            "agent_id": agent_id,
            "name": agent.name,
            "role": agent.role,
            "avatar": agent.avatar,
            "emotion": getattr(agent, 'current_emotion', '😊'),
            "is_mock": getattr(agent, 'is_mock', not AGENTS_AVAILABLE)
        })

    return JSONResponse({
        "agents": agents_status,
        "total_count": len(agents_status),
        "system_type": "real" if AGENTS_AVAILABLE else "mock"
    })


@app.get("/api/v1/collaboration/modes")
async def get_collaboration_modes():
    """获取协作模式列表"""
    return {
        "modes": [
            {
                "id": "discussion",
                "name": "自由讨论",
                "description": "智能体们就话题进行自由讨论，展现不同观点"
            },
            {
                "id": "correction",
                "name": "协作纠错",
                "description": "多个智能体协作纠正语法、用法等问题"
            },
            {
                "id": "creation",
                "name": "协作创作",
                "description": "智能体们协作进行内容创作"
            },
            {
                "id": "analysis",
                "name": "深度分析",
                "description": "从多个角度深入分析问题"
            }
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "progress_tracking": True,
        "message": "日语学习系统运行正常"
    }


# 添加到main.py末尾
@app.get("/api/v1/progress/summary")
async def get_progress_summary(user_id: str = "demo_user"):
    """获取学习进度摘要"""
    try:
        import sys
        sys.path.append('src')
        from data.repositories.progress_tracker import ProgressTracker

        tracker = ProgressTracker()
        summary = tracker.get_user_progress_summary(user_id)

        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/v1/progress/track")
async def track_learning_progress(
        user_input: str,
        agent_responses: dict,
        session_id: str,
        scene_context: str = "general"
):
    """手动追踪学习进度"""
    try:
        import sys
        sys.path.append('src')
        from data.repositories.progress_tracker import ProgressTracker

        tracker = ProgressTracker()
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
        return {
            "success": False,
            "error": str(e)
        }


# =================== WebSocket 路由 ===================

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket连接处理"""
    await websocket_manager.connect(websocket, session_id)
    logger.info(f"📱 WebSocket连接建立: {session_id}")

    try:
        # 发送欢迎消息
        await websocket_manager.send_message(session_id, {
            "type": "system_message",
            "content": "🎌 欢迎来到日语学习Multi-Agent系统！",
            "timestamp": str(asyncio.get_event_loop().time())
        })

        # 发送智能体状态
        await send_agents_status(session_id)

        while True:
            # 接收客户端消息
            data = await websocket.receive_json()
            await handle_websocket_message(session_id, data)

    except WebSocketDisconnect:
        logger.info(f"📱 WebSocket连接断开: {session_id}")
        websocket_manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"❌ WebSocket错误 {session_id}: {e}")
        websocket_manager.disconnect(session_id)


async def handle_websocket_message(session_id: str, data: dict):
    """处理WebSocket消息"""
    message_type = data.get("type", "")

    try:
        if message_type == "chat_message":
            await handle_chat_message(session_id, data)
        elif message_type == "agent_toggle":
            await handle_agent_toggle(session_id, data)
        elif message_type == "scene_change":
            await handle_scene_change(session_id, data)
        elif message_type == "ping":
            await websocket_manager.send_message(session_id, {"type": "pong"})
        else:
            await websocket_manager.send_message(session_id, {
                "type": "error",
                "content": f"未知的消息类型: {message_type}"
            })
    except Exception as e:
        logger.error(f"处理WebSocket消息错误: {e}")
        await websocket_manager.send_message(session_id, {
            "type": "error",
            "content": "处理消息时发生错误"
        })


async def handle_chat_message(session_id: str, data: dict):
    """处理聊天消息"""
    user_input = data.get("content", "")
    active_agents = data.get("active_agents", ["tanaka"])
    scene = data.get("scene", "grammar")

    if not user_input.strip():
        return

    logger.info(f"💬 处理聊天消息: {session_id}, 智能体: {active_agents}")

    # 发送思考指示器
    await websocket_manager.send_message(session_id, {
        "type": "thinking_indicator",
        "active": True
    })

    try:
        # 使用协作管理器处理消息
        responses = await collaboration_manager.process_user_input(
            session_id=session_id,
            user_input=user_input,
            active_agents=active_agents,
            scene=scene
        )

        # 逐个发送智能体回应
        for i, response in enumerate(responses):
            # 添加延迟模拟真实对话
            await asyncio.sleep(i * 0.5 + 0.5)

            await websocket_manager.send_message(session_id, {
                "type": "agent_response",
                "agent_id": response["agent_id"],
                "agent_name": response["agent_name"],
                "content": response["content"],
                "emotion": response.get("emotion", "😊"),
                "is_mock": response.get("is_mock", False),
                "timestamp": str(asyncio.get_event_loop().time())
            })

        # 发送学习进度更新（模拟）
        await websocket_manager.send_message(session_id, {
            "type": "progress_update",
            "grammar_improvement": 2,
            "vocabulary_growth": 1,
            "culture_points": 1 if scene == "culture" else 0
        })

    finally:
        # 关闭思考指示器
        await websocket_manager.send_message(session_id, {
            "type": "thinking_indicator",
            "active": False
        })


async def handle_agent_toggle(session_id: str, data: dict):
    """处理智能体切换"""
    agent_id = data.get("agent_id")
    action = data.get("action")  # "activate" or "deactivate"

    if agent_id not in agents_system:
        await websocket_manager.send_message(session_id, {
            "type": "error",
            "content": f"智能体 {agent_id} 不存在"
        })
        return

    agent = agents_system[agent_id]

    if action == "activate":
        # 发送智能体加入消息
        join_messages = {
            'tanaka': "失礼します。田中です。皆さんの日本語学習をお手伝いさせていただきます。",
            'koumi': "やっほー！小美だよ～！一緒に楽しく日本語を練習しよう！",
            'ai': "こんにちは、アイです。データ分析を通じて、あなたの学習をサポートします。",
            'yamada': "こんにちは。山田と申します。日本の文化について、色々とお話ししましょう。",
            'sato': "佐藤だ！試験合格を目指して、しっかりと練習するぞ！",
            'membot': "学習記録システム起動。あなたの進歩を記録・分析いたします。"
        }

        message = join_messages.get(agent_id, f"{agent.name}が参加しました。")

        await websocket_manager.send_message(session_id, {
            "type": "agent_response",
            "agent_id": agent_id,
            "agent_name": agent.name,
            "content": message + "\n\n**中文提示：** 我已准备好帮助您学习日语！",
            "timestamp": str(asyncio.get_event_loop().time())
        })

    # 发送更新后的智能体状态
    await send_agents_status(session_id)


async def handle_scene_change(session_id: str, data: dict):
    """处理场景切换"""
    scene_id = data.get("scene_id", "grammar")

    scene_info = settings.get_scene_config(scene_id)
    if not scene_info:
        scene_info = {"name": scene_id, "description": "自定义场景"}

    await websocket_manager.send_message(session_id, {
        "type": "scene_changed",
        "scene_id": scene_id,
        "scene_name": scene_info.get("name", scene_id),
        "description": scene_info.get("description", ""),
        "recommended_agents": scene_info.get("recommended_agents", [])
    })


async def send_agents_status(session_id: str):
    """发送智能体状态"""
    agents_status = []
    for agent_id, agent in agents_system.items():
        agents_status.append({
            "agent_id": agent_id,
            "name": agent.name,
            "is_active": False,  # 默认不激活
            "emotion": getattr(agent, 'current_emotion', '😊')
        })

    await websocket_manager.send_message(session_id, {
        "type": "agent_status_update",
        "agents": agents_status,
        "active_count": 1  # 默认田中先生激活
    })


# =================== 注册API路由（如果可用）===================

if API_ROUTES_AVAILABLE:
    app.include_router(chat.router, prefix="/api/chat", tags=["聊天"])
    app.include_router(agents.router, prefix="/api/agents", tags=["智能体"])
    app.include_router(learning.router, prefix="/api/learning", tags=["学习"])
    app.include_router(analytics.router, prefix="/api/analytics", tags=["分析"])
    app.include_router(progress.router, tags=["进度追踪"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

# 简单的进度追踪端点
@app.post("/api/v1/progress/track-simple")
async def track_simple(
    user_input: str, 
    session_id: str,
    agent_name: str = "unknown",
    agent_content: str = ""
):
    try:
        import sys
        sys.path.append('src')
        from data.repositories.progress_tracker import ProgressTracker
        
        tracker = ProgressTracker()
        agent_responses = {
            agent_name: {
                'content': agent_content,
                'agent_name': agent_name
            }
        }
        
        learning_data = tracker.extract_learning_data(
            user_input, agent_responses, session_id, 'general'
        )
        
        return {
            'success': True,
            'message': '学习数据追踪成功',
            'learning_data': {
                'grammar_points': len(learning_data.get('grammar_points', [])),
                'vocabulary': len(learning_data.get('vocabulary', [])),
                'cultural_topics': len(learning_data.get('cultural_topics', []))
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


@app.post("/api/v1/progress/track-working")
async def track_progress_simple(
    user_input: str,
    agent_name: str,
    agent_content: str,
    session_id: str
):
    try:
        import sys
        sys.path.append('src')
        from data.repositories.progress_tracker import ProgressTracker
        
        tracker = ProgressTracker()
        agent_responses = {
            agent_name: {
                'content': agent_content,
                'agent_name': agent_name
            }
        }
        
        learning_data = tracker.extract_learning_data(
            user_input, agent_responses, session_id, 'general'
        )
        
        return {
            'success': True,
            'message': '学习数据追踪成功',
            'learning_data': {
                'grammar_points': len(learning_data.get('grammar_points', [])),
                'vocabulary': len(learning_data.get('vocabulary', [])),
                'cultural_topics': len(learning_data.get('cultural_topics', []))
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
