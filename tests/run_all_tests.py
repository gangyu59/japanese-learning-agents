#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日语学习Multi-Agent系统 - 主测试执行器
按顺序执行所有测试阶段，生成完整测试报告
"""

import asyncio
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import argparse

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class TestSuiteRunner:
    """测试套件执行器"""

    def __init__(self, config_file: str = "test_config.json"):
        self.config = self.load_config(config_file)
        self.test_results = {}
        self.start_time = None
        self.total_time = None
        self.failed_tests = []

    def load_config(self, config_file: str) -> Dict:
        """加载测试配置"""
        default_config = {
            "database": {
                "url": "postgresql://user:password@localhost:5432/japanese_learning",
                "test_timeout": 30
            },
            "api": {
                "base_url": "http://localhost:8000",
                "timeout": 15
            },
            "test_phases": {
                "phase_1_database": True,
                "phase_2_single_agent": True,
                "phase_3_collaboration": True,
                "phase_4_persistence": True,
                "phase_5_integration": True
            },
            "performance": {
                "concurrent_requests": 5,
                "max_response_time": 10
            },
            "cleanup": {
                "auto_cleanup": True,
                "keep_test_data": False
            },
            "reporting": {
                "generate_html_report": True,
                "save_detailed_logs": True,
                "report_directory": "./test_reports"
            }
        }

        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 合并配置
                    self._merge_config(default_config, user_config)
                    print(f"✅ 已加载测试配置: {config_file}")
            else:
                print(f"⚠️  配置文件不存在，使用默认配置: {config_file}")
        except Exception as e:
            print(f"❌ 配置文件加载失败，使用默认配置: {e}")

        return default_config

    def _merge_config(self, base_config: Dict, user_config: Dict) -> None:
        """递归合并配置"""
        for key, value in user_config.items():
            if key in base_config:
                if isinstance(value, dict) and isinstance(base_config[key], dict):
                    self._merge_config(base_config[key], value)
                else:
                    base_config[key] = value
            else:
                base_config[key] = value

    def save_config_template(self, config_file: str = "test_config_template.json"):
        """保存配置模板文件"""
        template = {
            "_comment": "日语学习Multi-Agent系统测试配置文件",
            "database": {
                "url": "postgresql://user:password@localhost:5432/japanese_learning",
                "test_timeout": 30,
                "_comment": "数据库连接URL和超时时间（秒）"
            },
            "api": {
                "base_url": "http://localhost:8000",
                "timeout": 15,
                "_comment": "API服务地址和超时时间（秒）"
            },
            "test_phases": {
                "phase_1_database": True,
                "phase_2_single_agent": True,
                "phase_3_collaboration": True,
                "phase_4_persistence": True,
                "phase_5_integration": True,
                "_comment": "控制哪些测试阶段被执行"
            },
            "performance": {
                "concurrent_requests": 5,
                "max_response_time": 10,
                "_comment": "性能测试参数"
            },
            "cleanup": {
                "auto_cleanup": True,
                "keep_test_data": False,
                "_comment": "测试数据清理设置"
            },
            "reporting": {
                "generate_html_report": True,
                "save_detailed_logs": True,
                "report_directory": "./test_reports",
                "_comment": "测试报告生成设置"
            }
        }

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        print(f"✅ 已生成配置模板: {config_file}")

    async def run_phase_1_database_tests(self):
        """执行Phase 1: 数据库基础设施测试"""
        if not self.config["test_phases"]["phase_1_database"]:
            print("⏭️  跳过Phase 1: 数据库测试")
            self.test_results["phase_1"] = {"status": "skipped"}
            return True

        print("\n" + "=" * 60)
        print("🔄 Phase 1: 数据库基础设施测试")
        print("=" * 60)

        try:
            from database_connection_test import DatabaseTester

            tester = DatabaseTester(self.config["database"]["url"])
            success = await tester.run_all_tests()

            self.test_results["phase_1"] = {
                "status": "passed" if success else "failed",
                "details": "数据库基础设施测试",
                "timestamp": datetime.now().isoformat()
            }

            if not success:
                self.failed_tests.append("Phase 1: 数据库基础设施")
                print("❌ Phase 1失败 - 数据库问题可能影响后续测试")
                return False

            print("✅ Phase 1完成 - 数据库基础设施正常")
            return True

        except ImportError as e:
            print(f"❌ Phase 1测试模块导入失败: {e}")
            self.test_results["phase_1"] = {"status": "error", "error": str(e)}
            self.failed_tests.append("Phase 1: 模块导入错误")
            return False
        except Exception as e:
            print(f"❌ Phase 1执行异常: {e}")
            self.test_results["phase_1"] = {"status": "error", "error": str(e)}
            self.failed_tests.append("Phase 1: 执行异常")
            return False

    async def run_phase_2_single_agent_tests(self):
        """执行Phase 2: 单智能体回归测试"""
        if not self.config["test_phases"]["phase_2_single_agent"]:
            print("⏭️  跳过Phase 2: 单智能体测试")
            self.test_results["phase_2"] = {"status": "skipped"}
            return True

        print("\n" + "=" * 60)
        print("🔄 Phase 2: 单智能体功能回归测试")
        print("=" * 60)

        try:
            from single_agent_regression_test import SingleAgentTester

            tester = SingleAgentTester()
            success = await tester.run_all_tests()

            self.test_results["phase_2"] = {
                "status": "passed" if success else "failed",
                "details": "单智能体功能回归测试",
                "test_results": tester.test_results,
                "timestamp": datetime.now().isoformat()
            }

            if not success:
                self.failed_tests.append("Phase 2: 单智能体功能")
                print("❌ Phase 2失败 - 基础智能体功能存在问题")
                return False

            print("✅ Phase 2完成 - 单智能体功能正常")
            return True

        except ImportError as e:
            print(f"❌ Phase 2测试模块导入失败: {e}")
            self.test_results["phase_2"] = {"status": "error", "error": str(e)}
            self.failed_tests.append("Phase 2: 模块导入错误")
            return False
        except Exception as e:
            print(f"❌ Phase 2执行异常: {e}")
            self.test_results["phase_2"] = {"status": "error", "error": str(e)}
            self.failed_tests.append("Phase 2: 执行异常")
            return False

    async def run_phase_3_collaboration_tests(self):
        """执行Phase 3: 多智能体协作测试"""
        if not self.config["test_phases"]["phase_3_collaboration"]:
            print("⏭️  跳过Phase 3: 多智能体协作测试")
            self.test_results["phase_3"] = {"status": "skipped"}
            return True

        print("\n" + "=" * 60)
        print("🔄 Phase 3: 多智能体协作功能测试")
        print("=" * 60)

        try:
            from multi_agent_collaboration_test import CollaborationTester

            tester = CollaborationTester()
            success = await tester.run_all_tests()

            self.test_results["phase_3"] = {
                "status": "passed" if success else "failed",
                "details": "多智能体协作功能测试",
                "test_results": tester.test_results,
                "timestamp": datetime.now().isoformat()
            }

            if not success:
                self.failed_tests.append("Phase 3: 多智能体协作")
                print("⚠️  Phase 3部分失败 - 协作功能需要改进，但不阻止后续测试")
                # 协作功能失败不阻止后续测试，因为可能是高级功能
                return True

            print("✅ Phase 3完成 - 多智能体协作功能正常")
            return True

        except ImportError as e:
            print(f"❌ Phase 3测试模块导入失败: {e}")
            self.test_results["phase_3"] = {"status": "error", "error": str(e)}
            self.failed_tests.append("Phase 3: 模块导入错误")
            return True  # 不阻止后续测试
        except Exception as e:
            print(f"❌ Phase 3执行异常: {e}")
            self.test_results["phase_3"] = {"status": "error", "error": str(e)}
            self.failed_tests.append("Phase 3: 执行异常")
            return True  # 不阻止后续测试

    async def run_phase_4_persistence_tests(self):
        """执行Phase 4: 数据持久化测试"""
        if not self.config["test_phases"]["phase_4_persistence"]:
            print("⏭️  跳过Phase 4: 数据持久化测试")
            self.test_results["phase_4"] = {"status": "skipped"}
            return True

        print("\n" + "=" * 60)
        print("🔄 Phase 4: 数据持久化功能测试")
        print("=" * 60)

        try:
            from data_persistence_test import PersistenceTester

            tester = PersistenceTester()
            success = await tester.run_all_tests()

            self.test_results["phase_4"] = {
                "status": "passed" if success else "failed",
                "details": "数据持久化功能测试",
                "test_results": tester.test_results,
                "timestamp": datetime.now().isoformat()
            }

            if not success:
                self.failed_tests.append("Phase 4: 数据持久化")
                print("⚠️  Phase 4部分失败 - 持久化功能需要改进")
                return True  # 不阻止最终集成测试

            print("✅ Phase 4完成 - 数据持久化功能正常")
            return True

        except ImportError as e:
            print(f"❌ Phase 4测试模块导入失败: {e}")
            self.test_results["phase_4"] = {"status": "error", "error": str(e)}
            self.failed_tests.append("Phase 4: 模块导入错误")
            return True  # 不阻止后续测试
        except Exception as e:
            print(f"❌ Phase 4执行异常: {e}")
            self.test_results["phase_4"] = {"status": "error", "error": str(e)}
            self.failed_tests.append("Phase 4: 执行异常")
            return True  # 不阻止后续测试

    async def run_phase_5_integration_tests(self):
        """执行Phase 5: 端到端集成测试"""
        if not self.config["test_phases"]["phase_5_integration"]:
            print("⏭️  跳过Phase 5: 端到端集成测试")
            self.test_results["phase_5"] = {"status": "skipped"}
            return True

        print("\n" + "=" * 60)
        print("🔄 Phase 5: 端到端集成测试")
        print("=" * 60)

        try:
            from end_to_end_integration_test import EndToEndTester

            tester = EndToEndTester()
            # 传递配置参数
            tester.api_base_url = self.config["api"]["base_url"]

            success = await tester.run_all_tests()

            self.test_results["phase_5"] = {
                "status": "passed" if success else "failed",
                "details": "端到端集成测试",
                "test_results": tester.test_results,
                "timestamp": datetime.now().isoformat()
            }

            if not success:
                self.failed_tests.append("Phase 5: 端到端集成")
                print("❌ Phase 5失败 - 系统集成存在问题")
                return False

            print("✅ Phase 5完成 - 端到端集成测试通过")
            return True

        except ImportError as e:
            print(f"❌ Phase 5测试模块导入失败: {e}")
            self.test_results["phase_5"] = {"status": "error", "error": str(e)}
            self.failed_tests.append("Phase 5: 模块导入错误")
            return False
        except Exception as e:
            print(f"❌ Phase 5执行异常: {e}")
            self.test_results["phase_5"] = {"status": "error", "error": str(e)}
            self.failed_tests.append("Phase 5: 执行异常")
            return False

    def generate_final_report(self):
        """生成最终测试报告"""
        print("\n" + "=" * 80)
        print("📊 日语学习Multi-Agent系统 - 最终测试报告")
        print("=" * 80)

        # 统计各阶段结果
        phase_names = {
            "phase_1": "Phase 1: 数据库基础设施",
            "phase_2": "Phase 2: 单智能体功能",
            "phase_3": "Phase 3: 多智能体协作",
            "phase_4": "Phase 4: 数据持久化",
            "phase_5": "Phase 5: 端到端集成"
        }

        passed_phases = 0
        failed_phases = 0
        skipped_phases = 0
        error_phases = 0

        print("\n📋 测试阶段总结:")
        for phase_key, phase_name in phase_names.items():
            result = self.test_results.get(phase_key, {"status": "not_run"})
            status = result["status"]

            if status == "passed":
                status_icon = "✅ 通过"
                passed_phases += 1
            elif status == "failed":
                status_icon = "❌ 失败"
                failed_phases += 1
            elif status == "skipped":
                status_icon = "⏭️  跳过"
                skipped_phases += 1
            elif status == "error":
                status_icon = "💥 错误"
                error_phases += 1
            else:
                status_icon = "❓ 未运行"

            print(f"{phase_name:<35} {status_icon}")

        # 整体统计
        total_phases = passed_phases + failed_phases + error_phases
        if total_phases > 0:
            success_rate = (passed_phases / total_phases) * 100
        else:
            success_rate = 0

        print(f"\n📊 测试统计:")
        print(f"   通过: {passed_phases}")
        print(f"   失败: {failed_phases}")
        print(f"   错误: {error_phases}")
        print(f"   跳过: {skipped_phases}")
        print(f"   成功率: {success_rate:.1f}%")

        if self.total_time:
            print(f"   总耗时: {self.total_time:.2f} 秒")

        # 失败项目详情
        if self.failed_tests:
            print(f"\n⚠️  失败的测试项目:")
            for failed_test in self.failed_tests:
                print(f"   - {failed_test}")

        # 系统就绪状态评估
        print(f"\n🏁 系统就绪状态评估:")

        # 关键阶段检查
        critical_phases = ["phase_1", "phase_2", "phase_5"]
        critical_failures = []

        for phase in critical_phases:
            if phase in self.test_results:
                if self.test_results[phase]["status"] in ["failed", "error"]:
                    critical_failures.append(phase_names[phase])

        if len(critical_failures) == 0 and passed_phases >= 3:
            system_status = "🎉 系统完全就绪！所有核心功能正常工作。"
            ready_level = "完全就绪"
        elif len(critical_failures) == 0:
            system_status = "✅ 系统基本就绪，核心功能正常，可投入使用。"
            ready_level = "基本就绪"
        elif len(critical_failures) == 1:
            system_status = "⚠️  系统部分就绪，存在关键问题需要修复。"
            ready_level = "部分就绪"
        else:
            system_status = "❌ 系统未就绪，存在多个关键问题，需要重大修复。"
            ready_level = "未就绪"

        print(f"   状态: {ready_level}")
        print(f"   详情: {system_status}")

        if critical_failures:
            print(f"\n🔧 需要修复的关键问题:")
            for failure in critical_failures:
                print(f"   - {failure}")

        # 建议和下一步
        print(f"\n💡 建议和下一步:")
        if ready_level == "完全就绪":
            print("   - 🚀 系统已完全就绪，可以开始使用")
            print("   - 📚 建议准备用户文档和使用指南")
            print("   - 🔄 考虑设置定期回归测试")
        elif ready_level == "基本就绪":
            print("   - ✅ 核心功能可以投入使用")
            print("   - 🔧 并行修复非关键功能问题")
            print("   - 📊 监控系统运行状况")
        else:
            print("   - 🔧 优先修复关键功能问题")
            print("   - 🧪 修复后重新运行相关测试")
            print("   - 📋 考虑降低功能复杂度")

        return ready_level in ["完全就绪", "基本就绪"]

    def save_test_report(self):
        """保存测试报告到文件"""
        if not self.config["reporting"]["save_detailed_logs"]:
            return

        # 创建报告目录
        report_dir = Path(self.config["reporting"]["report_directory"])
        report_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 保存JSON格式详细报告
        json_report = {
            "test_suite": "日语学习Multi-Agent系统测试",
            "timestamp": datetime.now().isoformat(),
            "total_time": self.total_time,
            "config": self.config,
            "results": self.test_results,
            "failed_tests": self.failed_tests,
            "summary": {
                "total_phases": len(self.test_results),
                "passed": len([r for r in self.test_results.values() if r.get("status") == "passed"]),
                "failed": len([r for r in self.test_results.values() if r.get("status") == "failed"]),
                "errors": len([r for r in self.test_results.values() if r.get("status") == "error"]),
                "skipped": len([r for r in self.test_results.values() if r.get("status") == "skipped"])
            }
        }

        json_file = report_dir / f"test_report_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, indent=2, ensure_ascii=False)

        print(f"\n💾 详细测试报告已保存: {json_file}")

        # 如果需要生成HTML报告
        if self.config["reporting"]["generate_html_report"]:
            html_file = report_dir / f"test_report_{timestamp}.html"
            self._generate_html_report(json_report, html_file)
            print(f"📄 HTML测试报告已保存: {html_file}")

    def _generate_html_report(self, report_data: Dict, html_file: Path):
        """生成HTML格式的测试报告"""
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>日语学习Multi-Agent系统 - 测试报告</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; text-align: center; margin-bottom: 30px; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ background: #ecf0f1; padding: 20px; border-radius: 8px; text-align: center; }}
        .summary-card h3 {{ margin: 0; font-size: 2em; }}
        .passed {{ background-color: #d5edda; color: #155724; }}
        .failed {{ background-color: #f8d7da; color: #721c24; }}
        .error {{ background-color: #fff3cd; color: #856404; }}
        .skipped {{ background-color: #e2e3e5; color: #383d41; }}
        .phase {{ margin: 20px 0; padding: 20px; border-left: 4px solid #3498db; background: #f8f9fa; }}
        .phase.passed {{ border-left-color: #28a745; }}
        .phase.failed {{ border-left-color: #dc3545; }}
        .phase.error {{ border-left-color: #ffc107; }}
        .phase.skipped {{ border-left-color: #6c757d; }}
        .status {{ font-weight: bold; font-size: 1.2em; }}
        .timestamp {{ color: #6c757d; font-size: 0.9em; }}
        .details {{ margin-top: 15px; }}
        .test-list {{ list-style: none; padding: 0; }}
        .test-list li {{ padding: 5px 0; }}
        .test-pass::before {{ content: "✅ "; }}
        .test-fail::before {{ content: "❌ "; }}
        .config-section {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎌 日语学习Multi-Agent系统 - 测试报告</h1>

        <div class="summary">
            <div class="summary-card passed">
                <h3>{report_data['summary']['passed']}</h3>
                <p>通过</p>
            </div>
            <div class="summary-card failed">
                <h3>{report_data['summary']['failed']}</h3>
                <p>失败</p>
            </div>
            <div class="summary-card error">
                <h3>{report_data['summary']['errors']}</h3>
                <p>错误</p>
            </div>
            <div class="summary-card skipped">
                <h3>{report_data['summary']['skipped']}</h3>
                <p>跳过</p>
            </div>
        </div>

        <p class="timestamp">测试时间: {report_data['timestamp']}</p>
        <p class="timestamp">总耗时: {report_data.get('total_time', 0):.2f} 秒</p>

        <h2>📋 测试阶段详情</h2>
        """

        phase_names = {
            "phase_1": "Phase 1: 数据库基础设施",
            "phase_2": "Phase 2: 单智能体功能",
            "phase_3": "Phase 3: 多智能体协作",
            "phase_4": "Phase 4: 数据持久化",
            "phase_5": "Phase 5: 端到端集成"
        }

        for phase_key, phase_name in phase_names.items():
            result = report_data['results'].get(phase_key, {"status": "not_run"})
            status = result.get("status", "not_run")

            status_text = {
                "passed": "✅ 通过",
                "failed": "❌ 失败",
                "error": "💥 错误",
                "skipped": "⏭️ 跳过",
                "not_run": "❓ 未运行"
            }.get(status, status)

            html_content += f"""
        <div class="phase {status}">
            <h3>{phase_name}</h3>
            <div class="status">{status_text}</div>
            <div class="details">
                <p>{result.get('details', '无详情')}</p>
                <p class="timestamp">时间: {result.get('timestamp', 'N/A')}</p>
            """

            if 'error' in result:
                html_content += f"<p><strong>错误:</strong> {result['error']}</p>"

            html_content += "</div></div>"

        if report_data['failed_tests']:
            html_content += f"""
        <h2>⚠️ 失败的测试项目</h2>
        <ul class="test-list">
            {"".join(f'<li class="test-fail">{test}</li>' for test in report_data['failed_tests'])}
        </ul>
        """

        html_content += """
        </div>
</body>
</html>
        """

        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

    async def run_all_tests(self):
        """运行完整测试套件"""
        self.start_time = time.time()

        print("🎌 日语学习Multi-Agent系统 - 完整测试套件")
        print("=" * 80)
        print(f"📅 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⚙️  测试配置: {len([k for k, v in self.config['test_phases'].items() if v])} 个阶段已启用")

        # 按顺序执行所有测试阶段
        phase_results = []

        # Phase 1: 数据库基础设施（必须通过）
        phase_1_success = await self.run_phase_1_database_tests()
        phase_results.append(("Phase 1", phase_1_success))

        # 如果数据库测试失败，询问是否继续
        if not phase_1_success:
            print("\n⚠️  数据库基础设施测试失败！")
            continue_anyway = input("是否继续其他测试？(y/N): ").lower().strip() == 'y'
            if not continue_anyway:
                print("🛑 测试中止")
                return False

        # Phase 2: 单智能体功能（建议通过）
        phase_2_success = await self.run_phase_2_single_agent_tests()
        phase_results.append(("Phase 2", phase_2_success))

        # Phase 3: 多智能体协作（可选）
        phase_3_success = await self.run_phase_3_collaboration_tests()
        phase_results.append(("Phase 3", phase_3_success))

        # Phase 4: 数据持久化（可选）
        phase_4_success = await self.run_phase_4_persistence_tests()
        phase_results.append(("Phase 4", phase_4_success))

        # Phase 5: 端到端集成（重要）
        phase_5_success = await self.run_phase_5_integration_tests()
        phase_results.append(("Phase 5", phase_5_success))

        # 计算总时间
        end_time = time.time()
        self.total_time = end_time - self.start_time

        # 生成最终报告
        overall_success = self.generate_final_report()

        # 保存报告
        self.save_test_report()

        return overall_success


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='日语学习Multi-Agent系统测试套件')
    parser.add_argument('--config', '-c', default='test_config.json', help='测试配置文件路径')
    parser.add_argument('--generate-config', action='store_true', help='生成配置文件模板')
    parser.add_argument('--phases', nargs='+', choices=['1', '2', '3', '4', '5'], help='指定要运行的测试阶段')

    args = parser.parse_args()

    # 生成配置模板
    if args.generate_config:
        runner = TestSuiteRunner()
        runner.save_config_template('test_config_template.json')
        return

    # 创建测试运行器
    runner = TestSuiteRunner(args.config)

    # 如果指定了特定阶段
    if args.phases:
        for phase in ['1', '2', '3', '4', '5']:
            phase_key = f"phase_{phase}_" + {
                '1': 'database', '2': 'single_agent', '3': 'collaboration',
                '4': 'persistence', '5': 'integration'
            }[phase]
            runner.config["test_phases"][phase_key] = phase in args.phases

    # 运行测试
    try:
        success = asyncio.run(runner.run_all_tests())

        if success:
            print(f"\n🎊 测试套件执行完成！系统基本就绪。")
            sys.exit(0)
        else:
            print(f"\n🔧 测试套件发现问题，请根据报告进行修复。")
            sys.exit(1)

    except KeyboardInterrupt:
        print(f"\n⏹️  测试被用户中断")
        sys.exit(2)
    except Exception as e:
        print(f"\n💥 测试执行异常: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()