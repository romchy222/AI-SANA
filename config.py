# Configuration file for BolashakChat AI Agent System
# Конфигурационный файл для системы ИИ-агентов BolashakChat

import os
from typing import Dict, Any

class DatabaseConfig:
    """Database configuration settings"""
    
    # Database type selection
    DB_TYPE = os.environ.get('DB_TYPE', 'sqlite')  # 'sqlite', 'postgresql', 'mysql'
    
    # SQLite settings
    SQLITE_PATH = os.environ.get('SQLITE_PATH', 'bolashakbot.db')
    
    # PostgreSQL settings - использует переменные из созданной БД
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', os.environ.get('PGHOST', 'localhost'))
    POSTGRES_PORT = os.environ.get('POSTGRES_PORT', os.environ.get('PGPORT', '5432'))
    POSTGRES_DB = os.environ.get('POSTGRES_DB', os.environ.get('PGDATABASE', 'bolashakbot'))
    POSTGRES_USER = os.environ.get('POSTGRES_USER', os.environ.get('PGUSER', 'postgres'))
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', os.environ.get('PGPASSWORD', ''))
    
    # MySQL settings
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'bolashakbot')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database URL based on configuration"""
        # Check for explicit DATABASE_URL but modify it for driver compatibility
        database_url = os.environ.get("DATABASE_URL")
        if database_url and database_url.startswith("postgresql://"):
            # Convert PostgreSQL URL to use pg8000 if psycopg2 is not available
            try:
                import psycopg2
                return database_url
            except ImportError:
                # Replace postgresql:// with postgresql+pg8000:// and remove unsupported SSL params
                pg8000_url = database_url.replace("postgresql://", "postgresql+pg8000://")
                # Remove sslmode parameter as pg8000 handles SSL automatically
                if "?sslmode=require" in pg8000_url:
                    pg8000_url = pg8000_url.replace("?sslmode=require", "")
                elif "&sslmode=require" in pg8000_url:
                    pg8000_url = pg8000_url.replace("&sslmode=require", "")
                return pg8000_url
        elif database_url:
            return database_url
            
        if cls.DB_TYPE == 'postgresql':
            # Используем psycopg2 или fallback на pg8000 если psycopg2 недоступен
            try:
                import psycopg2
                return f"postgresql://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"
            except ImportError:
                # Fallback to pg8000 driver
                return f"postgresql+pg8000://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"
        elif cls.DB_TYPE == 'mysql':
            # Используем pymysql драйвер для MySQL
            return f"mysql+pymysql://{cls.MYSQL_USER}:{cls.MYSQL_PASSWORD}@{cls.MYSQL_HOST}:{cls.MYSQL_PORT}/{cls.MYSQL_DB}?charset=utf8mb4"
        else:  # Default to SQLite
            return f"sqlite:///{cls.SQLITE_PATH}"
    
    @classmethod
    def get_engine_options(cls) -> Dict[str, Any]:
        """Get database engine options based on database type"""
        base_options = {
            "pool_recycle": 300,  # Переподключение каждые 5 минут
            "pool_pre_ping": True,  # Проверка соединения перед использованием
        }
        
        if cls.DB_TYPE == 'postgresql':
            # Different options for psycopg2 vs pg8000
            try:
                import psycopg2
                return {
                    **base_options,
                    "pool_size": 5,
                    "max_overflow": 10,
                    "pool_timeout": 30,
                }
            except ImportError:
                # pg8000 works better with simpler pool settings
                return {
                    "pool_pre_ping": True,
                    "pool_recycle": 300,
                }
        elif cls.DB_TYPE == 'mysql':
            return {
                **base_options,
                "pool_size": 5,
                "max_overflow": 10,
                "pool_timeout": 30,
                "connect_args": {"charset": "utf8mb4"}
            }
        else:  # SQLite
            return {
                "pool_pre_ping": True,
                "connect_args": {"check_same_thread": False}
            }

class AgentConfig:
    """Agent-specific configuration settings"""
    
    # Agent knowledge base settings
    AGENT_KNOWLEDGE_ENABLED = os.environ.get('AGENT_KNOWLEDGE_ENABLED', 'true').lower() == 'true'
    DEFAULT_AGENT_PRIORITY = int(os.environ.get('DEFAULT_AGENT_PRIORITY', '1'))
    
    # Agent response settings
    MAX_RESPONSE_LENGTH = int(os.environ.get('MAX_RESPONSE_LENGTH', '2000'))
    DEFAULT_CONFIDENCE_THRESHOLD = float(os.environ.get('DEFAULT_CONFIDENCE_THRESHOLD', '0.3'))
    
    # Available agent types with their display names
    AGENT_TYPES = {
        'ai_assistant': 'AI-Assistant',
        'ai_navigator': 'AI-Навигатор', 
        'student_navigator': 'Студенческий навигатор',
        'green_navigator': 'GreenNavigator',
        'communication': 'Агент по вопросам общения'
    }

class SessionConfig:
    """Session management configuration"""
    
    # Session settings
    SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', '3600'))  # 1 hour
    VOICE_SESSION_TIMEOUT = int(os.environ.get('VOICE_SESSION_TIMEOUT', '1800'))  # 30 minutes
    
    # User context isolation
    ENABLE_USER_CONTEXT = os.environ.get('ENABLE_USER_CONTEXT', 'true').lower() == 'true'
    MAX_CONTEXT_HISTORY = int(os.environ.get('MAX_CONTEXT_HISTORY', '10'))

class RatingConfig:
    """Rating system configuration"""
    
    # Rating settings
    ENABLE_RATINGS = os.environ.get('ENABLE_RATINGS', 'true').lower() == 'true'
    RATING_TYPES = ['like', 'dislike']
    
    # Statistics settings
    STATS_CACHE_TIMEOUT = int(os.environ.get('STATS_CACHE_TIMEOUT', '300'))  # 5 minutes

class VoiceChatConfig:
    """Voice chat configuration"""
    
    # Voice chat settings
    ENABLE_VOICE_CHAT = os.environ.get('ENABLE_VOICE_CHAT', 'true').lower() == 'true'
    MAX_AUDIO_FILE_SIZE = int(os.environ.get('MAX_AUDIO_FILE_SIZE', '10485760'))  # 10 MB
    SUPPORTED_AUDIO_FORMATS = ['wav', 'mp3', 'ogg', 'webm']
    
    # TTS settings
    TTS_SERVICE_URL = os.environ.get('TTS_SERVICE_URL', 'https://api.silero.ai/voice')
    TTS_DEFAULT_FORMAT = os.environ.get('TTS_DEFAULT_FORMAT', 'wav')

def get_config() -> Dict[str, Any]:
    """Get complete configuration dictionary"""
    return {
        'database': {
            'type': DatabaseConfig.DB_TYPE,
            'url': DatabaseConfig.get_database_url()
        },
        'agents': {
            'knowledge_enabled': AgentConfig.AGENT_KNOWLEDGE_ENABLED,
            'types': AgentConfig.AGENT_TYPES,
            'confidence_threshold': AgentConfig.DEFAULT_CONFIDENCE_THRESHOLD
        },
        'sessions': {
            'timeout': SessionConfig.SESSION_TIMEOUT,
            'voice_timeout': SessionConfig.VOICE_SESSION_TIMEOUT,
            'context_enabled': SessionConfig.ENABLE_USER_CONTEXT
        },
        'ratings': {
            'enabled': RatingConfig.ENABLE_RATINGS,
            'types': RatingConfig.RATING_TYPES
        },
        'voice_chat': {
            'enabled': VoiceChatConfig.ENABLE_VOICE_CHAT,
            'max_file_size': VoiceChatConfig.MAX_AUDIO_FILE_SIZE,
            'formats': VoiceChatConfig.SUPPORTED_AUDIO_FORMATS
        }
    }