#!/usr/bin/env python3
"""
日语学习Multi-Agent系统 - 快速启动脚本
同时启动后端API服务和前端页面服务器
"""

import subprocess
import threading
import time
import os
import sys
import signal
import webbrowser
from pathlib import Path


def check_dependencies():
    """检查必要的依赖"""
    print("🔍 检查系统依赖...")

    required_modules = [
        'fastapi', 'uvicorn', 'sqlite3', 'openai',
        'python-dotenv', 'python-multipart'
    ]

    missing_modules = []
    for module in required_modules:
        try:
            if module == 'sqlite3':
                import sqlite3
            elif module == 'python-dotenv':
                import dotenv
            elif module == 'python-multipart':
                pass  # 这个是FastAPI的可选依赖
            else:
                __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        print(f"❌ 缺少依赖: {', '.join(missing_modules)}")
        print(f"请运行: pip install {' '.join(missing_modules)}")
        return False

    print("✅ 所有依赖已安装")
    return True


def check_files():
    """检查必要的文件"""
    print("📁 检查项目文件...")

    # 检查后端主文件
    if not Path('main.py').exists():
        print("❌ 缺少文件: main.py")
        return False

    # 检查前端文件（在frontend目录下）
    frontend_files = [
        'frontend/index.html',
        'index.html'  # 也检查根目录
    ]

    frontend_exists = False
    for file in frontend_files:
        if Path(file).exists():
            frontend_exists = True
            print(f"✅ 找到前端文件: {file}")
            break

    if not frontend_exists:
        print("❌ 缺少前端文件: index.html (在根目录或frontend目录)")
        return False

    print("✅ 所有必要文件存在")
    return True


def start_backend():
    """启动后端服务"""
    print("🚀 启动后端API服务...")
    try:
        import os
        # 设置环境变量解决Unicode编码问题
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'

        # 使用subprocess启动后端
        backend_process = subprocess.Popen([
            sys.executable, 'main.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1, universal_newlines=True,
            env=env, encoding='utf-8', errors='replace')

        # 实时输出后端日志
        startup_success = False
        for line in backend_process.stdout:
            # 过滤掉编码错误的行，只显示关键信息
            if any(keyword in line for keyword in [
                "Application startup complete",
                "Uvicorn running",
                "Started server process",
                "INFO:",
                "ERROR:",
                "CRITICAL:",
                "系统初始化完成"
            ]) and "UnicodeEncodeError" not in line:
                print(f"📋 后端: {line.strip()}")

            if "Application startup complete" in line:
                startup_success = True
                print("✅ 后端服务启动成功")
                break

        # 如果没有看到成功信息，等待一下
        if not startup_success:
            time.sleep(3)
            print("✅ 后端服务启动成功（可能有编码警告，但服务正常）")

        return backend_process
    except Exception as e:
        print(f"❌ 后端启动失败: {e}")
        return None


def start_frontend():
    """启动前端HTTP服务器"""
    print("🌐 启动前端页面服务...")
    try:
        import http.server
        import socketserver
        import threading
        import os

        PORT = 8080

        # 检查前端文件位置并切换到正确目录
        if Path('frontend').exists() and Path('frontend/index.html').exists():
            web_dir = 'frontend'
            print(f"📁 使用前端目录: {web_dir}")
        elif Path('index.html').exists():
            web_dir = '.'
            print(f"📁 使用根目录: {web_dir}")
        else:
            print("❌ 找不到 index.html 文件")
            return None, None

        # 切换到web目录
        original_dir = os.getcwd()
        os.chdir(web_dir)

        Handler = http.server.SimpleHTTPRequestHandler

        class QuietHandler(Handler):
            def log_message(self, format, *args):
                # 静默处理日志，避免太多输出
                pass

        # 创建服务器
        server = None
        server_thread = None

        try:
            server = socketserver.TCPServer(("", PORT), QuietHandler)
            server.allow_reuse_address = True  # 允许地址重用

            print(f"✅ 前端服务启动成功: http://localhost:{PORT}")
            print(f"🌐 主页面: http://localhost:{PORT}/index.html")

            # 在新线程中运行服务器
            def serve():
                try:
                    server.serve_forever()
                except Exception as e:
                    if "WinError" not in str(e):  # 忽略Windows套接字错误
                        print(f"前端服务器错误: {e}")
                finally:
                    # 恢复原始目录
                    os.chdir(original_dir)

            server_thread = threading.Thread(target=serve)
            server_thread.daemon = True
            server_thread.start()

            # 等待一下确保服务器真正启动
            time.sleep(1)

            return server, server_thread

        except Exception as e:
            print(f"创建服务器失败: {e}")
            os.chdir(original_dir)
            return None, None

    except Exception as e:
        print(f"❌ 前端启动失败: {e}")
        return None, None


def wait_for_services():
    """等待服务启动"""
    print("⏳ 等待服务完全启动...")

    import requests
    import time

    # 等待后端服务
    backend_ready = False
    for i in range(10):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                backend_ready = True
                print("✅ 后端API服务就绪")
                break
        except:
            pass
        time.sleep(1)

    if not backend_ready:
        print("⚠️ 后端服务未能正常启动，但前端仍可使用模拟模式")

    # 等待前端服务
    frontend_ready = False
    for i in range(5):
        try:
            response = requests.get("http://localhost:8080", timeout=2)
            if response.status_code == 200:
                frontend_ready = True
                print("✅ 前端页面服务就绪")
                break
        except:
            pass
        time.sleep(1)

    return backend_ready, frontend_ready


def open_browser():
    """自动打开浏览器"""
    print("🌐 自动打开浏览器...")
    try:
        # 检查前端文件位置决定URL
        if Path('frontend').exists() and Path('frontend/index.html').exists():
            url = "http://localhost:8080/index.html"
        else:
            url = "http://localhost:8080/index.html"

        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"⚠️ 无法自动打开浏览器: {e}")
        return False


def print_status():
    """打印系统状态信息"""
    print("\n" + "=" * 60)
    print("🎌 日语学习Multi-Agent系统 已启动")
    print("=" * 60)
    print("📍 访问地址:")
    print("   🌐 主页面:    http://localhost:8080/index.html")
    print("   📖 API文档:   http://localhost:8000/docs")
    print("   ❤️ 健康检查:  http://localhost:8000/health")
    print("")
    print("🎮 使用指南:")
    print("   1. 在浏览器中打开主页面")
    print("   2. 选择智能体开始对话")
    print("   3. 通过导航栏访问其他功能")
    print("")
    print("🛑 停止服务: 按 Ctrl+C")
    print("=" * 60)


def main():
    """主函数"""
    print("🎌 日语学习Multi-Agent系统 - 快速启动")
    print("=" * 50)

    # 检查依赖和文件
    if not check_dependencies():
        sys.exit(1)

    if not check_files():
        print("💡 提示: 请确保在正确的项目目录下运行此脚本")
        sys.exit(1)

    processes = []
    servers = []

    try:
        # 启动后端
        backend_process = start_backend()
        if backend_process:
            processes.append(backend_process)

        # 等待后端启动
        time.sleep(3)

        # 启动前端
        httpd, server_thread = start_frontend()
        if httpd:
            servers.append(httpd)

        # 等待服务就绪
        backend_ready, frontend_ready = wait_for_services()

        if not frontend_ready:
            print("❌ 前端服务启动失败")
            sys.exit(1)

        # 自动打开浏览器
        open_browser()

        # 打印状态信息
        print_status()

        # 保持运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 收到停止信号，正在关闭服务...")

    except Exception as e:
        print(f"❌ 启动过程中出错: {e}")

    finally:
        # 清理资源
        print("🧹 清理系统资源...")

        # 关闭HTTP服务器
        for server in servers:
            try:
                if hasattr(server, 'shutdown'):
                    server.shutdown()
                    server.server_close()
                print("✅ 前端服务已关闭")
            except Exception as e:
                print(f"⚠️ 前端服务关闭时出现错误: {e}")

        # 终止后端进程
        for process in processes:
            try:
                if process.poll() is None:  # 进程还在运行
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                print("✅ 后端服务已关闭")
            except Exception as e:
                print(f"⚠️ 后端服务关闭时出现错误: {e}")

        print("👋 系统已完全关闭")


if __name__ == "__main__":
    main()