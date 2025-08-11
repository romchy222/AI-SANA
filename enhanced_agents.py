"""
Enhanced agent functionalities for AI-SANA system
Implements specific capabilities for each agent type as described in requirements
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import logging

from models import (
    db, DocumentTemplate, StudentRequest, Schedule, JobPosting, 
    HousingRoom, HousingAssignment, Notification, FAQ, AgentKnowledgeBase
)

logger = logging.getLogger(__name__)

class AgentEnhancedFunctionality:
    """Base class for enhanced agent functionality"""
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
    
    def get_templates(self, language: str = 'ru') -> List[Dict]:
        """Get document templates for this agent"""
        templates = DocumentTemplate.query.filter_by(
            agent_type=self.agent_type, 
            is_active=True
        ).all()
        
        return [{
            'id': t.id,
            'name': t.get_name(language),
            'category': t.category,
            'instructions': t.get_instructions(language),
            'required_fields': t.required_fields,
            'file_path': t.file_path
        } for t in templates]
    
    def search_knowledge_base(self, query: str, language: str = 'ru', limit: int = 5) -> List[Dict]:
        """Search agent-specific knowledge base"""
        knowledge = AgentKnowledgeBase.query.filter_by(
            agent_type=self.agent_type,
            is_active=True
        ).filter(
            AgentKnowledgeBase.keywords.contains(query.lower())
        ).order_by(AgentKnowledgeBase.priority).limit(limit).all()
        
        return [{
            'title': k.title,
            'content': k.get_content(language),
            'category': k.category,
            'priority': k.priority
        } for k in knowledge]

class AIAbiturEnhanced(AgentEnhancedFunctionality):
    """Enhanced functionality for AI-Abitur agent"""
    
    def __init__(self):
        super().__init__('ai_abitur')
    
    def get_admission_info(self, language: str = 'ru') -> Dict:
        """Get comprehensive admission information"""
        return {
            'contact_info': {
                'phone': '+7 (7242) 123-457',
                'email': 'admission@bolashak.kz',
                'address': 'г. Кызылорда, ул. Университетская, 1',
                'working_hours': 'Пн-Пт 9:00-18:00'
            },
            'important_dates': [
                {'date': '2024-06-01', 'event': 'Начало приема документов'},
                {'date': '2024-07-15', 'event': 'Окончание приема документов'},
                {'date': '2024-08-01', 'event': 'Публикация результатов'},
                {'date': '2024-08-20', 'event': 'Начало учебного года'}
            ],
            'required_documents': [
                'Аттестат о среднем образовании',
                'Справка о состоянии здоровья',
                'Фотографии 3x4 (6 шт)',
                'Копия удостоверения личности',
                'Результаты ЕНТ'
            ],
            'faculties': [
                {'name': 'Естественно-технических наук', 'programs': 15},
                {'name': 'Гуманитарный', 'programs': 12},
                {'name': 'Экономический', 'programs': 8},
                {'name': 'Педагогический', 'programs': 10}
            ]
        }
    
    def get_application_templates(self, language: str = 'ru') -> List[Dict]:
        """Get admission-related document templates"""
        return self.get_templates(language)
    
    def track_application_status(self, application_id: str) -> Dict:
        """Track application status (simulated)"""
        # In a real system, this would check actual application database
        return {
            'application_id': application_id,
            'status': 'under_review',
            'submitted_date': '2024-06-15',
            'last_updated': '2024-06-20',
            'next_step': 'Ожидание результатов ЕНТ',
            'estimated_decision_date': '2024-08-01'
        }
    
    def get_program_requirements(self, program_name: str, language: str = 'ru') -> Dict:
        """Get specific program requirements"""
        # This would typically come from a database
        programs = {
            'информационные технологии': {
                'min_ent_score': 75,
                'required_subjects': ['Математика', 'Физика', 'Информатика'],
                'duration': '4 года',
                'language': 'Казахский/Русский',
                'tuition_fee': '400,000 тенге/год'
            },
            'экономика': {
                'min_ent_score': 70,
                'required_subjects': ['Математика', 'Обществознание', 'История'],
                'duration': '4 года',
                'language': 'Казахский/Русский',
                'tuition_fee': '350,000 тенге/год'
            }
        }
        
        program_key = program_name.lower()
        return programs.get(program_key, {
            'message': f'Информация по программе "{program_name}" не найдена. Обратитесь в приемную комиссию.'
        })

class KadrAIEnhanced(AgentEnhancedFunctionality):
    """Enhanced functionality for KadrAI agent"""
    
    def __init__(self):
        super().__init__('kadrai')
    
    def get_hr_procedures(self, language: str = 'ru') -> Dict:
        """Get HR procedures and regulations"""
        return {
            'vacation_policy': {
                'annual_days': 28,
                'advance_notice': '14 дней',
                'approval_process': 'Подача заявления → Согласование с руководителем → Приказ',
                'carryover_limit': '7 дней'
            },
            'transfer_procedures': {
                'internal_transfer': 'Заявление + согласие принимающего подразделения',
                'external_transfer': 'Заявление + справка с нового места работы',
                'processing_time': '10 рабочих дней'
            },
            'salary_info': {
                'payment_date': '15 число каждого месяца',
                'bonus_periods': ['Новый год', 'День университета', 'По итогам года'],
                'salary_review': 'Ежегодно в сентябре'
            }
        }
    
    def get_leave_calendar(self, department: str = None, language: str = 'ru') -> List[Dict]:
        """Get vacation/leave schedule"""
        # This would typically come from HR database
        return [
            {
                'employee': 'Иванов И.И.',
                'department': 'ИТ отдел',
                'leave_type': 'annual',
                'start_date': '2024-07-01',
                'end_date': '2024-07-14',
                'status': 'approved'
            },
            {
                'employee': 'Петрова А.С.',
                'department': 'Бухгалтерия',
                'leave_type': 'sick',
                'start_date': '2024-06-20',
                'end_date': '2024-06-25',
                'status': 'completed'
            }
        ]
    
    def submit_hr_request(self, request_data: Dict) -> Dict:
        """Submit HR-related request"""
        try:
            # Generate unique request ID
            request_id = f"HR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Create request record
            request = StudentRequest(
                request_id=request_id,
                student_name=request_data.get('employee_name'),
                student_email=request_data.get('email'),
                request_type='hr',
                category=request_data.get('request_type'),
                title=request_data.get('title'),
                description=request_data.get('description'),
                status='submitted',
                assigned_to='Отдел кадров'
            )
            
            db.session.add(request)
            db.session.commit()
            
            return {
                'success': True,
                'request_id': request_id,
                'message': 'Заявка успешно подана',
                'estimated_processing_time': '3-5 рабочих дней'
            }
            
        except Exception as e:
            logger.error(f"Error submitting HR request: {e}")
            return {
                'success': False,
                'message': 'Ошибка при подаче заявки. Попробуйте позже.'
            }

class UniNavEnhanced(AgentEnhancedFunctionality):
    """Enhanced functionality for UniNav agent"""
    
    def __init__(self):
        super().__init__('uninav')
    
    def get_current_schedule(self, group: str = None, language: str = 'ru') -> List[Dict]:
        """Get current class schedule"""
        query = Schedule.query.filter_by(
            schedule_type='class',
            is_active=True,
            is_cancelled=False
        )
        
        if group:
            query = query.filter_by(group_name=group)
        
        # Get schedule for current week
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        schedules = query.filter(
            Schedule.start_time >= week_start,
            Schedule.start_time <= week_end
        ).order_by(Schedule.start_time).all()
        
        return [{
            'title': s.title,
            'instructor': s.instructor,
            'start_time': s.start_time.strftime('%Y-%m-%d %H:%M'),
            'end_time': s.end_time.strftime('%Y-%m-%d %H:%M'),
            'location': f"{s.location}, ауд. {s.room}",
            'course_code': s.course_code,
            'group': s.group_name
        } for s in schedules]
    
    def get_exam_schedule(self, group: str = None, language: str = 'ru') -> List[Dict]:
        """Get exam schedule"""
        query = Schedule.query.filter_by(
            schedule_type='exam',
            is_active=True,
            is_cancelled=False
        )
        
        if group:
            query = query.filter_by(group_name=group)
        
        # Get upcoming exams
        today = datetime.now()
        exams = query.filter(
            Schedule.start_time >= today
        ).order_by(Schedule.start_time).limit(10).all()
        
        return [{
            'subject': s.title,
            'instructor': s.instructor,
            'date': s.start_time.strftime('%Y-%m-%d'),
            'time': f"{s.start_time.strftime('%H:%M')} - {s.end_time.strftime('%H:%M')}",
            'location': f"{s.location}, ауд. {s.room}",
            'course_code': s.course_code,
            'group': s.group_name
        } for s in exams]
    
    def submit_academic_request(self, request_data: Dict) -> Dict:
        """Submit academic-related request"""
        try:
            request_id = f"AC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            request = StudentRequest(
                request_id=request_id,
                student_id=request_data.get('student_id'),
                student_name=request_data.get('student_name'),
                student_email=request_data.get('email'),
                request_type='academic',
                category=request_data.get('request_type'),
                title=request_data.get('title'),
                description=request_data.get('description'),
                status='submitted',
                assigned_to='Деканат'
            )
            
            db.session.add(request)
            db.session.commit()
            
            return {
                'success': True,
                'request_id': request_id,
                'message': 'Заявка успешно подана в деканат',
                'estimated_processing_time': '5-7 рабочих дней'
            }
            
        except Exception as e:
            logger.error(f"Error submitting academic request: {e}")
            return {
                'success': False,
                'message': 'Ошибка при подаче заявки. Попробуйте позже.'
            }
    
    def get_faculty_info(self, faculty_name: str = None, language: str = 'ru') -> Dict:
        """Get faculty and instructor information"""
        faculties = {
            'естественно-технических наук': {
                'dean': 'Сидоров С.С.',
                'dean_email': 'siidorov@bolashak.kz',
                'office': 'Главный корпус, каб. 301',
                'phone': '+7 (7242) 123-461',
                'departments': [
                    'Кафедра математики и информатики',
                    'Кафедра физики и техники',
                    'Кафедра химии и биологии'
                ]
            },
            'гуманитарный': {
                'dean': 'Жанбосынова А.К.',
                'dean_email': 'zhanbosynova@bolashak.kz',
                'office': 'Главный корпус, каб. 201',
                'phone': '+7 (7242) 123-462',
                'departments': [
                    'Кафедра казахского языка и литературы',
                    'Кафедра истории и философии',
                    'Кафедра иностранных языков'
                ]
            }
        }
        
        if faculty_name:
            return faculties.get(faculty_name.lower(), {
                'message': f'Информация о факультете "{faculty_name}" не найдена'
            })
        
        return {'faculties': list(faculties.keys())}

class CareerNavigatorEnhanced(AgentEnhancedFunctionality):
    """Enhanced functionality for CareerNavigator agent"""
    
    def __init__(self):
        super().__init__('career_navigator')
    
    def search_jobs(self, skills: List[str] = None, location: str = None, 
                   job_type: str = None, language: str = 'ru') -> List[Dict]:
        """Search for job postings"""
        query = JobPosting.query.filter_by(is_active=True)
        
        if location:
            query = query.filter(JobPosting.location.contains(location))
        
        if job_type:
            query = query.filter_by(job_type=job_type)
        
        jobs = query.order_by(JobPosting.created_at.desc()).limit(10).all()
        
        return [{
            'id': j.id,
            'title': j.title,
            'company': j.company_name,
            'location': j.location,
            'type': j.job_type,
            'employment_type': j.employment_type,
            'salary_range': j.salary_range,
            'deadline': j.application_deadline.strftime('%Y-%m-%d') if j.application_deadline else None,
            'is_internal': j.is_internal,
            'required_skills': j.target_skills,
            'experience_level': j.experience_level
        } for j in jobs]
    
    def get_career_recommendations(self, student_profile: Dict, language: str = 'ru') -> Dict:
        """Get personalized career recommendations"""
        skills = student_profile.get('skills', [])
        faculty = student_profile.get('faculty', '')
        
        # Simple recommendation logic (would be more sophisticated in production)
        recommendations = {
            'job_matches': self.search_jobs(skills=skills),
            'skill_development': [],
            'career_paths': []
        }
        
        # Skill development suggestions
        if 'python' in [s.lower() for s in skills]:
            recommendations['skill_development'].append({
                'skill': 'Django/Flask',
                'reason': 'Дополнит ваши знания Python для веб-разработки',
                'resources': ['Онлайн курсы', 'Практические проекты']
            })
        
        # Career path suggestions based on faculty
        if 'технических' in faculty.lower():
            recommendations['career_paths'] = [
                'Системный администратор',
                'Веб-разработчик',
                'Инженер по данным',
                'DevOps инженер'
            ]
        
        return recommendations
    
    def create_resume_template(self, student_data: Dict, language: str = 'ru') -> str:
        """Generate resume template"""
        template = f"""
# {student_data.get('name', '[Ваше имя]')}

## Контактная информация
- Email: {student_data.get('email', '[email]')}
- Телефон: {student_data.get('phone', '[телефон]')}
- LinkedIn: {student_data.get('linkedin', '[профиль LinkedIn]')}

## Образование
**Кызылординский университет "Болашак"**
- Факультет: {student_data.get('faculty', '[факультет]')}
- Специальность: {student_data.get('major', '[специальность]')}
- Год окончания: {student_data.get('graduation_year', '[год]')}

## Навыки
{', '.join(student_data.get('skills', ['[укажите навыки]']))}

## Опыт работы
[Опишите ваш опыт работы]

## Проекты
[Опишите ваши проекты]

## Дополнительная информация
[Языки, сертификаты, хобби]
        """
        
        return template.strip()
    
    def get_interview_tips(self, job_type: str = None, language: str = 'ru') -> List[Dict]:
        """Get interview preparation tips"""
        general_tips = [
            {
                'category': 'Подготовка',
                'tips': [
                    'Изучите компанию и должность',
                    'Подготовьте ответы на типичные вопросы',
                    'Подготовьте вопросы для интервьюера'
                ]
            },
            {
                'category': 'Во время интервью',
                'tips': [
                    'Приходите вовремя',
                    'Одевайтесь профессионально',
                    'Поддерживайте зрительный контакт',
                    'Будьте конкретными в ответах'
                ]
            }
        ]
        
        if job_type == 'internship':
            general_tips.append({
                'category': 'Для стажировки',
                'tips': [
                    'Подчеркните желание учиться',
                    'Покажите энтузиазм',
                    'Расскажите о проектах из университета'
                ]
            })
        
        return general_tips

class UniRoomEnhanced(AgentEnhancedFunctionality):
    """Enhanced functionality for UniRoom agent"""
    
    def __init__(self):
        super().__init__('uniroom')
    
    def get_available_rooms(self, room_type: str = None, language: str = 'ru') -> List[Dict]:
        """Get available dormitory rooms"""
        query = HousingRoom.query.filter_by(
            status='available',
            is_active=True
        )
        
        if room_type:
            query = query.filter_by(room_type=room_type)
        
        rooms = query.order_by(HousingRoom.building, HousingRoom.room_number).all()
        
        return [{
            'id': r.id,
            'building': r.building,
            'room_number': r.room_number,
            'type': r.room_type,
            'capacity': r.capacity,
            'available_spaces': r.capacity - r.current_occupancy,
            'monthly_cost': r.monthly_cost,
            'deposit': r.deposit_amount,
            'amenities': r.amenities,
            'floor': r.floor
        } for r in rooms]
    
    def submit_housing_request(self, request_data: Dict) -> Dict:
        """Submit housing-related request"""
        try:
            request_id = f"HS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            request = StudentRequest(
                request_id=request_id,
                student_id=request_data.get('student_id'),
                student_name=request_data.get('student_name'),
                student_email=request_data.get('email'),
                request_type='housing',
                category=request_data.get('request_type'),  # settlement, relocation, maintenance
                title=request_data.get('title'),
                description=request_data.get('description'),
                status='submitted',
                assigned_to='Администрация общежития'
            )
            
            db.session.add(request)
            db.session.commit()
            
            return {
                'success': True,
                'request_id': request_id,
                'message': 'Заявка успешно подана в администрацию общежития',
                'estimated_processing_time': '3-5 рабочих дней'
            }
            
        except Exception as e:
            logger.error(f"Error submitting housing request: {e}")
            return {
                'success': False,
                'message': 'Ошибка при подаче заявки. Попробуйте позже.'
            }
    
    def get_housing_rules(self, language: str = 'ru') -> Dict:
        """Get dormitory rules and regulations"""
        return {
            'general_rules': [
                'Соблюдение тишины с 22:00 до 7:00',
                'Запрет на курение в здании',
                'Регистрация гостей в администрации',
                'Содержание комнаты в чистоте'
            ],
            'payment_rules': {
                'monthly_payment_date': '5 число каждого месяца',
                'late_fee': '10% за каждый день просрочки',
                'deposit_return': 'В течение 30 дней после выселения'
            },
            'maintenance_requests': {
                'urgent_issues': 'Немедленно обратиться в администрацию',
                'routine_maintenance': 'Подать заявку через систему',
                'response_time': '24-48 часов'
            },
            'contact_info': {
                'admin_office': 'Общежитие А, 1 этаж',
                'phone': '+7 (7242) 123-459',
                'emergency_phone': '+7 (7242) 123-999',
                'working_hours': '8:00-20:00 ежедневно'
            }
        }
    
    def check_occupancy_status(self, room_id: int = None, building: str = None) -> Dict:
        """Check room occupancy status"""
        if room_id:
            room = HousingRoom.query.get(room_id)
            if room:
                assignments = HousingAssignment.query.filter_by(
                    room_id=room_id,
                    status='active'
                ).all()
                
                return {
                    'room': f"{room.building}-{room.room_number}",
                    'capacity': room.capacity,
                    'current_occupancy': len(assignments),
                    'available_spaces': room.capacity - len(assignments),
                    'residents': [a.student_name for a in assignments],
                    'status': room.status
                }
        
        # Get building-wide statistics
        if building:
            rooms = HousingRoom.query.filter_by(building=building, is_active=True).all()
            total_capacity = sum(r.capacity for r in rooms)
            total_occupied = sum(r.current_occupancy for r in rooms)
            
            return {
                'building': building,
                'total_rooms': len(rooms),
                'total_capacity': total_capacity,
                'total_occupied': total_occupied,
                'occupancy_rate': f"{(total_occupied/total_capacity*100):.1f}%" if total_capacity > 0 else "0%"
            }
        
        return {'error': 'Необходимо указать room_id или building'}
    
    def get_maintenance_schedule(self, building: str = None, language: str = 'ru') -> List[Dict]:
        """Get maintenance and inspection schedule"""
        # This would typically come from a maintenance system
        schedule = [
            {
                'date': '2024-07-15',
                'time': '10:00-16:00',
                'type': 'Плановая проверка электропроводки',
                'building': 'А',
                'affected_floors': [1, 2, 3],
                'contact': 'Технический отдел: +7 (7242) 123-460'
            },
            {
                'date': '2024-07-20',
                'time': '9:00-12:00',
                'type': 'Ремонт системы отопления',
                'building': 'Б',
                'affected_floors': [2],
                'contact': 'Администрация общежития: +7 (7242) 123-459'
            }
        ]
        
        if building:
            schedule = [s for s in schedule if s['building'] == building]
        
        return schedule