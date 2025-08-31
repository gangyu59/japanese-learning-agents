#!/usr/bin/env python3
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

# 首先设置日志和创建logger
from utils.logger import setup_logging

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


# 导入API路由 (这些文件稍后实现)
API_ROUTES_AVAILABLE = False
try:
    from src.api.routers import chat, agents, learning, analytics

    # 检查是否有router属性
    if (hasattr(chat, 'router') and hasattr(agents, 'router') and
            hasattr(learning, 'router') and hasattr(analytics, 'router')):
        API_ROUTES_AVAILABLE = True
    else:
        print("⚠️  API路由模块未完全实现，将只启动基础服务")
except ImportError:
    print("⚠️  API路由模块尚未实现，将只启动基础服务")

# 导入智能体系统 (现在田中先生已实现)
AGENTS_AVAILABLE = False
try:
    from src.core.agents.core_agents.tanaka_sensei import TanakaSensei

    # 其他智能体暂时使用模拟版本
    AGENTS_AVAILABLE = True
    logger.info("✅ 田中先生智能体已加载")
except ImportError as e:
    logger.warning(f"⚠️  智能体模块部分可用: {e}")
    AGENTS_AVAILABLE = False

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
    """初始化智能体系统"""
    global agents_system, collaboration_manager

    if AGENTS_AVAILABLE:
        # 初始化智能体 - 田中先生使用真实实现，其他使用模拟
        agents_system = {
            'tanaka': TanakaSensei(),  # 真实的田中先生
            'koumi': MockAgent('koumi', '小美', '对话伙伴', '👧'),
            'ai': MockAgent('ai', 'アイ', '分析师', '🤖'),
            'yamada': MockAgent('yamada', '山田先生', '文化专家', '🎌'),
            'sato': MockAgent('sato', '佐藤教练', '考试专家', '🎯'),
            'membot': MockAgent('membot', '记忆管家', '学习记录', '🧠')
        }

        # 初始化协作管理器
        collaboration_manager = MixedCollaborationManager(agents_system)

        logger.info("🤖 混合智能体系统初始化完成（田中先生：真实AI，其他：模拟）")
    else:
        # 使用模拟智能体系统
        agents_system = await create_mock_agents()
        # collaboration_manager = MockCollaborationManager(agents_system)

        logger.info("🎭 模拟智能体系统初始化完成")


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
            "timestamp": datetime.now().isoformat()
        }


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
                    # 降级到简单响应
                    fallback_response = {
                        "content": f"{agent.name}正在思考中，请稍等...\n\n**中文提示：** 智能体暂时无法回应。",
                        "agent_id": agent_id,
                        "agent_name": agent.name,
                        "emotion": "🤔",
                        "error": True
                    }
                    responses.append(fallback_response)

        return responses


# =================== 路由定义 ===================

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回主页面"""
    html_file = Path("frontend/pages/index.html")

    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(encoding='utf-8'))
    else:
        # 如果主页面不存在，返回简单的临时页面
        return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎌 日语学习Multi-Agent系统</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            text-align: center; 
            padding: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            margin: 0;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            padding: 40px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            max-width: 600px;
            margin: 0 auto;
        }
        h1 { font-size: 2.5em; margin-bottom: 20px; }
        p { font-size: 1.2em; margin-bottom: 15px; }
        .status { 
            background: rgba(255, 255, 255, 0.2); 
            padding: 20px; 
            border-radius: 10px; 
            margin: 20px 0;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎌 日语学习Multi-Agent系统</h1>
        <p>智能化、游戏化的日语学习平台</p>

        <div class="status">
            <h3>📊 系统状态</h3>
            <p>🚀 后端服务：运行中</p>
            <p>🤖 智能体系统：""" + ("✅ 已加载" if AGENTS_AVAILABLE else "🎭 模拟模式") + """</p>
            <p>📡 WebSocket：准备就绪</p>
        </div>

        <div class="status">
            <h3>🔧 开发进度</h3>
            <p>✅ 项目结构创建完成</p>
            <p>✅ 基础服务启动成功</p>
            <p>🔄 前端界面开发中...</p>
            <p>🔄 智能体系统开发中...</p>
        </div>

        <p style="margin-top: 30px;">
            <strong>下一步：</strong>完善前端界面和智能体功能
        </p>

        <p style="font-size: 0.9em; opacity: 0.8;">
            访问 <a href="/docs" style="color: #fff;">/docs</a> 查看API文档
        </p>
    </div>

    <script>
        console.log('🎌 日语学习Multi-Agent系统已启动');

        // 简单的WebSocket连接测试
        if (window.WebSocket) {
            console.log('✅ WebSocket支持已启用');
        } else {
            console.log('❌ 浏览器不支持WebSocket');
        }
    </script>
</body>
</html>
        """)


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
                # 记录成功的对话
                logger.info(f"智能体 {request.agent_name} 成功处理消息")

                return ChatResponse(
                    success=True,
                    response=result["response"],
                    agent_name=request.agent_name,
                    learning_points=result.get("learning_points", []),
                    suggestions=result.get("suggestions", []),
                    timestamp=result.get("timestamp")
                )
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

# ===================