"""
修复后的Streamlit应用 - 兼容新版本
替换 src/ui/streamlit_app.py 的内容
"""

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
.main-header {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.user-message {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 20px 20px 5px 20px;
    margin: 1rem 0;
    margin-left: 20%;
    box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3);
}

.agent-message {
    background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
    color: #333;
    padding: 1rem 1.5rem;
    border-radius: 20px 20px 20px 5px;
    margin: 1rem 0;
    margin-right: 20%;
    border-left: 4px solid #ff9800;
    box-shadow: 0 3px 10px rgba(255, 152, 0, 0.2);
}

.quick-btn {
    background: linear-gradient(45deg, #667eea, #764ba2);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 25px;
    margin: 0.2rem;
    cursor: pointer;
    transition: all 0.3s ease;
}

.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    border: 2px solid #f0f0f0;
    margin: 0.5rem 0;
    text-align: center;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.stats-container {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
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
        st.success("✅ 田中先生已准备就绪！")
    except Exception as e:
        st.error(f"创建智能体失败: {e}")
        st.stop()

if 'stats' not in st.session_state:
    st.session_state.stats = {
        'total_messages': 0,
        'japanese_messages': 0,
        'corrections': 0,
        'praises': 0,
        'session_start': datetime.now()
    }

# 主标题
st.markdown("""
<div class="main-header">
    <h1>🎌 日语学习智能体系统</h1>
    <h3>田中先生的专业语法课堂</h3>
    <p>Tanaka-sensei's Professional Grammar Classroom</p>
</div>
""", unsafe_allow_html=True)

# 创建主要布局
col1, col2 = st.columns([2, 1])

with col1:
    # 对话区域
    st.subheader("💬 实时对话")

    # 显示对话历史
    chat_container = st.container()
    with chat_container:
        if not st.session_state.messages:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 15px; margin: 1rem 0;">
                <h3>🌸 欢迎来到田中先生的课堂！</h3>
                <p>请开始您的第一次对话</p>
                <p><strong>建议:</strong> 试试用日语说 "こんにちは" (你好)！</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for i, message in enumerate(st.session_state.messages):
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div class="user-message">
                        <strong>👤 您:</strong> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    confidence = message.get('confidence', 0.8)
                    response_type = message.get('metadata', {}).get('response_type', 'unknown')
                    processing_time = message.get('metadata', {}).get('processing_time', 0)

                    st.markdown(f"""
                    <div class="agent-message">
                        <strong>👨‍🏫 田中先生:</strong><br>
                        {message['content']}<br>
                        <small style="opacity: 0.7;">
                            📊 置信度: {confidence:.1%} | 🏷️ 类型: {response_type} | ⏱️ {processing_time:.2f}s
                        </small>
                    </div>
                    """, unsafe_allow_html=True)

    # 快速输入区域
    st.subheader("🚀 快速开始对话")

    quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
    quick_messages = [
        ("こんにちは", "你好"),
        ("今日は良い天気ですね", "今天天气真好"),
        ("ありがとうございます", "谢谢"),
        ("Hello world", "英语测试")
    ]

    for i, (msg, desc) in enumerate(quick_messages):
        with [quick_col1, quick_col2, quick_col3, quick_col4][i]:
            if st.button(f"{msg}\n({desc})", key=f"quick_{i}", use_container_width=True):
                # 直接处理快速输入，不使用rerun
                asyncio.run(process_message(msg))

    # 用户输入区域
    st.subheader("✏️ 自由输入")
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "请输入您的消息 (支持日语和英语):",
            placeholder="例如: こんにちは、田中先生！\n或者: 日本語を勉強しています。",
            height=100,
            help="💡 提示: 田中先生会纠正语法错误，并给出专业建议"
        )

        submitted = st.form_submit_button("📤 发送消息", type="primary", use_container_width=True)

        if submitted and user_input.strip():
            with st.spinner("🤔 田中先生正在仔细思考..."):
                asyncio.run(process_message(user_input.strip()))

with col2:
    # 侧边栏信息
    st.subheader("👨‍🏫 田中先生档案")

    # 智能体信息卡片
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 15px; border: 2px solid #e3f2fd; margin: 1rem 0;">
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 3rem;">👨‍🏫</div>
            <h3 style="margin: 0.5rem 0;">田中先生</h3>
            <p style="color: #666; margin: 0;">専門的な日本語文法教師</p>
        </div>
        <hr>
        <p><strong>🎯 专业领域:</strong> 日语语法、敬语指导</p>
        <p><strong>🎭 性格特点:</strong> 严格认真、专业负责</p>
        <p><strong>🏆 教学风格:</strong> 细致纠错、鼓励进步</p>
    </div>
    """, unsafe_allow_html=True)

    # 性格特征
    st.subheader("📊 性格特征分析")
    agent = st.session_state.tanaka_agent
    personality = agent.config.personality

    # 使用进度条显示特征
    st.write("**严谨程度**")
    st.progress(personality.strictness / 10)
    st.write(f"{personality.strictness}/10 - 非常严格")

    st.write("**耐心度**")
    st.progress(personality.patience / 10)
    st.write(f"{personality.patience}/10 - 比较耐心")

    st.write("**正式程度**")
    st.progress(personality.formality / 10)
    st.write(f"{personality.formality}/10 - 极其正式")

    st.write("**幽默感**")
    st.progress(personality.humor / 10)
    st.write(f"{personality.humor}/10 - 较少幽默")

    # 对话统计
    st.subheader("📈 本次会话统计")
    stats = st.session_state.stats

    # 统计卡片
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("总对话", stats['total_messages'])
        st.metric("日语消息", stats['japanese_messages'])
    with col_b:
        st.metric("语法纠正", stats['corrections'])
        st.metric("表扬次数", stats['praises'])

    # 会话时长
    duration = datetime.now() - stats['session_start']
    minutes = int(duration.total_seconds() // 60)
    st.metric("会话时长", f"{minutes}分钟")

    # 学习进度
    if stats['total_messages'] > 0:
        japanese_rate = stats['japanese_messages'] / stats['total_messages'] * 100
        st.subheader("📚 学习进度")
        st.write(f"日语使用率: {japanese_rate:.1f}%")
        st.progress(japanese_rate / 100)

    # 学习建议
    st.subheader("💡 学习建议")
    tips = [
        "🎯 多用日语练习问候语",
        "📚 尝试使用敬语表达",
        "🌸 练习描述天气和心情",
        "✨ 不要害怕犯错误",
        "🎌 学习日本文化背景"
    ]

    for tip in tips:
        st.write(f"- {tip}")

# 异步消息处理函数
async def process_message(message):
    """处理用户消息"""
    try:
        # 添加用户消息
        st.session_state.messages.append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now()
        })

        # 获取智能体响应
        agent = st.session_state.tanaka_agent
        response = await agent.process_message(message)

        # 添加智能体响应
        st.session_state.messages.append({
            'role': 'assistant',
            'content': response.content,
            'confidence': response.confidence,
            'metadata': response.metadata,
            'timestamp': datetime.now()
        })

        # 更新统计
        stats = st.session_state.stats
        stats['total_messages'] += 1

        # 检查是否包含日语
        if re.search(r'[ひらがなカタカナ漢字]', message):
            stats['japanese_messages'] += 1

        # 根据响应类型更新统计
        response_type = response.metadata.get('response_type', '')
        if response_type == 'correction':
            stats['corrections'] += 1
        elif response_type == 'praise':
            stats['praises'] += 1

        # 强制刷新页面显示
        st.rerun()  # 新版Streamlit使用st.rerun()替代st.experimental_rerun()

    except Exception as e:
        st.error(f"处理消息时出错: {e}")

# 底部信息
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px; margin-top: 2rem;">
    <p style="margin: 0; color: #666;">
        🎌 <strong>Japanese Learning Multi-Agent System v0.1.0</strong><br>
        田中先生专业语法指导 | 下一版本将推出小美智能体 ✨
    </p>
</div>
""", unsafe_allow_html=True)