"""田中先生测试脚本"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from src.core.agents.core_agents.tanaka import TanakaAgent
from src.data.models.agent import Agent
from src.data.models.base import AgentPersonality
from src.utils.logger import setup_logger


async def interactive_test():
    """交互式测试田中先生"""
    logger = setup_logger("test_tanaka")

    # 创建田中先生
    personality = AgentPersonality(
        strictness=8,
        humor=3,
        patience=6,
        creativity=4,
        formality=9
    )

    config = Agent(
        name="田中先生",
        description="严格的日语语法老师",
        personality=personality,
        expertise_areas=["grammar", "formal_japanese"],
        system_prompt="严格的日语老师"
    )

    tanaka = TanakaAgent(config)

    print("🎌 田中先生日语测试系统")
    print("=" * 50)
    print("田中先生已准备就绪！请输入日语句子进行测试。")
    print("输入 'quit' 退出程序")
    print("=" * 50)

    while True:
        try:
            # 获取用户输入
            user_input = input("\n👤 您: ").strip()

            if user_input.lower() == 'quit':
                print("👋 さようなら！")
                break

            if not user_input:
                continue

            # 处理消息
            print("🤔 田中先生正在思考...")
            response = await tanaka.process_message(user_input)

            # 显示响应
            print(f"\n🎌 田中先生: {response.content}")
            print(f"   信心度: {response.confidence:.2f}")

            if response.metadata:
                print("   元数据:", response.metadata)

        except KeyboardInterrupt:
            print("\n\n👋 プログラムを終了します。")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"❌ 错误: {e}")


if __name__ == "__main__":
    asyncio.run(interactive_test())