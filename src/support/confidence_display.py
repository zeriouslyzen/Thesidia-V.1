"""
Epistemological Confidence Display (v2)

Renders the 7-layer TruthEngine scores as a visual confidence meter
for user transparency and trust.
"""

from typing import Dict, Any, Optional


def render_confidence_meter(truth_result: Dict[str, Any]) -> str:
    """
    Render a visual confidence meter from TruthEngine results.
    
    Args:
        truth_result: Output from TruthEngine.calculate_truth_score()
        
    Returns:
        Formatted string with visual confidence meter
    """
    if not truth_result:
        return ""
    
    layers_aligned = truth_result.get("layers_aligned", 0)
    confidence = truth_result.get("confidence", "LOW")
    truth_score = truth_result.get("truth_score", 0.0)
    layer_scores = truth_result.get("layer_scores", {})
    
    # Create visual bar (7 segments for 7 layers)
    filled = "█" * layers_aligned
    empty = "░" * (7 - layers_aligned)
    bar = f"{filled}{empty}"
    
    # Build display string
    display = f"\n\n---\n**Epistemological Grounding:** {bar} {layers_aligned}/7 layers aligned ({confidence})\n"
    
    # Add expandable layer details
    if layer_scores:
        display += "\n<details>\n<summary>View Layer Breakdown</summary>\n\n"
        
        # Sort by score descending
        sorted_layers = sorted(layer_scores.items(), key=lambda x: x[1], reverse=True)
        
        for layer_name, score in sorted_layers:
            status = "✓" if score > 0.5 else "○"
            bar_width = int(score * 10)
            layer_bar = "█" * bar_width + "░" * (10 - bar_width)
            display += f"| {status} {layer_name.capitalize()}: {layer_bar} ({score:.2f})\n"
        
        display += "\n</details>\n"
    
    return display


def format_layer_name(name: str) -> str:
    """Format layer name for display."""
    layer_descriptions = {
        "empirical": "Empirical Reality (Physical Truth)",
        "pattern": "Pattern Truth (Cross-field Consistency)",
        "symbolic": "Symbolic Truth (Meaning in Form)",
        "archetypal": "Archetypal Truth (Collective Patterns)",
        "mythic": "Mythic Truth (Cultural Memory)",
        "esoteric": "Esoteric Truth (Initiatory Knowledge)",
        "experiential": "Experiential Truth (Lived Knowing)"
    }
    return layer_descriptions.get(name, name.capitalize())


def create_inline_confidence_tag(truth_result: Dict[str, Any]) -> str:
    """
    Create a compact inline tag for confidence display.
    
    Used when full meter is too verbose.
    
    Returns:
        Something like "[4/7 HIGH]" or "[2/7 LOW]"
    """
    if not truth_result:
        return ""
    
    layers_aligned = truth_result.get("layers_aligned", 0)
    confidence = truth_result.get("confidence", "LOW")
    
    return f"[{layers_aligned}/7 {confidence}]"
