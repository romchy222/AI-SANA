# Импорт необходимых библиотек
import os
import logging
from flask import Flask
from flask_cors import CORS
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)


# Базовый класс для моделей базы данных
class Base(DeclarativeBase):
    pass


# Import db from models to avoid circular imports
from models import db


def create_app():
    """Функция создания и настройки Flask приложения"""
    # Создание экземпляра Flask приложения
    app = Flask(__name__)
    # Установка секретного ключа для сессий
    app.secret_key = os.environ.get("SESSION_SECRET",
                                    "dev-secret-key-change-in-production")
    # Настройка ProxyFix для работы за прокси
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Настройка базы данных с использованием конфигурационного файла
    from config import DatabaseConfig
    database_url = DatabaseConfig.get_database_url()
    
    # Логирование информации о БД (скрываем пароли)
    if database_url:
        safe_url = database_url
        if "@" in safe_url:
            parts = safe_url.split("@")
            if ":" in parts[0]:
                user_pass = parts[0].split(":")
                safe_url = f"{user_pass[0]}:***@{parts[1]}"
        logging.info(f"Using database: {safe_url}")
    else:
        logging.error("No database URL configured")
        raise ValueError("Database configuration is required")
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    # Настройки движка базы данных в зависимости от типа БД
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = DatabaseConfig.get_engine_options()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Инициализация базы данных с приложением
    db.init_app(app)

    # Настройка CORS (разрешение кросс-доменных запросов)
    CORS(
        app,
        origins=[
            "https://7a0463a0-cbab-40ed-8964-1461cf93cb8a-00-tv6bvx5wqo3s.pike.replit.dev",
            "https://*.replit.dev",  # Разрешить все поддомены replit.dev
            "http://localhost:*",  # Для локальной разработки
            "https://localhost:*"  # Для локальной разработки с HTTPS
        ],
        supports_credentials=True)

    # Настройка системы локализации
    from localization import localization, localize_filter
    app.jinja_env.filters['localize'] = localize_filter
    app.jinja_env.globals['get_language'] = localization.get_current_language
    app.jinja_env.globals['get_locale'] = localization.get_current_language
    app.jinja_env.globals['_'] = localization.get_text

    # Импорт модулей с маршрутами (blueprints)
    from views import main_bp
    from admin import admin_bp
    from auth import auth_bp

    # Регистрация модулей маршрутов
    app.register_blueprint(main_bp)  # Основные страницы
    app.register_blueprint(admin_bp, url_prefix='/admin')  # Админ панель
    app.register_blueprint(auth_bp, url_prefix='/auth')  # Аутентификация
    
    # Register enhanced API blueprint
    from api_enhanced import api_enhanced
    app.register_blueprint(api_enhanced)

    # Инициализация в контексте приложения
    with app.app_context():
        # Импорт моделей для регистрации в SQLAlchemy и инициализация db
        import models

        # Создание всех таблиц в базе данных
        db.create_all()

        # Инициализация начальных данных с задержкой
        # Commented out for now to avoid circular imports
        # try:
        #     from setup_db import init_default_data
        #     init_default_data()
        # except Exception as e:
        #     import logging
        #     logger = logging.getLogger(__name__)
        #     logger.error(f"Error initializing default data: {e}")

    return app


# Создание экземпляра приложения
app = create_app()

# Запуск приложения в режиме разработки
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
