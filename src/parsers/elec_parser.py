"""Parser for electrical resistivity data."""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
from io import StringIO
import logging

from ..core.base_parser import BaseParser, ParserError, ValidationError


class ElecParser(BaseParser):
    """Parser for electrical resistivity survey data.
    
    This parser handles electrical resistivity data from various instruments,
    standardizing the format for further processing.
    
    Expected columns (after standardization):
        - station_id: Station identifier
        - depth_m: Depth in meters
        - resistivity_ohm_m: Resistivity in ohm-meters
        - current_ma: Current in milliamps (optional)
        - voltage_mv: Voltage in millivolts (optional)
    
    Example:
        >>> parser = ElecParser('electrical_data.csv')
        >>> result = parser.process()
        >>> df = result['data']
    """
    
    def load(self) -> None:
        """Load electrical data from file.
        
        Raises:
            ParserError: If file cannot be loaded.
        """
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                self._raw_data = f.read()
            self._is_loaded = True
            self.logger.info(f"Loaded {self.file_path.name} ({len(self._raw_data)} bytes)")
        except Exception as e:
            raise ParserError(f"Failed to load file: {e}")
    
    def parse(self) -> Dict[str, Any]:
        """Parse electrical resistivity data.
        
        Returns:
            Dictionary with 'metadata' and 'data' keys.
        
        Raises:
            ParserError: If parsing fails.
        """
        if not self.is_loaded:
            raise ParserError("Data must be loaded first. Call load() before parse().")
        
        try:
            # Try to read as CSV
            df = pd.read_csv(StringIO(self._raw_data))
            
            # Standardize column names (case-insensitive mapping)
            column_map = {
                'station': 'station_id',
                'Station': 'station_id',
                'STATION': 'station_id',
                'depth': 'depth_m',
                'Depth': 'depth_m',
                'DEPTH': 'depth_m',
                'depth_m': 'depth_m',
                'resistance': 'resistivity_ohm_m',
                'resistivity': 'resistivity_ohm_m',
                'Resistivity': 'resistivity_ohm_m',
                'RESISTIVITY': 'resistivity_ohm_m',
                'current': 'current_ma',
                'Current': 'current_ma',
                'voltage': 'voltage_mv',
                'Voltage': 'voltage_mv',
            }
            df = self._standardize_column_names(df, column_map)
            
            # Update metadata
            self.metadata.update({
                'data_type': 'electrical_resistivity',
                'record_count': len(df),
                'stations': df['station_id'].nunique() if 'station_id' in df else 0,
                'depth_range_m': (
                    df['depth_m'].min(), df['depth_m'].max()
                ) if 'depth_m' in df else None,
                'resistivity_range_ohm_m': (
                    df['resistivity_ohm_m'].min(), df['resistivity_ohm_m'].max()
                ) if 'resistivity_ohm_m' in df else None,
            })
            
            self._data = df
            self._is_parsed = True
            
            self.logger.info(
                f"Parsed {len(df)} records from {self.file_path.name}"
            )
            
            return {'metadata': self.metadata, 'data': self.data}
        except Exception as e:
            raise ParserError(f"Failed to parse electrical data: {e}")
    
    def validate(self, data: Optional[pd.DataFrame] = None) -> bool:
        """Validate electrical data.
        
        Args:
            data: DataFrame to validate. If None, uses self.data.
        
        Returns:
            True if validation passes.
        
        Raises:
            ValidationError: If validation fails.
        """
        if data is None:
            data = self.data
        
        if data is None:
            raise ValidationError("No data to validate. Call parse() first.")
        
        # Check required columns
        required = ['station_id', 'depth_m', 'resistivity_ohm_m']
        self._check_required_columns(data, required)
        
        # Check value ranges
        range_map = {
            'depth_m': (0, 10000),
            'resistivity_ohm_m': (0.001, 1e6),
            'current_ma': (0, 10000),
            'voltage_mv': (0, 100000),
        }
        self._check_value_ranges(data, range_map)
        
        # Check for negative values in depth and resistivity
        if (data['depth_m'] < 0).any():
            raise ValidationError("Depth values cannot be negative")
        
        if (data['resistivity_ohm_m'] <= 0).any():
            raise ValidationError("Resistivity values must be positive")
        
        self._is_validated = True
        self.logger.info("Validation passed for electrical data")
        return True
