"""File I/O utilities for GeoData-Standardizer."""

from pathlib import Path
from typing import Union, Any, Dict
import logging
import json


logger = logging.getLogger(__name__)


def read_text_file(file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
    """Read text file and return contents.
    
    Args:
        file_path: Path to the file.
        encoding: File encoding.
    
    Returns:
        File contents as string.
    
    Raises:
        FileNotFoundError: If file doesn't exist.
        IOError: If file cannot be read.
    """
    file_path = Path(file_path)
    
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
        logger.debug(f"Read {len(content)} bytes from {file_path}")
        return content
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise IOError(f"Failed to read file: {e}")


def write_text_file(
    file_path: Union[str, Path],
    content: str,
    encoding: str = 'utf-8',
    create_dirs: bool = True
) -> None:
    """Write text content to file.
    
    Args:
        file_path: Path to the file.
        content: Content to write.
        encoding: File encoding.
        create_dirs: Whether to create parent directories.
    
    Raises:
        IOError: If file cannot be written.
    """
    file_path = Path(file_path)
    
    if create_dirs:
        file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        logger.debug(f"Wrote {len(content)} bytes to {file_path}")
    except Exception as e:
        logger.error(f"Error writing to file {file_path}: {e}")
        raise IOError(f"Failed to write file: {e}")


def read_json_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Read JSON file and return parsed data.
    
    Args:
        file_path: Path to the JSON file.
    
    Returns:
        Parsed JSON data as dictionary.
    
    Raises:
        FileNotFoundError: If file doesn't exist.
        ValueError: If file contains invalid JSON.
    """
    file_path = Path(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.debug(f"Read JSON from {file_path}")
        return data
    except FileNotFoundError:
        logger.error(f"JSON file not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {file_path}: {e}")
        raise ValueError(f"Invalid JSON: {e}")


def write_json_file(
    file_path: Union[str, Path],
    data: Dict[str, Any],
    indent: int = 2,
    create_dirs: bool = True
) -> None:
    """Write data to JSON file.
    
    Args:
        file_path: Path to the JSON file.
        data: Data to write.
        indent: Indentation for pretty printing.
        create_dirs: Whether to create parent directories.
    
    Raises:
        IOError: If file cannot be written.
    """
    file_path = Path(file_path)
    
    if create_dirs:
        file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent)
        logger.debug(f"Wrote JSON to {file_path}")
    except Exception as e:
        logger.error(f"Error writing JSON to file {file_path}: {e}")
        raise IOError(f"Failed to write JSON file: {e}")


def ensure_directory_exists(dir_path: Union[str, Path]) -> Path:
    """Ensure directory exists, creating it if necessary.
    
    Args:
        dir_path: Path to the directory.
    
    Returns:
        Path object for the directory.
    """
    dir_path = Path(dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Ensured directory exists: {dir_path}")
    return dir_path


def get_file_size(file_path: Union[str, Path]) -> int:
    """Get file size in bytes.
    
    Args:
        file_path: Path to the file.
    
    Returns:
        File size in bytes.
    
    Raises:
        FileNotFoundError: If file doesn't exist.
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    size = file_path.stat().st_size
    logger.debug(f"File size of {file_path}: {size} bytes")
    return size


def list_files_in_directory(
    dir_path: Union[str, Path],
    pattern: str = '*',
    recursive: bool = False
) -> list:
    """List files in directory matching pattern.
    
    Args:
        dir_path: Path to the directory.
        pattern: Glob pattern for filtering files.
        recursive: Whether to search recursively.
    
    Returns:
        List of Path objects for matching files.
    
    Raises:
        FileNotFoundError: If directory doesn't exist.
    """
    dir_path = Path(dir_path)
    
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")
    
    if recursive:
        files = list(dir_path.rglob(pattern))
    else:
        files = list(dir_path.glob(pattern))
    
    # Filter to only files (not directories)
    files = [f for f in files if f.is_file()]
    
    logger.debug(f"Found {len(files)} files in {dir_path} matching '{pattern}'")
    return files
