"""
Logging configuration for the evaluation module.
"""

import logging
import os
from evaluation.config.settings import LOG_FILE

def setup_logging():
    """
    Configure logging for the evaluation module.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("hallucination_evaluator")
