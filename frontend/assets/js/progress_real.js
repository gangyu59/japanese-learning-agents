// frontend/assets/js/progress_real.js
/**
 * 真实学习进度数据处理
 * 替换progress.html中的假数据，使用真实API数据
 */

class RealProgressManager {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.progressData = null;
        this.isLoading = false;
    }

    /**
     * 初始化进度页面
     */
    async init() {
        console.log('🚀 初始化真实进度数据管理器');

        try {
            await this.loadProgressData();
            this.renderProgressData();
            this.setupEventListeners();
        } catch (error) {
            console.error('❌ 初始化进度页面失败:', error);
            this.showErrorMessage('加载进度数据失败，请刷新页面重试');
        }
    }

    /**
     * 从API加载进度数据
     */
    async loadProgressData() {
        this.setLoadingState(true);

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/v1/progress/summary?user_id=demo_user`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            if (result.success) {
                this.progressData = result.data;
                console.log('✅ 进度数据加载成功:', this.progressData);
            } else {
                throw new Error('API返回失败状态');
            }

        } catch (error) {
            console.error('❌ 加载进度数据失败:', error);
            // 使用默认数据作为fallback
            this.progressData = this.getDefaultProgressData();
        } finally {
            this.setLoadingState(false);
        }
    }

    /**
     * 渲染进度数据到页面
     */
    renderProgressData() {
        if (!this.progressData) {
            console.warn('⚠️  没有进度数据可渲染');
            return;
        }

        console.log('🎨 开始渲染进度数据');

        // 更新用户统计
        this.updateUserStats();

        // 更新技能进度
        this.updateSkillsProgress();

        // 更新学习建议
        this.updateRecommendations();

        // 启动动画
        this.animateProgressElements();
    }

    /**
     * 更新用户统计数据
     */
    updateUserStats() {
        const stats = this.progressData.user_stats;

        // 更新等级
        const levelElement = document.querySelector('.level-badge');
        if (levelElement) {
            levelElement.textContent = this.getLevelDisplay(stats.level);
        }

        // 更新整体进度百分比
        const overallProgress = this.calculateOverallProgress();
        this.updateCircularProgress(overallProgress);

        // 更新统计数字
        this.updateStatValue('等级', stats.level);
        this.updateStatValue('经验值', `${stats.total_xp} XP`);
        this.updateStatValue('连续学习', `${stats.streak_days} 天`);

        console.log('📊 用户统计数据已更新');
    }

    /**
     * 更新技能进度卡片
     */
    updateSkillsProgress() {
        const skills = this.progressData.skills;

        // 更新概览卡片
        this.updateOverviewCard('vocabulary', skills.vocabulary.count, skills.vocabulary.percentage);
        this.updateOverviewCard('grammar', skills.grammar.count, skills.grammar.percentage);
        this.updateOverviewCard('conversation', skills.conversation.count, skills.conversation.percentage);
        this.updateOverviewCard('cultural', skills.cultural.count, skills.cultural.percentage);

        // 更新详细技能卡片
        this.updateDetailedSkillCard('vocabulary', '词汇量', skills.vocabulary);
        this.updateDetailedSkillCard('grammar', '语法', skills.grammar);
        this.updateDetailedSkillCard('conversation', '对话', skills.conversation);
        this.updateDetailedSkillCard('cultural', '文化', skills.cultural);

        console.log('🎯 技能进度已更新');
    }

    /**
     * 更新学习建议
     */
    updateRecommendations() {
        const recommendations = this.progressData.recommendations || [];
        const recommendationsContainer = document.querySelector('.recommendations-grid');

        if (!recommendationsContainer || recommendations.length === 0) {
            return;
        }

        // 清空现有建议
        recommendationsContainer.innerHTML = '';

        // 添加真实建议
        recommendations.forEach((rec, index) => {
            const recCard = this.createRecommendationCard(rec, index);
            recommendationsContainer.appendChild(recCard);
        });

        console.log('💡 学习建议已更新');
    }

    /**
     * 更新概览卡片
     */
    updateOverviewCard(type, count, percentage) {
        // 根据类型找到对应的卡片
        const cardSelectors = {
            'vocabulary': '.overview-card:nth-child(1)',
            'grammar': '.overview-card:nth-child(2)',
            'conversation': '.overview-card:nth-child(3)',
            'cultural': '.overview-card:nth-child(4)'
        };

        const card = document.querySelector(cardSelectors[type]);
        if (!card) return;

        // 更新数字
        const numberElement = card.querySelector('.card-number');
        if (numberElement) {
            numberElement.textContent = count;
        }

        // 更新进度条
        const progressFill = card.querySelector('.mini-progress-fill');
        const progressText = card.querySelector('.progress-text');

        if (progressFill) {
            progressFill.style.width = `${percentage}%`;
        }

        if (progressText) {
            progressText.textContent = `${percentage}%`;
        }
    }

    /**
     * 更新详细技能卡片
     */
    updateDetailedSkillCard(skillType, skillName, skillData) {
        // 查找技能卡片
        const skillCards = document.querySelectorAll('.skill-card');
        const skillCard = Array.from(skillCards).find(card =>
            card.querySelector('h3').textContent.includes(skillName)
        );

        if (!skillCard) return;

        // 更新百分比
        const percentageElement = skillCard.querySelector('.skill-percentage');
        if (percentageElement) {
            percentageElement.textContent = `${skillData.percentage}%`;
        }

        // 更新进度条
        const progressFill = skillCard.querySelector('.skill-progress-fill');
        if (progressFill) {
            progressFill.style.width = `${skillData.percentage}%`;
        }

        // 更新等级标签
        const levelLabel = skillCard.querySelector('.skill-level');
        if (levelLabel) {
            levelLabel.textContent = this.getSkillLevel(skillData.percentage);
        }
    }

    /**
     * 创建建议卡片
     */
    createRecommendationCard(recommendation, index) {
        const card = document.createElement('div');
        card.className = `recommendation-card priority-${recommendation.priority}`;

        const priorityIcons = {
            'high': '⚠️',
            'medium': '📈',
            'low': '🎯'
        };

        const priorityTexts = {
            'high': '高优先级',
            'medium': '中优先级',
            'low': '低优先级'
        };

        card.innerHTML = `
            <div class="rec-header">
                <div class="rec-icon">${priorityIcons[recommendation.priority] || '💡'}</div>
                <div class="rec-priority">${priorityTexts[recommendation.priority]}</div>
            </div>
            <h3>${recommendation.title}</h3>
            <p>${recommendation.description}</p>
            <div class="rec-actions">
                <button class="rec-btn primary" onclick="handleRecommendationAction('${recommendation.title}')">
                    开始实践
                </button>
            </div>
        `;

        return card;
    }

    /**
     * 更新圆形进度条
     */
    updateCircularProgress(percentage) {
        const circle = document.querySelector('.circular-progress circle:last-child');
        const percentageText = document.querySelector('.progress-percentage');

        if (circle) {
            const circumference = 2 * Math.PI * 54; // radius = 54
            const offset = circumference - (percentage / 100) * circumference;
            circle.style.strokeDashoffset = offset;
        }

        if (percentageText) {
            percentageText.textContent = `${percentage}%`;
        }
    }

    /**
     * 计算整体进度
     */
    calculateOverallProgress() {
        const skills = this.progressData.skills;
        const weights = { vocabulary: 0.3, grammar: 0.3, conversation: 0.25, cultural: 0.15 };

        const weightedSum =
            skills.vocabulary.percentage * weights.vocabulary +
            skills.grammar.percentage * weights.grammar +
            skills.conversation.percentage * weights.conversation +
            skills.cultural.percentage * weights.cultural;

        return Math.round(weightedSum);
    }

    /**
     * 获取等级显示文本
     */
    getLevelDisplay(level) {
        if (level <= 5) return 'N5 级别';
        if (level <= 10) return 'N4 级别';
        if (level <= 15) return 'N3 级别';
        if (level <= 20) return 'N2 级别';
        return 'N1 级别';
    }

    /**
     * 获取技能等级
     */
    getSkillLevel(percentage) {
        if (percentage < 30) return '初级';
        if (percentage < 70) return '中级';
        return '高级';
    }

    /**
     * 更新统计数值
     */
    updateStatValue(label, value) {
        const statItems = document.querySelectorAll('.stat-item');
        const statItem = Array.from(statItems).find(item =>
            item.querySelector('.stat-label').textContent.includes(label)
        );

        if (statItem) {
            const valueElement = statItem.querySelector('.stat-value');
            if (valueElement) {
                valueElement.textContent = value;
            }
        }
    }

    /**
     * 启动进度动画
     */
    animateProgressElements() {
        // 延迟启动动画，让数据先渲染
        setTimeout(() => {
            this.animateProgressBars();
            this.animateCounters();
        }, 300);
    }

    /**
     * 动画进度条
     */
    animateProgressBars() {
        document.querySelectorAll('.mini-progress-fill, .skill-progress-fill').forEach((bar, index) => {
            setTimeout(() => {
                bar.style.transition = 'width 1.5s ease-out';
                const targetWidth = bar.style.width;
                bar.style.width = '0%';

                setTimeout(() => {
                    bar.style.width = targetWidth;
                }, 100);
            }, index * 200);
        });
    }

    /**
     * 动画数字计数器
     */
    animateCounters() {
        const counters = document.querySelectorAll('.card-number, .stat-value, .progress-percentage');

        counters.forEach(counter => {
            const target = parseInt(counter.textContent) || 0;
            if (target === 0) return;

            let current = 0;
            const increment = target / 30;
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    counter.textContent = target + (counter.textContent.includes('%') ? '%' : '');
                    clearInterval(timer);
                } else {
                    counter.textContent = Math.floor(current) + (counter.textContent.includes('%') ? '%' : '');
                }
            }, 50);
        });
    }

    /**
     * 设置加载状态
     */
    setLoadingState(loading) {
        this.isLoading = loading;

        // 可以添加加载指示器
        const loadingIndicator = document.querySelector('.loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.style.display = loading ? 'block' : 'none';
        }
    }

    /**
     * 显示错误消息
     */
    showErrorMessage(message) {
        console.error('🚨 错误:', message);

        // 可以显示用户友好的错误提示
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #f44336;
            color: white;
            padding: 15px;
            border-radius: 8px;
            z-index: 10000;
        `;

        document.body.appendChild(errorDiv);

        setTimeout(() => errorDiv.remove(), 5000);
    }

    /**
     * 获取默认进度数据（fallback）
     */
    getDefaultProgressData() {
        return {
            user_stats: {
                level: 1,
                total_xp: 0,
                streak_days: 0,
                current_level: 'beginner'
            },
            skills: {
                vocabulary: { count: 0, mastery: 0, percentage: 0 },
                grammar: { count: 0, mastery: 0, percentage: 0 },
                cultural: { count: 0, understanding: 0, percentage: 0 },
                conversation: { count: 0, percentage: 0 }
            },
            weak_points: [],
            recommendations: [{
                priority: 'high',
                title: '开始学习之旅',
                description: '欢迎来到日语学习系统！开始与智能体对话来积累学习数据。'
            }]
        };
    }

    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        // 刷新按钮
        const refreshBtn = document.querySelector('.refresh-progress');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshProgress());
        }

        // 定期自动刷新（可选）
        setInterval(() => {
            if (!this.isLoading) {
                this.loadProgressData().then(() => {
                    this.renderProgressData();
                });
            }
        }, 60000); // 每分钟刷新一次
    }

    /**
     * 手动刷新进度
     */
    async refreshProgress() {
        console.log('🔄 手动刷新进度数据');
        await this.loadProgressData();
        this.renderProgressData();
    }
}

// 全局建议处理函数
function handleRecommendationAction(title) {
    console.log('🎯 执行建议:', title);
    showNotification(`开始实践：${title}`, 'success');

    // 可以跳转到相应的学习模块
    // 例如：window.location.href = '/chat?focus=' + encodeURIComponent(title);
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 进度页面DOM加载完成');

    // 创建并初始化进度管理器
    window.progressManager = new RealProgressManager();
    window.progressManager.init();

    // 保持原有的动画效果
    animateProgressBars();
    initializeProgressPage();
});

// 兼容原有函数
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        animation: slideInRight 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}