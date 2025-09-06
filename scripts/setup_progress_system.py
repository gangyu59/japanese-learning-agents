# scripts/setup_progress_system.py
"""
快速设置学习进度系统
运行此脚本来初始化进度追踪功能
"""

import os
import sys
import sqlite3
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


def setup_progress_system():
    """设置学习进度系统"""
    print("🚀 开始设置日语学习进度系统...")

    # 1. 检查并创建必要的目录
    create_directories()

    # 2. 初始化数据库
    init_database()

    # 3. 更新API路由注册
    update_api_routes()

    # 4. 创建前端资源文件
    create_frontend_assets()

    # 5. 验证设置
    verify_setup()

    print("✅ 学习进度系统设置完成！")
    print_usage_instructions()


def create_directories():
    """创建必要的目录结构"""
    print("📁 创建目录结构...")

    directories = [
        "src/data/repositories",
        "src/data/models",
        "frontend/assets/js",
        "database"
    ]

    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {dir_path}")


def init_database():
    """初始化SQLite数据库"""
    print("🗄️  初始化数据库...")

    try:
        # 直接使用SQLite创建表
        db_path = "database/japanese_learning.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 创建学习进度表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_progress (
                id TEXT PRIMARY KEY,
                user_id TEXT DEFAULT 'demo_user',
                grammar_point TEXT NOT NULL,
                mastery_level REAL DEFAULT 0.0,
                practice_count INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0,
                last_reviewed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                next_review TIMESTAMP,
                difficulty_rating REAL DEFAULT 0.5,
                agent_source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建词汇进度表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vocabulary_progress (
                id TEXT PRIMARY KEY,
                user_id TEXT DEFAULT 'demo_user',
                word TEXT NOT NULL,
                reading TEXT,
                meaning TEXT NOT NULL,
                example_sentence TEXT,
                difficulty_level INTEGER DEFAULT 1,
                review_interval INTEGER DEFAULT 1,
                next_review TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                mastery_score REAL DEFAULT 0.0,
                times_reviewed INTEGER DEFAULT 0,
                times_correct INTEGER DEFAULT 0,
                jlpt_level TEXT,
                agent_source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建对话学习记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_learning (
                id TEXT PRIMARY KEY,
                user_id TEXT DEFAULT 'demo_user',
                session_id TEXT NOT NULL,
                user_input TEXT,
                agent_responses TEXT,
                learning_points TEXT,
                corrections_made TEXT,
                participating_agents TEXT,
                scene_context TEXT DEFAULT 'general',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建用户统计表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_stats (
                id TEXT PRIMARY KEY,
                user_id TEXT DEFAULT 'demo_user',
                total_conversations INTEGER DEFAULT 0,
                total_vocabulary INTEGER DEFAULT 0,
                total_grammar_points INTEGER DEFAULT 0,
                current_level TEXT DEFAULT 'beginner',
                target_jlpt TEXT DEFAULT 'N5',
                streak_days INTEGER DEFAULT 0,
                total_xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建文化知识表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cultural_knowledge (
                id TEXT PRIMARY KEY,
                user_id TEXT DEFAULT 'demo_user',
                topic TEXT NOT NULL,
                subtopic TEXT,
                content_summary TEXT,
                learned_from_agent TEXT,
                understanding_level REAL DEFAULT 0.0,
                interest_rating REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

        print(f"   ✓ 数据库已创建: {db_path}")

    except Exception as e:
        print(f"   ❌ 数据库初始化失败: {e}")


def update_api_routes():
    """更新API路由注册"""
    print("🛣️  更新API路由...")

    # 检查主路由文件是否需要更新
    main_router_files = [
        "src/api/__init__.py",
        "src/main.py",
        "main.py"
    ]

    found_main_file = False
    for main_file in main_router_files:
        if Path(main_file).exists():
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查是否已经包含进度路由
            if 'progress' not in content:
                print(f"   ⚠️  请在 {main_file} 中手动添加进度路由")
                print("   导入: from api import progress")
                print("   注册: app.include_router(progress.router)")
                found_main_file = True
                break
            else:
                print(f"   ✓ 进度路由已存在于 {main_file}")
                found_main_file = True
                break

    if not found_main_file:
        print("   ⚠️  未找到主路由文件，请手动配置")


def create_frontend_assets():
    """创建前端资源文件"""
    print("🎨 创建前端资源...")

    # 检查是否需要创建progress_real.html
    progress_html_path = "frontend/progress_real.html"

    if not Path(progress_html_path).exists():
        progress_html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 真实学习进度 - 日语学习系统</title>
    <link rel="stylesheet" href="assets/css/main.css">
    <link rel="stylesheet" href="assets/css/progress.css">
</head>
<body>
    <div class="container">
        <div class="loading-indicator">🔄 加载学习数据中...</div>

        <!-- 进度内容将由JavaScript动态生成 -->
        <div id="progress-content" style="display: none;">
            <!-- 内容将由progress_real.js填充 -->
        </div>

        <!-- 刷新按钮 -->
        <button class="refresh-progress" onclick="window.progressManager && window.progressManager.refreshProgress()">🔄</button>
    </div>

    <script src="assets/js/progress_real.js"></script>
</body>
</html>'''

        with open(progress_html_path, 'w', encoding='utf-8') as f:
            f.write(progress_html_content)

        print(f"   ✓ 创建进度页面: {progress_html_path}")
    else:
        print(f"   ✓ 进度页面已存在: {progress_html_path}")


def verify_setup():
    """验证设置是否正确"""
    print("🔍 验证设置...")

    # 检查数据库文件
    db_path = "database/japanese_learning.db"
    if Path(db_path).exists():
        print("   ✓ 数据库文件存在")

        # 检查表结构
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()

        expected_tables = [
            'learning_progress', 'vocabulary_progress', 'conversation_learning',
            'user_stats', 'cultural_knowledge'
        ]

        existing_tables = [table[0] for table in tables]

        for table in expected_tables:
            if table in existing_tables:
                print(f"   ✓ 表 {table} 已创建")
            else:
                print(f"   ❌ 表 {table} 缺失")
    else:
        print("   ❌ 数据库文件不存在")

    # 检查核心文件结构
    core_files = [
        "src/data/models/learning.py",
        "src/data/repositories/progress_tracker.py",
        "src/api/progress.py",
        "frontend/assets/js/progress_real.js"
    ]

    print("\n   核心文件检查:")
    for file_path in core_files:
        if Path(file_path).exists():
            print(f"   ✓ {file_path}")
        else:
            print(f"   ❌ {file_path} 需要创建")


def print_usage_instructions():
    """打印使用说明"""
    print("\n" + "=" * 60)
    print("📖 使用说明")
    print("=" * 60)

    print("\n1. 📝 创建缺失的模型文件:")
    print("   创建 src/data/models/learning.py - 参考提供的学习模型代码")
    print("   创建 src/data/repositories/progress_tracker.py - 参考提供的追踪器代码")
    print("   创建 src/api/progress.py - 参考提供的API代码")

    print("\n2. 🔧 更新 src/data/models/base.py:")
    print("   添加 SQLAlchemy 支持到现有的 base.py 文件")

    print("\n3. 🚀 在现有聊天API中集成进度追踪:")
    print("   在 src/api/collaboration.py 顶部添加:")
    print("   ```python")
    print("   try:")
    print("       from ..data.repositories.progress_tracker import ProgressTracker")
    print("       PROGRESS_TRACKER_AVAILABLE = True")
    print("   except ImportError:")
    print("       PROGRESS_TRACKER_AVAILABLE = False")
    print("   ```")

    print("\n4. 📊 在聊天函数中添加追踪调用:")
    print("   在处理完智能体响应后添加:")
    print("   ```python")
    print("   if PROGRESS_TRACKER_AVAILABLE:")
    print("       try:")
    print("           tracker = ProgressTracker()")
    print("           tracker.extract_learning_data(user_input, agent_responses, session_id)")
    print("       except Exception as e:")
    print("           logger.warning(f'进度追踪失败: {e}')")
    print("   ```")

    print("\n5. 🔗 注册进度API路由:")
    print("   在主应用文件中添加:")
    print("   ```python")
    print("   from api import progress")
    print("   app.include_router(progress.router)")
    print("   ```")

    print("\n6. 🎨 更新前端进度页面:")
    print("   在现有 progress.html 中添加:")
    print("   ```html")
    print("   <script src='assets/js/progress_real.js'></script>")
    print("   ```")

    print("\n7. 🧪 测试系统:")
    print("   启动API服务器后:")
    print("   - 与智能体对话几轮")
    print("   - 访问 /api/v1/progress/summary 查看数据")
    print("   - 打开进度页面查看真实统计")

    print("\n" + "=" * 60)


def create_sample_data():
    """创建一些示例数据用于测试"""
    print("🧪 创建示例数据...")

    import uuid
    from datetime import datetime, timedelta

    db_path = "database/japanese_learning.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 插入一些示例语法进度
    sample_grammar = [
        ('を', 0.8, 15, 12),
        ('が', 0.6, 10, 7),
        ('に', 0.4, 8, 5),
        ('です', 0.9, 20, 18),
        ('〜て', 0.3, 5, 2)
    ]

    for grammar_point, mastery, practice_count, correct_answers in sample_grammar:
        cursor.execute('''
            INSERT OR REPLACE INTO learning_progress 
            (id, grammar_point, mastery_level, practice_count, correct_answers, agent_source)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (str(uuid.uuid4()), grammar_point, mastery, practice_count, correct_answers, 'tanaka'))

    # 插入一些示例词汇
    sample_vocab = [
        ('こんにちは', 'konnichiha', '你好', 0.9, 10, 'koumi'),
        ('ありがとう', 'arigatou', '谢谢', 0.8, 8, 'koumi'),
        ('学校', 'gakkou', '学校', 0.6, 5, 'tanaka'),
        ('友達', 'tomodachi', '朋友', 0.7, 6, 'koumi')
    ]

    for word, reading, meaning, mastery, times_reviewed, agent in sample_vocab:
        cursor.execute('''
            INSERT OR REPLACE INTO vocabulary_progress 
            (id, word, reading, meaning, mastery_score, times_reviewed, agent_source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (str(uuid.uuid4()), word, reading, meaning, mastery, times_reviewed, agent))

    # 插入用户统计
    cursor.execute('''
        INSERT OR REPLACE INTO user_stats 
        (id, total_conversations, total_vocabulary, total_grammar_points, total_xp, level, streak_days)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4()), 25, 50, 15, 1250, 8, 12))

    # 插入一些文化知识
    sample_cultural = [
        ('茶道', '日本传统茶道文化', 0.6, 'yamada'),
        ('樱花', '日本樱花文化和花见', 0.8, 'yamada'),
        ('新年', '日本新年传统', 0.4, 'yamada')
    ]

    for topic, content, understanding, agent in sample_cultural:
        cursor.execute('''
            INSERT OR REPLACE INTO cultural_knowledge 
            (id, topic, content_summary, understanding_level, learned_from_agent)
            VALUES (?, ?, ?, ?, ?)
        ''', (str(uuid.uuid4()), topic, content, understanding, agent))

    conn.commit()
    conn.close()

    print("   ✓ 示例数据已创建")


if __name__ == "__main__":
    setup_progress_system()

    # 询问是否创建示例数据
    create_sample = input("\n是否创建示例数据进行测试? (y/N): ").lower()
    if create_sample in ['y', 'yes']:
        create_sample_data()  # scripts/setup_progress_system.py
"""
快速设置学习进度系统
运行此脚本来初始化进度追踪功能
"""

import os
import sys
import sqlite3
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


def setup_progress_system():
    """设置学习进度系统"""
    print("🚀 开始设置日语学习进度系统...")

    # 1. 检查并创建必要的目录
    create_directories()

    # 2. 初始化数据库
    init_database()

    # 3. 更新API路由注册
    update_api_routes()

    # 4. 创建前端资源文件
    create_frontend_assets()

    # 5. 验证设置
    verify_setup()

    print("✅ 学习进度系统设置完成！")
    print_usage_instructions()


def create_directories():
    """创建必要的目录结构"""
    print("📁 创建目录结构...")

    directories = [
        "src/core/data/repositories",
        "src/api/routers",
        "frontend/assets/js",
        "database"
    ]

    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {dir_path}")


def init_database():
    """初始化SQLite数据库"""
    print("🗄️  初始化数据库...")

    try:
        # 直接使用SQLite创建表
        db_path = "database/japanese_learning.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 创建学习进度表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_progress (
                id TEXT PRIMARY KEY,
                user_id TEXT DEFAULT 'demo_user',
                grammar_point TEXT NOT NULL,
                mastery_level REAL DEFAULT 0.0,
                practice_count INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0,
                last_reviewed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                next_review TIMESTAMP,
                difficulty_rating REAL DEFAULT 0.5,
                agent_source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建词汇进度表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vocabulary_progress (
                id TEXT PRIMARY KEY,
                user_id TEXT DEFAULT 'demo_user',
                word TEXT NOT NULL,
                reading TEXT,
                meaning TEXT NOT NULL,
                example_sentence TEXT,
                difficulty_level INTEGER DEFAULT 1,
                review_interval INTEGER DEFAULT 1,
                next_review TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                mastery_score REAL DEFAULT 0.0,
                times_reviewed INTEGER DEFAULT 0,
                times_correct INTEGER DEFAULT 0,
                jlpt_level TEXT,
                agent_source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建对话学习记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_learning (
                id TEXT PRIMARY KEY,
                user_id TEXT DEFAULT 'demo_user',
                session_id TEXT NOT NULL,
                user_input TEXT,
                agent_responses TEXT,
                learning_points TEXT,
                corrections_made TEXT,
                participating_agents TEXT,
                scene_context TEXT DEFAULT 'general',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建用户统计表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_stats (
                id TEXT PRIMARY KEY,
                user_id TEXT DEFAULT 'demo_user',
                total_conversations INTEGER DEFAULT 0,
                total_vocabulary INTEGER DEFAULT 0,
                total_grammar_points INTEGER DEFAULT 0,
                current_level TEXT DEFAULT 'beginner',
                target_jlpt TEXT DEFAULT 'N5',
                streak_days INTEGER DEFAULT 0,
                total_xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建文化知识表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cultural_knowledge (
                id TEXT PRIMARY KEY,
                user_id TEXT DEFAULT 'demo_user',
                topic TEXT NOT NULL,
                subtopic TEXT,
                content_summary TEXT,
                learned_from_agent TEXT,
                understanding_level REAL DEFAULT 0.0,
                interest_rating REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

        print(f"   ✓ 数据库已创建: {db_path}")

    except Exception as e:
        print(f"   ❌ 数据库初始化失败: {e}")


def update_api_routes():
    """更新API路由注册"""
    print("🛣️  更新API路由...")

    # 检查主路由文件是否需要更新
    main_router_file = "src/api/__init__.py"

    if Path(main_router_file).exists():
        with open(main_router_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否已经包含进度路由
        if 'progress' not in content:
            # 添加进度路由导入和注册
            progress_import = "from .routers import progress\n"
            progress_register = "app.include_router(progress.router)\n"

            print("   ⚠️  请手动在主路由文件中添加进度路由")
            print(f"   导入: {progress_import.strip()}")
            print(f"   注册: {progress_register.strip()}")
        else:
            print("   ✓ 进度路由已存在")
    else:
        print("   ⚠️  未找到主路由文件，请手动配置")


def create_frontend_assets():
    """创建前端资源文件"""
    print("🎨 创建前端资源...")

    # 创建进度页面更新HTML（如果不存在）
    progress_html_path = "frontend/progress_real.html"

    if not Path(progress_html_path).exists():
        progress_html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 真实学习进度 - 日语学习系统</title>
    <link rel="stylesheet" href="assets/css/main.css">
    <link rel="stylesheet" href="assets/css/progress.css">
</head>
<body>
    <div id="app">
        <div class="loading-indicator">🔄 加载中...</div>
        <!-- 进度内容将由JavaScript动态生成 -->
    </div>

    <script src="assets/js/progress_real.js"></script>
</body>
</html>'''

        with open(progress_html_path, 'w', encoding='utf-8') as f:
            f.write(progress_html_content)

        print(f"   ✓ 创建进度页面: {progress_html_path}")

    # 创建刷新按钮的CSS
    refresh_css = '''
/* 刷新按钮样式 */
.refresh-progress {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: linear-gradient(45deg, #4CAF50, #45a049);
    color: white;
    border: none;
    border-radius: 50%;
    width: 56px;
    height: 56px;
    font-size: 24px;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transition: all 0.3s ease;
}

.refresh-progress:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 20px rgba(0,0,0,0.2);
}

.loading-indicator {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 2rem;
    color: #666;
    display: none;
}

.error-message {
    background: #f44336;
    color: white;
    padding: 15px;
    border-radius: 8px;
    margin: 20px;
    animation: slideInDown 0.3s ease;
}
'''

    css_path = "frontend/assets/css/progress_real.css"
    Path(css_path).parent.mkdir(parents=True, exist_ok=True)

    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(refresh_css)

    print(f"   ✓ 创建样式文件: {css_path}")


def verify_setup():
    """验证设置是否正确"""
    print("🔍 验证设置...")

    # 检查数据库文件
    db_path = "database/japanese_learning.db"
    if Path(db_path).exists():
        print("   ✓ 数据库文件存在")

        # 检查表结构
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()

        expected_tables = [
            'learning_progress', 'vocabulary_progress', 'conversation_learning',
            'user_stats', 'cultural_knowledge'
        ]

        existing_tables = [table[0] for table in tables]

        for table in expected_tables:
            if table in existing_tables:
                print(f"   ✓ 表 {table} 已创建")
            else:
                print(f"   ❌ 表 {table} 缺失")
    else:
        print("   ❌ 数据库文件不存在")

    # 检查核心文件
    core_files = [
        "src/core/data/models/learning.py",
        "src/core/data/repositories/progress_tracker.py",
        "src/api/routers/progress.py",
        "frontend/assets/js/progress_real.js"
    ]

    for file_path in core_files:
        if Path(file_path).exists():
            print(f"   ✓ {file_path}")
        else:
            print(f"   ❌ {file_path} 缺失")


def print_usage_instructions():
    """打印使用说明"""
    print("\n" + "=" * 60)
    print("📖 使用说明")
    print("=" * 60)

    print("\n1. 🚀 启动API服务器:")
    print("   cd src && python -m uvicorn main:app --reload --port 8000")

    print("\n2. 🔧 在现有聊天API中集成进度追踪:")
    print("   在 collaboration.py 的 send_message 函数末尾添加:")
    print("   ```python")
    print("   from core.data.repositories.progress_tracker import ProgressTracker")
    print("   tracker = ProgressTracker()")
    print("   tracker.extract_learning_data(request.message, {request.agent_name: result}, request.session_id)")
    print("   ```")

    print("\n3. 📊 访问进度API:")
    print("   GET  /api/v1/progress/summary - 获取进度摘要")
    print("   POST /api/v1/progress/track   - 追踪学习数据")
    print("   GET  /api/v1/progress/stats   - 获取详细统计")

    print("\n4. 🎨 更新前端页面:")
    print("   将 progress.html 中的 JavaScript 替换为 progress_real.js")
    print("   或直接使用 progress_real.html")

    print("\n5. 🧪 测试进度追踪:")
    print("   与智能体对话几轮后，访问进度页面查看真实数据")

    print("\n6. 🔄 手动初始化一些测试数据:")
    print("   python scripts/create_sample_data.py")

    print("\n" + "=" * 60)


def create_sample_data():
    """创建一些示例数据用于测试"""
    print("🧪 创建示例数据...")

    import uuid
    from datetime import datetime, timedelta

    db_path = "database/japanese_learning.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 插入一些示例语法进度
    sample_grammar = [
        ('を', 0.8, 15, 12),
        ('が', 0.6, 10, 7),
        ('に', 0.4, 8, 5),
        ('です', 0.9, 20, 18),
        ('〜て', 0.3, 5, 2)
    ]

    for grammar_point, mastery, practice_count, correct_answers in sample_grammar:
        cursor.execute('''
            INSERT OR REPLACE INTO learning_progress 
            (id, grammar_point, mastery_level, practice_count, correct_answers, agent_source)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (str(uuid.uuid4()), grammar_point, mastery, practice_count, correct_answers, 'tanaka'))

    # 插入一些示例词汇
    sample_vocab = [
        ('こんにちは', 'konnichiha', '你好', 0.9, 10, 'koumi'),
        ('ありがとう', 'arigatou', '谢谢', 0.8, 8, 'koumi'),
        ('学校', 'gakkou', '学校', 0.6, 5, 'tanaka'),
        ('友達', 'tomodachi', '朋友', 0.7, 6, 'koumi')
    ]

    for word, reading, meaning, mastery, times_reviewed, agent in sample_vocab:
        cursor.execute('''
            INSERT OR REPLACE INTO vocabulary_progress 
            (id, word, reading, meaning, mastery_score, times_reviewed, agent_source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (str(uuid.uuid4()), word, reading, meaning, mastery, times_reviewed, agent))

    # 插入用户统计
    cursor.execute('''
        INSERT OR REPLACE INTO user_stats 
        (id, total_conversations, total_vocabulary, total_grammar_points, total_xp, level, streak_days)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4()), 25, 50, 15, 1250, 8, 12))

    # 插入一些文化知识
    sample_cultural = [
        ('茶道', '日本传统茶道文化', 0.6, 'yamada'),
        ('樱花', '日本樱花文化和花见', 0.8, 'yamada'),
        ('新年', '日本新年传统', 0.4, 'yamada')
    ]

    for topic, content, understanding, agent in sample_cultural:
        cursor.execute('''
            INSERT OR REPLACE INTO cultural_knowledge 
            (id, topic, content_summary, understanding_level, learned_from_agent)
            VALUES (?, ?, ?, ?, ?)
        ''', (str(uuid.uuid4()), topic, content, understanding, agent))

    conn.commit()
    conn.close()

    print("   ✓ 示例数据已创建")


if __name__ == "__main__":
    setup_progress_system()

    # 询问是否创建示例数据
    create_sample = input("\n是否创建示例数据进行测试? (y/N): ").lower()
    if create_sample in ['y', 'yes']:
        create_sample_data()