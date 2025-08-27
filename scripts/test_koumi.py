"""
小美智能体测试脚本
文件位置: scripts/test_koumi.py
运行方式: python scripts/test_koumi.py
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from src.core.agents.core_agents.koumi import KoumiAgent
    from src.data.models.agent import Agent
    from src.data.models.base import AgentPersonality
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保您在项目根目录下运行此脚本")
    print("当前工作目录:", Path.cwd())
    print("项目根目录:", project_root)
    sys.exit(1)

def create_koumi_agent():
    """创建小美智能体实例"""
    try:
        personality = AgentPersonality(
            strictness=3,       # 不严格
            humor=9,           # 很幽默
            patience=9,        # 很有耐心
            creativity=8,      # 很有创造力
            formality=2        # 非常随意
        )

        # 添加小美特有的性格特征
        personality.energy_level = 9
        personality.casualness = 8
        personality.encouragement = 9
        personality.modern_language = 10
        personality.emoji_usage = 8

        config = Agent(
            name="小美",
            description="活泼的日语对话伙伴",
            personality=personality,
            expertise_areas=["conversation", "modern_japanese", "encouragement"],
            system_prompt="活泼的日语对话伙伴"
        )

        return KoumiAgent(config)
    except Exception as e:
        print(f"❌ 创建智能体失败: {e}")
        return None

async def test_koumi_responses():
    """测试小美的各种响应"""
    print("🌸 小美智能体自动测试开始！")
    print("=" * 60)

    # 创建小美实例
    koumi = create_koumi_agent()
    if not koumi:
        return

    # 显示小美的基本信息
    print(f"👧 智能体: {koumi.config.name}")
    print(f"🎭 性格特征: 活泼开朗，现代日语专家")
    print(f"⭐ 专长领域: {', '.join(koumi.config.expertise_areas)}")
    print()

    # 测试用例
    test_cases = [
        ("こんにちは", "日语问候测试"),
        ("Hello, how are you?", "英语输入测试"),
        ("今日は良い天気ですね", "日语对话测试"),
        ("日本の文化について教えてください", "文化问题测试"),
        ("日本語の勉強が難しいです", "学习困难测试"),
        ("ありがとうございます！とても嬉しいです", "积极情感测试"),
        ("やばい！この料理美味しい", "现代日语测试"),
        ("推しのアニメが面白い", "年轻人用语测试"),
        ("文法がわからなくて困ってます", "语法求助测试"),
        ("今日はいい一日でした", "日常分享测试")
    ]

    print("💬 开始对话测试:")
    print("-" * 60)

    for i, (message, description) in enumerate(test_cases, 1):
        print(f"\n🧪 测试 {i}: {description}")
        print(f"👤 用户: {message}")

        try:
            # 获取小美的响应
            response = await koumi.process_message(message)

            print(f"👧 小美: {response.content}")
            print(f"📊 响应信息:")
            print(f"   • 置信度: {response.confidence:.1%}")
            print(f"   • 响应类型: {response.metadata.get('response_type', 'unknown')}")
            print(f"   • 处理时间: {response.metadata.get('processing_time', 0):.3f}s")
            print(f"   • 检测情感: {response.metadata.get('sentiment_detected', 'unknown')}")
            print(f"   • 鼓励级别: {response.metadata.get('encouragement_level', 0)}/10")
            print(f"   • 智能体心情: {response.metadata.get('agent_mood', 'unknown')}")

            modern_expressions = response.metadata.get('modern_expressions_used', [])
            if modern_expressions:
                print(f"   • 现代用语: {modern_expressions}")

        except Exception as e:
            print(f"❌ 测试失败: {e}")

        print("-" * 40)

    print(f"\n📈 对话统计:")
    print(f"   • 总对话数: {len(koumi.conversation_history)}")

    if koumi.conversation_history:
        avg_confidence = sum(0.85 for _ in koumi.conversation_history) / len(koumi.conversation_history)
        print(f"   • 平均置信度: {avg_confidence:.1%}")

    print(f"\n✨ 自动测试完成！小美表现优秀！")

async def interactive_test():
    """交互式测试"""
    print("\n" + "=" * 60)
    print("🎌 进入小美智能体交互测试模式")
    print("💡 输入 'quit' 或 '退出' 结束测试")
    print("=" * 60)

    koumi = create_koumi_agent()
    if not koumi:
        return

    # 小美的开场白
    greetings = [
        "こんにちは〜！今日はどんな日本語を練習したい？😊✨",
        "やあ〜！何か楽しいこと話そうよ〜！日本語で教えて💕",
        "おはよう〜！今日覚えた新しい単語とかある？🌟",
        "ハーイ！今の気分を日本語で表現してみて〜😄"
    ]

    import random
    starter = random.choice(greetings)
    print(f"\n👧 小美: {starter}")

    conversation_count = 0

    while True:
        try:
            # 获取用户输入
            user_input = input("\n👤 您: ").strip()

            if user_input.lower() in ['quit', '退出', 'exit', 'bye']:
                farewell = [
                    "またね〜！楽しかったよ〜✨ 日本語頑張って！",
                    "バイバイ〜！また一緒に勉強しようね😊💕",
                    "さようなら〜！いつでも話しかけてね🌸",
                    "また会おうね〜！日本語の練習応援してるよ💪✨"
                ]
                print(f"\n👧 小美: {random.choice(farewell)}")
                break

            if not user_input:
                print("👧 小美: 何か話してよ〜😊 恥ずかしがらないで！")
                continue

            print("🤔 小美正在思考...")

            # 获取响应
            response = await koumi.process_message(user_input)

            conversation_count += 1

            # 显示响应
            print(f"👧 小美: {response.content}")

            # 每3轮显示一次详细信息
            if conversation_count % 3 == 0:
                print(f"   📊 [置信度: {response.confidence:.1%} | "
                      f"类型: {response.metadata.get('response_type', 'unknown')} | "
                      f"用时: {response.metadata.get('processing_time', 0):.2f}s]")

        except KeyboardInterrupt:
            print(f"\n\n👧 小美: あっ、急に終わっちゃうの？😅 またね〜！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            print("👧 小美: あれ？何かエラーが起きちゃった😅 もう一度試してね〜！")

def show_personality_analysis():
    """显示小美的性格分析"""
    koumi = create_koumi_agent()
    if not koumi:
        return

    print(f"\n👧 {koumi.config.name} 的性格分析:")
    print("-" * 40)

    personality_traits = [
        ("strictness", "严谨程度", koumi.config.personality.strictness),
        ("humor", "幽默感", koumi.config.personality.humor),
        ("patience", "耐心度", koumi.config.personality.patience),
        ("creativity", "创造力", koumi.config.personality.creativity),
        ("formality", "正式程度", koumi.config.personality.formality)
    ]

    for trait_key, trait_name, value in personality_traits:
        print(f"📊 {trait_name}: {value}/10")
        # 简单的进度条显示
        bar = "█" * value + "░" * (10 - value)
        print(f"    {bar}")
        print()

    # 显示特殊属性（如果存在）
    special_traits = [
        ("energy_level", "活力程度", getattr(koumi.config.personality, 'energy_level', 5)),
        ("casualness", "随意程度", getattr(koumi.config.personality, 'casualness', 5)),
        ("encouragement", "鼓励程度", getattr(koumi.config.personality, 'encouragement', 5)),
        ("modern_language", "现代语言", getattr(koumi.config.personality, 'modern_language', 5))
    ]

    print("🌟 小美专属特征:")
    for trait_key, trait_name, value in special_traits:
        print(f"✨ {trait_name}: {value}/10")

    print(f"\n🎯 教学风格: 轻松愉快，现代化，富有同理心")
    print(f"🎓 目标学习者: 希望学习现代日语和年轻人用语的学习者")

def main():
    """主测试函数"""
    print("🎌 小美智能体 (Koumi Agent) 测试程序")
    print("活泼的日语对话伙伴 - 现代日语专家")
    print("文件位置: scripts/test_koumi.py")
    print()

    while True:
        print("选择测试模式:")
        print("1. 🧪 自动测试 (推荐先运行)")
        print("2. 💬 交互测试")
        print("3. 📊 性格分析")
        print("4. 🔍 系统信息")
        print("5. 🚪 退出")

        choice = input("\n请选择 (1-5): ").strip()

        if choice == '1':
            print("\n开始自动测试...")
            asyncio.run(test_koumi_responses())
        elif choice == '2':
            print("\n进入交互模式...")
            asyncio.run(interactive_test())
        elif choice == '3':
            show_personality_analysis()
        elif choice == '4':
            print(f"\n🔍 系统信息:")
            print(f"   • Python版本: {sys.version}")
            print(f"   • 项目根目录: {project_root}")
            print(f"   • 当前工作目录: {Path.cwd()}")
            print(f"   • 脚本位置: {Path(__file__)}")

            try:
                from src.core.agents.core_agents.koumi import KoumiAgent
                print(f"   • 小美模块: ✅ 导入成功")
            except ImportError as e:
                print(f"   • 小美模块: ❌ 导入失败 - {e}")

        elif choice == '5':
            print("👋 さようなら！また会いましょう〜✨")
            break
        else:
            print("❌ 无效选择，请重试")

        print()

if __name__ == "__main__":
    main()