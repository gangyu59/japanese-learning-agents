"""
日语学习Multi-Agent系统 - Web界面
运行方式: streamlit run web_app.py
"""

import streamlit as st
import asyncio
from datetime import datetime
import re
import time
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

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
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 20px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

.chat-container {
    max-height: 500px;
    overflow-y: auto;
    padding: 1rem;
    border: 2px solid #f0f0f0;
    border-radius: 15px;
    margin-bottom: 1rem;
    background: #fafafa;
}

.user-message {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 20px 20px 5px 20px;
    margin: 1rem 0;
    margin-left: 15%;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.agent-message {
    background: linear-gradient(135deg, #fff3e0 0%, #ffcc80 100%);
    color: #333;
    padding: 1rem 1.5rem;
    border-radius: 20px 20px 20px 5px;
    margin: 1rem 0;
    margin-right: 15%;
    border-left: 5px solid #ff9800;
    box-shadow: 0 4px 15px rgba(255, 152, 0, 0.2);
}

.agent-info-card {
    background: white;
    padding: 1.5rem;
    border-radius: 15px;
    border: 2px solid #e3f2fd;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    margin: 1rem 0;
}

.quick-button {
    background: linear-gradient(45deg, #667eea, #764ba2) !important;
    color: white !important;
    border: none !important;
    border-radius: 25px !important;
    padding: 0.5rem 1rem !important;
    margin: 0.25rem !important;
    transition: all 0.3s ease !important;
}

.metric-container {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    margin: 0.5rem 0;
    text-align: center;
}

.welcome-card {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    padding: 2rem;
    border-radius: 20px;
    text-align: center;
    margin: 2rem 0;
    border: 2px solid #2196f3;
}
</style>
""", unsafe_allow_html=True)


# 简化的田中先生智能体类
class TanakaAgent:
    def __init__(self):
        self.name = "田中先生"
        self.personality = {
            'strictness': 8,
            'patience': 6,
            'formality': 9,
            'humor': 3,
            'expertise': '日语语法'
        }
        self.conversation_history = []

    def _check_japanese(self, text):
        """检查是否包含日语字符"""
        return bool(re.search(r'[ひらがなカタカナ一-龯]', text))

    def _analyze_grammar(self, text):
        """分析语法问题"""
        issues = []

        # 检查是否为日语
        if not self._check_japanese(text):
            issues.append({
                'type': 'language',
                'message': '日本語で書いてください。',
                'suggestion': 'ひらがな、カタカナ、漢字を使って書いてみましょう。'
            })

        # 检查过于随意的表达
        casual_patterns = [r'だよね', r'じゃん', r'っしょ', r'やばい']
        for pattern in casual_patterns:
            if re.search(pattern, text):
                issues.append({
                    'type': 'formality',
                    'message': f'「{re.search(pattern, text).group()}」はカジュアルすぎます。',
                    'suggestion': 'もう少し丁寧な表現を使いましょう。'
                })

        return issues

    async def process_message(self, message):
        """处理消息并生成响应"""
        start_time = time.time()

        # 分析语法
        grammar_issues = self._analyze_grammar(message)

        # 生成响应
        if grammar_issues:
            # 有语法问题，给出纠正建议
            response_parts = []

            if self.personality['strictness'] > 7:
                response_parts.append("注意深く確認しましたが、いくつかの問題があります。")
            else:
                response_parts.append("良い試みですね。改善できる点があります。")

            for i, issue in enumerate(grammar_issues, 1):
                response_parts.append(f"{i}. {issue['message']}")
                response_parts.append(f"   💡 {issue['suggestion']}")

            response_parts.append("\n頑張って練習を続けましょう！✨")
            response_content = "\n".join(response_parts)
            response_type = 'correction'
            confidence = 0.9
        else:
            # 没有问题，给出表扬
            if self._check_japanese(message):
                response_content = f"素晴らしい文章ですね！「{message}」という表現は正確で自然です。この調子で頑張ってください！🌸"
            else:
                response_content = f"正しい文法です。「{message}」は適切な表現です。次はより複雑な文にチャレンジしてみましょう。📚"

            response_type = 'praise'
            confidence = 0.8

        processing_time = time.time() - start_time

        # 添加到对话历史
        self.conversation_history.append({
            'user': message,
            'assistant': response_content,
            'timestamp': datetime.now()
        })

        return {
            'content': response_content,
            'confidence': confidence,
            'response_type': response_type,
            'processing_time': processing_time,
            'grammar_issues_found': len(grammar_issues)
        }


# 初始化会话状态
def init_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if 'tanaka_agent' not in st.session_state:
        st.session_state.tanaka_agent = TanakaAgent()

    if 'stats' not in st.session_state:
        st.session_state.stats = {
            'total_messages': 0,
            'japanese_messages': 0,
            'corrections': 0,
            'praises': 0,
            'session_start': datetime.now()
        }


# 处理用户消息
async def handle_user_message(message):
    """处理用户消息"""
    # 添加用户消息
    st.session_state.messages.append({
        'role': 'user',
        'content': message,
        'timestamp': datetime.now()
    })

    # 获取田中先生的响应
    response = await st.session_state.tanaka_agent.process_message(message)

    # 添加助手响应
    st.session_state.messages.append({
        'role': 'assistant',
        'content': response['content'],
        'confidence': response['confidence'],
        'response_type': response['response_type'],
        'processing_time': response['processing_time'],
        'grammar_issues': response['grammar_issues_found']
    })

    # 更新统计数据
    stats = st.session_state.stats
    stats['total_messages'] += 1

    if re.search(r'[ひらがなカタカナ一-龯]', message):
        stats['japanese_messages'] += 1

    if response['response_type'] == 'correction':
        stats['corrections'] += 1
    elif response['response_type'] == 'praise':
        stats['praises'] += 1


def main():
    """主应用程序"""
    # 初始化会话状态
    init_session_state()

    # 主标题
    st.markdown("""
    <div class="main-header">
        <h1>🎌 日语学习Multi-Agent系统</h1>
        <h2>田中先生的专业语法课堂</h2>
        <p>Professional Japanese Grammar Classroom with Tanaka-sensei</p>
    </div>
    """, unsafe_allow_html=True)

    # 主要布局
    col1, col2 = st.columns([2.5, 1.5])

    with col1:
        # 对话区域
        st.markdown("## 💬 实时对话")

        # 消息显示容器
        chat_container = st.container()
        with chat_container:
            if not st.session_state.messages:
                st.markdown("""
                <div class="welcome-card">
                    <h3>🌸 欢迎来到田中先生的日语课堂！</h3>
                    <p>田中先生是一位经验丰富的日语语法老师</p>
                    <p><strong>建议开始语句：</strong></p>
                    <p>• こんにちは（你好）</p>
                    <p>• 今日は良い天気ですね（今天天气真好）</p>
                    <p>• よろしくお願いします（请多关照）</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                # 显示对话历史
                for message in st.session_state.messages:
                    if message['role'] == 'user':
                        st.markdown(f"""
                        <div class="user-message">
                            <strong>👤 您:</strong> {message['content']}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        confidence = message.get('confidence', 0.8)
                        response_type = message.get('response_type', 'unknown')
                        processing_time = message.get('processing_time', 0)
                        grammar_issues = message.get('grammar_issues', 0)

                        st.markdown(f"""
                        <div class="agent-message">
                            <strong>👨‍🏫 田中先生:</strong><br><br>
                            {message['content']}<br><br>
                            <small style="opacity: 0.8; font-size: 0.85em;">
                                📊 置信度: {confidence:.1%} | 
                                🏷️ 类型: {response_type} | 
                                ⏱️ 处理时间: {processing_time:.2f}s |
                                📝 语法问题: {grammar_issues}个
                            </small>
                        </div>
                        """, unsafe_allow_html=True)

        # 快速输入按钮
        st.markdown("### 🚀 快速开始对话")
        quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)

        quick_messages = [
            ("こんにちは", "问候"),
            ("今日は良い天気ですね", "天气"),
            ("ありがとうございます", "感谢"),
            ("Hello world", "英语测试")
        ]

        for i, (msg, desc) in enumerate(quick_messages):
            with [quick_col1, quick_col2, quick_col3, quick_col4][i]:
                if st.button(f"**{msg}**\n({desc})", key=f"quick_{i}", use_container_width=True):
                    with st.spinner("🤔 田中先生正在思考..."):
                        asyncio.run(handle_user_message(msg))
                        st.rerun()

        # 用户输入区域
        st.markdown("### ✏️ 自由输入对话")
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_area(
                "请输入您的消息（日语或英语）:",
                placeholder="例如：こんにちは、田中先生！お元気ですか？\n或者：Hello, how are you?",
                height=120,
                help="💡 田中先生会检查您的语法并给出专业建议"
            )

            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                submitted = st.form_submit_button(
                    "📤 发送给田中先生",
                    type="primary",
                    use_container_width=True
                )

            if submitted and user_input.strip():
                with st.spinner("🤔 田中先生正在仔细分析您的语法..."):
                    asyncio.run(handle_user_message(user_input.strip()))
                    st.rerun()

    with col2:
        # 田中先生信息面板
        st.markdown("## 👨‍🏫 田中先生档案")

        st.markdown("""
        <div class="agent-info-card">
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 4rem; margin-bottom: 0.5rem;">👨‍🏫</div>
                <h3 style="color: #333; margin: 0;">田中先生</h3>
                <p style="color: #666; font-style: italic;">Tanaka-sensei</p>
            </div>
            <hr style="margin: 1rem 0;">
            <p><strong>🎯 专业领域:</strong> 日语语法、敬语教学</p>
            <p><strong>🎭 性格特点:</strong> 严格认真、耐心负责</p>
            <p><strong>🏆 教学风格:</strong> 精确纠错、鼓励进步</p>
            <p><strong>📚 经验:</strong> 20年语法教学经验</p>
        </div>
        """, unsafe_allow_html=True)

        # 性格特征雷达图
        st.markdown("### 📊 性格特征分析")
        agent = st.session_state.tanaka_agent
        personality = agent.personality

        traits = [
            ("严谨程度", personality['strictness']),
            ("耐心度", personality['patience']),
            ("正式程度", personality['formality']),
            ("幽默感", personality['humor'])
        ]

        for trait_name, value in traits:
            st.markdown(f"**{trait_name}**")
            st.progress(value / 10, text=f"{value}/10")
            st.write("")

        # 对话统计
        st.markdown("### 📈 本次会话统计")
        stats = st.session_state.stats

        # 统计卡片
        metrics_col1, metrics_col2 = st.columns(2)
        with metrics_col1:
            st.metric("总对话数", stats['total_messages'])
            st.metric("语法纠正", stats['corrections'])

        with metrics_col2:
            st.metric("日语消息", stats['japanese_messages'])
            st.metric("获得表扬", stats['praises'])

        # 会话时长
        session_duration = datetime.now() - stats['session_start']
        minutes = int(session_duration.total_seconds() // 60)
        st.metric("会话时长", f"{minutes} 分钟")

        # 学习进度
        if stats['total_messages'] > 0:
            japanese_rate = (stats['japanese_messages'] / stats['total_messages']) * 100
            st.markdown("### 📚 日语使用率")
            st.progress(japanese_rate / 100, text=f"{japanese_rate:.1f}%")

            if japanese_rate > 70:
                st.success("🎉 优秀！日语使用率很高！")
            elif japanese_rate > 40:
                st.info("👍 不错！继续增加日语练习！")
            else:
                st.warning("💪 建议多用日语练习！")

        # 学习建议
        st.markdown("### 💡 个性化学习建议")

        tips = [
            "🎯 每日坚持日语问候练习",
            "📚 逐步学习敬语表达方式",
            "🌸 练习描述天气和季节",
            "✨ 不要害怕犯语法错误",
            "🎌 了解日本文化背景知识",
            "🗣️ 多练习日常对话场景"
        ]

        for tip in tips:
            st.write(f"• {tip}")

        # 下一步规划
        st.markdown("### 🚀 即将推出")
        st.info("""
        **小美智能体** 即将上线！🎉

        • 活泼可爱的对话风格
        • 现代日语和流行语教学  
        • 与田中先生形成完美互补
        • 多智能体协作学习模式
        """)

    # 页面底部
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 15px; margin-top: 2rem;">
        <p style="margin: 0; color: #555; font-size: 1.1em;">
            🎌 <strong>Japanese Learning Multi-Agent System v0.1.0</strong>
        </p>
        <p style="margin: 0.5rem 0 0 0; color: #777;">
            田中先生专业日语语法指导 | 让学习变得更加高效有趣 ✨
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()