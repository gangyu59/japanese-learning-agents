// 保存为: frontend/multi_agent_collaboration.js
/**
 * 多智能体协作前端功能
 * 基于你现有的前端结构
 */

class MultiAgentCollaboration {
    constructor() {
        this.apiBase = '';  // 相对路径，因为前端和后端在同一域
        this.activeAgents = new Set();
        this.collaborationMode = 'discussion';
        this.currentSession = null;

        // 智能体映射表
        this.agentMap = {
            'tanaka': '田中先生',
            'koumi': '小美',
            'ai': 'アイ',
            'yamada': '山田先生',
            'sato': '佐藤教练',
            'membot': 'MemBot'
        };

        this.init();
    }

    init() {
        // 检查是否在正确页面
        if (!document.getElementById('multi-agent-controls')) {
            return; // 不在协作页面，跳过初始化
        }

        this.setupEventListeners();
        this.loadAgentsList();
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

    async loadAgentsList() {
        try {
            const response = await fetch('/api/v1/agents/list');
            const agents = await response.json();
            this.renderAgentsSelection(agents);
        } catch (error) {
            console.error('加载智能体列表失败:', error);
        }
    }

    renderAgentsSelection(agents) {
        const container = document.getElementById('agents-selection');
        if (!container) return;

        const html = agents.map(agent => `
            <div class="agent-option">
                <label class="agent-label">
                    <input type="checkbox" class="agent-checkbox" value="${agent.id}">
                    <span class="agent-info">
                        <span class="agent-avatar">${agent.avatar}</span>
                        <span class="agent-name">${agent.name}</span>
                        <span class="agent-role">${agent.role}</span>
                    </span>
                </label>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    handleAgentToggle(checkbox) {
        const agentId = checkbox.value;

        if (checkbox.checked) {
            this.activeAgents.add(agentId);
        } else {
            this.activeAgents.delete(agentId);
        }

        this.updateCollaborationStatus();
    }

    updateCollaborationStatus() {
        const statusEl = document.getElementById('collaboration-status');
        const sendBtn = document.getElementById('send-multi-agent');

        if (this.activeAgents.size < 2) {
            if (statusEl) statusEl.textContent = '请选择至少2个智能体进行协作';
            if (sendBtn) sendBtn.disabled = true;
        } else {
            if (statusEl) statusEl.textContent = `已选择${this.activeAgents.size}个智能体，准备协作`;
            if (sendBtn) sendBtn.disabled = false;
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

        if (!message || this.activeAgents.size < 2) return;

        const requestData = {
            message: message,
            user_id: 'demo_user',
            session_id: this.currentSession || 'session_' + Date.now(),
            active_agents: Array.from(this.activeAgents),
            collaboration_mode: this.collaborationMode,
            scene_context: 'multi_agent_collaboration'
        };

        // 显示用户消息
        this.displayUserMessage(message);
        if (input) input.value = '';

        // 显示加载状态
        this.showThinkingIndicator();

        try {
            const response = await fetch('/api/v1/collaboration/multi-agent-chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            const data = await response.json();

            if (data.success) {
                // 显示智能体回复
                this.displayAgentResponses(data.responses);

                // 显示冲突（如果有）
                if (data.conflicts && data.conflicts.length > 0) {
                    this.displayConflicts(data.conflicts);
                }

                // 显示总结
                if (data.final_recommendation) {
                    this.displaySummary(data.final_recommendation);
                }
            } else {
                this.displayError('协作请求失败，请重试');
            }

        } catch (error) {
            console.error('协作请求失败:', error);
            this.displayError('网络请求失败，请检查连接');
        } finally {
            this.hideThinkingIndicator();
        }
    }

    displayUserMessage(message) {
        const container = document.getElementById('messages-container');
        if (!container) return;

        const messageEl = document.createElement('div');
        messageEl.className = 'message user-message';
        messageEl.innerHTML = `
            <div class="message-content">
                <span class="message-author">您</span>
                <div class="message-text">${this.escapeHtml(message)}</div>
                <div class="message-time">${new Date().toLocaleTimeString()}</div>
            </div>
        `;

        container.appendChild(messageEl);
        this.scrollToBottom();
    }

    displayAgentResponses(responses) {
        const container = document.getElementById('messages-container');
        if (!container) return;

        responses.forEach((response, index) => {
            // 添加延迟以模拟真实对话
            setTimeout(() => {
                const messageEl = document.createElement('div');
                messageEl.className = 'message agent-message';
                messageEl.innerHTML = `
                    <div class="message-content">
                        <span class="message-author">
                            ${response.emotion || '🤖'} ${response.agent_name}
                            ${response.confidence ? `(${Math.round(response.confidence * 100)}%)` : ''}
                        </span>
                        <div class="message-text">${this.formatContent(response.content)}</div>
                        ${response.learning_points?.length ? 
                            `<div class="learning-points">
                                <strong>学习要点:</strong> ${response.learning_points.join(', ')}
                             </div>` : ''
                        }
                        ${response.suggestions?.length ?
                            `<div class="suggestions">
                                <strong>建议:</strong> ${response.suggestions.join(', ')}
                             </div>` : ''
                        }
                        <div class="message-time">${new Date().toLocaleTimeString()}</div>
                    </div>
                `;

                container.appendChild(messageEl);
                this.scrollToBottom();
            }, index * 800); // 每个智能体间隔800ms
        });
    }

    displayConflicts(conflicts) {
        const container = document.getElementById('messages-container');
        if (!container) return;

        setTimeout(() => {
            const conflictEl = document.createElement('div');
            conflictEl.className = 'message conflict-message';
            conflictEl.innerHTML = `
                <div class="message-content conflict">
                    <span class="message-author">⚖️ 观点分歧</span>
                    <div class="message-text">
                        智能体们对此问题有不同看法：
                        ${conflicts.map(c => `
                            <div class="conflict-item">
                                <strong>${this.agentMap[c.agent1] || c.agent1}</strong> vs 
                                <strong>${this.agentMap[c.agent2] || c.agent2}</strong>: 
                                ${c.conflict_point}
                            </div>
                        `).join('')}
                    </div>
                    <div class="message-time">${new Date().toLocaleTimeString()}</div>
                </div>
            `;

            container.appendChild(conflictEl);
            this.scrollToBottom();
        }, conflicts.length * 1000); // 在所有智能体回复后显示
    }

    displaySummary(summary) {
        const container = document.getElementById('messages-container');
        if (!container) return;

        setTimeout(() => {
            const summaryEl = document.createElement('div');
            summaryEl.className = 'message summary-message';
            summaryEl.innerHTML = `
                <div class="message-content summary">
                    <span class="message-author">💡 协作总结</span>
                    <div class="message-text">${this.formatContent(summary)}</div>
                    <div class="message-time">${new Date().toLocaleTimeString()}</div>
                </div>
            `;

            container.appendChild(summaryEl);
            this.scrollToBottom();
        }, 2000);
    }

    displayError(error) {
        const container = document.getElementById('messages-container');
        if (!container) return;

        const errorEl = document.createElement('div');
        errorEl.className = 'message error-message';
        errorEl.innerHTML = `
            <div class="message-content error">
                <span class="message-author">❌ 错误</span>
                <div class="message-text">${this.escapeHtml(error)}</div>
                <div class="message-time">${new Date().toLocaleTimeString()}</div>
            </div>
        `;

        container.appendChild(errorEl);
        this.scrollToBottom();
    }

    showThinkingIndicator() {
        const container = document.getElementById('messages-container');
        if (!container) return;

        const thinkingEl = document.createElement('div');
        thinkingEl.id = 'thinking-indicator';
        thinkingEl.className = 'message thinking-message';
        thinkingEl.innerHTML = `
            <div class="message-content thinking">
                <span class="message-author">🤔 智能体们正在思考...</span>
                <div class="thinking-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;

        container.appendChild(thinkingEl);
        this.scrollToBottom();
    }

    hideThinkingIndicator() {
        const thinkingEl = document.getElementById('thinking-indicator');
        if (thinkingEl) {
            thinkingEl.remove();
        }
    }

    formatContent(content) {
        return this.escapeHtml(content)
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
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
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    window.multiAgentCollaboration = new MultiAgentCollaboration();
});

// 导出供其他脚本使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MultiAgentCollaboration;
}