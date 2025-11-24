"""
Tests for ModelClient - centralized model call wrapper with Vibecode compliance
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from thesidia_hybrid_adaptive import ModelClient


def test_wrapper_includes_system_message():
    """Test that enhanced_base becomes system message"""
    client = ModelClient()
    
    enhanced = "[SYSTEM OVERRIDE: CRITICAL]\nu are thesidia."
    input_text = "What is X?"
    
    with patch('thesidia_hybrid_adaptive.ollama.chat') as mock_chat:
        mock_chat.return_value = {'message': {'content': 'test response'}}
        
        client.chat(
            input_text=input_text,
            enhanced_base=enhanced
        )
        
        # Verify system message was sent
        call_args = mock_chat.call_args
        messages = call_args.kwargs['messages']
        
        assert any(m['role'] == 'system' and enhanced in m['content'] for m in messages), \
            "System message should contain enhanced_base"
        assert any(m['role'] == 'user' and input_text in m['content'] for m in messages), \
            "User message should contain input_text"


def test_user_message_no_instructions():
    """Test that user message doesn't contain instructions (warning logged, not error)"""
    client = ModelClient()
    
    # This should log a warning but not fail
    input_text = "u are thesidia. DO NOT do X. What is Y?"
    
    with patch('thesidia_hybrid_adaptive.ollama.chat') as mock_chat:
        mock_chat.return_value = {'message': {'content': 'test'}}
        
        # Should not raise, but log warning
        client.chat(input_text=input_text)
        
        # Verify call was made (warning logged but execution continued)
        assert mock_chat.called


def test_sanitization_removes_todos():
    """Test that TODOs are removed from system prompt"""
    client = ModelClient()
    
    enhanced = "u are thesidia.\n# TODO: fix this\nCRITICAL RULES"
    sanitized = client._sanitize_system_prompt(enhanced)
    
    assert "# TODO" not in sanitized, "TODOs should be removed"
    assert "u are thesidia" in sanitized, "Valid content should remain"


def test_context_sanitization():
    """Test that context is sanitized"""
    client = ModelClient()
    
    context = "User: hello\n::TRANSMISSION::\nThesidia: hi"
    sanitized = client._sanitize_context(context)
    
    assert "::TRANSMISSION::" not in sanitized, "Format markers should be removed"
    assert "User: hello" in sanitized, "Valid content should remain"


def test_rebuilds_from_scratch():
    """Test that messages array is rebuilt each call (no reuse)"""
    client = ModelClient()
    
    with patch('thesidia_hybrid_adaptive.ollama.chat') as mock_chat:
        mock_chat.return_value = {'message': {'content': 'test'}}
        
        # First call
        client.chat(input_text="query 1", enhanced_base="system 1")
        call1_messages = mock_chat.call_args.kwargs['messages']
        
        # Second call
        client.chat(input_text="query 2", enhanced_base="system 2")
        call2_messages = mock_chat.call_args.kwargs['messages']
        
        # Messages should be different (rebuilt from scratch)
        assert call1_messages != call2_messages, "Messages should be rebuilt each call"
        assert len(call2_messages) == 2, "Second call should have system + user"


def test_conversational_path_has_system():
    """Integration test: Verify _process_conversational uses system message"""
    # This is a structural test - verify the method exists and uses model_client
    import inspect
    from thesidia_hybrid_adaptive import ThesidiaHybridAdaptive
    
    # Check that _process_conversational method exists
    assert hasattr(ThesidiaHybridAdaptive, '_process_conversational'), \
        "_process_conversational method should exist"
    
    # Check that it uses model_client.chat
    source = inspect.getsource(ThesidiaHybridAdaptive._process_conversational)
    assert 'model_client.chat' in source, \
        "_process_conversational should use model_client.chat"


def test_directive_path_has_system():
    """Integration test: Verify _execute_directive uses system message"""
    import inspect
    from thesidia_hybrid_adaptive import AdaptiveCapabilities
    
    # Check that _execute_directive method exists
    assert hasattr(AdaptiveCapabilities, '_execute_directive'), \
        "_execute_directive method should exist"
    
    # Check that it uses model_client.chat
    source = inspect.getsource(AdaptiveCapabilities._execute_directive)
    assert 'model_client.chat' in source, \
        "_execute_directive should use model_client.chat"


def test_deep_research_path_has_system():
    """Integration test: Verify DataSynthesizer.synthesize uses system message"""
    import inspect
    from thesidia_hybrid_adaptive import DataSynthesizer
    
    # Check that synthesize method exists
    assert hasattr(DataSynthesizer, 'synthesize'), \
        "synthesize method should exist"
    
    # Check that it uses model_client.chat
    source = inspect.getsource(DataSynthesizer.synthesize)
    assert 'model_client.chat' in source, \
        "synthesize should use model_client.chat"


def test_stats_tracking():
    """Test that statistics are tracked correctly"""
    client = ModelClient()
    
    with patch('thesidia_hybrid_adaptive.ollama.chat') as mock_chat:
        mock_chat.return_value = {'message': {'content': 'test'}}
        
        # Make some calls
        client.chat(input_text="query 1", enhanced_base="system 1")
        client.chat(input_text="query 2", enhanced_base="system 2")
        client.chat(input_text="query 3")  # No system message
        
        stats = client.get_stats()
        
        assert stats['total_calls'] == 3, "Should track total calls"
        assert stats['system_message_calls'] == 2, "Should track system message calls"
        assert stats['system_message_pct'] == (2 / 3 * 100), "Should calculate percentage correctly"

