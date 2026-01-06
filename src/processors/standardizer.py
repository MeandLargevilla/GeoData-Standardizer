"""Data standardization processor."""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, Union
import logging
from datetime import datetime


class Standardizer:
    """Standardizes geophysical data to common format.
    
    This class takes parsed data from various sources and converts it
    to a standardized format for consistent downstream processing.
    
    Attributes:
        output_format: Format for output files ('csv', 'json', 'excel', 'parquet').
        logger: Logger instance for this class.
    
    Example:
        >>> standardizer = Standardizer(output_format='csv')
        >>> result = standardizer.standardize(parsed_data, 'electrical')
        >>> standardizer.write_output(result, 'output.csv')
    """
    
    def __init__(self, output_format: str = 'csv'):
        """Initialize the standardizer.
        
        Args:
            output_format: Format for output files.
        """
        self.output_format = output_format
        self.logger = logging.getLogger(__name__)
        
        # Supported output formats
        self._supported_formats = ['csv', 'json', 'excel', 'parquet']
        
        if output_format not in self._supported_formats:
            raise ValueError(
                f"Unsupported output format: {output_format}. "
                f"Supported: {', '.join(self._supported_formats)}"
            )
    
    def standardize(
        self,
        parsed_data: Dict[str, Any],
        data_type: str
    ) -> Dict[str, Any]:
        """Standardize parsed data to common format.
        
        Args:
            parsed_data: Dictionary with 'metadata' and 'data' keys.
            data_type: Type of geophysical data.
        
        Returns:
            Dictionary with standardized 'metadata' and 'data'.
        """
        df = parsed_data['data'].copy()
        metadata = parsed_data['metadata'].copy()
        
        # Add standardization metadata
        metadata['standardized_at'] = datetime.now().isoformat()
        metadata['standardization_version'] = '1.0'
        metadata['data_type'] = data_type
        
        # Apply common standardizations
        df = self._apply_common_standards(df)
        
        # Apply data type specific standardizations
        if data_type == 'electrical':
            df = self._standardize_electrical(df)
        elif data_type == 'seismic':
            df = self._standardize_seismic(df)
        elif data_type == 'radar':
            df = self._standardize_radar(df)
        
        self.logger.info(f"Standardized {len(df)} records for {data_type} data")
        
        return {'metadata': metadata, 'data': df}
    
    def _apply_common_standards(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply common standardizations to all data types.
        
        Args:
            df: DataFrame to standardize.
        
        Returns:
            Standardized DataFrame.
        """
        # Sort columns alphabetically
        df = df.reindex(sorted(df.columns), axis=1)
        
        # Remove any completely empty rows
        df = df.dropna(how='all')
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
    
    def _standardize_electrical(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply electrical data specific standardizations.
        
        Args:
            df: DataFrame to standardize.
        
        Returns:
            Standardized DataFrame.
        """
        # Ensure proper data types
        if 'station_id' in df.columns:
            df['station_id'] = df['station_id'].astype(str)
        
        if 'depth_m' in df.columns:
            df['depth_m'] = pd.to_numeric(df['depth_m'], errors='coerce')
        
        if 'resistivity_ohm_m' in df.columns:
            df['resistivity_ohm_m'] = pd.to_numeric(df['resistivity_ohm_m'], errors='coerce')
        
        return df
    
    def _standardize_seismic(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply seismic data specific standardizations.
        
        Args:
            df: DataFrame to standardize.
        
        Returns:
            Standardized DataFrame.
        """
        # Ensure proper data types
        if 'trace_number' in df.columns:
            df['trace_number'] = pd.to_numeric(df['trace_number'], errors='coerce')
        
        if 'time_ms' in df.columns:
            df['time_ms'] = pd.to_numeric(df['time_ms'], errors='coerce')
        
        if 'amplitude' in df.columns:
            df['amplitude'] = pd.to_numeric(df['amplitude'], errors='coerce')
        
        return df
    
    def _standardize_radar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply radar data specific standardizations.
        
        Args:
            df: DataFrame to standardize.
        
        Returns:
            Standardized DataFrame.
        """
        # Ensure proper data types
        if 'trace_number' in df.columns:
            df['trace_number'] = pd.to_numeric(df['trace_number'], errors='coerce')
        
        if 'sample_number' in df.columns:
            df['sample_number'] = pd.to_numeric(df['sample_number'], errors='coerce')
        
        if 'amplitude' in df.columns:
            df['amplitude'] = pd.to_numeric(df['amplitude'], errors='coerce')
        
        return df
    
    def write_output(
        self,
        data: Dict[str, Any],
        output_path: Union[str, Path],
        include_metadata: bool = True
    ) -> None:
        """Write standardized data to file.
        
        Args:
            data: Dictionary with 'metadata' and 'data' keys.
            output_path: Path where to save the output.
            include_metadata: Whether to save metadata to a separate file.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        df = data['data']
        
        # Write data file
        if self.output_format == 'csv':
            df.to_csv(output_path, index=False)
        elif self.output_format == 'json':
            df.to_json(output_path, orient='records', indent=2)
        elif self.output_format == 'excel':
            df.to_excel(output_path, index=False)
        elif self.output_format == 'parquet':
            df.to_parquet(output_path, index=False)
        
        self.logger.info(f"Wrote output to {output_path}")
        
        # Write metadata file if requested
        if include_metadata and data.get('metadata'):
            metadata_path = output_path.parent / f"{output_path.stem}_metadata.json"
            import json
            import numpy as np
            
            # Convert numpy types to native Python types for JSON serialization
            def convert_numpy_types(obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {k: convert_numpy_types(v) for k, v in obj.items()}
                elif isinstance(obj, (list, tuple)):
                    return [convert_numpy_types(item) for item in obj]
                return obj
            
            metadata_json = convert_numpy_types(data['metadata'])
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata_json, f, indent=2)
            self.logger.info(f"Wrote metadata to {metadata_path}")
