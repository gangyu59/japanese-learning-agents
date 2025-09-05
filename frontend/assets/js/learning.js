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

// ===== 词典层：可导入过万词 =====
const VOCAB_DICT_KEY = 'vocabDictionary';
let vocabDictionary = {};     // { [word]: {romaji, meaning, level?, tags?} }
let extractFromUser = false;  // 是否也从用户消息抽词（默认 false）

// —— 词索引缓存（来自 vocabDictionary + commonWords） ——
let vocabSet = new Set();
let maxWordLen = 1;

function rebuildVocabIndex() {
    const keys = [
        ...Object.keys(vocabDictionary || {}),
        ...Object.keys(japaneseVocabulary?.commonWords || {})
    ];
    vocabSet = new Set(keys);
    maxWordLen = 1;
    for (const w of keys) if (w.length > maxWordLen) maxWordLen = w.length;
}

function loadVocabDictionary() {
    try {
        const raw = localStorage.getItem(VOCAB_DICT_KEY);
        if (raw) {
            vocabDictionary = JSON.parse(raw);
        } else {
            // 首次迁移：把现有 small 词表作为种子（只做一次）
            vocabDictionary = { ...(japaneseVocabulary?.commonWords || {}) };
            localStorage.setItem(VOCAB_DICT_KEY, JSON.stringify(vocabDictionary));
        }
    } catch (e) {
        console.warn('加载词典失败，使用空词典', e);
        vocabDictionary = {};
    }
    rebuildVocabIndex(); // 关键：加载后建立索引
}

function saveVocabDictionary() {
    try {
        localStorage.setItem(VOCAB_DICT_KEY, JSON.stringify(vocabDictionary));
    } catch (e) {
        console.warn('保存词典失败', e);
    }
}

// 简易 CSV / NDJSON 解析 + 批量导入
function parseCSV(text) {
    return text.split(/\r?\n/).map(line => line.trim()).filter(Boolean).map(line => {
        const parts = line.split(',').map(s => s.trim());
        const [word, romaji='', meaning='', level='', tags=''] = parts;
        return { word, romaji, meaning, level, tags };
    });
}
function parseNDJSON(text) {
    return text.split(/\r?\n/).map(line => line.trim()).filter(Boolean).map(line => JSON.parse(line));
}
function bulkImportVocabulary(text) {
    let rows = [];
    const trimmed = (text || '').trim();
    try {
        if (trimmed.startsWith('[') || (trimmed.startsWith('{') && trimmed.endsWith('}'))) {
            const obj = JSON.parse(trimmed);
            rows = Array.isArray(obj) ? obj : Object.keys(obj).map(k => ({ word: k, ...(obj[k] || {}) }));
        } else if (trimmed.includes('{')) {
            rows = parseNDJSON(trimmed);
        } else {
            rows = parseCSV(trimmed);
        }
    } catch (e) {
        showNotification('❌ 解析失败：请检查数据格式（JSON/CSV/NDJSON）');
        return { added: 0, updated: 0, total: Object.keys(vocabDictionary).length };
    }

    let added = 0, updated = 0;
    rows.forEach(r => {
        if (!r || !r.word) return;
        const w = String(r.word).trim();
        if (!/[\u3040-\u30FF\u3400-\u9FFF]/.test(w)) return; // 必须含日文
        const payload = {
            romaji: r.romaji || '',
            meaning: r.meaning || '',
            level: r.level || '',
            tags: r.tags || ''
        };
        if (vocabDictionary[w]) {
            const old = vocabDictionary[w];
            vocabDictionary[w] = {
                romaji: payload.romaji || old.romaji || '',
                meaning: payload.meaning || old.meaning || '',
                level: payload.level || old.level || '',
                tags: payload.tags || old.tags || ''
            };
            updated++;
        } else {
            vocabDictionary[w] = payload;
            added++;
        }
    });

    saveVocabDictionary();
    rebuildVocabIndex(); // 导入后重建索引
    return { added, updated, total: Object.keys(vocabDictionary).length };
}

function exportToCSV(rows, filename) {
    if (!rows || !rows.length) {
        showNotification('没有可导出的数据');
        return;
    }
    const headers = Object.keys(rows[0]);
    const csv = [headers.join(',')]
      .concat(rows.map(r => headers.map(h => (r[h] ?? '')).join(',')))
      .join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);
    showNotification(`已导出：${filename}`);
}

function dedupNotebook() {
    const seen = new Set();
    const deduped = [];
    for (const item of vocabularyList) {
        if (!seen.has(item.word)) {
            seen.add(item.word);
            deduped.push(item);
        }
    }
    vocabularyList = deduped;
    saveVocabularyToStorage();
    renderVocabularyList();
    showNotification('✅ 生词本已去重');
}

// ===== 日语生词检测和处理（简洁版：词典驱动 + 简易回退） =====
const japaneseVocabulary = {
    // 基础词汇数据库（保留你的原始常用词）
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
    dynamicWords: {},

    // 抽词（对外保持同名）：词典最长前缀匹配 + 简易回退
    extractVocabulary(text, source = '对话') {
        const tokens = segmentByDictSimple(text); // ↓ 下面实现
        const found = [];
        tokens.forEach(word => {
            const hit = vocabDictionary[word] || this.commonWords[word] || null;
            found.push({
                word,
                romaji: hit?.romaji || '',
                meaning: hit?.meaning || '（待补全）',
                source,
                timestamp: Date.now()
            });
            // 未在任何库中的词，记录到动态库（可后续补全释义）
            if (!hit && !this.dynamicWords[word]) {
                this.dynamicWords[word] = { romaji: '', meaning: '（待补全）' };
            }
        });
        return found;
    }
};

// —— 简单且稳的切词实现 —— //
function isJaChar(ch) {
    return /[\u3040-\u30FF\u3400-\u9FFF]/.test(ch); // 假名 + 常用汉字
}

// 将文本分成“连续的日文段”，对每一段做最长前缀匹配；
// 如果匹配不到：
//   - 段长 ≤ 4：整段作为一个词；
//   - 段长 > 4：按 2 字切块，避免把超长句当成一个词。
function segmentByDictSimple(text) {
    const s = String(text || '');
    const seqs = s.match(/[\u3040-\u30FF\u3400-\u9FFF]+/g) || [];
    const out = [];

    for (const seg of seqs) {
        let i = 0;
        while (i < seg.length) {
            // 非日文直接跳过（理论上 seg 已都是日文）
            if (!isJaChar(seg[i])) { i++; continue; }

            // 从长到短找“词典里存在的词”
            const limit = Math.min(maxWordLen, seg.length - i);
            let hit = null, len = 0;
            for (let L = limit; L >= 2; L--) {
                const cand = seg.substr(i, L);
                if (vocabSet.has(cand)) { hit = cand; len = L; break; }
            }

            if (hit) {
                out.push(hit);
                i += len;
                continue;
            }

            // 简易回退策略
            const remain = seg.length - i;
            if (remain <= 4) {
                if (remain >= 2) out.push(seg.substr(i, remain));
                i = seg.length;
            } else {
                out.push(seg.substr(i, 2));
                i += 2;
            }
        }
    }

    // 去重（保留首次出现次序）
    const seen = new Set();
    return out.filter(w => (w.length > 1) && (seen.has(w) ? false : (seen.add(w), true)));
}

// ================== 初始化 & 事件 ==================
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
        if (card) card.addEventListener('click', () => selectAgent(agentCards[cardId]));
    });

    // 面板折叠按钮监听
    const agentsHeader = document.querySelector('#agentsPanel .panel-header');
    const vocabularyHeader = document.querySelector('#vocabularyPanel .panel-header');
    if (agentsHeader) agentsHeader.addEventListener('click', () => togglePanel('agents'));
    if (vocabularyHeader) vocabularyHeader.addEventListener('click', () => togglePanel('vocabulary'));

    // 清空生词本按钮监听
    const clearBtn = document.querySelector('.clear-vocab-btn');
    if (clearBtn) clearBtn.addEventListener('click', clearVocabulary);

    // 页面关闭前保存生词本
    window.addEventListener('beforeunload', saveVocabularyToStorage);

    // —— 导入面板事件（加 pointer-events 兜底） ——
    document.getElementById('btnImportVocab')?.addEventListener('click', () => {
        const p = document.getElementById('importPanel');
        p.style.display = 'block';
        p.style.pointerEvents = 'auto';
        p.removeAttribute('aria-hidden');
    });
    document.getElementById('btnCloseImport')?.addEventListener('click', () => {
        const p = document.getElementById('importPanel');
        p.style.display = 'none';
        p.style.pointerEvents = 'none';
        p.setAttribute('aria-hidden', 'true');
    });
    document.getElementById('btnDoImport')?.addEventListener('click', () => {
        const text = document.getElementById('importText').value || '';
        const { added, updated, total } = bulkImportVocabulary(text);
        const p = document.getElementById('importPanel');
        p.style.display = 'none';
        p.style.pointerEvents = 'none';
        p.setAttribute('aria-hidden', 'true');
        showNotification(`✅ 导入完成：新增 ${added}，更新 ${updated}，总词数 ${total}`);
    });

    // 导出/去重/抽词开关
    document.getElementById('btnExportVocab')?.addEventListener('click', () => {
        const rows = Object.keys(vocabDictionary).map(w => ({
            word: w,
            romaji: vocabDictionary[w].romaji || '',
            meaning: vocabDictionary[w].meaning || '',
            level: vocabDictionary[w].level || '',
            tags: vocabDictionary[w].tags || ''
        }));
        exportToCSV(rows, 'vocab_dictionary.csv');
    });
    document.getElementById('btnExportNotebook')?.addEventListener('click', () => {
        const rows = vocabularyList.map(x => ({
            word: x.word, romaji: x.romaji || '', meaning: x.meaning || '',
            source: x.source || '', timestamp: x.timestamp || ''
        }));
        exportToCSV(rows, 'vocab_notebook.csv');
    });
    document.getElementById('btnDedup')?.addEventListener('click', dedupNotebook);

    const chk = document.getElementById('chkExtractFromUser');
    if (chk) {
        chk.checked = false;
        chk.addEventListener('change', () => {
            extractFromUser = chk.checked;
            showNotification(extractFromUser ? '✅ 已开启：从用户消息抽词' : '📴 已关闭：从用户消息抽词');
        });
    }

    // 首次加载词典（含索引）
    loadVocabDictionary();

    // —— 可选：首次自动导入一次内置CSV（若你在 assets/data/vocab 放了文件） ——
    (async function autoImportCsvOnce() {
        try {
            const FLAG = 'vocab_auto_import_done';
            if (localStorage.getItem(FLAG)) return;
            const res = await fetch('../assets/data/vocab/vocab_jlpt_n5_n4.csv', { cache: 'no-store' });
            if (!res.ok) return;
            const text = await res.text();
            if (typeof bulkImportVocabulary === 'function') {
                const { added, updated, total } = bulkImportVocabulary(text);
                showNotification(`📥 词表初始化导入：新增 ${added}，更新 ${updated}，总计 ${total}`);
                localStorage.setItem(FLAG, '1');
            }
        } catch(e) { console.warn('自动导入失败', e); }
    })();

    // 生词区点击兜底：提高折叠头部层级，防止被工具条/其它元素覆盖
    (function fixVocabHeaderZIndex() {
        const content = document.getElementById('vocabularyContent');
        if (!content) return;
        const header = content.previousElementSibling;
        if (header) {
            header.style.position = 'relative';
            header.style.zIndex = 1001; // 高于工具条
        }
        const toolbar = document.getElementById('vocabToolbar') || content.querySelector('[data-role="vocab-toolbar"]');
        if (toolbar) {
            toolbar.style.position = 'relative';
            toolbar.style.zIndex = 1;
        }
    })();
}

// 面板折叠/展开功能
function togglePanel(panelType) {
    const panel = document.getElementById(`${panelType}Panel`);
    const btn = document.getElementById(`${panelType}CollapseBtn`);
    const mainContent = document.getElementById('mainContent');

    panelStates[panelType] = !panelStates[panelType];

    if (panelStates[panelType]) {
        panel.classList.remove('collapsed');
        if (btn) btn.innerHTML = '<span>▼</span>';
    } else {
        panel.classList.add('collapsed');
        if (btn) btn.innerHTML = '<span>◀</span>';
    }

    // 检查是否所有面板都收缩
    const allCollapsed = !panelStates.agents && !panelStates.vocabulary;
    if (allCollapsed) {
        mainContent.classList.add('sidebar-collapsed');
    } else {
        mainContent.classList.remove('sidebar-collapsed');
    }

    // 保险：切换后保存状态
    saveVocabularyToStorage();
}

// 智能体选择功能
function selectAgent(agentId) {
    const card = document.getElementById(`card-${agentId}`);

    if (currentAgents.has(agentId)) {
        currentAgents.delete(agentId);
        card?.classList.remove('active');
        showNotification(`${agents[agentId].name} 已停用`);
    } else {
        currentAgents.add(agentId);
        card?.classList.add('active');
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

    // 可选：从用户消息抽词
    try {
        if (sender === 'user' && extractFromUser) {
            extractVocabularyFromResponse(content, '用户');
        }
    } catch (e) {
        console.warn('从用户消息抽词失败', e);
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
            <span class="agent-emotion" id="emotion-${agentId}">${emotion}</span>
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
    if (emptyMsg) emptyMsg.remove();

    const vocabItem = document.createElement('div');
    vocabItem.className = 'vocabulary-item';
    vocabItem.innerHTML = `
        <div class="vocab-word">${wordData.word}</div>
        <div class="vocab-romaji">${wordData.romaji || ''}</div>
        <div class="vocab-meaning">${wordData.meaning || ''}</div>
        <div class="vocab-source">来源: ${wordData.source || ''}</div>
    `;

    // 插入到列表顶部
    vocabularyListEl.insertBefore(vocabItem, vocabularyListEl.firstChild);

    // 仅限制 DOM 渲染数量，不动真实数据
    const items = vocabularyListEl.querySelectorAll('.vocabulary-item');
    if (items.length > 50) items[items.length - 1].remove();
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
    const el = document.getElementById('vocabularyList');
    el.innerHTML = '';

    if (!vocabularyList.length) {
        el.innerHTML = '<div class="empty-vocab">📝 生词会在对话中自动收集</div>';
        return;
    }

    const MAX_RENDER = 50; // 仅控制显示条数
    const slice = vocabularyList.slice(0, MAX_RENDER);
    slice.forEach(wordData => {
        const item = document.createElement('div');
        item.className = 'vocabulary-item';
        item.innerHTML = `
            <div class="vocab-word">${wordData.word}</div>
            <div class="vocab-romaji">${wordData.romaji || ''}</div>
            <div class="vocab-meaning">${wordData.meaning || ''}</div>
            <div class="vocab-source">来源: ${wordData.source || ''}</div>
        `;
        el.appendChild(item);
    });

    if (vocabularyList.length > MAX_RENDER) {
        const tip = document.createElement('div');
        tip.className = 'empty-vocab';
        tip.textContent = `已收集 ${vocabularyList.length} 条生词（仅显示前 ${MAX_RENDER} 条）`;
        el.appendChild(tip);
    }
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

            // 恢复面板状态（DOM ready 之后执行）
            setTimeout(() => {
                Object.keys(panelStates).forEach(panelType => {
                    const panel = document.getElementById(`${panelType}Panel`);
                    const btn = document.getElementById(`${panelType}CollapseBtn`);
                    if (panel && btn) {
                        if (!panelStates[panelType]) {
                            panel.classList.add('collapsed');
                            btn.innerHTML = '<span>◀</span>';
                        } else {
                            panel.classList.remove('collapsed');
                            btn.innerHTML = '<span>▼</span>';
                        }
                    }
                });

                const allCollapsed = !panelStates.agents && !panelStates.vocabulary;
                const mainContent = document.getElementById('mainContent');
                if (allCollapsed) mainContent.classList.add('sidebar-collapsed');
                else mainContent.classList.remove('sidebar-collapsed');
            }, 100);
        }
    } catch (error) {
        console.warn('加载生词本失败:', error);
    }
}

// 辅助功能
function getAgentAvatar(agentId) {
    const avatars = { 'tanaka': '田', 'koumi': '美', 'ai': 'AI', 'yamada': '山', 'sato': '佐', 'membot': 'M' };
    return avatars[agentId] || '?';
}

function updateAgentEmotion(agentId, emotion) {
    const el = document.getElementById(`emotion-${agentId}`);
    if (el) el.textContent = emotion;
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

// 一键强制展开（卡住时可在控制台调用）
window.forceOpenVocabulary = function () {
    const c = document.getElementById('vocabularyContent');
    if (!c) return;
    c.style.display = 'block';
    c.style.maxHeight = 'none';
    c.classList.remove('collapsed');
};

// 导出主要功能供全局使用
window.selectAgent = selectAgent;
window.sendMessage = sendMessage;
window.togglePanel = togglePanel;
window.clearVocabulary = clearVocabulary;
