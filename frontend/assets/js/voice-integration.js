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
        // 清理内容
        const cleanContent = cleanTextForSpeech(content);

        if (!cleanContent.trim()) {
            if (window.showNotification) {
                window.showNotification('没有可播放的内容', 'warning');
            }
            resetSpeakerButton(buttonElement);
            return;
        }

        console.log('清理后的内容:', cleanContent);

        // 创建语音合成实例
        const utterance = new SpeechSynthesisUtterance(cleanContent);
        utterance.lang = 'ja-JP';
        utterance.rate = 0.8;
        utterance.pitch = 1.0;
        utterance.volume = 0.8;

        // 设置日语语音
        const setVoice = () => {
            const voices = speechSynthesis.getVoices();
            const japaneseVoice = voices.find(v =>
                v.lang.startsWith('ja') ||
                v.name.toLowerCase().includes('japanese') ||
                v.name.toLowerCase().includes('japan')
            );

            if (japaneseVoice) {
                utterance.voice = japaneseVoice;
                console.log('使用日语语音:', japaneseVoice.name);
            } else {
                console.warn('未找到日语语音，使用默认语音');
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

/**
 * 清理文本用于语音播放
 */
function cleanTextForSpeech(text) {
    if (!text) return '';

    let cleanText = text;

    // 移除HTML标签
    cleanText = cleanText.replace(/<[^>]*>/g, '');

    // 移除模拟响应标记
    cleanText = cleanText.replace(/\*\[.*?\]\*/g, '');

    // 移除中文翻译部分（保留日语）
    const parts = cleanText.split(/\*\*中文翻译：\*\*|\*\*中文提示：\*\*/);
    if (parts.length > 1) {
        cleanText = parts[0].trim();
    }

    // 移除多余的空白字符
    cleanText = cleanText.replace(/\s+/g, ' ').trim();

    return cleanText;
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