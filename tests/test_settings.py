"""
設定管理のテスト

Settingsクラスのテストケース
"""

import os
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase, main

from app.config.settings import Settings, SettingsError


class TestSettings(TestCase):
    """Settingsクラスのテストケース"""

    def setUp(self):
        """テストの前準備"""
        # テスト用の一時ディレクトリを作成
        self.test_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.test_dir) / ".bookmarksearch"
        self.config_file = self.config_dir / "config.json"

        # 設定ディレクトリを作成
        os.makedirs(self.config_dir, exist_ok=True)

        # 元のパスを保存
        self._original_config_dir = (
            Settings._instance.config_dir if Settings._instance else None
        )
        self._original_config_file = (
            Settings._instance.config_file if Settings._instance else None
        )

        # テスト用のパスを設定
        Settings._instance = None
        Settings._initialized = False
        settings = Settings()
        settings.config_dir = self.config_dir
        settings.config_file = self.config_file

    def tearDown(self):
        """テストの後片付け"""
        # 一時ディレクトリを削除
        shutil.rmtree(self.test_dir)

        # 元のパスを復元
        Settings._instance = None
        Settings._initialized = False
        if self._original_config_dir and self._original_config_file:
            settings = Settings()
            settings.config_dir = self._original_config_dir
            settings.config_file = self._original_config_file

    def test_singleton(self):
        """シングルトンパターンのテスト"""
        settings1 = Settings()
        settings2 = Settings()
        self.assertIs(settings1, settings2)

    def test_default_settings(self):
        """デフォルト設定のテスト"""
        settings = Settings()
        self.assertEqual(
            settings.get("search_engine.model_name"),
            "intfloat/multilingual-e5-large",
        )
        self.assertTrue(settings.get("search_engine.use_gpu"))
        self.assertEqual(settings.get("search_engine.top_k"), 5)

    def test_get_nonexistent_setting(self):
        """存在しない設定の取得テスト"""
        settings = Settings()
        self.assertIsNone(settings.get("nonexistent.key"))
        self.assertEqual(
            settings.get("nonexistent.key", default="default"), "default"
        )

    def test_set_and_get_setting(self):
        """設定の設定と取得のテスト"""
        settings = Settings()
        test_value = "test_value"
        settings.set("test.key", test_value)
        self.assertEqual(settings.get("test.key"), test_value)

    def test_set_nested_setting(self):
        """ネストされた設定の設定テスト"""
        settings = Settings()
        test_value = {"nested": "value"}
        settings.set("test.nested_key", test_value)
        self.assertEqual(settings.get("test.nested_key.nested"), "value")

    def test_save_and_load_settings(self):
        """設定の保存と読み込みのテスト"""
        settings = Settings()
        test_value = "test_value"
        settings.set("test.key", test_value)

        # 新しいインスタンスを作成して設定が保存されているか確認
        Settings._instance = None
        Settings._initialized = False
        new_settings = Settings()
        self.assertEqual(new_settings.get("test.key"), test_value)

    def test_reset_all_settings(self):
        """全設定のリセットテスト"""
        settings = Settings()
        settings.set("test.key", "test_value")
        settings.reset()
        self.assertIsNone(settings.get("test.key"))
        self.assertEqual(
            settings.get("search_engine.model_name"),
            "intfloat/multilingual-e5-large",
        )

    def test_reset_specific_setting(self):
        """特定の設定のリセットテスト"""
        settings = Settings()
        original_value = settings.get("search_engine.top_k")
        settings.set("search_engine.top_k", 10)
        settings.reset("search_engine.top_k")
        self.assertEqual(settings.get("search_engine.top_k"), original_value)

    def test_invalid_json_file(self):
        """不正なJSONファイルのテスト"""
        # 不正なJSONファイルを作成
        with open(self.config_file, "w", encoding="utf-8") as f:
            f.write("invalid json")

        # 新しいインスタンスを作成して設定を読み込む
        Settings._instance = None
        Settings._initialized = False
        with self.assertRaises(SettingsError):
            settings = Settings()
            settings._load_settings()  # 明示的に設定を読み込む

    def test_merge_settings(self):
        """設定のマージテスト"""
        settings = Settings()
        defaults = {"a": 1, "b": {"c": 2, "d": 3}}
        user_settings = {"b": {"c": 4, "e": 5}}
        merged = settings._merge_settings(defaults, user_settings)
        self.assertEqual(merged["a"], 1)
        self.assertEqual(merged["b"]["c"], 4)
        self.assertEqual(merged["b"]["d"], 3)
        self.assertEqual(merged["b"]["e"], 5)


if __name__ == "__main__":
    main()
