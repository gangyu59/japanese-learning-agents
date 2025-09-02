# core/workflows/grammar_workflows.py
"""
Enhanced Grammar Collaboration Workflows
增强版语法协作工作流 - 基于现有架构扩展
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# 导入协作编排器
from .collaboration import MultiAgentOrchestrator, CollaborationMode


class GrammarCollaborationWorkflows:
    """语法协作工作流集合"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.orchestrator = MultiAgentOrchestrator()

    async def collaborative_grammar_correction(
            self,
            user_input: str,
            session_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        协作语法纠错工作流

        多个智能体按专业领域依次分析和纠正用户的日语输入
        """

        self.logger.info(f"开始协作语法纠错: {user_input}")

        # 选择参与纠错的智能体 - 按专业程度排序
        correction_agents = ["tanaka", "yamada", "koumi", "ai"]  # 语法->文化->口语->分析

        # 使用纠错模式进行协作
        result = await self.orchestrator.orchestrate_collaboration(
            user_input=user_input,
            active_agents=correction_agents,
            mode=CollaborationMode.CORRECTION,
            session_context={
                **session_context,
                "workflow_type": "grammar_correction",
                "correction_focus": ["grammar", "syntax", "naturalness", "cultural_appropriateness"]
            }
        )

        # 整合纠错结果
        corrections = self._extract_grammar_corrections(result.responses)

        return {
            "type": "collaborative_grammar_correction",
            "original_input": user_input,
            "corrections": corrections,
            "agents_participated": correction_agents,
            "final_recommendation": result.final_recommendation,
            "confidence_score": self._calculate_correction_confidence(result.responses),
            "learning_points": self._extract_learning_points(result.responses),
            "session_id": session_context.get("session_id")
        }

    async def grammar_explanation_discussion(
            self,
            grammar_point: str,
            user_question: str,
            session_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        语法点解释讨论工作流

        多个智能体从不同角度解释同一个语法点
        """

        self.logger.info(f"开始语法点讨论: {grammar_point}")

        # 让不同智能体从不同角度解释
        discussion_agents = ["tanaka", "yamada", "koumi", "sato"]

        enhanced_question = f"请解释日语语法点「{grammar_point}」: {user_question}"

        result = await self.orchestrator.orchestrate_collaboration(
            user_input=enhanced_question,
            active_agents=discussion_agents,
            mode=CollaborationMode.ANALYSIS,
            session_context={
                **session_context,
                "workflow_type": "grammar_explanation",
                "grammar_point": grammar_point,
                "analysis_focus": "comprehensive_explanation"
            }
        )

        # 整合解释结果
        explanations = self._organize_grammar_explanations(result.responses, grammar_point)

        return {
            "type": "grammar_explanation_discussion",
            "grammar_point": grammar_point,
            "user_question": user_question,
            "explanations": explanations,
            "comprehensive_summary": result.final_recommendation,
            "agents_participated": discussion_agents,
            "conflicting_views": result.conflicts,
            "session_id": session_context.get("session_id")
        }

    async def sentence_building_collaboration(
            self,
            target_grammar: str,
            context_hint: str,
            session_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        造句协作工作流

        多个智能体协作帮助用户构建使用特定语法的句子
        """

        self.logger.info(f"开始造句协作: {target_grammar}")

        creation_agents = ["tanaka", "koumi", "yamada"]  # 语法专家+对话专家+文化专家

        creation_prompt = f"请帮助用户使用语法「{target_grammar}」造句。上下文提示: {context_hint}"

        result = await self.orchestrator.orchestrate_collaboration(
            user_input=creation_prompt,
            active_agents=creation_agents,
            mode=CollaborationMode.CREATION,
            session_context={
                **session_context,
                "workflow_type": "sentence_building",
                "target_grammar": target_grammar,
                "context_hint": context_hint
            }
        )

        # 整合造句结果
        sentences = self._extract_example_sentences(result.responses, target_grammar)

        return {
            "type": "sentence_building_collaboration",
            "target_grammar": target_grammar,
            "context_hint": context_hint,
            "example_sentences": sentences,
            "step_by_step_guidance": result.final_recommendation,
            "agents_participated": creation_agents,
            "session_id": session_context.get("session_id")
        }

    async def grammar_comparison_analysis(
            self,
            grammar_points: List[str],
            user_confusion: str,
            session_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        语法对比分析工作流

        当用户对相似语法点感到困惑时，多智能体协作进行对比分析
        """

        self.logger.info(f"开始语法对比分析: {grammar_points}")

        analysis_agents = ["tanaka", "ai", "yamada", "sato"]  # 全方位分析

        comparison_prompt = f"请对比分析这些语法点的区别: {', '.join(grammar_points)}。用户困惑: {user_confusion}"

        result = await self.orchestrator.orchestrate_collaboration(
            user_input=comparison_prompt,
            active_agents=analysis_agents,
            mode=CollaborationMode.ANALYSIS,
            session_context={
                **session_context,
                "workflow_type": "grammar_comparison",
                "compared_grammar": grammar_points,
                "user_confusion": user_confusion
            }
        )

        # 整合对比分析结果
        comparison = self._structure_grammar_comparison(result.responses, grammar_points)

        return {
            "type": "grammar_comparison_analysis",
            "compared_grammar": grammar_points,
            "user_confusion": user_confusion,
            "detailed_comparison": comparison,
            "summary": result.final_recommendation,
            "memory_tips": self._extract_memory_tips(result.responses),
            "agents_participated": analysis_agents,
            "session_id": session_context.get("session_id")
        }

    def _extract_grammar_corrections(self, responses) -> List[Dict[str, Any]]:
        """从响应中提取语法纠错信息"""
        corrections = []

        for resp in responses:
            if resp.suggestions:
                for suggestion in resp.suggestions:
                    corrections.append({
                        "corrector": resp.agent_name,
                        "correction": suggestion,
                        "confidence": resp.confidence,
                        "category": self._categorize_correction(suggestion)
                    })

        return corrections

    def _categorize_correction(self, correction: str) -> str:
        """分类纠错类型"""
        correction_lower = correction.lower()

        if any(word in correction_lower for word in ["助词", "は", "を", "に", "が"]):
            return "助词"
        elif any(word in correction_lower for word in ["动词", "时态", "敬语"]):
            return "动词变形"
        elif any(word in correction_lower for word in ["语序", "位置"]):
            return "语序"
        elif any(word in correction_lower for word in ["自然", "口语", "表达"]):
            return "自然性"
        else:
            return "其他"

    def _calculate_correction_confidence(self, responses) -> float:
        """计算纠错的总体置信度"""
        if not responses:
            return 0.0

        total_confidence = sum(resp.confidence for resp in responses)
        return total_confidence / len(responses)

    def _extract_learning_points(self, responses) -> List[str]:
        """提取学习要点"""
        all_points = []
        for resp in responses:
            all_points.extend(resp.learning_points)

        # 去重并返回前5个最重要的点
        unique_points = list(dict.fromkeys(all_points))  # 保持顺序的去重
        return unique_points[:5]

    def _organize_grammar_explanations(self, responses, grammar_point: str) -> Dict[str, Any]:
        """整理语法解释"""
        explanations = {
            "basic_explanation": "",
            "cultural_context": "",
            "usage_tips": "",
            "common_mistakes": "",
            "examples": []
        }

        for resp in responses:
            content = resp.content
            agent_name = resp.agent_name

            if "田中" in agent_name:  # 语法专家的基础解释
                explanations["basic_explanation"] = content
            elif "山田" in agent_name:  # 文化专家的背景解释
                explanations["cultural_context"] = content
            elif "小美" in agent_name:  # 对话专家的使用技巧
                explanations["usage_tips"] = content
            elif "佐藤" in agent_name:  # 考试专家的常见错误
                explanations["common_mistakes"] = content

            # 提取例句
            if resp.suggestions:
                explanations["examples"].extend(resp.suggestions)

        return explanations

    def _extract_example_sentences(self, responses, target_grammar: str) -> List[Dict[str, Any]]:
        """提取造句示例"""
        sentences = []

        for resp in responses:
            if resp.suggestions:
                for suggestion in resp.suggestions:
                    sentences.append({
                        "sentence": suggestion,
                        "creator": resp.agent_name,
                        "confidence": resp.confidence,
                        "explanation": self._extract_sentence_explanation(resp.content, suggestion)
                    })

        return sentences[:6]  # 最多6个例句

    def _extract_sentence_explanation(self, content: str, sentence: str) -> str:
        """提取句子解释"""
        # 简化的解释提取逻辑
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if sentence in line or any(char in line for char in sentence[:10]):
                # 找到句子所在行，返回下一行作为解释
                if i + 1 < len(lines):
                    return lines[i + 1].strip()
        return ""

    def _structure_grammar_comparison(self, responses, grammar_points: List[str]) -> Dict[str, Any]:
        """结构化语法对比结果"""
        comparison = {
            "differences": {},
            "similarities": [],
            "usage_contexts": {},
            "difficulty_ranking": []
        }

        for resp in responses:
            content = resp.content
            agent_name = resp.agent_name

            if "区别" in content or "不同" in content:
                comparison["differences"][agent_name] = content
            elif "相似" in content or "共同" in content:
                comparison["similarities"].append({
                    "agent": agent_name,
                    "similarity": content
                })

            # 提取使用场景
            if resp.suggestions:
                for grammar in grammar_points:
                    if grammar not in comparison["usage_contexts"]:
                        comparison["usage_contexts"][grammar] = []

                    for suggestion in resp.suggestions:
                        if grammar in suggestion:
                            comparison["usage_contexts"][grammar].append({
                                "context": suggestion,
                                "source": agent_name
                            })

        return comparison

    def _extract_memory_tips(self, responses) -> List[str]:
        """提取记忆技巧"""
        memory_tips = []

        for resp in responses:
            content = resp.content

            # 寻找包含记忆、技巧、窍门等关键词的内容
            if any(keyword in content for keyword in ["记住", "技巧", "窍门", "方法", "诀窍"]):
                # 提取相关句子
                sentences = content.split('。')
                for sentence in sentences:
                    if any(keyword in sentence for keyword in ["记住", "技巧", "窍门", "方法"]):
                        memory_tips.append(sentence.strip() + '。')

        return memory_tips[:3]  # 最多3个记忆技巧


# 具体的语法场景工作流实例

class SpecificGrammarScenarios:
    """特定语法场景的协作工作流"""

    def __init__(self):
        self.workflows = GrammarCollaborationWorkflows()

    async def handle_particle_confusion(self, user_input: str, session_context: Dict[str, Any]):
        """处理助词混淆问题"""
        return await self.workflows.collaborative_grammar_correction(user_input, {
            **session_context,
            "focus_area": "particles",
            "common_confusions": ["は vs が", "を vs に", "で vs から"]
        })

    async def handle_keigo_correction(self, user_input: str, session_context: Dict[str, Any]):
        """处理敬语纠错"""
        return await self.workflows.collaborative_grammar_correction(user_input, {
            **session_context,
            "focus_area": "keigo",
            "politeness_level": "business_formal"
        })

    async def handle_verb_conjugation(self, verb_form: str, session_context: Dict[str, Any]):
        """处理动词活用问题"""
        return await self.workflows.grammar_explanation_discussion(
            grammar_point=f"{verb_form}活用",
            user_question=f"请解释{verb_form}的活用规则和使用方法",
            session_context={
                **session_context,
                "focus_area": "verb_conjugation",
                "verb_form": verb_form
            }
        )

    async def compare_similar_expressions(self, expressions: List[str], session_context: Dict[str, Any]):
        """对比相似表达"""
        return await self.workflows.grammar_comparison_analysis(
            grammar_points=expressions,
            user_confusion="这些表达方式有什么区别？什么时候用哪个？",
            session_context=session_context
        )


# 工作流选择器

class GrammarWorkflowSelector:
    """语法工作流选择器 - 根据用户输入选择最合适的协作工作流"""

    def __init__(self):
        self.workflows = GrammarCollaborationWorkflows()
        self.scenarios = SpecificGrammarScenarios()

    async def select_and_execute_workflow(
            self,
            user_input: str,
            session_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """根据用户输入选择并执行最合适的语法协作工作流"""

        # 分析用户输入，选择合适的工作流
        workflow_type = self._analyze_input_type(user_input)

        if workflow_type == "correction_needed":
            return await self.workflows.collaborative_grammar_correction(user_input, session_context)

        elif workflow_type == "explanation_request":
            grammar_point = self._extract_grammar_point(user_input)
            return await self.workflows.grammar_explanation_discussion(
                grammar_point, user_input, session_context
            )

        elif workflow_type == "comparison_request":
            grammar_points = self._extract_comparison_points(user_input)
            return await self.workflows.grammar_comparison_analysis(
                grammar_points, user_input, session_context
            )

        elif workflow_type == "sentence_building":
            target_grammar = self._extract_target_grammar(user_input)
            return await self.workflows.sentence_building_collaboration(
                target_grammar, user_input, session_context
            )

        else:
            # 默认使用通用协作模式
            return await self.workflows.collaborative_grammar_correction(user_input, session_context)

    def _analyze_input_type(self, user_input: str) -> str:
        """分析输入类型"""
        input_lower = user_input.lower()

        # 检查是否是解释请求
        if any(word in input_lower for word in ["什么意思", "怎么用", "解释", "什么是"]):
            return "explanation_request"

        # 检查是否是对比请求
        elif any(word in input_lower for word in ["区别", "不同", "对比", "vs", "和...有什么"]):
            return "comparison_request"

        # 检查是否是造句请求
        elif any(word in input_lower for word in ["造句", "例句", "举例", "怎么说"]):
            return "sentence_building"

        # 默认认为需要纠错
        else:
            return "correction_needed"

    def _extract_grammar_point(self, user_input: str) -> str:
        """提取语法点"""
        # 简化的语法点提取逻辑
        common_grammar = ["て形", "ます形", "た形", "ない形", "ば条件", "と条件", "たら条件", "なら条件"]

        for grammar in common_grammar:
            if grammar in user_input:
                return grammar

        # 如果没找到特定语法点，返回输入的关键部分
        return user_input[:20]

    def _extract_comparison_points(self, user_input: str) -> List[str]:
        """提取对比点"""
        # 简化的对比点提取逻辑
        points = []

        # 寻找常见的对比模式
        if " vs " in user_input or " 和 " in user_input:
            parts = user_input.replace(" vs ", "|").replace(" 和 ", "|").split("|")
            points = [part.strip() for part in parts[:2]]

        return points if points else [user_input[:15], "相关语法"]

    def _extract_target_grammar(self, user_input: str) -> str:
        """提取目标语法"""
        # 寻找引号或特殊标记中的语法
        import re

        # 寻找「」或""中的内容
        matches = re.findall(r'[「『"](.*?)[」』"]', user_input)
        if matches:
            return matches[0]

        return user_input[:20]


# 导出主要类
__all__ = [
    'GrammarCollaborationWorkflows',
    'SpecificGrammarScenarios',
    'GrammarWorkflowSelector'
]