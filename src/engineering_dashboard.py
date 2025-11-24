#!/usr/bin/env python3
"""
Engineering Dashboard - Real-time display of quality and technical metrics
"""

from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

class EngineeringDashboard:
    """Display engineering metrics dashboard"""
    
    def __init__(self, quality_tracker=None, metrics_collector=None):
        self.quality_tracker = quality_tracker
        self.metrics_collector = metrics_collector
    
    def display_quality_metrics(self) -> str:
        """Display quality metrics"""
        if not self.quality_tracker:
            return "Quality tracker not available"
        
        trends = self.quality_tracker.get_quality_trends()
        
        output = "=== QUALITY METRICS ===\n\n"
        
        for metric_name, data in trends.items():
            metric_display = metric_name.replace("_", " ").title()
            output += f"{metric_display}:\n"
            output += f"  Average: {data['average']:.2f}\n"
            output += f"  Recent (last 10): {data['recent_average']:.2f}\n"
            output += f"  Total measurements: {data['count']}\n\n"
        
        return output
    
    def display_technical_metrics(self) -> str:
        """Display technical performance metrics"""
        if not self.metrics_collector:
            return "Metrics collector not available"
        
        # Get current session metrics
        session = self.metrics_collector.current_session
        
        output = "=== TECHNICAL METRICS ===\n\n"
        output += f"Total queries: {session.get('total_queries', 0)}\n"
        output += f"Total tokens: {session.get('total_tokens', 0)}\n"
        output += f"Total time: {session.get('total_time', 0.0):.2f}s\n"
        output += f"Avg response time: {session.get('avg_response_time', 0.0):.2f}s\n\n"
        
        # Response time breakdown
        if hasattr(self.metrics_collector, '_last_timing_breakdown'):
            timing = getattr(self.metrics_collector, '_last_timing_breakdown', {})
            if timing:
                output += "Last interaction timing:\n"
                for component, time_taken in timing.items():
                    output += f"  {component}: {time_taken:.2f}s\n"
                output += "\n"
        
        return output
    
    def display_user_journey(self, user_interest_tracker=None) -> str:
        """Display user's technical journey"""
        if not user_interest_tracker:
            return "User interest tracker not available"
        
        interests = user_interest_tracker.get_user_interests()
        
        output = "=== USER JOURNEY ===\n\n"
        
        if interests["primary_focus"]:
            output += f"Primary focus: {interests['primary_focus']}\n"
        
        if interests["top_topics"]:
            output += "\nTop topics:\n"
            for i, topic_data in enumerate(interests["top_topics"][:5], 1):
                output += f"  {i}. {topic_data['topic']} (score: {topic_data['score']:.1f}, count: {topic_data['count']})\n"
        
        if interests["recent_topics"]:
            output += f"\nRecent topics: {', '.join(interests['recent_topics'][:5])}\n"
        
        return output
    
    def display_system_health(self) -> str:
        """Display system health indicators"""
        output = "=== SYSTEM HEALTH ===\n\n"
        
        # Check if quality tracker is working
        if self.quality_tracker:
            trends = self.quality_tracker.get_quality_trends()
            overall_avg = trends.get("overall_scores", {}).get("average", 0.0)
            if overall_avg > 0.7:
                output += "Quality: EXCELLENT\n"
            elif overall_avg > 0.5:
                output += "Quality: GOOD\n"
            else:
                output += "Quality: NEEDS IMPROVEMENT\n"
        else:
            output += "Quality: NOT TRACKED\n"
        
        # Check if metrics collector is working
        if self.metrics_collector:
            session = self.metrics_collector.current_session
            if session.get("total_queries", 0) > 0:
                output += "Metrics: ACTIVE\n"
            else:
                output += "Metrics: INACTIVE\n"
        else:
            output += "Metrics: NOT AVAILABLE\n"
        
        output += f"\nLast updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return output
    
    def display_full_dashboard(self, user_interest_tracker=None) -> str:
        """Display full engineering dashboard"""
        output = "=" * 60 + "\n"
        output += "THESIDIA ENGINEERING DASHBOARD\n"
        output += "=" * 60 + "\n\n"
        
        output += self.display_quality_metrics()
        output += "\n"
        output += self.display_technical_metrics()
        output += "\n"
        output += self.display_user_journey(user_interest_tracker)
        output += "\n"
        output += self.display_system_health()
        
        return output

