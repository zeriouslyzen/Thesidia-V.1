#!/usr/bin/env python3
"""
Event System - Event-driven messaging between components
Provides event routing, async processing, and event handlers
"""

from typing import Dict, List, Callable, Any, Optional
from datetime import datetime
import threading
from queue import Queue, Empty
from collections import defaultdict
import asyncio


class Event:
    """Represents an event in the system"""
    
    def __init__(
        self,
        event_type: str,
        data: Dict[str, Any],
        source: Optional[str] = None,
        target: Optional[str] = None
    ):
        """
        Initialize event.
        
        Args:
            event_type: Type of event
            data: Event data dictionary
            source: Source component/agent ID
            target: Target component/agent ID (None for broadcast)
        """
        self.event_type = event_type
        self.data = data
        self.source = source
        self.target = target
        self.timestamp = datetime.now()
        self.handled = False
    
    def __repr__(self):
        return f"Event(type={self.event_type}, source={self.source}, target={self.target})"


class EventSystem:
    """
    Central event system for component communication.
    
    Provides:
    - Event emission and routing
    - Event listener registration
    - Async event processing
    - Event filtering and routing
    """
    
    def __init__(self, async_processing: bool = True):
        """
        Initialize event system.
        
        Args:
            async_processing: Whether to process events asynchronously
        """
        self._listeners: Dict[str, List[Callable]] = defaultdict(list)
        self._global_listeners: List[Callable] = []
        self._event_queue: Queue = Queue()
        self._async_processing = async_processing
        self._processing_thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()
        
        if async_processing:
            self._start_processing_thread()
    
    def _start_processing_thread(self):
        """Start background thread for async event processing."""
        self._running = True
        self._processing_thread = threading.Thread(
            target=self._process_event_queue,
            daemon=True
        )
        self._processing_thread.start()
    
    def _process_event_queue(self):
        """Process events from queue (runs in background thread)."""
        while self._running:
            try:
                event = self._event_queue.get(timeout=1.0)
                self._handle_event(event)
                self._event_queue.task_done()
            except Empty:
                continue
            except Exception as e:
                print(f"Error processing event: {e}")
    
    def register_listener(self, event_type: str, handler: Callable[[Event], None]):
        """
        Register an event listener for a specific event type.
        
        Args:
            event_type: Type of event to listen for
            handler: Handler function that takes an Event
        """
        with self._lock:
            self._listeners[event_type].append(handler)
    
    def register_global_listener(self, handler: Callable[[Event], None]):
        """
        Register a global listener for all events.
        
        Args:
            handler: Handler function that takes an Event
        """
        with self._lock:
            self._global_listeners.append(handler)
    
    def unregister_listener(self, event_type: str, handler: Callable[[Event], None]):
        """
        Unregister an event listener.
        
        Args:
            event_type: Event type
            handler: Handler to remove
        """
        with self._lock:
            if event_type in self._listeners:
                if handler in self._listeners[event_type]:
                    self._listeners[event_type].remove(handler)
    
    def emit(
        self,
        event_type: str,
        data: Dict[str, Any],
        source: Optional[str] = None,
        target: Optional[str] = None,
        async_processing: Optional[bool] = None
    ):
        """
        Emit an event.
        
        Args:
            event_type: Type of event
            data: Event data
            source: Source component ID
            target: Target component ID (None for broadcast)
            async_processing: Override default async processing
        """
        event = Event(event_type, data, source, target)
        
        use_async = async_processing if async_processing is not None else self._async_processing
        
        if use_async:
            self._event_queue.put(event)
        else:
            self._handle_event(event)
    
    def _handle_event(self, event: Event):
        """
        Handle an event by calling registered listeners.
        
        Args:
            event: Event to handle
        """
        # Call global listeners first
        for handler in self._global_listeners:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in global listener: {e}")
        
        # Call type-specific listeners
        listeners = self._listeners.get(event.event_type, [])
        for handler in listeners:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in event listener for {event.event_type}: {e}")
        
        event.handled = True
    
    def wait_for_event(
        self,
        event_type: str,
        timeout: Optional[float] = None,
        condition: Optional[Callable[[Event], bool]] = None
    ) -> Optional[Event]:
        """
        Wait for a specific event to occur.
        
        Args:
            event_type: Type of event to wait for
            timeout: Timeout in seconds (None for no timeout)
            condition: Optional condition function to check event
            
        Returns:
            Event if received, None if timeout
        """
        received_event = None
        event_received = threading.Event()
        
        def handler(event: Event):
            nonlocal received_event
            if condition is None or condition(event):
                received_event = event
                event_received.set()
        
        self.register_listener(event_type, handler)
        
        try:
            if event_received.wait(timeout=timeout):
                return received_event
            return None
        finally:
            self.unregister_listener(event_type, handler)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get event system statistics.
        
        Returns:
            Dictionary with stats
        """
        with self._lock:
            return {
                "total_listeners": sum(len(handlers) for handlers in self._listeners.values()),
                "global_listeners": len(self._global_listeners),
                "event_types": list(self._listeners.keys()),
                "queue_size": self._event_queue.qsize(),
                "async_processing": self._async_processing
            }
    
    def shutdown(self):
        """Shutdown event system and stop processing thread."""
        self._running = False
        if self._processing_thread:
            self._processing_thread.join(timeout=5.0)


# Global event system instance
_global_event_system: Optional[EventSystem] = None


def get_event_system() -> EventSystem:
    """
    Get the global event system instance.
    
    Returns:
        Global EventSystem instance
    """
    global _global_event_system
    if _global_event_system is None:
        _global_event_system = EventSystem()
    return _global_event_system


def set_event_system(event_system: EventSystem):
    """
    Set the global event system instance.
    
    Args:
        event_system: EventSystem instance to use globally
    """
    global _global_event_system
    _global_event_system = event_system

