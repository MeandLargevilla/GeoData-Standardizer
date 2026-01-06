"""Logging utilities for GeoData-Standardizer."""

import logging
import logging.config
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = None,
    log_file: Optional[Path] = None,
    level: int = logging.INFO,
    console: bool = True
) -> logging.Logger:
    """Set up logger with console and file handlers.
    
    Args:
        name: Logger name. If None, returns root logger.
        log_file: Optional path to log file.
        level: Logging level.
        console: Whether to add console handler.
    
    Returns:
        Configured logger instance.
    
    Example:
        >>> logger = setup_logger('my_app', log_file=Path('app.log'))
        >>> logger.info('Application started')
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        # Ensure log directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always log DEBUG to file
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def setup_detailed_logger(
    name: str = None,
    log_file: Optional[Path] = None,
    level: int = logging.INFO
) -> logging.Logger:
    """Set up logger with detailed formatting including file and line number.
    
    Args:
        name: Logger name. If None, returns root logger.
        log_file: Optional path to log file.
        level: Logging level.
    
    Returns:
        Configured logger instance with detailed formatting.
    
    Example:
        >>> logger = setup_detailed_logger('debug_app')
        >>> logger.debug('Detailed debug message')
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create detailed formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - '
        '%(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """Get existing logger or create a basic one.
    
    Args:
        name: Logger name. If None, returns root logger.
    
    Returns:
        Logger instance.
    
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info('Using existing logger')
    """
    return logging.getLogger(name)


def set_log_level(logger: logging.Logger, level: int) -> None:
    """Set the log level for a logger and all its handlers.
    
    Args:
        logger: Logger instance.
        level: New logging level.
    
    Example:
        >>> logger = get_logger('my_app')
        >>> set_log_level(logger, logging.DEBUG)
    """
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


def disable_logging(logger_name: str = None) -> None:
    """Disable logging for a specific logger or all loggers.
    
    Args:
        logger_name: Name of logger to disable. If None, disables all.
    
    Example:
        >>> disable_logging('noisy_module')
    """
    if logger_name:
        logging.getLogger(logger_name).setLevel(logging.CRITICAL + 1)
    else:
        logging.disable(logging.CRITICAL)


def enable_logging() -> None:
    """Re-enable logging after it was disabled.
    
    Example:
        >>> enable_logging()
    """
    logging.disable(logging.NOTSET)
