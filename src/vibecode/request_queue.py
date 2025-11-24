#!/usr/bin/env python3
"""
Request Queue System - Vibecode Compliance
===========================================

Fixes race condition: UI sends multiple requests in parallel,
backend processes out of order.

Solution: Sequential request processing with queue.
"""

from __future__ import annotations

import asyncio
from queue import Queue
from typing import Any, Dict, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class RequestQueue:
    """
    Sequential request queue to prevent race conditions.
    
    Ensures requests are processed in order, even when
    multiple requests arrive simultaneously.
    """
    
    def __init__(self):
        self.queue: Queue = Queue()
        self.processing: bool = False
        self.request_ids: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
    
    async def enqueue(
        self, 
        request_id: str, 
        request: Dict[str, Any],
        processor: Callable[[Dict[str, Any]], Any]
    ) -> Any:
        """
        Add request to queue and process sequentially.
        
        Args:
            request_id: Unique identifier for the request
            request: Request data dictionary
            processor: Async function to process the request
            
        Returns:
            Result from processor function
        """
        # Create future for this request
        future = asyncio.Future()
        self.request_ids[request_id] = future
        
        # Add to queue
        self.queue.put((request_id, request, processor, future))
        
        # Start processing if not already running
        asyncio.create_task(self._process_queue())
        
        # Wait for result
        return await future
    
    async def _process_queue(self):
        """Process queue sequentially."""
        async with self._lock:
            if self.processing:
                return
            self.processing = True
        
        try:
            while not self.queue.empty():
                try:
                    request_id, request, processor, future = self.queue.get_nowait()
                    
                    try:
                        # Process request
                        result = await processor(request)
                        future.set_result(result)
                    except Exception as e:
                        logger.error(f"Error processing request {request_id}: {e}")
                        future.set_exception(e)
                    finally:
                        # Clean up
                        if request_id in self.request_ids:
                            del self.request_ids[request_id]
                
                except asyncio.QueueEmpty:
                    break
        finally:
            self.processing = False
    
    def get_queue_size(self) -> int:
        """Get current queue size."""
        return self.queue.qsize()
    
    def is_processing(self) -> bool:
        """Check if queue is currently processing."""
        return self.processing


# Global instance (singleton pattern)
_request_queue: Optional[RequestQueue] = None


def get_request_queue() -> RequestQueue:
    """Get global request queue instance."""
    global _request_queue
    if _request_queue is None:
        _request_queue = RequestQueue()
    return _request_queue

