#!/usr/bin/env python3
"""
Database migration script for enhanced AI-SANA models
Adds new tables for enhanced agent functionality
"""

import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, DocumentTemplate, StudentRequest, Schedule, JobPosting, HousingRoom, HousingAssignment, Notification

def migrate_database():
    """Create enhanced models tables"""
    print("Starting database migration for enhanced AI-SANA models...")
    
    app = create_app()
    with app.app_context():
        try:
            # Create all new tables
            print("Creating enhanced models tables...")
            db.create_all()
            
            # Add some sample data for testing
            print("Adding sample data...")
            add_sample_data()
            
            print("Database migration completed successfully!")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            raise

def add_sample_data():
    """Add sample data for testing the enhanced functionality"""
    
    # Sample document templates
    templates = [
        {
            'name_ru': 'Заявление на поступление',
            'name_kz': 'Түсу туралы өтініш',
            'category': 'admission',
            'agent_type': 'ai_abitur',
            'template_content': '''
# Заявление на поступление

**Ректору Кызылординского университета "Болашак"**

От: {{student_name}}
Дата рождения: {{birth_date}}
Адрес: {{address}}
Телефон: {{phone}}
Email: {{email}}

Прошу принять меня на {{program_name}} на {{study_form}} форму обучения.

К заявлению прилагаю:
- Аттестат о среднем образовании
- Медицинская справка
- Фотографии 3x4 (6 шт)
- Копия удостоверения личности

Дата: {{date}}
Подпись: _________________
            ''',
            'required_fields': ['student_name', 'birth_date', 'address', 'phone', 'email', 'program_name', 'study_form'],
            'instructions_ru': 'Заполните все поля и приложите необходимые документы',
            'instructions_kz': 'Барлық өрістерді толтырыңыз және қажетті құжаттарды тіркеңіз'
        },
        {
            'name_ru': 'Заявление на отпуск',
            'name_kz': 'Демалыс туралы өтініш',
            'category': 'hr',
            'agent_type': 'kadrai',
            'template_content': '''
# Заявление на отпуск

**Ректору Кызылординского университета "Болашак"**

От: {{employee_name}}
Должность: {{position}}
Подразделение: {{department}}

Прошу предоставить мне ежегодный оплачиваемый отпуск с {{start_date}} по {{end_date}} на {{days_count}} календарных дней.

Основание: {{reason}}

Дата: {{date}}
Подпись: _________________
            ''',
            'required_fields': ['employee_name', 'position', 'department', 'start_date', 'end_date', 'days_count', 'reason'],
            'instructions_ru': 'Подайте заявление не менее чем за 2 недели до отпуска',
            'instructions_kz': 'Өтінішті демалысқа дейін кемінде 2 апта бұрын беріңіз'
        },
        {
            'name_ru': 'Заявление на поселение в общежитие',
            'name_kz': 'Жатақханаға орналасу туралы өтініш',
            'category': 'housing',
            'agent_type': 'uniroom',
            'template_content': '''
# Заявление на поселение в общежитие

**Директору общежития №{{dorm_number}}**

От: {{student_name}}
Группа: {{group}}
Курс: {{course}}
Факультет: {{faculty}}

Прошу поселить меня в общежитие №{{dorm_number}} на {{academic_year}} учебный год.

Тип размещения: {{room_type}}
Особые пожелания: {{preferences}}

Контактный телефон: {{phone}}
Email: {{email}}

Дата: {{date}}
Подпись: _________________
            ''',
            'required_fields': ['student_name', 'group', 'course', 'faculty', 'dorm_number', 'academic_year', 'room_type', 'phone', 'email'],
            'instructions_ru': 'Подавайте заявление до 1 сентября',
            'instructions_kz': '1 қыркүйекке дейін өтініш беріңіз'
        }
    ]
    
    # Sample schedules
    schedules = [
        {
            'schedule_type': 'class',
            'title': 'Математический анализ',
            'faculty': 'Естественно-технических наук',
            'course_code': 'MATH101',
            'group_name': 'ЕТН-21-1',
            'instructor': 'Иванов И.И.',
            'start_time': datetime(2024, 9, 2, 9, 0),
            'end_time': datetime(2024, 9, 2, 10, 30),
            'location': 'Главный корпус',
            'room': '204',
            'is_recurring': True,
            'recurrence_pattern': 'weekly_monday'
        },
        {
            'schedule_type': 'exam',
            'title': 'Экзамен по Истории Казахстана',
            'faculty': 'Гуманитарный',
            'course_code': 'HIST102',
            'group_name': 'ГУМ-21-2',
            'instructor': 'Петрова А.С.',
            'start_time': datetime(2024, 12, 15, 9, 0),
            'end_time': datetime(2024, 12, 15, 11, 0),
            'location': 'Главный корпус',
            'room': '105'
        }
    ]
    
    # Sample job postings
    jobs = [
        {
            'title': 'Стажер-программист',
            'company_name': 'ТОО "IT Solutions"',
            'company_website': 'https://itsolutions.kz',
            'job_type': 'internship',
            'employment_type': 'hybrid',
            'description': 'Ищем мотивированного стажера для работы над веб-проектами',
            'requirements': 'Знание Python, HTML, CSS, JavaScript',
            'salary_range': '100 000 - 150 000 тенге',
            'location': 'Кызылорда',
            'target_faculties': ['Естественно-технических наук', 'Информационных технологий'],
            'target_skills': ['Python', 'JavaScript', 'HTML', 'CSS'],
            'experience_level': 'entry',
            'application_email': 'hr@itsolutions.kz',
            'application_deadline': datetime(2024, 10, 30),
            'is_internal': False
        }
    ]
    
    # Sample housing rooms
    rooms = [
        {
            'building': 'А',
            'floor': 2,
            'room_number': '201',
            'room_type': 'double',
            'capacity': 2,
            'current_occupancy': 1,
            'amenities': ['wifi', 'furniture', 'heating'],
            'monthly_cost': 25000.0,
            'deposit_amount': 50000.0,
            'status': 'available'
        },
        {
            'building': 'Б',
            'floor': 3,
            'room_number': '305',
            'room_type': 'triple',
            'capacity': 3,
            'current_occupancy': 3,
            'amenities': ['wifi', 'furniture', 'heating', 'refrigerator'],
            'monthly_cost': 20000.0,
            'deposit_amount': 40000.0,
            'status': 'occupied'
        }
    ]
    
    try:
        # Add templates
        for template_data in templates:
            template = DocumentTemplate(**template_data)
            template.created_by = 1  # Assuming admin user with ID 1 exists
            db.session.add(template)
        
        # Add schedules
        for schedule_data in schedules:
            schedule = Schedule(**schedule_data)
            db.session.add(schedule)
        
        # Add job postings
        for job_data in jobs:
            job = JobPosting(**job_data)
            job.posted_by = 1  # Assuming admin user with ID 1 exists
            db.session.add(job)
        
        # Add housing rooms
        for room_data in rooms:
            room = HousingRoom(**room_data)
            db.session.add(room)
        
        # Commit all changes
        db.session.commit()
        print("Sample data added successfully!")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error adding sample data: {e}")
        raise

if __name__ == '__main__':
    migrate_database()