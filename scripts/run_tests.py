"""测试运行脚本"""
import subprocess
import sys
from pathlib import Path


def run_unit_tests():
    """运行单元测试"""
    print("🧪 运行单元测试...")

    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/unit/",
        "-v",
        "--tb=short",
        "--disable-warnings"
    ], cwd=Path.cwd())

    return result.returncode == 0


def check_code_style():
    """检查代码风格"""
    print("📋 检查代码风格...")

    # 使用 flake8 进行基本检查
    result = subprocess.run([
        sys.executable, "-m", "flake8",
        "src/",
        "--max-line-length=100",
        "--ignore=E203,W503"
    ], cwd=Path.cwd())

    return result.returncode == 0


if __name__ == "__main__":
    print("🚀 开始代码质量检查...\n")

    # 运行测试
    tests_passed = run_unit_tests()

    # 检查代码风格
    style_passed = check_code_style()

    # 总结
    if tests_passed and style_passed:
        print("\n✅ 所有检查通过！代码质量良好。")
        sys.exit(0)
    else:
        print("\n❌ 发现问题，请修复后重试。")
        sys.exit(1)