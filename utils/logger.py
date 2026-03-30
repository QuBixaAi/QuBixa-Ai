import logging
import os
import sys
from datetime import datetime

class QubixaLogger:
    def __init__(self, log_file=None, level=logging.INFO):
        self.logger = logging.getLogger("QubixaAI")
        self.logger.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File Handler
        if log_file:
            log_dir = os.path.dirname(log_file)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger

# Global logger instance
log_path = os.getenv("LOG_FILE", "./logs/qubixa.log")
logger_instance = QubixaLogger(log_file=log_path).get_logger()
