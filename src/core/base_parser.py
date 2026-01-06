"""Base parser module for geophysical data standardization.

This module provides abstract base classes and utilities for parsing
various geophysical data formats.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple
import pandas as pd
import logging
from datetime import datetime


class ParserError(Exception):
    """Base exception for parser errors."""
    pass


class ValidationError(ParserError):
    """Exception raised when data validation fails."""
    pass


class FileFormatError(ParserError):
    """Exception raised when file format is invalid."""
    pass


class BaseParser(ABC):
    """Abstract base class for all geophysical data parsers.
    
    This class defines the interface and common functionality for parsing
    different types of geophysical data (electrical, seismic, radar, etc.).
    
    Attributes:
        file_path (Path): Path to the input file.
        metadata (dict): Metadata extracted from the file.
        data (pd.DataFrame): Parsed data in standardized format.
        raw_data (str): Raw file content before parsing.
        is_loaded (bool): Whether data has been loaded.
        is_parsed (bool): Whether data has been parsed.
        is_validated (bool): Whether data has been validated.
    
    Example:
        >>> class MyParser(BaseParser):
        ...     def load(self):
        ...         # Implementation
        ...         pass
        ...     def parse(self):
        ...         # Implementation
        ...         pass
        ...     def validate(self, data=None):
        ...         # Implementation
        ...         pass
        >>> parser = MyParser('data.txt')
        >>> parser.process()
    """
    
    def __init__(
        self,
        file_path: Union[str, Path],
        encoding: str = 'utf-8',
        **kwargs
    ):
        """Initialize the parser.
        
        Args:
            file_path: Path to the data file to parse.
            encoding: File encoding (default: 'utf-8').
            **kwargs: Additional parser-specific parameters.
        
        Raises:
            FileNotFoundError: If the file does not exist.
            ParserError: If file path validation fails.
        """
        self._file_path = Path(file_path)
        self._encoding = encoding
        self._metadata: Dict[str, Any] = {
            'file_name': self._file_path.name,
            'file_path': str(self._file_path),
            'created_at': datetime.now().isoformat(),
        }
        self._data: Optional[pd.DataFrame] = None
        self._raw_data: Optional[str] = None
        self._is_loaded = False
        self._is_parsed = False
        self._is_validated = False
        self._extra_params = kwargs
        
        # Set up logger
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Validate file path on initialization
        self._validate_file_path()
    
    @property
    def file_path(self) -> Path:
        """Get the file path."""
        return self._file_path
    
    @property
    def encoding(self) -> str:
        """Get the file encoding."""
        return self._encoding
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get metadata dictionary."""
        return self._metadata
    
    @property
    def data(self) -> Optional[pd.DataFrame]:
        """Get parsed data."""
        return self._data
    
    @property
    def raw_data(self) -> Optional[str]:
        """Get raw data."""
        return self._raw_data
    
    @property
    def is_loaded(self) -> bool:
        """Check if data has been loaded."""
        return self._is_loaded
    
    @property
    def is_parsed(self) -> bool:
        """Check if data has been parsed."""
        return self._is_parsed
    
    @property
    def is_validated(self) -> bool:
        """Check if data has been validated."""
        return self._is_validated
    
    def _validate_file_path(self) -> None:
        """Validate that the file path exists and is readable.
        
        Raises:
            FileNotFoundError: If file does not exist.
            PermissionError: If file is not readable.
        """
        if not self._file_path.exists():
            raise FileNotFoundError(f"File not found: {self._file_path}")
        
        if not self._file_path.is_file():
            raise ParserError(f"Path is not a file: {self._file_path}")
        
        if not self._file_path.stat().st_size > 0:
            raise ParserError(f"File is empty: {self._file_path}")
    
    def _check_required_columns(
        self,
        data: pd.DataFrame,
        required_columns: List[str]
    ) -> None:
        """Check if required columns exist in the data.
        
        Args:
            data: DataFrame to check.
            required_columns: List of required column names.
        
        Raises:
            ValidationError: If required columns are missing.
        """
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValidationError(
                f"Missing required columns: {', '.join(missing_columns)}"
            )
    
    def _check_value_ranges(
        self,
        data: pd.DataFrame,
        range_map: Dict[str, Tuple[float, float]]
    ) -> None:
        """Check if values are within expected ranges.
        
        Args:
            data: DataFrame to check.
            range_map: Dictionary mapping column names to (min, max) tuples.
        
        Raises:
            ValidationError: If values are out of range.
        """
        for column, (min_val, max_val) in range_map.items():
            if column not in data.columns:
                continue
            
            out_of_range = (
                (data[column] < min_val) | (data[column] > max_val)
            ).sum()
            
            if out_of_range > 0:
                raise ValidationError(
                    f"Column '{column}' has {out_of_range} values out of "
                    f"range [{min_val}, {max_val}]"
                )
    
    def _check_data_types(
        self,
        data: pd.DataFrame,
        type_map: Dict[str, type]
    ) -> None:
        """Check if columns have expected data types.
        
        Args:
            data: DataFrame to check.
            type_map: Dictionary mapping column names to expected types.
        
        Raises:
            ValidationError: If data types don't match.
        """
        for column, expected_type in type_map.items():
            if column not in data.columns:
                continue
            
            if expected_type == 'numeric':
                if not pd.api.types.is_numeric_dtype(data[column]):
                    raise ValidationError(
                        f"Column '{column}' must be numeric"
                    )
            elif expected_type == 'string':
                if not pd.api.types.is_string_dtype(data[column]):
                    raise ValidationError(
                        f"Column '{column}' must be string"
                    )
    
    def _standardize_column_names(
        self,
        data: pd.DataFrame,
        column_map: Dict[str, str]
    ) -> pd.DataFrame:
        """Standardize column names according to mapping.
        
        Args:
            data: DataFrame with columns to rename.
            column_map: Dictionary mapping old names to new names.
        
        Returns:
            DataFrame with standardized column names.
        """
        # Only rename columns that exist
        rename_dict = {
            old: new for old, new in column_map.items()
            if old in data.columns
        }
        return data.rename(columns=rename_dict)
    
    def _remove_duplicates(
        self,
        data: pd.DataFrame,
        subset: Optional[List[str]] = None,
        keep: str = 'first'
    ) -> pd.DataFrame:
        """Remove duplicate rows from data.
        
        Args:
            data: DataFrame to deduplicate.
            subset: Column names to consider for duplicates.
            keep: Which duplicates to keep ('first', 'last', False).
        
        Returns:
            DataFrame with duplicates removed.
        """
        initial_count = len(data)
        data = data.drop_duplicates(subset=subset, keep=keep)
        removed_count = initial_count - len(data)
        
        if removed_count > 0:
            self.logger.info(f"Removed {removed_count} duplicate rows")
        
        return data
    
    def _handle_missing_values(
        self,
        data: pd.DataFrame,
        strategy: str = 'drop',
        fill_value: Any = None
    ) -> pd.DataFrame:
        """Handle missing values in data.
        
        Args:
            data: DataFrame with potential missing values.
            strategy: How to handle missing values ('drop', 'fill', 'forward', 'backward').
            fill_value: Value to use when strategy is 'fill'.
        
        Returns:
            DataFrame with missing values handled.
        """
        if strategy == 'drop':
            data = data.dropna()
        elif strategy == 'fill':
            data = data.fillna(fill_value)
        elif strategy == 'forward':
            data = data.fillna(method='ffill')
        elif strategy == 'backward':
            data = data.fillna(method='bfill')
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        return data
    
    @abstractmethod
    def load(self) -> None:
        """Load data from file.
        
        This method should read the file and populate self._raw_data.
        It should also set self._is_loaded to True on success.
        
        Raises:
            ParserError: If loading fails.
        """
        pass
    
    @abstractmethod
    def parse(self) -> Dict[str, Any]:
        """Parse the loaded data.
        
        This method should convert raw data into a standardized DataFrame
        and populate self._data and self._metadata.
        It should also set self._is_parsed to True on success.
        
        Returns:
            Dictionary containing 'metadata' and 'data' keys.
        
        Raises:
            ParserError: If parsing fails.
        """
        pass
    
    @abstractmethod
    def validate(self, data: Optional[pd.DataFrame] = None) -> bool:
        """Validate the parsed data.
        
        This method should check data integrity, required fields,
        value ranges, etc. It should set self._is_validated to True
        on success.
        
        Args:
            data: DataFrame to validate. If None, uses self.data.
        
        Returns:
            True if validation passes.
        
        Raises:
            ValidationError: If validation fails.
        """
        pass
    
    def process(self, skip_validation: bool = False) -> Dict[str, Any]:
        """Run the complete parsing pipeline.
        
        This is a convenience method that runs load(), parse(), and
        optionally validate() in sequence.
        
        Args:
            skip_validation: If True, skip the validation step.
        
        Returns:
            Dictionary containing 'metadata' and 'data' keys.
        
        Raises:
            ParserError: If any step fails.
        """
        self.logger.info(f"Processing {self.file_path.name}")
        
        # Load
        if not self.is_loaded:
            self.load()
        
        # Parse
        if not self.is_parsed:
            result = self.parse()
        else:
            result = {'metadata': self.metadata, 'data': self.data}
        
        # Validate
        if not skip_validation and not self.is_validated:
            self.validate()
        
        self.logger.info(f"Successfully processed {self.file_path.name}")
        return result
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the parsed data.
        
        Returns:
            Dictionary with summary statistics.
        """
        summary = {
            'file_name': self.file_path.name,
            'is_loaded': self.is_loaded,
            'is_parsed': self.is_parsed,
            'is_validated': self.is_validated,
        }
        
        if self.data is not None:
            summary.update({
                'row_count': len(self.data),
                'column_count': len(self.data.columns),
                'columns': list(self.data.columns),
                'memory_usage_mb': self.data.memory_usage(deep=True).sum() / 1024**2,
            })
        
        if self.metadata:
            summary['metadata'] = self.metadata
        
        return summary
    
    def save_data(
        self,
        output_path: Union[str, Path],
        format: str = 'csv',
        **kwargs
    ) -> None:
        """Save parsed data to file.
        
        Args:
            output_path: Path where to save the data.
            format: Output format ('csv', 'json', 'excel', 'parquet').
            **kwargs: Additional arguments passed to pandas save method.
        
        Raises:
            ParserError: If data hasn't been parsed or save fails.
        """
        if self.data is None:
            raise ParserError("No data to save. Run parse() first.")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if format == 'csv':
                self.data.to_csv(output_path, index=False, **kwargs)
            elif format == 'json':
                self.data.to_json(output_path, orient='records', indent=2, **kwargs)
            elif format == 'excel':
                self.data.to_excel(output_path, index=False, **kwargs)
            elif format == 'parquet':
                self.data.to_parquet(output_path, index=False, **kwargs)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            self.logger.info(f"Saved data to {output_path}")
        except Exception as e:
            raise ParserError(f"Failed to save data: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert parser state to dictionary.
        
        Returns:
            Dictionary representation of the parser.
        """
        return {
            'file_path': str(self.file_path),
            'encoding': self.encoding,
            'metadata': self.metadata,
            'is_loaded': self.is_loaded,
            'is_parsed': self.is_parsed,
            'is_validated': self.is_validated,
            'data_shape': self.data.shape if self.data is not None else None,
        }
    
    def __repr__(self) -> str:
        """String representation of parser."""
        return (
            f"{self.__class__.__name__}("
            f"file_path='{self.file_path.name}', "
            f"loaded={self.is_loaded}, "
            f"parsed={self.is_parsed}, "
            f"validated={self.is_validated})"
        )
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        return f"{self.__class__.__name__} for {self.file_path.name}"
