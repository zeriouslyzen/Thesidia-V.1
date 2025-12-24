
import logging
from logging.handlers import RotatingFileHandler
import os
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Formats logs as JSON for easy ingestion by monitoring tools."""
    def format(self, record):
        log_obj = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
            "process": record.process,
            "thread": record.threadName
        }
        
        # Add extra fields if available
        if hasattr(record, 'response_time_ms'):
             log_obj['response_time_ms'] = record.response_time_ms
        if hasattr(record, 'status_code'):
             log_obj['status_code'] = record.status_code
        if hasattr(record, 'user_id'):
             log_obj['user_id'] = record.user_id
             
        return json.dumps(log_obj)

def setup_logger(name='katanx_server', log_file='server.json.log'):
    """
    Sets up a structured JSON logger with rotation.
    10MB per file, keeps last 5 backups.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers if setup logic is called multiple times
    if logger.handlers:
        return logger
        
    # File Handler - JSON formatted
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)
    
    file_handler = RotatingFileHandler(
        log_path, 
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    # Console Handler - Standard formatted for local dev visibility
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(console_handler)
    
    logger.info("Structured logging initialized")
    return logger

# Singleton instance
server_logger = setup_logger()
