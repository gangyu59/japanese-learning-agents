# -*- coding: utf-8 -*-
from typing import List, Dict, Any, Optional

class DummyLLMClient:
    def __init__(self, provider: str = "unknown", **kwargs):
        self.provider = provider

    def _format_messages(self, messages: List[Dict[str, Any]]) -> str:
        try:
            parts = []
            for m in messages:
                role = m.get("role", "")
                content = m.get("content", "")
                parts.append(f"{role}:{content}")
            return " | ".join(parts)
        except Exception:
            # 兜底：确保总是返回字符串
            return str(messages)

    # 同步接口：返回字符串
    def chat(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        return f"[未配置API/{self.provider}] 收到: {self._format_messages(messages)}"

    # 异步接口：也返回字符串；内部复用 chat，兼容 await 调用
    async def chat_completion(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        return self.chat(messages, **kwargs)

def get_llm_client(config: Optional[Dict[str, Any]] = None):
    provider = (config or {}).get("provider", "unknown")
    return DummyLLMClient(provider=provider)
