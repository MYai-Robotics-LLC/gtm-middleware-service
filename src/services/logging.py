import logging
from logging.handlers import RotatingFileHandler 
from typing import Optional, Literal
import os


def build_logger(name: str, file_name: Optional[str] = None, handlers: Optional[Literal['both', 'console', 'file']] = 'both') -> logging.Logger:
    logger = logging.getLogger(name)
    log_to_file = file_name or 'app.log'
    log_file_path = os.path.join('logs', log_to_file)
    
    
    if any(logger.handlers):
        return logger
    
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s')
    
    if not handlers or not handlers == 'file':
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        logger.addHandler(console)
    if not handlers or not handlers == 'console':
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        handler = RotatingFileHandler(log_file_path, maxBytes=1024*1024, backupCount=5)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger