#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎌 WebSocket连接管理器
"""

import json
import logging
from typing import Dict, Optional
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket连接管理器"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """建立WebSocket连接"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"📱 WebSocket连接建立: {session_id}")

    def disconnect(self, session_id: str):
        """断开WebSocket连接"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"📱 WebSocket连接断开: {session_id}")

    async def send_message(self, session_id: str, message: dict):
        """发送消息给指定会话"""
        if session_id in self.active_connections:
            try:
                websocket = self.active_connections[session_id]
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logger.error(f"❌ 发送WebSocket消息失败 {session_id}: {e}")
                self.disconnect(session_id)

    async def broadcast_message(self, message: dict, exclude_session: Optional[str] = None):
        """广播消息给所有连接"""
        disconnected = []

        for session_id, websocket in self.active_connections.items():
            if exclude_session and session_id == exclude_session:
                continue

            try:
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logger.error(f"❌ 广播消息失败 {session_id}: {e}")
                disconnected.append(session_id)

        # 清理失效连接
        for session_id in disconnected:
            self.disconnect(session_id)

    async def close_all_connections(self):
        """关闭所有WebSocket连接"""
        for session_id, websocket in list(self.active_connections.items()):
            try:
                await websocket.close()
            except Exception as e:
                logger.error(f"❌ 关闭WebSocket连接失败 {session_id}: {e}")

        self.active_connections.clear()
        logger.info("🛑 所有WebSocket连接已关闭")

    def get_connection_count(self) -> int:
        """获取活跃连接数"""
        return len(self.active_connections)

    def is_connected(self, session_id: str) -> bool:
        """检查指定会话是否连接"""
        return session_id in self.active_connections