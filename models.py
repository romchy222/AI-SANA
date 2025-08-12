# Импорт необходимых модулей
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

# Initialize db object that will be imported by app.py
db = SQLAlchemy()

class Category(db.Model):
    """Модель категории для FAQ"""
    __tablename__ = 'categories'
    
    # Первичный ключ
    id = db.Column(db.Integer, primary_key=True)
    # Название категории на русском языке
    name_ru = db.Column(db.String(100), nullable=False)
    # Название категории на казахском языке
    name_kz = db.Column(db.String(100), nullable=False)
    # Описание категории на русском языке
    description_ru = db.Column(db.Text)
    # Описание категории на казахском языке
    description_kz = db.Column(db.Text)
    # Дата создания записи
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связь один-ко-многим с FAQ
    faqs = db.relationship('FAQ', backref='category', lazy=True)
    
    def __repr__(self):
        """Строковое представление категории"""
        return f'<Category {self.name_ru}>'

class FAQ(db.Model):
    """Модель часто задаваемых вопросов"""
    __tablename__ = 'faqs'
    
    # Первичный ключ
    id = db.Column(db.Integer, primary_key=True)
    # Вопрос на русском языке
    question_ru = db.Column(db.Text, nullable=False)
    # Вопрос на казахском языке
    question_kz = db.Column(db.Text, nullable=False)
    # Ответ на русском языке
    answer_ru = db.Column(db.Text, nullable=False)
    # Ответ на казахском языке
    answer_kz = db.Column(db.Text, nullable=False)
    # Внешний ключ на категорию
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    # Статус активности FAQ
    is_active = db.Column(db.Boolean, default=True)
    # Дата создания записи
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Дата последнего обновления
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        """Строковое представление FAQ"""
        return f'<FAQ {self.question_ru[:50]}...>'

class UserQuery(db.Model):
    __tablename__ = 'user_queries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(5), nullable=False, default='ru')
    response_time = db.Column(db.Float)  # Response time in seconds
    
    # Agent tracking fields
    agent_type = db.Column(db.String(50))  # Type of agent that handled the query
    agent_name = db.Column(db.String(100))  # Name of the agent
    agent_confidence = db.Column(db.Float)  # Confidence score of the selected agent
    context_used = db.Column(db.Boolean, default=False)  # Whether FAQ context was used
    
    # Rating system fields
    user_rating = db.Column(db.String(10))  # 'like', 'dislike', or null
    rating_timestamp = db.Column(db.DateTime)  # When rating was given
    
    session_id = db.Column(db.String(100))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserQuery {self.user_message[:30]}...>'

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # pdf, doc, txt, etc.
    file_size = db.Column(db.Integer)  # Size in bytes
    content_text = db.Column(db.Text)  # Extracted text content
    is_processed = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Document {self.title}>'

class WebSource(db.Model):
    __tablename__ = 'web_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    content_text = db.Column(db.Text)  # Extracted text content
    last_scraped = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    scrape_frequency = db.Column(db.String(20), default='daily')  # daily, weekly, manual
    added_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<WebSource {self.title}>'

class KnowledgeBase(db.Model):
    __tablename__ = 'knowledge_base'
    
    id = db.Column(db.Integer, primary_key=True)
    source_type = db.Column(db.String(20), nullable=False)  # 'document', 'web', 'manual'
    source_id = db.Column(db.Integer)  # Foreign key to Document or WebSource
    content_chunk = db.Column(db.Text, nullable=False)
    extra_data = db.Column(db.JSON)  # Additional metadata like page numbers, sections, etc.
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<KnowledgeBase {self.source_type}:{self.source_id}>'

class AgentKnowledgeBase(db.Model):
    """Agent-specific knowledge base entries"""
    __tablename__ = 'agent_knowledge_base'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_type = db.Column(db.String(50), nullable=False)  # Type of agent this knowledge belongs to
    title = db.Column(db.String(200), nullable=False)
    content_ru = db.Column(db.Text, nullable=False)  # Content in Russian
    content_kz = db.Column(db.Text, nullable=False)  # Content in Kazakh
    content_en = db.Column(db.Text)  # Content in English (optional)
    keywords = db.Column(db.String(500))  # Search keywords
    priority = db.Column(db.Integer, default=1)  # Priority for ordering (1=highest)
    category = db.Column(db.String(100))  # Knowledge category
    tags = db.Column(db.String(300))  # Comma-separated tags
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)  # Featured knowledge entries
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_content(self, language='ru'):
        """Get content in specific language with fallback"""
        if language == 'kz' and self.content_kz:
            return self.content_kz
        elif language == 'en' and self.content_en:
            return self.content_en
        else:
            return self.content_ru
    
    def __repr__(self):
        return f'<AgentKnowledgeBase {self.agent_type}:{self.title}>'

class AgentType(db.Model):
    """Model for agent types and their configurations"""
    __tablename__ = 'agent_types'
    
    id = db.Column(db.Integer, primary_key=True)
    type_code = db.Column(db.String(50), unique=True, nullable=False)  # e.g., 'admission', 'scholarship'
    name_ru = db.Column(db.String(100), nullable=False)  # Name in Russian
    name_kz = db.Column(db.String(100), nullable=False)  # Name in Kazakh
    name_en = db.Column(db.String(100))  # Name in English
    description_ru = db.Column(db.Text)  # Description in Russian
    description_kz = db.Column(db.Text)  # Description in Kazakh
    description_en = db.Column(db.Text)  # Description in English
    system_prompt_ru = db.Column(db.Text)  # System prompt in Russian
    system_prompt_kz = db.Column(db.Text)  # System prompt in Kazakh
    system_prompt_en = db.Column(db.Text)  # System prompt in English
    icon_class = db.Column(db.String(50))  # CSS icon class
    color_scheme = db.Column(db.String(20))  # Color scheme identifier
    priority = db.Column(db.Integer, default=1)  # Display priority
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with knowledge base
    knowledge_entries = db.relationship('AgentKnowledgeBase', 
                                      foreign_keys='AgentKnowledgeBase.agent_type',
                                      primaryjoin='AgentType.type_code == AgentKnowledgeBase.agent_type',
                                      backref='agent_type_obj',
                                      lazy='dynamic')
    
    def get_name(self, language='ru'):
        """Get name in specific language with fallback"""
        if language == 'kz' and self.name_kz:
            return self.name_kz
        elif language == 'en' and self.name_en:
            return self.name_en
        else:
            return self.name_ru
    
    def get_description(self, language='ru'):
        """Get description in specific language with fallback"""
        if language == 'kz' and self.description_kz:
            return self.description_kz
        elif language == 'en' and self.description_en:
            return self.description_en
        else:
            return self.description_ru
    
    def get_system_prompt(self, language='ru'):
        """Get system prompt in specific language with fallback"""
        if language == 'kz' and self.system_prompt_kz:
            return self.system_prompt_kz
        elif language == 'en' and self.system_prompt_en:
            return self.system_prompt_en
        else:
            return self.system_prompt_ru
    
    def __repr__(self):
        return f'<AgentType {self.type_code}:{self.name_ru}>'

class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    documents = db.relationship('Document', backref='uploader', lazy=True)
    web_sources = db.relationship('WebSource', backref='creator', lazy=True)
    agent_knowledge = db.relationship('AgentKnowledgeBase', backref='creator', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<AdminUser {self.username}>'

# Enhanced models for specific agent functionality

class DocumentTemplate(db.Model):
    """Templates for various university documents and forms"""
    __tablename__ = 'document_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name_ru = db.Column(db.String(200), nullable=False)
    name_kz = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200))
    category = db.Column(db.String(100), nullable=False)  # admission, hr, student, housing, etc.
    agent_type = db.Column(db.String(50), nullable=False)  # Which agent this template belongs to
    template_content = db.Column(db.Text, nullable=False)  # Template content in HTML/Markdown
    required_fields = db.Column(db.JSON)  # JSON array of required field names
    instructions_ru = db.Column(db.Text)  # Instructions in Russian
    instructions_kz = db.Column(db.Text)  # Instructions in Kazakh
    file_path = db.Column(db.String(500))  # Path to downloadable template file
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_name(self, language='ru'):
        if language == 'kz' and self.name_kz:
            return self.name_kz
        elif language == 'en' and self.name_en:
            return self.name_en
        return self.name_ru
    
    def get_instructions(self, language='ru'):
        if language == 'kz' and self.instructions_kz:
            return self.instructions_kz
        return self.instructions_ru
    
    def __repr__(self):
        return f'<DocumentTemplate {self.category}:{self.name_ru}>'

class StudentRequest(db.Model):
    """Tracking system for student requests (HR, housing, academic)"""
    __tablename__ = 'student_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.String(50), unique=True, nullable=False)  # Human-readable ID
    student_id = db.Column(db.String(50))  # Student ID number
    student_name = db.Column(db.String(200))
    student_email = db.Column(db.String(120))
    request_type = db.Column(db.String(50), nullable=False)  # housing, hr, academic, etc.
    category = db.Column(db.String(100))  # specific subcategory
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='submitted')  # submitted, in_progress, approved, rejected, completed
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    
    # Document attachments
    attached_documents = db.Column(db.JSON)  # Array of document paths/names
    
    # Processing information
    assigned_to = db.Column(db.String(200))  # Department/person assigned to
    processed_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    processing_notes = db.Column(db.Text)
    
    # Timestamps
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<StudentRequest {self.request_id}:{self.title}>'

class Schedule(db.Model):
    """University schedules for classes, exams, events"""
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    schedule_type = db.Column(db.String(50), nullable=False)  # class, exam, event, meeting
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    
    # Academic information
    faculty = db.Column(db.String(100))
    department = db.Column(db.String(100))
    course_code = db.Column(db.String(50))
    group_name = db.Column(db.String(50))
    instructor = db.Column(db.String(200))
    
    # Time and location
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    room = db.Column(db.String(50))
    
    # Recurrence
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_pattern = db.Column(db.String(100))  # weekly, daily, etc.
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_cancelled = db.Column(db.Boolean, default=False)
    cancellation_reason = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Schedule {self.schedule_type}:{self.title}>'

class JobPosting(db.Model):
    """Job postings for career services"""
    __tablename__ = 'job_postings'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    company_website = db.Column(db.String(500))
    job_type = db.Column(db.String(50), nullable=False)  # internship, part_time, full_time, contract
    employment_type = db.Column(db.String(50))  # remote, onsite, hybrid
    
    # Job details
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    benefits = db.Column(db.Text)
    salary_range = db.Column(db.String(100))
    location = db.Column(db.String(200))
    
    # Targeting
    target_faculties = db.Column(db.JSON)  # Array of faculty names
    target_skills = db.Column(db.JSON)  # Array of required skills
    experience_level = db.Column(db.String(50))  # entry, junior, mid, senior
    
    # Application details
    application_url = db.Column(db.String(500))
    application_email = db.Column(db.String(120))
    application_deadline = db.Column(db.DateTime)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    is_internal = db.Column(db.Boolean, default=False)  # Internal university position
    
    # Tracking
    views_count = db.Column(db.Integer, default=0)
    applications_count = db.Column(db.Integer, default=0)
    
    posted_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<JobPosting {self.company_name}:{self.title}>'

class HousingRoom(db.Model):
    """Dormitory room management"""
    __tablename__ = 'housing_rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    building = db.Column(db.String(50), nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    room_number = db.Column(db.String(20), nullable=False)
    room_type = db.Column(db.String(50), nullable=False)  # single, double, triple, etc.
    capacity = db.Column(db.Integer, nullable=False)
    current_occupancy = db.Column(db.Integer, default=0)
    
    # Room details
    amenities = db.Column(db.JSON)  # Array of amenities
    monthly_cost = db.Column(db.Float)
    deposit_amount = db.Column(db.Float)
    
    # Status
    status = db.Column(db.String(50), default='available')  # available, occupied, maintenance, reserved
    is_active = db.Column(db.Boolean, default=True)
    
    # Maintenance
    last_maintenance = db.Column(db.DateTime)
    next_maintenance = db.Column(db.DateTime)
    maintenance_notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<HousingRoom {self.building}-{self.room_number}>'

class HousingAssignment(db.Model):
    """Student housing assignments"""
    __tablename__ = 'housing_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), nullable=False)
    student_name = db.Column(db.String(200), nullable=False)
    student_email = db.Column(db.String(120))
    
    room_id = db.Column(db.Integer, db.ForeignKey('housing_rooms.id'), nullable=False)
    room = db.relationship('HousingRoom', backref='assignments')
    
    # Assignment details
    assignment_type = db.Column(db.String(50), default='regular')  # regular, temporary, emergency
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    
    # Status
    status = db.Column(db.String(50), default='active')  # active, completed, cancelled
    
    # Payment tracking
    monthly_payment = db.Column(db.Float)
    deposit_paid = db.Column(db.Float, default=0)
    last_payment_date = db.Column(db.DateTime)
    
    # Emergency contact
    emergency_contact_name = db.Column(db.String(200))
    emergency_contact_phone = db.Column(db.String(50))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<HousingAssignment {self.student_name}:{self.room.building}-{self.room.room_number}>'

class Notification(db.Model):
    """System notifications for various events"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    notification_type = db.Column(db.String(50), nullable=False)  # reminder, alert, info, warning
    target_audience = db.Column(db.String(100))  # all, students, staff, specific_group
    agent_type = db.Column(db.String(50))  # Which agent sends this notification
    
    # Content
    title_ru = db.Column(db.String(300), nullable=False)
    title_kz = db.Column(db.String(300), nullable=False)
    message_ru = db.Column(db.Text, nullable=False)
    message_kz = db.Column(db.Text, nullable=False)
    
    # Targeting
    target_users = db.Column(db.JSON)  # Array of specific user IDs/emails
    target_faculties = db.Column(db.JSON)  # Array of faculty names
    target_groups = db.Column(db.JSON)  # Array of group names
    
    # Scheduling
    send_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    # Status
    status = db.Column(db.String(50), default='draft')  # draft, scheduled, sent, expired
    is_urgent = db.Column(db.Boolean, default=False)
    
    # Tracking
    sent_count = db.Column(db.Integer, default=0)
    read_count = db.Column(db.Integer, default=0)
    
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_title(self, language='ru'):
        return self.title_kz if language == 'kz' else self.title_ru
    
    def get_message(self, language='ru'):
        return self.message_kz if language == 'kz' else self.message_ru
    
    def __repr__(self):
        return f'<Notification {self.notification_type}:{self.title_ru}>'
