"""
Advanced Semantic Search with Embeddings and Knowledge Graphs
Расширенный семантический поиск с эмбеддингами и графами знаний

This module provides advanced semantic search capabilities using
text embeddings and knowledge graph relationships.
"""

import logging
import re
import json
import math
from typing import Dict, List, Tuple, Optional, Set, Any
from collections import defaultdict, Counter
import hashlib

logger = logging.getLogger(__name__)


class SemanticSearchEngine:
    """Advanced semantic search with embeddings simulation and knowledge graphs"""
    
    def __init__(self):
        self.knowledge_graph = {}  # Simple knowledge graph representation
        self.concept_embeddings = {}  # Simulated embeddings for concepts
        self.entity_relationships = defaultdict(set)
        self.concept_synonyms = {}
        
        # Initialize with university domain knowledge
        self._initialize_domain_knowledge()
        
        # Semantic similarity cache
        self.similarity_cache = {}
        
    def _initialize_domain_knowledge(self):
        """Initialize domain-specific knowledge graph and concepts"""
        
        # Define university domain concepts and relationships
        university_concepts = {
            'поступление': {
                'synonyms': ['зачисление', 'приём', 'admission', 'enrollment'],
                'related': ['документы', 'экзамены', 'требования', 'специальности'],
                'category': 'academic_process'
            },
            'документы': {
                'synonyms': ['справки', 'certificates', 'papers'],
                'related': ['аттестат', 'паспорт', 'фотографии', 'заявление'],
                'category': 'documentation'
            },
            'расписание': {
                'synonyms': ['schedule', 'timetable', 'график'],
                'related': ['занятия', 'время', 'аудитории', 'преподаватели'],
                'category': 'academic_schedule'
            },
            'общежитие': {
                'synonyms': ['dormitory', 'residence', 'жилье'],
                'related': ['заселение', 'комнаты', 'администрация', 'проживание'],
                'category': 'accommodation'
            },
            'работа': {
                'synonyms': ['трудоустройство', 'карьера', 'job', 'employment'],
                'related': ['резюме', 'вакансии', 'собеседование', 'стажировка'],
                'category': 'career'
            },
            'отпуск': {
                'synonyms': ['vacation', 'leave', 'каникулы'],
                'related': ['заявление', 'дни', 'график', 'замещение'],
                'category': 'hr_procedures'
            },
            'экзамены': {
                'synonyms': ['exams', 'tests', 'зачеты'],
                'related': ['оценки', 'пересдача', 'расписание', 'билеты'],
                'category': 'academic_assessment'
            },
            'стипендия': {
                'synonyms': ['scholarship', 'grant', 'пособие'],
                'related': ['выплаты', 'успеваемость', 'льготы', 'документы'],
                'category': 'financial_support'
            }
        }
        
        # Build knowledge graph
        for concept, data in university_concepts.items():
            self.knowledge_graph[concept] = data
            
            # Store synonyms
            self.concept_synonyms[concept] = set(data['synonyms'])
            for synonym in data['synonyms']:
                self.concept_synonyms[synonym] = {concept}
            
            # Build relationships
            for related_concept in data['related']:
                self.entity_relationships[concept].add(related_concept)
                self.entity_relationships[related_concept].add(concept)
        
        # Simulate embeddings using simple word co-occurrence
        self._generate_concept_embeddings()
    
    def _generate_concept_embeddings(self):
        """Generate simple embeddings for concepts based on relationships"""
        # Simple embedding simulation: use concept relationships as features
        all_concepts = set(self.knowledge_graph.keys())
        
        for concept in all_concepts:
            # Create feature vector based on related concepts
            embedding = {}
            
            # Direct relationships
            related = self.entity_relationships.get(concept, set())
            for rel_concept in related:
                embedding[rel_concept] = 1.0
            
            # Category-based features
            concept_data = self.knowledge_graph.get(concept, {})
            category = concept_data.get('category', '')
            if category:
                embedding[f'category_{category}'] = 2.0
            
            # Synonym-based features
            synonyms = self.concept_synonyms.get(concept, set())
            for synonym in synonyms:
                embedding[f'synonym_{synonym}'] = 1.5
            
            # Normalize embedding
            if embedding:
                norm = math.sqrt(sum(v * v for v in embedding.values()))
                if norm > 0:
                    embedding = {k: v / norm for k, v in embedding.items()}
            
            self.concept_embeddings[concept] = embedding
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        # Create cache key
        key = hashlib.md5(f"{text1}|{text2}".encode()).hexdigest()[:12]
        if key in self.similarity_cache:
            return self.similarity_cache[key]
        
        # Extract concepts from both texts
        concepts1 = self._extract_concepts(text1.lower())
        concepts2 = self._extract_concepts(text2.lower())
        
        if not concepts1 or not concepts2:
            similarity = self._calculate_lexical_similarity(text1, text2)
        else:
            # Calculate concept-based similarity
            similarity = self._calculate_concept_similarity(concepts1, concepts2)
        
        # Cache result
        self.similarity_cache[key] = similarity
        
        return similarity
    
    def _extract_concepts(self, text: str) -> Set[str]:
        """Extract known concepts from text"""
        concepts = set()
        text_words = set(re.findall(r'\b\w+\b', text.lower()))
        
        # Direct concept matches
        for concept in self.knowledge_graph:
            if concept in text:
                concepts.add(concept)
        
        # Synonym matches
        for word in text_words:
            if word in self.concept_synonyms:
                concepts.update(self.concept_synonyms[word])
        
        # Partial matches for compound concepts
        for concept in self.knowledge_graph:
            concept_words = set(concept.split())
            if concept_words.intersection(text_words):
                concepts.add(concept)
        
        return concepts
    
    def _calculate_concept_similarity(self, concepts1: Set[str], concepts2: Set[str]) -> float:
        """Calculate similarity based on concept embeddings"""
        if not concepts1 or not concepts2:
            return 0.0
        
        # Direct concept overlap
        direct_overlap = len(concepts1.intersection(concepts2))
        max_concepts = max(len(concepts1), len(concepts2))
        direct_score = direct_overlap / max_concepts if max_concepts > 0 else 0
        
        # Embedding-based similarity
        embedding_scores = []
        for c1 in concepts1:
            for c2 in concepts2:
                if c1 in self.concept_embeddings and c2 in self.concept_embeddings:
                    embedding_sim = self._cosine_similarity(
                        self.concept_embeddings[c1],
                        self.concept_embeddings[c2]
                    )
                    embedding_scores.append(embedding_sim)
        
        embedding_score = max(embedding_scores) if embedding_scores else 0
        
        # Relationship-based similarity
        relationship_score = self._calculate_relationship_similarity(concepts1, concepts2)
        
        # Weighted combination
        final_score = (
            direct_score * 0.5 +
            embedding_score * 0.3 +
            relationship_score * 0.2
        )
        
        return min(1.0, final_score)
    
    def _calculate_relationship_similarity(self, concepts1: Set[str], concepts2: Set[str]) -> float:
        """Calculate similarity based on concept relationships"""
        relationship_matches = 0
        total_relationships = 0
        
        for c1 in concepts1:
            related1 = self.entity_relationships.get(c1, set())
            for c2 in concepts2:
                related2 = self.entity_relationships.get(c2, set())
                
                if related1 and related2:
                    overlap = len(related1.intersection(related2))
                    union = len(related1.union(related2))
                    if union > 0:
                        relationship_matches += overlap / union
                        total_relationships += 1
        
        return relationship_matches / total_relationships if total_relationships > 0 else 0
    
    def _cosine_similarity(self, embedding1: Dict[str, float], embedding2: Dict[str, float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        if not embedding1 or not embedding2:
            return 0.0
        
        # Get common features
        common_features = set(embedding1.keys()).intersection(set(embedding2.keys()))
        
        if not common_features:
            return 0.0
        
        # Calculate dot product and norms
        dot_product = sum(embedding1[f] * embedding2[f] for f in common_features)
        norm1 = math.sqrt(sum(v * v for v in embedding1.values()))
        norm2 = math.sqrt(sum(v * v for v in embedding2.values()))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _calculate_lexical_similarity(self, text1: str, text2: str) -> float:
        """Fallback lexical similarity calculation"""
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def semantic_search(self, query: str, knowledge_entries: List, 
                       language: str = 'ru', max_results: int = 5,
                       semantic_threshold: float = 0.2) -> List[Dict]:
        """
        Perform semantic search on knowledge entries
        
        Args:
            query: Search query
            knowledge_entries: List of knowledge base entries
            language: Query language
            max_results: Maximum results to return
            semantic_threshold: Minimum semantic similarity threshold
            
        Returns:
            List of ranked results with semantic scores
        """
        if not query or not knowledge_entries:
            return []
        
        scored_results = []
        
        for entry in knowledge_entries:
            # Get content based on language
            content = entry.content_ru if language == 'ru' else entry.content_kz
            if not content:
                continue
            
            # Calculate semantic similarity
            title_similarity = self.calculate_semantic_similarity(query, entry.title)
            content_similarity = self.calculate_semantic_similarity(query, content)
            
            # Calculate keyword semantic similarity
            keywords = entry.keywords or ''
            keyword_similarity = self.calculate_semantic_similarity(query, keywords)
            
            # Weighted semantic score
            semantic_score = (
                title_similarity * 0.4 +
                content_similarity * 0.4 +
                keyword_similarity * 0.2
            )
            
            # Add concept expansion boost
            query_concepts = self._extract_concepts(query.lower())
            entry_concepts = self._extract_concepts(f"{entry.title} {content} {keywords}".lower())
            
            if query_concepts and entry_concepts:
                concept_expansion_score = self._calculate_concept_expansion_score(
                    query_concepts, entry_concepts
                )
                semantic_score += concept_expansion_score * 0.1
            
            # Apply priority boost
            priority_boost = 1.0 / max(entry.priority or 1, 1) * 0.05
            semantic_score += priority_boost
            
            # Only include results above threshold
            if semantic_score >= semantic_threshold:
                scored_results.append({
                    'entry': entry,
                    'semantic_score': semantic_score,
                    'title_similarity': title_similarity,
                    'content_similarity': content_similarity,
                    'keyword_similarity': keyword_similarity,
                    'content': content,
                    'title': entry.title
                })
        
        # Sort by semantic score
        scored_results.sort(key=lambda x: x['semantic_score'], reverse=True)
        
        logger.info(f"Semantic search for '{query}': {len(scored_results)} results "
                   f"(best score: {scored_results[0]['semantic_score']:.3f})" if scored_results else "No results")
        
        return scored_results[:max_results]
    
    def _calculate_concept_expansion_score(self, query_concepts: Set[str], 
                                         entry_concepts: Set[str]) -> float:
        """Calculate score for concept expansion (related concepts)"""
        expansion_score = 0.0
        
        for query_concept in query_concepts:
            # Check for related concepts in entry
            related_concepts = self.entity_relationships.get(query_concept, set())
            
            for entry_concept in entry_concepts:
                if entry_concept in related_concepts:
                    expansion_score += 0.5  # Boost for related concepts
                
                # Check category relationships
                query_category = self.knowledge_graph.get(query_concept, {}).get('category')
                entry_category = self.knowledge_graph.get(entry_concept, {}).get('category')
                
                if query_category and entry_category and query_category == entry_category:
                    expansion_score += 0.3  # Boost for same category
        
        return min(1.0, expansion_score)
    
    def expand_query(self, query: str, expansion_level: str = 'medium') -> List[str]:
        """
        Expand query with related concepts and synonyms
        
        Args:
            query: Original query
            expansion_level: 'low', 'medium', 'high'
            
        Returns:
            List of expanded query terms
        """
        expanded_terms = [query]
        query_concepts = self._extract_concepts(query.lower())
        
        expansion_limits = {
            'low': 2,
            'medium': 4,
            'high': 6
        }
        limit = expansion_limits.get(expansion_level, 4)
        
        for concept in query_concepts:
            # Add synonyms
            synonyms = self.concept_synonyms.get(concept, set())
            for synonym in list(synonyms)[:limit//2]:
                expanded_terms.append(synonym)
            
            # Add related concepts
            related = self.entity_relationships.get(concept, set())
            for related_concept in list(related)[:limit//2]:
                expanded_terms.append(related_concept)
        
        return expanded_terms[:limit + 1]  # +1 for original query
    
    def get_concept_suggestions(self, partial_query: str) -> List[str]:
        """Get concept suggestions for autocomplete"""
        partial_lower = partial_query.lower()
        suggestions = []
        
        # Direct concept matches
        for concept in self.knowledge_graph:
            if concept.startswith(partial_lower):
                suggestions.append(concept)
        
        # Synonym matches
        for synonym in self.concept_synonyms:
            if synonym.startswith(partial_lower):
                suggestions.append(synonym)
        
        # Remove duplicates and sort by length (shorter first)
        suggestions = list(set(suggestions))
        suggestions.sort(key=len)
        
        return suggestions[:10]
    
    def analyze_query_semantics(self, query: str) -> Dict[str, Any]:
        """Analyze query semantics for debugging and optimization"""
        concepts = self._extract_concepts(query.lower())
        
        analysis = {
            'original_query': query,
            'extracted_concepts': list(concepts),
            'concept_categories': {},
            'related_concepts': {},
            'potential_expansions': []
        }
        
        for concept in concepts:
            concept_data = self.knowledge_graph.get(concept, {})
            if concept_data:
                analysis['concept_categories'][concept] = concept_data.get('category', 'unknown')
                analysis['related_concepts'][concept] = list(self.entity_relationships.get(concept, set()))
        
        # Generate potential query expansions
        analysis['potential_expansions'] = self.expand_query(query, 'medium')
        
        return analysis
    
    def update_knowledge_graph(self, concept: str, related_concepts: List[str], 
                             category: str = '', synonyms: List[str] = None):
        """Update knowledge graph with new concept"""
        if concept not in self.knowledge_graph:
            self.knowledge_graph[concept] = {
                'synonyms': synonyms or [],
                'related': related_concepts,
                'category': category
            }
        
        # Update relationships
        for related in related_concepts:
            self.entity_relationships[concept].add(related)
            self.entity_relationships[related].add(concept)
        
        # Update synonyms
        if synonyms:
            self.concept_synonyms[concept] = set(synonyms)
            for synonym in synonyms:
                if synonym not in self.concept_synonyms:
                    self.concept_synonyms[synonym] = set()
                self.concept_synonyms[synonym].add(concept)
        
        # Regenerate embeddings for updated concept
        self._generate_concept_embeddings()
        
        logger.info(f"Updated knowledge graph with concept: {concept}")
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """Get semantic search statistics"""
        return {
            'total_concepts': len(self.knowledge_graph),
            'total_relationships': sum(len(rels) for rels in self.entity_relationships.values()) // 2,
            'total_synonyms': sum(len(syns) for syns in self.concept_synonyms.values()),
            'cache_size': len(self.similarity_cache),
            'categories': list(set(
                data.get('category', 'unknown') 
                for data in self.knowledge_graph.values()
            ))
        }


# Global semantic search engine
semantic_search_engine = SemanticSearchEngine()