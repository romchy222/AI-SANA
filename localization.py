# Система локализации для BolashakChat
# Localization system for BolashakChat

import os
import json
from typing import Dict, Any, Optional
from flask import session, request

class Localization:
    """Класс для управления локализацией"""
    
    def __init__(self):
        self.translations = {}
        self.default_language = 'ru'
        self.supported_languages = ['ru', 'kz', 'en']
        self.load_translations()
    
    def load_translations(self):
        """Загрузка переводов из файлов"""
        translations_dir = 'translations'
        if not os.path.exists(translations_dir):
            os.makedirs(translations_dir)
            
        for lang in self.supported_languages:
            file_path = os.path.join(translations_dir, f'{lang}.json')
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.translations[lang] = json.load(f)
                except Exception as e:
                    print(f"Error loading {lang} translations: {e}")
                    self.translations[lang] = {}
            else:
                self.translations[lang] = {}
    
    def get_current_language(self) -> str:
        """Получение текущего языка"""
        # Приоритет: URL параметр > сессия > заголовки браузера > по умолчанию
        lang = request.args.get('lang')
        if lang and lang in self.supported_languages:
            session['language'] = lang
            return lang
            
        if 'language' in session and session['language'] in self.supported_languages:
            return session['language']
            
        # Определение языка из заголовков браузера
        if request.accept_languages:
            best_match = request.accept_languages.best_match(self.supported_languages)
            if best_match:
                session['language'] = best_match
                return best_match
                
        return self.default_language
    
    def get_text(self, key: str, language: Optional[str] = None, **kwargs) -> str:
        """Получение локализованного текста"""
        if language is None:
            try:
                language = self.get_current_language()
            except:
                language = self.default_language
            
        # Поддержка ключей с точками (например, app.title)
        def get_nested_value(data: dict, key: str):
            """Получение значения по ключу с точками"""
            keys = key.split('.')
            current = data
            for k in keys:
                if isinstance(current, dict) and k in current:
                    current = current[k]
                else:
                    return None
            return current
        
        # Попытка найти перевод
        translation = get_nested_value(self.translations.get(language, {}), key)
        
        # Fallback на русский язык
        if not translation and language != 'ru':
            translation = get_nested_value(self.translations.get('ru', {}), key)
            
        # Fallback на ключ
        if not translation:
            translation = key
            
        # Форматирование с параметрами
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except (KeyError, ValueError):
                pass
                
        return translation
    
    def get_agent_types_localized(self, language: Optional[str] = None) -> Dict[str, str]:
        """Получение локализованных названий типов агентов"""
        if language is None:
            language = self.get_current_language()
            
        return {
            'admission': self.get_text('agent.admission', language),
            'scholarship': self.get_text('agent.scholarship', language),
            'academic': self.get_text('agent.academic', language),
            'student_life': self.get_text('agent.student_life', language),
            'general': self.get_text('agent.general', language),
            'technical': self.get_text('agent.technical', language),
            'international': self.get_text('agent.international', language),
        }

# Глобальный экземпляр локализации
localization = Localization()

def _(key: str, **kwargs) -> str:
    """Shortcut функция для получения переводов"""
    return localization.get_text(key, **kwargs)

def get_language() -> str:
    """Shortcut функция для получения текущего языка"""
    return localization.get_current_language()

# Flask template filter
def localize_filter(key: str, **kwargs) -> str:
    """Фильтр Jinja2 для локализации"""
    return localization.get_text(key, **kwargs)