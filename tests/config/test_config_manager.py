"""
ConfigManagerのテスト

設定管理機能の単体テストを実施します。
"""

import pytest

from app.config.manager import ConfigManager


@pytest.fixture
def config_file(tmp_path):
    """テスト用の設定ファイルを作成"""
    config_content = """
    timeouts:
        llm: 30
        search: 10
        extraction: 45
        total: 90

    retry:
        max_attempts: 5
        base_delay: 2
        max_delay: 32

    thresholds:
        relevance: 0.7
        validation: 0.8
        confidence: 0.6
    """
    config_path = tmp_path / "config.yml"
    config_path.write_text(config_content)
    return str(config_path)


@pytest.fixture
def config_manager(config_file):
    """ConfigManagerのインスタンスを作成"""
    return ConfigManager(config_file)


def test_load_config(config_manager):
    """設定ファイルの読み込みテスト"""
    config = config_manager.get_config()
    
    # タイムアウト設定の検証
    assert config["timeouts"]["llm"] == 30
    assert config["timeouts"]["search"] == 10
    assert config["timeouts"]["extraction"] == 45
    assert config["timeouts"]["total"] == 90
    
    # リトライ設定の検証
    assert config["retry"]["max_attempts"] == 5
    assert config["retry"]["base_delay"] == 2
    assert config["retry"]["max_delay"] == 32
    
    # 閾値設定の検証
    assert config["thresholds"]["relevance"] == 0.7
    assert config["thresholds"]["validation"] == 0.8
    assert config["thresholds"]["confidence"] == 0.6


def test_get_section(config_manager):
    """設定セクション取得のテスト"""
    timeouts = config_manager.get_section("timeouts")
    assert timeouts["llm"] == 30
    assert timeouts["search"] == 10
    
    retry = config_manager.get_section("retry")
    assert retry["max_attempts"] == 5
    assert retry["base_delay"] == 2


def test_update_config(config_manager):
    """設定更新のテスト"""
    # 設定値の更新
    config_manager.update_config({
        "timeouts": {"llm": 60}
    })
    
    # 更新の確認
    config = config_manager.get_config()
    assert config["timeouts"]["llm"] == 60
    assert config["timeouts"]["search"] == 10  # 未更新の値は維持


def test_invalid_config():
    """不正な設定値のテスト"""
    with pytest.raises(ValueError):
        ConfigManager("non_existent_file.yml")
    
    with pytest.raises(ValueError):
        ConfigManager(None)


def test_environment_override(config_manager, monkeypatch):
    """環境変数によるオーバーライドのテスト"""
    # 環境変数の設定
    monkeypatch.setenv("APP_TIMEOUT_LLM", "90")
    monkeypatch.setenv("APP_RETRY_MAX_ATTEMPTS", "10")
    
    # 設定の再読み込み
    config_manager.reload()
    config = config_manager.get_config()
    
    # 環境変数による上書きの確認
    assert config["timeouts"]["llm"] == 90
    assert config["retry"]["max_attempts"] == 10


def test_config_validation(config_manager):
    """設定値の検証テスト"""
    # 不正な値での更新を試行
    with pytest.raises(ValueError):
        config_manager.update_config({
            "timeouts": {"llm": -1}  # 負の値は不正
        })
    
    with pytest.raises(ValueError):
        config_manager.update_config({
            "thresholds": {"relevance": 2.0}  # 1.0を超える値は不正
        })


def test_config_persistence(config_manager, tmp_path):
    """設定の永続化テスト"""
    # 設定を更新
    config_manager.update_config({
        "timeouts": {"llm": 60}
    })
    
    # 設定を保存
    save_path = tmp_path / "saved_config.yml"
    config_manager.save_config(str(save_path))
    
    # 新しいインスタンスで読み込み
    new_manager = ConfigManager(str(save_path))
    new_config = new_manager.get_config()
    
    # 保存された設定の確認
    assert new_config["timeouts"]["llm"] == 60 