#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Integration Test for AI Agent Improvements
Простой интеграционный тест для улучшений ИИ-агентов
"""

import os
import sys

# Set up environment
os.environ['DB_TYPE'] = 'sqlite'
os.environ['MISTRAL_API_KEY'] = 'test-key'

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_module_imports():
    """Test that all new modules can be imported"""
    print("🔄 Testing module imports...")
    
    try:
        from knowledge_search import KnowledgeSearchEngine, knowledge_search_engine
        print("✅ Knowledge search module imported successfully")
        
        from prompt_engineering import PromptEngineer, prompt_engineer 
        print("✅ Prompt engineering module imported successfully")
        
        from response_cache import ResponseCache, response_cache
        print("✅ Response cache module imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_knowledge_search_functionality():
    """Test knowledge search engine functionality"""
    print("\n🔄 Testing knowledge search functionality...")
    
    try:
        from knowledge_search import knowledge_search_engine
        
        # Test text preprocessing
        text = "Как поступить в университет? Документы и требования."
        processed = knowledge_search_engine.preprocess_text(text, 'ru')
        assert len(processed) > 0, "Text preprocessing failed"
        print("✅ Text preprocessing works")
        
        # Test fuzzy matching
        score = knowledge_search_engine.fuzzy_match_score("поступление", "поступление в университет")
        assert score == 1.0, "Fuzzy matching failed for exact match"
        print("✅ Fuzzy matching works")
        
        # Test relevance scoring
        entry = {
            'title': 'Поступление',
            'content': 'Информация о поступлении в университет',
            'keywords': 'поступление, документы',
            'priority': 1
        }
        score = knowledge_search_engine.calculate_relevance_score("поступление документы", entry, 'ru')
        assert score > 0, "Relevance scoring failed"
        print("✅ Relevance scoring works")
        
        return True
    except Exception as e:
        print(f"❌ Knowledge search test error: {e}")
        return False

def test_prompt_engineering_functionality():
    """Test prompt engineering functionality"""
    print("\n🔄 Testing prompt engineering functionality...")
    
    try:
        from prompt_engineering import prompt_engineer
        
        # Test token estimation
        text = "Тестовый текст для подсчета токенов"
        tokens = prompt_engineer.estimate_token_count(text)
        assert tokens > 0, "Token estimation failed"
        print("✅ Token estimation works")
        
        # Test context quality assessment
        context = "**Заголовок**\nПолезная информация о поступлении"
        query = "информация поступление"
        quality = prompt_engineer.assess_context_quality(context, query)
        assert 'relevance' in quality, "Context quality assessment failed"
        print("✅ Context quality assessment works")
        
        # Test prompt generation
        system_prompt = "Вы помощник университета"
        context = "Информация о поступлении"
        user_query = "Как поступить?"
        
        enhanced_prompt, metrics = prompt_engineer.generate_enhanced_prompt(
            system_prompt, context, user_query, 'ru'
        )
        assert len(enhanced_prompt) > 0, "Enhanced prompt generation failed"
        assert 'relevance' in metrics, "Metrics generation failed"
        print("✅ Enhanced prompt generation works")
        
        return True
    except Exception as e:
        print(f"❌ Prompt engineering test error: {e}")
        return False

def test_response_cache_functionality():
    """Test response caching functionality"""
    print("\n🔄 Testing response cache functionality...")
    
    try:
        from response_cache import ResponseCache
        
        cache = ResponseCache(max_size=10, default_ttl=60)
        
        # Test cache operations
        message = "тест вопрос"
        agent_type = "test_agent"
        response_data = {'response': 'тест ответ', 'confidence': 0.8}
        
        # Should be empty initially
        cached = cache.get(message, agent_type)
        assert cached is None, "Cache should be empty initially"
        
        # Set and get
        success = cache.set(message, agent_type, response_data)
        assert success, "Cache set failed"
        
        cached = cache.get(message, agent_type)
        assert cached is not None, "Cache get failed"
        assert cached['response'] == 'тест ответ', "Cached content mismatch"
        print("✅ Response caching works")
        
        # Test cache heuristics
        good_response = {
            'response': 'Подробный ответ на вопрос пользователя с полезной информацией для поступления',
            'confidence': 0.8
        }
        should_cache = cache.should_cache("хороший длинный вопрос о поступлении", good_response)
        assert should_cache, "Should cache good responses"
        
        bad_response = {'response': 'Короткий', 'confidence': 0.2}
        should_not_cache = cache.should_cache("вопрос", bad_response)
        assert not should_not_cache, "Should not cache bad responses"
        print("✅ Cache heuristics work")
        
        return True
    except Exception as e:
        print(f"❌ Response cache test error: {e}")
        return False

def test_system_integration():
    """Test basic system integration"""
    print("\n🔄 Testing system integration...")
    
    try:
        # Test that Flask app can be created with new modules
        from app import create_app
        app = create_app()
        
        # Test that agents can be imported
        from agents import AgentRouter
        router = AgentRouter()
        
        assert len(router.agents) > 0, "No agents found"
        print(f"✅ System integration works - {len(router.agents)} agents loaded")
        
        return True
    except Exception as e:
        print(f"❌ System integration test error: {e}")
        return False

def run_integration_tests():
    """Run all integration tests"""
    print("🧪 Запуск интеграционных тестов улучшений...")
    print("🧪 Running integration tests for improvements...")
    
    tests = [
        ("Module Imports", test_module_imports),
        ("Knowledge Search", test_knowledge_search_functionality),
        ("Prompt Engineering", test_prompt_engineering_functionality),
        ("Response Cache", test_response_cache_functionality),
        ("System Integration", test_system_integration)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
                failed += 1
        except Exception as e:
            print(f"💥 {test_name} ERROR: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print("📊 FINAL RESULTS / ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
    print('='*50)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! ALL TESTS PASSED!")
        print("🚀 Улучшения готовы к использованию!")
        print("🚀 Improvements are ready for use!")
    else:
        print(f"\n⚠️  {failed} тестов провалилось. Требуется доработка.")
        print(f"⚠️  {failed} tests failed. Needs more work.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)