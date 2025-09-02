# backend/services/learning_service.py
"""
Learning Service Layer
学习服务层 - 处理学习进度、分析和推荐
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json
import statistics

# 数据库相关导入
try:
    from ..database.models import (
        DatabaseManager, User, LearningProgress, VocabularyProgress,
        ConversationHistory, LearningSession, MemoryCard, StudyPlan
    )
    from sqlalchemy.orm import Session
    from sqlalchemy import func, and_, or_

    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False


@dataclass
class LearningStats:
    """学习统计数据结构"""
    total_sessions: int
    total_duration_minutes: int
    average_session_duration: float
    learning_points_mastered: int
    vocabulary_learned: int
    grammar_points_practiced: int
    satisfaction_score: float
    progress_percentage: float


@dataclass
class WeakArea:
    """薄弱环节数据结构"""
    area_name: str
    error_count: int
    success_rate: float
    last_practiced: datetime
    recommendations: List[str]


class LearningAnalyticsService:
    """学习分析服务"""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.logger = logging.getLogger(__name__)
        self.db_manager = db_manager

        # 如果没有数据库，使用内存缓存
        self.memory_cache = {}

    async def get_learning_stats(self, user_id: str, days: int = 30) -> LearningStats:
        """获取用户学习统计数据"""

        if self.db_manager:
            return await self._get_stats_from_db(user_id, days)
        else:
            return await self._get_stats_from_cache(user_id, days)

    async def _get_stats_from_db(self, user_id: str, days: int) -> LearningStats:
        """从数据库获取学习统计"""

        try:
            with self.db_manager.get_session() as session:
                # 获取指定天数内的学习会话
                cutoff_date = datetime.now() - timedelta(days=days)

                sessions = session.query(LearningSession).filter(
                    and_(
                        LearningSession.user_id == user_id,
                        LearningSession.start_time >= cutoff_date
                    )
                ).all()

                if not sessions:
                    return LearningStats(0, 0, 0.0, 0, 0, 0, 0.0, 0.0)

                # 计算基础统计
                total_sessions = len(sessions)
                total_duration = sum(s.duration_minutes or 0 for s in sessions)
                avg_duration = total_duration / total_sessions if total_sessions > 0 else 0

                # 计算学习内容统计
                all_learning_points = []
                all_vocabulary = []
                all_grammar_points = []
                satisfaction_scores = []

                for session in sessions:
                    if session.learning_points_covered:
                        all_learning_points.extend(session.learning_points_covered)
                    if session.vocabulary_learned:
                        all_vocabulary.extend(session.vocabulary_learned)
                    if session.grammar_points_practiced:
                        all_grammar_points.extend(session.grammar_points_practiced)
                    if session.satisfaction_score:
                        satisfaction_scores.append(session.satisfaction_score)

                # 去重计算唯一学习点
                unique_learning_points = len(set(all_learning_points))
                unique_vocabulary = len(set(all_vocabulary))
                unique_grammar = len(set(all_grammar_points))
                avg_satisfaction = statistics.mean(satisfaction_scores) if satisfaction_scores else 0.0

                # 计算进度百分比 (基于目标)
                user = session.query(User).filter(User.user_id == user_id).first()
                progress_percentage = await self._calculate_progress_percentage(user, session)

                return LearningStats(
                    total_sessions=total_sessions,
                    total_duration_minutes=total_duration,
                    average_session_duration=avg_duration,
                    learning_points_mastered=unique_learning_points,
                    vocabulary_learned=unique_vocabulary,
                    grammar_points_practiced=unique_grammar,
                    satisfaction_score=avg_satisfaction,
                    progress_percentage=progress_percentage
                )

        except Exception as e:
            self.logger.error(f"数据库统计查询错误: {str(e)}")
            return LearningStats(0, 0, 0.0, 0, 0, 0, 0.0, 0.0)

    async def _get_stats_from_cache(self, user_id: str, days: int) -> LearningStats:
        """从缓存获取学习统计"""
        # 简化的缓存实现
        user_data = self.memory_cache.get(user_id, {})
        sessions = user_data.get('sessions', [])

        # 过滤最近几天的会话
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_sessions = [
            s for s in sessions
            if datetime.fromisoformat(s.get('timestamp', '')) >= cutoff_date
        ]

        if not recent_sessions:
            return LearningStats(0, 0, 0.0, 0, 0, 0, 0.0, 0.0)

        total_sessions = len(recent_sessions)
        total_duration = sum(s.get('duration', 0) for s in recent_sessions)
        avg_duration = total_duration / total_sessions if total_sessions > 0 else 0

        return LearningStats(
            total_sessions=total_sessions,
            total_duration_minutes=total_duration,
            average_session_duration=avg_duration,
            learning_points_mastered=total_sessions * 2,  # 估算
            vocabulary_learned=total_sessions * 3,  # 估算
            grammar_points_practiced=total_sessions * 1,  # 估算
            satisfaction_score=4.0,  # 默认值
            progress_percentage=min(total_sessions * 2, 100)  # 简单估算
        )

    async def _calculate_progress_percentage(self, user, session) -> float:
        """计算学习进度百分比"""

        if not user or not user.target_jlpt_level:
            return 0.0

        # JLPT级别要求 (简化版本)
        jlpt_requirements = {
            'N5': {'vocab': 800, 'grammar': 80, 'kanji': 100},
            'N4': {'vocab': 1500, 'grammar': 150, 'kanji': 300},
            'N3': {'vocab': 3000, 'grammar': 250, 'kanji': 650},
            'N2': {'vocab': 6000, 'grammar': 400, 'kanji': 1000},
            'N1': {'vocab': 10000, 'grammar': 600, 'kanji': 2000}
        }

        requirements = jlpt_requirements.get(user.target_jlpt_level, jlpt_requirements['N5'])

        # 查询用户当前掌握情况
        vocab_count = session.query(VocabularyProgress).filter(
            and_(
                VocabularyProgress.user_id == user.user_id,
                VocabularyProgress.mastery_score >= 0.7
            )
        ).count()

        grammar_count = session.query(LearningProgress).filter(
            and_(
                LearningProgress.user_id == user.user_id,
                LearningProgress.mastery_level >= 0.7
            )
        ).count()

        # 计算完成百分比
        vocab_progress = min(vocab_count / requirements['vocab'], 1.0) * 40  # 40%权重
        grammar_progress = min(grammar_count / requirements['grammar'], 1.0) * 40  # 40%权重
        time_progress = 0.2  # 20%权重 - 简化为时间投入

        return vocab_progress + grammar_progress + (time_progress * 20)

    async def identify_weak_areas(self, user_id: str, limit: int = 5) -> List[WeakArea]:
        """识别学习薄弱环节"""

        if self.db_manager:
            return await self._identify_weak_areas_from_db(user_id, limit)
        else:
            return await self._identify_weak_areas_from_cache(user_id, limit)

    async def _identify_weak_areas_from_db(self, user_id: str, limit: int) -> List[WeakArea]:
        """从数据库识别薄弱环节"""

        try:
            with self.db_manager.get_session() as session:
                # 分析学习进度中的薄弱环节
                weak_progress = session.query(LearningProgress).filter(
                    and_(
                        LearningProgress.user_id == user_id,
                        LearningProgress.mastery_level < 0.6,  # 掌握度低于60%
                        LearningProgress.practice_count > 2  # 练习过至少3次
                    )
                ).order_by(LearningProgress.mastery_level.asc()).limit(limit).all()

                weak_areas = []
                for progress in weak_progress:
                    success_rate = progress.correct_answers / max(progress.practice_count, 1)

                    recommendations = self._generate_recommendations_for_grammar(progress.grammar_point)

                    weak_areas.append(WeakArea(
                        area_name=progress.grammar_point,
                        error_count=progress.practice_count - progress.correct_answers,
                        success_rate=success_rate,
                        last_practiced=progress.last_reviewed,
                        recommendations=recommendations
                    ))

                # 分析词汇薄弱环节
                weak_vocab = session.query(VocabularyProgress).filter(
                    and_(
                        VocabularyProgress.user_id == user_id,
                        VocabularyProgress.mastery_score < 0.6,
                        VocabularyProgress.times_reviewed > 2
                    )
                ).order_by(VocabularyProgress.mastery_score.asc()).limit(limit - len(weak_areas)).all()

                for vocab in weak_vocab:
                    success_rate = vocab.times_correct / max(vocab.times_reviewed, 1)

                    recommendations = self._generate_recommendations_for_vocabulary(vocab.word)

                    weak_areas.append(WeakArea(
                        area_name=f"词汇: {vocab.word}",
                        error_count=vocab.times_reviewed - vocab.times_correct,
                        success_rate=success_rate,
                        last_practiced=vocab.created_at,  # 简化处理
                        recommendations=recommendations
                    ))

                return weak_areas[:limit]

        except Exception as e:
            self.logger.error(f"薄弱环节分析错误: {str(e)}")
            return []

    async def _identify_weak_areas_from_cache(self, user_id: str, limit: int) -> List[WeakArea]:
        """从缓存识别薄弱环节"""
        # 简化的缓存实现
        user_data = self.memory_cache.get(user_id, {})
        errors = user_data.get('common_errors', [])

        weak_areas = []
        for i, error in enumerate(errors[:limit]):
            weak_areas.append(WeakArea(
                area_name=error,
                error_count=3,  # 估算
                success_rate=0.4,  # 估算
                last_practiced=datetime.now() - timedelta(days=i + 1),
                recommendations=[f"加强{error}的练习", f"查看{error}的相关例句"]
            ))

        return weak_areas

    def _generate_recommendations_for_grammar(self, grammar_point: str) -> List[str]:
        """为语法点生成建议"""
        base_recommendations = [
            f"重点复习{grammar_point}的基本用法",
            f"寻找更多{grammar_point}的例句练习",
            f"在实际对话中使用{grammar_point}",
            f"对比{grammar_point}与相似语法点的区别"
        ]

        # 根据语法点类型添加特定建议
        if "助词" in grammar_point:
            base_recommendations.append("练习助词在不同语境中的用法")
        elif "动词" in grammar_point:
            base_recommendations.append("练习动词变形的规则")
        elif "敬语" in grammar_point:
            base_recommendations.append("了解敬语使用的社交场合")

        return base_recommendations[:3]  # 最多返回3个建议

    def _generate_recommendations_for_vocabulary(self, word: str) -> List[str]:
        """为词汇生成建议"""
        return [
                   f"使用{word}造句练习",
                   f"查找{word}的同义词和反义词",
                   f"在对话中主动使用{word}",
                   f"了解{word}的文化背景和使用场合"
               ][:3]

    async def get_learning_trends(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """获取学习趋势分析"""

        if self.db_manager:
            return await self._get_trends_from_db(user_id, days)
        else:
            return await self._get_trends_from_cache(user_id, days)

    async def _get_trends_from_db(self, user_id: str, days: int) -> Dict[str, Any]:
        """从数据库获取学习趋势"""

        try:
            with self.db_manager.get_session() as session:
                cutoff_date = datetime.now() - timedelta(days=days)

                # 按天分组获取学习数据
                daily_sessions = session.query(
                    func.date(LearningSession.start_time).label('date'),
                    func.count(LearningSession.session_id).label('session_count'),
                    func.sum(LearningSession.duration_minutes).label('total_duration'),
                    func.avg(LearningSession.satisfaction_score).label('avg_satisfaction')
                ).filter(
                    and_(
                        LearningSession.user_id == user_id,
                        LearningSession.start_time >= cutoff_date
                    )
                ).group_by(func.date(LearningSession.start_time)).all()

                # 处理数据
                dates = []
                session_counts = []
                durations = []
                satisfactions = []

                for record in daily_sessions:
                    dates.append(record.date.isoformat())
                    session_counts.append(record.session_count)
                    durations.append(record.total_duration or 0)
                    satisfactions.append(float(record.avg_satisfaction) if record.avg_satisfaction else 0)

                # 计算趋势
                trend_analysis = self._calculate_trends(session_counts, durations, satisfactions)

                return {
                    "dates": dates,
                    "session_counts": session_counts,
                    "durations": durations,
                    "satisfactions": satisfactions,
                    "trends": trend_analysis,
                    "total_days": len(dates),
                    "active_days": len([c for c in session_counts if c > 0])
                }

        except Exception as e:
            self.logger.error(f"趋势分析错误: {str(e)}")
            return {"error": str(e)}

    async def _get_trends_from_cache(self, user_id: str, days: int) -> Dict[str, Any]:
        """从缓存获取学习趋势"""
        # 简化的趋势分析
        return {
            "dates": [(datetime.now() - timedelta(days=i)).date().isoformat() for i in range(7)],
            "session_counts": [1, 2, 1, 3, 2, 1, 2],
            "durations": [25, 45, 20, 60, 40, 15, 35],
            "satisfactions": [4.0, 4.5, 3.5, 4.8, 4.2, 3.8, 4.1],
            "trends": {
                "session_trend": "stable",
                "duration_trend": "improving",
                "satisfaction_trend": "stable"
            },
            "total_days": 7,
            "active_days": 7
        }

    def _calculate_trends(self, session_counts: List[int], durations: List[int], satisfactions: List[float]) -> Dict[
        str, str]:
        """计算趋势方向"""

        def get_trend(data: List[float]) -> str:
            if len(data) < 2:
                return "insufficient_data"

            # 简单的趋势计算：比较前半段和后半段的平均值
            mid = len(data) // 2
            first_half = statistics.mean(data[:mid]) if data[:mid] else 0
            second_half = statistics.mean(data[mid:]) if data[mid:] else 0

            if second_half > first_half * 1.1:
                return "improving"
            elif second_half < first_half * 0.9:
                return "declining"
            else:
                return "stable"

        return {
            "session_trend": get_trend([float(x) for x in session_counts]),
            "duration_trend": get_trend([float(x) for x in durations]),
            "satisfaction_trend": get_trend(satisfactions)
        }


class VocabularyService:
    """词汇管理服务"""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.logger = logging.getLogger(__name__)
        self.db_manager = db_manager
        self.memory_cache = {}

    async def add_vocabulary(
            self,
            user_id: str,
            word: str,
            reading: str,
            meaning: str,
            example_sentence: str = "",
            difficulty_level: int = 3
    ) -> bool:
        """添加新词汇到学习列表"""

        if self.db_manager:
            return await self._add_vocabulary_to_db(
                user_id, word, reading, meaning, example_sentence, difficulty_level
            )
        else:
            return await self._add_vocabulary_to_cache(
                user_id, word, reading, meaning, example_sentence, difficulty_level
            )

    async def _add_vocabulary_to_db(
            self, user_id: str, word: str, reading: str, meaning: str,
            example_sentence: str, difficulty_level: int
    ) -> bool:
        """添加词汇到数据库"""

        try:
            with self.db_manager.get_session() as session:
                # 检查是否已存在
                existing = session.query(VocabularyProgress).filter(
                    and_(
                        VocabularyProgress.user_id == user_id,
                        VocabularyProgress.word == word
                    )
                ).first()

                if existing:
                    # 更新现有记录
                    existing.reading = reading
                    existing.meaning = meaning
                    existing.example_sentence = example_sentence
                    existing.difficulty_level = difficulty_level
                else:
                    # 创建新记录
                    vocab = VocabularyProgress(
                        user_id=user_id,
                        word=word,
                        reading=reading,
                        meaning=meaning,
                        example_sentence=example_sentence,
                        difficulty_level=difficulty_level,
                        next_review=datetime.now() + timedelta(days=1)  # 明天复习
                    )
                    session.add(vocab)

                session.commit()
                return True

        except Exception as e:
            self.logger.error(f"添加词汇错误: {str(e)}")
            return False

    async def _add_vocabulary_to_cache(
            self, user_id: str, word: str, reading: str, meaning: str,
            example_sentence: str, difficulty_level: int
    ) -> bool:
        """添加词汇到缓存"""

        if user_id not in self.memory_cache:
            self.memory_cache[user_id] = []

        vocab_item = {
            "word": word,
            "reading": reading,
            "meaning": meaning,
            "example_sentence": example_sentence,
            "difficulty_level": difficulty_level,
            "times_reviewed": 0,
            "times_correct": 0,
            "mastery_score": 0.0,
            "next_review": (datetime.now() + timedelta(days=1)).isoformat()
        }

        # 检查是否已存在
        for i, existing in enumerate(self.memory_cache[user_id]):
            if existing["word"] == word:
                self.memory_cache[user_id][i] = vocab_item
                return True

        # 添加新词汇
        self.memory_cache[user_id].append(vocab_item)
        return True

    async def get_due_vocabulary(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """获取需要复习的词汇"""

        if self.db_manager:
            return await self._get_due_vocabulary_from_db(user_id, limit)
        else:
            return await self._get_due_vocabulary_from_cache(user_id, limit)

    async def _get_due_vocabulary_from_db(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        """从数据库获取待复习词汇"""

        try:
            with self.db_manager.get_session() as session:
                due_vocab = session.query(VocabularyProgress).filter(
                    and_(
                        VocabularyProgress.user_id == user_id,
                        VocabularyProgress.next_review <= datetime.now()
                    )
                ).order_by(VocabularyProgress.next_review.asc()).limit(limit).all()

                result = []
                for vocab in due_vocab:
                    result.append({
                        "vocab_id": str(vocab.vocab_id),
                        "word": vocab.word,
                        "reading": vocab.reading,
                        "meaning": vocab.meaning,
                        "example_sentence": vocab.example_sentence,
                        "difficulty_level": vocab.difficulty_level,
                        "mastery_score": vocab.mastery_score,
                        "times_reviewed": vocab.times_reviewed,
                        "next_review": vocab.next_review.isoformat()
                    })

                return result

        except Exception as e:
            self.logger.error(f"获取待复习词汇错误: {str(e)}")
            return []

    async def _get_due_vocabulary_from_cache(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        """从缓存获取待复习词汇"""

        user_vocab = self.memory_cache.get(user_id, [])
        now = datetime.now()

        due_vocab = []
        for vocab in user_vocab:
            next_review = datetime.fromisoformat(vocab["next_review"])
            if next_review <= now:
                due_vocab.append(vocab)

        # 按复习时间排序
        due_vocab.sort(key=lambda x: x["next_review"])
        return due_vocab[:limit]

    async def update_vocabulary_review(
            self,
            user_id: str,
            vocab_id: str,
            quality: int,  # 0-5, 5=perfect recall
            response_time: float = 0.0
    ) -> Dict[str, Any]:
        """更新词汇复习结果"""

        if self.db_manager:
            return await self._update_review_in_db(user_id, vocab_id, quality, response_time)
        else:
            return await self._update_review_in_cache(user_id, vocab_id, quality, response_time)

    async def _update_review_in_db(
            self, user_id: str, vocab_id: str, quality: int, response_time: float
    ) -> Dict[str, Any]:
        """在数据库中更新复习结果"""

        try:
            with self.db_manager.get_session() as session:
                vocab = session.query(VocabularyProgress).filter(
                    VocabularyProgress.vocab_id == vocab_id
                ).first()

                if not vocab:
                    return {"success": False, "error": "词汇不存在"}

                # 更新统计
                vocab.times_reviewed += 1
                if quality >= 3:
                    vocab.times_correct += 1

                # 更新掌握度 (使用简化算法)
                old_mastery = vocab.mastery_score
                adjustment = (quality - 2.5) / 10.0  # -0.25 to +0.25
                vocab.mastery_score = max(0.0, min(1.0, old_mastery + adjustment))

                # 计算下次复习间隔 (简化的SM-2算法)
                if quality >= 3:
                    vocab.ease_factor = max(1.3,
                                            vocab.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
                    if vocab.repetition_count == 0:
                        vocab.review_interval = 1
                    elif vocab.repetition_count == 1:
                        vocab.review_interval = 6
                    else:
                        vocab.review_interval = int(vocab.review_interval * vocab.ease_factor)
                    vocab.repetition_count += 1
                else:
                    vocab.repetition_count = 0
                    vocab.review_interval = 1
                    vocab.ease_factor = max(1.3, vocab.ease_factor - 0.2)

                # 设置下次复习时间
                vocab.next_review = datetime.now() + timedelta(days=vocab.review_interval)

                session.commit()

                return {
                    "success": True,
                    "new_mastery_score": vocab.mastery_score,
                    "next_review": vocab.next_review.isoformat(),
                    "review_interval": vocab.review_interval
                }

        except Exception as e:
            self.logger.error(f"更新复习结果错误: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _update_review_in_cache(
            self, user_id: str, vocab_id: str, quality: int, response_time: float
    ) -> Dict[str, Any]:
        """在缓存中更新复习结果"""

        user_vocab = self.memory_cache.get(user_id, [])

        for vocab in user_vocab:
            if vocab.get("vocab_id") == vocab_id or vocab["word"] == vocab_id:  # 兼容性处理
                # 更新统计
                vocab["times_reviewed"] += 1
                if quality >= 3:
                    vocab["times_correct"] += 1

                # 更新掌握度
                old_mastery = vocab["mastery_score"]
                adjustment = (quality - 2.5) / 10.0
                vocab["mastery_score"] = max(0.0, min(1.0, old_mastery + adjustment))

                # 计算下次复习间隔
                if quality >= 3:
                    interval = 1 if vocab["times_reviewed"] == 1 else min(vocab["times_reviewed"] * 2, 30)
                else:
                    interval = 1

                vocab["next_review"] = (datetime.now() + timedelta(days=interval)).isoformat()

                return {
                    "success": True,
                    "new_mastery_score": vocab["mastery_score"],
                    "next_review": vocab["next_review"],
                    "review_interval": interval
                }

        return {"success": False, "error": "词汇不存在"}


# 综合学习服务管理器
class LearningServiceManager:
    """学习服务管理器 - 统一管理所有学习相关服务"""

    def __init__(self, database_url: Optional[str] = None):
        self.logger = logging.getLogger(__name__)

        # 初始化数据库管理器
        if database_url and DATABASE_AVAILABLE:
            try:
                self.db_manager = DatabaseManager(database_url)
                self.db_manager.create_tables()
                self.logger.info("数据库连接成功")
            except Exception as e:
                self.logger.error(f"数据库连接失败: {str(e)}")
                self.db_manager = None
        else:
            self.db_manager = None
            self.logger.warning("使用内存缓存模式")

        # 初始化服务
        self.analytics = LearningAnalyticsService(self.db_manager)
        self.vocabulary = VocabularyService(self.db_manager)

    async def record_learning_session(
            self,
            user_id: str,
            session_type: str,
            duration_minutes: int,
            agents_used: List[str],
            learning_points: List[str],
            vocabulary_learned: List[str],
            grammar_practiced: List[str],
            satisfaction_score: int
    ) -> bool:
        """记录学习会话"""

        if self.db_manager:
            return await self._record_session_to_db(
                user_id, session_type, duration_minutes, agents_used,
                learning_points, vocabulary_learned, grammar_practiced, satisfaction_score
            )
        else:
            return await self._record_session_to_cache(
                user_id, session_type, duration_minutes, agents_used,
                learning_points, vocabulary_learned, grammar_practiced, satisfaction_score
            )

    async def _record_session_to_db(
            self, user_id: str, session_type: str, duration_minutes: int,
            agents_used: List[str], learning_points: List[str], vocabulary_learned: List[str],
            grammar_practiced: List[str], satisfaction_score: int
    ) -> bool:
        """记录会话到数据库"""

        try:
            with self.db_manager.get_session() as session:
                learning_session = LearningSession(
                    user_id=user_id,
                    session_type=session_type,
                    start_time=datetime.now() - timedelta(minutes=duration_minutes),
                    end_time=datetime.now(),
                    duration_minutes=duration_minutes,
                    learning_points_covered=learning_points,
                    vocabulary_learned=vocabulary_learned,
                    grammar_points_practiced=grammar_practiced,
                    agents_used=agents_used,
                    satisfaction_score=satisfaction_score
                )

                session.add(learning_session)
                session.commit()
                return True

        except Exception as e:
            self.logger.error(f"记录学习会话错误: {str(e)}")
            return False

    async def _record_session_to_cache(
            self, user_id: str, session_type: str, duration_minutes: int,
            agents_used: List[str], learning_points: List[str], vocabulary_learned: List[str],
            grammar_practiced: List[str], satisfaction_score: int
    ) -> bool:
        """记录会话到缓存"""

        if user_id not in self.analytics.memory_cache:
            self.analytics.memory_cache[user_id] = {"sessions": []}

        session_record = {
            "timestamp": datetime.now().isoformat(),
            "session_type": session_type,
            "duration": duration_minutes,
            "agents_used": agents_used,
            "learning_points": learning_points,
            "vocabulary_learned": vocabulary_learned,
            "grammar_practiced": grammar_practiced,
            "satisfaction_score": satisfaction_score
        }

        self.analytics.memory_cache[user_id]["sessions"].append(session_record)
        return True

    async def get_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """获取学习仪表板数据"""

        # 并行获取各种数据
        tasks = [
            self.analytics.get_learning_stats(user_id, 30),
            self.analytics.identify_weak_areas(user_id, 5),
            self.analytics.get_learning_trends(user_id, 14),
            self.vocabulary.get_due_vocabulary(user_id, 10)
        ]

        try:
            stats, weak_areas, trends, due_vocab = await asyncio.gather(*tasks)

            return {
                "user_id": user_id,
                "stats": {
                    "total_sessions": stats.total_sessions,
                    "total_duration_minutes": stats.total_duration_minutes,
                    "average_session_duration": stats.average_session_duration,
                    "learning_points_mastered": stats.learning_points_mastered,
                    "vocabulary_learned": stats.vocabulary_learned,
                    "grammar_points_practiced": stats.grammar_points_practiced,
                    "satisfaction_score": stats.satisfaction_score,
                    "progress_percentage": stats.progress_percentage
                },
                "weak_areas": [
                    {
                        "area_name": area.area_name,
                        "error_count": area.error_count,
                        "success_rate": area.success_rate,
                        "recommendations": area.recommendations
                    }
                    for area in weak_areas
                ],
                "trends": trends,
                "due_vocabulary": due_vocab,
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"获取仪表板数据错误: {str(e)}")
            return {"error": str(e)}


# 导出主要类
__all__ = [
    'LearningServiceManager', 'LearningAnalyticsService', 'VocabularyService',
    'LearningStats', 'WeakArea'
]