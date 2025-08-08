#!/usr/bin/env python3
"""
Test script to debug agent knowledge base integration
"""

import logging
logging.basicConfig(level=logging.INFO)

def test_knowledge_base():
    """Test if agents can access their knowledge base"""
    print("Testing agent knowledge base integration...")
    
    # Test all agent types
    test_cases = [
        ("AIAbiturAgent", "поступление в университет"),
        ("KadrAIAgent", "отпуск сотрудника"),
        ("UniNavAgent", "расписание занятий"),
        ("CareerNavigatorAgent", "поиск работы"),
        ("UniRoomAgent", "общежитие заселение")
    ]
    
    results = []
    
    for agent_class, test_message in test_cases:
        try:
            # Import agent class dynamically
            from agents import AIAbiturAgent, KadrAIAgent, UniNavAgent, CareerNavigatorAgent, UniRoomAgent
            
            agent_map = {
                "AIAbiturAgent": AIAbiturAgent,
                "KadrAIAgent": KadrAIAgent,
                "UniNavAgent": UniNavAgent,
                "CareerNavigatorAgent": CareerNavigatorAgent,
                "UniRoomAgent": UniRoomAgent
            }
            
            agent_cls = agent_map[agent_class]
            agent = agent_cls()
            print(f"\n✓ Testing {agent.name} ({agent.agent_type})")
            
            # Test context retrieval
            context = agent.get_agent_context(test_message, 'ru')
            
            print(f"Query: '{test_message}'")
            print(f"Context length: {len(context)}")
            
            if context:
                print("✓ Agent returned context")
                print(f"Context preview: {context[:150]}...")
                results.append(True)
            else:
                print("✗ Agent returned empty context")
                results.append(False)
                
        except Exception as e:
            print(f"✗ Error testing {agent_class}: {e}")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n=== Test Summary ===")
    print(f"Success rate: {success_rate:.1f}% ({sum(results)}/{len(results)} agents working)")
    
    return all(results)

if __name__ == "__main__":
    success = test_knowledge_base()
    exit(0 if success else 1)