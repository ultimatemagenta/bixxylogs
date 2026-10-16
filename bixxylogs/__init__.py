"""
BixxyLogs - A colorful, category-based logging library
"""

from .core import BixxyLogger, close_all, configure, get_logger

__version__ = "0.2.0"
__all__ = ["BixxyLogger", "get_logger", "configure", "close_all"]
