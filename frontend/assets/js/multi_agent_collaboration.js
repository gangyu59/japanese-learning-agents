// frontend/assets/js/multi_agent_collaboration.js
/**
 * 多智能体协作前端功能
 * 支持真实的分歧检测和协作流程
 */

class MultiAgentCollaboration {
    constructor() {
        this.apiBase = '';
        this.activeAgents = new Set();
        this.collaborationMode = 'discussion';
        this.currentSession = null;
        this.isCollaborating = false;

        // 智能体配置
        this.agentConfigs = {
            'tanaka': { name: '田中先生', avatar: '👨‍🏫', role: '语法专家' },
            'koumi': { name: '小美', avatar: '👧', role: '对话伙伴' },
            'ai': { name: 'アイ', avatar: '🤖', role: '数据分析师' },
            'yamada': { name: '山田先生', avatar: '🎌', role: '文化专家' },
            'sato': { name: '佐藤教练', avatar: '🎯', role: '考试专家' },
            'membot': { name: 'MemBot', avatar: '🧠', role: '记忆管家' }
        };

        this.init();
    }

    init() {
        // 检查是否在协作页面
        if (!document.getElementById('multi-agent-controls')) {
            return;
        }

        this.setupEventListeners();
        this.updateUIState();
    }

    setupEventListeners() {
        // 智能体选择
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('agent-checkbox')) {
                this.handleAgentToggle(e.target);
            }
        });

        // 协作模式选择
        document.addEventListener('change', (e) => {
            if (e.target.name === 'collaboration-mode') {
                this.collaborationMode = e.target.value;
                this.updateModeDescription();
            }
        });

        // 发送按钮
        const sendBtn = document.getElementById('send-multi-agent');
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }

        // 回车发送
        const input = document.getElementById('multi-agent-input');
        if (input) {
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
    }

    handleAgentToggle(checkbox) {
        const agentId = checkbox.value;
        const option = checkbox.closest('.agent-option');

        if (checkbox.checked) {
            this.activeAgents.add(agentId);
            option.classList.add('selected');
        } else {
            this.activeAgents.delete(agentId);
            option.classList.remove('selected');
        }

        this.updateUIState();
    }

    updateUIState() {
        this.updateCollaborationStatus();
        this.updateActiveAgentsDisplay();
        this.updateInputState();
    }

    updateCollaborationStatus() {
        const statusEl = document.getElementById('collaboration-status');
        const selectedCount = this.activeAgents.size;

        if (selectedCount >= 2) {
            statusEl.textContent = `已选择${selectedCount}个智能体，准备协作！`;
            statusEl.classList.add('ready');
        } else {
            statusEl.textContent = '请选择至少2个智能体开始协作';
            statusEl.classList.remove('ready');
        }
    }

    updateActiveAgentsDisplay() {
        const displayEl = document.getElementById('active-agents-display');

        if (this.activeAgents.size > 0) {
            const badges = Array.from(this.activeAgents).map(agentId => {
                const config = this.agentConfigs[agentId];
                return `<span class="active-agent-badge">${config.avatar} ${config.name}</span>`;
            }).join('');

            displayEl.innerHTML = badges;
        } else {
            displayEl.innerHTML = '';
        }
    }

    updateInputState() {
        const inputElement = document.getElementById('multi-agent-input');
        const sendButton = document.getElementById('send-multi-agent');
        const canCollaborate = this.activeAgents.size >= 2 && !this.isCollaborating;

        if (inputElement) {
            inputElement.disabled = !canCollaborate;
        }

        if (sendButton) {
            sendButton.disabled = !canCollaborate;
            sendButton.textContent = this.isCollaborating ? '协作中...' : '发送';
        }

        // 隐藏或显示欢迎界面
        const welcomeScreen = document.querySelector('.welcome-screen');
        if (welcomeScreen) {
            welcomeScreen.style.display = canCollaborate ? 'none' : 'flex';
        }
    }

    updateModeDescription() {
        const descriptions = {
            'discussion': '智能体们将就您的问题进行自由讨论',
            'correction': '智能体们将协作纠正您的语法和用法问题',
            'creation': '智能体们将协作创作内容',
            'analysis': '智能体们将从多个角度深入分析问题'
        };

        const descEl = document.getElementById('mode-description');
        if (descEl) {
            descEl.textContent = descriptions[this.collaborationMode] || '';
        }
    }

    async sendMessage() {
        const input = document.getElementById('multi-agent-input');
        const message = input?.value?.trim();

        if (!message || this.activeAgents.size < 2 || this.isCollaborating) {
            return;
        }

        // 设置协作状态
        this.isCollaborating = true;
        this.updateInputState();

        // 显示用户消息
        this.displayUserMessage(message);
        input.value = '';

        // 显示协作开始提示
        this.showCollaborationStart();

        try {
            // 发送协作请求
            const result = await this.requestCollaboration(message);

            // 处理协作结果
            await this.displayCollaborationResult(result);

        } catch (error) {
            console.error('协作失败:', error);
            this.displayErrorMessage('协作过程中出现错误，请重试');
        } finally {
            this.isCollaborating = false;
            this.updateInputState();
        }
    }

    async requestCollaboration(message) {
        const requestData = {
            message: message,
            user_id: 'demo_user',
            session_id: this.currentSession || `session_${Date.now()}`,
            active_agents: Array.from(this.activeAgents),
            collaboration_mode: this.collaborationMode,
            scene_context: 'multi_agent_collaboration'
        };

            // 添加这行调试
        console.log('发送的数据:', JSON.stringify(requestData, null, 2));

       const response = await fetch('http://localhost:8000/api/v1/chat/multi-agent-collaboration', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });

       // 添加这行调试
        console.log('响应状态:', response.status, response.statusText);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || '协作请求失败');
        }

        return data;
    }

    showCollaborationStart() {
        const agentNames = Array.from(this.activeAgents).map(id =>
            this.agentConfigs[id].name
        ).join('、');

        this.addSystemMessage(`🤝 ${agentNames} 开始协作讨论...`);
    }

    async displayCollaborationResult(result) {
        // 1. 显示智能体响应
        if (result.responses && result.responses.length > 0) {
            await this.displayAgentResponses(result.responses);
        }

        // 2. 显示分歧（如果有）
        if (result.disagreements && result.disagreements.length > 0) {
            await this.displayDisagreements(result.disagreements);
        }

        // 3. 显示冲突（向后兼容）
        if (result.conflicts && result.conflicts.length > 0) {
            await this.displayConflicts(result.conflicts);
        }

        // 4. 显示共识或总结
        if (result.consensus) {
            this.addSystemMessage(`💡 协作共识: ${result.consensus}`, 'summary');
        }

        // 5. 显示最终建议
        if (result.final_recommendation) {
            this.addSystemMessage(`📋 最终建议: ${result.final_recommendation}`, 'recommendation');
        }

        // 6. 如果需要用户仲裁
        if (result.user_arbitration_needed) {
            this.showArbitrationInterface(result.disagreements);
        }
    }

    async displayAgentResponses(responses) {
        for (let i = 0; i < responses.length; i++) {
            await this.delay(600 * (i + 1)); // 错开显示时间
            this.displayAgentMessage(responses[i]);
        }
    }

    displayAgentMessage(response) {
        const config = this.agentConfigs[response.agent_id] || {};
        const avatar = config.avatar || '🤖';
        const name = response.agent_name || config.name || response.agent_id;

        const messageEl = this.addMessage('agent', '', `${avatar} ${name}`);
        const contentDiv = messageEl.querySelector('.message-text');

        // 主要内容
        contentDiv.innerHTML = this.formatContent(response.content);

        // 置信度显示
        if (response.confidence) {
            const confidenceSpan = document.createElement('span');
            confidenceSpan.className = 'confidence-indicator';
            confidenceSpan.textContent = ` (${Math.round(response.confidence * 100)}%)`;
            confidenceSpan.style.opacity = '0.7';
            confidenceSpan.style.fontSize = '0.9em';
            messageEl.querySelector('.message-author').appendChild(confidenceSpan);
        }

        // 学习要点
        if (response.learning_points && response.learning_points.length > 0) {
            const learningDiv = document.createElement('div');
            learningDiv.className = 'learning-points';
            learningDiv.innerHTML = `<strong>学习要点:</strong> ${response.learning_points.join(', ')}`;
            messageEl.querySelector('.message-content').appendChild(learningDiv);
        }

        // 建议
        if (response.suggestions && response.suggestions.length > 0) {
            const suggestionsDiv = document.createElement('div');
            suggestionsDiv.className = 'suggestions';
            suggestionsDiv.innerHTML = `<strong>建议:</strong> ${response.suggestions.join(', ')}`;
            messageEl.querySelector('.message-content').appendChild(suggestionsDiv);
        }

        return messageEl;
    }

    async displayDisagreements(disagreements) {
        await this.delay(1000);

        for (const disagreement of disagreements) {
            this.displayDisagreementMessage(disagreement);
            await this.delay(500);
        }
    }

    displayDisagreementMessage(disagreement) {
        const messageEl = this.addMessage('conflict', '', '⚠️ 发现观点分歧');
        const contentDiv = messageEl.querySelector('.message-text');

        let content = `关于 "${disagreement.topic}" 的分歧:\n\n`;

        // 显示各智能体的立场
        for (const [agent, position] of Object.entries(disagreement.positions)) {
            content += `• ${agent}: ${position}\n`;
        }

        content += `\n严重程度: ${disagreement.severity}`;

        contentDiv.innerHTML = this.formatContent(content);
    }

    async displayConflicts(conflicts) {
        await this.delay(800);

        const messageEl = this.addMessage('conflict', '', '⚖️ 智能体冲突');
        const contentDiv = messageEl.querySelector('.message-text');

        let content = '检测到以下冲突观点:\n\n';
        conflicts.forEach((conflict, index) => {
            content += `${index + 1}. ${conflict[0]} vs ${conflict[1]}: ${conflict[2]}\n`;
        });

        contentDiv.innerHTML = this.formatContent(content);
    }

    showArbitrationInterface(disagreements) {
        const messageEl = this.addMessage('system', '', '⚖️ 需要您的仲裁');
        const contentDiv = messageEl.querySelector('.message-content');

        disagreements.forEach((disagreement, index) => {
            const arbitrationDiv = document.createElement('div');
            arbitrationDiv.className = 'arbitration-section';
            arbitrationDiv.style.marginTop = '15px';
            arbitrationDiv.style.padding = '10px';
            arbitrationDiv.style.border = '1px solid #ddd';
            arbitrationDiv.style.borderRadius = '8px';

            const titleDiv = document.createElement('div');
            titleDiv.innerHTML = `<strong>分歧 ${index + 1}: ${disagreement.topic}</strong>`;
            arbitrationDiv.appendChild(titleDiv);

            const buttonsDiv = document.createElement('div');
            buttonsDiv.style.marginTop = '10px';

            // 为每个立场创建按钮
            Object.entries(disagreement.positions).forEach(([agent, position]) => {
                const button = document.createElement('button');
                button.className = 'btn btn-secondary';
                button.style.margin = '3px';
                button.textContent = `支持 ${agent} (${position})`;
                button.onclick = () => this.handleArbitration(disagreement, agent, position);
                buttonsDiv.appendChild(button);
            });

            arbitrationDiv.appendChild(buttonsDiv);
            contentDiv.appendChild(arbitrationDiv);
        });
    }

    handleArbitration(disagreement, chosenAgent, chosenPosition) {
        this.addSystemMessage(
            `✅ 您选择支持 ${chosenAgent} 的观点: ${chosenPosition}`,
            'arbitration-result'
        );

        // 禁用仲裁按钮
        const arbitrationSections = document.querySelectorAll('.arbitration-section');
        arbitrationSections.forEach(section => {
            const buttons = section.querySelectorAll('button');
            buttons.forEach(btn => btn.disabled = true);
        });
    }

    displayUserMessage(message) {
        this.addMessage('user', message, '您');
    }

    displayErrorMessage(error) {
        this.addMessage('error', error, '❌ 错误');
    }

    addMessage(type, content, author) {
        const messagesContainer = document.getElementById('messages-container');

        // 隐藏欢迎界面
        const welcomeScreen = messagesContainer.querySelector('.welcome-screen');
        if (welcomeScreen) {
            welcomeScreen.style.display = 'none';
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';

        if (author) {
            const authorSpan = document.createElement('span');
            authorSpan.className = 'message-author';
            authorSpan.textContent = author;
            messageContent.appendChild(authorSpan);
        }

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.innerHTML = this.formatContent(content);
        messageContent.appendChild(textDiv);

        // 添加时间戳
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = new Date().toLocaleTimeString();
        messageContent.appendChild(timeDiv);

        messageDiv.appendChild(messageContent);
        messagesContainer.appendChild(messageDiv);

        // 滚动到底部
        this.scrollToBottom();

        return messageDiv;
    }

    addSystemMessage(content, type = 'system') {
        return this.addMessage(type, content, null);
    }

    formatContent(content) {
        if (!content) return '';

        return this.escapeHtml(content)
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    scrollToBottom() {
        const container = document.getElementById('messages-container');
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    window.multiAgentCollaboration = new MultiAgentCollaboration();
    console.log('🤝 多智能体协作系统已初始化');
});

// 导出供其他脚本使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MultiAgentCollaboration;
}