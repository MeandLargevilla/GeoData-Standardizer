"""Parser for ground-penetrating radar (GPR) data."""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from ..core.base_parser import BaseParser, ParserError, ValidationError


class RadarParser(BaseParser):
    """Parser for ground-penetrating radar (GPR) survey data.
    
    This parser handles GPR data from various formats (DZT, RD3, etc.),
    standardizing the format for further processing.
    
    Expected columns (after standardization):
        - trace_number: Trace identifier
        - sample_number: Sample number within trace
        - amplitude: Signal amplitude
        - distance_m: Distance in meters (optional)
        - time_ns: Time in nanoseconds (optional)
        - antenna_freq_mhz: Antenna frequency in MHz (optional)
    
    Example:
        >>> parser = RadarParser('gpr_data.dzt')
        >>> result = parser.process()
        >>> df = result['data']
    """
    
    def load(self) -> None:
        """Load GPR data from file.
        
        Raises:
            ParserError: If file cannot be loaded.
        """
        try:
            # For binary formats like DZT, we would use specialized libraries
            # For now, support simple CSV format
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                self._raw_data = f.read()
            self._is_loaded = True
            self.logger.info(f"Loaded {self.file_path.name} ({len(self._raw_data)} bytes)")
        except Exception as e:
            raise ParserError(f"Failed to load GPR file: {e}")
    
    def parse(self) -> Dict[str, Any]:
        """Parse GPR data.
        
        Returns:
            Dictionary with 'metadata' and 'data' keys.
        
        Raises:
            ParserError: If parsing fails.
        """
        if not self.is_loaded:
            raise ParserError("Data must be loaded first. Call load() before parse().")
        
        try:
            # Parse CSV format (simplified for now)
            df = pd.read_csv(pd.io.common.StringIO(self._raw_data))
            
            # Standardize column names
            column_map = {
                'trace': 'trace_number',
                'Trace': 'trace_number',
                'TRACE': 'trace_number',
                'sample': 'sample_number',
                'Sample': 'sample_number',
                'SAMPLE': 'sample_number',
                'amp': 'amplitude',
                'Amplitude': 'amplitude',
                'AMPLITUDE': 'amplitude',
                'distance': 'distance_m',
                'Distance': 'distance_m',
                'time': 'time_ns',
                'Time': 'time_ns',
                'time_ns': 'time_ns',
                'frequency': 'antenna_freq_mhz',
                'freq': 'antenna_freq_mhz',
                'antenna_frequency': 'antenna_freq_mhz',
            }
            df = self._standardize_column_names(df, column_map)
            
            # Update metadata
            self.metadata.update({
                'data_type': 'radar',
                'record_count': len(df),
                'traces': df['trace_number'].nunique() if 'trace_number' in df else 0,
                'samples_per_trace': df['sample_number'].nunique() if 'sample_number' in df else 0,
                'amplitude_range': (
                    df['amplitude'].min(), df['amplitude'].max()
                ) if 'amplitude' in df else None,
                'distance_range_m': (
                    df['distance_m'].min(), df['distance_m'].max()
                ) if 'distance_m' in df else None,
            })
            
            self._data = df
            self._is_parsed = True
            
            self.logger.info(
                f"Parsed {len(df)} records from {self.file_path.name}"
            )
            
            return {'metadata': self.metadata, 'data': self.data}
        except Exception as e:
            raise ParserError(f"Failed to parse GPR data: {e}")
    
    def validate(self, data: Optional[pd.DataFrame] = None) -> bool:
        """Validate GPR data.
        
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
        required = ['trace_number', 'sample_number', 'amplitude']
        self._check_required_columns(data, required)
        
        # Check value ranges
        range_map = {
            'sample_number': (0, 100000),
            'amplitude': (-32768, 32767),
            'distance_m': (0, 10000),
            'time_ns': (0, 1000000),
            'antenna_freq_mhz': (10, 5000),
        }
        self._check_value_ranges(data, range_map)
        
        # Check for negative sample numbers
        if (data['sample_number'] < 0).any():
            raise ValidationError("Sample numbers cannot be negative")
        
        self._is_validated = True
        self.logger.info("Validation passed for GPR data")
        return True
