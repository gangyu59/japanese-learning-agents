"""
日语学习Multi-Agent系统 - 双智能体Web界面
文件位置: multi_agent_app.py (项目根目录)
运行方式: python -m streamlit run multi_agent_app.py

田中先生 + 小美的完美组合
"""

import streamlit as st
import asyncio
import sys
from pathlib import Path
from datetime import datetime
import re
import time
import random

# 添加项目路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# 页面配置
st.set_page_config(
    page_title="🎌 日语学习Multi-Agent系统",
    page_icon="🎌",
    layout="wide"
)

# 导入智能体（简化版，避免复杂导入问题）
class SimpleTanakaAgent:
    """简化版田中先生 - 严格语法老师"""
    def __init__(self):
        self.name = "田中先生"
        self.personality = {'strictness': 8, 'patience': 6, 'formality': 9, 'humor': 3}

    def check_japanese(self, text):
        return bool(re.search(r'[ひらがなカタカナ一-龯]', text))

    async def process_message(self, message):
        start_time = time.time()

        if not self.check_japanese(message):
            response = "日本語で書いてください。ひらがな、カタカナ、漢字を使って正確に表現してみましょう。"
            return {
                'content': response,
                'confidence': 0.9,
                'response_type': 'correction',
                'processing_time': time.time() - start_time,
                'agent_style': 'formal'
            }
        else:
            response = f"素晴らしい文章ですね。「{message}」という表現は正確で自然です。この調子で頑張ってください。"
            return {
                'content': response,
                'confidence': 0.8,
                'response_type': 'praise',
                'processing_time': time.time() - start_time,
                'agent_style': 'formal'
            }

class SimpleKoumiAgent:
    """简化版小美 - 活泼对话伙伴"""
    def __init__(self):
        self.name = "小美"
        self.personality = {'energy_level': 9, 'casualness': 8, 'encouragement': 9, 'humor': 8}
        self.emojis = ["✨", "💫", "🌟", "😊", "😄", "🤗", "💪", "👍", "🎉", "🌸", "💕", "🥰"]
        self.expressions = ["そうなんだ〜！", "すごいじゃん！", "いいね〜！", "やったね！", "頑張って〜！", "わかる〜！"]

    def check_japanese(self, text):
        return bool(re.search(r'[ひらがなカタカナ一-龯]', text))

    async def process_message(self, message):
        start_time = time.time()

        if 'hello' in message.lower() or (not self.check_japanese(message) and 'こんにちは' not in message):
            responses = [
                "Oh, English! でも、せっかくだから日本語でも話してみない？😊",
                "English is cool〜 but let's try Japanese too! 日本語で言ってみて〜✨",
                "I understand English, でも日本語の練習をしよう〜！How do you say that in Japanese? 💪"
            ]
            response = random.choice(responses)
            response_type = 'language_redirect'
        elif 'こんにちは' in message or 'こんばんは' in message or 'おはよう' in message:
            responses = [
                "こんにちは〜！今日も元気だね〜✨",
                "やあ〜！会えて嬉しい😊 今日はどんな感じ？",
                "ハーイ〜！今日の気分はどう？😄",
                "おはよう〜！今日も日本語頑張ろうね💪"
            ]
            response = random.choice(responses)
            response_type = 'greeting'
        elif any(word in message for word in ['難しい', '分からない', '困る', '心配', 'だめ']):
            responses = [
                "わかるよ〜😌 でも大丈夫だよ〜！一緒に頑張ろう💪",
                "そっかあ...でも心配しないで〜！私がサポートするから🌟",
                "みんな最初はそうだよ〜！少しずつ上手になってるよ✨",
                "全然問題ないよ〜！楽しく学ぶのが一番だよ〜💕"
            ]
            response = random.choice(responses)
            response_type = 'encouragement'
        elif self.check_japanese(message):
            responses = [
                f"わあ〜！「{message}」って表現、めっちゃ自然だよ〜！素晴らしい🌟",
                f"すごいじゃん！「{message}」って言えるの、最高だよ〜😄",
                f"やったね〜！その「{message}」っていう言い方、完璧だよ〜✨",
                f"いいね〜！「{message}」って日本語、とっても上手だよ〜💕"
            ]
            response = random.choice(responses)
            response_type = 'praise'
        else:
            responses = [
                "そうなんだ〜！もっと聞かせて😊",
                "へえ〜面白いね！詳しく教えて〜✨",
                "なるほど〜！そういうことかあ💫",
                "わかる〜！私も似たような経験あるよ〜🌟"
            ]
            response = random.choice(responses)
            response_type = 'general'

        # 随机添加表情符号
        if not any(emoji in response for emoji in self.emojis):
            response += random.choice(self.emojis)

        return {
            'content': response,
            'confidence': 0.85,
            'response_type': response_type,
            'processing_time': time.time() - start_time,
            'agent_style': 'casual'
        }

# 样式定义
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 20px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.agent-selector {
    background: white;
    padding: 1.5rem;
    border-radius: 15px;
    border: 2px solid #e3f2fd;
    margin-bottom: 1rem;
    box-shadow: 0 5px 15px rgba(0,0,0,0.05);
}

.chat-container {
    max-height: 400px;
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

.tanaka-message {
    background: linear-gradient(135deg, #fff3e0 0%, #ffcc80 100%);
    color: #333;
    padding: 1rem 1.5rem;
    border-radius: 20px 20px 20px 5px;
    margin: 1rem 0;
    margin-right: 15%;
    border-left: 5px solid #ff9800;
    box-shadow: 0 4px 15px rgba(255, 152, 0, 0.2);
}

.koumi-message {
    background: linear-gradient(135deg, #fce4ec 0%, #f8bbd9 100%);
    color: #333;
    padding: 1rem 1.5rem;
    border-radius: 20px 20px 20px 5px;
    margin: 1rem 0;
    margin-right: 15%;
    border-left: 5px solid #e91e63;
    box-shadow: 0 4px 15px rgba(233, 30, 99, 0.2);
}

.agent-card {
    background: white;
    padding: 1.5rem;
    border-radius: 15px;
    border: 2px solid #f0f0f0;
    margin: 1rem 0;
    box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    transition: all 0.3s ease;
}

.agent-card:hover {
    border-color: #667eea;
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}

.collaboration-mode {
    background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
    padding: 1.5rem;
    border-radius: 15px;
    border: 2px solid #4caf50;
    margin: 1rem 0;
}

.welcome-card {
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    padding: 2rem;
    border-radius: 20px;
    text-align: center;
    margin: 2rem 0;
    border: 2px solid #2196f3;
}

.feature-highlight {
    background: linear-gradient(135deg, #fff9c4 0%, #fff176 100%);
    padding: 1rem;
    border-radius: 10px;
    border-left: 4px solid #ffc107;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
def init_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if 'tanaka_agent' not in st.session_state:
        st.session_state.tanaka_agent = SimpleTanakaAgent()

    if 'koumi_agent' not in st.session_state:
        st.session_state.koumi_agent = SimpleKoumiAgent()

    if 'selected_agent' not in st.session_state:
        st.session_state.selected_agent = 'tanaka'

    if 'collaboration_mode' not in st.session_state:
        st.session_state.collaboration_mode = False

    if 'stats' not in st.session_state:
        st.session_state.stats = {
            'total_messages': 0,
            'tanaka_responses': 0,
            'koumi_responses': 0,
            'japanese_messages': 0,
            'collaborations': 0,
            'session_start': datetime.now()
        }

# 处理消息
async def handle_message(message):
    """处理用户消息"""
    # 添加用户消息
    st.session_state.messages.append({
        'role': 'user',
        'content': message,
        'timestamp': datetime.now()
    })

    # 更新统计
    stats = st.session_state.stats
    stats['total_messages'] += 1
    if re.search(r'[ひらがなカタカナ一-龯]', message):
        stats['japanese_messages'] += 1

    # 选择智能体响应
    responses = []

    if st.session_state.collaboration_mode:
        # 协作模式：两个智能体都响应
        tanaka_response = await st.session_state.tanaka_agent.process_message(message)
        koumi_response = await st.session_state.koumi_agent.process_message(message)

        responses.append(('tanaka', tanaka_response))
        responses.append(('koumi', koumi_response))

        stats['tanaka_responses'] += 1
        stats['koumi_responses'] += 1
        stats['collaborations'] += 1
    else:
        # 单一智能体模式
        if st.session_state.selected_agent == 'tanaka':
            response = await st.session_state.tanaka_agent.process_message(message)
            responses.append(('tanaka', response))
            stats['tanaka_responses'] += 1
        else:
            response = await st.session_state.koumi_agent.process_message(message)
            responses.append(('koumi', response))
            stats['koumi_responses'] += 1

    # 添加智能体响应到消息列表
    for agent_name, response in responses:
        st.session_state.messages.append({
            'role': 'assistant',
            'agent': agent_name,
            'content': response['content'],
            'confidence': response['confidence'],
            'response_type': response['response_type'],
            'processing_time': response['processing_time'],
            'agent_style': response['agent_style']
        })

def display_messages():
    """显示聊天消息"""
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-card">
            <h3>🌸 欢迎来到多智能体日语学习系统！</h3>
            <div style="display: flex; justify-content: space-around; margin: 2rem 0;">
                <div style="text-align: center;">
                    <div style="font-size: 3rem; margin-bottom: 0.5rem;">👨‍🏫</div>
                    <h4>田中先生</h4>
                    <p>严格的语法专家<br>正式教学风格</p>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 3rem; margin-bottom: 0.5rem;">👧</div>
                    <h4>小美</h4>
                    <p>活泼的对话伙伴<br>现代日语专家</p>
                </div>
            </div>
            <div class="feature-highlight">
                <h4>🤝 协作模式特色</h4>
                <p>开启协作模式，让两位老师同时为您提供不同角度的指导！<br>
                体验严格正式 vs 轻松活泼的教学风格对比</p>
            </div>
            <p><strong>快速开始:</strong> 试试说 <code>こんにちは</code> 或 <code>Hello world</code></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for message in st.session_state.messages:
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="user-message">
                    <strong>👤 您:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                agent = message['agent']
                agent_name = "👨‍🏫 田中先生" if agent == 'tanaka' else "👧 小美"
                message_class = "tanaka-message" if agent == 'tanaka' else "koumi-message"

                confidence = message.get('confidence', 0.8)
                response_type = message.get('response_type', 'unknown')
                processing_time = message.get('processing_time', 0)

                st.markdown(f"""
                <div class="{message_class}">
                    <strong>{agent_name}:</strong><br><br>
                    {message['content']}<br><br>
                    <small style="opacity: 0.7;">
                        📊 置信度: {confidence:.1%} | 🏷️ 类型: {response_type} | ⏱️ {processing_time:.2f}s
                    </small>
                </div>
                """, unsafe_allow_html=True)

def main():
    """主应用程序"""
    init_session_state()

    # 主标题
    st.markdown("""
    <div class="main-header">
        <h1>🎌 日语学习Multi-Agent系统</h1>
        <h2>田中先生 ✕ 小美 = 完美学习组合</h2>
        <p>Professional Grammar Teacher × Cheerful Conversation Partner</p>
        <p style="margin-top: 1rem; opacity: 0.9;">v0.2.0 - 多智能体协作学习平台</p>
    </div>
    """, unsafe_allow_html=True)

    # 智能体选择器
    with st.container():
        st.markdown('<div class="agent-selector">', unsafe_allow_html=True)
        st.subheader("🤖 选择您的学习伙伴")

        col1, col2, col3 = st.columns(3)

        with col1:
            tanaka_type = "primary" if st.session_state.selected_agent == 'tanaka' and not st.session_state.collaboration_mode else "secondary"
            if st.button("👨‍🏫 田中先生\n(语法专家)", use_container_width=True, type=tanaka_type):
                st.session_state.selected_agent = 'tanaka'
                st.session_state.collaboration_mode = False
                st.success("已选择田中先生 - 专业语法指导")

        with col2:
            koumi_type = "primary" if st.session_state.selected_agent == 'koumi' and not st.session_state.collaboration_mode else "secondary"
            if st.button("👧 小美\n(对话伙伴)", use_container_width=True, type=koumi_type):
                st.session_state.selected_agent = 'koumi'
                st.session_state.collaboration_mode = False
                st.success("已选择小美 - 轻松愉快学习")

        with col3:
            collab_type = "primary" if st.session_state.collaboration_mode else "secondary"
            if st.button("🤝 协作模式\n(双重指导)", use_container_width=True, type=collab_type):
                st.session_state.collaboration_mode = not st.session_state.collaboration_mode
                if st.session_state.collaboration_mode:
                    st.success("协作模式已开启 - 双重智能体指导")
                else:
                    st.info("协作模式已关闭")

        st.markdown('</div>', unsafe_allow_html=True)

    # 显示当前模式
    if st.session_state.collaboration_mode:
        st.markdown("""
        <div class="collaboration-mode">
            <h4>🤝 协作模式已激活</h4>
            <p>田中先生和小美将同时为您提供指导，体验不同教学风格的完美结合！</p>
            <ul style="margin: 0.5rem 0;">
                <li>🎓 田中先生：严格的语法纠正和正式表达</li>
                <li>✨ 小美：鼓励式指导和现代日语表达</li>
                <li>🔄 对比学习：观察两种不同的教学方法</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        current_agent = "田中先生" if st.session_state.selected_agent == 'tanaka' else "小美"
        current_emoji = "👨‍🏫" if st.session_state.selected_agent == 'tanaka' else "👧"
        current_style = "严格正式风格" if st.session_state.selected_agent == 'tanaka' else "活泼亲切风格"
        st.info(f"{current_emoji} 当前选择: {current_agent} ({current_style})")

    # 主要布局
    col1, col2 = st.columns([2.5, 1.5])

    with col1:
        # 对话区域
        st.subheader("💬 智能体对话区域")

        # 消息显示容器
        display_messages()

        # 快速输入按钮
        st.subheader("🚀 快速开始对话")

        quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
        quick_messages = [
            ("こんにちは", "问候", "测试两种问候风格"),
            ("今日は良い天気ですね", "天气", "观察表扬方式差异"),
            ("日本語の勉強が難しいです", "求助", "体验鼓励方式对比"),
            ("Hello world", "英语", "对比纠错vs引导")
        ]

        for i, (msg, desc, tooltip) in enumerate(quick_messages):
            with [quick_col1, quick_col2, quick_col3, quick_col4][i]:
                if st.button(f"**{msg}**\n({desc})", key=f"quick_{i}",
                           use_container_width=True, help=tooltip):
                    with st.spinner("🤔 智能体正在思考..."):
                        asyncio.run(handle_message(msg))
                        st.rerun()

        # 用户输入
        st.subheader("✏️ 自由对话输入")
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_area(
                "请输入您的消息:",
                placeholder="例如：こんにちは、先生方！\n或者：日本語の文法について質問があります\n或者：推しのアニメについて話しましょう",
                height=100,
                help="💡 协作模式下，两位老师都会回应您，体验不同的教学风格！"
            )

            col_send1, col_send2, col_send3 = st.columns([1, 2, 1])
            with col_send2:
                submitted = st.form_submit_button("📤 发送消息", type="primary", use_container_width=True)

            if submitted and user_input.strip():
                with st.spinner("🤔 智能体正在分析并生成回应..."):
                    asyncio.run(handle_message(user_input.strip()))
                    st.rerun()

    with col2:
        # 智能体信息面板
        st.subheader("🤖 智能体档案中心")

        # 田中先生信息卡
        st.markdown("""
        <div class="agent-card">
            <div style="text-align: center;">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">👨‍🏫</div>
                <h3 style="color: #ff9800;">田中先生</h3>
                <p style="color: #ff9800; font-weight: bold; margin: 0;">専門語法教師</p>
            </div>
            <hr>
            <p><strong>🎯 核心专长:</strong> 日语语法、敬语、正式表达</p>
            <p><strong>🎭 教学风格:</strong> 严格认真、追求完美</p>
            <p><strong>📊 严谨程度:</strong> 8/10 ⭐⭐⭐⭐⭐⭐⭐⭐</p>
            <p><strong>💬 回应特色:</strong> 详细纠错、规范指导</p>
        </div>
        """, unsafe_allow_html=True)

        # 小美信息卡
        st.markdown("""
        <div class="agent-card">
            <div style="text-align: center;">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">👧</div>
                <h3 style="color: #e91e63;">小美</h3>
                <p style="color: #e91e63; font-weight: bold; margin: 0;">活発な会話パートナー</p>
            </div>
            <hr>
            <p><strong>🎯 核心专长:</strong> 现代日语、流行语、对话练习</p>
            <p><strong>🎭 教学风格:</strong> 活泼亲切、积极鼓励</p>
            <p><strong>⚡ 活力程度:</strong> 9/10 🌟🌟🌟🌟🌟🌟🌟🌟🌟</p>
            <p><strong>🎓 适合学员:</strong> 想要轻松学习现代日语的学习者</p>
            <p><strong>💬 回应特色:</strong> 情感支持、趣味引导</p>
        </div>
        """, unsafe_allow_html=True)

        # 智能体对比
        st.markdown("### ⚖️ 智能体特色对比")

        comparison_data = {
            "特征": ["教学严格度", "鼓励程度", "现代用语", "语法纠错", "情感支持"],
            "田中先生": ["⭐⭐⭐⭐⭐⭐⭐⭐", "⭐⭐⭐⭐⭐⭐", "⭐⭐", "⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐", "⭐⭐⭐⭐"],
            "小美": ["⭐⭐⭐", "⭐⭐⭐⭐⭐⭐⭐⭐⭐", "⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐", "⭐⭐⭐⭐⭐", "⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐"]
        }

        import pandas as pd
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # 对话统计
        st.subheader("📈 实时会话统计")
        stats = st.session_state.stats

        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("总对话数", stats['total_messages'], delta=None)
            st.metric("田中响应", stats['tanaka_responses'], delta=None)
        with col_b:
            st.metric("日语消息", stats['japanese_messages'], delta=None)
            st.metric("小美响应", stats['koumi_responses'], delta=None)

        st.metric("🤝 协作次数", stats['collaborations'], delta=None)

        # 会话时长和效率
        duration = datetime.now() - stats['session_start']
        minutes = int(duration.total_seconds() // 60)
        st.metric("会话时长", f"{minutes} 分钟")

        # 学习效果分析
        if stats['total_messages'] > 0:
            japanese_rate = stats['japanese_messages'] / stats['total_messages'] * 100
            collab_rate = stats['collaborations'] / stats['total_messages'] * 100 if stats['total_messages'] > 0 else 0

            st.subheader("📊 学习效果分析")

            st.write("**日语使用率:**")
            st.progress(japanese_rate / 100)
            st.write(f"{japanese_rate:.1f}% ({stats['japanese_messages']}/{stats['total_messages']})")

            st.write("**协作模式使用率:**")
            st.progress(collab_rate / 100)
            st.write(f"{collab_rate:.1f}%")

            # 智能建议
            st.subheader("🎯 个性化学习建议")

            if stats['collaborations'] > 0:
                st.success("🤝 您已体验协作模式！不同视角的指导很有价值")
            else:
                st.info("💡 建议尝试协作模式，获得双重智能体指导")

            if japanese_rate > 70:
                st.success("🎌 日语使用率很高！继续保持优秀表现")
            elif japanese_rate > 40:
                st.info("📈 日语使用率良好，可以继续提高")
            else:
                st.warning("💪 建议增加日语练习，多用日语交流")

            if stats['tanaka_responses'] > stats['koumi_responses'] * 2:
                st.info("👨‍🏫 您更偏爱田中先生的严格指导，也可以试试小美的轻松风格")
            elif stats['koumi_responses'] > stats['tanaka_responses'] * 2:
                st.info("👧 您更喜欢小美的活泼风格，也可以体验田中先生的专业指导")
            else:
                st.success("⚖️ 您很好地平衡了两种教学风格！")

        # 功能特色介绍
        st.subheader("✨ 系统特色功能")

        features = [
            "🎭 双智能体个性化对话",
            "🤝 实时协作模式切换",
            "📊 智能学习进度分析",
            "🎯 个性化学习建议",
            "💬 多样化回应风格体验",
            "📈 详细的使用统计数据"
        ]

        for feature in features:
            st.write(f"• {feature}")

        # 使用技巧
        st.subheader("💡 使用技巧")

        tips = [
            "🔄 **切换模式**: 比较不同智能体的回应风格",
            "🤝 **协作学习**: 开启协作模式获得双重指导",
            "🎯 **场景练习**: 用不同场景测试智能体反应",
            "📝 **错误学习**: 故意犯错观察纠错方式差异",
            "🌟 **风格适应**: 找到最适合自己的学习风格"
        ]

        for tip in tips:
            st.write(f"• {tip}")

    # 页面底部信息
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 15px; margin-top: 2rem;">
        <h3>🎌 Japanese Learning Multi-Agent System</h3>
        <p style="font-size: 1.2em; margin: 1rem 0;"><strong>v0.2.0 - 多智能体协作学习平台</strong></p>
        <div style="display: flex; justify-content: center; gap: 3rem; margin: 1.5rem 0;">
            <div>
                <div style="font-size: 2rem;">👨‍🏫</div>
                <p><strong>田中先生</strong><br>语法严谨性</p>
            </div>
            <div style="font-size: 2rem; align-self: center;">✕</div>
            <div>
                <div style="font-size: 2rem;">👧</div>
                <p><strong>小美</strong><br>现代亲和力</p>
            </div>
            <div style="font-size: 2rem; align-self: center;">=</div>
            <div>
                <div style="font-size: 2rem;">🎯</div>
                <p><strong>完美结合</strong><br>高效学习</p>
            </div>
        </div>
        <p style="color: #555; font-style: italic;">
            体验不同教学风格，找到最适合您的日语学习方式 ✨
        </p>
        <p style="margin-top: 1rem; color: #777; font-size: 0.9em;">
            🚀 即将推出：智能体间对话讨论、文化深度解析、创作协作模式
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()