/**
 * 语音输入模块
 * 路径: frontend/assets/js/voice.js
 * 功能: 处理语音识别和语音合成
 */

class VoiceInputManager {
    constructor() {
        this.recognition = null;
        this.synthesis = null;
        this.isListening = false;
        this.isSupported = false;
        this.currentLanguage = 'ja-JP'; // 默认日语
        this.fallbackLanguage = 'zh-CN'; // 备用中文

        this.init();
    }

    /**
     * 初始化语音功能
     */
    init() {
        this.initSpeechRecognition();
        this.initSpeechSynthesis();
        this.bindEvents();
    }

    /**
     * 初始化语音识别
     */
    initSpeechRecognition() {
        // 检查浏览器支持
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            console.warn('语音识别不支持');
            this.showNotSupported();
            return;
        }

        this.recognition = new SpeechRecognition();
        this.setupRecognitionConfig();
        this.setupRecognitionEvents();
        this.isSupported = true;
    }

    /**
     * 配置语音识别参数
     */
    setupRecognitionConfig() {
        this.recognition.continuous = false;           // 单次识别
        this.recognition.interimResults = true;        // 显示临时结果
        this.recognition.maxAlternatives = 3;          // 最多3个候选结果
        this.recognition.lang = this.currentLanguage;  // 设置语言
    }

    /**
     * 设置语音识别事件
     */
    setupRecognitionEvents() {
        // 开始识别
        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateVoiceButtonState('listening');
            this.showVoiceStatus('正在监听语音输入...', 'listening');
        };

        // 识别结果
        this.recognition.onresult = (event) => {
            this.handleRecognitionResult(event);
        };

        // 识别结束
        this.recognition.onend = () => {
            this.isListening = false;
            this.updateVoiceButtonState('idle');
            this.hideVoiceStatus();

            // 如果识别结束时还有临时结果且没有最终结果，清理临时状态
            const input = document.getElementById('messageInput');
            if (input && input.dataset.originalValue !== undefined && input.style.color === '#999') {
                this.clearInterimResult();
            }
        };

        // 识别错误
        this.recognition.onerror = (event) => {
            this.handleRecognitionError(event);
        };

        // 无语音输入
        this.recognition.onnomatch = () => {
            this.showVoiceStatus('未识别到有效语音，请重试', 'error');
        };
    }

    /**
     * 处理识别结果
     */
    handleRecognitionResult(event) {
        let finalTranscript = '';
        let interimTranscript = '';

        // 处理识别结果
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;

            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }

        // 显示临时结果
        if (interimTranscript) {
            this.showInterimResult(interimTranscript);
        }

        // 处理最终结果
        if (finalTranscript) {
            this.processFinalResult(finalTranscript, event.results);
        }
    }

    /**
     * 处理最终识别结果
     */
    processFinalResult(transcript, results) {
        const confidence = results[0][0].confidence;

        // 获取多个候选结果
        const alternatives = [];
        for (let i = 0; i < Math.min(results[0].length, 3); i++) {
            alternatives.push({
                transcript: results[0][i].transcript,
                confidence: results[0][i].confidence
            });
        }

        // 置信度检查
        if (confidence < 0.6) {
            this.showLowConfidenceDialog(alternatives);
        } else {
            this.insertTextToInput(transcript);
            this.showVoiceStatus(`语音识别完成 (置信度: ${Math.round(confidence * 100)}%)`, 'success');
        }
    }

    /**
     * 显示低置信度选择对话框
     */
    showLowConfidenceDialog(alternatives) {
        const dialog = document.createElement('div');
        dialog.className = 'voice-alternatives-dialog';
        dialog.innerHTML = `
            <div class="dialog-content">
                <h4>请选择正确的识别结果：</h4>
                <div class="alternatives-list">
                    ${alternatives.map((alt, index) => `
                        <button class="alternative-btn" data-text="${alt.transcript}">
                            ${alt.transcript} (${Math.round(alt.confidence * 100)}%)
                        </button>
                    `).join('')}
                </div>
                <div class="dialog-actions">
                    <button class="btn-retry">重新识别</button>
                    <button class="btn-cancel">取消</button>
                </div>
            </div>
        `;

        // 添加事件监听
        dialog.addEventListener('click', (e) => {
            if (e.target.classList.contains('alternative-btn')) {
                this.insertTextToInput(e.target.dataset.text);
                document.body.removeChild(dialog);
            } else if (e.target.classList.contains('btn-retry')) {
                document.body.removeChild(dialog);
                this.startVoiceInput();
            } else if (e.target.classList.contains('btn-cancel')) {
                document.body.removeChild(dialog);
            }
        });

        document.body.appendChild(dialog);
    }

    /**
     * 处理识别错误
     */
    handleRecognitionError(event) {
        this.isListening = false;
        this.updateVoiceButtonState('error');

        let errorMessage = '语音识别失败';

        switch (event.error) {
            case 'no-speech':
                errorMessage = '未检测到语音输入';
                break;
            case 'audio-capture':
                errorMessage = '无法访问麦克风';
                break;
            case 'not-allowed':
                errorMessage = '麦克风权限被拒绝';
                this.showPermissionDialog();
                break;
            case 'network':
                errorMessage = '网络连接错误';
                break;
            case 'service-not-allowed':
                errorMessage = '语音服务不可用';
                break;
            default:
                errorMessage = `语音识别错误: ${event.error}`;
        }

        this.showVoiceStatus(errorMessage, 'error');
        setTimeout(() => this.updateVoiceButtonState('idle'), 3000);
    }

    /**
     * 初始化语音合成
     */
    initSpeechSynthesis() {
        if ('speechSynthesis' in window) {
            this.synthesis = window.speechSynthesis;
        }
    }

    /**
     * 语音播放文本
     */
    speakText(text, language = 'ja-JP') {
        if (!this.synthesis) return;

        // 停止当前播放
        this.synthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = language;
        utterance.rate = 0.8;   // 语速
        utterance.pitch = 1.0;  // 音调
        utterance.volume = 0.8; // 音量

        // 选择合适的语音
        const voices = this.synthesis.getVoices();
        const voice = voices.find(v => v.lang.startsWith(language.split('-')[0]));
        if (voice) {
            utterance.voice = voice;
        }

        this.synthesis.speak(utterance);
    }

    /**
     * 开始语音输入
     */
    startVoiceInput() {
        if (!this.isSupported) {
            this.showNotSupported();
            return;
        }

        if (this.isListening) {
            this.stopVoiceInput();
            return;
        }

        try {
            this.recognition.start();
        } catch (error) {
            console.error('启动语音识别失败:', error);
            this.showVoiceStatus('启动语音识别失败', 'error');
        }
    }

    /**
     * 停止语音输入
     */
    stopVoiceInput() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
    }

    /**
     * 切换语言
     */
    switchLanguage(language = null) {
        if (language) {
            this.currentLanguage = language;
        } else {
            // 在日语和中文之间切换
            this.currentLanguage = this.currentLanguage === 'ja-JP' ? 'zh-CN' : 'ja-JP';
        }

        if (this.recognition) {
            this.recognition.lang = this.currentLanguage;
        }

        const langName = this.currentLanguage === 'ja-JP' ? '日语' : '中文';
        this.showVoiceStatus(`语音识别语言已切换到: ${langName}`, 'info');
    }

    /**
     * 更新语音按钮状态
     */
    updateVoiceButtonState(state) {
        const voiceBtn = document.querySelector('.voice-btn');
        if (!voiceBtn) return;

        // 重置所有状态类
        voiceBtn.classList.remove('listening', 'processing', 'error');

        switch (state) {
            case 'listening':
                voiceBtn.classList.add('listening');
                voiceBtn.innerHTML = '<i class="fas fa-stop"></i>';
                voiceBtn.style.background = 'linear-gradient(135deg, #e53e3e 0%, #c53030 100%)';
                break;
            case 'processing':
                voiceBtn.classList.add('processing');
                voiceBtn.innerHTML = '<i class="fas fa-cog fa-spin"></i>';
                voiceBtn.style.background = 'linear-gradient(135deg, #4299e1 0%, #3182ce 100%)';
                break;
            case 'error':
                voiceBtn.classList.add('error');
                voiceBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
                voiceBtn.style.background = 'linear-gradient(135deg, #e53e3e 0%, #c53030 100%)';
                break;
            default: // idle
                voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
                voiceBtn.style.background = 'linear-gradient(135deg, #ed8936 0%, #dd6b20 100%)';
        }
    }

    /**
     * 显示语音状态
     */
    showVoiceStatus(message, type = 'info') {
        // 使用现有的通知系统
        if (window.showNotification) {
            window.showNotification(message, type);
        }

        // 同时显示在语音状态区域
        this.updateVoiceStatusDisplay(message, type);
    }

    /**
     * 更新语音状态显示
     */
    updateVoiceStatusDisplay(message, type) {
        let statusElement = document.getElementById('voiceStatus');

        if (!statusElement) {
            statusElement = document.createElement('div');
            statusElement.id = 'voiceStatus';
            statusElement.className = 'voice-status';

            // 插入到输入框附近
            const chatInput = document.querySelector('.chat-input');
            if (chatInput) {
                chatInput.appendChild(statusElement);
            }
        }

        statusElement.textContent = message;
        statusElement.className = `voice-status ${type}`;
        statusElement.style.display = 'block';

        // 3秒后自动隐藏
        setTimeout(() => {
            statusElement.style.display = 'none';
        }, 3000);
    }

    /**
     * 显示临时识别结果
     */
    showInterimResult(text) {
        const input = document.getElementById('messageInput');
        if (input) {
            // 保存原始值
            if (!input.dataset.originalValue) {
                input.dataset.originalValue = input.value;
            }

            // 显示临时结果（灰色文本）
            input.value = input.dataset.originalValue + text;
            input.style.color = '#999';
        }
    }

    /**
     * 将文本插入输入框
     */
    insertTextToInput(text) {
        const input = document.getElementById('messageInput');
        if (input) {
            // 恢复正常颜色
            input.style.color = '';

            // 清理临时数据
            delete input.dataset.originalValue;

            // 插入文本
            const currentValue = input.value;
            const cleanText = text.trim();

            if (currentValue && !currentValue.endsWith(' ')) {
                input.value = currentValue + ' ' + cleanText;
            } else {
                input.value = currentValue + cleanText;
            }

            // 触发焦点
            input.focus();
        }
    }

    /**
     * 隐藏语音状态
     */
    hideVoiceStatus() {
        const statusElement = document.getElementById('voiceStatus');
        if (statusElement) {
            statusElement.style.display = 'none';
        }
    }

    /**
     * 显示不支持提示
     */
    showNotSupported() {
        this.showVoiceStatus('您的浏览器不支持语音识别功能', 'warning');
    }

    /**
     * 显示权限对话框
     */
    showPermissionDialog() {
        const dialog = document.createElement('div');
        dialog.className = 'permission-dialog';
        dialog.innerHTML = `
            <div class="dialog-content">
                <h4>需要麦克风权限</h4>
                <p>为了使用语音输入功能，请允许访问您的麦克风。</p>
                <div class="dialog-actions">
                    <button class="btn-primary" onclick="this.parentElement.parentElement.parentElement.remove()">
                        知道了
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(dialog);
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 绑定语音按钮点击事件
        document.addEventListener('click', (e) => {
            if (e.target.closest('.voice-btn')) {
                e.preventDefault();
                this.startVoiceInput();
            }

            // 语言切换按钮
            if (e.target.closest('.voice-lang-switch')) {
                e.preventDefault();
                this.switchLanguage();
            }
        });

        // 键盘快捷键：Ctrl/Cmd + Shift + V
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'V') {
                e.preventDefault();
                this.startVoiceInput();
            }
        });

        // 长按语音按钮持续录音
        let pressTimer = null;
        document.addEventListener('mousedown', (e) => {
            if (e.target.closest('.voice-btn')) {
                pressTimer = setTimeout(() => {
                    // 长按模式：持续录音
                    this.startContinuousRecording();
                }, 500);
            }
        });

        document.addEventListener('mouseup', (e) => {
            if (pressTimer) {
                clearTimeout(pressTimer);
                pressTimer = null;
            }
        });
    }

    /**
     * 持续录音模式
     */
    startContinuousRecording() {
        if (this.recognition) {
            this.recognition.continuous = true;
            this.recognition.interimResults = true;
            this.showVoiceStatus('持续录音模式已启动，再次点击停止', 'info');
        }
    }

    /**
     * 获取支持的语言列表
     */
    getSupportedLanguages() {
        return [
            { code: 'ja-JP', name: '日语 (日本)' },
            { code: 'zh-CN', name: '中文 (简体)' },
            { code: 'zh-TW', name: '中文 (繁体)' },
            { code: 'en-US', name: '英语 (美国)' },
            { code: 'ko-KR', name: '韩语' }
        ];
    }

    /**
     * 销毁语音管理器
     */
    destroy() {
        if (this.recognition) {
            this.recognition.abort();
        }
        if (this.synthesis) {
            this.synthesis.cancel();
        }
    }
}

// 导出模块
window.VoiceInputManager = VoiceInputManager;