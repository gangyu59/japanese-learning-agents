// 配置常量
const API_BASE_URL = 'http://localhost:8000';

// 智能体配置
const agents = {
    tanaka: {
        name: '田中先生',
        role: '语法专家',
        avatar: '👨‍🏫',
        personality: { strict: 8, patient: 6, humor: 3 },
        expertise: ['grammar', 'formal_language'],
        speaking_style: 'formal',
        emotions: ['😐', '🤔', '😤', '😊', '👍']
    },
    koumi: {
        name: '小美',
        role: '对话伙伴',
        avatar: '👧',
        personality: { strict: 2, patient: 9, humor: 8 },
        expertise: ['conversation', 'casual_language', 'youth_culture'],
        speaking_style: 'casual',
        emotions: ['😊', '😄', '😍', '🤗', '😉']
    },
    ai: {
        name: 'アイ',
        role: '分析师',
        avatar: '🤖',
        personality: { strict: 5, patient: 7, humor: 4 },
        expertise: ['analysis', 'personalization', 'data'],
        speaking_style: 'professional',
        emotions: ['🤔', '💡', '📊', '🔍', '⚡']
    },
    yamada: {
        name: '山田先生',
        role: '文化专家',
        avatar: '🎌',
        personality: { strict: 4, patient: 8, humor: 7 },
        expertise: ['culture', 'history', 'traditions'],
        speaking_style: 'storytelling',
        emotions: ['😌', '🎎', '⛩️', '🍃', '📿']
    },
    sato: {
        name: '佐藤教练',
        role: '考试专家',
        avatar: '🎯',
        personality: { strict: 9, patient: 5, humor: 2 },
        expertise: ['jlpt', 'testing', 'strategy'],
        speaking_style: 'motivational',
        emotions: ['😤', '💪', '🏆', '⚡', '🔥']
    },
    membot: {
        name: '记忆管家',
        role: '学习记录',
        avatar: '🧠',
        personality: { strict: 6, patient: 10, humor: 5 },
        expertise: ['memory', 'progress', 'scheduling'],
        speaking_style: 'systematic',
        emotions: ['🧠', '📚', '⏰', '💾', '📈']
    }
};

// 全局状态
let currentAgents = new Set();
let sessionId = 'session_' + Date.now();
let isProcessing = false;
let vocabularyList = [];
let panelStates = {
    agents: true,
    vocabulary: true
};

// 日语生词检测和处理
const japaneseVocabulary = {
    // 基础词汇数据库
    commonWords: {
        'こんにちは': { romaji: 'konnichiwa', meaning: '你好' },
        'ありがとう': { romaji: 'arigatou', meaning: '谢谢' },
        'すみません': { romaji: 'sumimasen', meaning: '对不起/不好意思' },
        'はじめまして': { romaji: 'hajimemashite', meaning: '初次见面' },
        'よろしく': { romaji: 'yoroshiku', meaning: '请多关照' },
        'おはよう': { romaji: 'ohayou', meaning: '早上好' },
        'こんばんは': { romaji: 'konbanwa', meaning: '晚上好' },
        'さようなら': { romaji: 'sayounara', meaning: '再见' },
        '日本語': { romaji: 'nihongo', meaning: '日语' },
        '勉強': { romaji: 'benkyou', meaning: '学习' },
        '先生': { romaji: 'sensei', meaning: '老师' },
        '学生': { romaji: 'gakusei', meaning: '学生' },
        '友達': { romaji: 'tomodachi', meaning: '朋友' },
        '家族': { romaji: 'kazoku', meaning: '家人' },
        '仕事': { romaji: 'shigoto', meaning: '工作' },
        '会社': { romaji: 'kaisha', meaning: '公司' },
        '学校': { romaji: 'gakkou', meaning: '学校' },
        '時間': { romaji: 'jikan', meaning: '时间' },
        '今日': { romaji: 'kyou', meaning: '今天' },
        '明日': { romaji: 'ashita', meaning: '明天' },
        '昨日': { romaji: 'kinou', meaning: '昨天' },
        '今': { romaji: 'ima', meaning: '现在' },
        '食べる': { romaji: 'taberu', meaning: '吃' },
        '飲む': { romaji: 'nomu', meaning: '喝' },
        '見る': { romaji: 'miru', meaning: '看' },
        '聞く': { romaji: 'kiku', meaning: '听' },
        '話す': { romaji: 'hanasu', meaning: '说话' },
        '読む': { romaji: 'yomu', meaning: '读' },
        '書く': { romaji: 'kaku', meaning: '写' },
        '行く': { romaji: 'iku', meaning: '去' },
        '来る': { romaji: 'kuru', meaning: '来' },
        '帰る': { romaji: 'kaeru', meaning: '回去' },
        '美しい': { romaji: 'utsukushii', meaning: '美丽的' },
        '大きい': { romaji: 'ookii', meaning: '大的' },
        '小さい': { romaji: 'chiisai', meaning: '小的' },
        '新しい': { romaji: 'atarashii', meaning: '新的' },
        '古い': { romaji: 'furui', meaning: '旧的' },
        '良い': { romaji: 'yoi/ii', meaning: '好的' },
        '悪い': { romaji: 'warui', meaning: '坏的' },
        '高い': { romaji: 'takai', meaning: '高的/贵的' },
        '安い': { romaji: 'yasui', meaning: '便宜的' },
        '忙しい': { romaji: 'isogashii', meaning: '忙的' }
    },

    // 检测文本中的日语词汇
    extractVocabulary(text, source = '对话') {
        const foundWords = [];
        const japaneseRegex = /[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+/g;
        const matches = text.match(japaneseRegex);

        if (matches) {
            matches.forEach(word => {
                // 去重和过滤单个假名
                if (word.length > 1 && this.commonWords[word]) {
                    const vocabData = this.commonWords[word];
                    foundWords.push({
                        word: word,
                        romaji: vocabData.romaji,
                        meaning: vocabData.meaning,
                        source: source,
                        timestamp: Date.now()
                    });
                }
            });
        }

        return foundWords;
    }
};

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    loadVocabularyFromStorage();
});

function initializeEventListeners() {
    // 输入框回车键监听
    document.getElementById('messageInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // 发送按钮点击监听
    document.getElementById('sendButton').addEventListener('click', sendMessage);

    // 智能体卡片点击监听
    const agentCards = {
        'card-tanaka': 'tanaka',
        'card-koumi': 'koumi',
        'card-ai': 'ai',
        'card-yamada': 'yamada',
        'card-sato': 'sato',
        'card-membot': 'membot'
    };

    Object.keys(agentCards).forEach(cardId => {
        const card = document.getElementById(cardId);
        if (card) {
            card.addEventListener('click', () => selectAgent(agentCards[cardId]));
        }
    });

    // 面板折叠按钮监听
    const agentsHeader = document.querySelector('#agentsPanel .panel-header');
    const vocabularyHeader = document.querySelector('#vocabularyPanel .panel-header');

    if (agentsHeader) {
        agentsHeader.addEventListener('click', () => togglePanel('agents'));
    }

    if (vocabularyHeader) {
        vocabularyHeader.addEventListener('click', () => togglePanel('vocabulary'));
    }

    // 清空生词本按钮监听
    const clearBtn = document.querySelector('.clear-vocab-btn');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearVocabulary);
    }

    // 页面关闭前保存生词本
    window.addEventListener('beforeunload', saveVocabularyToStorage);
}

// 面板折叠/展开功能
function togglePanel(panelType) {
    const panel = document.getElementById(`${panelType}Panel`);
    const content = document.getElementById(`${panelType}Content`);
    const btn = document.getElementById(`${panelType}CollapseBtn`);
    const mainContent = document.getElementById('mainContent');

    panelStates[panelType] = !panelStates[panelType];

    if (panelStates[panelType]) {
        panel.classList.remove('collapsed');
        btn.innerHTML = '<span>▼</span>';
    } else {
        panel.classList.add('collapsed');
        btn.innerHTML = '<span>◀</span>';
    }

    // 检查是否所有面板都收缩
    const allCollapsed = !panelStates.agents && !panelStates.vocabulary;
    if (allCollapsed) {
        mainContent.classList.add('sidebar-collapsed');
    } else {
        mainContent.classList.remove('sidebar-collapsed');
    }
}

// 智能体选择功能
function selectAgent(agentId) {
    const card = document.getElementById(`card-${agentId}`);

    if (currentAgents.has(agentId)) {
        currentAgents.delete(agentId);
        card.classList.remove('active');
        showNotification(`${agents[agentId].name} 已停用`);
    } else {
        currentAgents.add(agentId);
        card.classList.add('active');
        showNotification(`${agents[agentId].name} 已激活`);
        addAgentMessage(agentId, `こんにちは！${agents[agentId].name}です。よろしくお願いします！`, [], [], getRandomEmotion(agentId));
    }
}

// 发送消息主函数
async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();

    if (!message || isProcessing) return;

    if (currentAgents.size === 0) {
        showNotification('请先选择至少一个智能体老师！');
        return;
    }

    addMessage(message, 'user');
    input.value = '';
    setProcessing(true);

    try {
        await processMessageWithAPI(message);
    } catch (error) {
        console.error('消息处理错误:', error);
        addSystemMessage('抱歉，系统出现错误，请稍后重试。');
    } finally {
        setProcessing(false);
    }
}

// API消息处理
async function processMessageWithAPI(userMessage) {
    const activeAgentsList = Array.from(currentAgents);

    for (const [idx, agentId] of activeAgentsList.entries()) {
        try {
            if (idx > 0) {
                await new Promise(resolve => setTimeout(resolve, 1500));
            }

            const requestBody = {
                message: String(userMessage),
                user_id: 'demo_user',
                session_id: sessionId,
                agent_name: agentId,
                scene_context: 'general'
            };

            console.log(`发送给 ${agents[agentId].name}:`, requestBody);

            const response = await fetch(`${API_BASE_URL}/api/v1/chat/send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json; charset=utf-8',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(requestBody)
            });

            if (response.ok) {
                const data = await response.json();
                console.log(`${agents[agentId].name} 响应:`, data);

                if (data.success && data.response) {
                    const emotion = data.emotion || getRandomEmotion(agentId);
                    updateAgentEmotion(agentId, emotion);
                    addAgentMessage(agentId, data.response, data.learning_points || [], data.suggestions || [], emotion);

                    // 从智能体回复中提取生词
                    extractVocabularyFromResponse(data.response, agents[agentId].name);
                } else {
                    addAgentMessage(agentId, data.response || '抱歉，我无法理解您的问题。', [], [], '😅');
                }
            } else {
                console.error(`API请求失败 (${agents[agentId].name}):`, response.status);
                addAgentMessage(agentId, '抱歉，我现在无法回答，请稍后再试。', [], [], '😵');
            }
        } catch (error) {
            console.error(`请求 ${agents[agentId].name} 时出错:`, error);
            addAgentMessage(agentId, '连接出现问题，请检查网络连接。', [], [], '😵');
        }
    }
}

// 消息显示功能
function addMessage(content, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.textContent = content;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();

    // 从用户消息中提取生词
    if (sender === 'user') {
        extractVocabularyFromResponse(content, '用户输入');
    }
}

function addAgentMessage(agentId, content, learningPoints, suggestions, emotion) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message agent-message';

    let html = `
        <div class="agent-header">
            <div class="agent-avatar-small ${agentId}">${getAgentAvatar(agentId)}</div>
            <span>${agents[agentId].name}：</span>
            <span class="agent-emotion">${emotion}</span>
        </div>
        <div>${content}</div>
    `;

    if (learningPoints && learningPoints.length > 0) {
        html += `<div class="learning-points"><strong>📚 学习点：</strong> ${learningPoints.join(' • ')}</div>`;
    }

    if (suggestions && suggestions.length > 0) {
        html += `<div class="suggestions"><strong>💡 建议：</strong> ${suggestions.join(' • ')}</div>`;
    }

    messageDiv.innerHTML = html;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function addSystemMessage(content) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message agent-message';
    messageDiv.innerHTML = `
        <div class="agent-header">
            <span style="color: #666;">🔔 系统：</span>
        </div>
        <div>${content}</div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// 生词处理功能
function extractVocabularyFromResponse(text, source) {
    const newWords = japaneseVocabulary.extractVocabulary(text, source);

    newWords.forEach(wordData => {
        // 检查是否已存在
        const exists = vocabularyList.some(existing => existing.word === wordData.word);
        if (!exists) {
            vocabularyList.push(wordData);
            addVocabularyToUI(wordData);
        }
    });

    saveVocabularyToStorage();
}

function addVocabularyToUI(wordData) {
    const vocabularyListEl = document.getElementById('vocabularyList');

    // 移除空状态提示
    const emptyMsg = vocabularyListEl.querySelector('.empty-vocab');
    if (emptyMsg) {
        emptyMsg.remove();
    }

    const vocabItem = document.createElement('div');
    vocabItem.className = 'vocabulary-item';
    vocabItem.innerHTML = `
        <div class="vocab-word">${wordData.word}</div>
        <div class="vocab-romaji">${wordData.romaji}</div>
        <div class="vocab-meaning">${wordData.meaning}</div>
        <div class="vocab-source">来源: ${wordData.source}</div>
    `;

    // 插入到列表顶部
    vocabularyListEl.insertBefore(vocabItem, vocabularyListEl.firstChild);

    // 限制显示数量，避免过多
    const items = vocabularyListEl.querySelectorAll('.vocabulary-item');
    if (items.length > 50) {
        items[items.length - 1].remove();
        vocabularyList = vocabularyList.slice(0, 50);
    }
}

function clearVocabulary() {
    if (vocabularyList.length === 0) {
        showNotification('生词本已经是空的了');
        return;
    }

    if (confirm('确定要清空生词本吗？')) {
        vocabularyList = [];
        const vocabularyListEl = document.getElementById('vocabularyList');
        vocabularyListEl.innerHTML = '<div class="empty-vocab">📝 生词会在对话中自动收集</div>';
        saveVocabularyToStorage();
        showNotification('生词本已清空');
    }
}

function renderVocabularyList() {
    const vocabularyListEl = document.getElementById('vocabularyList');
    vocabularyListEl.innerHTML = '';

    if (vocabularyList.length === 0) {
        vocabularyListEl.innerHTML = '<div class="empty-vocab">📝 生词会在对话中自动收集</div>';
        return;
    }

    vocabularyList.forEach(wordData => {
        const vocabItem = document.createElement('div');
        vocabItem.className = 'vocabulary-item';
        vocabItem.innerHTML = `
            <div class="vocab-word">${wordData.word}</div>
            <div class="vocab-romaji">${wordData.romaji}</div>
            <div class="vocab-meaning">${wordData.meaning}</div>
            <div class="vocab-source">来源: ${wordData.source}</div>
        `;
        vocabularyListEl.appendChild(vocabItem);
    });
}

// 本地存储功能
function saveVocabularyToStorage() {
    try {
        localStorage.setItem('vocabularyList', JSON.stringify(vocabularyList));
        localStorage.setItem('panelStates', JSON.stringify(panelStates));
    } catch (error) {
        console.warn('保存生词本失败:', error);
    }
}

function loadVocabularyFromStorage() {
    try {
        const saved = localStorage.getItem('vocabularyList');
        if (saved) {
            vocabularyList = JSON.parse(saved);
            renderVocabularyList();
        }

        const savedPanels = localStorage.getItem('panelStates');
        if (savedPanels) {
            const savedStates = JSON.parse(savedPanels);
            panelStates = { ...panelStates, ...savedStates };

            // 恢复面板状态 - 需要在DOM加载完成后执行
            setTimeout(() => {
                Object.keys(panelStates).forEach(panelType => {
                    const panel = document.getElementById(`${panelType}Panel`);
                    const btn = document.getElementById(`${panelType}CollapseBtn`);

                    if (panel && btn) {
                        if (!panelStates[panelType]) {
                            // 如果保存的状态是折叠的，应用折叠样式
                            panel.classList.add('collapsed');
                            btn.innerHTML = '<span>◀</span>';
                        } else {
                            // 展开状态
                            panel.classList.remove('collapsed');
                            btn.innerHTML = '<span>▼</span>';
                        }
                    }
                });

                // 检查主内容区域状态
                const allCollapsed = !panelStates.agents && !panelStates.vocabulary;
                const mainContent = document.getElementById('mainContent');
                if (allCollapsed) {
                    mainContent.classList.add('sidebar-collapsed');
                } else {
                    mainContent.classList.remove('sidebar-collapsed');
                }
            }, 100);
        }
    } catch (error) {
        console.warn('加载生词本失败:', error);
    }
}

// 辅助功能
function getAgentAvatar(agentId) {
    const avatars = {
        'tanaka': '田', 'koumi': '美', 'ai': 'AI',
        'yamada': '山', 'sato': '佐', 'membot': 'M'
    };
    return avatars[agentId] || '?';
}

function updateAgentEmotion(agentId, emotion) {
    const emotionElement = document.getElementById(`emotion-${agentId}`);
    if (emotionElement) {
        emotionElement.textContent = emotion;
    }
}

function getRandomEmotion(agentId) {
    const emotions = agents[agentId].emotions;
    return emotions[Math.floor(Math.random() * emotions.length)];
}

function setProcessing(processing) {
    isProcessing = processing;
    const sendButton = document.getElementById('sendButton');
    const input = document.getElementById('messageInput');

    if (processing) {
        sendButton.innerHTML = '<div class="loading"></div>';
        sendButton.disabled = true;
        input.disabled = true;
    } else {
        sendButton.innerHTML = '发送';
        sendButton.disabled = false;
        input.disabled = false;
    }
}

function showNotification(message) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: #667eea;
        color: white;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
        max-width: 300px;
        word-wrap: break-word;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 导出主要功能供全局使用
window.selectAgent = selectAgent;
window.sendMessage = sendMessage;
window.togglePanel = togglePanel;
window.clearVocabulary = clearVocabulary;