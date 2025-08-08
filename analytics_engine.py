"""
Analytics and Learning System
Система аналитики и обучения

This module provides comprehensive analytics, A/B testing capabilities,
and learning mechanisms for the AI agent system.
"""

import logging
import json
import time
from typing import Dict, List, Optional, Any
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import random
import statistics

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Comprehensive analytics and learning system"""
    
    def __init__(self):
        # Core metrics storage
        self.interaction_history = []
        self.agent_performance = defaultdict(list)
        self.user_satisfaction = defaultdict(list)
        self.response_times = defaultdict(list)
        self.error_tracking = defaultdict(list)
        
        # A/B testing framework
        self.ab_tests = {}
        self.test_assignments = {}
        
        # Learning metrics
        self.learning_progress = defaultdict(dict)
        self.quality_trends = defaultdict(list)
        
        # Performance benchmarks
        self.benchmarks = {
            'response_time_target': 2.0,  # seconds
            'satisfaction_target': 0.8,   # 80%
            'accuracy_target': 0.85,      # 85%
            'cache_hit_target': 0.3       # 30%
        }
        
    def track_interaction(self, interaction_data: Dict[str, Any]):
        """Track user interaction with comprehensive metrics"""
        interaction = {
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'user_id': interaction_data.get('user_id', 'anonymous'),
            'message': interaction_data.get('message', ''),
            'agent_type': interaction_data.get('agent_type'),
            'agent_name': interaction_data.get('agent_name'),
            'confidence': interaction_data.get('confidence', 0.0),
            'response_time': interaction_data.get('response_time', 0.0),
            'cached': interaction_data.get('cached', False),
            'context_used': interaction_data.get('context_used', False),
            'context_confidence': interaction_data.get('context_confidence', 0.0),
            'language': interaction_data.get('language', 'ru'),
            'user_rating': interaction_data.get('user_rating'),
            'session_id': interaction_data.get('session_id'),
            'ab_test': interaction_data.get('ab_test')
        }
        
        # Store interaction
        self.interaction_history.append(interaction)
        
        # Update agent performance metrics
        agent_type = interaction['agent_type']
        if agent_type:
            self.agent_performance[agent_type].append({
                'confidence': interaction['confidence'],
                'response_time': interaction['response_time'],
                'cached': interaction['cached'],
                'context_confidence': interaction['context_confidence'],
                'timestamp': interaction['timestamp']
            })
        
        # Track response times
        if interaction['response_time'] > 0:
            self.response_times[agent_type or 'unknown'].append(interaction['response_time'])
        
        # Track user satisfaction if provided
        if interaction['user_rating'] is not None:
            self.user_satisfaction[agent_type or 'unknown'].append(interaction['user_rating'])
        
        # Limit history size to prevent memory issues
        if len(self.interaction_history) > 10000:
            self.interaction_history = self.interaction_history[-8000:]  # Keep recent 8000
        
        logger.info(f"Tracked interaction: {agent_type} confidence={interaction['confidence']:.2f}")
    
    def track_error(self, error_data: Dict[str, Any]):
        """Track system errors for analysis"""
        error = {
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'error_type': error_data.get('error_type', 'unknown'),
            'agent_type': error_data.get('agent_type'),
            'message': error_data.get('message', ''),
            'error_details': error_data.get('error_details', ''),
            'user_impact': error_data.get('user_impact', 'unknown')
        }
        
        self.error_tracking[error['error_type']].append(error)
        logger.warning(f"Tracked error: {error['error_type']} for {error['agent_type']}")
    
    def get_performance_metrics(self, agent_type: Optional[str] = None, 
                              time_window_hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        cutoff_time = time.time() - (time_window_hours * 3600)
        
        # Filter interactions by time window
        recent_interactions = [
            i for i in self.interaction_history 
            if i['timestamp'] >= cutoff_time
        ]
        
        if agent_type:
            recent_interactions = [
                i for i in recent_interactions 
                if i['agent_type'] == agent_type
            ]
        
        if not recent_interactions:
            return {'error': 'No data available for the specified criteria'}
        
        # Calculate metrics
        total_interactions = len(recent_interactions)
        
        # Confidence metrics
        confidences = [i['confidence'] for i in recent_interactions if i['confidence'] > 0]
        avg_confidence = statistics.mean(confidences) if confidences else 0
        
        # Response time metrics
        response_times = [i['response_time'] for i in recent_interactions if i['response_time'] > 0]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        # Cache metrics
        cached_count = sum(1 for i in recent_interactions if i['cached'])
        cache_hit_rate = cached_count / total_interactions if total_interactions > 0 else 0
        
        # Context usage metrics
        context_used_count = sum(1 for i in recent_interactions if i['context_used'])
        context_usage_rate = context_used_count / total_interactions if total_interactions > 0 else 0
        
        # Context confidence metrics
        context_confidences = [i['context_confidence'] for i in recent_interactions if i['context_confidence'] > 0]
        avg_context_confidence = statistics.mean(context_confidences) if context_confidences else 0
        
        # User satisfaction metrics
        ratings = [i['user_rating'] for i in recent_interactions if i['user_rating'] is not None]
        avg_satisfaction = statistics.mean(ratings) if ratings else None
        satisfaction_count = len(ratings)
        
        # Error rate calculation
        recent_errors = [
            e for error_list in self.error_tracking.values() 
            for e in error_list 
            if e['timestamp'] >= cutoff_time
        ]
        error_rate = len(recent_errors) / total_interactions if total_interactions > 0 else 0
        
        # Agent distribution
        agent_distribution = Counter(i['agent_type'] for i in recent_interactions if i['agent_type'])
        
        # Language distribution
        language_distribution = Counter(i['language'] for i in recent_interactions)
        
        return {
            'time_window_hours': time_window_hours,
            'total_interactions': total_interactions,
            'performance': {
                'avg_confidence': round(avg_confidence, 3),
                'avg_response_time': round(avg_response_time, 3),
                'cache_hit_rate': round(cache_hit_rate, 3),
                'context_usage_rate': round(context_usage_rate, 3),
                'avg_context_confidence': round(avg_context_confidence, 3),
                'error_rate': round(error_rate, 3)
            },
            'user_satisfaction': {
                'avg_rating': round(avg_satisfaction, 3) if avg_satisfaction else None,
                'rating_count': satisfaction_count,
                'satisfaction_rate': round(avg_satisfaction, 3) if avg_satisfaction else None
            },
            'distributions': {
                'agents': dict(agent_distribution),
                'languages': dict(language_distribution)
            },
            'benchmarks': {
                'response_time_ok': avg_response_time <= self.benchmarks['response_time_target'],
                'satisfaction_ok': (avg_satisfaction or 0) >= self.benchmarks['satisfaction_target'],
                'cache_hit_ok': cache_hit_rate >= self.benchmarks['cache_hit_target']
            }
        }
    
    def create_ab_test(self, test_name: str, variants: List[str], 
                      traffic_split: Optional[Dict[str, float]] = None) -> bool:
        """Create a new A/B test"""
        if test_name in self.ab_tests:
            logger.warning(f"A/B test '{test_name}' already exists")
            return False
        
        # Default to equal split if not specified
        if traffic_split is None:
            split_ratio = 1.0 / len(variants)
            traffic_split = {variant: split_ratio for variant in variants}
        
        # Validate traffic split
        total_traffic = sum(traffic_split.values())
        if abs(total_traffic - 1.0) > 0.01:
            logger.error(f"Traffic split must sum to 1.0, got {total_traffic}")
            return False
        
        self.ab_tests[test_name] = {
            'variants': variants,
            'traffic_split': traffic_split,
            'created_at': time.time(),
            'active': True,
            'results': defaultdict(list)
        }
        
        logger.info(f"Created A/B test '{test_name}' with variants: {variants}")
        return True
    
    def assign_ab_test_variant(self, test_name: str, user_id: str) -> Optional[str]:
        """Assign user to A/B test variant"""
        if test_name not in self.ab_tests or not self.ab_tests[test_name]['active']:
            return None
        
        # Check if user already assigned
        assignment_key = f"{test_name}:{user_id}"
        if assignment_key in self.test_assignments:
            return self.test_assignments[assignment_key]
        
        # Assign based on traffic split
        test_config = self.ab_tests[test_name]
        variants = test_config['variants']
        traffic_split = test_config['traffic_split']
        
        # Use deterministic assignment based on user_id hash
        import hashlib
        hash_value = int(hashlib.md5(f"{test_name}:{user_id}".encode()).hexdigest()[:8], 16)
        random_value = (hash_value % 10000) / 10000.0  # 0.0 to 1.0
        
        # Assign variant based on cumulative traffic split
        cumulative = 0.0
        for variant, split in traffic_split.items():
            cumulative += split
            if random_value <= cumulative:
                self.test_assignments[assignment_key] = variant
                logger.debug(f"Assigned user {user_id} to variant '{variant}' in test '{test_name}'")
                return variant
        
        # Fallback to first variant
        variant = variants[0]
        self.test_assignments[assignment_key] = variant
        return variant
    
    def track_ab_test_result(self, test_name: str, variant: str, 
                           metric_name: str, metric_value: float):
        """Track A/B test result"""
        if test_name not in self.ab_tests:
            return
        
        result = {
            'variant': variant,
            'metric': metric_name,
            'value': metric_value,
            'timestamp': time.time()
        }
        
        self.ab_tests[test_name]['results'][variant].append(result)
        logger.debug(f"Tracked A/B test result: {test_name}/{variant} {metric_name}={metric_value}")
    
    def get_ab_test_results(self, test_name: str) -> Optional[Dict]:
        """Get A/B test results with statistical analysis"""
        if test_name not in self.ab_tests:
            return None
        
        test_data = self.ab_tests[test_name]
        results = test_data['results']
        
        # Aggregate results by variant
        variant_stats = {}
        for variant in test_data['variants']:
            variant_results = results.get(variant, [])
            if variant_results:
                # Group by metric
                metrics = defaultdict(list)
                for result in variant_results:
                    metrics[result['metric']].append(result['value'])
                
                # Calculate stats for each metric
                metric_stats = {}
                for metric, values in metrics.items():
                    metric_stats[metric] = {
                        'count': len(values),
                        'mean': statistics.mean(values),
                        'median': statistics.median(values),
                        'std_dev': statistics.stdev(values) if len(values) > 1 else 0
                    }
                
                variant_stats[variant] = metric_stats
            else:
                variant_stats[variant] = {}
        
        return {
            'test_name': test_name,
            'variants': test_data['variants'],
            'traffic_split': test_data['traffic_split'],
            'created_at': test_data['created_at'],
            'active': test_data['active'],
            'variant_stats': variant_stats,
            'total_results': sum(len(results.get(v, [])) for v in test_data['variants'])
        }
    
    def analyze_learning_progress(self, agent_type: str) -> Dict[str, Any]:
        """Analyze learning progress for an agent"""
        # Get recent performance data
        recent_performance = self.agent_performance.get(agent_type, [])
        if len(recent_performance) < 2:
            return {'error': 'Insufficient data for learning analysis'}
        
        # Sort by timestamp
        recent_performance.sort(key=lambda x: x['timestamp'])
        
        # Calculate trends over time
        time_windows = [7, 30, 90]  # days
        current_time = time.time()
        
        trends = {}
        for window in time_windows:
            cutoff = current_time - (window * 24 * 3600)
            window_data = [p for p in recent_performance if p['timestamp'] >= cutoff]
            
            if len(window_data) >= 2:
                confidences = [p['confidence'] for p in window_data]
                response_times = [p['response_time'] for p in window_data if p['response_time'] > 0]
                
                trends[f'{window}d'] = {
                    'interactions': len(window_data),
                    'avg_confidence': statistics.mean(confidences),
                    'confidence_trend': self._calculate_trend(confidences),
                    'avg_response_time': statistics.mean(response_times) if response_times else 0,
                    'response_time_trend': self._calculate_trend(response_times) if response_times else 0
                }
        
        # Calculate overall learning score
        learning_score = self._calculate_learning_score(agent_type, recent_performance)
        
        return {
            'agent_type': agent_type,
            'learning_score': learning_score,
            'trends': trends,
            'total_interactions': len(recent_performance),
            'improvement_areas': self._identify_improvement_areas(agent_type, recent_performance)
        }
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate simple trend (positive = improving, negative = declining)"""
        if len(values) < 2:
            return 0.0
        
        # Simple linear trend calculation
        n = len(values)
        x_vals = list(range(n))
        
        # Calculate slope
        x_mean = sum(x_vals) / n
        y_mean = sum(values) / n
        
        numerator = sum((x_vals[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x_vals[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        return slope
    
    def _calculate_learning_score(self, agent_type: str, performance_data: List[Dict]) -> float:
        """Calculate overall learning score for an agent"""
        if len(performance_data) < 10:
            return 0.5  # Neutral score for insufficient data
        
        # Recent vs historical performance comparison
        recent_size = min(len(performance_data) // 4, 50)  # Recent 25% or max 50 interactions
        recent_data = performance_data[-recent_size:]
        historical_data = performance_data[:-recent_size] if len(performance_data) > recent_size else []
        
        if not historical_data:
            return 0.5
        
        # Compare confidence improvements
        recent_confidence = statistics.mean(p['confidence'] for p in recent_data)
        historical_confidence = statistics.mean(p['confidence'] for p in historical_data)
        confidence_improvement = (recent_confidence - historical_confidence) / historical_confidence
        
        # Compare response time improvements (lower is better)
        recent_response_times = [p['response_time'] for p in recent_data if p['response_time'] > 0]
        historical_response_times = [p['response_time'] for p in historical_data if p['response_time'] > 0]
        
        response_time_improvement = 0
        if recent_response_times and historical_response_times:
            recent_avg_time = statistics.mean(recent_response_times)
            historical_avg_time = statistics.mean(historical_response_times)
            response_time_improvement = (historical_avg_time - recent_avg_time) / historical_avg_time
        
        # Combine improvements into learning score
        learning_score = 0.5 + (confidence_improvement * 0.3) + (response_time_improvement * 0.2)
        
        # Clamp to [0, 1] range
        return max(0.0, min(1.0, learning_score))
    
    def _identify_improvement_areas(self, agent_type: str, performance_data: List[Dict]) -> List[str]:
        """Identify areas where the agent needs improvement"""
        improvement_areas = []
        
        if not performance_data:
            return improvement_areas
        
        # Analyze recent performance
        recent_data = performance_data[-50:]  # Last 50 interactions
        
        # Check confidence levels
        confidences = [p['confidence'] for p in recent_data]
        avg_confidence = statistics.mean(confidences)
        if avg_confidence < 0.7:
            improvement_areas.append("Low confidence in responses")
        
        # Check response times
        response_times = [p['response_time'] for p in recent_data if p['response_time'] > 0]
        if response_times:
            avg_response_time = statistics.mean(response_times)
            if avg_response_time > self.benchmarks['response_time_target']:
                improvement_areas.append("Slow response times")
        
        # Check context utilization
        context_usage = sum(1 for p in recent_data if p.get('context_confidence', 0) > 0.5)
        context_usage_rate = context_usage / len(recent_data)
        if context_usage_rate < 0.3:
            improvement_areas.append("Low context utilization")
        
        # Check cache efficiency
        cache_usage = sum(1 for p in recent_data if p.get('cached', False))
        cache_rate = cache_usage / len(recent_data)
        if cache_rate < self.benchmarks['cache_hit_target']:
            improvement_areas.append("Low cache hit rate")
        
        return improvement_areas
    
    def generate_insights_report(self) -> Dict[str, Any]:
        """Generate comprehensive insights report"""
        # Get overall metrics
        overall_metrics = self.get_performance_metrics(time_window_hours=168)  # 1 week
        
        # Analyze each agent
        agent_insights = {}
        agent_types = set(i['agent_type'] for i in self.interaction_history if i['agent_type'])
        
        for agent_type in agent_types:
            agent_metrics = self.get_performance_metrics(agent_type, time_window_hours=168)
            learning_analysis = self.analyze_learning_progress(agent_type)
            
            agent_insights[agent_type] = {
                'metrics': agent_metrics,
                'learning': learning_analysis
            }
        
        # Get A/B test summaries
        ab_test_summaries = {}
        for test_name in self.ab_tests:
            ab_test_summaries[test_name] = self.get_ab_test_results(test_name)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(overall_metrics, agent_insights)
        
        return {
            'generated_at': datetime.now().isoformat(),
            'overall_metrics': overall_metrics,
            'agent_insights': agent_insights,
            'ab_tests': ab_test_summaries,
            'recommendations': recommendations,
            'system_health': self._assess_system_health(overall_metrics)
        }
    
    def _generate_recommendations(self, overall_metrics: Dict, agent_insights: Dict) -> List[str]:
        """Generate actionable recommendations based on analytics"""
        recommendations = []
        
        # Check overall performance
        performance = overall_metrics.get('performance', {})
        
        if performance.get('avg_response_time', 0) > self.benchmarks['response_time_target']:
            recommendations.append("Consider optimizing response times through better caching or async processing")
        
        if performance.get('cache_hit_rate', 0) < self.benchmarks['cache_hit_target']:
            recommendations.append("Improve caching strategy to reduce API calls and response times")
        
        if performance.get('avg_confidence', 0) < 0.7:
            recommendations.append("Enhance knowledge base content and search algorithms for better confidence")
        
        # Check individual agents
        for agent_type, insights in agent_insights.items():
            learning = insights.get('learning', {})
            improvement_areas = learning.get('improvement_areas', [])
            
            if improvement_areas:
                recommendations.append(f"Focus on {agent_type}: {', '.join(improvement_areas)}")
        
        # User satisfaction
        satisfaction = overall_metrics.get('user_satisfaction', {})
        avg_rating = satisfaction.get('avg_rating')
        if avg_rating and avg_rating < self.benchmarks['satisfaction_target']:
            recommendations.append("Collect more user feedback to understand satisfaction issues")
        
        return recommendations
    
    def _assess_system_health(self, metrics: Dict) -> str:
        """Assess overall system health"""
        performance = metrics.get('performance', {})
        benchmarks = metrics.get('benchmarks', {})
        
        healthy_metrics = sum(1 for status in benchmarks.values() if status)
        total_metrics = len(benchmarks)
        
        health_ratio = healthy_metrics / total_metrics if total_metrics > 0 else 0
        
        if health_ratio >= 0.8:
            return "Excellent"
        elif health_ratio >= 0.6:
            return "Good"
        elif health_ratio >= 0.4:
            return "Fair"
        else:
            return "Needs Attention"


# Global analytics instance
analytics_engine = AnalyticsEngine()