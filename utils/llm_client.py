"""
LLM客户端工具
支持DeepSeek和火山引擎ARK API
"""

import os
import json
import httpx
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """LLM配置类"""
    api_key: str
    api_base: str
    model: str
    provider: str


class LLMClient:
    """LLM客户端，支持多个提供商"""

    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "deepseek").lower()
        self.config = self._load_config()
        self.client = httpx.AsyncClient(timeout=60.0)

        logger.info(f"初始化LLM客户端，提供商: {self.provider}")

    def _load_config(self) -> LLMConfig:
        """加载配置"""
        if self.provider == "deepseek":
            return LLMConfig(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                api_base=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
                model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                provider="deepseek"
            )
        elif self.provider == "ark":
            return LLMConfig(
                api_key=os.getenv("ARK_API_KEY"),
                api_base=os.getenv("ARK_API_BASE", "https://ark.cn-beijing.volces.com/api/v3"),
                model=os.getenv("ARK_MODEL"),
                provider="ark"
            )
        else:
            raise ValueError(f"不支持的LLM提供商: {self.provider}")


    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> Optional[str]:
        """聊天方法，调用chat_completion的别名"""
        return await self.chat_completion(messages, **kwargs)

    async def chat_completion(
            self,
            messages: List[Dict[str, str]],
            temperature: float = 0.7,
            max_tokens: Optional[int] = None,
            system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        统一的聊天完成接口
        """
        try:
            # 如果有系统提示词，添加到消息开头
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages

            # 构建请求数据
            request_data = {
                "model": self.config.model,
                "messages": messages,
                "temperature": temperature,
                "stream": False
            }

            if max_tokens:
                request_data["max_tokens"] = max_tokens

            # 构建请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}"
            }

            # 发送API请求
            url = f"{self.config.api_base}/chat/completions"

            logger.debug(f"发送请求到 {url}")

            response = await self.client.post(
                url=url,
                headers=headers,
                json=request_data
            )

            response.raise_for_status()
            result = response.json()

            # 提取回复内容
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                logger.info(f"成功获取{self.provider}响应")
                return content
            else:
                logger.error(f"API响应格式异常: {result}")
                return None

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP错误: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            logger.error(f"请求错误: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"意外错误: {str(e)}")
            return None

    async def test_connection(self) -> bool:
        """测试API连接"""
        try:
            test_messages = [{"role": "user", "content": "Hello"}]
            response = await self.chat_completion(test_messages)
            return response is not None
        except Exception as e:
            logger.error(f"连接测试失败: {str(e)}")
            return False

    def get_provider_info(self) -> Dict[str, Any]:
        """获取当前提供商信息"""
        return {
            "provider": self.provider,
            "model": self.config.model,
            "api_base": self.config.api_base,
            "has_api_key": bool(self.config.api_key)
        }

    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


# 全局LLM客户端实例
llm_client = None


def get_llm_client() -> LLMClient:
    """获取全局LLM客户端实例"""
    global llm_client
    if llm_client is None:
        llm_client = LLMClient()
    return llm_client