"""
User Personalization and Learning System
Система персонализации и обучения пользователей

This module provides user learning, personalization, and adaptive response
capabilities for the AI agent system.
"""

import logging
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, deque
import hashlib

logger = logging.getLogger(__name__)


class UserProfile:
    """Individual user profile with learning history"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.created_at = time.time()
        self.interaction_count = 0
        
        # Preference tracking
        self.preferred_agents = defaultdict(int)
        self.language_preference = 'ru'
        self.response_style_preference = 'detailed'  # detailed, concise, intermediate
        self.topic_interests = defaultdict(float)
        
        # Behavioral patterns
        self.session_patterns = {
            'avg_session_length': 0,
            'typical_question_types': defaultdict(int),
            'interaction_times': deque(maxlen=100)  # Recent interaction timestamps
        }
        
        # Learning history
        self.learning_history = {
            'successful_interactions': [],
            'problematic_interactions': [],
            'feedback_given': [],
            'satisfaction_trend': deque(maxlen=50)
        }
        
        # Adaptation preferences
        self.adaptation_settings = {
            'auto_agent_selection': True,
            'context_level': 'medium',  # low, medium, high
            'explanation_level': 'medium',
            'follow_up_suggestions': True
        }
    
    def update_interaction(self, interaction_data: Dict[str, Any]):
        """Update profile based on new interaction"""
        self.interaction_count += 1
        
        # Update agent preferences
        agent_type = interaction_data.get('agent_type')
        if agent_type:
            confidence = interaction_data.get('confidence', 0)
            # Weight by confidence and user satisfaction
            user_rating = interaction_data.get('user_rating')
            weight = confidence
            if user_rating:
                weight = (confidence + user_rating) / 2
            
            self.preferred_agents[agent_type] += weight
        
        # Update language preference
        language = interaction_data.get('language', 'ru')
        if language != self.language_preference:
            # Gradual language preference adjustment
            self.language_preference = language
        
        # Update topic interests based on message content
        message = interaction_data.get('message', '').lower()
        self._extract_and_update_topics(message, interaction_data.get('confidence', 0))
        
        # Track session patterns
        self.session_patterns['interaction_times'].append(time.time())
        
        # Update question type patterns
        question_type = self._classify_question_type(message)
        self.session_patterns['typical_question_types'][question_type] += 1
        
        # Store learning data
        if interaction_data.get('confidence', 0) > 0.8:
            self.learning_history['successful_interactions'].append(interaction_data)
        elif interaction_data.get('confidence', 0) < 0.3:
            self.learning_history['problematic_interactions'].append(interaction_data)
        
        # Limit history size
        if len(self.learning_history['successful_interactions']) > 100:
            self.learning_history['successful_interactions'] = self.learning_history['successful_interactions'][-50:]
        if len(self.learning_history['problematic_interactions']) > 50:
            self.learning_history['problematic_interactions'] = self.learning_history['problematic_interactions'][-25:]
    
    def add_feedback(self, rating: float, feedback_text: str = ''):
        """Add user feedback to profile"""
        feedback = {
            'rating': rating,
            'text': feedback_text,
            'timestamp': time.time()
        }
        
        self.learning_history['feedback_given'].append(feedback)
        self.learning_history['satisfaction_trend'].append(rating)
        
        # Limit feedback history
        if len(self.learning_history['feedback_given']) > 100:
            self.learning_history['feedback_given'] = self.learning_history['feedback_given'][-50:]
    
    def get_preferred_agent(self) -> Optional[str]:
        """Get user's preferred agent based on interaction history"""
        if not self.preferred_agents:
            return None
        
        # Weight recent interactions more heavily
        weighted_preferences = {}
        total_weight = sum(self.preferred_agents.values())
        
        for agent, score in self.preferred_agents.items():
            weighted_preferences[agent] = score / total_weight
        
        # Return agent with highest weighted preference
        return max(weighted_preferences.items(), key=lambda x: x[1])[0]
    
    def get_satisfaction_trend(self) -> float:
        """Get recent satisfaction trend (-1 to 1, where 1 is improving)"""
        if len(self.learning_history['satisfaction_trend']) < 3:
            return 0.0
        
        recent_ratings = list(self.learning_history['satisfaction_trend'])
        
        # Compare recent half with earlier half
        mid_point = len(recent_ratings) // 2
        earlier_avg = sum(recent_ratings[:mid_point]) / mid_point
        recent_avg = sum(recent_ratings[mid_point:]) / (len(recent_ratings) - mid_point)
        
        # Normalize difference to -1 to 1 range
        max_rating = 1.0  # Assuming ratings are 0-1
        trend = (recent_avg - earlier_avg) / max_rating
        return max(-1, min(1, trend))
    
    def _extract_and_update_topics(self, message: str, confidence: float):
        """Extract topics from message and update interests"""
        # Simple topic extraction based on keywords
        topic_keywords = {
            'admission': ['поступление', 'зачисление', 'документы', 'экзамен'],
            'schedule': ['расписание', 'занятие', 'время', 'аудитория'],
            'grades': ['оценка', 'зачет', 'экзамен', 'балл'],
            'dormitory': ['общежитие', 'заселение', 'комната'],
            'career': ['работа', 'карьера', 'трудоустройство', 'резюме'],
            'hr': ['отпуск', 'зарплата', 'кадры', 'сотрудник'],
            'academic': ['учеба', 'предмет', 'дисциплина', 'курс']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in message for keyword in keywords):
                # Weight by confidence
                self.topic_interests[topic] += confidence * 0.1
        
        # Decay old interests slightly
        for topic in self.topic_interests:
            self.topic_interests[topic] *= 0.99
    
    def _classify_question_type(self, message: str) -> str:
        """Classify the type of question"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['как', 'каким образом']):
            return 'how'
        elif any(word in message_lower for word in ['что', 'какой', 'какая', 'какие']):
            return 'what'
        elif any(word in message_lower for word in ['когда', 'во сколько']):
            return 'when'
        elif any(word in message_lower for word in ['где', 'куда']):
            return 'where'
        elif any(word in message_lower for word in ['почему', 'зачем']):
            return 'why'
        else:
            return 'general'
    
    def get_personalization_context(self) -> Dict[str, Any]:
        """Get context for personalizing responses"""
        return {
            'user_id': self.user_id,
            'interaction_count': self.interaction_count,
            'preferred_agent': self.get_preferred_agent(),
            'language_preference': self.language_preference,
            'response_style': self.response_style_preference,
            'top_topics': dict(sorted(self.topic_interests.items(), 
                                    key=lambda x: x[1], reverse=True)[:3]),
            'satisfaction_trend': self.get_satisfaction_trend(),
            'adaptation_settings': self.adaptation_settings
        }


class PersonalizationEngine:
    """Main personalization engine managing user profiles and adaptive responses"""
    
    def __init__(self):
        self.user_profiles: Dict[str, UserProfile] = {}
        self.global_patterns = {
            'popular_topics': defaultdict(float),
            'effective_agents': defaultdict(float),
            'common_question_patterns': defaultdict(int)
        }
        
        # Personalization strategies
        self.strategies = {
            'agent_recommendation': True,
            'response_adaptation': True,
            'proactive_suggestions': True,
            'learning_optimization': True
        }
    
    def get_or_create_profile(self, user_id: str) -> UserProfile:
        """Get existing user profile or create new one"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(user_id)
            logger.info(f"Created new user profile: {user_id}")
        
        return self.user_profiles[user_id]
    
    def update_user_interaction(self, user_id: str, interaction_data: Dict[str, Any]):
        """Update user profile with new interaction"""
        profile = self.get_or_create_profile(user_id)
        profile.update_interaction(interaction_data)
        
        # Update global patterns
        agent_type = interaction_data.get('agent_type')
        if agent_type:
            confidence = interaction_data.get('confidence', 0)
            self.global_patterns['effective_agents'][agent_type] += confidence
        
        # Extract and track topics globally
        message = interaction_data.get('message', '').lower()
        self._update_global_topic_tracking(message, interaction_data.get('confidence', 0))
        
        logger.debug(f"Updated user profile: {user_id}")
    
    def add_user_feedback(self, user_id: str, rating: float, feedback_text: str = ''):
        """Add user feedback to profile"""
        profile = self.get_or_create_profile(user_id)
        profile.add_feedback(rating, feedback_text)
        
        logger.info(f"Added feedback for user {user_id}: rating={rating}")
    
    def get_agent_recommendation(self, user_id: str, message: str, 
                               available_agents: List[str]) -> Optional[Tuple[str, float]]:
        """Get personalized agent recommendation"""
        if not self.strategies['agent_recommendation']:
            return None
        
        profile = self.get_or_create_profile(user_id)
        
        # Get user's preferred agent
        preferred_agent = profile.get_preferred_agent()
        
        # If user has a strong preference and agent is available, recommend it
        if preferred_agent and preferred_agent in available_agents:
            # Calculate confidence based on user's history with this agent
            agent_interactions = profile.preferred_agents[preferred_agent]
            total_interactions = sum(profile.preferred_agents.values())
            
            if total_interactions > 0:
                preference_strength = agent_interactions / total_interactions
                
                # Boost confidence if user has positive satisfaction trend
                satisfaction_trend = profile.get_satisfaction_trend()
                confidence = preference_strength + (satisfaction_trend * 0.1)
                confidence = max(0.1, min(1.0, confidence))
                
                return preferred_agent, confidence
        
        return None
    
    def adapt_response_style(self, user_id: str, base_response: str) -> str:
        """Adapt response style based on user preferences"""
        if not self.strategies['response_adaptation']:
            return base_response
        
        profile = self.get_or_create_profile(user_id)
        personalization = profile.get_personalization_context()
        
        # Adapt based on response style preference
        style = personalization['response_style']
        
        if style == 'concise':
            # Make response more concise
            adapted_response = self._make_concise(base_response)
        elif style == 'detailed':
            # Add more context and explanation
            adapted_response = self._add_detail(base_response, personalization)
        else:
            adapted_response = base_response
        
        # Add personalization touches
        if personalization['interaction_count'] > 1:
            adapted_response = self._add_personalization_touches(adapted_response, personalization)
        
        return adapted_response
    
    def generate_proactive_suggestions(self, user_id: str, 
                                     current_context: str) -> List[str]:
        """Generate proactive suggestions based on user history"""
        if not self.strategies['proactive_suggestions']:
            return []
        
        profile = self.get_or_create_profile(user_id)
        suggestions = []
        
        # Suggest based on user's top topics
        top_topics = profile.get_personalization_context()['top_topics']
        
        for topic, interest_score in top_topics.items():
            if interest_score > 0.5:  # Significant interest
                suggestion = self._generate_topic_suggestion(topic, current_context)
                if suggestion:
                    suggestions.append(suggestion)
        
        # Suggest based on common patterns
        common_question_type = max(profile.session_patterns['typical_question_types'].items(), 
                                 key=lambda x: x[1], default=(None, 0))[0]
        
        if common_question_type and len(suggestions) < 3:
            type_suggestion = self._generate_question_type_suggestion(common_question_type)
            if type_suggestion:
                suggestions.append(type_suggestion)
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def optimize_for_learning(self, user_id: str, message: str) -> Dict[str, Any]:
        """Optimize interaction for user learning"""
        if not self.strategies['learning_optimization']:
            return {}
        
        profile = self.get_or_create_profile(user_id)
        personalization = profile.get_personalization_context()
        
        optimization = {
            'explanation_level': personalization['adaptation_settings']['explanation_level'],
            'follow_up_enabled': personalization['adaptation_settings']['follow_up_suggestions'],
            'context_verbosity': personalization['adaptation_settings']['context_level']
        }
        
        # Adjust based on satisfaction trend
        satisfaction_trend = personalization['satisfaction_trend']
        
        if satisfaction_trend < -0.3:  # Declining satisfaction
            # Provide more detailed explanations and context
            optimization['explanation_level'] = 'high'
            optimization['context_verbosity'] = 'high'
            optimization['follow_up_enabled'] = True
        elif satisfaction_trend > 0.3:  # Improving satisfaction
            # User is learning well, can handle more concise responses
            if personalization['interaction_count'] > 10:
                optimization['explanation_level'] = 'medium'
        
        return optimization
    
    def _update_global_topic_tracking(self, message: str, confidence: float):
        """Update global topic popularity tracking"""
        topic_keywords = {
            'admission': ['поступление', 'зачисление', 'документы'],
            'schedule': ['расписание', 'занятие', 'время'],
            'grades': ['оценка', 'зачет', 'экзамен'],
            'dormitory': ['общежитие', 'заселение'],
            'career': ['работа', 'карьера', 'трудоустройство'],
            'hr': ['отпуск', 'зарплата', 'кадры'],
            'academic': ['учеба', 'предмет', 'дисциплина']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in message for keyword in keywords):
                self.global_patterns['popular_topics'][topic] += confidence * 0.1
    
    def _make_concise(self, response: str) -> str:
        """Make response more concise"""
        # Simple conciseness: remove redundant phrases and shorten
        concise_response = response.replace('Пожалуйста, обратите внимание, что', '')
        concise_response = concise_response.replace('Хочу отметить, что', '')
        concise_response = concise_response.replace('Важно понимать, что', '')
        
        # Split into sentences and keep only essential ones
        sentences = concise_response.split('.')
        essential_sentences = [s.strip() for s in sentences if len(s.strip()) > 20][:3]
        
        return '. '.join(essential_sentences) + '.'
    
    def _add_detail(self, response: str, personalization: Dict) -> str:
        """Add more detail and context to response"""
        # Add context based on user interests
        top_topics = personalization.get('top_topics', {})
        
        additional_context = []
        
        if 'admission' in top_topics:
            additional_context.append("💡 **Совет**: Рекомендуем также ознакомиться с требованиями к документам.")
        
        if 'schedule' in top_topics:
            additional_context.append("📅 **Дополнительно**: Расписание может изменяться, следите за обновлениями.")
        
        if additional_context:
            detailed_response = response + "\n\n" + "\n".join(additional_context)
        else:
            detailed_response = response
        
        return detailed_response
    
    def _add_personalization_touches(self, response: str, personalization: Dict) -> str:
        """Add personalization touches to response"""
        interaction_count = personalization['interaction_count']
        
        # Add personalized greeting for returning users
        if interaction_count > 5:
            personalized_response = response + f"\n\n*Рад помочь вам снова! Это ваше {interaction_count}-е обращение.*"
        elif interaction_count > 1:
            personalized_response = response + "\n\n*Надеюсь, информация будет полезной!*"
        else:
            personalized_response = response
        
        return personalized_response
    
    def _generate_topic_suggestion(self, topic: str, current_context: str) -> Optional[str]:
        """Generate suggestion based on user's topic interest"""
        suggestions = {
            'admission': "Возможно, вас также интересуют сроки подачи документов?",
            'schedule': "Хотите узнать о изменениях в расписании?",
            'grades': "Интересует процедура пересдачи экзаменов?",
            'dormitory': "Нужна информация о правилах проживания в общежитии?",
            'career': "Рассказать о карьерных возможностях для выпускников?",
            'hr': "Интересуют другие кадровые процедуры?",
            'academic': "Хотите узнать об академических программах?"
        }
        
        return suggestions.get(topic)
    
    def _generate_question_type_suggestion(self, question_type: str) -> Optional[str]:
        """Generate suggestion based on common question type"""
        suggestions = {
            'how': "Нужна пошаговая инструкция по процедуре?",
            'what': "Хотите более подробную информацию о деталях?",
            'when': "Интересуют точные сроки и временные рамки?",
            'where': "Нужна информация о местах и контактах?",
            'why': "Требуется объяснение причин и обоснований?"
        }
        
        return suggestions.get(question_type)
    
    def get_personalization_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get personalization statistics"""
        if user_id:
            # Stats for specific user
            profile = self.user_profiles.get(user_id)
            if not profile:
                return {'error': 'User not found'}
            
            return {
                'user_id': user_id,
                'total_interactions': profile.interaction_count,
                'preferred_agents': dict(profile.preferred_agents),
                'satisfaction_trend': profile.get_satisfaction_trend(),
                'top_topics': dict(sorted(profile.topic_interests.items(), 
                                        key=lambda x: x[1], reverse=True)[:5]),
                'question_types': dict(profile.session_patterns['typical_question_types'])
            }
        else:
            # Global stats
            total_users = len(self.user_profiles)
            total_interactions = sum(p.interaction_count for p in self.user_profiles.values())
            
            # Aggregate feedback
            all_satisfaction = []
            for profile in self.user_profiles.values():
                if profile.learning_history['satisfaction_trend']:
                    all_satisfaction.extend(profile.learning_history['satisfaction_trend'])
            
            avg_satisfaction = sum(all_satisfaction) / len(all_satisfaction) if all_satisfaction else 0
            
            return {
                'total_users': total_users,
                'total_interactions': total_interactions,
                'avg_satisfaction': round(avg_satisfaction, 3),
                'popular_topics': dict(sorted(self.global_patterns['popular_topics'].items(), 
                                            key=lambda x: x[1], reverse=True)[:5]),
                'effective_agents': dict(sorted(self.global_patterns['effective_agents'].items(), 
                                               key=lambda x: x[1], reverse=True))
            }


# Global personalization engine
personalization_engine = PersonalizationEngine()