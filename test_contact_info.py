#!/usr/bin/env python3
"""
Тест получения контактной информации агентами
"""

import logging
from app import create_app, db
from agents import AgentRouter

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_contact_info_access():
    """Тестирует доступ агентов к контактной информации"""
    
    # Создаем роутер агентов
    router = AgentRouter()
    
    # Тестовые запросы с контактной информацией
    test_queries = [
        "как связаться с университетом",
        "телефон приемной комиссии", 
        "адрес университета",
        "контакты деканата",
        "часы работы университета"
    ]
    
    print("🔍 Тестирование доступа к контактной информации")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n📞 Запрос: '{query}'")
        
        try:
            # Получаем ответ от роутера
            result = router.route_message(query, 'ru')
            
            print(f"🤖 Агент: {result.get('agent_name', 'Unknown')}")
            print(f"📊 Уверенность: {result.get('confidence', 0):.2f}")
            print(f"📚 Контекст использован: {result.get('context_used', False)}")
            
            # Проверяем, содержит ли ответ контактную информацию
            response = result.get('response', '')
            has_phone = any(phone in response for phone in ['+7 (7242) 123-456', '+7 (7242) 123-457', '+7 (7242) 123-458'])
            has_address = 'Университетская, 1' in response
            has_email = any(email in response for email in ['info@bolashak.kz', 'admission@bolashak.kz'])
            
            print(f"📞 Содержит телефон: {'✅' if has_phone else '❌'}")
            print(f"📍 Содержит адрес: {'✅' if has_address else '❌'}")
            print(f"📧 Содержит email: {'✅' if has_email else '❌'}")
            
            if has_phone or has_address or has_email:
                print("✅ УСПЕХ: Контактная информация доступна агенту!")
            else:
                print("❌ ПРОБЛЕМА: Контактная информация не найдена в ответе")
                print(f"Ответ: {response[:200]}...")
                
        except Exception as e:
            print(f"❌ Ошибка при тестировании: {e}")
        
        print("-" * 40)

def main():
    """Главная функция"""
    with create_app().app_context():
        logger.info("Начинаем тестирование доступа к контактной информации...")
        
        try:
            test_contact_info_access()
            logger.info("Тестирование завершено!")
            
        except Exception as e:
            logger.error(f"Ошибка при тестировании: {str(e)}")
            raise

if __name__ == "__main__":
    main()