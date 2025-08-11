import logging
from models import KnowledgeBase
from sqlalchemy import or_
from typing import List

logger = logging.getLogger(__name__)

def get_relevant_context(user_message: str, language: str = "ru", limit: int = 3) -> str:
    """Get relevant context from knowledge base based on user message"""
    try:
        # Search knowledge base for relevant content
        kb_context = get_knowledge_base_context(user_message, language, limit)
        
        return "\n\n".join(kb_context) if kb_context else ""
        
    except Exception as e:
        logger.error(f"Error getting relevant context: {str(e)}")
        return ""

def get_knowledge_base_context(user_message: str, language: str = "ru", limit: int = 3) -> List[str]:
    """Get relevant context from knowledge base"""
    try:
        user_message_lower = user_message.lower()
        keywords = [word for word in user_message_lower.split() if len(word) > 2]
        
        if not keywords:
            return []
        
        # Search knowledge base for relevant chunks
        search_conditions = []
        for keyword in keywords[:3]:  # Limit to first 3 keywords
            search_conditions.append(KnowledgeBase.content_chunk.ilike(f'%{keyword}%'))
        
        relevant_entries = KnowledgeBase.query.filter(
            KnowledgeBase.is_active == True,
            or_(*search_conditions)
        ).limit(limit).all()
        
        context_parts = []
        for entry in relevant_entries:
            source_label = "Документ" if entry.source_type == 'document' else "Веб-сайт"
            context_parts.append(f"{source_label} - {entry.content_chunk}")
        
        return context_parts
        
    except Exception as e:
        logger.error(f"Error getting knowledge base context: {str(e)}")
        return []

def format_response_time(seconds: float) -> str:
    """Format response time for display"""
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    else:
        return f"{seconds:.2f}s"

def validate_language(language: str) -> str:
    """Validate and return supported language code"""
    return language if language in ['ru', 'kz'] else 'ru'
