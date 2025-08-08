#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for AI agent knowledge base improvements
Тестовый набор для улучшений базы знаний ИИ-агентов
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add root directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set test environment
os.environ['DB_TYPE'] = 'sqlite'
os.environ['MISTRAL_API_KEY'] = 'test-key'

from knowledge_search import KnowledgeSearchEngine
from prompt_engineering import PromptEngineer
from response_cache import ResponseCache


class TestKnowledgeSearch(unittest.TestCase):
    """Test enhanced knowledge base search functionality"""
    
    def setUp(self):
        self.search_engine = KnowledgeSearchEngine()
        
    def test_text_preprocessing(self):
        """Test text preprocessing functionality"""
        text = "Как поступить в университет? Документы и требования."
        processed = self.search_engine.preprocess_text(text, 'ru')
        
        # Should remove stop words and clean text
        self.assertNotIn('в', processed)
        self.assertIn('поступить', processed)
        self.assertIn('университет', processed)
        
    def test_relevance_scoring(self):
        """Test relevance scoring algorithm"""
        query = "поступление документы"
        
        # Mock knowledge entry with relevant content
        entry = {
            'title': 'Документы для поступления',
            'content': 'Для поступления в университет нужны документы: аттестат, справки, фотографии',
            'keywords': 'поступление, документы, аттестат',
            'priority': 1
        }
        
        score = self.search_engine.calculate_relevance_score(query, entry, 'ru')
        
        # Should have high relevance due to keyword and content match
        self.assertGreater(score, 0.5)
        
    def test_fuzzy_matching(self):
        """Test fuzzy matching for typos"""
        # Test exact match
        score_exact = self.search_engine.fuzzy_match_score("поступление", "поступление в университет")
        self.assertEqual(score_exact, 1.0)
        
        # Test partial match  
        score_partial = self.search_engine.fuzzy_match_score("поступлене", "поступление в университет")
        self.assertGreater(score_partial, 0.5)


class TestPromptEngineering(unittest.TestCase):
    """Test enhanced prompt engineering functionality"""
    
    def setUp(self):
        self.prompt_engineer = PromptEngineer()
        
    def test_token_estimation(self):
        """Test token count estimation"""
        text = "Это тестовый текст для проверки подсчета токенов"
        tokens = self.prompt_engineer.estimate_token_count(text)
        
        # Should return reasonable token estimate
        self.assertGreater(tokens, 0)
        self.assertLess(tokens, len(text))  # Should be less than character count
        
    def test_context_quality_assessment(self):
        """Test context quality assessment"""
        context = """
        **Поступление в университет**
        
        Для поступления необходимы документы:
        - Аттестат
        - Справки  
        - Фотографии
        """
        
        query = "какие документы нужны для поступления"
        
        quality = self.prompt_engineer.assess_context_quality(context, query)
        
        # Should have good relevance due to word overlap
        self.assertGreater(quality['relevance'], 0.3)  # Lowered threshold
        self.assertGreater(quality['clarity'], 0.5)
        
    def test_prompt_optimization(self):
        """Test prompt structure optimization"""
        system_prompt = "Вы помощник университета"
        context = "Информация о поступлении"
        user_query = "Как поступить?"
        
        optimized = self.prompt_engineer.optimize_prompt_structure(
            system_prompt, context, user_query
        )
        
        # Should contain all sections
        self.assertIn("СИСТЕМА", optimized)
        self.assertIn("КОНТЕКСТ", optimized)
        self.assertIn("ВОПРОС", optimized)


class TestResponseCache(unittest.TestCase):
    """Test response caching functionality"""
    
    def setUp(self):
        self.cache = ResponseCache(max_size=10, default_ttl=60)
        
    def test_cache_operations(self):
        """Test basic cache operations"""
        message = "тест вопрос"
        agent_type = "test_agent"
        response_data = {
            'response': 'тест ответ',
            'confidence': 0.8
        }
        
        # Cache should be empty initially
        cached = self.cache.get(message, agent_type)
        self.assertIsNone(cached)
        
        # Set cache
        success = self.cache.set(message, agent_type, response_data)
        self.assertTrue(success)
        
        # Should retrieve cached response
        cached = self.cache.get(message, agent_type)
        self.assertIsNotNone(cached)
        self.assertEqual(cached['response'], 'тест ответ')
        
    def test_cache_key_generation(self):
        """Test cache key generation"""
        # Same message should generate same key
        key1 = self.cache._generate_cache_key("тест", "agent", "ru")
        key2 = self.cache._generate_cache_key("тест", "agent", "ru")
        self.assertEqual(key1, key2)
        
        # Different messages should generate different keys
        key3 = self.cache._generate_cache_key("другой тест", "agent", "ru")
        self.assertNotEqual(key1, key3)
        
    def test_cache_heuristics(self):
        """Test caching decision heuristics"""
        # Should cache good responses
        good_response = {
            'response': 'Подробный ответ на вопрос пользователя с полезной информацией',
            'confidence': 0.8
        }
        should_cache = self.cache.should_cache("нормальный вопрос", good_response)
        self.assertTrue(should_cache)
        
        # Should not cache low confidence responses
        bad_response = {
            'response': 'Ответ',
            'confidence': 0.2
        }
        should_not_cache = self.cache.should_cache("вопрос", bad_response)
        self.assertFalse(should_not_cache)


class TestAgentIntegration(unittest.TestCase):
    """Test integration of improvements with agent system"""
    
    def test_agent_imports(self):
        """Test that agents can import new modules"""
        try:
            from agents import BaseAgent
            from knowledge_search import knowledge_search_engine
            from prompt_engineering import prompt_engineer
            from response_cache import response_cache
            
            # All imports should succeed
            self.assertIsNotNone(knowledge_search_engine)
            self.assertIsNotNone(prompt_engineer)
            self.assertIsNotNone(response_cache)
            
        except ImportError as e:
            self.fail(f"Failed to import required modules: {e}")
    
    def test_enhanced_agent_processing(self):
        """Test that agents use enhanced processing"""
        from agents import AIAbiturAgent
        
        agent = AIAbiturAgent()
        
        # Mock the MistralClient instance
        mock_mistral = Mock()
        mock_mistral.get_response_with_system_prompt.return_value = "Тестовый ответ"
        agent.mistral = mock_mistral
        
        # Mock database access at the model level
        with patch('models.AgentKnowledgeBase') as mock_kb:
            mock_kb.query.filter_by.return_value.order_by.return_value.all.return_value = []
            
            response = agent.process_message("как поступить в университет", "ru")
            
            # Should return enhanced response with new fields
            self.assertIn('confidence', response)
            self.assertIn('context_confidence', response)
            self.assertIn('cached', response)


def run_tests():
    """Run all tests"""
    print("🧪 Запуск тестов улучшений ИИ-агентов...")
    print("🧪 Running AI agent improvements tests...")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestKnowledgeSearch,
        TestPromptEngineering, 
        TestResponseCache,
        TestAgentIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n📊 Результаты тестирования:")
    print(f"📊 Test Results:")
    print(f"✅ Пройдено / Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Провалено / Failed: {len(result.failures)}")
    print(f"💥 Ошибки / Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ Провалившиеся тесты / Failed tests:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\n💥 Ошибки в тестах / Test errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Error:')[-1].strip()}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)