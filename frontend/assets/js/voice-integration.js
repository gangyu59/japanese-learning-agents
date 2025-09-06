/**
 * 语音集成模块
 * 文件路径: frontend/assets/js/voice-integration.js
 * 功能: 整合语音功能到主界面
 */

// 等待页面完全加载后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeVoiceIntegration();
});

function initializeVoiceIntegration() {
    console.log('初始化语音集成...');

    // 创建全局语音管理器实例
    if (typeof VoiceInputManager !== 'undefined') {
        window.voiceManagerInstance = new VoiceInputManager();
        console.log('语音管理器初始化成功');
    } else {
        console.warn('VoiceInputManager 未找到');
    }

    // 添加必要的CSS样式
    addVoiceStyles();

    // 监听语音按钮点击事件（事件委托）
    document.addEventListener('click', handleVoiceButtonClick);

    // 修复现有消息的播放按钮
    setTimeout(fixExistingMessages, 1000);
}

/**
 * 添加语音相关样式
 */
function addVoiceStyles() {
    const existingStyle = document.getElementById('voice-integration-styles');
    if (existingStyle) return;

    const style = document.createElement('style');
    style.id = 'voice-integration-styles';
    style.textContent = `
        .message-actions {
            margin-top: 8px;
            display: flex;
            gap: 8px;
            opacity: 1;
            transition: opacity 0.3s ease;
        }

        .speaker-btn {
            width: 28px;
            height: 28px;
            border: none;
            border-radius: 50%;
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            transition: all 0.3s ease;
            position: relative;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .speaker-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 4px 12px rgba(72, 187, 120, 0.4);
        }

        .speaker-btn.playing {
            background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
            animation: speaker-pulse 1.5s ease-in-out infinite;
        }

        .speaker-btn.loading {
            background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
        }

        .speaker-btn.loading i {
            animation: spin 1s linear infinite;
        }

        @keyframes speaker-pulse {
            0%, 100% {
                box-shadow: 0 0 0 0 rgba(237, 137, 54, 0.7);
            }
            50% {
                box-shadow: 0 0 0 8px rgba(237, 137, 54, 0);
            }
        }

        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
    `;

    document.head.appendChild(style);
    console.log('语音样式已添加');
}

/**
 * 处理语音按钮点击事件
 */
function handleVoiceButtonClick(event) {
    const speakerBtn = event.target.closest('.speaker-btn');
    if (speakerBtn) {
        event.preventDefault();
        event.stopPropagation();

        const content = speakerBtn.getAttribute('data-content');
        if (content) {
            speakMessageContent(decodeURIComponent(content), speakerBtn);
        } else {
            console.error('播放按钮缺少内容数据');
            if (window.showNotification) {
                window.showNotification('播放内容缺失', 'error');
            }
        }
    }
}

/**
 * 播放消息内容
 */
function speakMessageContent(content, buttonElement) {
    console.log('开始播放:', content.substring(0, 50) + '...');

    // 如果正在播放，停止播放
    if (speechSynthesis.speaking) {
        speechSynthesis.cancel();
        resetAllSpeakerButtons();
        return;
    }

    // 重置所有按钮状态
    resetAllSpeakerButtons();

    // 设置当前按钮为加载状态
    buttonElement.classList.add('loading');
    buttonElement.innerHTML = '<i class="fas fa-cog fa-spin"></i>';

    try {
        // 清理内容 - 只保留日语部分
        const cleanContent = cleanTextForSpeech(content);

        if (!cleanContent.trim()) {
            if (window.showNotification) {
                window.showNotification('没有可播放的日语内容', 'warning');
            }
            resetSpeakerButton(buttonElement);
            return;
        }

        console.log('清理后的日语内容:', cleanContent);

        // 检测智能体类型
        const messageElement = buttonElement.closest('.message');
        console.log('消息元素:', messageElement);

        // 尝试多种方式获取发送者名称
        const senderElement1 = messageElement.querySelector('.sender-name');
        const senderElement2 = messageElement.querySelector('strong');
        const senderElement3 = messageElement.querySelector('.message-meta strong');

        console.log('方式1 (.sender-name):', senderElement1?.textContent);
        console.log('方式2 (strong):', senderElement2?.textContent);
        console.log('方式3 (.message-meta strong):', senderElement3?.textContent);

        // 也检查头像来确定智能体
        const avatarElement = messageElement.querySelector('.message-avatar');
        console.log('头像内容:', avatarElement?.textContent);

        let senderName = '';
        if (senderElement3) {
            senderName = senderElement3.textContent.trim();
        } else if (senderElement2) {
            senderName = senderElement2.textContent.trim();
        } else if (senderElement1) {
            senderName = senderElement1.textContent.trim();
        }

        // 如果还是找不到，通过头像判断
        if (!senderName && avatarElement) {
            const avatar = avatarElement.textContent.trim();
            switch(avatar) {
                case '👧': senderName = '小美'; break;
                case '👨‍🏫': senderName = '田中先生'; break;
                case '🤖': senderName = 'アイ'; break;
                case '🎌': senderName = '山田先生'; break;
                case '🎯': senderName = '佐藤教练'; break;
                case '🧠': senderName = '记忆管家'; break;
            }
        }

        console.log('最终确定的发送者:', `"${senderName}"`);

        // 创建语音合成实例
        const utterance = new SpeechSynthesisUtterance(cleanContent);
        utterance.lang = 'ja-JP';
        utterance.volume = 0.8;

        // 根据智能体设置语音参数
        let voiceConfig = getVoiceConfig(senderName);
        utterance.rate = voiceConfig.rate;
        utterance.pitch = voiceConfig.pitch;

        // 设置日语语音
        const setVoice = () => {
            const voices = speechSynthesis.getVoices();
            console.log('可用语音数量:', voices.length);

            // 打印所有日语语音供调试
            const japaneseVoices = voices.filter(v => v.lang.startsWith('ja'));
            console.log('可用的日语语音:', japaneseVoices.map(v => `${v.name} (${v.lang})`));

            let selectedVoice = selectVoiceForAgent(voices, senderName);

            if (selectedVoice) {
                utterance.voice = selectedVoice;
                console.log(`${senderName} 使用语音: ${selectedVoice.name} (${selectedVoice.lang})`);
            } else {
                console.warn('未找到合适的日语语音，使用默认语音');
            }
        };

        // 处理语音列表加载
        if (speechSynthesis.getVoices().length === 0) {
            speechSynthesis.onvoiceschanged = () => {
                setVoice();
                speechSynthesis.onvoiceschanged = null;
            };
        } else {
            setVoice();
        }

        // 播放事件处理
        utterance.onstart = () => {
            console.log('开始播放语音');
            buttonElement.classList.remove('loading');
            buttonElement.classList.add('playing');
            buttonElement.innerHTML = '<i class="fas fa-stop"></i>';
        };

        utterance.onend = () => {
            console.log('播放完成');
            resetAllSpeakerButtons();
        };

        utterance.onerror = (event) => {
            console.error('语音播放错误:', event);
            if (window.showNotification) {
                window.showNotification('语音播放失败: ' + event.error, 'error');
            }
            resetAllSpeakerButtons();
        };

        // 开始播放
        speechSynthesis.speak(utterance);

    } catch (error) {
        console.error('播放失败:', error);
        if (window.showNotification) {
            window.showNotification('语音播放失败', 'error');
        }
        resetSpeakerButton(buttonElement);
    }
}


// 为智能体选择合适的语音
function selectVoiceForAgent(voices, senderName) {
    // 过滤出日语语音
    const japaneseVoices = voices.filter(v => v.lang.startsWith('ja'));

    if (japaneseVoices.length === 0) {
        return null;
    }

    console.log('为', senderName, '选择语音，可用语音:', japaneseVoices.map(v => v.name));

    let selectedVoice = null;

    if (senderName.includes('小美')) {
        // 小美：先尝试 Ayumi（童声，像少女），再尝试 Sayaka，最后用默认第一个
        selectedVoice = japaneseVoices.find(v => v.name.includes('Ayumi')) ||
                      japaneseVoices.find(v => v.name.includes('Sayaka')) ||
                      japaneseVoices[0]; // 使用第一个日语语音作为备选
        console.log('小美使用少女声音:', selectedVoice?.name);
    }
    else if (senderName.includes('アイ')) {
        // AI：使用 Haruka（听起来比较像AI/童声）
        selectedVoice = japaneseVoices.find(v => v.name.includes('Haruka'));
        console.log('アイ使用童声/AI声音:', selectedVoice?.name);
    }
    else if (senderName.includes('记忆管家')) {
        // 记忆管家：使用 Ayumi（童声效果）
        selectedVoice = japaneseVoices.find(v => v.name.includes('Ayumi'));
        console.log('记忆管家使用童声:', selectedVoice?.name);
    }
    else if (senderName.includes('田中先生')) {
        // 田中先生：使用 Ichiro（成熟男声）
        selectedVoice = japaneseVoices.find(v => v.name.includes('Ichiro'));
        console.log('田中先生使用成熟男声:', selectedVoice?.name);
    }
    else if (senderName.includes('山田先生')) {
        // 山田先生：用 Ichiro 但调整参数
        selectedVoice = japaneseVoices.find(v => v.name.includes('Ichiro'));
        console.log('山田先生使用男声（温和版）:', selectedVoice?.name);
    }
    else if (senderName.includes('佐藤教练')) {
        // 佐藤教练：用 Ichiro 但参数更激烈
        selectedVoice = japaneseVoices.find(v => v.name.includes('Ichiro'));
        console.log('佐藤教练使用男声（激励版）:', selectedVoice?.name);
    }

    // 如果没找到指定语音，使用默认
    if (!selectedVoice) {
        selectedVoice = japaneseVoices[0];
        console.log('使用默认语音:', selectedVoice.name);
    }

    console.log('最终选择:', selectedVoice.name);
    return selectedVoice;
}


// 更新语音参数配置，让相同语音听起来不同
function getVoiceConfig(senderName) {
    if (senderName.includes('小美')) {
        return {
            rate: 1.1,   // 稍快（活泼少女）
            pitch: 1.4   // 很高音调（少女声）
        };
    } else if (senderName.includes('アイ')) {
        return {
            rate: 0.8,   // 慢速（机器感）
            pitch: 0.7   // 低音调（AI/童声机器化）
        };
    } else if (senderName.includes('记忆管家')) {
        return {
            rate: 0.9,   // 稍慢（系统化）
            pitch: 1.3   // 高音调（童声）
        };
    } else if (senderName.includes('田中先生')) {
        return {
            rate: 0.75,  // 很慢（严格老师）
            pitch: 0.8   // 低音调（权威感）
        };
    } else if (senderName.includes('山田先生')) {
        return {
            rate: 0.85,  // 慢速（温和）
            pitch: 0.9   // 稍低音调（温和男声）
        };
    } else if (senderName.includes('佐藤教练')) {
        return {
            rate: 1.2,   // 快速（激励感）
            pitch: 0.8   // 低音调（有力男声）
        };
    } else {
        return {
            rate: 0.8,
            pitch: 1.0
        };
    }
}

/**
 * 清理文本用于语音播放 - 只保留日语内容
 */
function cleanTextForSpeech(text) {
    if (!text) return '';

    console.log('原始文本:', text);

    let cleanText = text;

    // 移除HTML标签和格式标记
    cleanText = cleanText.replace(/<[^>]*>/g, '');
    cleanText = cleanText.replace(/\*\*/g, '');
    cleanText = cleanText.replace(/（.*?）/g, '');
    cleanText = cleanText.replace(/\(.*?\)/g, '');

    // 按句子分割，但保持更宽松的过滤
    const sentences = cleanText.split(/[。．！？\n]/);
    const japaneseSentences = [];

    for (let sentence of sentences) {
        sentence = sentence.trim();
        if (!sentence || sentence.length < 2) continue;

        // 检查是否包含日文字符（平假名、片假名、或常见日语汉字）
        const hasHiragana = /[\u3040-\u309F]/.test(sentence);
        const hasKatakana = /[\u30A0-\u30FF]/.test(sentence);
        const hasJapaneseKanji = /[申合格目指練習試験]/.test(sentence); // 常见日语汉字

        // 检查是否是明显的中文解释段落
        const isChineseExplanation = /[很高兴认识您|作为|一定|优秀|著名|重点大学|特别是|景色|非常有名|让我想起|如果您|学习|过程中|遇到|任何|问题|请随时|告诉我|详细解说|比如|区别|正确用法|变形规则|例如|句子中|主题|助词|表示|相当于|中文|礼貌体|断定|建议|可以从|每天|基础|配合|例句|进行|记忆|期待|一起|探索]/.test(sentence);

        // 如果包含日文字符且不是中文解释，就保留
        if ((hasHiragana || hasKatakana || hasJapaneseKanji) && !isChineseExplanation) {
            japaneseSentences.push(sentence);
        }
    }

    const result = japaneseSentences.join('。');
    console.log('过滤后的日语:', result);

    return result;
}

/**
 * 重置所有播放按钮状态
 */
function resetAllSpeakerButtons() {
    document.querySelectorAll('.speaker-btn').forEach(btn => {
        resetSpeakerButton(btn);
    });
}

/**
 * 重置单个播放按钮状态
 */
function resetSpeakerButton(btn) {
    btn.classList.remove('loading', 'playing');
    btn.innerHTML = '<i class="fas fa-volume-up"></i>';
}

/**
 * 修复现有消息的播放按钮
 */
function fixExistingMessages() {
    const messages = document.querySelectorAll('.message:not(.user)');
    console.log('找到', messages.length, '条智能体消息');

    messages.forEach(message => {
        if (!message.querySelector('.speaker-btn')) {
            addPlayButtonToMessage(message);
        }
    });
}

/**
 * 为消息添加播放按钮
 */
function addPlayButtonToMessage(messageElement) {
    const messageContent = messageElement.querySelector('.message-content');
    if (!messageContent) return;

    // 查找消息文本
    const messageTextElements = messageContent.querySelectorAll('div');
    let messageText = '';

    for (let div of messageTextElements) {
        if (!div.classList.contains('message-meta') && !div.classList.contains('message-actions')) {
            messageText = div.textContent || div.innerText;
            break;
        }
    }

    if (!messageText) return;

    // 创建按钮容器
    let actionsContainer = messageContent.querySelector('.message-actions');
    if (!actionsContainer) {
        actionsContainer = document.createElement('div');
        actionsContainer.className = 'message-actions';
        messageContent.appendChild(actionsContainer);
    }

    // 创建播放按钮
    const speakerBtn = document.createElement('button');
    speakerBtn.className = 'speaker-btn';
    speakerBtn.title = '播放语音';
    speakerBtn.setAttribute('data-content', encodeURIComponent(messageText));
    speakerBtn.innerHTML = '<i class="fas fa-volume-up"></i>';

    actionsContainer.appendChild(speakerBtn);
    console.log('为消息添加了播放按钮:', messageText.substring(0, 30) + '...');
}

/**
 * 重写原始的 addMessage 函数以确保播放按钮正确添加
 */
function enhanceAddMessage() {
    const originalAddMessage = window.addMessage;

    if (typeof originalAddMessage === 'function') {
        window.addMessage = function(senderId, content) {
            // 调用原始函数
            const result = originalAddMessage.call(this, senderId, content);

            // 如果是智能体消息，确保有播放按钮
            if (senderId !== 'user') {
                setTimeout(() => {
                    const lastMessage = document.querySelector('.message:last-child');
                    if (lastMessage && !lastMessage.classList.contains('user')) {
                        if (!lastMessage.querySelector('.speaker-btn')) {
                            addPlayButtonToMessage(lastMessage);
                        }
                    }
                }, 100);
            }

            return result;
        };

        console.log('addMessage 函数已增强');
    } else {
        console.warn('未找到原始 addMessage 函数');
    }
}

// 页面加载完成后增强 addMessage 函数
setTimeout(enhanceAddMessage, 2000);

// 导出函数供外部使用
window.voiceIntegration = {
    speakMessageContent,
    resetAllSpeakerButtons,
    addPlayButtonToMessage,
    cleanTextForSpeech
};

console.log('语音集成模块已加载');

// 调试函数：列出所有可用语音
function debugAvailableVoices() {
    const voices = speechSynthesis.getVoices();
    console.log('=== 所有可用语音 ===');
    voices.forEach((voice, index) => {
        console.log(`${index}: ${voice.name} (${voice.lang}) - ${voice.localService ? '本地' : '远程'}`);
    });

    const japaneseVoices = voices.filter(v => v.lang.startsWith('ja'));
    console.log('=== 日语语音 ===');
    japaneseVoices.forEach((voice, index) => {
        console.log(`${index}: ${voice.name} (${voice.lang})`);
    });
}

// 兼容函数：为了支持 index.html 中可能调用 speakMessage 的地方
window.speakMessage = function(buttonElement) {
    const content = buttonElement.getAttribute('data-content');
    if (content) {
        speakMessageContent(decodeURIComponent(content), buttonElement);
    }
};

// 确保这些函数也可以全局访问
window.resetAllSpeakerButtons = resetAllSpeakerButtons;
window.resetSpeakerButton = resetSpeakerButton;
window.debugAvailableVoices = debugAvailableVoices;