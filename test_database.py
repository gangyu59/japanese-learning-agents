# test_database.py
import sys
sys.path.append('src')

from data.repositories.progress_tracker import ProgressTracker

def test_database():
    print("测试数据库连接...")
    try:
        tracker = ProgressTracker()
        summary = tracker.get_user_progress_summary()
        print(f"✅ 数据库连接成功")
        print(f"当前进度: 等级{summary['user_stats']['level']}, "
              f"经验值{summary['user_stats']['total_xp']}")
        print(f"词汇数: {summary['skills']['vocabulary']['count']}")
        print(f"语法点: {summary['skills']['grammar']['count']}")
        return True
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

if __name__ == "__main__":
    test_database()