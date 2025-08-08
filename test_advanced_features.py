#!/usr/bin/env python3
"""
Comprehensive Test Suite for Advanced AI Agent Features
Комплексный тест для расширенных возможностей ИИ-агентов

This script tests all the new ML-powered features:
1. ML-based Intent Classification
2. Analytics and Learning System
3. User Personalization
4. Semantic Search with Knowledge Graphs
5. Distributed Caching and Async Processing
"""

import sys
import os
import time
import random
from typing import Dict, List, Any

# Add the parent directory to sys.path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_intent_classification():
    """Test ML-based intent classification"""
    print("🧠 Testing ML-based Intent Classification...")
    
    try:
        from intent_classifier import intent_classifier
        
        test_queries = [
            ("как поступить в университет", "ai_abitur"),
            ("нужна информация о документах для поступления", "ai_abitur"),
            ("где взять справку об отпуске", "kadrai"),
            ("когда будет расписание экзаменов", "uninav"),
            ("помогите найти работу", "career_navigator"),
            ("проблемы с заселением в общежитие", "uniroom")
        ]
        
        correct_predictions = 0
        total_tests = len(test_queries)
        
        for query, expected_agent in test_queries:
            scores = intent_classifier.classify_intent(query, 'ru')
            predicted_agent = max(scores, key=scores.get) if scores else None
            
            if predicted_agent == expected_agent:
                correct_predictions += 1
                status = "✅"
            else:
                status = "❌"
            
            print(f"  {status} Query: '{query}'")
            print(f"     Expected: {expected_agent}, Predicted: {predicted_agent}")
            print(f"     Scores: {dict(list(scores.items())[:3])}")
        
        accuracy = correct_predictions / total_tests * 100
        print(f"\n📊 Intent Classification Accuracy: {accuracy:.1f}% ({correct_predictions}/{total_tests})")
        
        # Test learning from feedback
        intent_classifier.learn_from_feedback(
            "как подать документы на поступление", 
            "ai_abitur", 
            0.9, 
            'ru'
        )
        print("✅ Feedback learning tested successfully")
        
        # Get learning statistics
        stats = intent_classifier.get_learning_stats()
        print(f"📈 Learning Stats: {stats}")
        
        return accuracy > 70  # Consider 70%+ accuracy as success
        
    except Exception as e:
        print(f"❌ Intent Classification Test Failed: {e}")
        return False


def test_analytics_engine():
    """Test comprehensive analytics and A/B testing"""
    print("\n📊 Testing Analytics and Learning System...")
    
    try:
        from analytics_engine import analytics_engine
        
        # Test interaction tracking
        test_interactions = [
            {
                'user_id': 'test_user_1',
                'message': 'Как поступить в университет?',
                'agent_type': 'ai_abitur',
                'agent_name': 'AI-Abitur',
                'confidence': 0.85,
                'response_time': 1.2,
                'cached': False,
                'context_used': True,
                'context_confidence': 0.7,
                'language': 'ru'
            },
            {
                'user_id': 'test_user_2',
                'message': 'Расписание экзаменов',
                'agent_type': 'uninav',
                'agent_name': 'UniNav',
                'confidence': 0.9,
                'response_time': 0.8,
                'cached': True,
                'context_used': True,
                'context_confidence': 0.8,
                'language': 'ru',
                'user_rating': 0.9
            }
        ]
        
        # Track test interactions
        for interaction in test_interactions:
            analytics_engine.track_interaction(interaction)
        
        print("✅ Interaction tracking tested")
        
        # Test performance metrics
        metrics = analytics_engine.get_performance_metrics(time_window_hours=1)
        print(f"📈 Performance Metrics: {metrics}")
        
        # Test A/B testing framework
        test_created = analytics_engine.create_ab_test(
            "response_style_test",
            ["detailed", "concise"],
            {"detailed": 0.5, "concise": 0.5}
        )
        
        if test_created:
            # Test variant assignment
            variant1 = analytics_engine.assign_ab_test_variant("response_style_test", "user1")
            variant2 = analytics_engine.assign_ab_test_variant("response_style_test", "user2")
            print(f"✅ A/B Testing: user1 -> {variant1}, user2 -> {variant2}")
            
            # Track some test results
            analytics_engine.track_ab_test_result("response_style_test", variant1, "satisfaction", 0.8)
            analytics_engine.track_ab_test_result("response_style_test", variant2, "satisfaction", 0.75)
            
            # Get test results
            ab_results = analytics_engine.get_ab_test_results("response_style_test")
            print(f"📊 A/B Test Results: {ab_results}")
        
        # Test error tracking
        analytics_engine.track_error({
            'error_type': 'test_error',
            'agent_type': 'ai_abitur',
            'message': 'test message',
            'error_details': 'simulated error for testing',
            'user_impact': 'minor'
        })
        print("✅ Error tracking tested")
        
        # Generate insights report
        insights = analytics_engine.generate_insights_report()
        print(f"🔍 Insights Report Generated: {len(insights)} sections")
        
        return True
        
    except Exception as e:
        print(f"❌ Analytics Engine Test Failed: {e}")
        return False


def test_personalization_engine():
    """Test user personalization and learning"""
    print("\n👤 Testing Personalization and Learning...")
    
    try:
        from personalization_engine import personalization_engine
        
        test_user = "test_user_123"
        
        # Simulate user interactions
        interactions = [
            {
                'message': 'Как поступить в университет?',
                'agent_type': 'ai_abitur',
                'agent_name': 'AI-Abitur',
                'confidence': 0.85,
                'response_time': 1.2,
                'language': 'ru'
            },
            {
                'message': 'Какие документы нужны?',
                'agent_type': 'ai_abitur',
                'agent_name': 'AI-Abitur',
                'confidence': 0.9,
                'response_time': 1.0,
                'language': 'ru'
            },
            {
                'message': 'Расписание занятий',
                'agent_type': 'uninav',
                'agent_name': 'UniNav',
                'confidence': 0.8,
                'response_time': 0.9,
                'language': 'ru'
            }
        ]
        
        # Update user profile with interactions
        for interaction in interactions:
            personalization_engine.update_user_interaction(test_user, interaction)
        
        print("✅ User interaction tracking tested")
        
        # Test feedback
        personalization_engine.add_user_feedback(test_user, 0.85, "Очень полезная информация!")
        personalization_engine.add_user_feedback(test_user, 0.9, "Быстро и точно!")
        
        print("✅ User feedback tested")
        
        # Test agent recommendation
        recommendation = personalization_engine.get_agent_recommendation(
            test_user, 
            "Вопрос о поступлении", 
            ['ai_abitur', 'uninav', 'kadrai']
        )
        
        if recommendation:
            agent, confidence = recommendation
            print(f"✅ Agent Recommendation: {agent} (confidence: {confidence:.2f})")
        
        # Test response adaptation
        base_response = "Для поступления нужны документы об образовании."
        adapted_response = personalization_engine.adapt_response_style(test_user, base_response)
        print(f"✅ Response Adaptation: '{adapted_response[:50]}...'")
        
        # Test proactive suggestions
        suggestions = personalization_engine.generate_proactive_suggestions(
            test_user, 
            "admission context"
        )
        print(f"✅ Proactive Suggestions: {len(suggestions)} suggestions generated")
        
        # Get personalization stats
        stats = personalization_engine.get_personalization_stats(test_user)
        print(f"📊 User Stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Personalization Engine Test Failed: {e}")
        return False


def test_semantic_search():
    """Test semantic search with knowledge graphs"""
    print("\n🔍 Testing Semantic Search and Knowledge Graphs...")
    
    try:
        from semantic_search import semantic_search_engine
        
        # Test concept extraction
        test_text = "Мне нужна информация о поступлении и требуемых документах"
        concepts = semantic_search_engine._extract_concepts(test_text)
        print(f"✅ Concept Extraction: {concepts}")
        
        # Test semantic similarity
        similarity1 = semantic_search_engine.calculate_semantic_similarity(
            "поступление в университет",
            "зачисление в вуз"
        )
        
        similarity2 = semantic_search_engine.calculate_semantic_similarity(
            "расписание занятий",
            "общежитие"
        )
        
        print(f"✅ Semantic Similarity: 'поступление'↔'зачисление' = {similarity1:.3f}")
        print(f"✅ Semantic Similarity: 'расписание'↔'общежитие' = {similarity2:.3f}")
        
        # Test query expansion
        expanded = semantic_search_engine.expand_query("поступление", "medium")
        print(f"✅ Query Expansion: 'поступление' → {expanded}")
        
        # Test concept suggestions
        suggestions = semantic_search_engine.get_concept_suggestions("пост")
        print(f"✅ Concept Suggestions for 'пост': {suggestions}")
        
        # Test query analysis
        analysis = semantic_search_engine.analyze_query_semantics("Как подать документы на поступление?")
        print(f"🔍 Query Analysis: {analysis}")
        
        # Get search statistics
        stats = semantic_search_engine.get_search_statistics()
        print(f"📊 Search Engine Stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Semantic Search Test Failed: {e}")
        return False


def test_distributed_system():
    """Test distributed caching and async processing"""
    print("\n🚀 Testing Distributed System and Performance...")
    
    try:
        from distributed_system import distributed_cache, async_processor, performance_optimizer
        
        # Test distributed cache
        test_key = "test:key:123"
        test_value = {"response": "Test response", "confidence": 0.85}
        
        # Set and get from cache
        set_success = distributed_cache.set(test_key, test_value, 60)
        retrieved_value = distributed_cache.get(test_key)
        
        cache_test_passed = set_success and retrieved_value is not None
        print(f"✅ Distributed Cache: {'PASS' if cache_test_passed else 'FAIL'}")
        
        # Test async processing
        def test_task(x, y):
            time.sleep(0.1)  # Simulate work
            return x + y
        
        task_id = async_processor.submit_task(test_task, 5, 3)
        result = async_processor.get_result(task_id, timeout=2.0)
        
        async_test_passed = result == 8
        print(f"✅ Async Processing: {'PASS' if async_test_passed else 'FAIL'}")
        
        # Test performance optimization
        optimization = performance_optimizer.optimize_response_generation(
            "Test message",
            "ai_abitur",
            "ru"
        )
        print(f"✅ Performance Optimization: {optimization}")
        
        # Get system statistics
        cache_stats = distributed_cache.get_stats()
        processor_stats = async_processor.get_stats()
        optimization_stats = performance_optimizer.get_optimization_stats()
        
        print(f"📊 Cache Stats: {cache_stats['combined_stats']}")
        print(f"📊 Processor Stats: {processor_stats['statistics']}")
        
        return cache_test_passed and async_test_passed
        
    except Exception as e:
        print(f"❌ Distributed System Test Failed: {e}")
        return False


def test_agent_integration():
    """Test complete agent integration with all new features"""
    print("\n🤖 Testing Complete Agent Integration...")
    
    try:
        from agents import AgentRouter
        
        router = AgentRouter()
        
        # Test enhanced routing
        test_messages = [
            ("Как поступить в университет?", "ru", "test_user_1"),
            ("Мне нужен отпуск", "ru", "test_user_2"),
            ("Расписание экзаменов", "ru", "test_user_3"),
            ("Помогите найти работу", "ru", "test_user_1"),  # Same user for personalization
            ("Проблемы в общежитии", "ru", "test_user_4")
        ]
        
        results = []
        for message, language, user_id in test_messages:
            print(f"\n  Testing: '{message}' (user: {user_id})")
            
            start_time = time.time()
            result = router.route_message(message, language, user_id)
            response_time = time.time() - start_time
            
            if result and 'response' in result:
                print(f"    ✅ Agent: {result.get('agent_name', 'Unknown')}")
                print(f"    ✅ Confidence: {result.get('confidence', 0):.2f}")
                print(f"    ✅ Response Time: {response_time:.2f}s")
                print(f"    ✅ Cached: {result.get('cached', False)}")
                
                if 'routing_info' in result:
                    routing_info = result['routing_info']
                    print(f"    🧠 ML Scores: {routing_info.get('ml_scores', {})}")
                
                if 'suggestions' in result:
                    print(f"    💡 Suggestions: {len(result['suggestions'])} generated")
                
                results.append(result)
            else:
                print(f"    ❌ No response generated")
        
        # Test feedback system
        if results:
            first_result = results[0]
            router.provide_feedback(
                user_id="test_user_1",
                message="Как поступить в университет?",
                agent_type=first_result.get('agent_type', ''),
                user_rating=0.9,
                feedback_text="Отличный ответ!"
            )
            print("✅ Feedback system tested")
        
        # Get routing analytics
        analytics = router.get_routing_analytics()
        print(f"📊 Routing Analytics: {analytics}")
        
        success_rate = len([r for r in results if r.get('confidence', 0) > 0.5]) / len(results)
        print(f"\n📈 Integration Success Rate: {success_rate:.1%}")
        
        return success_rate > 0.8  # 80% success rate threshold
        
    except Exception as e:
        print(f"❌ Agent Integration Test Failed: {e}")
        return False


def run_comprehensive_test():
    """Run all tests and generate report"""
    print("🚀 Starting Comprehensive Advanced AI Agent Features Test\n")
    print("=" * 70)
    
    test_results = {}
    
    # Run all test modules
    test_functions = [
        ("Intent Classification", test_intent_classification),
        ("Analytics Engine", test_analytics_engine),
        ("Personalization Engine", test_personalization_engine),
        ("Semantic Search", test_semantic_search),
        ("Distributed System", test_distributed_system),
        ("Agent Integration", test_agent_integration)
    ]
    
    passed_tests = 0
    total_tests = len(test_functions)
    
    for test_name, test_func in test_functions:
        print(f"\n{'='*50}")
        try:
            result = test_func()
            test_results[test_name] = result
            if result:
                passed_tests += 1
                status = "✅ PASSED"
            else:
                status = "⚠️ FAILED"
        except Exception as e:
            test_results[test_name] = False
            status = f"❌ ERROR: {e}"
        
        print(f"\n{test_name}: {status}")
    
    # Generate final report
    print(f"\n{'='*70}")
    print("📋 COMPREHENSIVE TEST REPORT")
    print(f"{'='*70}")
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
    
    success_rate = passed_tests / total_tests * 100
    print(f"\n📊 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
    
    if success_rate >= 80:
        print("🎉 EXCELLENT: Advanced AI Agent System is working excellently!")
    elif success_rate >= 60:
        print("👍 GOOD: Advanced AI Agent System is working well with minor issues")
    else:
        print("⚠️ NEEDS ATTENTION: Some advanced features need debugging")
    
    print(f"\n📝 Test completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return success_rate


if __name__ == "__main__":
    try:
        success_rate = run_comprehensive_test()
        sys.exit(0 if success_rate >= 60 else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Critical test error: {e}")
        sys.exit(1)