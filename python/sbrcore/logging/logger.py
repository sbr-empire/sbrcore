# ============================================================================
# Centralized Logging System
# ============================================================================

import logging
import sys
from typing import Optional
from datetime import datetime

class SBRFormatter(logging.Formatter):
    """Custom formatter for SBRCORE logs"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[92m',       # Green
        'WARNING': '\033[93m',    # Yellow
        'ERROR': '\033[91m',      # Red
        'CRITICAL': '\033[95m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_message = f"{log_color}[{timestamp}] [{record.levelname:8}] {record.name}: {record.getMessage()}{self.RESET}"
        
        if record.exc_info:
            log_message += f"\n{self.format_exception(record)}"
        
        return log_message

def setup_logging(level: str = 'INFO'):
    """Setup global logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('sbrcore.log')
        ]
    )

def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance"""
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(SBRFormatter())
        logger.addHandler(handler)
    
    return logger
