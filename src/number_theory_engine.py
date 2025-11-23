#!/usr/bin/env python3
"""
Number Theory Engine - Fibonacci, golden ratio, sacred geometry, numerical patterns
Pattern recognition, not mystical
"""

from typing import Dict, List, Optional, Any
import math


class NumberTheoryEngine:
    """
    Number theory engine for pattern recognition in numbers.
    Fibonacci, golden ratio, sacred geometry, numerical patterns.
    """
    
    def __init__(self):
        self.golden_ratio = (1 + math.sqrt(5)) / 2  # φ (phi)
        self.fibonacci_sequence = self._generate_fibonacci(100)
        
    def _generate_fibonacci(self, n: int) -> List[int]:
        """Generate Fibonacci sequence up to n terms."""
        if n <= 0:
            return []
        if n == 1:
            return [0]
        if n == 2:
            return [0, 1]
        
        fib = [0, 1]
        for i in range(2, n):
            fib.append(fib[i-1] + fib[i-2])
        return fib
    
    def detect_fibonacci_pattern(self, numbers: List[float], tolerance: float = 0.01) -> Optional[Dict[str, Any]]:
        """
        Detect if numbers follow Fibonacci pattern.
        Returns pattern info or None.
        """
        if len(numbers) < 3:
            return None
        
        # Check if ratios approximate golden ratio
        ratios = []
        for i in range(len(numbers) - 1):
            if numbers[i] != 0:
                ratio = numbers[i+1] / numbers[i]
                ratios.append(ratio)
        
        # Check if ratios are close to golden ratio
        golden_ratios = [abs(r - self.golden_ratio) < tolerance for r in ratios]
        
        if sum(golden_ratios) >= len(ratios) * 0.7:  # 70% match
            return {
                "pattern": "fibonacci",
                "golden_ratio": self.golden_ratio,
                "ratios": ratios,
                "confidence": sum(golden_ratios) / len(ratios) if ratios else 0
            }
        
        return None
    
    def detect_golden_ratio(self, a: float, b: float, tolerance: float = 0.01) -> bool:
        """
        Detect if two numbers are in golden ratio.
        Returns True if (a+b)/a ≈ a/b ≈ φ
        """
        if b == 0:
            return False
        
        ratio1 = a / b
        ratio2 = (a + b) / a if a != 0 else 0
        
        return (abs(ratio1 - self.golden_ratio) < tolerance or 
                abs(ratio2 - self.golden_ratio) < tolerance)
    
    def analyze_numerical_pattern(self, numbers: List[float]) -> Dict[str, Any]:
        """
        Analyze numerical pattern in given numbers.
        Returns pattern analysis.
        """
        analysis = {
            "fibonacci": self.detect_fibonacci_pattern(numbers),
            "golden_ratio_detected": False,
            "patterns": []
        }
        
        # Check for golden ratio in pairs
        for i in range(len(numbers) - 1):
            if self.detect_golden_ratio(numbers[i], numbers[i+1]):
                analysis["golden_ratio_detected"] = True
                analysis["patterns"].append(f"Golden ratio detected between positions {i} and {i+1}")
        
        return analysis
    
    def generate_number_theory_prompt(self, query: str, analysis: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate number theory prompt if relevant.
        """
        prompt_parts = [
            "[NUMBER THEORY ANALYSIS]",
            "",
            "You are analyzing numerical patterns. Consider:",
            "",
            "- Fibonacci sequence and golden ratio patterns",
            "- Sacred geometry and geometric proportions",
            "- Numerical sequences and patterns in nature",
            "- Mathematical constants and their relationships",
            "",
            "APPROACH:",
            "- Pattern recognition, NOT mystical causation",
            "- Scientific analysis of numerical relationships",
            "- Cross-domain connections (numbers in nature, architecture, biology)",
            "",
            "Be precise and scientific - show the mathematical relationships."
        ]
        
        if analysis and analysis.get("fibonacci"):
            prompt_parts.append(f"\nDetected Fibonacci pattern with confidence: {analysis['fibonacci']['confidence']:.2%}")
        
        if analysis and analysis.get("golden_ratio_detected"):
            prompt_parts.append("\nGolden ratio detected in the data.")
        
        return "\n".join(prompt_parts)

