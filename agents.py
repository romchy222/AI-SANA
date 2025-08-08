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
            # Get agent-specific system prompt
            system_prompt = self.get_system_prompt(language)
            
            # Get agent-specific context from knowledge base
            context = self.get_agent_context(message, language)
            
            # Use agent-specific system prompt for this message
            response = self.mistral.get_response_with_system_prompt(
                message, context, language, system_prompt
            )
            return {
                'response': response,
                'confidence': self.can_handle(message, language),
                'agent_type': self.agent_type,
                'agent_name': self.name,
                'context_used': bool(context)
            }
        except Exception as e:
            logger.error(f"Error in {self.name} agent: {str(e)}")
            return {
                'response': f"Извините, возникла ошибка при обработке запроса по теме '{self.description}'.",
                'confidence': 0.1,
                'agent_type': self.agent_type,
                'agent_name': self.name,
                'context_used': False
            }
    
    def get_agent_context(self, message: str, language: str = "ru") -> str:
        """Get agent-specific context from knowledge base"""
        try:
            from models import AgentKnowledgeBase
            from app import db
            
            # Search for relevant knowledge entries for this agent
            knowledge_entries = AgentKnowledgeBase.query.filter_by(
                agent_type=self.agent_type,
                is_active=True
            ).order_by(AgentKnowledgeBase.priority.asc()).all()
            
            if not knowledge_entries:
                return ""
            
            # Build context from relevant entries
            context_parts = []
            message_lower = message.lower()
            
            for entry in knowledge_entries:
                # Check if keywords match the message
                if entry.keywords:
                    keywords = [k.strip().lower() for k in entry.keywords.split(',')]
                    if any(keyword in message_lower for keyword in keywords):
                        content = entry.content_ru if language == 'ru' else entry.content_kz
                        context_parts.append(f"**{entry.title}**\n{content}")
                        
                        # Limit context to prevent too long prompts
                        if len(context_parts) >= 3:
                            break
            
            # If no keyword matches, include high-priority general entries
            if not context_parts:
                for entry in knowledge_entries[:2]:  # Top 2 priority entries
                    content = entry.content_ru if language == 'ru' else entry.content_kz
                    context_parts.append(f"**{entry.title}**\n{content}")
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error getting agent context: {str(e)}")
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