#!/usr/bin/env python3
"""
启动日语学习智能体Web界面
运行方式: python run_ui.py
"""

import subprocess
import sys
import os
from pathlib import Path


def check_streamlit():
    """检查streamlit是否安装"""
    try:
        import streamlit
        print("✅ Streamlit已安装")
        return True
    except ImportError:
        print("❌ Streamlit未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"])
        return True


def create_streamlit_app():
    """创建简化版Streamlit应用"""
    app_content = '''
import streamlit as st
import asyncio
import sys
from pathlib import Path
from datetime import datetime
import re

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

try:
    from src.core.agents.core_agents.tanaka import TanakaAgent
    from src.data.models.agent import Agent
    from src.data.models.base import AgentPersonality
except ImportError as e:
    st.error(f"导入错误: {e}")
    st.stop()

# 页面配置
st.set_page_config(
    page_title="🎌 日语学习智能体",
    page_icon="🎌",
    layout="wide"
)

# 自定义样式
st.markdown("""
<style>
.user-message {
    background-color: #e3f2fd;
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
    border-left: 4px solid #2196f3;
}
.agent-message {
    background-color: #fff3e0;
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
    border-left: 4px solid #ff9800;
}
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'tanaka_agent' not in st.session_state:
    try:
        personality = AgentPersonality(
            strictness=8, humor=3, patience=6, creativity=4, formality=9
        )
        config = Agent(
            name="田中先生",
            description="严格的日语语法老师", 
            personality=personality,
            expertise_areas=["grammar", "formal_japanese"],
            system_prompt="严格的日语老师"
        )
        st.session_state.tanaka_agent = TanakaAgent(config)
    except Exception as e:
        st.error(f"创建智能体失败: {e}")
        st.stop()

# 主标题
st.title("🎌 日语学习智能体 - 田中先生")
st.markdown("### 与严格的语法老师一起学习日语！")

# 侧边栏
with st.sidebar:
    st.header("👨‍🏫 田中先生")
    st.write("**专业**: 日语语法")
    st.write("**性格**: 严格认真")

    # 性格特征
    st.subheader("性格特征")
    agent = st.session_state.tanaka_agent
    st.metric("严谨程度", f"{agent.config.personality.strictness}/10")
    st.metric("耐心度", f"{agent.config.personality.patience}/10")
    st.metric("正式程度", f"{agent.config.personality.formality}/10")

    st.subheader("对话统计")
    st.metric("总对话数", len(st.session_state.messages) // 2)

# 显示对话历史
st.subheader("💬 对话记录")

if not st.session_state.messages:
    st.info("🌸 欢迎！请开始您的第一次对话。试试用日语说 'こんにちは'！")
else:
    for message in st.session_state.messages:
        if message['role'] == 'user':
            st.markdown(f"""
            <div class="user-message">
                <strong>👤 您:</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="agent-message">
                <strong>👨‍🏫 田中先生:</strong><br>
                {message['content']}
                <br><small>置信度: {message.get('confidence', 0.8):.1%} | 
                响应类型: {message.get('metadata', {}).get('response_type', 'unknown')}</small>
            </div>
            """, unsafe_allow_html=True)

# 快速输入按钮
st.subheader("🚀 快速开始")
col1, col2, col3, col4 = st.columns(4)

quick_messages = [
    "こんにちは",
    "今日は良い天気ですね", 
    "ありがとうございます",
    "Hello world"
]

for i, msg in enumerate(quick_messages):
    with [col1, col2, col3, col4][i]:
        if st.button(msg, key=f"quick_{i}"):
            # 处理快速输入
            async def process_quick_message():
                response = await st.session_state.tanaka_agent.process_message(msg)

                st.session_state.messages.append({'role': 'user', 'content': msg})
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': response.content,
                    'confidence': response.confidence,
                    'metadata': response.metadata
                })

            asyncio.run(process_quick_message())
            st.experimental_rerun()

# 用户输入
st.subheader("✏️ 输入您的消息")
user_input = st.text_area(
    "请用日语或英语输入:",
    placeholder="例如: こんにちは、田中先生！",
    height=100,
    key="user_input"
)

if st.button("📤 发送消息", type="primary"):
    if user_input.strip():
        with st.spinner("田中先生正在思考..."):
            async def process_message():
                try:
                    response = await st.session_state.tanaka_agent.process_message(user_input)

                    # 添加到消息历史
                    st.session_state.messages.append({
                        'role': 'user', 
                        'content': user_input
                    })
                    st.session_state.messages.append({
                        'role': 'assistant',
                        'content': response.content,
                        'confidence': response.confidence,
                        'metadata': response.metadata
                    })

                    return response
                except Exception as e:
                    st.error(f"处理消息时出错: {e}")
                    return None

            response = asyncio.run(process_message())
            if response:
                st.success("消息已发送！")
                st.experimental_rerun()

# 学习提示
st.subheader("💡 学习提示")
tips = [
    "🎯 尝试日语问候: こんにちは (你好)",
    "📚 练习感谢: ありがとうございます (谢谢)",
    "🌸 描述天气: 今日は良い天気ですね (今天天气真好)",
    "✨ 用英语测试纠错功能",
    "🎌 学习正式的敬语表达"
]

for tip in tips:
    st.write(f"- {tip}")

st.markdown("---")
st.markdown("🎌 **Japanese Learning Multi-Agent System v0.1.0** | 田中先生专业语法指导")
'''

    # 保存应用文件
    os.makedirs("src/ui", exist_ok=True)
    with open("src/ui/streamlit_app.py", "w", encoding="utf-8") as f:
        f.write(app_content)

    print("✅ Streamlit应用已创建")


def main():
    """主启动函数"""
    print("🚀 启动日语学习智能体Web界面...")

    # 检查依赖
    if not check_streamlit():
        print("❌ 无法安装Streamlit")
        return

    # 创建应用
    create_streamlit_app()

    # 启动Streamlit
    print("🌟 正在启动Web界面...")
    print("📱 浏览器将自动打开 http://localhost:8501")
    print("⚡ 使用 Ctrl+C 停止服务")

    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "src/ui/streamlit_app.py",
            "--server.address", "localhost",
            "--server.port", "8501"
        ])
    except KeyboardInterrupt:
        print("\n👋 Web界面已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")


if __name__ == "__main__":
    main()