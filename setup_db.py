def init_default_data():
    """Initialize database with default data"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Import here to avoid circular imports
        from models import Category, FAQ, AdminUser, db
        from app import create_app
        
        # Ensure we're within application context
        app = create_app()
        with app.app_context():
        
        # Check if data already exists
            if Category.query.first() is not None:
                logger.info("Default data already exists, skipping initialization")
                return
            
            # Create default categories
            categories_data = [
                {
                    'name_ru': 'Поступление',
                    'name_kz': 'Түсу',
                    'description_ru': 'Вопросы о поступлении в университет',
                    'description_kz': 'Университетке түсу туралы сұрақтар'
                },
                {
                    'name_ru': 'Документы',
                    'name_kz': 'Құжаттар',
                    'description_ru': 'Необходимые документы для поступления',
                    'description_kz': 'Түсу үшін қажетті құжаттар'
                },
                {
                    'name_ru': 'Программы обучения',
                    'name_kz': 'Оқу бағдарламалары',
                    'description_ru': 'Информация о специальностях и программах',
                    'description_kz': 'Мамандықтар мен бағдарламалар туралы ақпарат'
                },
                {
                    'name_ru': 'Стоимость обучения',
                    'name_kz': 'Оқу құны',
                    'description_ru': 'Информация о стоимости обучения',
                    'description_kz': 'Оқу құны туралы ақпарат'
                }
            ]
            
            categories = []
            for cat_data in categories_data:
                category = Category(**cat_data)
                db.session.add(category)
                categories.append(category)
            
            db.session.flush()  # Get IDs for categories
            
            # Create default FAQs
            faqs_data = [
                {
                    'question_ru': 'Как поступить в университет Болашак?',
                    'question_kz': 'Болашақ университетіне қалай түсуге болады?',
                    'answer_ru': 'Для поступления необходимо подать документы в приемную комиссию, сдать вступительные экзамены или предоставить результаты ЕНТ.',
                    'answer_kz': 'Түсу үшін қабылдау комиссиясына құжаттар тапсыру, кіру емтихандарын тапсыру немесе БТ нәтижелерін ұсыну қажет.',
                    'category_id': categories[0].id
                },
                {
                    'question_ru': 'Какие документы нужны для поступления?',
                    'question_kz': 'Түсу үшін қандай құжаттар қажет?',
                    'answer_ru': 'Аттестат о среднем образовании, справка о состоянии здоровья, фотографии 3x4, копия удостоверения личности.',
                    'answer_kz': 'Орта білім туралы аттестат, денсаулық жағдайы туралы анықтама, 3x4 фотосуреттер, жеке куәліктің көшірмесі.',
                    'category_id': categories[1].id
                },
                {
                    'question_ru': 'Какие специальности есть в университете?',
                    'question_kz': 'Университетте қандай мамандықтар бар?',
                    'answer_ru': 'В университете есть специальности по IT, экономике, педагогике, медицине, инженерии и другим направлениям.',
                    'answer_kz': 'Университетте IT, экономика, педагогика, медицина, инженерия және басқа да бағыттар бойынша мамандықтар бар.',
                    'category_id': categories[2].id
                },
                {
                    'question_ru': 'Сколько стоит обучение?',
                    'question_kz': 'Оқу қанша тұрады?',
                    'answer_ru': 'Стоимость обучения зависит от специальности. Подробную информацию можно получить в приемной комиссии.',
                    'answer_kz': 'Оқу құны мамандыққа байланысты. Толық ақпаратты қабылдау комиссиясынан алуға болады.',
                    'category_id': categories[3].id
                }
            ]
            
            for faq_data in faqs_data:
                faq = FAQ(**faq_data)
                db.session.add(faq)
            
            # Create default admin user
            admin = AdminUser(
                username='admin',
                email='admin@bolashak.edu.kz'
            )
            admin.set_password('admin123')  # Change this in production!
            db.session.add(admin)
            
            db.session.commit()
            logger.info("Default data initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing default data: {str(e)}")
        try:
            from models import db
            db.session.rollback()
        except:
            pass
