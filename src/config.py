"""Configuration module for GeoData-Standardizer.

This module contains all configuration settings for the application,
including paths, logging configuration, parser settings, and QC thresholds.
"""

from pathlib import Path
import logging
from typing import Dict, Any


# Base directories
BASE_DIR = Path(__file__).parent.parent.resolve()
DATA_DIR = BASE_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
LOGS_DIR = BASE_DIR / 'logs'
DOCS_DIR = BASE_DIR / 'docs'
EXAMPLES_DIR = BASE_DIR / 'examples'
TESTS_DIR = BASE_DIR / 'tests'


# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': str(LOGS_DIR / 'geodata_standardizer.log'),
            'mode': 'a',
        },
    },
    'loggers': {
        '': {  # Root logger
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
        },
    },
}


# Parser configuration
PARSER_CONFIG = {
    'electrical': {
        'supported_extensions': ['.dat', '.txt', '.csv'],
        'encoding': 'utf-8',
        'required_columns': ['station_id', 'depth_m', 'resistivity_ohm_m'],
        'optional_columns': ['current_ma', 'voltage_mv', 'latitude', 'longitude'],
        'value_ranges': {
            'depth_m': (0, 10000),
            'resistivity_ohm_m': (0.001, 1e6),
            'current_ma': (0, 10000),
            'voltage_mv': (0, 100000),
        },
    },
    'seismic': {
        'supported_extensions': ['.sgy', '.segy', '.seg2'],
        'encoding': 'utf-8',
        'required_columns': ['trace_number', 'time_ms', 'amplitude'],
        'optional_columns': ['station_id', 'offset_m', 'elevation_m'],
        'value_ranges': {
            'time_ms': (0, 100000),
            'amplitude': (-1e6, 1e6),
            'offset_m': (0, 100000),
        },
    },
    'radar': {
        'supported_extensions': ['.dzt', '.rd3', '.dt1'],
        'encoding': 'utf-8',
        'required_columns': ['trace_number', 'sample_number', 'amplitude'],
        'optional_columns': ['distance_m', 'time_ns', 'antenna_freq_mhz'],
        'value_ranges': {
            'sample_number': (0, 100000),
            'amplitude': (-32768, 32767),
            'distance_m': (0, 10000),
            'time_ns': (0, 1000000),
            'antenna_freq_mhz': (10, 5000),
        },
    },
}


# Standardization configuration
STANDARDIZATION_CONFIG = {
    'output_formats': ['csv', 'json', 'excel', 'parquet'],
    'default_format': 'csv',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'coordinate_system': 'WGS84',
    'unit_standards': {
        'depth': 'meters',
        'distance': 'meters',
        'time': 'milliseconds',
        'resistivity': 'ohm_meters',
        'frequency': 'megahertz',
    },
}


# Quality control configuration
QC_CONFIG = {
    'missing_value_threshold': 0.1,  # Max 10% missing values
    'duplicate_threshold': 0.05,  # Max 5% duplicates
    'outlier_detection': {
        'method': 'iqr',  # or 'zscore'
        'iqr_multiplier': 1.5,
        'zscore_threshold': 3,
    },
    'validation_rules': {
        'check_missing': True,
        'check_duplicates': True,
        'check_outliers': True,
        'check_ranges': True,
        'check_dtypes': True,
    },
}


# Output configuration
OUTPUT_CONFIG = {
    'compression': {
        'csv': None,
        'json': None,
        'parquet': 'snappy',
    },
    'encoding': 'utf-8',
    'include_metadata': True,
    'metadata_file_suffix': '_metadata.json',
}


# Application configuration
APP_CONFIG = {
    'name': 'GeoData-Standardizer',
    'version': '0.1.0',
    'description': 'A Python tool for standardizing geophysical data formats',
    'author': 'GeoData-Standardizer Contributors',
    'default_encoding': 'utf-8',
    'max_file_size_mb': 1000,  # Maximum file size to process
    'chunk_size': 10000,  # Rows per chunk for large files
    'verbose': False,
}


def get_parser_config(data_type: str) -> Dict[str, Any]:
    """Get configuration for a specific parser type.
    
    Args:
        data_type: Type of geophysical data.
    
    Returns:
        Configuration dictionary for the parser.
    
    Raises:
        ValueError: If data_type is not recognized.
    """
    if data_type not in PARSER_CONFIG:
        raise ValueError(
            f"Unknown data type: {data_type}. "
            f"Available: {list(PARSER_CONFIG.keys())}"
        )
    return PARSER_CONFIG[data_type]


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration.
    
    Args:
        verbose: If True, set console handler to DEBUG level.
    """
    import logging.config
    
    # Ensure logs directory exists
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    config = LOGGING_CONFIG.copy()
    
    if verbose:
        config['handlers']['console']['level'] = 'DEBUG'
    
    logging.config.dictConfig(config)


def get_output_path(
    input_path: Path,
    output_dir: Path = None,
    format: str = 'csv',
    suffix: str = '_standardized'
) -> Path:
    """Generate output file path.
    
    Args:
        input_path: Input file path.
        output_dir: Output directory (default: PROCESSED_DATA_DIR).
        format: Output format.
        suffix: Suffix to add to filename.
    
    Returns:
        Path for the output file.
    """
    if output_dir is None:
        output_dir = PROCESSED_DATA_DIR
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine file extension
    ext_map = {
        'csv': '.csv',
        'json': '.json',
        'excel': '.xlsx',
        'parquet': '.parquet',
    }
    ext = ext_map.get(format, '.csv')
    
    # Create output filename
    output_name = f"{input_path.stem}{suffix}{ext}"
    return output_dir / output_name


def validate_config() -> bool:
    """Validate configuration settings.
    
    Returns:
        True if configuration is valid.
    
    Raises:
        ValueError: If configuration is invalid.
    """
    # Check that required directories are defined
    required_dirs = [BASE_DIR, DATA_DIR, LOGS_DIR]
    for dir_path in required_dirs:
        if not isinstance(dir_path, Path):
            raise ValueError(f"Invalid directory path: {dir_path}")
    
    # Check parser configurations
    for data_type, config in PARSER_CONFIG.items():
        if 'supported_extensions' not in config:
            raise ValueError(
                f"Parser config for '{data_type}' missing 'supported_extensions'"
            )
        if 'required_columns' not in config:
            raise ValueError(
                f"Parser config for '{data_type}' missing 'required_columns'"
            )
    
    return True


# Validate configuration on import
validate_config()
