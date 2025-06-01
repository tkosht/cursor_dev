"""
Unit tests for main module.
"""
import pytest
from app.main import main


def test_main(capsys):
    """Test main function."""
    main()
    captured = capsys.readouterr()
    assert captured.out == "Hello, World!\n"