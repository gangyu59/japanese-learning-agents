/**
 * 聊天模块
 * 路径: frontend/assets/js/chat.js
 * 功能: 处理消息发送、接收和显示
 */

class ChatManager {
    constructor() {
        this.chatHistory = [];
        this.isThinking = false;
        this.messageQueue = [];
        this.typingIndicators = new Map();

        this.init();
    }

    init() {
        this.bindEvents();
        this.loadChatHistory();
    }

    /**
     * 绑定聊天相关事件
     */
    bindEvents() {
        // Enter键发送消息
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            // 输入时显示正在输入状态
            messageInput.addEventListener('input', () => {
                this.handleTyping();
            });
        }

        // 发送按钮点击
        const sendBtn = document.querySelector('.send-btn');
        if (sendBtn) {
            sendBtn.addEventListener('click', () => {
                this.sendMessage();
            });
        }
    }

    /**
     * 发送消息
     */
    sendMessage() {
        const input = document.getElementById('messageInput');
        if (!input) return;

        const message = input.value.trim();
        if (!message) return;

        // 清空输入框
        input.value = '';

        // 添加用户消息到历史
        const userMessage = {
            id: this.generateMessageId(),
            sender: 'user',
            content: message,
            timestamp: new Date(),
            type: 'text'
        };

        this.addMessageToHistory(userMessage);
        this.displayMessage(userMessage);

        // 显示思考指示器
        this.showThinkingIndicator();

        // 处理消息
        this.processUserMessage(message);
    }

    /**
     * 处理用户消息
     */
    async processUserMessage(message) {
        try {
            // 获取当前活跃的智能体
            const activeAgents = Array.from(window.currentAgents || ['tanaka']);

            // 为每个智能体生成回应
            const responses = await this.generateAgentResponses(message, activeAgents);

            // 显示智能体回应
            this.displayAgentResponses(responses);

        } catch (error) {
            console.error('处理消息失败:', error);
            this.showErrorMessage('消息处理失败，请重试');
        } finally {
            this.hideThinkingIndicator();
        }
    }

    /**
     * 生成智能体回应
     */
    async generateAgentResponses(userMessage, activeAgents) {
        const responses = [];

        for (const agentId of activeAgents) {
            try {
                let response;

                if (window.backendConnected) {
                    // 真实API调用
                    response = await this.callAgentAPI(agentId, userMessage);
                } else {
                    // 模拟响应
                    response = this.generateMockResponse(agentId, userMessage);
                }

                responses.push({
                    agentId,
                    response,
                    timestamp: new Date()
                });

            } catch (error) {
                console.error(`生成${agentId}回应失败:`, error);
                // 使用默认回应
                responses.push({
                    agentId,
                    response: this.getDefaultResponse(agentId),
                    timestamp: new Date(),
                    error: true
                });
            }
        }

        return responses;
    }

    /**
     * 调用智能体API
     */
    async callAgentAPI(agentId, userMessage) {
        const agent = window.agents[agentId];
        if (!agent) throw new Error(`未找到智能体: ${agentId}`);

        const requestBody = {
            message: userMessage,
            user_id: "demo_user",
            session_id: "session_" + Date.now(),
            agent_name: agent.name,
            scene_context: window.currentScene || "general"
        };

        const response = await fetch(`${window.API_BASE_URL}/api/v1/chat/send`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json"
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            throw new Error(`API调用失败: ${response.status}`);
        }

        const data = await response.json();
        return {
            content: data.response || "抱歉，我现在无法回答。",
            learning_points: data.learning_points || [],
            suggestions: data.suggestions || [],
            emotion: data.emotion || this.getRandomEmotion(agentId)
        };
    }

    /**
     * 生成模拟回应
     */
    generateMockResponse(agentId, userMessage) {
        const agent = window.agents[agentId];
        if (!agent) return this.getDefaultResponse(agentId);

        // 简单的关键词匹配回应
        const responses = this.getMockResponses(agentId, userMessage);
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];

        return {
            content: randomResponse + "\n\n*[模拟响应]*",
            learning_points: this.generateLearningPoints(userMessage),
            suggestions: this.generateSuggestions(agentId),
            emotion: this.getRandomEmotion(agentId)
        };
    }

    /**
     * 获取模拟回应内容
     */
    getMockResponses(agentId, userMessage) {
        const defaultResponses = {
            tanaka: [
                "この文法について詳しく説明しましょう。",
                "正しい表現を教えます。",
                "文法的には次のようになります。"
            ],
            koumi: [
                "わあ、面白い質問だね！",
                "それについて話そうよ！",
                "私も同じこと思ってた！"
            ],
            ai: [
                "データ分析結果をお示しします。",
                "学習パターンを分析しました。",
                "統計的に見ると..."
            ],
            yamada: [
                "日本の文化では...",
                "興味深い背景があります。",
                "伝統的には..."
            ],
            sato: [
                "試験対策として重要です！",
                "この問題をマスターしましょう！",
                "効率的な学習方法を教えます。"
            ],
            membot: [
                "学習記録を更新しました。",
                "復習スケジュールを調整します。",
                "進捗データを分析中..."
            ]
        };

        return defaultResponses[agentId] || ["ありがとうございます。"];
    }

    /**
     * 显示智能体回应
     */
    displayAgentResponses(responses) {
        responses.forEach((response, index) => {
            setTimeout(() => {
                this.displayAgentMessage(response);

                // 更新智能体情绪
                if (window.updateAgentEmotion) {
                    window.updateAgentEmotion(response.agentId);
                }

                // 显示学习点和建议
                this.showLearningFeedback(response.response);

            }, index * 800 + 500); // 错开显示时间
        });
    }

    /**
     * 显示智能体消息
     */
    displayAgentMessage(response) {
        const agent = window.agents[response.agentId];
        if (!agent) return;

        const message = {
            id: this.generateMessageId(),
            sender: response.agentId,
            content: response.response.content,
            timestamp: response.timestamp,
            type: 'text',
            agentName: agent.name,
            avatar: agent.avatar,
            emotion: response.response.emotion
        };

        this.addMessageToHistory(message);
        this.displayMessage(message);
    }

    /**
     * 显示消息
     */
    displayMessage(message) {
        const messagesContainer = document.getElementById('chatMessages');
        if (!messagesContainer) return;

        const messageElement = this.createMessageElement(message);
        messagesContainer.appendChild(messageElement);

        // 滚动到底部
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // 添加动画效果
        messageElement.classList.add('bounce');
    }

    /**
     * 创建消息元素
     */
    createMessageElement(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message' + (message.sender === 'user' ? ' user' : '');
        messageDiv.dataset.messageId = message.id;

        let avatarContent, senderName, avatarStyle;

        if (message.sender === 'user') {
            avatarContent = '👤';
            senderName = '你';
            avatarStyle = 'background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);';
        } else {
            const agent = window.agents[message.sender];
            avatarContent = agent ? agent.avatar : '🤖';
            senderName = message.agentName || (agent ? agent.name : '智能体');
            avatarStyle = this.getAgentAvatarStyle(message.sender);
        }

        messageDiv.innerHTML = `
            <div class="message-avatar" style="${avatarStyle}">${avatarContent}</div>
            <div class="message-content">
                <div class="message-meta">
                    <strong>${senderName}</strong>
                    <span>${this.formatTime(message.timestamp)}</span>
                    ${message.emotion ? `<span class="message-emotion">${message.emotion}</span>` : ''}
                </div>
                <div class="message-text">${this.formatMessageContent(message.content)}</div>
                ${this.createMessageActions(message)}
            </div>
        `;

        return messageDiv;
    }

    /**
     * 格式化消息内容
     */
    formatMessageContent(content) {
        // 处理换行
        content = content.replace(/\n/g, '<br>');

        // 处理日语和中文翻译
        if (content.includes('**中文翻译：**') || content.includes('**中文提示：**')) {
            content = content.replace(/\*\*(.*?)：\*\*/g, '<strong style="color: #666;">$1：</strong>');
        }

        // 处理模拟响应标记
        content = content.replace(/\*\[(.*?)\]\*/g, '<em style="color: #999; font-size: 0.9em;">[$1]</em>');

        return content;
    }

    /**
     * 创建消息操作按钮
     */
    createMessageActions(message) {
        if (message.sender === 'user') return '';

        return `
            <div class="message-actions" style="margin-top: 8px; display: flex; gap: 8px;">
                <button class="action-btn-small" onclick="chatManager.speakMessage('${message.id}')" title="朗读">
                    <i class="fas fa-volume-up"></i>
                </button>
                <button class="action-btn-small" onclick="chatManager.copyMessage('${message.id}')" title="复制">
                    <i class="fas fa-copy"></i>
                </button>
                <button class="action-btn-small" onclick="chatManager.translateMessage('${message.id}')" title="翻译">
                    <i class="fas fa-language"></i>
                </button>
            </div>
        `;
    }

    /**
     * 朗读消息
     */
    speakMessage(messageId) {
        const message = this.chatHistory.find(m => m.id === messageId);
        if (!message || !window.voiceManager) return;

        // 提取日语内容（去除中文翻译部分）
        let textToSpeak = message.content;
        if (textToSpeak.includes('**中文')) {
            textToSpeak = textToSpeak.split('**中文')[0].trim();
        }

        // 去除HTML标签
        textToSpeak = textToSpeak.replace(/<[^>]*>/g, '');

        window.voiceManager.speakText(textToSpeak, 'ja-JP');
    }

    /**
     * 复制消息
     */
    copyMessage(messageId) {
        const message = this.chatHistory.find(m => m.id === messageId);
        if (!message) return;

        const textToCopy = message.content.replace(/<[^>]*>/g, '');

        navigator.clipboard.writeText(textToCopy).then(() => {
            if (window.showNotification) {
                window.showNotification('消息已复制到剪贴板', 'success');
            }
        }).catch(err => {
            console.error('复制失败:', err);
        });
    }

    /**
     * 翻译消息
     */
    translateMessage(messageId) {
        // 这里可以集成翻译API
        if (window.showNotification) {
            window.showNotification('翻译功能开发中...', 'info');
        }
    }

    /**
     * 获取智能体头像样式
     */
    getAgentAvatarStyle(agentId) {
        const styles = {
            tanaka: 'background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);',
            koumi: 'background: linear-gradient(135deg, #ed64a6 0%, #d53f8c 100%);',
            ai: 'background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);',
            yamada: 'background: linear-gradient(135deg, #38a169 0%, #2f855a 100%);',
            sato: 'background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);',
            membot: 'background: linear-gradient(135deg, #805ad5 0%, #6b46c1 100%);'
        };
        return styles[agentId] || styles.ai;
    }

    /**
     * 格式化时间
     */
    formatTime(timestamp) {
        const now = new Date();
        const diff = now - timestamp;

        if (diff < 60000) {
            return '刚刚';
        } else if (diff < 3600000) {
            return Math.floor(diff / 60000) + '分钟前';
        } else if (diff < 86400000) {
            return Math.floor(diff / 3600000) + '小时前';
        } else {
            return timestamp.toLocaleDateString();
        }
    }

    /**
     * 显示思考指示器
     */
    showThinkingIndicator() {
        const indicator = document.getElementById('thinkingIndicator');
        if (indicator) {
            indicator.classList.add('active');
            this.isThinking = true;
        }
    }

    /**
     * 隐藏思考指示器
     */
    hideThinkingIndicator() {
        const indicator = document.getElementById('thinkingIndicator');
        if (indicator) {
            indicator.classList.remove('active');
            this.isThinking = false;
        }
    }

    /**
     * 显示错误消息
     */
    showErrorMessage(error) {
        const errorMessage = {
            id: this.generateMessageId(),
            sender: 'system',
            content: `<span style="color: #e53e3e;"><i class="fas fa-exclamation-triangle"></i> ${error}</span>`,
            timestamp: new Date(),
            type: 'error'
        };

        this.displayMessage(errorMessage);
    }

    /**
     * 显示学习反馈
     */
    showLearningFeedback(response) {
        if (response.learning_points && response.learning_points.length > 0) {
            setTimeout(() => {
                if (window.showNotification) {
                    window.showNotification(`学习点: ${response.learning_points.join(", ")}`, "info");
                }
            }, 500);
        }

        if (response.suggestions && response.suggestions.length > 0) {
            setTimeout(() => {
                if (window.showNotification) {
                    window.showNotification(`建议: ${response.suggestions.join(", ")}`, "success");
                }
            }, 1000);
        }
    }

    /**
     * 处理输入状态
     */
    handleTyping() {
        // 这里可以实现输入状态的显示
        // 比如显示"正在输入..."的提示
    }

    /**
     * 添加消息到历史
     */
    addMessageToHistory(message) {
        this.chatHistory.push(message);

        // 限制历史记录长度
        if (this.chatHistory.length > 100) {
            this.chatHistory = this.chatHistory.slice(-100);
        }

        // 保存到本地存储
        this.saveChatHistory();
    }

    /**
     * 保存聊天历史
     */
    saveChatHistory() {
        try {
            const historyToSave = this.chatHistory.map(msg => ({
                ...msg,
                timestamp: msg.timestamp.toISOString()
            }));
            localStorage.setItem('japanese_learning_chat_history', JSON.stringify(historyToSave));
        } catch (error) {
            console.error('保存聊天历史失败:', error);
        }
    }

    /**
     * 加载聊天历史
     */
    loadChatHistory() {
        try {
            const saved = localStorage.getItem('japanese_learning_chat_history');
            if (saved) {
                const history = JSON.parse(saved);
                this.chatHistory = history.map(msg => ({
                    ...msg,
                    timestamp: new Date(msg.timestamp)
                }));

                // 重新显示最近的几条消息
                this.displayRecentMessages();
            }
        } catch (error) {
            console.error('加载聊天历史失败:', error);
        }
    }

    /**
     * 显示最近消息
     */
    displayRecentMessages() {
        const recentMessages = this.chatHistory.slice(-5); // 最近5条
        const messagesContainer = document.getElementById('chatMessages');
        if (!messagesContainer) return;

        // 清空现有消息（除了欢迎消息）
        const welcomeMessages = messagesContainer.querySelectorAll('.message:not([data-message-id])');
        messagesContainer.innerHTML = '';
        welcomeMessages.forEach(msg => messagesContainer.appendChild(msg));

        // 显示历史消息
        recentMessages.forEach(message => {
            this.displayMessage(message);
        });
    }

    /**
     * 清空聊天历史
     */
    clearChatHistory() {
        this.chatHistory = [];
        localStorage.removeItem('japanese_learning_chat_history');

        const messagesContainer = document.getElementById('chatMessages');
        if (messagesContainer) {
            messagesContainer.innerHTML = '';
        }

        if (window.showNotification) {
            window.showNotification('聊天记录已清空', 'info');
        }
    }

    /**
     * 生成消息ID
     */
    generateMessageId() {
        return 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * 获取随机情绪
     */
    getRandomEmotion(agentId) {
        const agent = window.agents[agentId];
        if (!agent || !agent.emotions) return '😊';

        return agent.emotions[Math.floor(Math.random() * agent.emotions.length)];
    }

    /**
     * 生成学习点
     */
    generateLearningPoints(userMessage) {
        const points = [];

        // 简单的日语检测和学习点生成
        if (/[\u3040-\u309F]/.test(userMessage)) {
            points.push('平假名使用');
        }
        if (/[\u30A0-\u30FF]/.test(userMessage)) {
            points.push('片假名使用');
        }
        if (/[\u4E00-\u9FAF]/.test(userMessage)) {
            points.push('汉字使用');
        }

        return points;
    }

    /**
     * 生成建议
     */
    generateSuggestions(agentId) {
        const suggestions = {
            tanaka: ['注意语法结构', '练习敬语形式'],
            koumi: ['试试更自然的表达', '学习年轻人用语'],
            ai: ['分析语言模式', '制定学习计划'],
            yamada: ['了解文化背景', '学习传统表达'],
            sato: ['准备考试重点', '提高答题技巧'],
            membot: ['定期复习', '记录学习进度']
        };

        return suggestions[agentId] || ['继续练习'];
    }

    /**
     * 获取默认回应
     */
    getDefaultResponse(agentId) {
        const defaultResponses = {
            tanaka: "申し訳ございません。もう一度お聞かせください。",
            koumi: "ごめんね、よく分からなかった。もう一回言ってくれる？",
            ai: "データ処理中にエラーが発生しました。再試行してください。",
            yamada: "すみません、少し考えさせてください。",
            sato: "もう一度挑戦しましょう！",
            membot: "システムエラーが発生しました。記録を確認中です。"
        };

        return {
            content: defaultResponses[agentId] || "申し訳ございません。",
            learning_points: [],
            suggestions: [],
            emotion: '😅'
        };
    }

    /**
     * 导出聊天记录
     */
    exportChatHistory() {
        const exportData = {
            timestamp: new Date().toISOString(),
            messages: this.chatHistory,
            totalMessages: this.chatHistory.length
        };

        const blob = new Blob([JSON.stringify(exportData, null, 2)],
            { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `chat_history_${new Date().toLocaleDateString()}.json`;
        a.click();

        URL.revokeObjectURL(url);

        if (window.showNotification) {
            window.showNotification('聊天记录已导出', 'success');
        }
    }
}

// 创建全局聊天管理器实例
window.chatManager = new ChatManager();

// 导出函数供其他模块使用
window.sendMessage = () => window.chatManager.sendMessage();
window.clearChatHistory = () => window.chatManager.clearChatHistory();
window.exportChatHistory = () => window.chatManager.exportChatHistory();