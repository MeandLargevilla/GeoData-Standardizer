"""GeoData-Standardizer package.

A Python tool for standardizing geophysical data formats.
"""

__version__ = '0.1.0'
__author__ = 'GeoData-Standardizer Contributors'

from .core.base_parser import BaseParser, ParserError, ValidationError, FileFormatError
from .core.dispatcher import Dispatcher

__all__ = [
    'BaseParser',
    'ParserError',
    'ValidationError',
    'FileFormatError',
    'Dispatcher',
]
