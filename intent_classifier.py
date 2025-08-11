"""
ML-based Intent Classification System
Система классификации намерений на основе машинного обучения

This module provides machine learning-based intent classification
to replace simple keyword matching for better agent routing.
"""

import logging
import re
import json
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
from difflib import SequenceMatcher
import math

logger = logging.getLogger(__name__)


class MLIntentClassifier:
    """Machine Learning-based intent classifier for multi-agent routing"""
    
    def __init__(self):
        self.feature_weights = {
            'keyword_exact': 0.35,
            'keyword_semantic': 0.25,
            'domain_specific': 0.20,
            'context_patterns': 0.15,
            'question_type': 0.05
        }
        
        # Initialize agent training data
        self._init_training_data()
        
        # Initialize learned patterns
        self.learned_patterns = defaultdict(list)
        self.user_feedback = defaultdict(list)
        
    def _init_training_data(self):
        """Initialize training data for each agent with extended patterns"""
        self.training_data = {
            'ai_abitur': {
                'keywords': [
                    'поступление', 'поступаю', 'абитуриент', 'документы', 'экзамен', 
                    'приём', 'требования', 'специальности', 'факультет', 'зачисление',
                    'заявление', 'конкурс', 'баллы', 'аттестат', 'вступительные',
                    'подача', 'сроки', 'льготы', 'целевое', 'бюджет', 'платное'
                ],
                'patterns': [
                    r'как поступить',
                    r'какие документы',
                    r'когда подавать',
                    r'проходной балл',
                    r'вступительные экзамены',
                    r'специальности',
                    r'факультеты'
                ],
                'context_indicators': [
                    'школьник', 'выпускник', 'одиннадцатый класс', '11 класс',
                    'после школы', 'выбираю вуз', 'хочу учиться'
                ],
                'question_types': ['admission', 'requirements', 'faculties']
            },
            'kadrai': {
                'keywords': [
                    'кадры', 'отпуск', 'перевод', 'приказ', 'сотрудник', 'преподаватель',
                    'отдел кадров', 'трудовой', 'зарплата', 'кадровые', 'увольнение',
                    'прием на работу', 'должность', 'оклад', 'премия', 'больничный',
                    'декрет', 'командировка', 'аттестация', 'повышение'
                ],
                'patterns': [
                    r'оформить отпуск',
                    r'перевести на должность',
                    r'оформление документов',
                    r'трудовая книжка',
                    r'расчет зарплаты',
                    r'кадровые процедуры'
                ],
                'context_indicators': [
                    'сотрудник', 'работаю', 'преподаватель', 'администрация',
                    'коллега', 'отдел', 'кафедра'
                ],
                'question_types': ['hr_procedures', 'vacation', 'salary', 'documents']
            },
            'uninav': {
                'keywords': [
                    'расписание', 'учёба', 'занятие', 'заявление', 'обращение', 
                    'деканат', 'академический', 'экзамен', 'зачёт', 'лекция',
                    'семинар', 'практика', 'дисциплина', 'предмет', 'оценка',
                    'пересдача', 'академотпуск', 'перевод', 'восстановление'
                ],
                'patterns': [
                    r'расписание занятий',
                    r'когда экзамен',
                    r'где аудитория',
                    r'подать заявление',
                    r'академическая справка',
                    r'перевод на курс'
                ],
                'context_indicators': [
                    'студент', 'учусь', 'курс', 'группа', 'семестр',
                    'сессия', 'преподаватель'
                ],
                'question_types': ['schedule', 'academic', 'procedures', 'exams']
            },
            'career_navigator': {
                'keywords': [
                    'работа', 'трудоустройство', 'вакансии', 'резюме', 'карьера',
                    'выпускник', 'стажировка', 'работодатель', 'собеседование',
                    'поиск работы', 'профессия', 'навыки', 'опыт', 'практика',
                    'internship', 'cv', 'interview', 'job'
                ],
                'patterns': [
                    r'найти работу',
                    r'составить резюме',
                    r'поиск вакансий',
                    r'карьерное развитие',
                    r'стажировка',
                    r'трудоустройство'
                ],
                'context_indicators': [
                    'выпускник', 'ищу работу', 'карьера', 'профессия',
                    'трудоустройство', 'работодатель'
                ],
                'question_types': ['job_search', 'resume', 'career', 'internship']
            },
            'uniroom': {
                'keywords': [
                    'общежитие', 'заселение', 'переселение', 'бытовые', 'администрация',
                    'комната', 'жилищные', 'проживание', 'проблемы', 'соседи',
                    'коммунальные', 'ремонт', 'мебель', 'интернет', 'питание',
                    'охрана', 'пропуск', 'посетители'
                ],
                'patterns': [
                    r'заселиться в общежитие',
                    r'переселение',
                    r'проблемы в комнате',
                    r'бытовые вопросы',
                    r'администрация общежития'
                ],
                'context_indicators': [
                    'живу в общежитии', 'общага', 'комната', 'соседи',
                    'заселение', 'проживание'
                ],
                'question_types': ['accommodation', 'room_issues', 'services']
            }
        }
    
    def _extract_features(self, message: str, language: str = 'ru') -> Dict[str, float]:
        """Extract ML features from user message"""
        message_lower = message.lower()
        features = {}
        
        # Preprocessing
        # Remove punctuation and normalize
        clean_message = re.sub(r'[^\w\s]', ' ', message_lower)
        words = clean_message.split()
        
        # 1. Keyword exact match features
        for agent, data in self.training_data.items():
            exact_matches = sum(1 for keyword in data['keywords'] 
                              if keyword in message_lower)
            features[f'{agent}_keyword_exact'] = exact_matches / len(data['keywords'])
        
        # 2. Semantic similarity features (using word overlap)
        for agent, data in self.training_data.items():
            agent_words = set()
            for keyword in data['keywords']:
                agent_words.update(keyword.split())
            
            message_words = set(words)
            if agent_words and message_words:
                overlap = len(agent_words.intersection(message_words))
                features[f'{agent}_semantic'] = overlap / len(agent_words.union(message_words))
            else:
                features[f'{agent}_semantic'] = 0.0
        
        # 3. Domain-specific pattern matching
        for agent, data in self.training_data.items():
            pattern_matches = 0
            for pattern in data['patterns']:
                if re.search(pattern, message_lower):
                    pattern_matches += 1
            features[f'{agent}_patterns'] = pattern_matches / len(data['patterns'])
        
        # 4. Context indicators
        for agent, data in self.training_data.items():
            context_matches = sum(1 for indicator in data['context_indicators']
                                if indicator in message_lower)
            features[f'{agent}_context'] = context_matches / len(data['context_indicators'])
        
        # 5. Question type analysis
        question_indicators = {
            'what': ['что', 'какой', 'какая', 'какие'],
            'how': ['как', 'каким образом'],
            'when': ['когда', 'во сколько'],
            'where': ['где', 'куда'],
            'why': ['почему', 'зачем']
        }
        
        for q_type, indicators in question_indicators.items():
            if any(ind in message_lower for ind in indicators):
                features[f'question_{q_type}'] = 1.0
            else:
                features[f'question_{q_type}'] = 0.0
        
        return features
    
    def _calculate_agent_score(self, agent: str, features: Dict[str, float]) -> float:
        """Calculate ML-based score for agent using weighted features"""
        score = 0.0
        
        # Aggregate features for this agent
        keyword_exact = features.get(f'{agent}_keyword_exact', 0)
        semantic = features.get(f'{agent}_semantic', 0)
        patterns = features.get(f'{agent}_patterns', 0)
        context = features.get(f'{agent}_context', 0)
        
        # Question type bonus (some agents better for certain question types)
        question_bonus = 0.0
        if agent == 'ai_abitur':
            question_bonus = features.get('question_how', 0) * 0.3 + features.get('question_what', 0) * 0.2
        elif agent == 'uninav':
            question_bonus = features.get('question_when', 0) * 0.3 + features.get('question_where', 0) * 0.2
        elif agent == 'kadrai':
            question_bonus = features.get('question_how', 0) * 0.2
        
        # Weighted combination
        score = (
            keyword_exact * self.feature_weights['keyword_exact'] +
            semantic * self.feature_weights['keyword_semantic'] +
            patterns * self.feature_weights['domain_specific'] +
            context * self.feature_weights['context_patterns'] +
            question_bonus * self.feature_weights['question_type']
        )
        
        # Apply learned patterns boost
        if agent in self.learned_patterns:
            for pattern_data in self.learned_patterns[agent]:
                if pattern_data['confidence'] > 0.7:
                    similarity = SequenceMatcher(None, message.lower(), 
                                               pattern_data['message'].lower()).ratio()
                    if similarity > 0.6:
                        score *= 1.1  # 10% boost for learned patterns
                        break
        
        return min(1.0, max(0.0, score))
    
    def classify_intent(self, message: str, language: str = 'ru') -> Dict[str, float]:
        """
        Classify user intent using ML features
        
        Returns:
            Dict with agent names as keys and confidence scores as values
        """
        if not message.strip():
            return {}
        
        # Extract features
        features = self._extract_features(message, language)
        
        # Calculate scores for each agent
        agent_scores = {}
        for agent in self.training_data.keys():
            score = self._calculate_agent_score(agent, features)
            agent_scores[agent] = score
        
        # Normalize scores to ensure they sum to reasonable values
        max_score = max(agent_scores.values()) if agent_scores.values() else 0
        if max_score > 0:
            # Apply softmax-like normalization
            exp_scores = {agent: math.exp(score * 3) for agent, score in agent_scores.items()}
            sum_exp = sum(exp_scores.values())
            if sum_exp > 0:
                agent_scores = {agent: exp_score / sum_exp 
                              for agent, exp_score in exp_scores.items()}
        
        return agent_scores
    
    def get_best_agent(self, message: str, language: str = 'ru', 
                      min_confidence: float = 0.15) -> Tuple[Optional[str], float]:
        """
        Get the best agent for handling the message
        
        Returns:
            Tuple of (agent_name, confidence_score)
        """
        scores = self.classify_intent(message, language)
        
        if not scores:
            return None, 0.0
        
        best_agent = max(scores.items(), key=lambda x: x[1])
        agent_name, confidence = best_agent
        
        # Return None if confidence is too low
        if confidence < min_confidence:
            return None, confidence
            
        return agent_name, confidence
    
    def learn_from_feedback(self, message: str, actual_agent: str, 
                          user_rating: float, language: str = 'ru'):
        """
        Learn from user feedback to improve future classifications
        
        Args:
            message: Original user message
            actual_agent: Agent that was actually used
            user_rating: User satisfaction rating (0.0 to 1.0)
            language: Message language
        """
        # Store feedback for analysis
        feedback_data = {
            'message': message,
            'agent': actual_agent,
            'rating': user_rating,
            'language': language,
            'features': self._extract_features(message, language)
        }
        
        self.user_feedback[actual_agent].append(feedback_data)
        
        # If rating is high, add to learned patterns
        if user_rating >= 0.8:
            pattern_data = {
                'message': message,
                'confidence': user_rating,
                'language': language
            }
            self.learned_patterns[actual_agent].append(pattern_data)
            
            # Keep only recent high-quality patterns (max 100 per agent)
            if len(self.learned_patterns[actual_agent]) > 100:
                # Sort by confidence and keep top patterns
                self.learned_patterns[actual_agent].sort(
                    key=lambda x: x['confidence'], reverse=True
                )
                self.learned_patterns[actual_agent] = self.learned_patterns[actual_agent][:100]
        
        logger.info(f"Learned from feedback: {actual_agent} rating={user_rating:.2f}")
    
    def get_classification_explanation(self, message: str, language: str = 'ru') -> Dict:
        """Get detailed explanation of classification decision"""
        features = self._extract_features(message, language)
        scores = self.classify_intent(message, language)
        
        # Build explanation
        explanation = {
            'message': message,
            'agent_scores': scores,
            'feature_analysis': {},
            'decision_factors': []
        }
        
        # Analyze features for each agent
        for agent in self.training_data.keys():
            agent_features = {
                'keyword_exact': features.get(f'{agent}_keyword_exact', 0),
                'semantic': features.get(f'{agent}_semantic', 0),
                'patterns': features.get(f'{agent}_patterns', 0),
                'context': features.get(f'{agent}_context', 0)
            }
            explanation['feature_analysis'][agent] = agent_features
            
            # Identify top contributing factors
            top_feature = max(agent_features.items(), key=lambda x: x[1])
            if top_feature[1] > 0.1:
                explanation['decision_factors'].append({
                    'agent': agent,
                    'feature': top_feature[0],
                    'score': top_feature[1]
                })
        
        return explanation
    
    def get_learning_stats(self) -> Dict:
        """Get statistics about learned patterns and feedback"""
        stats = {
            'total_feedback': sum(len(feedback) for feedback in self.user_feedback.values()),
            'learned_patterns': sum(len(patterns) for patterns in self.learned_patterns.values()),
            'agent_feedback': {},
            'average_ratings': {}
        }
        
        for agent, feedback_list in self.user_feedback.items():
            stats['agent_feedback'][agent] = len(feedback_list)
            if feedback_list:
                avg_rating = sum(f['rating'] for f in feedback_list) / len(feedback_list)
                stats['average_ratings'][agent] = round(avg_rating, 3)
        
        return stats


# Global classifier instance
intent_classifier = MLIntentClassifier()