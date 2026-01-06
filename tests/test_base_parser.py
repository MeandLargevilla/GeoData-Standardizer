"""Tests for base_parser module."""

import pytest
from pathlib import Path
from src.core.base_parser import BaseParser, ParserError


def test_base_parser_cannot_instantiate():
    """Test that BaseParser cannot be instantiated directly."""
    with pytest.raises(TypeError):
        # BaseParser is abstract and cannot be instantiated
        parser = BaseParser('dummy.txt')


def test_base_parser_requires_abstract_methods():
    """Test that subclasses must implement abstract methods."""
    
    class IncompleteParser(BaseParser):
        """Parser missing required abstract methods."""
        pass
    
    # Should raise TypeError because abstract methods are not implemented
    with pytest.raises(TypeError):
        parser = IncompleteParser('dummy.txt')


def test_parser_error_exception():
    """Test ParserError exception."""
    error = ParserError("Test error message")
    assert str(error) == "Test error message"
    assert isinstance(error, Exception)
