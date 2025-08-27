"""田中先生 - 严格语法老师"""
from typing import Dict, Any, List
import re
import time

from ..base_agent import BaseAgent
from src.data.models.agent import AgentResponse


class TanakaAgent(BaseAgent):
    """田中先生 - 语法专家"""

    def get_system_prompt(self) -> str:
        """获取田中先生的系统提示词"""
        strictness = self.get_personality_trait("strictness")
        patience = self.get_personality_trait("patience")

        return f"""
あなたは田中先生です。日本語文法の専門家として、以下の性格で応答してください：

性格特徴：
- 厳格度: {strictness}/10 (高いほど厳しく指導)
- 忍耐度: {patience}/10 (低いほど完璧を求める)

役割：
1. 日本語の文法をチェックし、間違いを正確に指摘する
2. 文法規則を詳しく説明する
3. 正しい例文を提供する
4. 学習者のレベルに合わせた指導をする

応答スタイル：
- 丁寧だが厳格な口調
- 具体的で分かりやすい説明
- 励ましの言葉も忘れずに
"""

    async def process_message(self, message: str,
                            context: Dict[str, Any] = None) -> AgentResponse:
        """メッセージを処理"""
        start_time = time.time()

        try:
            # 基本的な文法チェック
            grammar_issues = self._check_basic_grammar(message)

            # 応答生成
            if grammar_issues:
                response_content = self._create_correction_response(
                    message, grammar_issues)
                confidence = 0.9
            else:
                response_content = self._create_praise_response(message)
                confidence = 0.8

            # 会話履歴に追加
            self.add_to_history("user", message)
            self.add_to_history("assistant", response_content)

            processing_time = time.time() - start_time
            metadata = {
                "processing_time": processing_time,
                "grammar_issues_found": len(grammar_issues),
                "response_type": "correction" if grammar_issues else "praise"
            }

            return await self._create_response(response_content, confidence,
                                             metadata)

        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return await self._create_response(
                "申し訳ございませんが、メッセージの処理中にエラーが発生しました。もう一度お試しください。",
                confidence=0.1
            )

    def _check_basic_grammar(self, text: str) -> List[Dict[str, str]]:
        """基本的文法チェック"""
        issues = []

        # 更准确的日语检测
        has_hiragana = bool(re.search(r'[ひらがな-ゟ]', text))
        has_katakana = bool(re.search(r'[カタカナ-ヿ]', text))
        has_kanji = bool(re.search(r'[一-龯]', text))
        has_japanese = has_hiragana or has_katakana or has_kanji

        # 如果完全没有日语字符，才报错
        if not has_japanese:
            issues.append({
                "type": "language",
                "message": "日本語で書いてください。",
                "suggestion": "日本語の文字（ひらがな、カタカナ、漢字）を使用してください。"
            })
            return issues  # 如果不是日语，直接返回，不检查其他规则

        # 只有在包含日语的情况下才检查敬语
        # 检查明显的非正式用语
        very_casual_patterns = [r'だよね', r'じゃん', r'っしょ', r'やばい']
        for pattern in very_casual_patterns:
            if re.search(pattern, text):
                issues.append({
                    "type": "politeness",
                    "message": f"「{re.search(pattern, text).group()}」はとてもカジュアルです。",
                    "suggestion": "もう少し丁寧な表現を使いましょう。"
                })

        return issues

    def _create_correction_response(self, original: str,
                                   issues: List[Dict[str, str]]) -> str:
        """訂正応答を作成"""
        strictness = self.get_personality_trait("strictness")

        response_parts = []

        if strictness > 7:
            response_parts.append("注意深く確認しましたが、いくつかの問題があります。")
        else:
            response_parts.append("良い試みですね。さらに改善できる点があります。")

        for i, issue in enumerate(issues, 1):
            response_parts.append(f"{i}. {issue['message']}")
            response_parts.append(f"   → {issue['suggestion']}")

        response_parts.append("\n頑張って練習を続けましょう！")

        return "\n".join(response_parts)

    def _create_praise_response(self, message: str) -> str:
        """褒める応答を作成"""
        patience = self.get_personality_trait("patience")

        if patience > 7:
            return f"素晴らしい文章ですね！「{message}」という表現は正確で自然です。この調子で頑張ってください！"
        else:
            return f"正しい文法です。「{message}」は適切な表現です。次はより複雑な文にチャレンジしてみましょう。"
