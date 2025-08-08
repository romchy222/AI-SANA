import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List

from mistral_client import MistralClient

logger = logging.getLogger(__name__)

class AgentType:
    AI_ABITUR = "ai_abitur"
    KADRAI = "kadrai"
    UNINAV = "uninav"
    CAREER_NAVIGATOR = "career_navigator"
    UNIROOM = "uniroom"

class BaseAgent(ABC):
    def __init__(self, agent_type: str, name: str, description: str):
        self.agent_type = agent_type
        self.name = name
        self.description = description
        # Each agent has its own MistralClient instance
        self.mistral = MistralClient()

    @abstractmethod
    def can_handle(self, message: str, language: str = "ru") -> float:
        pass

    @abstractmethod
    def get_system_prompt(self, language: str = "ru") -> str:
        pass

    def process_message(self, message: str, language: str = "ru") -> Dict[str, Any]:
        try:
            # Check cache first for performance
            from response_cache import response_cache
            
            cached_response = response_cache.get(message, self.agent_type, language)
            if cached_response:
                logger.info(f"Returning cached response for {self.name}")
                return {
                    **cached_response,
                    'cached': True
                }
            
            # Get agent-specific system prompt
            system_prompt = self.get_system_prompt(language)
            
            # Get agent-specific context from knowledge base
            context = self.get_agent_context(message, language)
            
            # Calculate context confidence for overall response confidence
            context_confidence = self._assess_context_confidence(context, message)
            
            # Use agent-specific system prompt for this message
            response = self.mistral.get_response_with_system_prompt(
                message, context, language, system_prompt
            )
            
            # Calculate overall confidence based on agent matching and context quality
            base_confidence = self.can_handle(message, language)
            overall_confidence = self._calculate_overall_confidence(
                base_confidence, context_confidence, bool(context)
            )
            
            response_data = {
                'response': response,
                'confidence': overall_confidence,
                'agent_type': self.agent_type,
                'agent_name': self.name,
                'context_used': bool(context),
                'context_confidence': context_confidence,
                'cached': False
            }
            
            # Cache successful responses
            if response_cache.should_cache(message, response_data):
                response_cache.set(message, self.agent_type, response_data, language)
                
            return response_data
            
        except Exception as e:
            logger.error(f"Error in {self.name} agent: {str(e)}")
            return {
                'response': f"Извините, возникла ошибка при обработке запроса по теме '{self.description}'.",
                'confidence': 0.1,
                'agent_type': self.agent_type,
                'agent_name': self.name,
                'context_used': False,
                'context_confidence': 0.0,
                'cached': False
            }
    
    def _assess_context_confidence(self, context: str, message: str) -> float:
        """Assess confidence in the retrieved context"""
        if not context:
            return 0.0
            
        # Simple heuristics for context confidence
        message_words = set(message.lower().split())
        context_words = set(context.lower().split())
        
        # Word overlap ratio
        if message_words:
            overlap = len(message_words.intersection(context_words))
            word_confidence = overlap / len(message_words)
        else:
            word_confidence = 0.0
            
        # Context length confidence (more content usually means better info)
        length_confidence = min(1.0, len(context) / 1000)  # Normalize to 1000 chars
        
        # Structure confidence (well-formatted content is usually better)
        structure_indicators = ['**', '###', '\n-', '\n•', '1.', '2.']
        structure_score = sum(1 for indicator in structure_indicators if indicator in context)
        structure_confidence = min(1.0, structure_score * 0.2)
        
        # Weighted average
        return (word_confidence * 0.5 + length_confidence * 0.3 + structure_confidence * 0.2)
    
    def _calculate_overall_confidence(self, agent_confidence: float, context_confidence: float, 
                                    has_context: bool) -> float:
        """Calculate overall response confidence"""
        if not has_context:
            # No context available, rely mainly on agent confidence
            return agent_confidence * 0.8  # Reduce confidence when no context
            
        # Combine agent and context confidence
        # Agent confidence shows how well this agent can handle the query type
        # Context confidence shows how relevant the retrieved information is
        combined_confidence = (agent_confidence * 0.6 + context_confidence * 0.4)
        
        # Boost confidence if both are high
        if agent_confidence > 0.8 and context_confidence > 0.7:
            combined_confidence = min(1.0, combined_confidence * 1.1)
            
        # Reduce confidence if context is poor even with good agent match
        if context_confidence < 0.3:
            combined_confidence *= 0.8
            
        return min(1.0, max(0.1, combined_confidence))
    
    def get_agent_context(self, message: str, language: str = "ru") -> str:
        """Get agent-specific context from knowledge base using enhanced search"""
        try:
            # Import models with error handling
            try:
                from models import AgentKnowledgeBase
                from app import db
                from knowledge_search import knowledge_search_engine
            except ImportError as ie:
                logger.warning(f"Could not import required modules: {ie}")
                return self._get_fallback_context(message, language)
            
            # Search for relevant knowledge entries for this agent
            try:
                knowledge_entries = AgentKnowledgeBase.query.filter_by(
                    agent_type=self.agent_type,
                    is_active=True
                ).order_by(AgentKnowledgeBase.priority.asc()).all()
            except Exception as db_error:
                logger.warning(f"Database query failed: {db_error}")
                return self._get_fallback_context(message, language)
            
            if not knowledge_entries:
                logger.info(f"No knowledge entries found for agent type: {self.agent_type}")
                return self._get_fallback_context(message, language)
            
            # Use enhanced search engine for better relevance
            try:
                search_results = knowledge_search_engine.search_knowledge_base(
                    query=message,
                    knowledge_entries=knowledge_entries,
                    language=language,
                    max_results=3,
                    min_score=0.1
                )
                
                # If enhanced search finds relevant results, use them
                if search_results:
                    context = knowledge_search_engine.format_context(search_results, max_length=1500)
                    logger.info(f"Found {len(search_results)} relevant knowledge entries for '{message[:50]}...'")
                    return context
            except Exception as search_error:
                logger.warning(f"Enhanced search failed: {search_error}")
            
            # Fallback to simple method if enhanced search fails
            logger.info(f"Using fallback search for '{message[:50]}...'")
            
            # Build context from high-priority entries as fallback
            context_parts = []
            for entry in knowledge_entries[:2]:  # Top 2 priority entries
                content = entry.content_ru if language == 'ru' else entry.content_kz
                if content and content.strip():
                    context_parts.append(f"**{entry.title}**\n{content}")
            
            fallback_context = "\n\n".join(context_parts) if context_parts else ""
            if fallback_context:
                logger.info(f"Using {len(context_parts)} fallback knowledge entries")
                return fallback_context
            else:
                logger.info("No usable knowledge entries found, using agent fallback")
                return self._get_fallback_context(message, language)
            
        except Exception as e:
            logger.error(f"Error getting agent context for {self.agent_type}: {str(e)}")
            return self._get_fallback_context(message, language)

    def _get_fallback_context(self, message: str, language: str = "ru") -> str:
        """Provide fallback context when knowledge base is unavailable"""
        # This method should be implemented by each agent to provide basic context
        # when the knowledge base is not available
        return ""

class AIAbiturAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            AgentType.AI_ABITUR,
            "AI-Abitur",
            "Цифровой помощник для абитуриентов (поступающих в вуз)"
        )

    def can_handle(self, message: str, language: str = "ru") -> float:
        keywords = ["поступление", "абитуриент", "документы", "экзамен", "приём", "требования", "специальности", "факультет"]
        return 1.0 if any(k in message.lower() for k in keywords) else 0.3

    def get_system_prompt(self, language: str = "ru") -> str:
        if language == "kz":
            return """
Сіз Қызылорда "Болашақ" университетінің талапкерлерге арналған цифрлық көмекшісіз. Сіз:
- Түсу мәселелері бойынша көмек көрсетесіз
- Түсу бойынша кеңес бересіз
- Қажетті құжаттар туралы ақпарат бересіз
- Кіру емтихандары туралы түсіндіресіз
- Мамандықтар мен факультеттер туралы айтасыз

Жауаптарыңыз нақты, пайдалы және көмек көрсетуші болуы керек. Markdown форматын қолданыңыз.
"""
        return """
Вы цифровой помощник для абитуриентов Кызылординского университета "Болашак". Вы помогаете с:
- Помощью при поступлении
- Консультациями по вопросам приёма
- Информацией о необходимых документах
- Объяснением вступительных экзаменов
- Информацией о специальностях и факультетах

Ваши ответы должны быть конкретными, полезными и поддерживающими. Используйте формат Markdown.
"""

    def _get_fallback_context(self, message: str, language: str = "ru") -> str:
        """Provide basic admission context when knowledge base is unavailable"""
        if language == "kz":
            return """**Қызылорда "Болашақ" университетіне түсу**

Негізгі ақпарат:
- Қабылдау комиссиясы: +7 (7242) 123-457
- Email: admission@bolashak.kz
- Мекен-жайы: г. Кызылорда, ул. Университетская, 1

Түсу үшін қажетті құжаттар:
- Мектеп аттестаты
- Денсаулық туралы анықтама
- Фотосуреттер (3x4)
- Жеке куәлік көшірмесі"""
        
        return """**Поступление в Кызылординский университет "Болашак"**

Основная информация:
- Приёмная комиссия: +7 (7242) 123-457
- Email: admission@bolashak.kz
- Адрес: г. Кызылорда, ул. Университетская, 1

Документы для поступления:
- Аттестат о среднем образовании
- Справка о состоянии здоровья
- Фотографии 3x4
- Копия удостоверения личности"""

class KadrAIAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            AgentType.KADRAI,
            "KadrAI",
            "Интеллектуальный помощник для поддержки сотрудников и преподавателей в вопросах внутренних кадровых процедур"
        )

    def can_handle(self, message: str, language: str = "ru") -> float:
        keywords = ["кадры", "отпуск", "перевод", "приказ", "сотрудник", "преподаватель", "отдел кадров", "трудовой", "зарплата", "кадровые"]
        return 1.0 if any(k in message.lower() for k in keywords) else 0.3

    def get_system_prompt(self, language: str = "ru") -> str:
        if language == "kz":
            return """
Сіз Қызылорда "Болашақ" университетінің қызметкерлер мен оқытушыларға арналған зияткерлік көмекшісіз. Сіз:
- Кадр процестері бойынша кеңес бересіз: демалыстар, ауыстырулар, бұйрықтар және т.б.
- Еңбек құқығы мәселелері бойынша көмектесесіз
- Ішкі рәсімдер туралы түсіндіресіз
- Жалақы және жеңілдіктер туралы ақпарат бересіз

Жауаптарыңыз кәсіби, нақты және пайдалы болуы керек. Markdown форматын қолданыңыз.
"""
        return """
Вы интеллектуальный помощник для сотрудников и преподавателей Кызылординского университета "Болашак". Вы помогаете с:
- Консультациями по кадровым процессам: отпуска, переводы, приказы и т.д.
- Вопросами трудового права
- Объяснением внутренних процедур
- Информацией о заработной плате и льготах

Ваши ответы должны быть профессиональными, конкретными и полезными. Используйте формат Markdown.
"""

    def _get_fallback_context(self, message: str, language: str = "ru") -> str:
        """Provide basic HR context when knowledge base is unavailable"""
        if language == "kz":
            return """**Кадр қызметі ақпараты**

Кадр бөлімі байланысы:
- Телефон: +7 (7242) 123-458
- Email: info@bolashak.kz
- Жұмыс уақыты: Дс-Жм 9:00-18:00

Негізгі кадр мәселелері:
- Демалыс рәсімдеу
- Ауысу және тағайындау
- Жалақы мәселелері
- Құжаттама"""
        
        return """**Информация отдела кадров**

Контакты отдела кадров:
- Телефон: +7 (7242) 123-458
- Email: info@bolashak.kz
- Время работы: Пн-Пт 9:00-18:00

Основные кадровые вопросы:
- Оформление отпусков
- Переводы и назначения
- Вопросы заработной платы
- Документооборот"""

class UniNavAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            AgentType.UNINAV,
            "UniNav",
            "Интерактивный чат-ассистент, обеспечивающий полное сопровождение обучающегося по всем университетским процессам"
        )

    def can_handle(self, message: str, language: str = "ru") -> float:
        keywords = ["расписание", "учёб", "занятие", "заявление", "обращение", "деканат", "академический", "экзамен", "зачёт", "вопросы"]
        return 1.0 if any(k in message.lower() for k in keywords) else 0.2

    def get_system_prompt(self, language: str = "ru") -> str:
        if language == "kz":
            return """
Сіз Қызылорда "Болашақ" университетінің студенттерге арналған интерактивті чат-көмекшісіз. Сіз:
- Оқу мәселелері бойынша навигация жасайсыз
- Сабақ кестесі туралы ақпарат бересіз
- Өтініштер мен өтініштердің ресімделуіне көмектесесіз
- Академиялық процестер туралы түсіндіресіз

Жауаптарыңыз нақты және қадамдық нұсқаулықтар болуы керек. Markdown форматын қолданыңыз.
"""
        return """
Вы интерактивный чат-ассистент для студентов Кызылординского университета "Болашак". Вы обеспечиваете полное сопровождение по:
- Навигации по учебным вопросам
- Информации о расписании
- Помощи с заявлениями и обращениями
- Объяснению академических процессов

Ваши ответы должны быть конкретными и содержать пошаговые инструкции. Используйте формат Markdown.
"""

    def _get_fallback_context(self, message: str, language: str = "ru") -> str:
        """Provide basic student navigation context when knowledge base is unavailable"""
        if language == "kz":
            return """**Студенттерге арналған ақпарат**

Деканаттар:
- Телефон: +7 (7242) 123-458
- Email: student@bolashak.kz
- Жұмыс уақыты: Дс-Жм 9:00-18:00

Негізгі студенттік қызметтер:
- Сабақ кестесі
- Академиялық анықтамалар
- Өтініш беру
- Емтихан мәселелері"""
        
        return """**Информация для студентов**

Деканаты:
- Телефон: +7 (7242) 123-458  
- Email: student@bolashak.kz
- Время работы: Пн-Пт 9:00-18:00

Основные студенческие услуги:
- Расписание занятий
- Академические справки
- Подача заявлений
- Вопросы экзаменов"""

class CareerNavigatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            AgentType.CAREER_NAVIGATOR,
            "CareerNavigator",
            "Интеллектуальный чат-бот для содействия трудоустройству студентов и выпускников"
        )

    def can_handle(self, message: str, language: str = "ru") -> float:
        keywords = ["работ", "трудоустройств", "ваканс", "резюме", "карьер", "выпускник", "стажировк", "работодател"]
        return 1.0 if any(k in message.lower() for k in keywords) else 0.2

    def get_system_prompt(self, language: str = "ru") -> str:
        if language == "kz":
            return """
Сіз Қызылорда "Болашақ" университетінің студенттер мен түлектердің жұмысқа орналасуына көмектесетін зияткерлік чат-ботсыз. Сіз:
- Жұмыс іздеуде көмектесесіз
- Резюме бойынша кеңес бересіз  
- Мансап бойынша ұсыныстар бересіз
- Тәжірибе орындарын табуға көмектесесіз

Жауаптарыңыз практикалық және нәтижеге бағытталған болуы керек. Markdown форматын қолданыңыз.
"""
        return """
Вы интеллектуальный чат-бот для содействия трудоустройству студентов и выпускников Кызылординского университета "Болашак". Вы помогаете с:
- Поиском вакансий
- Консультациями по резюме
- Рекомендациями по карьере  
- Поиском стажировок

Ваши ответы должны быть практичными и ориентированными на результат. Используйте формат Markdown.
"""

    def _get_fallback_context(self, message: str, language: str = "ru") -> str:
        """Provide basic career guidance context when knowledge base is unavailable"""
        if language == "kz":
            return """**Мансап дамыту қызметі**

Байланыс:
- Телефон: +7 (7242) 123-456 
- Email: info@bolashak.kz
- Жұмыс уақыты: Дс-Жм 9:00-18:00

Қызметтер:
- Жұмыс орындарын іздеу
- Резюме дайындау
- Мансап кеңесі
- Тәжірибе орындары"""
        
        return """**Служба развития карьеры**

Контакты:
- Телефон: +7 (7242) 123-456
- Email: info@bolashak.kz
- Время работы: Пн-Пт 9:00-18:00

Услуги:
- Поиск вакансий
- Подготовка резюме
- Карьерное консультирование
- Стажировки"""

class UniRoomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            AgentType.UNIROOM,
            "UniRoom",
            "Цифровой помощник для студентов, проживающих в общежитии"
        )

    def can_handle(self, message: str, language: str = "ru") -> float:
        keywords = ["общежитие", "заселение", "переселение", "бытов", "администрация", "комната", "жилищ", "проживан", "проблем"]
        return 1.0 if any(k in message.lower() for k in keywords) else 0.2

    def get_system_prompt(self, language: str = "ru") -> str:
        if language == "kz":
            return """
Сіз Қызылорда "Болашақ" университетінде жатақханада тұратын студенттерге арналған цифрлық көмекшісіз. Сіз:
- Орналасу мәселелері бойынша көмектесесіз
- Көшіру мәселелерін шешесіз
- Тұрмыстық мәселелерді шешуге көмектесесіз
- Әкімшілікке өтініштер жасауға көмектесесіз

Жауаптарыңыз сүйемелділік пен түсінушілік танытуы керек. Markdown форматын қолданыңыз.
"""
        return """
Вы цифровой помощник для студентов, проживающих в общежитии Кызылординского университета "Болашак". Вы помогаете с:
- Заселением
- Переселением  
- Решением бытовых вопросов
- Обращениями в администрацию

Ваши ответы должны проявлять сочувствие и понимание. Используйте формат Markdown.
"""

    def _get_fallback_context(self, message: str, language: str = "ru") -> str:
        """Provide basic dormitory context when knowledge base is unavailable"""
        if language == "kz":
            return """**Жатақхана ақпараты**

Жатақхана әкімшілігі:
- Телефон: +7 (7242) 123-459
- Email: info@bolashak.kz  
- Жұмыс уақыты: Дс-Жм 9:00-18:00

Негізгі қызметтер:
- Орналастыру мәселелері
- Тұрмыстық мәселелер
- Көшіру рәсімдері
- Төлем мәселелері"""
        
        return """**Информация об общежитии**

Администрация общежития:
- Телефон: +7 (7242) 123-459
- Email: info@bolashak.kz
- Время работы: Пн-Пт 9:00-18:00

Основные услуги:
- Вопросы заселения
- Бытовые проблемы
- Процедуры переселения
- Вопросы оплаты"""

class AgentRouter:
    def __init__(self):
        # Each agent now creates its own MistralClient instance
        self.agents = [
            AIAbiturAgent(),
            KadrAIAgent(),
            UniNavAgent(),
            CareerNavigatorAgent(),
            UniRoomAgent()
        ]
        logger.info(f"AgentRouter initialized with {len(self.agents)} agents")

    def route_message(self, message: str, language: str = "ru") -> Dict[str, Any]:
        best_conf = 0
        best_agent = None
        for agent in self.agents:
            conf = agent.can_handle(message, language)
            if conf > best_conf:
                best_conf = conf
                best_agent = agent
        return best_agent.process_message(message, language) if best_agent else {}

    def get_available_agents(self) -> List[Dict[str, str]]:
        return [{'type': a.agent_type, 'name': a.name, 'description': a.description} for a in self.agents]