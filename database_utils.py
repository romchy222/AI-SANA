# Утилиты для работы с базой данных
# Database utilities for BolashakChat

import logging
import os
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config import DatabaseConfig

class DatabaseManager:
    """Управление подключениями к базе данных"""
    
    def __init__(self):
        self.config = DatabaseConfig()
        
    def test_connection(self, db_type: Optional[str] = None) -> bool:
        """Тестирование подключения к базе данных"""
        original_type = None
        try:
            if db_type:
                # Временно изменяем тип БД для тестирования
                original_type = DatabaseConfig.DB_TYPE
                DatabaseConfig.DB_TYPE = db_type
                
            database_url = DatabaseConfig.get_database_url()
            engine_options = DatabaseConfig.get_engine_options()
            
            engine = create_engine(database_url, **engine_options)
            
            # Тестовый запрос
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1 as test"))
                row = result.fetchone()
                if row and row[0] == 1:
                    logging.info(f"Database connection successful for {db_type or DatabaseConfig.DB_TYPE}")
                    return True
                    
        except SQLAlchemyError as e:
            logging.error(f"Database connection failed for {db_type or DatabaseConfig.DB_TYPE}: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error testing {db_type or DatabaseConfig.DB_TYPE}: {str(e)}")
            return False
        finally:
            if db_type and original_type is not None:
                # Восстанавливаем оригинальный тип
                DatabaseConfig.DB_TYPE = original_type
                
        return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Получение информации о текущей конфигурации БД"""
        database_url = DatabaseConfig.get_database_url()
        
        # Парсинг URL для получения информации
        info = {
            'type': DatabaseConfig.DB_TYPE,
            'url': database_url,
            'engine_options': DatabaseConfig.get_engine_options()
        }
        
        if DatabaseConfig.DB_TYPE == 'postgresql':
            info.update({
                'host': DatabaseConfig.POSTGRES_HOST,
                'port': DatabaseConfig.POSTGRES_PORT,
                'database': DatabaseConfig.POSTGRES_DB,
                'user': DatabaseConfig.POSTGRES_USER
            })
        elif DatabaseConfig.DB_TYPE == 'mysql':
            info.update({
                'host': DatabaseConfig.MYSQL_HOST,
                'port': DatabaseConfig.MYSQL_PORT,
                'database': DatabaseConfig.MYSQL_DB,
                'user': DatabaseConfig.MYSQL_USER
            })
        else:  # SQLite
            info.update({
                'path': DatabaseConfig.SQLITE_PATH
            })
            
        return info
    
    def create_database_if_not_exists(self, db_type: str = None) -> bool:
        """Создание базы данных если она не существует (только для MySQL и PostgreSQL)"""
        if not db_type:
            db_type = DatabaseConfig.DB_TYPE
            
        if db_type == 'sqlite':
            # SQLite создаёт файл автоматически
            return True
            
        try:
            if db_type == 'mysql':
                # Подключение к MySQL серверу без указания БД
                base_url = f"mysql+pymysql://{DatabaseConfig.MYSQL_USER}:{DatabaseConfig.MYSQL_PASSWORD}@{DatabaseConfig.MYSQL_HOST}:{DatabaseConfig.MYSQL_PORT}/"
                engine = create_engine(base_url)
                
                with engine.connect() as connection:
                    # Проверяем существует ли БД
                    result = connection.execute(text(f"SHOW DATABASES LIKE '{DatabaseConfig.MYSQL_DB}'"))
                    if not result.fetchone():
                        # Создаём БД если не существует
                        connection.execute(text(f"CREATE DATABASE {DatabaseConfig.MYSQL_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                        logging.info(f"Created MySQL database: {DatabaseConfig.MYSQL_DB}")
                    
            elif db_type == 'postgresql':
                # Подключение к PostgreSQL серверу без указания БД
                base_url = f"postgresql://{DatabaseConfig.POSTGRES_USER}:{DatabaseConfig.POSTGRES_PASSWORD}@{DatabaseConfig.POSTGRES_HOST}:{DatabaseConfig.POSTGRES_PORT}/postgres"
                engine = create_engine(base_url)
                
                with engine.connect() as connection:
                    # Проверяем существует ли БД
                    result = connection.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{DatabaseConfig.POSTGRES_DB}'"))
                    if not result.fetchone():
                        # Создаём БД если не существует
                        connection.execute(text(f"CREATE DATABASE {DatabaseConfig.POSTGRES_DB}"))
                        logging.info(f"Created PostgreSQL database: {DatabaseConfig.POSTGRES_DB}")
                        
            return True
            
        except SQLAlchemyError as e:
            logging.error(f"Failed to create database for {db_type}: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error creating database for {db_type}: {str(e)}")
            return False

def test_all_databases() -> Dict[str, bool]:
    """Тестирование всех доступных типов БД"""
    manager = DatabaseManager()
    results = {}
    
    for db_type in ['postgresql', 'mysql', 'sqlite']:
        results[db_type] = manager.test_connection(db_type)
        
    return results

if __name__ == "__main__":
    # Тестирование при запуске модуля
    logging.basicConfig(level=logging.INFO)
    
    manager = DatabaseManager()
    
    print("=== Database Configuration Info ===")
    info = manager.get_database_info()
    for key, value in info.items():
        if key == 'url' and '@' in str(value):
            # Скрываем пароль в URL
            parts = str(value).split('@')
            if ':' in parts[0]:
                user_pass = parts[0].split(':')
                safe_value = f"{user_pass[0]}:***@{parts[1]}"
                print(f"{key}: {safe_value}")
            else:
                print(f"{key}: {value}")
        else:
            print(f"{key}: {value}")
    
    print("\n=== Testing Database Connections ===")
    results = test_all_databases()
    for db_type, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{db_type.upper()}: {status}")
    
    print(f"\nCurrent database type: {DatabaseConfig.DB_TYPE}")
    current_status = "✓ SUCCESS" if manager.test_connection() else "✗ FAILED"
    print(f"Current connection: {current_status}")