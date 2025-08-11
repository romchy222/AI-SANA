"""
Enhanced Prompt Engineering Module
Модуль улучшенной генерации промптов

This module provides intelligent prompt generation with context relevance,
dynamic templates, and token management.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PromptConfig:
    """Configuration for prompt generation"""
    max_tokens: int = 4000  # Maximum tokens for entire prompt
    context_weight: float = 0.6  # How much of token budget for context
    system_prompt_weight: float = 0.25  # How much for system prompt
    user_query_weight: float = 0.15  # How much for user query
    min_context_relevance: float = 0.2  # Minimum context relevance to include


class PromptEngineer:
    """Enhanced prompt engineering with dynamic templates and optimization"""
    
    def __init__(self, config: Optional[PromptConfig] = None):
        self.config = config or PromptConfig()
        
    def estimate_token_count(self, text: str) -> int:
        """Rough estimation of token count (1 token ≈ 4 characters for Russian)"""
        if not text:
            return 0
        return max(1, len(text) // 3)  # More conservative estimate for Russian
    
    def truncate_text_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to approximate token limit"""
        if not text:
            return text
            
        estimated_tokens = self.estimate_token_count(text)
        if estimated_tokens <= max_tokens:
            return text
            
        # Calculate approximate character limit
        char_limit = max_tokens * 3
        if len(text) <= char_limit:
            return text
            
        # Smart truncation - try to cut at sentence boundaries
        truncated = text[:char_limit]
        
        # Find last sentence ending
        sentence_endings = ['. ', '! ', '? ', '.\n', '!\n', '?\n']
        last_sentence_end = -1
        
        for ending in sentence_endings:
            pos = truncated.rfind(ending)
            if pos > last_sentence_end:
                last_sentence_end = pos
                
        if last_sentence_end > char_limit * 0.7:  # If we found a good cut point
            return truncated[:last_sentence_end + 1] + "\n\n[...]"
        else:
            return truncated + "..."
    
    def assess_context_quality(self, context: str, user_query: str) -> Dict[str, float]:
        """Assess the quality and relevance of context"""
        if not context or not user_query:
            return {'relevance': 0.0, 'completeness': 0.0, 'clarity': 1.0}
            
        query_words = set(user_query.lower().split())
        context_words = set(context.lower().split())
        
        # Relevance: how many query words appear in context
        if query_words:
            word_overlap = len(query_words.intersection(context_words))
            relevance = word_overlap / len(query_words)
        else:
            relevance = 0.0
            
        # Completeness: based on context length (longer = more complete info)
        context_length = len(context)
        if context_length > 1000:
            completeness = 1.0
        elif context_length > 500:
            completeness = 0.8
        elif context_length > 200:
            completeness = 0.6
        else:
            completeness = 0.4
            
        # Clarity: based on structure (presence of headers, bullet points)
        clarity_indicators = ['**', '*', '\n-', '\n•', '1.', '2.', '###']
        clarity_score = sum(1 for indicator in clarity_indicators if indicator in context)
        clarity = min(1.0, clarity_score * 0.2 + 0.4)  # Base clarity + structure bonus
        
        return {
            'relevance': relevance,
            'completeness': completeness,
            'clarity': clarity
        }
    
    def generate_dynamic_system_prompt(self, base_prompt: str, context_quality: Dict[str, float], 
                                     language: str = 'ru') -> str:
        """Generate dynamic system prompt based on context quality"""
        
        # Start with base prompt
        prompt_parts = [base_prompt.strip()]
        
        # Add context-specific instructions based on quality
        relevance = context_quality.get('relevance', 0.0)
        completeness = context_quality.get('completeness', 0.0)
        
        if language == 'ru':
            if relevance < 0.3:
                prompt_parts.append(
                    "ВАЖНО: Предоставленный контекст может быть не полностью релевантен запросу. "
                    "Используйте свои знания для дополнения ответа."
                )
            elif relevance > 0.7:
                prompt_parts.append(
                    "Контекст высоко релевантен запросу. Используйте его в качестве основы ответа."
                )
                
            if completeness < 0.5:
                prompt_parts.append(
                    "Контекст ограничен. При необходимости укажите, что требуется дополнительная информация."
                )
                
            # Always add formatting instructions
            prompt_parts.append(
                "Форматирование: Используйте Markdown для структурирования ответа. "
                "Выделяйте важные моменты и создавайте читаемую структуру."
            )
        else:  # Kazakh
            if relevance < 0.3:
                prompt_parts.append(
                    "МАҢЫЗДЫ: Берілген контекст сұрауға толық сәйкес келмеуі мүмкін. "
                    "Жауапты толықтыру үшін өз білімдеріңізді пайдаланыңыз."
                )
            elif relevance > 0.7:
                prompt_parts.append(
                    "Контекст сұрауға өте сәйкес келеді. Оны жауаптың негізі ретінде пайдаланыңыз."
                )
                
            if completeness < 0.5:
                prompt_parts.append(
                    "Контекст шектеулі. Қажет болса, қосымша ақпарат қажет екенін көрсетіңіз."
                )
                
            prompt_parts.append(
                "Форматтау: Жауапты құрылымдау үшін Markdown пайдаланыңыз. "
                "Маңызды тұстарды ерекшелеп, оқуға ыңғайлы құрылым жасаңыз."
            )
        
        return "\n\n".join(prompt_parts)
    
    def optimize_prompt_structure(self, system_prompt: str, context: str, user_query: str) -> str:
        """Optimize the overall prompt structure and length"""
        
        # Calculate current token usage
        system_tokens = self.estimate_token_count(system_prompt)
        context_tokens = self.estimate_token_count(context)
        query_tokens = self.estimate_token_count(user_query)
        total_tokens = system_tokens + context_tokens + query_tokens
        
        logger.debug(f"Token usage: system={system_tokens}, context={context_tokens}, "
                    f"query={query_tokens}, total={total_tokens}")
        
        # If within limits, return as-is
        if total_tokens <= self.config.max_tokens:
            return self._format_final_prompt(system_prompt, context, user_query)
        
        # Need to truncate - prioritize based on weights
        available_tokens = self.config.max_tokens
        
        # Reserve tokens for user query (highest priority)
        query_token_limit = int(available_tokens * self.config.user_query_weight)
        if query_tokens > query_token_limit:
            user_query = self.truncate_text_to_tokens(user_query, query_token_limit)
            query_tokens = self.estimate_token_count(user_query)
        
        # Reserve tokens for system prompt
        remaining_tokens = available_tokens - query_tokens
        system_token_limit = int(remaining_tokens * (self.config.system_prompt_weight / 
                                                     (self.config.system_prompt_weight + self.config.context_weight)))
        
        if system_tokens > system_token_limit:
            system_prompt = self.truncate_text_to_tokens(system_prompt, system_token_limit)
            system_tokens = self.estimate_token_count(system_prompt)
        
        # Use remaining tokens for context
        context_token_limit = available_tokens - query_tokens - system_tokens
        if context_tokens > context_token_limit:
            context = self.truncate_text_to_tokens(context, context_token_limit)
        
        logger.info(f"Prompt optimized: {total_tokens} -> {self.estimate_token_count(system_prompt + context + user_query)} tokens")
        
        return self._format_final_prompt(system_prompt, context, user_query)
    
    def _format_final_prompt(self, system_prompt: str, context: str, user_query: str) -> str:
        """Format the final prompt with clear sections"""
        
        sections = []
        
        # System prompt section
        if system_prompt:
            sections.append(f"=== СИСТЕМА ===\n{system_prompt}")
        
        # Context section (if available)
        if context and context.strip():
            sections.append(f"=== КОНТЕКСТ ИЗ БАЗЫ ЗНАНИЙ ===\n{context}")
        
        # User query section
        if user_query:
            sections.append(f"=== ВОПРОС ПОЛЬЗОВАТЕЛЯ ===\n{user_query}")
        
        return "\n\n".join(sections)
    
    def generate_enhanced_prompt(self, system_prompt: str, context: str, user_query: str,
                               language: str = 'ru') -> Tuple[str, Dict[str, float]]:
        """
        Generate enhanced prompt with quality assessment and optimization
        
        Returns:
            Tuple of (optimized_prompt, quality_metrics)
        """
        
        # Assess context quality
        context_quality = self.assess_context_quality(context, user_query)
        
        # Generate dynamic system prompt based on context quality
        enhanced_system_prompt = self.generate_dynamic_system_prompt(
            system_prompt, context_quality, language
        )
        
        # Optimize prompt structure and length
        optimized_prompt = self.optimize_prompt_structure(
            enhanced_system_prompt, context, user_query
        )
        
        # Calculate final metrics
        final_tokens = self.estimate_token_count(optimized_prompt)
        quality_metrics = {
            **context_quality,
            'token_efficiency': min(1.0, self.config.max_tokens / max(final_tokens, 1)),
            'final_tokens': final_tokens
        }
        
        logger.info(f"Enhanced prompt generated: {final_tokens} tokens, "
                   f"relevance={context_quality['relevance']:.2f}")
        
        return optimized_prompt, quality_metrics


# Global instance
prompt_engineer = PromptEngineer()