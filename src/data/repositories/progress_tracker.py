# src/data/repositories/progress_tracker.py
"""
学习进度追踪核心引擎
负责收集、计算和存储学习进度数据
"""

import uuid
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from ..models.learning import (
    LearningProgress, VocabularyProgress, ConversationLearning,
    UserStats, CulturalKnowledge
)
from ..models.base import get_db_session


class ProgressTracker:
    """学习进度追踪器"""

    def __init__(self):
        self.session = get_db_session()

    def extract_learning_data(self, user_input: str, agent_responses: Dict,
                              session_id: str, scene_context: str = 'general') -> Dict:
        """
        从对话中提取学习数据
        不改变现有API的输入输出，只是额外收集数据
        """
        learning_data = {
            'grammar_points': [],
            'vocabulary': [],
            'cultural_topics': [],
            'corrections': [],
            'conversation_id': str(uuid.uuid4())
        }

        # 分析每个智能体的回复
        for agent_name, response in agent_responses.items():
            if isinstance(response, dict):
                content = response.get('content', '')
                agent_id = response.get('agent_name', agent_name)

                # 根据智能体类型提取不同的学习数据
                if '田中先生' in agent_id or 'tanaka' in agent_id.lower():
                    learning_data['grammar_points'].extend(
                        self._extract_grammar_points(content, user_input)
                    )
                    learning_data['corrections'].extend(
                        self._extract_corrections(content, user_input)
                    )

                elif '小美' in agent_id or 'koumi' in agent_id.lower():
                    learning_data['vocabulary'].extend(
                        self._extract_casual_vocabulary(content)
                    )

                elif '山田先生' in agent_id or 'yamada' in agent_id.lower():
                    learning_data['cultural_topics'].extend(
                        self._extract_cultural_topics(content)
                    )

                elif 'アイ' in agent_id or 'ai' in agent_id.lower():
                    # AI分析师可能提供学习建议和难度评估
                    pass

        # 存储对话学习记录
        self._save_conversation_learning(
            user_input, agent_responses, learning_data, session_id, scene_context
        )

        # 更新各种进度
        self._update_progress_from_learning_data(learning_data)

        return learning_data

    def _extract_grammar_points(self, agent_content: str, user_input: str) -> List[Dict]:
        """提取语法点（田中先生的专长）"""
        grammar_points = []

        # 常见的语法指示词
        grammar_indicators = [
            'を', 'が', 'に', 'で', 'から', 'まで', 'と', 'や',
            'です', 'ます', 'た', 'だ', 'である',
            '〜て', '〜た', '〜ない', '〜る',
            '敬语', '谦让语', '丁宁语'
        ]

        # 在智能体回复中查找语法解释
        for indicator in grammar_indicators:
            if indicator in agent_content and ('语法' in agent_content or '文法' in agent_content):
                grammar_points.append({
                    'point': indicator,
                    'explanation': agent_content,
                    'user_example': user_input,
                    'difficulty': self._estimate_grammar_difficulty(indicator),
                    'source_agent': 'tanaka'
                })

        return grammar_points

    def _extract_corrections(self, agent_content: str, user_input: str) -> List[Dict]:
        """提取语法纠正"""
        corrections = []

        # 查找纠正指示词
        correction_indicators = ['应该是', '正确的是', '改为', '错误', '不对', '修正']

        for indicator in correction_indicators:
            if indicator in agent_content:
                corrections.append({
                    'original': user_input,
                    'corrected': agent_content,
                    'error_type': 'grammar',
                    'explanation': agent_content,
                    'source_agent': 'tanaka'
                })

        return corrections

    def _extract_casual_vocabulary(self, agent_content: str) -> List[Dict]:
        """提取口语词汇（小美的专长）"""
        vocabulary = []

        # 日语词汇模式匹配
        japanese_pattern = r'[ひらがなカタカナ一-龯]+'
        words = re.findall(japanese_pattern, agent_content)

        for word in words:
            if len(word) >= 2:  # 过滤单字符
                vocabulary.append({
                    'word': word,
                    'context': agent_content,
                    'type': 'casual',
                    'source_agent': 'koumi'
                })

        return vocabulary

    def _extract_cultural_topics(self, agent_content: str) -> List[Dict]:
        """提取文化话题（山田先生的专长）"""
        cultural_topics = []

        # 文化关键词
        cultural_keywords = [
            '传统', '文化', '历史', '节日', '仪式', '茶道', '武士道',
            '和服', '寺庙', '神社', '祭り', '桜', '新年', '盂兰盆节'
        ]

        for keyword in cultural_keywords:
            if keyword in agent_content:
                cultural_topics.append({
                    'topic': keyword,
                    'content': agent_content,
                    'category': 'traditional_culture',
                    'source_agent': 'yamada'
                })

        return cultural_topics

    def _estimate_grammar_difficulty(self, grammar_point: str) -> float:
        """估算语法点难度"""
        difficulty_map = {
            'を': 0.2, 'が': 0.3, 'に': 0.4, 'で': 0.3,
            'です': 0.1, 'ます': 0.2,
            '敬语': 0.8, '谦让语': 0.9,
            '〜て': 0.5, '〜た': 0.4
        }
        return difficulty_map.get(grammar_point, 0.5)

    def _save_conversation_learning(self, user_input: str, agent_responses: Dict,
                                    learning_data: Dict, session_id: str, scene_context: str):
        """保存对话学习记录"""
        conversation = ConversationLearning(
            id=learning_data['conversation_id'],
            session_id=session_id,
            user_input=user_input,
            agent_responses=agent_responses,
            learning_points=learning_data,
            corrections_made=learning_data['corrections'],
            participating_agents=list(agent_responses.keys()),
            scene_context=scene_context
        )

        self.session.add(conversation)
        self.session.commit()

    def _update_progress_from_learning_data(self, learning_data: Dict):
        """根据学习数据更新进度"""
        # 更新语法进度
        for grammar in learning_data['grammar_points']:
            self._update_grammar_progress(grammar)

        # 更新词汇进度
        for vocab in learning_data['vocabulary']:
            self._update_vocabulary_progress(vocab)

        # 更新文化知识
        for cultural in learning_data['cultural_topics']:
            self._update_cultural_knowledge(cultural)

        # 更新用户统计
        self._update_user_stats()

    def _update_grammar_progress(self, grammar_data: Dict):
        """更新语法学习进度"""
        point = grammar_data['point']

        # 查找现有记录
        existing = self.session.query(LearningProgress).filter(
            and_(
                LearningProgress.user_id == 'demo_user',
                LearningProgress.grammar_point == point
            )
        ).first()

        if existing:
            # 更新现有记录
            existing.practice_count += 1
            existing.last_reviewed = datetime.now()
            # 简单的掌握度计算：practice_count的对数函数
            import math
            existing.mastery_level = min(1.0, math.log(existing.practice_count + 1) / 5)
            existing.difficulty_rating = grammar_data['difficulty']
        else:
            # 创建新记录
            new_progress = LearningProgress(
                id=str(uuid.uuid4()),
                grammar_point=point,
                practice_count=1,
                mastery_level=0.1,
                difficulty_rating=grammar_data['difficulty'],
                agent_source=grammar_data['source_agent']
            )
            self.session.add(new_progress)

        self.session.commit()

    def _update_vocabulary_progress(self, vocab_data: Dict):
        """更新词汇学习进度"""
        word = vocab_data['word']

        # 查找现有记录
        existing = self.session.query(VocabularyProgress).filter(
            and_(
                VocabularyProgress.user_id == 'demo_user',
                VocabularyProgress.word == word
            )
        ).first()

        if existing:
            existing.times_reviewed += 1
            # 简单的记忆强度计算
            existing.mastery_score = min(1.0, existing.times_reviewed * 0.1)
        else:
            # 创建新词汇记录
            new_vocab = VocabularyProgress(
                id=str(uuid.uuid4()),
                word=word,
                meaning='',  # 可以后续补充
                times_reviewed=1,
                mastery_score=0.1,
                agent_source=vocab_data['source_agent']
            )
            self.session.add(new_vocab)

        self.session.commit()

    def _update_cultural_knowledge(self, cultural_data: Dict):
        """更新文化知识"""
        topic = cultural_data['topic']

        existing = self.session.query(CulturalKnowledge).filter(
            and_(
                CulturalKnowledge.user_id == 'demo_user',
                CulturalKnowledge.topic == topic
            )
        ).first()

        if existing:
            existing.understanding_level = min(1.0, existing.understanding_level + 0.1)
        else:
            new_cultural = CulturalKnowledge(
                id=str(uuid.uuid4()),
                topic=topic,
                content_summary=cultural_data['content'],
                learned_from_agent=cultural_data['source_agent'],
                understanding_level=0.1
            )
            self.session.add(new_cultural)

        self.session.commit()

    def _update_user_stats(self):
        """更新用户统计数据"""
        # 获取或创建用户统计记录
        user_stats = self.session.query(UserStats).filter(
            UserStats.user_id == 'demo_user'
        ).first()

        if not user_stats:
            user_stats = UserStats(
                id=str(uuid.uuid4()),
                user_id='demo_user'
            )
            self.session.add(user_stats)

        # 更新统计数据
        user_stats.total_conversations = self.session.query(ConversationLearning).filter(
            ConversationLearning.user_id == 'demo_user'
        ).count()

        user_stats.total_vocabulary = self.session.query(VocabularyProgress).filter(
            VocabularyProgress.user_id == 'demo_user'
        ).count()

        user_stats.total_grammar_points = self.session.query(LearningProgress).filter(
            LearningProgress.user_id == 'demo_user'
        ).count()

        # 计算经验值（简单算法）
        user_stats.total_xp = (
                user_stats.total_conversations * 10 +
                user_stats.total_vocabulary * 5 +
                user_stats.total_grammar_points * 15
        )

        # 计算等级（每500XP升一级）
        user_stats.level = max(1, user_stats.total_xp // 500 + 1)

        user_stats.last_active = datetime.now()

        self.session.commit()

    def get_user_progress_summary(self, user_id: str = 'demo_user') -> Dict:
        """获取用户学习进度摘要"""
        # 用户统计
        user_stats = self.session.query(UserStats).filter(
            UserStats.user_id == user_id
        ).first()

        if not user_stats:
            return self._get_empty_progress()

        # 语法进度
        grammar_progress = self.session.query(LearningProgress).filter(
            LearningProgress.user_id == user_id
        ).all()

        # 词汇进度
        vocab_progress = self.session.query(VocabularyProgress).filter(
            VocabularyProgress.user_id == user_id
        ).all()

        # 文化知识
        cultural_progress = self.session.query(CulturalKnowledge).filter(
            CulturalKnowledge.user_id == user_id
        ).all()

        # 计算平均掌握度
        avg_grammar_mastery = sum(g.mastery_level for g in grammar_progress) / len(
            grammar_progress) if grammar_progress else 0
        avg_vocab_mastery = sum(v.mastery_score for v in vocab_progress) / len(vocab_progress) if vocab_progress else 0
        avg_cultural_understanding = sum(c.understanding_level for c in cultural_progress) / len(
            cultural_progress) if cultural_progress else 0

        return {
            'user_stats': {
                'level': user_stats.level,
                'total_xp': user_stats.total_xp,
                'streak_days': user_stats.streak_days,
                'current_level': user_stats.current_level
            },
            'skills': {
                'vocabulary': {
                    'count': len(vocab_progress),
                    'mastery': avg_vocab_mastery,
                    'percentage': int(avg_vocab_mastery * 100)
                },
                'grammar': {
                    'count': len(grammar_progress),
                    'mastery': avg_grammar_mastery,
                    'percentage': int(avg_grammar_mastery * 100)
                },
                'cultural': {
                    'count': len(cultural_progress),
                    'understanding': avg_cultural_understanding,
                    'percentage': int(avg_cultural_understanding * 100)
                },
                'conversation': {
                    'count': user_stats.total_conversations,
                    'percentage': min(100, user_stats.total_conversations * 2)  # 简单计算
                }
            },
            'weak_points': self._identify_weak_points(grammar_progress, vocab_progress),
            'recommendations': self._generate_recommendations(user_stats, grammar_progress, vocab_progress)
        }

    def _get_empty_progress(self) -> Dict:
        """返回空的进度数据"""
        return {
            'user_stats': {'level': 1, 'total_xp': 0, 'streak_days': 0, 'current_level': 'beginner'},
            'skills': {
                'vocabulary': {'count': 0, 'mastery': 0, 'percentage': 0},
                'grammar': {'count': 0, 'mastery': 0, 'percentage': 0},
                'cultural': {'count': 0, 'understanding': 0, 'percentage': 0},
                'conversation': {'count': 0, 'percentage': 0}
            },
            'weak_points': [],
            'recommendations': [{'priority': 'high', 'title': '开始学习', 'description': '开始你的日语学习之旅吧！'}]
        }

    def _identify_weak_points(self, grammar_progress: List, vocab_progress: List) -> List[str]:
        """识别薄弱环节"""
        weak_points = []

        # 掌握度低于0.3的语法点
        weak_grammar = [g.grammar_point for g in grammar_progress if g.mastery_level < 0.3]
        if weak_grammar:
            weak_points.extend(weak_grammar[:3])  # 最多显示3个

        # 记忆强度低的词汇
        weak_vocab = len([v for v in vocab_progress if v.mastery_score < 0.3])
        if weak_vocab > 10:
            weak_points.append('词汇记忆')

        return weak_points

    def _generate_recommendations(self, user_stats, grammar_progress: List, vocab_progress: List) -> List[Dict]:
        """生成学习建议"""
        recommendations = []

        # 基于数据生成建议
        if len(vocab_progress) < 50:
            recommendations.append({
                'priority': 'high',
                'title': '扩展词汇量',
                'description': f'你目前掌握了{len(vocab_progress)}个词汇，建议增加到50个以上。'
            })

        if len(grammar_progress) < 20:
            recommendations.append({
                'priority': 'medium',
                'title': '加强语法学习',
                'description': f'你已学习{len(grammar_progress)}个语法点，继续保持！'
            })

        if user_stats.total_conversations < 10:
            recommendations.append({
                'priority': 'medium',
                'title': '增加对话练习',
                'description': '多与智能体对话可以提高你的实际应用能力。'
            })

        return recommendations[:3]  # 最多返回3个建议