# env_loading_diagnostic.py
"""
诊断和修复环境变量加载问题
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv


def diagnose_env_loading():
    """诊断环境变量加载问题"""
    print("🔍 诊断环境变量加载问题...")
    print("=" * 50)

    # 1. 检查.env文件位置
    current_dir = Path.cwd()
    env_file = current_dir / ".env"

    print(f"📁 当前工作目录: {current_dir}")
    print(f"📄 .env文件路径: {env_file}")
    print(f"✅ .env文件存在: {env_file.exists()}")

    if not env_file.exists():
        print("❌ .env文件不存在于当前目录")
        # 尝试在父目录查找
        parent_env = current_dir.parent / ".env"
        if parent_env.exists():
            print(f"🔍 在父目录找到.env: {parent_env}")
            env_file = parent_env
        else:
            print("❌ 在父目录也未找到.env文件")
            return False

    # 2. 加载环境变量
    try:
        load_dotenv(env_file, override=True)
        print("✅ .env文件加载成功")
    except Exception as e:
        print(f"❌ .env文件加载失败: {e}")
        return False

    # 3. 检查关键环境变量
    required_vars = {
        "LLM_PROVIDER": os.getenv("LLM_PROVIDER"),
        "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY"),
        "DEEPSEEK_API_BASE": os.getenv("DEEPSEEK_API_BASE"),
        "DEEPSEEK_MODEL": os.getenv("DEEPSEEK_MODEL"),
        "ARK_API_KEY": os.getenv("ARK_API_KEY"),
        "DATABASE_URL": os.getenv("DATABASE_URL")
    }

    print("\n🔑 环境变量检查:")
    all_good = True
    for var_name, var_value in required_vars.items():
        if var_value:
            # 隐藏API密钥的大部分内容
            if "API_KEY" in var_name:
                display_value = f"{var_value[:8]}...{var_value[-4:]}"
            else:
                display_value = var_value
            print(f"   ✅ {var_name}: {display_value}")
        else:
            print(f"   ❌ {var_name}: 未设置")
            all_good = False

    return all_good


def fix_agent_config_loading():
    """修复智能体配置加载"""
    print("\n🔧 生成智能体配置加载修复代码...")

    config_loader_code = '''
# config_loader.py
"""
确保智能体正确加载环境变量配置
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

class ConfigLoader:
    """配置加载器 - 确保环境变量正确加载"""

    def __init__(self):
        self.config = {}
        self._load_env_file()
        self._validate_config()

    def _load_env_file(self):
        """加载.env文件"""
        # 尝试多个可能的.env文件位置
        possible_paths = [
            Path.cwd() / ".env",
            Path.cwd().parent / ".env", 
            Path(__file__).parent / ".env",
            Path(__file__).parent.parent / ".env"
        ]

        for env_path in possible_paths:
            if env_path.exists():
                load_dotenv(env_path, override=True)
                print(f"✅ 已加载环境变量: {env_path}")
                break
        else:
            print("⚠️  未找到.env文件，使用系统环境变量")

    def _validate_config(self):
        """验证配置完整性"""
        self.config = {
            "llm_provider": os.getenv("LLM_PROVIDER", "deepseek"),
            "deepseek_api_key": os.getenv("DEEPSEEK_API_KEY"),
            "deepseek_api_base": os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
            "deepseek_model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            "ark_api_key": os.getenv("ARK_API_KEY"),
            "ark_api_base": os.getenv("ARK_API_BASE", "https://ark.cn-beijing.volces.com/api/v3"),
            "ark_model": os.getenv("ARK_MODEL", "ep-20250313161944-69jw8"),
            "database_url": os.getenv("DATABASE_URL", "sqlite:///./japanese_learning.db"),
            "debug": os.getenv("DEBUG", "false").lower() == "true"
        }

        # 检查必要的配置
        provider = self.config["llm_provider"]
        if provider == "deepseek" and not self.config["deepseek_api_key"]:
            raise ValueError("DeepSeek API密钥未配置")
        elif provider == "ark" and not self.config["ark_api_key"]:
            raise ValueError("ARK API密钥未配置")

    def get_llm_config(self) -> Dict[str, Any]:
        """获取LLM配置"""
        provider = self.config["llm_provider"]

        if provider == "deepseek":
            return {
                "provider": "deepseek",
                "api_key": self.config["deepseek_api_key"],
                "api_base": self.config["deepseek_api_base"], 
                "model": self.config["deepseek_model"],
                "timeout": 30
            }
        elif provider == "ark":
            return {
                "provider": "ark",
                "api_key": self.config["ark_api_key"],
                "api_base": self.config["ark_api_base"],
                "model": self.config["ark_model"], 
                "timeout": 30
            }
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}")

    def get_database_config(self) -> str:
        """获取数据库配置"""
        return self.config["database_url"]

    def is_debug_mode(self) -> bool:
        """是否调试模式"""
        return self.config["debug"]

# 全局配置实例
try:
    config_loader = ConfigLoader()
    print("✅ 配置加载器初始化成功")
except Exception as e:
    print(f"❌ 配置加载器初始化失败: {e}")
    config_loader = None
'''

    # 保存配置加载器
    with open("config_loader.py", "w", encoding="utf-8") as f:
        f.write(config_loader_code)

    print("✅ 已生成 config_loader.py")

    # 生成智能体基类修复
    base_agent_fix = '''
# base_agent_fix.py
"""
修复智能体基类的配置加载问题
"""

from config_loader import config_loader

class BaseAgentFixed:
    """修复后的智能体基类"""

    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name

        # 确保配置加载
        if config_loader is None:
            raise RuntimeError("配置加载器未正确初始化")

        self.llm_config = config_loader.get_llm_config()
        self.debug_mode = config_loader.is_debug_mode()

        # 显示加载的配置信息用于调试
        if self.debug_mode:
            provider = self.llm_config["provider"]
            model = self.llm_config["model"]
            print(f"🤖 {self.name} 初始化: {provider}/{model}")

    async def process_user_input(self, user_input: str, session_context: dict, scene: str = "general"):
        """处理用户输入"""
        try:
            # 根据配置调用相应的LLM
            if self.llm_config["provider"] == "deepseek":
                response = await self._call_deepseek_api(user_input)
            elif self.llm_config["provider"] == "ark": 
                response = await self._call_ark_api(user_input)
            else:
                raise ValueError(f"未知的LLM提供商: {self.llm_config['provider']}")

            return {
                "success": True,
                "content": response,
                "agent_name": self.name,
                "emotion": self._get_emotion(),
                "learning_points": self._extract_learning_points(response),
                "suggestions": self._generate_suggestions(response)
            }

        except Exception as e:
            error_msg = f"[{self.llm_config['provider']}] 处理失败: {str(e)}"
            return {
                "success": False,
                "error": error_msg,
                "content": f"抱歉，{self.name}暂时无法回答。请稍后再试。",
                "agent_name": self.name,
                "emotion": "😓"
            }

    async def _call_deepseek_api(self, user_input: str) -> str:
        """调用DeepSeek API"""
        import aiohttp
        import json

        headers = {
            "Authorization": f"Bearer {self.llm_config['api_key']}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.llm_config["model"],
            "messages": [
                {"role": "system", "content": f"你是{self.name}，请用这个角色回答。"},
                {"role": "user", "content": user_input}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.post(
                f"{self.llm_config['api_base']}/chat/completions",
                headers=headers,
                json=payload
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error_text = await resp.text()
                    raise Exception(f"API错误 {resp.status}: {error_text}")

    async def _call_ark_api(self, user_input: str) -> str:
        """调用ARK API"""
        import aiohttp
        import json

        headers = {
            "Authorization": f"Bearer {self.llm_config['api_key']}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.llm_config["model"],
            "messages": [
                {"role": "system", "content": f"你是{self.name}，请用这个角色回答。"},
                {"role": "user", "content": user_input}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.post(
                f"{self.llm_config['api_base']}/chat/completions",
                headers=headers,
                json=payload
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error_text = await resp.text()
                    raise Exception(f"API错误 {resp.status}: {error_text}")

    def _get_emotion(self) -> str:
        """获取智能体情绪"""
        return "😊"  # 默认情绪

    def _extract_learning_points(self, response: str) -> list:
        """提取学习点"""
        return ["学习点1", "学习点2"]

    def _generate_suggestions(self, response: str) -> list:
        """生成建议"""
        return ["建议1", "建议2"]
'''

    # 保存智能体修复
    with open("base_agent_fix.py", "w", encoding="utf-8") as f:
        f.write(base_agent_fix)

    print("✅ 已生成 base_agent_fix.py")
    return True


def create_test_env_validation():
    """创建测试环境验证脚本"""
    validation_script = '''
# test_env_validation.py
"""
验证测试环境中的配置加载
"""

import asyncio
from config_loader import config_loader
from base_agent_fix import BaseAgentFixed

async def test_configuration():
    """测试配置是否正确加载"""
    print("🧪 测试环境配置验证")
    print("=" * 40)

    try:
        # 测试配置加载
        llm_config = config_loader.get_llm_config()
        print(f"✅ LLM配置加载成功")
        print(f"   提供商: {llm_config['provider']}")
        print(f"   模型: {llm_config['model']}")
        print(f"   API基础URL: {llm_config['api_base']}")

        # 测试智能体初始化
        test_agent = BaseAgentFixed("test", "测试智能体")
        print(f"✅ 智能体初始化成功: {test_agent.name}")

        # 测试API调用
        test_input = "你好，请介绍一下自己"
        result = await test_agent.process_user_input(
            user_input=test_input,
            session_context={},
            scene="test"
        )

        if result["success"]:
            print(f"✅ API调用成功")
            print(f"   响应长度: {len(result['content'])} 字符")
            print(f"   响应预览: {result['content'][:100]}...")
        else:
            print(f"❌ API调用失败: {result.get('error', 'Unknown error')}")
            return False

        print("🎉 所有配置测试通过!")
        return True

    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_configuration())
    exit(0 if result else 1)
'''

    with open("test_env_validation.py", "w", encoding="utf-8") as f:
        f.write(validation_script)

    print("✅ 已生成 test_env_validation.py")


def main():
    """主诊断流程"""
    print("🎌 环境变量加载问题诊断和修复")
    print("=" * 60)

    # Step 1: 诊断环境变量加载
    env_ok = diagnose_env_loading()

    if not env_ok:
        print("\n❌ 环境变量加载有问题，请检查.env文件")
        return False

    # Step 2: 生成修复代码
    fix_ok = fix_agent_config_loading()

    # Step 3: 创建验证脚本
    create_test_env_validation()

    print("\n🚀 修复步骤:")
    print("1. 运行配置验证: python test_env_validation.py")
    print("2. 如果验证通过，替换你现有的基类文件")
    print("3. 重新运行测试: python tests/run_all_tests.py")

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)