"""
test_scripts用のpytest設定
scriptsディレクトリをPYTHONPATHに追加
"""

import sys
from pathlib import Path

# Add scripts directory to Python path
scripts_dir = Path(__file__).parent.parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))
