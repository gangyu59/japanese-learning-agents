#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终快速验证脚本 - 使用完整智能体加载器
将此文件保存为: tests/final_quick_verify.py
"""

import asyncio
import time
import sys
import os
import sqlite3
from pathlib import Path
from datetime import datetime

# 配置项目路径
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
agents_path = src_path / "core" / "agents"

# 添加路径到系统路径
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(agents_path))

print(f"🏠 项目根目录: {project_root}")
print(f"📁 源码目录: {src_path}")
print(f"🤖 智能体目录: {agents_path}")


class FinalQuickVerifier:
    """最终快速验证器"""

    def __init__(self):
        self.start_time = None
        self.results = {}
        self.db_path = project_root / "japanese_learning.db"

    async def check_sqlite_database(self):
        """检查SQLite数据库"""
        print("🔍 SQLite数据库检查...")

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # 创建日语学习相关的表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    grammar_point TEXT,
                    mastery_level REAL DEFAULT 0.0,
                    last_reviewed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)

            # 测试插入和查询
            cursor.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", ("test_user",))
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", ("test_user",))
            user_count = cursor.fetchone()[0]

            conn.commit()
            conn.close()

            print(f"   ✅ SQLite数据库正常，创建了学习相关表")
            print(f"   📊 测试用户数: {user_count}")
            self.results["database"] = True
            return True

        except Exception as e:
            print(f"   ❌ SQLite数据库检查失败: {e}")
            self.results["database"] = False
            return False

    async def check_environment_config(self):
        """检查环境配置"""
        print("🔍 环境配置检查...")

        # 检查LLM提供商配置
        llm_provider = os.getenv('LLM_PROVIDER', 'deepseek')
        print(f"   🎯 LLM提供商: {llm_provider}")

        config_ok = False

        if llm_provider == 'deepseek':
            api_key = os.getenv('DEEPSEEK_API_KEY')
            api_base = os.getenv('DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1')
            model = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')

            if api_key:
                print(f"   ✅ DeepSeek API Key: {api_key[:10]}...")
                print(f"   ✅ API Base: {api_base}")
                print(f"   ✅ Model: {model}")
                config_ok = True
            else:
                print(f"   ⚠️  DEEPSEEK_API_KEY 未配置（将使用模拟响应）")
                config_ok = True  # 允许无API运行

        elif llm_provider == 'ark':
            api_key = os.getenv('ARK_API_KEY')
            api_base = os.getenv('ARK_API_BASE', 'https://ark.cn-beijing.volces.com/api/v3')
            model = os.getenv('ARK_MODEL')

            if api_key:
                print(f"   ✅ ARK API Key: {api_key[:10]}...")
                print(f"   ✅ API Base: {api_base}")
                print(f"   ✅ Model: {model}")
                config_ok = True
            else:
                print(f"   ⚠️  ARK_API_KEY 未配置（将使用模拟响应）")
                config_ok = True  # 允许无API运行
        else:
            print(f"   ❌ 未知的LLM提供商: {llm_provider}")
            print(f"   💡 支持的提供商: deepseek, ark")

        self.results["env_config"] = config_ok
        return config_ok

    async def check_complete_agent_loader(self):
        """检查完整智能体加载器"""
        print("🔍 完整智能体加载器检查...")

        try:
            # 检查完整加载器文件是否存在
            complete_loader_path = agents_path / "complete_agent_loader.py"
            if not complete_loader_path.exists():
                print(f"   ❌ 完整加载器文件不存在: {complete_loader_path}")
                print(f"   💡 请创建 src/core/agents/complete_agent_loader.py 文件")
                self.results["complete_loader"] = False
                return False

            print(f"   ✅ 完整加载器文件存在")

            # 导入完整加载器
            from core.agents.complete_agent_loader import CompleteAgentLoader, get_agent, list_agents
            print(f"   ✅ 完整加载器导入成功")

            # 创建加载器实例（这会自动加载所有智能体）
            print(f"\n   🔄 创建加载器实例并自动加载智能体...")
            loader = CompleteAgentLoader()

            # 检查加载结果
            available_agents = loader.list_available_agents()

            print(f"\n   📊 智能体加载结果:")
            print(f"      总数: {len(available_agents)}")

            if len(available_agents) > 0:
                for agent_id, class_name in available_agents.items():
                    print(f"      ✅ {agent_id}: {class_name}")
                print(f"   🎉 智能体加载成功！")
                self.results["complete_loader"] = True
                return True
            else:
                print(f"      ❌ 没有成功加载任何智能体")
                self.results["complete_loader"] = False
                return False

        except ImportError as e:
            print(f"   ❌ 完整加载器导入失败: {e}")
            print(f"   💡 请确保 complete_agent_loader.py 文件语法正确")
            self.results["complete_loader"] = False
            return False
        except Exception as e:
            print(f"   ❌ 完整加载器检查失败: {e}")
            import traceback
            print(f"   🔍 详细错误:")
            for line in traceback.format_exc().split('\n')[-10:]:
                if line.strip():
                    print(f"      {line}")
            self.results["complete_loader"] = False
            return False

    async def check_agent_instantiation(self):
        """检查智能体实例化"""
        print("🔍 智能体实例化检查...")

        try:
            from core.agents.complete_agent_loader import get_agent, list_agents

            # 获取可用智能体列表
            available_agents = list_agents()

            if not available_agents:
                print("   ❌ 没有可用的智能体")
                self.results["agent_instantiation"] = False
                return False

            # 测试实例化每个智能体
            instantiated_count = 0
            total_agents = len(available_agents)

            for agent_id in available_agents.keys():
                try:
                    print(f"   🔄 测试实例化: {agent_id}")
                    agent = get_agent(agent_id)

                    # 检查基本属性
                    agent_name = getattr(agent, 'name', 'Unknown')
                    agent_role = getattr(agent, 'role', 'Unknown')

                    print(f"      ✅ 成功: {agent_name} ({agent_role})")
                    instantiated_count += 1

                except Exception as e:
                    print(f"      ❌ 失败: {e}")

            success_rate = instantiated_count / total_agents * 100
            print(f"   📊 实例化成功率: {success_rate:.1f}% ({instantiated_count}/{total_agents})")

            if instantiated_count >= 3:  # 至少成功3个
                self.results["agent_instantiation"] = True
                return True
            else:
                self.results["agent_instantiation"] = False
                return False

        except Exception as e:
            print(f"   ❌ 智能体实例化检查失败: {e}")
            self.results["agent_instantiation"] = False
            return False

    async def check_agent_response_capability(self):
        """检查智能体响应能力"""
        print("🔍 智能体响应能力检查...")

        try:
            from core.agents.complete_agent_loader import get_agent

            # 选择一个智能体进行测试（通常田中先生最稳定）
            test_agent_ids = ["tanaka", "koumi", "ai", "yamada", "sato", "membot"]
            test_agent = None
            test_agent_id = None

            for agent_id in test_agent_ids:
                try:
                    test_agent = get_agent(agent_id)
                    test_agent_id = agent_id
                    break
                except:
                    continue

            if not test_agent:
                print("   ❌ 无法获取测试智能体")
                self.results["agent_response"] = False
                return False

            print(f"   📞 使用 {test_agent_id} 进行响应测试")

            # 构建测试上下文
            session_context = {
                "user_id": "test_user_001",
                "session_id": "test_session_001",
                "scene": "greeting",
                "history": []
            }

            # 测试几种不同的输入
            test_cases = [
                ("こんにちは", "greeting"),
                ("私は日本語を勉強しています", "learning_discussion"),
                ("ありがとうございます", "gratitude")
            ]

            successful_responses = 0

            for user_input, scene in test_cases:
                try:
                    print(f"      🔄 测试输入: '{user_input}' (场景: {scene})")

                    # 设置合理的超时时间
                    response = await asyncio.wait_for(
                        test_agent.process_user_input(user_input, session_context, scene),
                        timeout=20.0
                    )

                    if response and isinstance(response, dict):
                        content = response.get("content", "")
                        agent_name = response.get("agent_name", "Unknown")

                        if content and len(content.strip()) > 0:
                            print(f"         ✅ 响应正常: {content[:50]}...")
                            successful_responses += 1
                        else:
                            print(f"         ⚠️  响应为空")
                    else:
                        print(f"         ⚠️  响应格式异常: {type(response)}")

                except asyncio.TimeoutError:
                    print(f"         ⚠️  响应超时（可能是网络或API问题）")
                except Exception as e:
                    print(f"         ❌ 响应异常: {e}")

            success_rate = successful_responses / len(test_cases) * 100
            print(f"   📊 响应成功率: {success_rate:.1f}% ({successful_responses}/{len(test_cases)})")

            # 即使成功率不是100%也可以接受，只要有响应就说明系统基本正常
            if successful_responses >= 1:
                print(f"   ✅ 智能体响应能力正常")
                self.results["agent_response"] = True
                return True
            else:
                print(f"   ❌ 智能体无法正常响应")
                self.results["agent_response"] = False
                return False

        except Exception as e:
            print(f"   ❌ 智能体响应能力检查失败: {e}")
            self.results["agent_response"] = False
            return False

    def generate_final_report(self):
        """生成最终报告"""
        print("\n" + "=" * 70)
        print("🎌 日语学习Multi-Agent系统 - 最终验证报告")
        print("=" * 70)

        checks = [
            ("database", "SQLite数据库"),
            ("env_config", "环境配置"),
            ("complete_loader", "完整智能体加载器"),
            ("agent_instantiation", "智能体实例化"),
            ("agent_response", "智能体响应能力")
        ]

        passed = 0
        failed = 0
        critical_issues = []

        print("\n📋 检查项目详情:")
        for check_key, check_name in checks:
            result = self.results.get(check_key, False)

            if result is True:
                status = "✅ 正常"
                passed += 1
            else:
                status = "❌ 异常"
                failed += 1

                # 标记关键问题
                if check_key in ["complete_loader", "agent_instantiation"]:
                    critical_issues.append(check_name)

            print(f"   {check_name:<25} {status}")

        total_time = time.time() - self.start_time if self.start_time else 0

        print(f"\n📊 验证统计:")
        print(f"   ✅ 通过: {passed}")
        print(f"   ❌ 失败: {failed}")
        print(f"   📊 成功率: {(passed / (passed + failed) * 100):.1f}%")
        print(f"   ⏱️  总耗时: {total_time:.1f} 秒")

        # 系统就绪状态评估
        print(f"\n🏁 系统就绪状态:")

        if len(critical_issues) == 0 and passed >= 4:
            status = "🎉 系统完全就绪！"
            ready = True
        elif len(critical_issues) == 0:
            status = "✅ 系统基本就绪，部分功能可能需要优化"
            ready = True
        elif len(critical_issues) == 1:
            status = "⚠️  系统存在关键问题，需要修复后使用"
            ready = False
        else:
            status = "🛑 系统存在多个关键问题，需要全面检查"
            ready = False

        print(f"   {status}")

        if critical_issues:
            print(f"\n🔧 关键问题:")
            for issue in critical_issues:
                print(f"   - {issue}")

        # 使用指南
        print(f"\n📖 使用指南:")
        if ready:
            print("   🎌 恭喜！你的日语学习Multi-Agent系统已准备就绪")
            print("   📝 快速开始:")
            print("      from core.agents.complete_agent_loader import get_agent")
            print("      agent = get_agent('tanaka')  # 获取田中先生")
            print("      response = await agent.process_user_input('こんにちは', context)")
            print("   🧪 运行完整测试: python tests/run_all_tests.py")
        else:
            print("   🔧 请根据上面的错误信息修复问题")
            print("   📞 如需帮助，请提供详细的错误信息")

        return ready

    async def run_verification(self):
        """运行最终验证"""
        self.start_time = time.time()

        print("🚀 日语学习Multi-Agent系统 - 最终验证")
        print("=" * 70)
        print("🎯 目标：全面验证系统是否可用")
        print(f"📅 开始时间: {datetime.now().strftime('%H:%M:%S')}")
        print()

        # 按顺序运行检查
        await self.check_sqlite_database()
        print()
        await self.check_environment_config()
        print()
        await self.check_complete_agent_loader()
        print()
        await self.check_agent_instantiation()
        print()
        await self.check_agent_response_capability()

        # 生成最终报告
        return self.generate_final_report()


async def main():
    """主函数"""
    print("🎌 开始日语学习Multi-Agent系统最终验证...")

    verifier = FinalQuickVerifier()

    try:
        success = await verifier.run_verification()

        if success:
            print(f"\n🎊 最终验证成功！系统已就绪！")
            return 0
        else:
            print(f"\n🔧 最终验证发现问题，请修复后重试。")
            return 1

    except KeyboardInterrupt:
        print(f"\n⏹️  验证被用户中断")
        return 2
    except Exception as e:
        print(f"\n💥 验证执行异常: {e}")
        import traceback
        traceback.print_exc()
        return 3


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)