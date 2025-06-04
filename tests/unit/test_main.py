"""
Unit tests for main module.
"""

from app.main import main


def test_main(capsys):
    """Test main function."""
    main()
    captured = capsys.readouterr()
    assert captured.out == "Hello, World!\n"
