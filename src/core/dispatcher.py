"""Dispatcher module to route data to appropriate parser based on file type."""

from pathlib import Path
from typing import Union, Type
import logging

from .base_parser import BaseParser, ParserError
from ..parsers.elec_parser import ElecParser
from ..parsers.seismic_parser import SeismicParser
from ..parsers.radar_parser import RadarParser


class Dispatcher:
    """Routes input files to the appropriate parser based on data type.
    
    The Dispatcher acts as a factory for creating parser instances based on
    either explicit data type specification or automatic file extension detection.
    
    Example:
        >>> dispatcher = Dispatcher()
        >>> parser = dispatcher.get_parser('electrical', 'data.csv')
        >>> parser.process()
        
        >>> # Auto-detect type
        >>> data_type = dispatcher.detect_type('data.sgy')
        >>> parser = dispatcher.get_parser(data_type, 'data.sgy')
    """
    
    def __init__(self):
        """Initialize the dispatcher with parser mappings."""
        self.logger = logging.getLogger(__name__)
        self._parser_map = {
            'electrical': ElecParser,
            'seismic': SeismicParser,
            'radar': RadarParser,
        }
    
    def get_parser(
        self,
        data_type: str,
        file_path: Union[str, Path] = None,
        **kwargs
    ) -> Union[BaseParser, Type[BaseParser]]:
        """Get appropriate parser for the data type.
        
        Args:
            data_type: Type of geophysical data ('electrical', 'seismic', 'radar').
            file_path: Optional path to the data file.
            **kwargs: Additional arguments passed to parser constructor.
        
        Returns:
            Parser instance if file_path is provided, otherwise parser class.
        
        Raises:
            ParserError: If data_type is unknown.
        
        Example:
            >>> dispatcher = Dispatcher()
            >>> parser = dispatcher.get_parser('electrical', 'data.csv')
            >>> # or get just the class
            >>> ParserClass = dispatcher.get_parser('electrical')
        """
        data_type_lower = data_type.lower()
        
        if data_type_lower not in self._parser_map:
            available_types = ', '.join(self._parser_map.keys())
            raise ParserError(
                f"Unknown data type: '{data_type}'. "
                f"Available types: {available_types}"
            )
        
        parser_class = self._parser_map[data_type_lower]
        
        if file_path:
            self.logger.info(f"Creating {data_type} parser for {file_path}")
            return parser_class(file_path, **kwargs)
        
        return parser_class
    
    def detect_type(self, file_path: Union[str, Path]) -> str:
        """Auto-detect data type from file extension.
        
        Args:
            file_path: Path to the data file.
        
        Returns:
            Detected data type string.
        
        Raises:
            ParserError: If file type cannot be detected.
        
        Example:
            >>> dispatcher = Dispatcher()
            >>> data_type = dispatcher.detect_type('survey.sgy')
            >>> print(data_type)  # 'seismic'
        """
        file_path = Path(file_path)
        ext = file_path.suffix.lower()
        
        # Extension to data type mapping
        extension_map = {
            '.dat': 'electrical',
            '.txt': 'electrical',
            '.csv': 'electrical',
            '.sgy': 'seismic',
            '.segy': 'seismic',
            '.dzt': 'radar',
            '.rd3': 'radar',
        }
        
        if ext in extension_map:
            detected_type = extension_map[ext]
            self.logger.info(
                f"Detected data type '{detected_type}' from extension '{ext}'"
            )
            return detected_type
        
        raise ParserError(
            f"Cannot detect data type from extension: '{ext}'. "
            f"Supported extensions: {', '.join(extension_map.keys())}"
        )
    
    def get_supported_types(self) -> list:
        """Get list of supported data types.
        
        Returns:
            List of supported data type strings.
        """
        return list(self._parser_map.keys())
    
    def register_parser(self, data_type: str, parser_class: Type[BaseParser]) -> None:
        """Register a new parser type.
        
        This allows extending the dispatcher with custom parsers.
        
        Args:
            data_type: Name for the data type.
            parser_class: Parser class (must inherit from BaseParser).
        
        Raises:
            TypeError: If parser_class doesn't inherit from BaseParser.
        
        Example:
            >>> class CustomParser(BaseParser):
            ...     pass
            >>> dispatcher = Dispatcher()
            >>> dispatcher.register_parser('custom', CustomParser)
        """
        if not issubclass(parser_class, BaseParser):
            raise TypeError(
                f"Parser class must inherit from BaseParser, "
                f"got {parser_class.__name__}"
            )
        
        self._parser_map[data_type.lower()] = parser_class
        self.logger.info(f"Registered parser '{parser_class.__name__}' for type '{data_type}'")
