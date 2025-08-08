#!/usr/bin/env python3
"""
Скрипт для добавления контактной информации университета "Болашак" во все агенты
"""

import logging
from app import create_app, db
from models import AgentKnowledgeBase, AdminUser

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_university_contacts():
    """Добавляет контактную информацию университета для всех агентов"""
    
    # Получаем или создаем админа для связи
    admin_user = AdminUser.query.first()
    if not admin_user:
        # Создаем системного администратора
        admin_user = AdminUser(
            username='system',
            email='system@bolashak.kz'
        )
        admin_user.set_password('system123')
        db.session.add(admin_user)
        db.session.commit()
        logger.info("Создан системный администратор для связи записей")
    
    # Список всех типов агентов
    agent_types = ['ai_abitur', 'kadrai', 'uninav', 'career_navigator', 'uniroom']
    
    # Контактная информация университета
    contact_data = {
        'title': 'Контактная информация университета "Болашак"',
        'content_ru': '''**Университет "Болашак"**

**Адрес:**
г. Кызылорда, ул. Университетская, 1
Почтовый индекс: 120000

**Телефоны:**
• Приёмная ректора: +7 (7242) 123-456
• Приёмная комиссия: +7 (7242) 123-457
• Деканаты: +7 (7242) 123-458
• Общежитие: +7 (7242) 123-459

**Email:**
• info@bolashak.kz - общие вопросы
• admission@bolashak.kz - поступление
• student@bolashak.kz - для студентов

**Часы работы:**
• Понедельник-Пятница: 9:00-18:00
• Суббота: 9:00-13:00
• Воскресенье: выходной''',
        'content_kz': '''**"Болашақ" университеті**

**Мекенжайы:**
Қызылорда қ., Университетская к-сі, 1
Пошта индексі: 120000

**Телефондар:**
• Ректор кеңсесі: +7 (7242) 123-456
• Қабылдау комиссиясы: +7 (7242) 123-457
• Деканаттар: +7 (7242) 123-458
• Жатақхана: +7 (7242) 123-459

**Email:**
• info@bolashak.kz - жалпы сұрақтар
• admission@bolashak.kz - түсу
• student@bolashak.kz - студенттерге

**Жұмыс уақыты:**
• Дүйсенбі-Жұма: 9:00-18:00
• Сенбі: 9:00-13:00
• Жексенбі: демалыс күні''',
        'content_en': '''**"Bolashak" University**

**Address:**
Kyzylorda city, Universitetskaya str., 1
Postal code: 120000

**Phones:**
• Rector's office: +7 (7242) 123-456
• Admissions committee: +7 (7242) 123-457
• Deaneries: +7 (7242) 123-458
• Dormitory: +7 (7242) 123-459

**Email:**
• info@bolashak.kz - general questions
• admission@bolashak.kz - admissions
• student@bolashak.kz - for students

**Working hours:**
• Monday-Friday: 9:00-18:00
• Saturday: 9:00-13:00
• Sunday: closed''',
        'keywords': 'контакты, телефон, адрес, email, часы работы, университет, болашак',
        'category': 'Контакты',
        'tags': 'контакты,телефон,адрес,email,университет',
        'priority': 1,  # Высокий приоритет
        'is_featured': True,
        'is_active': True
    }
    
    # Добавляем контактную информацию для каждого типа агента
    for agent_type in agent_types:
        # Проверяем, есть ли уже такая запись
        existing_contact = AgentKnowledgeBase.query.filter_by(
            agent_type=agent_type,
            title=contact_data['title']
        ).first()
        
        if existing_contact:
            # Обновляем существующую запись
            for key, value in contact_data.items():
                if key != 'title':  # Не обновляем title, так как по нему ищем
                    setattr(existing_contact, key, value)
            logger.info(f"Обновлена контактная информация для агента: {agent_type}")
        else:
            # Создаем новую запись
            contact_entry = AgentKnowledgeBase(
                agent_type=agent_type,
                created_by=admin_user.id,
                **contact_data
            )
            db.session.add(contact_entry)
            logger.info(f"Добавлена контактная информация для агента: {agent_type}")
    
    # Сохраняем изменения
    db.session.commit()
    logger.info("Контактная информация университета добавлена для всех агентов")

def main():
    """Главная функция"""
    with create_app().app_context():
        logger.info("Начинаем добавление контактной информации университета...")
        
        try:
            add_university_contacts()
            logger.info("Контактная информация успешно добавлена!")
            
        except Exception as e:
            logger.error(f"Ошибка при добавлении контактной информации: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    main()