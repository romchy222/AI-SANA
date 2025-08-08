#!/usr/bin/env python3
"""
Скрипт для инициализации базовых данных агентов и их баз знаний
"""

import logging
from app import create_app, db
from models import AgentType, AgentKnowledgeBase, AdminUser

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_agent_types():
    """Инициализация типов агентов"""
    
    agent_types_data = [
        {
            'type_code': 'ai_abitur',
            'name_ru': 'AI-Abitur',
            'name_kz': 'AI-Abitur',
            'name_en': 'AI-Abitur',
            'description_ru': 'Цифровой помощник для абитуриентов (поступающих в вуз). Помощь при поступлении, консультации по вопросам приёма.',
            'description_kz': 'Талапкерлерге арналған цифрлық көмекші. Түсу кезінде көмек көрсету, қабылдау мәселелері бойынша кеңес беру.',
            'description_en': 'Digital assistant for applicants (university entrants). Assistance with admission, consultations on admission issues.',
            'system_prompt_ru': 'Вы - цифровой помощник для абитуриентов университета "Болашак". Помогайте с вопросами поступления, консультациями по приёму, требованиями к документам, датами подачи заявлений и вступительными экзаменами.',
            'system_prompt_kz': 'Сіз "Болашақ" университетінің талапкерлеріне арналған цифрлық көмекшісіз. Түсу сұрақтары, қабылдау бойынша кеңес беру, құжаттарға қойылатын талаптар, өтініш беру мерзімдері және кіру емтихандары бойынша көмек көрсетіңіз.',
            'system_prompt_en': 'You are a digital assistant for applicants to Bolashak University. Help with admission questions, admission consultations, document requirements, application deadlines and entrance exams.',
            'icon_class': 'fas fa-graduation-cap',
            'color_scheme': 'primary',
            'priority': 1
        },
        {
            'type_code': 'kadrai',
            'name_ru': 'KadrAI',
            'name_kz': 'KadrAI',
            'name_en': 'KadrAI',
            'description_ru': 'Интеллектуальный помощник (чат-бот) для поддержки сотрудников и преподавателей в вопросах внутренних кадровых процедур. Консультации по кадровым процессам: отпуска, переводы, приказы и т.д.',
            'description_kz': 'Қызметкерлер мен оқытушыларды ішкі кадр рәсімдері мәселелерінде қолдауға арналған зияткерлік көмекші (чат-бот). Кадр процестері бойынша кеңес беру: демалыстар, ауыстырулар, бұйрықтар және т.б.',
            'description_en': 'Intelligent assistant (chatbot) to support employees and teachers in matters of internal HR procedures. Consultations on HR processes: vacations, transfers, orders, etc.',
            'system_prompt_ru': 'Вы - интеллектуальный помощник по кадровым вопросам университета "Болашак". Консультируйте сотрудников и преподавателей по внутренним кадровым процедурам, отпускам, переводам, приказам, трудовому праву и льготам.',
            'system_prompt_kz': 'Сіз "Болашақ" университетінің кадр мәселелері бойынша зияткерлік көмекшісіз. Қызметкерлер мен оқытушыларға ішкі кадр рәсімдері, демалыстар, ауыстырулар, бұйрықтар, еңбек құқығы және жеңілдіктер бойынша кеңес беріңіз.',
            'system_prompt_en': 'You are an intelligent HR assistant at Bolashak University. Consult employees and teachers on internal HR procedures, vacations, transfers, orders, labor law and benefits.',
            'icon_class': 'fas fa-users-cog',
            'color_scheme': 'info',
            'priority': 2
        },
        {
            'type_code': 'uninav',
            'name_ru': 'UniNav',
            'name_kz': 'UniNav',
            'name_en': 'UniNav',
            'description_ru': 'Интерактивный чат-ассистент, обеспечивающий полное сопровождение обучающегося по всем университетским процессам. Навигация по учебным вопросам, расписание, заявления, обращения и др.',
            'description_kz': 'Барлық университет процестері бойынша студентке толық сүйемелдеу беретін интерактивті чат-көмекші. Оқу мәселелері бойынша навигация, кесте, өтініштер, өтініштер және т.б.',
            'description_en': 'Interactive chat assistant providing complete support to students across all university processes. Navigation on academic issues, schedules, applications, appeals, etc.',
            'system_prompt_ru': 'Вы - интерактивный чат-ассистент для студентов университета "Болашак". Обеспечивайте полное сопровождение по учебным вопросам, расписанию, заявлениям, обращениям и всем университетским процессам.',
            'system_prompt_kz': 'Сіз "Болашақ" университетінің студенттеріне арналған интерактивті чат-көмекшісіз. Оқу мәселелері, кесте, өтініштер, өтініштер және барлық университет процестері бойынша толық сүйемелдеу беріңіз.',
            'system_prompt_en': 'You are an interactive chat assistant for Bolashak University students. Provide complete support on academic issues, schedules, applications, appeals and all university processes.',
            'icon_class': 'fas fa-compass',
            'color_scheme': 'success',
            'priority': 3
        },
        {
            'type_code': 'career_navigator',
            'name_ru': 'CareerNavigator',
            'name_kz': 'CareerNavigator',
            'name_en': 'CareerNavigator',
            'description_ru': 'Интеллектуальный чат-бот для содействия трудоустройству студентов и выпускников. Поиск вакансий, консультации по резюме, рекомендации по карьере.',
            'description_kz': 'Студенттер мен түлектердің жұмысқа орналасуына көмек көрсетуге арналған зияткерлік чат-бот. Бос жұмыс орындарын іздеу, резюме бойынша кеңес беру, мансап бойынша ұсыныстар.',
            'description_en': 'Intelligent chatbot to assist students and graduates with employment. Job search, resume consultations, career recommendations.',
            'system_prompt_ru': 'Вы - интеллектуальный чат-бот для содействия трудоустройству студентов и выпускников университета "Болашак". Помогайте с поиском вакансий, составлением резюме, карьерными рекомендациями и стажировками.',
            'system_prompt_kz': 'Сіз "Болашақ" университетінің студенттері мен түлектерінің жұмысқа орналасуына көмек көрсетуге арналған зияткерлік чат-ботсыз. Бос жұмыс орындарын іздеу, резюме құру, мансап ұсыныстары және тәжірибе орындары бойынша көмектесіңіз.',
            'system_prompt_en': 'You are an intelligent chatbot to assist students and graduates of Bolashak University with employment. Help with job search, resume writing, career recommendations and internships.',
            'icon_class': 'fas fa-briefcase',
            'color_scheme': 'warning',
            'priority': 4
        },
        {
            'type_code': 'uniroom',
            'name_ru': 'UniRoom',
            'name_kz': 'UniRoom',
            'name_en': 'UniRoom',
            'description_ru': 'Цифровой помощник для студентов, проживающих в общежитии. Заселение, переселение, решение бытовых вопросов, обращения в администрацию.',
            'description_kz': 'Жатақханада тұратын студенттерге арналған цифрлық көмекші. Орналасу, көшіру, тұрмыстық мәселелерді шешу, әкімшілікке өтініштер.',
            'description_en': 'Digital assistant for students living in dormitories. Settlement, relocation, solving household issues, appeals to administration.',
            'system_prompt_ru': 'Вы - цифровой помощник для студентов, проживающих в общежитии университета "Болашак". Помогайте с заселением, переселением, решением бытовых вопросов и обращениями в администрацию общежития.',
            'system_prompt_kz': 'Сіз "Болашақ" университетінің жатақханасында тұратын студенттерге арналған цифрлық көмекшісіз. Орналасу, көшіру, тұрмыстық мәселелерді шешу және жатақхана әкімшілігіне өтініштер жасауда көмектесіңіз.',
            'system_prompt_en': 'You are a digital assistant for students living in Bolashak University dormitory. Help with settlement, relocation, solving household issues and appeals to dormitory administration.',
            'icon_class': 'fas fa-home',
            'color_scheme': 'secondary',
            'priority': 5
        }
    ]
    
    for agent_data in agent_types_data:
        existing_agent = AgentType.query.filter_by(type_code=agent_data['type_code']).first()
        if not existing_agent:
            agent_type = AgentType(**agent_data)
            db.session.add(agent_type)
            logger.info(f"Создан тип агента: {agent_data['type_code']}")
        else:
            logger.info(f"Тип агента уже существует: {agent_data['type_code']}")
    
    db.session.commit()
    logger.info("Инициализация типов агентов завершена")

def init_knowledge_base():
    """Инициализация базы знаний агентов"""
    
    # Получаем или создаем админа для связи
    admin_user = AdminUser.query.first()
    if not admin_user:
        admin_user = AdminUser(
            username='system',
            email='system@bolashak.kz',
            password_hash='system',
            full_name='System Administrator'
        )
        db.session.add(admin_user)
        db.session.commit()
    
    knowledge_data = [
        # AI-Abitur Agent Knowledge
        {
            'agent_type': 'ai_abitur',
            'title': 'Требования для поступления',
            'content_ru': 'Для поступления в университет "Болашак" необходимы следующие документы:\n\n• Аттестат о среднем образовании или диплом о среднем специальном образовании\n• Копия удостоверения личности\n• Медицинская справка формы 086-У\n• 6 фотографий 3x4\n• Документы об участии в олимпиадах (при наличии)\n\nВступительные экзамены проводятся по следующим предметам:\n• Казахский или русский язык (язык обучения)\n• Математика\n• История Казахстана\n• Профильный предмет (зависит от специальности)',
            'content_kz': '"Болашақ" университетіне түсу үшін келесі құжаттар қажет:\n\n• Орта білім туралы аттестат немесе орта арнайы білім туралы диплом\n• Жеке басын куәландыратын құжаттың көшірмесі\n• 086-У нысанындағы медициналық анықтама\n• 3x4 өлшемінде 6 фотосурет\n• Олимпиадаларға қатысу туралы құжаттар (болған жағдайда)\n\nКіру емтихандары келесі пәндер бойынша өткізіледі:\n• Қазақ немесе орыс тілі (оқыту тілі)\n• Математика\n• Қазақстан тарихы\n• Бейінді пән (мамандыққа байланысты)',
            'content_en': 'To enter Bolashak University, the following documents are required:\n\n• Certificate of secondary education or diploma of secondary special education\n• Copy of identity document\n• Medical certificate form 086-U\n• 6 photos 3x4\n• Documents on participation in olympiads (if available)\n\nEntrance exams are conducted in the following subjects:\n• Kazakh or Russian language (language of instruction)\n• Mathematics\n• History of Kazakhstan\n• Profile subject (depends on specialty)',
            'keywords': 'поступление, документы, экзамены, требования, аттестат',
            'category': 'Поступление',
            'tags': 'документы,экзамены,требования',
            'priority': 1,
            'is_featured': True
        },
        {
            'agent_type': 'ai_abitur',
            'title': 'Сроки подачи документов',
            'content_ru': 'Приём документов на обучение осуществляется:\n\n**Основной период:**\n• 15 июня - 25 июля - подача документов\n• 26-31 июля - проведение вступительных экзаменов\n• 1-10 августа - зачисление\n\n**Дополнительный период:**\n• 15-25 августа - подача документов на свободные места\n• 26-28 августа - вступительные экзамены\n• 29-31 августа - зачисление\n\nДокументы подаются в приёмную комиссию с 9:00 до 18:00, обеденный перерыв с 13:00 до 14:00.',
            'content_kz': 'Оқуға құжаттар қабылдау мына мерзімдерде жүзеге асырылады:\n\n**Негізгі кезең:**\n• 15 маусым - 25 шілде - құжаттар беру\n• 26-31 шілде - кіру емтихандарын өткізу\n• 1-10 тамыз - қабылдау\n\n**Қосымша кезең:**\n• 15-25 тамыз - бос орындарға құжаттар беру\n• 26-28 тамыз - кіру емтихандары\n• 29-31 тамыз - қабылдау\n\nҚұжаттар қабылдау комиссиясына 9:00-дан 18:00-ге дейін беріледі, түскі үзіліс 13:00-14:00.',
            'content_en': 'Document submission for education is carried out:\n\n**Main period:**\n• June 15 - July 25 - document submission\n• July 26-31 - entrance exams\n• August 1-10 - enrollment\n\n**Additional period:**\n• August 15-25 - document submission for available places\n• August 26-28 - entrance exams\n• August 29-31 - enrollment\n\nDocuments are submitted to the admissions committee from 9:00 to 18:00, lunch break from 13:00 to 14:00.',
            'keywords': 'сроки, подача, документы, даты, приём',
            'category': 'Поступление',
            'tags': 'сроки,даты,документы',
            'priority': 2,
            'is_featured': True
        },
        
        # KadrAI Agent Knowledge
        {
            'agent_type': 'kadrai',
            'title': 'Процедура оформления отпуска',
            'content_ru': 'Для оформления отпуска сотруднику необходимо:\n\n**Основной отпуск:**\n• Подать заявление за 2 недели до планируемой даты\n• Согласовать с непосредственным руководителем\n• Получить подпись в отделе кадров\n\n**Учебный отпуск:**\n• Предоставить справку-вызов из учебного заведения\n• Подать заявление с приложением документов\n• Согласование с руководством\n\n**Отпуск без сохранения зарплаты:**\n• Указать причину в заявлении\n• Получить согласие руководителя\n• Максимальный срок - 1 год за весь период работы',
            'content_kz': 'Қызметкердің демалысын ресімдеу үшін қажет:\n\n**Негізгі демалыс:**\n• Жоспарланған күнге дейін 2 апта бұрын өтініш беру\n• Тікелей басшымен келісу\n• Кадр бөлімінен қол қойдыру\n\n**Оқу демалысы:**\n• Оқу орнынан шақыру-анықтама беру\n• Құжаттар қоса өтініш беру\n• Басшылықпен келісу\n\n**Жалақысыз демалыс:**\n• Өтінішке себебін көрсету\n• Басшының келісімін алу\n• Ең көп мерзімі - барлық жұмыс кезеңінде 1 жыл',
            'content_en': 'To process vacation, an employee needs to:\n\n**Main vacation:**\n• Submit application 2 weeks before planned date\n• Coordinate with direct supervisor\n• Get signature from HR department\n\n**Study leave:**\n• Provide reference-summons from educational institution\n• Submit application with attached documents\n• Coordination with management\n\n**Unpaid leave:**\n• Indicate reason in application\n• Get supervisor\'s consent\n• Maximum term - 1 year for entire work period',
            'keywords': 'отпуск, заявление, кадры, процедура',
            'category': 'Кадровые процедуры',
            'tags': 'отпуск,кадры,процедуры',
            'priority': 1,
            'is_featured': True
        },
        
        # UniNav Agent Knowledge  
        {
            'agent_type': 'uninav',
            'title': 'Учебное расписание и навигация',
            'content_ru': 'Для получения информации о расписании занятий:\n\n**Онлайн-расписание:**\n• Доступно на сайте университета в разделе "Расписание"\n• Обновляется еженедельно\n• Можно фильтровать по группам и преподавателям\n\n**Мобильное приложение:**\n• Скачайте приложение "Болашак Студент"\n• Персональное расписание по номеру группы\n• Уведомления об изменениях\n\n**Информационные стенды:**\n• На каждом этаже учебных корпусов\n• Обновляются каждый понедельник\n• Содержат актуальные изменения',
            'content_kz': 'Сабақ кестесі туралы ақпарат алу үшін:\n\n**Онлайн-кесте:**\n• Университет сайтында "Кесте" бөлімінде қолжетімді\n• Апта сайын жаңартылады\n• Топтар мен оқытушылар бойынша сүзуге болады\n\n**Мобильді қосымша:**\n• "Болашақ Студент" қосымшасын жүктеп алыңыз\n• Топ нөмірі бойынша жеке кесте\n• Өзгерістер туралы хабарландырулар\n\n**Ақпараттық стендтер:**\n• Оқу корпустарының әр қабатында\n• Әр дүйсенбі сайын жаңартылады\n• Өзекті өзгерістерді қамтиды',
            'content_en': 'To get information about class schedule:\n\n**Online schedule:**\n• Available on university website in "Schedule" section\n• Updated weekly\n• Can be filtered by groups and teachers\n\n**Mobile application:**\n• Download "Bolashak Student" app\n• Personal schedule by group number\n• Change notifications\n\n**Information stands:**\n• On each floor of academic buildings\n• Updated every Monday\n• Contain current changes',
            'keywords': 'расписание, занятия, учёба, навигация',
            'category': 'Учебный процесс',
            'tags': 'расписание,учёба,навигация',
            'priority': 1,
            'is_featured': True
        },
        
        # CareerNavigator Agent Knowledge
        {
            'agent_type': 'career_navigator',
            'title': 'Поиск работы и стажировок',
            'content_ru': 'Центр карьеры университета "Болашак" предлагает:\n\n**Поиск вакансий:**\n• База данных партнёрских компаний\n• Еженедельные ярмарки вакансий\n• Персональные консультации по трудоустройству\n\n**Помощь с резюме:**\n• Бесплатные мастер-классы по составлению резюме\n• Индивидуальные консультации\n• Шаблоны и примеры успешных резюме\n\n**Стажировки:**\n• Программы стажировок в ведущих компаниях\n• Летние стажировки для студентов 3-4 курсов\n• Возможность трудоустройства после стажировки\n\n**Контакты:**\n• Кабинет 205, учебный корпус №1\n• Телефон: +7 (7242) 123-460\n• Email: career@bolashak.kz',
            'content_kz': '"Болашақ" университетінің мансап орталығы ұсынады:\n\n**Жұмыс іздеу:**\n• Серіктес компаниялардың дерекқоры\n• Апта сайынғы жұмыс орындарының жәрмеңкелері\n• Жұмысқа орналасу бойынша жеке кеңестер\n\n**Резюмемен көмек:**\n• Резюме құру бойынша тегін шеберлік сыныптары\n• Жеке кеңестер\n• Сәтті резюмелердің үлгілері мен мысалдары\n\n**Тәжірибе орындары:**\n• Жетекші компанияларда тәжірибе бағдарламалары\n• 3-4 курс студенттеріне жазғы тәжірибе\n• Тәжірибеден кейін жұмысқа орналасу мүмкіндігі\n\n**Байланыстар:**\n• 205 кабинет, №1 оқу корпусы\n• Телефон: +7 (7242) 123-460\n• Email: career@bolashak.kz',
            'content_en': 'Bolashak University Career Center offers:\n\n**Job search:**\n• Partner companies database\n• Weekly job fairs\n• Personal employment consultations\n\n**Resume help:**\n• Free resume writing workshops\n• Individual consultations\n• Templates and examples of successful resumes\n\n**Internships:**\n• Internship programs in leading companies\n• Summer internships for 3rd-4th year students\n• Employment opportunities after internship\n\n**Contacts:**\n• Room 205, academic building №1\n• Phone: +7 (7242) 123-460\n• Email: career@bolashak.kz',
            'keywords': 'работа, карьера, резюме, стажировка, вакансии',
            'category': 'Карьера',
            'tags': 'работа,карьера,резюме',
            'priority': 1,
            'is_featured': True
        },
        
        # UniRoom Agent Knowledge
        {
            'agent_type': 'uniroom',
            'title': 'Общежитие университета',
            'content_ru': 'Университет "Болашак" предоставляет студентам современное общежитие:\n\n**Условия проживания:**\n• 2-3 местные комнаты\n• Общие кухни на каждом этаже\n• Wi-Fi интернет\n• Прачечная и гладильная комнаты\n• Охрана 24/7\n\n**Стоимость:**\n• 15 000 тенге в месяц\n• Коммунальные услуги включены\n\n**Правила заселения:**\n• Приоритет для иногородних студентов\n• Подача заявления до 1 августа\n• Необходимы: справка о доходах семьи, медицинская справка\n\n**Контакты администрации:**\n• Комендант: +7 (7242) 123-459\n• Адрес: ул. Студенческая, 15, г. Кызылорда',
            'content_kz': '"Болашақ" университеті студенттерге заманауи жатақхана ұсынады:\n\n**Тұру жағдайлары:**\n• 2-3 орындық бөлмелер\n• Әр қабатта ортақ ас үйлер\n• Wi-Fi интернет\n• Кір жуу және үтіктеу бөлмелері\n• 24/7 күзет\n\n**Құны:**\n• Айына 15 000 теңге\n• Коммуналдық қызметтер кіреді\n\n**Орналасу ережелері:**\n• Басқа қалалардан келген студенттерге басымдық\n• 1 тамызға дейін өтініш беру\n• Қажет: отбасы табысы туралы анықтама, медициналық анықтама\n\n**Әкімшілік байланыстары:**\n• Комендант: +7 (7242) 123-459\n• Мекенжайы: Студенттік к-сі, 15, Қызылорда қ.',
            'content_en': 'Bolashak University provides students with modern dormitory:\n\n**Living conditions:**\n• 2-3 bed rooms\n• Common kitchens on each floor\n• Wi-Fi internet\n• Laundry and ironing rooms\n• 24/7 security\n\n**Cost:**\n• 15,000 tenge per month\n• Utilities included\n\n**Settlement rules:**\n• Priority for non-local students\n• Application submission until August 1\n• Required: family income certificate, medical certificate\n\n**Administration contacts:**\n• Commandant: +7 (7242) 123-459\n• Address: Studentskaya str., 15, Kyzylorda',
            'keywords': 'общежитие, проживание, стоимость, условия',
            'category': 'Проживание',
            'tags': 'общежитие,проживание,жилье',
            'priority': 1,
            'is_featured': True
        }
    ]
    
    for knowledge in knowledge_data:
        existing_knowledge = AgentKnowledgeBase.query.filter_by(
            agent_type=knowledge['agent_type'], 
            title=knowledge['title']
        ).first()
        
        if not existing_knowledge:
            kb_entry = AgentKnowledgeBase(
                created_by=admin_user.id,
                **knowledge
            )
            db.session.add(kb_entry)
            logger.info(f"Создана запись базы знаний: {knowledge['title']} для {knowledge['agent_type']}")
        else:
            logger.info(f"Запись базы знаний уже существует: {knowledge['title']}")
    
    db.session.commit()
    logger.info("Инициализация базы знаний завершена")

def main():
    """Главная функция инициализации"""
    with create_app().app_context():
        logger.info("Начинаем инициализацию данных агентов...")
        
        try:
            init_agent_types()
            init_knowledge_base()
            
            logger.info("Инициализация данных агентов завершена успешно!")
            
        except Exception as e:
            logger.error(f"Ошибка при инициализации данных: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    main()