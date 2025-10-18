"""
Logging Configuration for Financial Intelligence System
Provides centralized logging setup with file and console handlers
"""
import logging
import os
from datetime import datetime
from config.settings import Config

def setup_logging():
    """
    Configure application logging

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

    # Create logger
    logger = logging.getLogger('financial_intelligence')
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))

    # Remove existing handlers
    logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)

    # File handler with daily rotation
    log_file = f"logs/app_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Log startup message
    logger.info("="*60)
    logger.info("Financial Intelligence System - Logging Initialized")
    logger.info(f"Log Level: {Config.LOG_LEVEL}")
    logger.info(f"Log File: {log_file}")
    logger.info("="*60)

    return logger
