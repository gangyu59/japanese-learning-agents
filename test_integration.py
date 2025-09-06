# test_integration.py
import sys

sys.path.append('src')

from data.repositories.progress_tracker import ProgressTracker


def test_chat_integration():
    print("测试聊天集成...")

    tracker = ProgressTracker()

    # 模拟多轮对话
    conversations = [
        {
            "user": "こんにちは、元気ですか？",
            "agents": {
                "小美": {
                    "content": "元気です！こんにちはは基本的な挨拶ですね。",
                    "agent_name": "小美"
                }
            }
        },
        {
            "user": "昨日、図書館で本を読みました",
            "agents": {
                "田中先生": {
                    "content": "いい文章ですね！「で」は場所を表す助詞として正しく使われています。",
                    "agent_name": "田中先生"
                }
            }
        },
        {
            "user": "日本の茶道について教えてください",
            "agents": {
                "山田先生": {
                    "content": "茶道は日本の伝統文化の一つです。和の心を表現する美しい文化です。",
                    "agent_name": "山田先生"
                }
            }
        }
    ]

    for i, conv in enumerate(conversations, 1):
        print(f"\n对话 {i}:")
        print(f"用户: {conv['user']}")

        learning_data = tracker.extract_learning_data(
            user_input=conv['user'],
            agent_responses=conv['agents'],
            session_id=f"integration_test_{i}",
            scene_context="test_conversation"
        )

        for agent_name in conv['agents']:
            print(f"{agent_name}: {conv['agents'][agent_name]['content']}")

        print(f"学习数据: 语法{len(learning_data.get('grammar_points', []))}个, "
              f"词汇{len(learning_data.get('vocabulary', []))}个")

    # 查看最终进度
    summary = tracker.get_user_progress_summary()
    print(f"\n最终进度统计:")
    print(f"等级: {summary['user_stats']['level']}")
    print(f"总经验值: {summary['user_stats']['total_xp']}")
    print(f"对话次数: {summary['skills']['conversation']['count']}")
    print(f"词汇总数: {summary['skills']['vocabulary']['count']}")
    print(f"语法点: {summary['skills']['grammar']['count']}")
    print(f"文化知识: {summary['skills']['cultural']['count']}")


if __name__ == "__main__":
    test_chat_integration()