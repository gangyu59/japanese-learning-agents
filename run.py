#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎌 日语学习Multi-Agent系统 - 修复版启动脚本
"""

import os
import sys
import subprocess
import threading
import time
import webbrowser
import signal
import atexit
import socket
from pathlib import Path
import http.server
import socketserver


class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_colored(text, color=Colors.WHITE):
    print(f"{color}{text}{Colors.END}")


def print_banner():
    banner = """
🎌 日语学习Multi-Agent系统 - 启动器
==================================================
"""
    print_colored(banner, Colors.CYAN + Colors.BOLD)


def check_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0


def check_dependencies():
    print_colored("🔍 检查系统依赖...", Colors.BLUE)

    # 移除了python-multipart依赖检查
    required_packages = [
        'fastapi', 'uvicorn', 'streamlit', 'chromadb',
        'aiohttp', 'pydantic'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print_colored(f"❌ 缺少依赖包: {', '.join(missing_packages)}", Colors.RED)
        print_colored("💡 请运行: pip install -r requirements.txt", Colors.YELLOW)
        return False

    print_colored("✅ 所有依赖已安装", Colors.GREEN)
    return True


def check_project_structure():
    print_colored("📁 检查项目文件...", Colors.BLUE)

    required_files = [
        "main.py",
        "frontend/index.html",
        "requirements.txt"
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print_colored(f"❌ 缺少文件: {', '.join(missing_files)}", Colors.RED)
        return False

    for file_path in required_files:
        print_colored(f"✅ 找到文件: {file_path}", Colors.GREEN)

    return True


class ServiceManager:
    def __init__(self):
        self.processes = []
        self.servers = []
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        print_colored("\n🛑 收到退出信号，正在关闭服务...", Colors.YELLOW)
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        print_colored("🧹 清理服务...", Colors.BLUE)

        for server in self.servers:
            try:
                server.shutdown()
                server.server_close()
                print_colored("✅ HTTP服务器已关闭", Colors.GREEN)
            except Exception as e:
                print_colored(f"⚠️ 关闭HTTP服务器时出错: {e}", Colors.YELLOW)

        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print_colored("✅ 后端进程已终止", Colors.GREEN)
            except subprocess.TimeoutExpired:
                process.kill()
                print_colored("⚠️ 强制终止后端进程", Colors.YELLOW)
            except Exception as e:
                print_colored(f"⚠️ 终止进程时出错: {e}", Colors.YELLOW)

    # def start_backend(self):
    #     """启动后端服务"""
    #     print_colored("🚀 启动后端API服务...", Colors.BLUE)
    #     print_colored("💡 请在新的命令行窗口中手动运行以下命令：", Colors.YELLOW)
    #     print_colored("   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload", Colors.CYAN + Colors.BOLD)
    #     print_colored("⏳ 等待您手动启动后端服务...", Colors.BLUE)
    #
    #     backend_port = 8000
    #
    #     # 等待用户手动启动后端
    #     for i in range(30):  # 等待30秒
    #         if check_port(backend_port):
    #             print_colored(f"✅ 检测到后端服务: http://localhost:{backend_port}", Colors.GREEN)
    #             return True, backend_port
    #         time.sleep(1)
    #         if i % 5 == 0:  # 每5秒提醒一次
    #             print_colored(f"⏳ 还在等待后端启动... ({30 - i}秒)", Colors.BLUE)
    #
    #     print_colored("⚠️ 未检测到后端服务，前端将以模拟模式运行", Colors.YELLOW)
    #     return False, backend_port

    def start_backend(self, port: int = 8000):
        """自动启动后端服务（稳健版）"""
        print_colored("🚀 启动后端API服务（自动）...", Colors.BLUE)

        import http.client
        import contextlib

        def http_ready():
            # 优先探测 /health，其次 /docs
            for path in ["/health", "/docs", "/openapi.json", "/"]:
                try:
                    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=1.5)
                    conn.request("GET", path)
                    resp = conn.getresponse()
                    if 200 <= resp.status < 500:
                        return True
                except Exception:
                    pass
                finally:
                    with contextlib.suppress(Exception):
                        conn.close()
            return False

        if check_port(port) or http_ready():
            print_colored(f"✅ 检测到已有后端服务: http://localhost:{port}", Colors.GREEN)
            return True, port

        # 两套启动参数：先稳定版（无 --reload），失败再尝试带 --reload
        candidate_cmds = [
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(port)],
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(port), "--reload"],
        ]

        for idx, cmd in enumerate(candidate_cmds, start=1):
            mode = "稳定模式" if "--reload" not in cmd else "开发热重载模式"
            print_colored(f"⏳ 正在拉起后端（{mode}）: {' '.join(cmd)}", Colors.BLUE)

            try:
                # 关键点：不再用 PIPE，直接继承父进程的 stdout/stderr，避免卡死
                proc = subprocess.Popen(cmd, creationflags=0)
                self.processes.append(proc)

                # 等待就绪（最多 90 秒），期间若进程退出则立即失败并切换下一种模式
                for sec in range(90):
                    if http_ready() or check_port(port):
                        print_colored(f"✅ 后端已就绪: http://localhost:{port}", Colors.GREEN)
                        return True, port
                    if proc.poll() is not None:
                        print_colored("❌ 后端进程提前退出（请查看上方 Uvicorn 日志）", Colors.RED)
                        break
                    if sec % 10 == 0:
                        print_colored(f"⏳ 等待后端启动中...（剩余 {90 - sec} 秒）", Colors.BLUE)
                    time.sleep(1)

                # 这一种模式超时/失败，先杀掉，再试下一种
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                except Exception:
                    with contextlib.suppress(Exception):
                        proc.kill()

                if idx < len(candidate_cmds):
                    print_colored("🔁 切换另一种启动模式重试...", Colors.YELLOW)

            except FileNotFoundError:
                print_colored("❌ 未找到 uvicorn，可执行: pip install uvicorn", Colors.RED)
                return False, port
            except Exception as e:
                print_colored(f"❌ 启动后端失败: {e}", Colors.RED)
                # 尝试下一种模式
                continue

        print_colored("⚠️ 后端启动失败，请查看上方 Uvicorn 输出诊断", Colors.YELLOW)
        return False, port

    def start_frontend(self):
        """启动前端服务"""
        print_colored("🌐 启动前端页面服务...", Colors.BLUE)

        frontend_port = 8080
        if check_port(frontend_port):
            print_colored("⚠️ 端口8080被占用，尝试其他端口", Colors.YELLOW)
            for port in range(8081, 8090):
                if not check_port(port):
                    frontend_port = port
                    break

        try:
            frontend_dir = Path("frontend")
            if not frontend_dir.exists():
                print_colored(f"❌ 前端目录不存在: {frontend_dir}", Colors.RED)
                return False, None

            print_colored(f"📁 使用前端目录: {frontend_dir.absolute()}", Colors.BLUE)

            original_dir = os.getcwd()
            os.chdir(frontend_dir)

            class QuietHandler(http.server.SimpleHTTPRequestHandler):
                def log_message(self, format, *args):
                    pass

            httpd = socketserver.TCPServer(("", frontend_port), QuietHandler)
            self.servers.append(httpd)

            def run_server():
                try:
                    print_colored(f"✅ 前端服务启动成功: http://localhost:{frontend_port}", Colors.GREEN)
                    httpd.serve_forever()
                except Exception as e:
                    if "WinError 10053" not in str(e):
                        print_colored(f"⚠️ 前端服务异常: {e}", Colors.YELLOW)
                finally:
                    os.chdir(original_dir)

            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()

            time.sleep(2)
            return True, frontend_port

        except Exception as e:
            print_colored(f"❌ 前端服务启动失败: {e}", Colors.RED)
            if 'original_dir' in locals():
                os.chdir(original_dir)
            return False, None


def main():
    print_banner()

    if not check_dependencies():
        input("按回车键退出...")
        return

    if not check_project_structure():
        input("按回车键退出...")
        return

    service_manager = ServiceManager()

    # 启动后端（手动方式）
    backend_success, backend_port = service_manager.start_backend()

    # 启动前端
    frontend_success, frontend_port = service_manager.start_frontend()

    if not frontend_success:
        print_colored("❌ 前端服务启动失败", Colors.RED)
        input("按回车键退出...")
        return

    # 构建访问URL
    frontend_url = f"http://localhost:{frontend_port}/index.html"
    backend_docs_url = f"http://localhost:{backend_port}/docs" if backend_success else "后端未启动"
    health_url = f"http://localhost:{backend_port}/health" if backend_success else "后端未启动"

    # 打印服务信息
    print_colored("=" * 60, Colors.CYAN)
    print_colored("🎌 日语学习Multi-Agent系统 已启动", Colors.CYAN + Colors.BOLD)
    print_colored("=" * 60, Colors.CYAN)
    print_colored(f"📍 访问地址:", Colors.BLUE + Colors.BOLD)
    print_colored(f"   🌐 主页面:    {frontend_url}", Colors.WHITE)
    print_colored(f"   📖 API文档:   {backend_docs_url}", Colors.WHITE)
    print_colored(f"   ❤️ 健康检查:  {health_url}", Colors.WHITE)
    print_colored("=" * 60, Colors.CYAN)

    if backend_success:
        print_colored("🎉 前后端服务都已启动！", Colors.GREEN + Colors.BOLD)
    else:
        print_colored("⚠️ 仅前端服务启动，系统运行在模拟模式", Colors.YELLOW)

    # 自动打开浏览器
    try:
        print_colored("🌐 自动打开浏览器...", Colors.BLUE)
        webbrowser.open(frontend_url)
        print_colored("✅ 浏览器已打开", Colors.GREEN)
    except Exception as e:
        print_colored(f"⚠️ 无法自动打开浏览器: {e}", Colors.YELLOW)
        print_colored(f"请手动访问: {frontend_url}", Colors.BLUE)

    print_colored("\n💡 提示:", Colors.YELLOW + Colors.BOLD)
    print_colored("   - 按 Ctrl+C 退出系统", Colors.WHITE)
    print_colored("   - 确保后端服务正在运行以使用AI功能", Colors.WHITE)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print_colored("\n👋 感谢使用日语学习Multi-Agent系统！", Colors.CYAN + Colors.BOLD)


if __name__ == "__main__":
    main()