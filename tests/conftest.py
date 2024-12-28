"""
pytestの共通設定
"""

import os
import sys
from pathlib import Path

# プロジェクトルートをPYTHONPATHに追加
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

# テスト用の設定
os.environ.setdefault('COMPANY_CONFIG_PATH', 'app/config/companies.yaml') 