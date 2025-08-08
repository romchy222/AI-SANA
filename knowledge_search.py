"""
Enhanced Knowledge Base Search Module
Модуль улучшенного поиска по базе знаний

This module provides advanced search capabilities for the knowledge base
including TF-IDF similarity, fuzzy matching, and relevance scoring.
"""

import re
import logging
from typing import List, Dict, Tuple, Optional
from collections import Counter
from difflib import SequenceMatcher
import math

logger = logging.getLogger(__name__)


class KnowledgeSearchEngine:
    """Enhanced search engine for knowledge base with TF-IDF and fuzzy matching"""
    
    def __init__(self):
        self.stop_words = {
            'ru': {'и', 'в', 'на', 'с', 'по', 'для', 'как', 'что', 'где', 'когда', 'кто', 'как', 'это', 'то', 'да', 'нет', 'не', 'а', 'но', 'или', 'из', 'у', 'к', 'о', 'об', 'от', 'до', 'за', 'при', 'под', 'над', 'между', 'через', 'без', 'во', 'со', 'про'},
            'kz': {'және', 'пен', 'бен', 'мен', 'де', 'да', 'те', 'та', 'ке', 'қе', 'ға', 'на', 'нан', 'дан', 'тан', 'ден', 'тен', 'нен', 'мен', 'бен', 'пен', 'жоқ', 'бар', 'емес', 'болу', 'ол', 'бұл', 'сол'}
        }
        self.processed_knowledge = {}  # Cache for processed knowledge entries
        
    def preprocess_text(self, text: str, language: str = 'ru') -> List[str]:
        """Preprocess text for better search"""
        if not text:
            return []
            
        # Convert to lowercase and clean
        text = text.lower()
        
        # Remove special characters but keep letters and numbers
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Split into words
        words = text.split()
        
        # Remove stop words
        stop_words = self.stop_words.get(language, set())
        words = [word for word in words if word not in stop_words and len(word) > 2]
        
        return words
    
    def calculate_tf_idf(self, query_words: List[str], documents: List[Dict]) -> Dict[int, float]:
        """Calculate TF-IDF scores for documents"""
        if not query_words or not documents:
            return {}
            
        # Calculate document frequency for each term
        df = Counter()
        doc_words = {}
        
        for i, doc in enumerate(documents):
            # Combine title, content and keywords for search
            text = f"{doc.get('title', '')} {doc.get('content', '')} {doc.get('keywords', '')}"
            words = self.preprocess_text(text, doc.get('language', 'ru'))
            doc_words[i] = words
            
            # Count unique terms in document
            unique_words = set(words)
            for word in unique_words:
                df[word] += 1
        
        # Calculate TF-IDF scores
        scores = {}
        num_docs = len(documents)
        
        for i, doc in enumerate(documents):
            score = 0.0
            doc_word_list = doc_words.get(i, [])
            doc_word_count = Counter(doc_word_list)
            doc_length = len(doc_word_list)
            
            if doc_length == 0:
                scores[i] = 0.0
                continue
                
            for query_word in query_words:
                # Term frequency
                tf = doc_word_count.get(query_word, 0) / doc_length
                
                # Inverse document frequency
                if df[query_word] > 0:
                    idf = math.log(num_docs / df[query_word])
                else:
                    idf = 0
                    
                score += tf * idf
            
            scores[i] = score
            
        return scores
    
    def fuzzy_match_score(self, query: str, text: str) -> float:
        """Calculate fuzzy matching score for handling typos"""
        if not query or not text:
            return 0.0
            
        # Direct substring match gets highest score
        if query.lower() in text.lower():
            return 1.0
            
        # Calculate similarity ratio
        similarity = SequenceMatcher(None, query.lower(), text.lower()).ratio()
        
        # Boost score for partial word matches
        query_words = query.lower().split()
        text_words = text.lower().split()
        
        word_matches = 0
        for q_word in query_words:
            for t_word in text_words:
                if q_word in t_word or SequenceMatcher(None, q_word, t_word).ratio() > 0.8:
                    word_matches += 1
                    break
        
        word_match_ratio = word_matches / len(query_words) if query_words else 0
        
        # Combine similarity and word match scores
        return max(similarity, word_match_ratio * 0.8)
    
    def calculate_relevance_score(self, query: str, entry: Dict, language: str = 'ru') -> float:
        """Calculate overall relevance score combining multiple factors"""
        
        # Extract text fields
        title = entry.get('title', '')
        content = entry.get('content', '')
        keywords = entry.get('keywords', '')
        priority = entry.get('priority', 1)
        
        # Calculate different score components
        scores = {}
        
        # 1. Keyword exact match (highest weight)
        if keywords:
            keyword_list = [k.strip().lower() for k in keywords.split(',')]
            query_lower = query.lower()
            exact_keyword_matches = sum(1 for k in keyword_list if k in query_lower)
            scores['keyword_exact'] = exact_keyword_matches / len(keyword_list) if keyword_list else 0
        else:
            scores['keyword_exact'] = 0
            
        # 2. Fuzzy keyword match
        scores['keyword_fuzzy'] = self.fuzzy_match_score(query, keywords) if keywords else 0
        
        # 3. Title relevance
        scores['title'] = self.fuzzy_match_score(query, title)
        
        # 4. Content relevance  
        scores['content'] = self.fuzzy_match_score(query, content)
        
        # 5. TF-IDF score (requires document collection)
        query_words = self.preprocess_text(query, language)
        doc_text = f"{title} {content} {keywords}"
        doc_words = self.preprocess_text(doc_text, language)
        
        # Simple term frequency for single document
        if query_words and doc_words:
            word_count = Counter(doc_words)
            doc_length = len(doc_words)
            tf_score = sum(word_count.get(word, 0) for word in query_words) / doc_length
            scores['tf'] = tf_score
        else:
            scores['tf'] = 0
            
        # 6. Priority boost (higher priority = lower number = higher score)
        priority_score = 1.0 / max(priority, 1)  # Inverse priority
        scores['priority'] = min(priority_score, 1.0)
        
        # Weighted combination of scores
        weights = {
            'keyword_exact': 0.4,    # Highest weight for exact keyword matches
            'keyword_fuzzy': 0.2,    # Fuzzy keyword matching
            'title': 0.15,           # Title relevance
            'content': 0.1,          # Content relevance
            'tf': 0.1,               # Term frequency
            'priority': 0.05         # Priority boost
        }
        
        # Calculate weighted score
        final_score = sum(scores[key] * weights[key] for key in weights)
        
        # Log scoring details for debugging
        logger.debug(f"Relevance scoring for query '{query}': {scores} -> {final_score}")
        
        return final_score
    
    def search_knowledge_base(self, query: str, knowledge_entries: List, language: str = 'ru', 
                            max_results: int = 3, min_score: float = 0.1) -> List[Dict]:
        """
        Enhanced search through knowledge base entries
        
        Args:
            query: User query string
            knowledge_entries: List of knowledge base entries
            language: Language for processing
            max_results: Maximum number of results to return
            min_score: Minimum relevance score threshold
            
        Returns:
            List of relevant knowledge entries with scores
        """
        if not query or not knowledge_entries:
            return []
            
        # Convert knowledge entries to search format
        search_docs = []
        for entry in knowledge_entries:
            doc = {
                'id': entry.id,
                'title': entry.title,
                'content': entry.content_ru if language == 'ru' else entry.content_kz,
                'keywords': entry.keywords or '',
                'priority': entry.priority or 1,
                'entry': entry  # Keep reference to original entry
            }
            search_docs.append(doc)
        
        # Calculate relevance scores
        scored_results = []
        for doc in search_docs:
            score = self.calculate_relevance_score(query, doc, language)
            if score >= min_score:
                scored_results.append({
                    'entry': doc['entry'],
                    'score': score,
                    'content': doc['content'],
                    'title': doc['title']
                })
        
        # Sort by score (descending) and limit results
        scored_results.sort(key=lambda x: x['score'], reverse=True)
        
        # Log search results
        logger.info(f"Knowledge search for '{query}': {len(scored_results)} results "
                   f"(max_score: {scored_results[0]['score']:.3f})" if scored_results else "No results")
        
        return scored_results[:max_results]
    
    def format_context(self, search_results: List[Dict], max_length: int = 1500) -> str:
        """Format search results into context string with smart truncation"""
        if not search_results:
            return ""
            
        context_parts = []
        total_length = 0
        
        for result in search_results:
            title = result['title']
            content = result['content']
            score = result['score']
            
            # Format entry with score indication
            entry_text = f"**{title}** (релевантность: {score:.2f})\n{content}"
            
            # Check if adding this entry would exceed length limit
            if total_length + len(entry_text) > max_length and context_parts:
                break
                
            context_parts.append(entry_text)
            total_length += len(entry_text)
        
        formatted_context = "\n\n".join(context_parts)
        
        # Add truncation notice if needed
        if total_length > max_length:
            truncated = formatted_context[:max_length] + "..."
            truncated += "\n\n[Контекст сокращен для оптимизации]"
            return truncated
            
        return formatted_context


# Global instance
knowledge_search_engine = KnowledgeSearchEngine()