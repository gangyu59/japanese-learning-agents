# database/connection.py
"""
Database Connection Management
数据库连接管理 - 统一的数据库连接和配置管理
"""

import os
import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager
import asyncio
from datetime import datetime

try:
    from sqlalchemy import create_engine, event, pool
    from sqlalchemy.orm import sessionmaker, Session
    from sqlalchemy.engine import Engine
    from sqlalchemy.pool import StaticPool
    import asyncpg

    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

from .models import Base, DatabaseManager


class DatabaseConfig:
    """数据库配置管理"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # 从环境变量读取配置
        self.database_url = os.getenv(
            'DATABASE_URL',
            'sqlite:///./japanese_learning.db'  # 默认SQLite
        )

        # 数据库连接池配置
        self.pool_size = int(os.getenv('DB_POOL_SIZE', '5'))
        self.max_overflow = int(os.getenv('DB_MAX_OVERFLOW', '10'))
        self.pool_timeout = int(os.getenv('DB_POOL_TIMEOUT', '30'))
        self.pool_recycle = int(os.getenv('DB_POOL_RECYCLE', '3600'))

        # 连接重试配置
        self.max_retries = int(os.getenv('DB_MAX_RETRIES', '3'))
        self.retry_delay = float(os.getenv('DB_RETRY_DELAY', '1.0'))

        # 调试模式
        self.debug_mode = os.getenv('DB_DEBUG', 'false').lower() == 'true'

        self.logger.info(f"数据库配置: {self.get_db_info()}")

    def get_db_info(self) -> Dict[str, Any]:
        """获取数据库信息（隐藏敏感信息）"""
        db_type = self.database_url.split('://')[0] if '://' in self.database_url else 'unknown'
        return {
            'type': db_type,
            'pool_size': self.pool_size,
            'max_overflow': self.max_overflow,
            'debug_mode': self.debug_mode
        }


class EnhancedDatabaseManager(DatabaseManager):
    """增强版数据库管理器"""

    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
        self.logger = logging.getLogger(__name__)

        if not DATABASE_AVAILABLE:
            raise ImportError("数据库依赖未安装。请运行: pip install sqlalchemy asyncpg psycopg2-binary")

        self.engine = None
        self.SessionLocal = None
        self._connection_healthy = False

        self._setup_database()

    def _setup_database(self):
        """设置数据库连接"""
        try:
            # 根据数据库类型配置引擎
            if self.config.database_url.startswith('sqlite'):
                self._setup_sqlite()
            elif self.config.database_url.startswith('postgresql'):
                self._setup_postgresql()
            else:
                self._setup_generic()

            # 设置事件监听器
            self._setup_event_listeners()

            # 创建会话工厂
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

            # 测试连接
            self._test_connection()

            self.logger.info("数据库连接初始化成功")

        except Exception as e:
            self.logger.error(f"数据库初始化失败: {str(e)}")
            raise

    def _setup_sqlite(self):
        """配置SQLite"""
        self.engine = create_engine(
            self.config.database_url,
            echo=self.config.debug_mode,
            poolclass=StaticPool,
            connect_args={
                "check_same_thread": False,
                "timeout": 20
            }
        )

    def _setup_postgresql(self):
        """配置PostgreSQL"""
        self.engine = create_engine(
            self.config.database_url,
            echo=self.config.debug_mode,
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            pool_timeout=self.config.pool_timeout,
            pool_recycle=self.config.pool_recycle,
            pool_pre_ping=True,  # 自动检测连接健康状态
            connect_args={
                "connect_timeout": 10,
                "server_settings": {
                    "application_name": "japanese_learning_system",
                }
            }
        )

    def _setup_generic(self):
        """通用数据库配置"""
        self.engine = create_engine(
            self.config.database_url,
            echo=self.config.debug_mode,
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            pool_timeout=self.config.pool_timeout,
            pool_recycle=self.config.pool_recycle
        )

    def _setup_event_listeners(self):
        """设置数据库事件监听器"""

        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """SQLite优化设置"""
            if self.config.database_url.startswith('sqlite'):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
                cursor.close()

        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """连接检出事件"""
            self.logger.debug("数据库连接检出")

        @event.listens_for(self.engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """连接归还事件"""
            self.logger.debug("数据库连接归还")

    def _test_connection(self):
        """测试数据库连接"""
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            self._connection_healthy = True
            self.logger.info("数据库连接测试成功")
        except Exception as e:
            self._connection_healthy = False
            self.logger.error(f"数据库连接测试失败: {str(e)}")
            raise

    def create_tables(self):
        """创建数据库表"""
        try:
            # 检查连接健康状态
            if not self._connection_healthy:
                self._test_connection()

            # 创建所有表
            Base.metadata.create_all(bind=self.engine)

            # 执行初始化数据
            self._initialize_default_data()

            self.logger.info("数据库表创建成功")

        except Exception as e:
            self.logger.error(f"创建数据库表失败: {str(e)}")
            raise

    def _initialize_default_data(self):
        """初始化默认数据"""
        try:
            with self.get_session() as session:
                # 检查是否已有数据
                from .models import User
                existing_users = session.query(User).count()

                if existing_users == 0:
                    # 创建默认用户
                    default_user = User(
                        username='demo_user',
                        email='demo@example.com',
                        password_hash='demo_hash',
                        learning_level='beginner',
                        target_jlpt_level='N5',
                        daily_goal=30
                    )
                    session.add(default_user)

                    # 添加一些示例记忆卡片
                    from .models import MemoryCard
                    sample_cards = [
                        MemoryCard(
                            user_id=default_user.user_id,
                            front='こんにちは',
                            back='你好 (konnichiwa)',
                            card_type='vocabulary',
                            difficulty=1,
                            tags=['greeting', 'basic']
                        ),
                        MemoryCard(
                            user_id=default_user.user_id,
                            front='ありがとう',
                            back='谢谢 (arigatou)',
                            card_type='vocabulary',
                            difficulty=1,
                            tags=['greeting', 'basic']
                        ),
                        MemoryCard(
                            user_id=default_user.user_id,
                            front='て形的用法',
                            back='表示进行时态、连接动词等',
                            card_type='grammar',
                            difficulty=3,
                            tags=['grammar', 'verb_form']
                        )
                    ]

                    for card in sample_cards:
                        session.add(card)

                    session.commit()
                    self.logger.info("默认数据初始化完成")

        except Exception as e:
            self.logger.error(f"初始化默认数据失败: {str(e)}")
            # 不抛出异常，因为这不是致命错误

    @contextmanager
    def get_session(self) -> Session:
        """获取数据库会话（上下文管理器）"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"数据库会话错误: {str(e)}")
            raise
        finally:
            session.close()

    def get_session_simple(self) -> Session:
        """获取数据库会话（简单版本，需要手动管理）"""
        return self.SessionLocal()

    def health_check(self) -> Dict[str, Any]:
        """数据库健康检查"""
        try:
            start_time = datetime.now()

            with self.engine.connect() as conn:
                result = conn.execute("SELECT 1").fetchone()

            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000

            # 检查连接池状态
            pool_status = {
                'pool_size': self.engine.pool.size(),
                'checked_in': self.engine.pool.checkedin(),
                'checked_out': self.engine.pool.checkedout(),
                'invalidated': self.engine.pool.invalidated()
            }

            return {
                'status': 'healthy',
                'response_time_ms': response_time,
                'database_type': self.config.database_url.split('://')[0],
                'pool_status': pool_status,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'database_type': self.config.database_url.split('://')[0],
                'timestamp': datetime.now().isoformat()
            }

    def execute_with_retry(self, operation, *args, **kwargs):
        """带重试机制的操作执行"""
        for attempt in range(self.config.max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    self.logger.error(f"数据库操作失败，已重试{self.config.max_retries}次: {str(e)}")
                    raise

                self.logger.warning(f"数据库操作失败，第{attempt + 1}次重试: {str(e)}")
                asyncio.sleep(self.config.retry_delay * (attempt + 1))  # 递增延迟

    def backup_database(self, backup_path: str) -> bool:
        """数据库备份"""
        try:
            if self.config.database_url.startswith('sqlite'):
                return self._backup_sqlite(backup_path)
            elif self.config.database_url.startswith('postgresql'):
                return self._backup_postgresql(backup_path)
            else:
                self.logger.warning("不支持的数据库类型，无法备份")
                return False

        except Exception as e:
            self.logger.error(f"数据库备份失败: {str(e)}")
            return False

    def _backup_sqlite(self, backup_path: str) -> bool:
        """备份SQLite数据库"""
        try:
            import shutil
            import sqlite3

            # 获取数据库文件路径
            db_path = self.config.database_url.replace('sqlite:///', '')

            if os.path.exists(db_path):
                # 使用SQLite的备份API
                source = sqlite3.connect(db_path)
                backup = sqlite3.connect(backup_path)

                source.backup(backup)

                source.close()
                backup.close()

                self.logger.info(f"SQLite数据库备份完成: {backup_path}")
                return True
            else:
                self.logger.error(f"源数据库文件不存在: {db_path}")
                return False

        except Exception as e:
            self.logger.error(f"SQLite备份失败: {str(e)}")
            return False

    def _backup_postgresql(self, backup_path: str) -> bool:
        """备份PostgreSQL数据库"""
        try:
            import subprocess
            from urllib.parse import urlparse

            # 解析数据库URL
            parsed = urlparse(self.config.database_url)

            # 构建pg_dump命令
            cmd = [
                'pg_dump',
                f'--host={parsed.hostname}',
                f'--port={parsed.port or 5432}',
                f'--username={parsed.username}',
                f'--dbname={parsed.path[1:]}',  # 去掉开头的/
                f'--file={backup_path}',
                '--verbose',
                '--format=custom'
            ]

            # 设置密码环境变量
            env = os.environ.copy()
            if parsed.password:
                env['PGPASSWORD'] = parsed.password

            # 执行备份
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)

            if result.returncode == 0:
                self.logger.info(f"PostgreSQL数据库备份完成: {backup_path}")
                return True
            else:
                self.logger.error(f"PostgreSQL备份失败: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"PostgreSQL备份失败: {str(e)}")
            return False

    def close(self):
        """关闭数据库连接"""
        try:
            if self.engine:
                self.engine.dispose()
                self.logger.info("数据库连接已关闭")
        except Exception as e:
            self.logger.error(f"关闭数据库连接失败: {str(e)}")


# 全局数据库管理器实例
_db_manager: Optional[EnhancedDatabaseManager] = None


def get_database_manager(config: Optional[DatabaseConfig] = None) -> EnhancedDatabaseManager:
    """获取全局数据库管理器实例"""
    global _db_manager

    if _db_manager is None:
        _db_manager = EnhancedDatabaseManager(config)

    return _db_manager


def init_database(config: Optional[DatabaseConfig] = None) -> EnhancedDatabaseManager:
    """初始化数据库"""
    db_manager = get_database_manager(config)
    db_manager.create_tables()
    return db_manager


# 配置文件生成器
class ConfigGenerator:
    """配置文件生成器"""

    @staticmethod
    def generate_env_template() -> str:
        """生成环境变量配置模板"""
        return """# 日语学习Multi-Agent系统 - 数据库配置

# 数据库连接URL
# SQLite (开发环境)
DATABASE_URL=sqlite:///./japanese_learning.db

# PostgreSQL (生产环境)  
# DATABASE_URL=postgresql://username:password@localhost:5432/japanese_learning

# 数据库连接池配置
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# 连接重试配置
DB_MAX_RETRIES=3
DB_RETRY_DELAY=1.0

# 调试模式 (开发时设为true)
DB_DEBUG=false

# 其他配置
LOG_LEVEL=INFO
"""

    @staticmethod
    def generate_docker_compose() -> str:
        """生成Docker Compose配置"""
        return """version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://japanese_user:japanese_pass@postgres:5432/japanese_learning
      - DB_POOL_SIZE=10
      - DB_MAX_OVERFLOW=20
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=japanese_learning
      - POSTGRES_USER=japanese_user
      - POSTGRES_PASSWORD=japanese_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/migrations:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U japanese_user -d japanese_learning"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
"""

    @staticmethod
    def save_config_files(output_dir: str = "."):
        """保存配置文件"""
        try:
            # 创建.env文件
            env_path = os.path.join(output_dir, '.env.template')
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(ConfigGenerator.generate_env_template())

            # 创建docker-compose.yml
            compose_path = os.path.join(output_dir, 'docker-compose.yml')
            with open(compose_path, 'w', encoding='utf-8') as f:
                f.write(ConfigGenerator.generate_docker_compose())

            print(f"配置文件已生成:")
            print(f"  - {env_path}")
            print(f"  - {compose_path}")

            return True

        except Exception as e:
            print(f"生成配置文件失败: {str(e)}")
            return False


# CLI工具
def main():
    """命令行工具入口"""
    import argparse

    parser = argparse.ArgumentParser(description='日语学习系统数据库管理工具')
    parser.add_argument('action', choices=['init', 'health', 'backup', 'config'],
                        help='执行的操作')
    parser.add_argument('--config', help='数据库配置文件路径')
    parser.add_argument('--backup-path', help='备份文件路径')
    parser.add_argument('--output-dir', default='.', help='配置文件输出目录')

    args = parser.parse_args()

    if args.action == 'config':
        # 生成配置文件
        success = ConfigGenerator.save_config_files(args.output_dir)
        exit(0 if success else 1)

    # 初始化数据库管理器
    config = DatabaseConfig()

    if args.action == 'init':
        # 初始化数据库
        try:
            db_manager = init_database(config)
            print("数据库初始化成功!")
        except Exception as e:
            print(f"数据库初始化失败: {str(e)}")
            exit(1)

    elif args.action == 'health':
        # 健康检查
        try:
            db_manager = get_database_manager(config)
            health = db_manager.health_check()
            print(f"数据库健康状态: {health}")
        except Exception as e:
            print(f"健康检查失败: {str(e)}")
            exit(1)

    elif args.action == 'backup':
        # 数据库备份
        if not args.backup_path:
            print("请指定备份文件路径 --backup-path")
            exit(1)

        try:
            db_manager = get_database_manager(config)
            success = db_manager.backup_database(args.backup_path)
            if success:
                print(f"数据库备份成功: {args.backup_path}")
            else:
                print("数据库备份失败")
                exit(1)
        except Exception as e:
            print(f"数据库备份失败: {str(e)}")
            exit(1)


if __name__ == '__main__':
    main()

# 导出主要类
__all__ = [
    'DatabaseConfig', 'EnhancedDatabaseManager',
    'get_database_manager', 'init_database', 'ConfigGenerator'
]